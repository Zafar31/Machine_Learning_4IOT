import cherrypy

class GreetingGenerator(object):
    @cherrypy.expose
    def index(self, name=None, surname=None):
        if name and surname:
            return "Hi " + name + " " + surname + "!"
        else:
            return '''
                <html>
                    <body>
                        <form method="get" action="index">
                            Name: <input type="text" name="name" />
                            Surname: <input type="text" name="surname" />
                            <input type="submit" value="Greet me!" />
                        </form>
                    </body>
                </html>
            '''

cherrypy.quickstart(GreetingGenerator())