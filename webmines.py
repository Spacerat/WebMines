
import cherrypy
import os
import threading

current_dir = os.path.dirname(os.path.abspath(__file__))

class Root:
    
    def __init__(self):
        self.html = {}
    
    @cherrypy.expose
    def index(self):
        return open('static/index.html').read()
        
class InputThread(threading.Thread):
    def run(self):
        go = True
        while go:
            cmd = raw_input(">")
            if cmd=="exit":
                go = False
                cherrypy.engine.exit()

InputThread().start()

if __name__ == "__main__":
    cherrypy.config.update('config.cfg')
    cherrypy.quickstart(Root(),'/')
