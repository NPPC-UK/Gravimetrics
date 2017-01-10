import web
from table_builder import getTable, plantsForm
from login_builder import createLoginForm, loginForm
from data_plotter import generateFakeGraph, generateBalanceHistory
from database import Connection


class Index:
    """
    This is the index of the site
    running this executes everything from it
    currently the default screen is the viewing of plants
    and editing of their target weights
    """

    def __init__(self):
        """
        Constructor for the file
        nothing special here
        """
        self.render = web.template.render('templates/')

    def GET(self, name=None):
        """
        This function processes the GET requests from the site
        """
        if name:
            print(name)

        data = web.input()
        print(data)

        if session.get('loggedin', None):
            f = plantsForm()
            return self.render.index(f, getTable)
        else:
            web.seeother('login')

    def POST(self):
        """
        This function handles any post requests from the site
        """
        f = plantsForm()
        if f.validates():
            return self.render.index(f, getTable)
        else:
            # do whatever we want after a unsuccessful post
            return 'Post hasn\'t worked!'


class Data:
    """
    This generates and prints out the data for a particular plant
    """

    def __init__(self):
        """
        Default constructor for this class, nothing of note
        """
        self.render = web.template.render('templates/')

    def GET(self):
        """
        Uses a given get variable to generate the data required
        """
        plantId = web.input()['plantId']
        return self.render.data(generateBalanceHistory(connection, plantId))


class Login:
    """
    This is the login form
    that takes all of the database information
    rather than have specific users log into the system
    """

    def __init__(self):
        """
        Constructor for the file
        nothing special here
        """
        self.render = web.template.render('templates/')

    def GET(self):
        f = loginForm()
        return self.render.login(f)

    def POST(self):
        f = loginForm()
        if f.validates():
            session.loggedin = True
            data = web.input()
            if connection.create_connection(
                    data['Host'], data['User'], data['Password'], data['Database']) == 0:
                return web.seeother('/')
            else:
                return self.render.login(f)
        else:
            return self.render.login(f)


class Logout:
    """
    Not really a page, just kills the session and redirects
    """

    def GET(self):
        session.kill()
        web.seeother('/login')


if __name__ == '__main__':
    """
    All going well and everything that is required being in place
    this should fire off and the website should load
    """

    # This is some webpy stuff that shouldn't really need changed
    # unless we start some MVC stuff, but please don't make me.
    urls = ('/', 'Index',
            '/index/?', 'Index',
            '/data/?', 'Data',
            '/login/?', 'Login',
            '/logout/?', 'Logout')

    app = web.application(urls, globals())
    session = web.session.Session(app, web.session.DiskStore(
        'sessions'))

    connection = Connection()

    app.run()
