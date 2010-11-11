
import cherrypy
from cherrypy import expose
import os
import threading
import json
import time
from random import randint
from Cheetah.Template import Template

from game import Game, Player

current_dir = os.path.dirname(os.path.abspath(__file__))
website_title = 'MultiMines'

class Site():
    def get_session_player(self,name=''):
        id = cherrypy.session.get('id')
        if id==None and name!='':
            p = Player(name)
            cherrypy.session['id'] = p.id
            cherrypy.session['name'] = p.name
            return p
        elif id in Player.players:
            return Player.players[id]
        else:
            return None

class RootHandler(Site):
    
    @cherrypy.expose
    def index(self):
        data = {
            'title':website_title,
            'games':Game.games.values(),
            'numgames':len(Game.games.values()),
            'player': self.get_session_player()
        }
        t = Template(file='html/index.html',searchList=[data])
        return t.respond()
    
    @cherrypy.expose
    def create(self,name="",pname=""):
        if not name:
            return "You must supply a game name."
        pl = self.get_session_player(name=pname)
        if not pl:
            return "Please supply a player name."
        newgame = Game(name)
        newgame.add_player(pl)
        raise cherrypy.HTTPRedirect("/game/"+newgame.id)

    @cherrypy.expose
    def join(self,id="",pname=""):
        if not id:
            return "Please select a game."
        pl = self.get_session_player(name=pname)
        if not pl:
            return "Please supply a player name."
        game = Game.games.get(id,None)
        if not game:
            return "Invalid game ID."
        if game.started == False:
            game.add_player(pl)    
        raise cherrypy.HTTPRedirect("/game/"+game.id)
        
        
        
class GameHandler(Site):
    
    polls = {}
    
    def encodetiles(self,tilelist):
        if not tilelist: return ''
        r=''
        for t in tilelist:
            #The browser swaps the X and Y values, it seems.
            r+="%d%d%d"%(t.pos[1],t.pos[0],t.uncovered)
            if t.bomb:
                r+="X"
            else:
                r+=str(t.adjacency)
        return r        
    
    def clickresponse(self,game,player,x,y):
        return self.encodetiles(game.click(player,x,y))
    
    def send_data(self,data):
        for p in GameHandler.polls:
            GameHandler.polls[p] = data       
    
    @cherrypy.expose
    def default(self,*args,**kwargs):
        response = ""
        id = args[0]
        player = self.get_session_player() 
        action = kwargs.get('action','')
        if id in Game.games:
            game = Game.games[id]
        else:
            raise Exception, "Invalid game ID"
        if action=='click':
            data = self.clickresponse(game, player, int(kwargs['x']), int(kwargs['y']))
            if data: self.send_data(json.dumps({'reveal':data}))
            
        elif action=='refresh':
            l = []
            for row in game.board.tiles:
                l+=row
            data = self.encodetiles(l)
            if data: return json.dumps({'reveal':data})
            
        elif action=='poll':
            pollid=0
            #Add a poll request to the poll list
            while pollid==0 or pollid in GameHandler.polls.keys():
                pollid = randint(0,10000)
            GameHandler.polls[pollid] = '{}'
            #wait until the request is filled
            cherrypy.session.save()
            while GameHandler.polls[pollid]=='{}':
                time.sleep(0.1)
            response = GameHandler.polls[pollid]
            del GameHandler.polls[pollid]
            
        elif action=='':
            data = {
                'title':website_title,
                'game':game,
                'player':player,
                'players': game.players,
                'playing': player.id in game.players
            }
            t = Template(file='html/game.html',searchList=[data])
            response = t.respond()

        
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
    InputThread().start()
    
    cherrypy.tree.mount(GameHandler(),'/game','config.cfg')
    cherrypy.quickstart(RootHandler(),'/','config.cfg')
