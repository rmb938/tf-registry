from schematics import Model
from schematics.types import StringType, IntType, URLType

from registry.http.schematics.types import NameType, SemVerType, ArrowType


class ParamsCreateVersion(Model):
    organization_name = NameType(required=True)
    module_name = NameType(required=True)
    provider_name = NameType(required=True)


class ParamsVersion(Model):
    organization_name = NameType(required=True)
    module_name = NameType(required=True)
    provider_name = NameType(required=True)
    version = SemVerType(required=True)


class ParamsListVersion(Model):
    organization_name = NameType(required=True)
    module_name = NameType(required=True)
    provider_name = NameType(required=True)
    limit = IntType(default=20, min_value=1, max_value=100)
    marker = StringType()


class RequestCreateVersion(Model):
    version = SemVerType(required=True)


class ResponseVersion(Model):
    version = SemVerType(required=True)
    created_at = ArrowType(required=True)
    updated_at = ArrowType(required=True)


class ResponseCreateVersion(ResponseVersion):
    upload_url = URLType(required=True)
