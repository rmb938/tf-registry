from schematics import Model
from schematics.types import IntType, StringType

from registry.http.schematics.types import ArrowType
from registry.http.schematics.types import NameType


class ParamsOrganization(Model):
    organization_name = NameType(required=True)


class ParamsListOrganization(Model):
    limit = IntType(default=20, min_value=1, max_value=100)
    marker = StringType()


class RequestCreateOrganization(Model):
    name = NameType(required=True)


class ResponseOrganization(Model):
    name = NameType(required=True)
    created_at = ArrowType(required=True)
    updated_at = ArrowType(required=True)
