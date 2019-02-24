import base64
import uuid
from typing import List

import cherrypy
from ingredients_http.request_methods import RequestMethods
from ingredients_http.route import Route
from sqlalchemy import desc

from registry.http.mounts.root.routes.api.v1.modules.validation_models.providers import ParamsCreateProvider, \
    RequestCreateProvider, ResponseProvider, ParamsProvider, ParamsListProvider
from registry.http.router import RegistryRouter
from registry.sql.models.module import Module, ModuleProvider, ModuleProviderVersion
from registry.sql.models.organization import Organization


class ModuleProviderRouter(RegistryRouter):

    def __init__(self):
        super().__init__(uri_base='{organization_name}/{module_name}/providers')

    @Route(methods=[RequestMethods.POST])
    @cherrypy.tools.db_session()
    @cherrypy.tools.model_params(cls=ParamsCreateProvider)
    @cherrypy.tools.model_in(cls=RequestCreateProvider)
    @cherrypy.tools.model_out(cls=ResponseProvider)
    def create(self, organization_name, module_name):
        """Create a Provider
        ---
        post:
          description: Create a Provider
          tags:
            - module
            - provider
          requestBody:
            description: Provider to create
          responses:
            200:
              description: The created Provider
        """
        model: RequestCreateProvider = cherrypy.request.model
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
                ModuleProvider.module_id == module.id).filter(ModuleProvider.name == model.name).first()
            if provider is not None:
                raise cherrypy.HTTPError(409, 'A provider with the requested name already exists')

            provider = ModuleProvider()
            provider.module_id = module.id
            provider.name = model.name
            session.add(provider)
            session.commit()
            session.refresh(provider)

        response = ResponseProvider()
        response.name = provider.name
        response.created_at = provider.created_at
        response.updated_at = provider.updated_at

        return response

    @Route(route='{provider_name}')
    @cherrypy.tools.db_session()
    @cherrypy.tools.model_params(cls=ParamsProvider)
    @cherrypy.tools.model_out(cls=ResponseProvider)
    def read(self, organization_name, module_name, provider_name):
        """Get a Provider
        ---
        get:
          description: Get a Provider
          tags:
            - module
            - provider
          responses:
            200:
              description: The Provider
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

        response = ResponseProvider()
        response.name = provider.name
        response.created_at = provider.created_at
        response.updated_at = provider.updated_at

        return response

    @Route()
    @cherrypy.tools.db_session()
    @cherrypy.tools.model_params(cls=ParamsListProvider)
    @cherrypy.tools.model_out_pagination(cls=ResponseProvider)
    def list(self, organization_name, module_name, limit, marker):
        """List Providers
        ---
        get:
          description: List Providers
          tags:
            - module
            - provider
          responses:
            200:
              description: List of Providers
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

            providers: List[ModuleProvider] = session.query(ModuleProvider).filter(
                ModuleProvider.module_id == module.id).order_by(desc(ModuleProvider.created_at))
            if marker is not None:
                try:
                    marker_id = uuid.UUID(bytes=base64.urlsafe_b64decode(marker + "=="))
                except ValueError:
                    raise cherrypy.HTTPError(400, 'Invalid provider list marker')
                marker: ModuleProvider = session.query(ModuleProvider).filter(ModuleProvider.id == marker_id).first()
                if marker is None:
                    raise cherrypy.HTTPError(404, 'Unknown provider list marker')

                providers = providers.filter(ModuleProvider.created_at < marker.created_at)
            providers = providers.limit(limit + 1).all()

        if len(providers) > limit:
            marker = base64.urlsafe_b64encode(providers[-1].id.bytes).decode().rstrip("=")
            del providers[-1]
        else:
            marker = None

        response = []
        for p in providers:
            provider = ResponseProvider()
            provider.name = p.name
            provider.created_at = p.created_at
            provider.updated_at = p.updated_at
            response.append(provider)

        return response, marker

    @Route(route='{provider_name}', methods=[RequestMethods.DELETE])
    @cherrypy.tools.db_session()
    @cherrypy.tools.model_params(cls=ParamsProvider)
    def delete(self, organization_name, module_name, provider_name):
        """Delete a Provider
        ---
        delete:
          description: Delete a Provider
          tags:
            - module
            - provider
          responses:
            204: Provider deleted
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

            provider = session.query(ModuleProvider).filter(
                ModuleProvider.module_id == module.id).filter(ModuleProvider.name == provider_name).first()
            if provider is None:
                raise cherrypy.HTTPError(404, 'A provider with the requested name does not exist.')

            version = session.query(ModuleProviderVersion).filter(
                ModuleProviderVersion.provider_id == provider.id).scalar()
            if version is not None:
                raise cherrypy.HTTPError(409, 'Provider cannot be deleted while it has versions.')

            provider.delete()
            session.commit()
