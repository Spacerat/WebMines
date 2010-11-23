import game

import cherrypy
import os
import threading
import json
import time
from random import randint
from Cheetah.Template import Template
from game import Game

current_dir = os.path.dirname(os.path.abspath(__file__))
website_title = 'AjaxMines'

class Site():
    def get_session_player(self,game,name=''):
        if name=="":
            name = self.get_cookie_name()
        id = cherrypy.session.get(game.id)
        if id==None and name!='':
            p = game.add_player(name)
            cherrypy.session[game.id] = p.id
            cherrypy.response.cookie['name'] = name
            cherrypy.response.cookie['name']['expires'] = 60*60*24
            return p
        elif id:
            return game.get_player(id)

    def get_cookie_name(self):
        try:
            return cherrypy.request.cookie.get('name','').value
        except AttributeError:
            return ''


class RootHandler(Site):
    
    @cherrypy.expose
    def index(self):
        data = {
            'title':website_title,
            'games':Game.games.values(),
            'numgames':len(Game.games.values()),
            'name': self.get_cookie_name()
        }
        t = Template(file='html/index.html',searchList=[data])
        return t.respond()

    @cherrypy.expose
    def name(self,name=""):
        cherrypy.response.cookie['name']=name

    @cherrypy.expose
    def create(self,name="",pname="",width=-1,height=-1,mines=-1,defaultmines=1,wrap=False):
        if defaultmines=='true':
            mines=-1
        if wrap=='true':
            wrap=True
        else:
            wrap=False

        width = int(width)
        height = int(height)
        mines = int(mines)

        if not name:
            return "You must supply a game name."
        newgame = Game(name,width,height,mines,wrap)
        pl = self.get_session_player(newgame,name=pname)
        if not pl:
            newgame.close()
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
        
    def encodetiles(self,tilelist):
        if not tilelist: return ''
        r=[]
        for t in tilelist:
            if (not t.uncovered) and (not t.flag): continue
            #The browser swaps the X and Y values, it seems.
            r.append({
                'x': t.pos[1],
                'y': t.pos[0],
                'fl': t.flag
            })
            if t.uncovered or t.flag:
                r[-1]['pl']=t.uncovered
                if t.uncovered:
                    if t.bomb:
                        r[-1]['val']="X"
                    else:
                        r[-1]['val']=t.adjacency
        return r

    def encode_playerlist(self,game,this_player):
        return [{
            'name':p.name,
            'present':p.present,
            'id':p.id,
            'me':(p==this_player)
        } for p in game.players]
    
    def clickresponse(self,game,player,x,y):
        return self.encodetiles(game.click(player,x,y))
    
    def send_data(self,game,data):
        for p in game.players:
            p.send_data(data)
    
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
        game.check_activity()
        if game.closed:
            raise cherrypy.NotFound

        if player==None:
            player = self.get_session_player(game,"Guest")

        if action=='click':
            data = self.clickresponse(game, player, int(kwargs['x']), int(kwargs['y']))
            if data: data = {'reveal':data}
            if game.time_won>0:
                data['won']=True
            if data: self.send_data(game,data)

        elif action=='flag':
            x = int(kwargs['x'])
            y = int(kwargs['y'])
            data = game.flag(player,x,y )
            print "data",data
            self.send_data(game,{'flag': {
                'x': x,
                'y': y,
                'fl': data
            }})

        elif action=='refresh':
            l = []
            for row in game.board.tiles:
                l+=row
            data = self.encodetiles(l)
            response = json.dumps({'reveal':data,'players': self.encode_playerlist(game,player)})
            
        elif action=='poll':
            #Wait until the request is filled
            cherrypy.session.save()
            while player.polldata==None:
                time.sleep(0.1)

            responsedict = {}
            while len(player.polldata)>0:
                responsedict.update(player.polldata.pop(0))
            response = json.dumps(responsedict)
            player.polldata=None

        elif action=='leave':
            player.present = False
            self.send_data(game, {
                'players': self.encode_playerlist(game,player)
            })
            game.check_activity()

        elif action=='':
            player.present = True
            data = {
                'title': website_title,
                'game': game,
                'player': player,
                'players': game.players,
                'playing': player.id in game.players
            }
            self.send_data(game,{
                'players': self.encode_playerlist(game,player)
            })
            t = Template(file='html/game.html',searchList=[data])
            response = t.respond()

        #print response
        return response
        

if __name__ == "__main__":
    
    cherrypy.tree.mount(GameHandler(),'/game','config.cfg')
    cherrypy.quickstart(RootHandler(),'/','config.cfg')
