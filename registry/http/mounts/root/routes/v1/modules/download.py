import cherrypy
from ingredients_http.route import Route
from ingredients_http.router import Router

from registry.sql.models.module import Module
from registry.sql.models.organization import Organization
from registry.sql.models.version import Version


class DownloadRouter(Router):

    def __init__(self):
        super().__init__(uri_base="{organization_name}/{name}/{provider}/{version}/download")

    @Route()
    @cherrypy.tools.db_session()
    def download(self, organization_name, name, provider, version):
        with cherrypy.request.db_session() as session:
            organization: Organization = session.query(Organization).filter(
                Organization.name == organization_name).first()

            if organization is None:
                raise cherrypy.HTTPError(404, "The request organization could not be found")

            module: Module = session.query(Module).filter(Module.organization_id == organization.id).filter(
                Module.name == name).first()

            if module is None:
                raise cherrypy.HTTPError(404, "The requested module could not be found")

            version = session.query(Version).filter(Version.module_id == module.id).filter(
                Version.provider == provider).filter(Version.version == version).first()

            if version is None:
                raise cherrypy.HTTPError(404, "The requested module version could not be found")

            cherrypy.response.headers['X-Terraform-Get'] = ''  # TODO: generate pre-signed url
