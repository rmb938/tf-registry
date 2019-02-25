import cherrypy
from apispec import APISpec
from ingredients_http.app import HTTPApplication
from ingredients_http.app_mount import ApplicationMount

from registry.http.spec.plugins.docstring import DocStringPlugin
from registry.http.tools.model import model_out_pagination
from registry.sql.database import Database


class RootMount(ApplicationMount):
    def __init__(self, app: HTTPApplication, database: Database, s3_bucket, s3_client):
        super().__init__(app=app, mount_point='/')
        self.database = database
        self.s3_bucket = s3_bucket
        self.s3_client = s3_client
        self.api_spec = APISpec(
            title='TF Registry API',
            version='0.0.1',
            openapi_version='3.0.2',
            plugins=[DocStringPlugin()]
        )

    def db_session(self):
        cherrypy.request.db_session = self.database.session

    def s3_client_tool(self):
        cherrypy.request.s3_client = self.s3_client

    def __setup_tools(self):
        cherrypy.tools.db_session = cherrypy.Tool('before_request_body', self.db_session, priority=30)
        cherrypy.tools.s3_client = cherrypy.Tool('before_request_body', self.s3_client_tool, priority=30)

        cherrypy.tools.model_out_pagination = cherrypy.Tool('before_handler', model_out_pagination)

    def setup(self):
        self.__setup_tools()
        super().setup()
