import cherrypy
from ingredients_http.app import HTTPApplication
from ingredients_http.app_mount import ApplicationMount

from registry.sql.database import Database


class RootMount(ApplicationMount):
    def __init__(self, app: HTTPApplication, database: Database):
        super().__init__(app=app, mount_point='/')
        self.database = database

    def db_session(self):
        cherrypy.request.db_session = self.database.session

    def __setup_tools(self):
        cherrypy.tools.db_session = cherrypy.Tool('before_request_body', self.db_session, priority=30)

    def setup(self):
        self.__setup_tools()
        super().setup()
