import cherrypy

class GreetingGenerator(object):
    @cherrypy.expose
    def GET(self, *path, **query):
        name = query.get('name')
        surname = query.get('surname')
        if name and surname:
            return "Hi " + name + " " + surname + "!"
        else:
            return '''
                <html>
                    <body>
                        <form method="get" action="">
                            Name: <input type="text" name="name" />
                            Surname: <input type="text" name="surname" />
                            <input type="submit" value="Greet me!" />
                        </form>
                    </body>
                </html>
            '''
    index = GET
    
cherrypy.quickstart(GreetingGenerator(), '/')
