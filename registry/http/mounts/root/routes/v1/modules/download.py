import cherrypy
from ingredients_http.route import Route

from registry.http.router import RegistryRouter
from registry.sql.models.module import Module, ModuleVersion
from registry.sql.models.organization import Organization


class DownloadRouter(RegistryRouter):

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

            version = session.query(ModuleVersion).filter(ModuleVersion.module_id == module.id).filter(
                ModuleVersion.provider == provider).filter(ModuleVersion.version == version).first()

            if version is None:
                raise cherrypy.HTTPError(404, "The requested module version could not be found")

            cherrypy.response.headers['X-Terraform-Get'] = ''  # TODO: generate pre-signed url
