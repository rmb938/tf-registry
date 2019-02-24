from schematics import Model
from schematics.types import StringType, IntType

from registry.http.schematics.types import NameType, ArrowType


class ParamsCreateModule(Model):
    organization_name = NameType(required=True)


class ParamsModule(Model):
    organization_name = NameType(required=True)
    module_name = NameType(required=True)


class ParamsListModule(Model):
    organization_name = NameType(required=True)
    limit = IntType(default=20, min_value=1, max_value=100)
    marker = StringType()


class RequestCreateModule(Model):
    name = NameType(required=True)


class ResponseModule(Model):
    name = NameType(required=True)
    created_at = ArrowType(required=True)
    updated_at = ArrowType(required=True)
