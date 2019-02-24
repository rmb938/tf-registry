import cherrypy
from ingredients_http.route import Route
from ingredients_http.router import Router


class WellKnownRouter(Router):

    def __init__(self):
        super().__init__(uri_base=".well-known")

    @Route(route="terraform.json")
    @cherrypy.tools.json_out()
    def terraform(self):
        return {
            "modules.v1": cherrypy.request.base + "/v1/modules"
        }
