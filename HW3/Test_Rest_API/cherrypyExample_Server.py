import cherrypy

class HelloWorld(object):

    # exposing to the 8080 port
    @cherrypy.expose
    
    def index(self, name='Bitch'):
        return f'Hello, {name}!'

if __name__ == '__main__':
    cherrypy.quickstart(HelloWorld())

# connect to 127.0.0.1:8080/?name=Gaetano to have another experience. Default experience -> 127.0.0.1:8080