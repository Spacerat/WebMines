
import cherrypy
import os
import threading
import json
import time
from random import randint
from Cheetah.Template import Template
from game import Game

current_dir = os.path.dirname(os.path.abspath(__file__))
website_title = 'MultiMines'

class Site():
    def get_session_player(self,game,name=''):
        if name=="":
            name = cherrypy.request.cookie.get('name','').value
        id = cherrypy.session.get(game.id)
        if id==None and name!='':
            p = game.add_player(name)
            cherrypy.session[game.id] = p.id
            cherrypy.response.cookie['name'] = name
            cherrypy.response.cookie['name']['expires'] = 60*60*24
            return p
        else:
            return game.get_player(id)


class RootHandler(Site):
    
    @cherrypy.expose
    def index(self):
        data = {
            'title':website_title,
            'games':Game.games.values(),
            'numgames':len(Game.games.values()),
            'name': cherrypy.request.cookie.get('name','').value
        }
        t = Template(file='html/index.html',searchList=[data])
        return t.respond()
    
    @cherrypy.expose
    def create(self,name="",pname=""):
        if not name:
            return "You must supply a game name."
        newgame = Game(name)
        pl = self.get_session_player(newgame,name=pname)
        if not pl:
            return "Please supply a player name."
        raise cherrypy.HTTPRedirect("/game/"+newgame.id)

    @cherrypy.expose
    def join(self,id="",pname=""):
        if not id:
            return "Please select a game."
        game = Game.games.get(id,None)
        if not game:
            return "Invalid game ID."
        pl = self.get_session_player(game,name=pname)
        if not pl:
            return "Please supply a player name."   
        raise cherrypy.HTTPRedirect("/game/"+game.id)


class GameHandler(Site):
    
    polls = {}
    
    def encodetiles(self,tilelist):
        if not tilelist: return ''
        r=[]
        for t in tilelist:
            if not t.uncovered: continue
            #The browser swaps the X and Y values, it seems.
            r.append({
                'x':t.pos[1],
                'y':t.pos[0],
                'pl':t.uncovered
            })
            if t.bomb:
                r[-1]['val']="X"
            else:
                r[-1]['val']=t.adjacency
        return r

    def encode_playerlist(self,game):
        return [{
            'name':p.name,
            'present':p.present,
            'id':p.id
        } for p in game.players]
    
    def clickresponse(self,game,player,x,y):
        return self.encodetiles(game.click(player,x,y))
    
    def send_data(self,data):
        for p in GameHandler.polls:
            GameHandler.polls[p].append(data)
    
    @cherrypy.expose
    def default(self,*args,**kwargs):
        response = ""
        id = args[0]
        action = kwargs.get('action','')
        if id in Game.games:
            game = Game.games[id]
        else:
            raise cherrypy.NotFound
        player = self.get_session_player(game)
        if action=='click':
            data = self.clickresponse(game, player, int(kwargs['x']), int(kwargs['y']))
            if data: self.send_data({'reveal':data})
        elif action=='refresh':
            l = []
            for row in game.board.tiles:
                l+=row
            data = self.encodetiles(l)
            response = json.dumps({'reveal':data,'players': self.encode_playerlist(game)})
            
        elif action=='poll':
            pollid=0
            #Add a poll request to the poll list
            while pollid==0 or pollid in GameHandler.polls.keys():
                pollid = randint(0,10000)
            GameHandler.polls[pollid] = []
            #wait until the request is filled
            cherrypy.session.save()

            responsedict = {}
            count = 0
            while len(GameHandler.polls[pollid])==0:
                time.sleep(0.1)
                count+=0.1
                if count>300:
                    #Timeout!
                    print "Playe %s timed out!"%player.name
                    player.present = False
                    self.send_data({'players': self.encode_playerlist(game)})
                    game.check_activity()
                    break

                    
            while len(GameHandler.polls[pollid])>0:
                responsedict.update(GameHandler.polls[pollid].pop(0))
            response = json.dumps(responsedict)
            del GameHandler.polls[pollid]
            
        elif action=='':
            player.present = True
            data = {
                'title': website_title,
                'game': game,
                'player': player,
                'players': game.players,
                'playing': player.id in game.players
            }
            self.send_data({
                'players': self.encode_playerlist(game)
            })
            t = Template(file='html/game.html',searchList=[data])
            response = t.respond()

        print response
        return response
        
class InputThread(threading.Thread):
    def run(self):
        go = True
        while go:
            cmd = raw_input(">")
            if cmd=="exit":
                go = False
                cherrypy.engine.exit()

if __name__ == "__main__":
    
    cherrypy.tree.mount(GameHandler(),'/game','config.cfg')
    cherrypy.quickstart(RootHandler(),'/','config.cfg')
