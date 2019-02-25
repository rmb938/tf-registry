import datetime

import cherrypy
from ingredients_http.route import Route

from registry.http.router import RegistryRouter
from registry.sql.models.module import Module, ModuleProviderVersion, ModuleProvider
from registry.sql.models.organization import Organization


class DownloadRouter(RegistryRouter):

    def __init__(self):
        super().__init__(uri_base="{organization_name}/{name}/{provider}/{version}/download")

    @Route()
    @cherrypy.tools.db_session()
    @cherrypy.tools.s3_client()
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

            provider: ModuleProvider = session.query(ModuleProvider).filter(
                ModuleProvider.module_id == module.id).filter(ModuleProvider.name == provider).first()
            if provider is None:
                raise cherrypy.HTTPError(404, "The requested provider could not be found")

            version = session.query(ModuleProviderVersion).filter(ModuleProviderVersion.provider_id == provider.id) \
                .filter(ModuleProviderVersion.version == version).first()

            if version is None:
                raise cherrypy.HTTPError(404, "The requested module version could not be found")

            # We are going to assume the module is tar.gz
            # other types will not be supported
            # Supporting multiple formats is hard
            # Terraform enterprise only supports tar.gz so that should be a safe assumption

            s3_client = cherrypy.request.s3_client
            get_object_url = s3_client.generate_presigned_url(
                ClientMethod='get_object',
                Params={'Bucket': self.mount.s3_bucket, 'Key': str(version.id),
                        'ResponseContentDisposition': 'attachment;filename=' + organization.name + '-' + module.name + '-' + provider.name + '-' + version.version + '.tar.gz'},
                ExpiresIn=datetime.timedelta(minutes=5).seconds
            )

            cherrypy.response.headers['X-Terraform-Get'] = get_object_url + '&archive=tar.gz'
