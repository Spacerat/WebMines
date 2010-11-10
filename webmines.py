
import cherrypy
import os
import threading
from Cheetah.Template import Template

current_dir = os.path.dirname(os.path.abspath(__file__))

class ListedGame:
    def __init__(self,name,id):
        self.name=name
        self.id=id

class Root:
    
    @cherrypy.expose
    def index(self):
        data = {}
        data['title']='MultiMines'
        data['games']=[]
        data['numgames'] = max(len(data['games']),10)
        
        t = Template(file='html/index.html',searchList=[data])
        return t.respond()
        
        
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
    cherrypy.quickstart(Root(),'/','config.cfg')
