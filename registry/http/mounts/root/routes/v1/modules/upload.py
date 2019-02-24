import hashlib

import cherrypy
from ingredients_http.request_methods import RequestMethods
from ingredients_http.route import Route

from registry.http.router import RegistryRouter
from registry.sql.models.module import Module, ModuleVersion
from registry.sql.models.organization import Organization

ALLOWED_EXTENSIONS = ('.zip', '.tar.gz')


class UploadRouter(RegistryRouter):

    def __init__(self):
        super().__init__(uri_base="{organization_name}/{name}/{provider}/{version}/upload")

    @Route(methods=[RequestMethods.POST])
    @cherrypy.tools.db_session()
    def upload(self, organization_name, name, provider, version, artifact):
        if artifact.filename.endswith(ALLOWED_EXTENSIONS) is False:
            raise cherrypy.HTTPError(415,
                                     'Module Artifact must be one of the following extensions: %s' % ', '.join(
                                         ALLOWED_EXTENSIONS))

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

        m = hashlib.sha256()
        m.update(module.namespace.encode())
        m.update(module.name.encode())
        m.update(module.provider.encode())
        m.update(version.version.encode())
        file_name = m.hexdigest() + "." + artifact.filename

        data = artifact.file

        # upload to s3

        # save filename onto the version for future download
