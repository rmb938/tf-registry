import base64
import uuid
from typing import List

import cherrypy
from ingredients_http.request_methods import RequestMethods
from ingredients_http.route import Route
from sqlalchemy import desc

from registry.http.mounts.root.routes.api.v1.modules.validation_models.modules import ParamsModule, ParamsListModule, \
    ParamsCreateModule, RequestCreateModule, ResponseModule
from registry.http.router import RegistryRouter
from registry.sql.models.module import Module, ModuleProvider
from registry.sql.models.organization import Organization


class ModuleRouter(RegistryRouter):

    def __init__(self):
        super().__init__(uri_base='{organization_name}')

    @Route(methods=[RequestMethods.POST])
    @cherrypy.tools.db_session()
    @cherrypy.tools.model_params(cls=ParamsCreateModule)
    @cherrypy.tools.model_in(cls=RequestCreateModule)
    @cherrypy.tools.model_out(cls=ResponseModule)
    def create(self, organization_name):
        """Create a Module
        ---
        post:
          description: Create a Module
          tags:
            - module
          requestBody:
            description: Module to create
          responses:
            200:
              description: The created Modeul
        """
        model: RequestCreateModule = cherrypy.request.model
        with cherrypy.request.db_session() as session:
            organization = session.query(Organization).filter(Organization.name == organization_name).first()
            if organization is None:
                raise cherrypy.HTTPError(404, 'An organization with the requested name does not exist.')

            module = session.query(Module).filter(Module.organization_id == organization.id).filter(
                Module.name == model.name).first()
            if module is not None:
                raise cherrypy.HTTPError(409, 'A module with the requested name already exists')

            module = Module()
            module.organization_id = organization.id
            module.name = model.name
            session.add(module)
            session.commit()
            session.refresh(module)

        response = ResponseModule()
        response.name = module.name
        response.created_at = module.created_at
        response.updated_at = module.updated_at

        return response

    @Route(route='{module_name}')
    @cherrypy.tools.db_session()
    @cherrypy.tools.model_params(cls=ParamsModule)
    @cherrypy.tools.model_out(cls=ResponseModule)
    def read(self, organization_name, module_name):
        """Get a Module
        ---
        get:
          description: Get a Module
          tags:
            - module
          responses:
            200:
              description: The Module
        """
        with cherrypy.request.db_session() as session:
            organization = session.query(Organization).filter(Organization.name == organization_name).first()
            if organization is None:
                raise cherrypy.HTTPError(404, 'An organization with the requested name does not exist.')

            module = session.query(Module).filter(Module.organization_id == organization.id).filter(
                Module.name == module_name).first()
            if module is None:
                raise cherrypy.HTTPError(409, 'A module with the requested name does not exist.')

        response = ResponseModule()
        response.name = module.name
        response.created_at = module.created_at
        response.updated_at = module.updated_at

        return response

    @Route()
    @cherrypy.tools.db_session()
    @cherrypy.tools.model_params(cls=ParamsListModule)
    @cherrypy.tools.model_out_pagination(cls=ResponseModule)
    def list(self, organization_name, limit, marker):
        """List Modules
        ---
        get:
          description: List Modules
          tags:
            - module
          responses:
            200:
              description: List of Modules
        """
        with cherrypy.request.db_session() as session:
            organization = session.query(Organization).filter(Organization.name == organization_name).first()
            if organization is None:
                raise cherrypy.HTTPError(404, 'An organization with the requested name does not exist.')

            modules: List[Module] = session.query(Module).filter(Module.organization_id == organization.id).order_by(
                desc(Module.created_at))
            if marker is not None:
                try:
                    marker_id = uuid.UUID(bytes=base64.urlsafe_b64decode(marker + "=="))
                except ValueError:
                    raise cherrypy.HTTPError(400, 'Invalid module list marker')
                marker: Module = session.query(Module).filter(Module.id == marker_id).first()
                if marker is None:
                    raise cherrypy.HTTPError(404, 'Unknown module list marker')

                modules = modules.filter(Module.created_at < marker.created_at)
            modules = modules.limit(limit + 1).all()

            if len(modules) > limit:
                marker = base64.urlsafe_b64encode(modules[-1].id.bytes).decode().rstrip("=")
                del modules[-1]
            else:
                marker = None

            response = []
            for m in modules:
                module = ResponseModule()
                module.name = m.name
                module.created_at = m.created_at
                module.updated_at = m.updated_at
                response.append(module)

            return response, marker

    @Route(route='{module_name}', methods=[RequestMethods.DELETE])
    @cherrypy.tools.db_session()
    @cherrypy.tools.model_params(cls=ParamsModule)
    def delete(self, organization_name, module_name):
        """Delete a Module
        ---
        delete:
          description: Delete a Module
          tags:
            - module
          responses:
            204:
              description: Module deleted
        """
        cherrypy.response.status = 204
        with cherrypy.request.db_session() as session:
            organization = session.query(Organization).filter(Organization.name == organization_name).first()
            if organization is None:
                raise cherrypy.HTTPError(404, 'An organization with the requested name does not exist.')

            module = session.query(Module).filter(Module.organization_id == organization.id).filter(
                Module.name == module_name).first()
            if module is None:
                raise cherrypy.HTTPError(404, 'A module with the requested name does not exist.')

            provider = session.query(ModuleProvider).filter(ModuleProvider.module_id == module.id).scalar()
            if provider is not None:
                raise cherrypy.HTTPError(409, 'Module cannot be deleted while it has providers.')

        module.delete()
        session.commit()
