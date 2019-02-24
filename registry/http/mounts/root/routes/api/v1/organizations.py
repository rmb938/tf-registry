import base64
import uuid
from typing import List

import cherrypy
from ingredients_http.request_methods import RequestMethods
from ingredients_http.route import Route
from sqlalchemy import desc

from registry.http.mounts.root.routes.api.v1.validation_models.organizations import RequestCreateOrganization, \
    ResponseOrganization, ParamsOrganization, ParamsListOrganization
from registry.http.router import RegistryRouter
from registry.sql.models.module import Module
from registry.sql.models.organization import Organization


class OrganizationRouter(RegistryRouter):

    def __init__(self):
        super().__init__(uri_base='organizations')

    @Route(methods=[RequestMethods.POST])
    @cherrypy.tools.db_session()
    @cherrypy.tools.model_in(cls=RequestCreateOrganization)
    @cherrypy.tools.model_out(cls=ResponseOrganization)
    def create(self):
        """Create an Organization
        ---
        post:
          description: Create an Organization
          tags:
            - organization
          requestBody:
            description: Organization to create
          responses:
            200:
              description: The created Organization

        """
        model: RequestCreateOrganization = cherrypy.request.model
        with cherrypy.request.db_session() as session:
            organization = session.query(Organization).filter(Organization.name == model.name).first()
            if organization is not None:
                raise cherrypy.HTTPError(409, 'An organization with the requested name already exists')

            organization = Organization()
            organization.name = model.name
            session.add(organization)
            session.commit()
            session.refresh(organization)

        response = ResponseOrganization()
        response.name = organization.name
        response.created_at = organization.created_at
        response.updated_at = organization.updated_at

        return response

    @Route(route='{organization_name}')
    @cherrypy.tools.db_session()
    @cherrypy.tools.model_params(cls=ParamsOrganization)
    @cherrypy.tools.model_out(cls=ResponseOrganization)
    def read(self, organization_name):
        """Get an Organization
        ---
        get:
          description: Get an Organization
          tags:
            - organization
          responses:
            200:
              description: The Organization
        """
        with cherrypy.request.db_session() as session:
            organization = session.query(Organization).filter(Organization.name == organization_name).first()
            if organization is None:
                raise cherrypy.HTTPError(404, 'An organization with the requested name does not exist.')

        response = ResponseOrganization()
        response.name = organization.name
        response.created_at = organization.created_at
        response.updated_at = organization.updated_at

        return response

    @Route()
    @cherrypy.tools.db_session()
    @cherrypy.tools.model_params(cls=ParamsListOrganization)
    @cherrypy.tools.model_out_pagination(cls=ResponseOrganization)
    def list(self, limit, marker):
        """List Organizations
        ---
        get:
          description: List Organizations
          tags:
            - organization
          responses:
            200:
              description: List of Organizations

        """
        with cherrypy.request.db_session() as session:
            organizations: List[Organization] = session.query(Organization).order_by(desc(Organization.created_at))
            if marker is not None:
                try:
                    marker_id = uuid.UUID(bytes=base64.urlsafe_b64decode(marker + "=="))
                except ValueError:
                    raise cherrypy.HTTPError(400, 'Invalid organization list marker')
                marker: Organization = session.query(Organization).filter(Organization.id == marker_id).first()
                if marker is None:
                    raise cherrypy.HTTPError(404, 'Unknown organization list marker')

                organizations = organizations.filter(Organization.created_at < marker.created_at)
            organizations = organizations.limit(limit + 1).all()

            if len(organizations) > limit:
                marker = base64.urlsafe_b64encode(organizations[-1].id.bytes).decode().rstrip("=")
                del organizations[-1]
            else:
                marker = None

            response = []
            for o in organizations:
                org = ResponseOrganization()
                org.name = o.name
                org.created_at = o.created_at
                org.updated_at = o.updated_at
                response.append(org)

            return response, marker

    @Route(route='{organization_name}', methods=[RequestMethods.PUT])
    @cherrypy.tools.db_session()
    def update(self, organization_name):
        # TODO: allow changing the org name
        pass

    @Route(route='{organization_name}', methods=[RequestMethods.DELETE])
    @cherrypy.tools.db_session()
    @cherrypy.tools.model_params(cls=ParamsOrganization)
    def delete(self, organization_name):
        """Delete an Organization
        ---
        delete:
          description: Delete an Organization
          tags:
            - organization
          responses:
            204:
              description: Organization deleted
        """
        cherrypy.response.status = 204
        with cherrypy.request.db_session() as session:
            organization = session.query(Organization).filter(Organization.name == organization_name).first()
            if organization is None:
                raise cherrypy.HTTPError(404, 'An organization with the requested name does not exist.')

            module = session.query(Module).filter(Module.organization_id == organization.id).scalar()
            if module is not None:
                raise cherrypy.HTTPError(404, 'Organization cannot be deleted while it has modules.')

            organization.delete()
            session.commit()
