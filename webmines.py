
import cherrypy
import os
current_dir = os.path.dirname(os.path.abspath(__file__))

class Root:
    
    def __init__(self):
        self.html = {}
    
    @cherrypy.expose
    def index(self):
        return open('static/index.html').read()
        

if __name__ == "__main__":
    cherrypy.config.update('config.cfg')
    
    cherrypy.quickstart(Root())
