from typing import List

import cherrypy
from ingredients_http.request_methods import RequestMethods
from ingredients_http.route import Route
from ingredients_http.router import Router

from registry.sql.models.module import Module
from registry.sql.models.organization import Organization
from registry.sql.models.version import Version


class VersionsRouter(Router):

    def __init__(self):
        super().__init__(uri_base="{organization_name}/{name}/{provider}/versions")

    @Route(methods=[RequestMethods.POST])
    def create(self, namespace, name, provider):
        pass

    @Route()
    @cherrypy.tools.json_out()
    @cherrypy.tools.db_session()
    def list(self, organization_name, name, provider):
        with cherrypy.request.db_session() as session:
            organization: Organization = session.query(Organization).filter(
                Organization.name == organization_name).first()

            if organization is None:
                raise cherrypy.HTTPError(404, "The request organization could not be found")

            module: Module = session.query(Module).filter(Module.organization_id == organization.id).filter(
                Module.name == name).first()

            if module is None:
                raise cherrypy.HTTPError(404, "The requested module could not be found")

            output_versions = []
            versions: List[Version] = session.query(Version).filter(Version.module_id == module.id).filter(
                Version.provider == provider)
            for version in versions:
                output_versions.append({
                    "version": version.version  # TODO: root dependencies and providers list, sub modules, ect...
                })

        return {
            'modules': [{
                "source": "%s/%s/%s" % (module.namespace, module.name, module.provider),
                "versions": output_versions
            }]
        }
