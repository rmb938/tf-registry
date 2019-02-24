import base64
import uuid
from typing import List

import cherrypy
from ingredients_http.request_methods import RequestMethods
from ingredients_http.route import Route
from sqlalchemy import desc

from registry.http.mounts.root.routes.api.v1.modules.validation_models.versions import ParamsCreateVersion, \
    ParamsVersion, ParamsListVersion, RequestCreateVersion, ResponseVersion
from registry.http.router import RegistryRouter
from registry.sql.models.module import Module, ModuleProvider, ModuleProviderVersion
from registry.sql.models.organization import Organization


class ModuleProviderVersionRouter(RegistryRouter):
    def __init__(self):
        super().__init__(uri_base='{organization_name}/{module_name}/providers/{provider_name}/versions')

    @Route(methods=[RequestMethods.POST])
    @cherrypy.tools.db_session()
    @cherrypy.tools.model_params(cls=ParamsCreateVersion)
    @cherrypy.tools.model_in(cls=RequestCreateVersion)
    @cherrypy.tools.model_out(cls=ResponseVersion)
    def create(self, organization_name, module_name, provider_name):
        """Create a Version
        ---
        post:
          description: Create a Version
          tags:
            - module
            - provider
            - version
          requestBody:
            description: Version to create
          responses:
            200:
              description: The created Version
        """
        model: RequestCreateVersion = cherrypy.request.model
        with cherrypy.request.db_session() as session:
            organization: Organization = session.query(Organization).filter(
                Organization.name == organization_name).first()
            if organization is None:
                raise cherrypy.HTTPError(404, 'An organization with the requested name does not exist.')

            module: Module = session.query(Module).filter(Module.organization_id == organization.id).filter(
                Module.name == module_name).first()
            if module is None:
                raise cherrypy.HTTPError(404, 'A module with the requested name does not exist.')

            provider: ModuleProvider = session.query(ModuleProvider).filter(
                ModuleProvider.module_id == module.id).filter(ModuleProvider.name == provider_name).first()
            if provider is None:
                raise cherrypy.HTTPError(409, 'A provider with the requested name does not exist.')

            version: ModuleProviderVersion = session.query(ModuleProviderVersion).filter(
                ModuleProviderVersion.provider_id == provider.id).filter(
                ModuleProviderVersion.version == str(model.version)).first()
            if version is not None:
                raise cherrypy.HTTPError(409, 'The requested version already exists')

            version = ModuleProviderVersion()
            version.provider_id = provider.id
            version.version = str(model.version)
            session.add(version)
            session.commit()
            session.refresh(version)

        response = ResponseVersion()
        response.version = version.version
        response.created_at = version.created_at
        response.updated_at = version.updated_at

        return response

    @Route(route='{version}')
    @cherrypy.tools.db_session()
    @cherrypy.tools.model_params(cls=ParamsVersion)
    @cherrypy.tools.model_out(cls=ResponseVersion)
    def read(self, organization_name, module_name, provider_name, version):
        """Get a Version
        ---
        get:
          description: Get a Version
          tags:
            - module
            - provider
            - version
          responses:
            200:
              description: The Version
        """
        with cherrypy.request.db_session() as session:
            organization: Organization = session.query(Organization).filter(
                Organization.name == organization_name).first()
            if organization is None:
                raise cherrypy.HTTPError(404, 'An organization with the requested name does not exist.')

            module: Module = session.query(Module).filter(Module.organization_id == organization.id).filter(
                Module.name == module_name).first()
            if module is None:
                raise cherrypy.HTTPError(404, 'A module with the requested name does not exist.')

            provider: ModuleProvider = session.query(ModuleProvider).filter(
                ModuleProvider.module_id == module.id).filter(ModuleProvider.name == provider_name).first()
            if provider is None:
                raise cherrypy.HTTPError(409, 'A provider with the requested name does not exist.')

            version: ModuleProviderVersion = session.query(ModuleProviderVersion).filter(
                ModuleProviderVersion.provider_id == provider.id).filter(
                ModuleProviderVersion.version == str(version)).first()
            if version is None:
                raise cherrypy.HTTPError(409, 'The requested version does not exist.')

        response = ResponseVersion()
        response.version = version.version
        response.created_at = version.created_at
        response.updated_at = version.updated_at

        return response

    @Route()
    @cherrypy.tools.db_session()
    @cherrypy.tools.model_params(cls=ParamsListVersion)
    @cherrypy.tools.model_out_pagination(cls=ResponseVersion)
    def list(self, organization_name, module_name, provider_name, limit, marker):
        """List Versions
        ---
        get:
          description: List Versions
          tags:
            - module
            - provider
            - version
          responses:
            200:
              description: List of Versions
        """
        with cherrypy.request.db_session() as session:
            organization: Organization = session.query(Organization).filter(
                Organization.name == organization_name).first()
            if organization is None:
                raise cherrypy.HTTPError(404, 'An organization with the requested name does not exist.')

            module: Module = session.query(Module).filter(Module.organization_id == organization.id).filter(
                Module.name == module_name).first()
            if module is None:
                raise cherrypy.HTTPError(404, 'A module with the requested name does not exist.')

            provider: ModuleProvider = session.query(ModuleProvider).filter(
                ModuleProvider.module_id == module.id).filter(ModuleProvider.name == provider_name).first()
            if provider is None:
                raise cherrypy.HTTPError(409, 'A provider with the requested name does not exist.')

            versions: List[ModuleProviderVersion] = session.query(ModuleProviderVersion).filter(
                ModuleProviderVersion.provider_id == provider.id).order_by(desc(ModuleProviderVersion.created_at))
            if marker is not None:
                try:
                    marker_id = uuid.UUID(bytes=base64.urlsafe_b64decode(marker + "=="))
                except ValueError:
                    raise cherrypy.HTTPError(400, 'Invalid version list marker')
                marker: ModuleProviderVersion = session.query(ModuleProviderVersion).filter(
                    ModuleProviderVersion.id == marker_id).first()
                if marker is None:
                    raise cherrypy.HTTPError(404, 'Unknown version list marker')

                versions = versions.filter(ModuleProviderVersion.created_at < marker.created_at)
            versions = versions.limit(limit + 1).all()

            if len(versions) > limit:
                marker = base64.urlsafe_b64encode(versions[-1].id.bytes).decode().rstrip("=")
                del versions[-1]
            else:
                marker = None

            response = []
            for v in versions:
                version = ResponseVersion()
                version.version = v.version
                version.created_at = v.created_at
                version.updated_at = v.updated_at
                response.append(version)

            return response, marker

    @Route(route='{version}', methods=[RequestMethods.DELETE])
    @cherrypy.tools.db_session()
    @cherrypy.tools.model_params(cls=ParamsVersion)
    def delete(self, organization_name, module_name, provider_name, version):
        """Delete a Version
        ---
        delete:
          description: Delete a Version
          tags:
            - module
            - provider
            - version
          responses:
            204: Version deleted
        """
        cherrypy.response.status = 204
        with cherrypy.request.db_session() as session:
            organization: Organization = session.query(Organization).filter(
                Organization.name == organization_name).first()
            if organization is None:
                raise cherrypy.HTTPError(404, 'An organization with the requested name does not exist.')

            module: Module = session.query(Module).filter(Module.organization_id == organization.id).filter(
                Module.name == module_name).first()
            if module is None:
                raise cherrypy.HTTPError(404, 'A module with the requested name does not exist.')

            provider: ModuleProvider = session.query(ModuleProvider).filter(
                ModuleProvider.module_id == module.id).filter(ModuleProvider.name == provider_name).first()
            if provider is None:
                raise cherrypy.HTTPError(409, 'A provider with the requested name does not exist.')

            version = session.query(ModuleProviderVersion).filter(
                ModuleProviderVersion.provider_id == provider.id).filter(
                ModuleProviderVersion.version == str(version)).first()
            if version is None:
                raise cherrypy.HTTPError(409, 'The requested version does not exist.')

            version.delete()

            # TODO: delete object from s3 if it exists

            session.commit()
