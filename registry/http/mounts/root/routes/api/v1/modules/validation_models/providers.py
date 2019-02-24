from schematics import Model
from schematics.types import StringType, IntType

from registry.http.schematics.types import NameType, ArrowType


class ParamsCreateProvider(Model):
    organization_name = NameType(required=True)
    module_name = NameType(required=True)


class RequestCreateProvider(Model):
    name = NameType(required=True)


class ParamsProvider(Model):
    organization_name = NameType(required=True)
    module_name = NameType(required=True)
    provider_name = NameType(required=True)


class ParamsListProvider(Model):
    organization_name = NameType(required=True)
    module_name = NameType(required=True)
    limit = IntType(default=20, min_value=1, max_value=100)
    marker = StringType()


class ResponseProvider(Model):
    name = NameType(required=True)
    created_at = ArrowType(required=True)
    updated_at = ArrowType(required=True)
