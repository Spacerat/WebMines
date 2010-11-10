
import cherrypy
from cherrypy import expose
import os
import threading
from game import Game, Player
from Cheetah.Template import Template

current_dir = os.path.dirname(os.path.abspath(__file__))
website_title = 'MultiMines'

class Site():
    def get_session_id(self,name=''):
        id = cherrypy.session.get('id')
        if id==None and name!='':
            p = Player(name)
            cherrypy.session['id'] = p.id
            cherrypy.session['name'] = p.name
            id = p.id
        return id
    
    def get_session_player(self,name=''):
        id = cherrypy.session.get('id')
        print "sessionid",id
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
    @cherrypy.expose
    def default(self,*args,**kwargs):
        response = ""
        id = args[0]
        player = self.get_session_player()
        if id in Game.games:
            game = Game.games[id]
            data = {
                'title':website_title,
                'game':game,
                'player':player,
                'players': game.players,
                'playing': player.id in game.players
            }
            t = Template(file='html/game.html',searchList=[data])
            response = t.respond()
        else:
            response = "This is not a valid game."
            
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
