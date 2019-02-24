from typing import List

import cherrypy
from ingredients_http.route import Route
from sqlalchemy import desc

from registry.http.router import RegistryRouter
from registry.sql.models.module import Module, ModuleProviderVersion, ModuleProvider
from registry.sql.models.organization import Organization


class VersionsRouter(RegistryRouter):

    def __init__(self):
        super().__init__(uri_base="{organization_name}/{name}/{provider}/versions")

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

            provider: ModuleProvider = session.query(ModuleProvider).filter(
                ModuleProvider.module_id == module.id).filter(ModuleProvider.name == provider).first()
            if provider is None:
                raise cherrypy.HTTPError(404, "The requested provider could not be found")

            output_versions = []
            versions: List[ModuleProviderVersion] = session.query(ModuleProviderVersion).filter(
                ModuleProviderVersion.provider_id == provider.id).order_by(desc(ModuleProviderVersion.created_at))
            for version in versions:
                output_versions.append({
                    "version": version.version  # TODO: root dependencies and providers list, sub modules, ect...
                })

        return {
            'modules': [{
                "source": "%s/%s/%s" % (organization.name, module.name, provider.name),
                "versions": output_versions
            }]
        }
