import cherrypy

class HelloWorld(object):
    @cherrypy.expose

    # this creates a text field and a button, to send text with a button :)
    def index(self):
        return '''
            <form method="get" action="greet">
                <input type="text" name="name" />
                <button type="submit">Greet me!</button>
            </form>
        '''

    @cherrypy.expose
    def greet(self, name = "If you can get me, you are goooood :)"):
        return f'Hello, {name}!'

if __name__ == '__main__':
    cherrypy.quickstart(HelloWorld())
