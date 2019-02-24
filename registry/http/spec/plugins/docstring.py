from apispec import BasePlugin
from apispec.exceptions import DuplicateComponentNameError
from apispec.yaml_utils import load_operations_from_docstring
from schematics.contrib.enum_type import EnumType
from schematics.models import FieldDescriptor
from schematics.types import ModelType, DictType, ListType, BooleanType, EmailType, UUIDType, StringType, IntType
from schematics.undefined import UndefinedType

from registry.http.schematics.types import ArrowType, NameType


class DocStringPlugin(BasePlugin):

    def __init__(self):
        self.spec = None

    def init_spec(self, spec):
        super().init_spec(spec)
        self.spec = spec

    def operation_helper(self, path, operations, router, func, **kwargs):
        new_operations = load_operations_from_docstring(func.__doc__)

        if hasattr(func, '_cp_config') is False:
            return None

        cp_config = func._cp_config

        if new_operations is not None:
            for method, data in new_operations.items():

                if cp_config.get('tools.authentication.on', True):
                    data['security'] = [
                        {'Bearer': []}
                    ]

                if 'tools.model_in.cls' in cp_config:
                    model_cls = cp_config['tools.model_in.cls']
                    try:
                        self.spec.components.schema(model_cls.__name__, component=parse_model(self.spec, model_cls))
                    except DuplicateComponentNameError:
                        pass

                    data['requestBody']['required'] = True
                    data['requestBody']['content'] = {
                        'application/json': {
                            'schema': {'$ref': '#/components/schemas/' + model_cls.__name__}
                        }
                    }

                if 'tools.model_params.cls' in cp_config:
                    model_cls = cp_config['tools.model_params.cls']
                    data['parameters'] = data.get('parameters', [])

                    # In query vs in path
                    for key, obj in model_cls.__dict__.items():
                        inn = 'query'
                        if '{' + key + '}' in path:
                            inn = 'path'
                        if isinstance(obj, FieldDescriptor):
                            paramenters = {
                                'name': key,
                                'in': inn,
                                'required': model_cls._fields[key].required,
                                'schema': parse_model_type(self.spec, model_cls._fields[key]),
                            }
                            if isinstance(model_cls._fields[key]._default, UndefinedType) is False:
                                paramenters['schema']['default'] = model_cls._fields[key]._default
                            data['parameters'].append(paramenters)

                if 'tools.model_out.cls' in cp_config:
                    model_cls = cp_config['tools.model_out.cls']
                    try:
                        self.spec.components.schema(model_cls.__name__, component=parse_model(self.spec, model_cls))
                    except DuplicateComponentNameError:
                        pass
                    data['responses'][200]['content'] = {
                        'application/json': {
                            'schema': {'$ref': '#/components/schemas/' + model_cls.__name__}
                        }
                    }

                if 'tools.model_out_pagination.cls' in cp_config:
                    model_cls = cp_config['tools.model_out_pagination.cls']
                    try:
                        self.spec.components.schema(model_cls.__name__, component=parse_model(self.spec, model_cls))
                    except DuplicateComponentNameError:
                        pass
                    self.spec.components.schema("List" + model_cls.__name__,
                                                component={
                                                    'type': 'object',
                                                    'properties': {
                                                        path.split("/")[-1]: {
                                                            'type': 'array',
                                                            'items': {
                                                                '$ref': '#/components/schemas/' + model_cls.__name__}
                                                        },
                                                        path.split("/")[-1] + "_links": {
                                                            'type': 'array',
                                                            'items': {
                                                                'type': 'object',
                                                                'properties': {
                                                                    'href': {
                                                                        'type': 'string'
                                                                    },
                                                                    'rel': {
                                                                        'type': 'string'
                                                                    }
                                                                }
                                                            }
                                                        }
                                                    },
                                                })
                    data['responses'][200]['content'] = {
                        'application/json': {
                            'schema': {'$ref': '#/components/schemas/' + "List" + model_cls.__name__}
                        }
                    }

                if 'tools.enforce_permission.permission_name' in cp_config:
                    data['x-required-permission'] = cp_config['tools.enforce_permission.permission_name']

        operations.update(new_operations)
        return None


def parse_model(spec, model_cls):
    kwargs = {
        'properties': {},
        'type': 'object',
        'required': [],
    }
    for key, obj in model_cls.__dict__.items():
        if isinstance(obj, FieldDescriptor):
            kwargs['properties'][key] = parse_model_type(spec, model_cls._fields[key])
            if model_cls._fields[key].required:
                kwargs['required'].append(key)

    if len(kwargs['required']) == 0:
        del kwargs['required']

    return kwargs


def parse_model_type(spec, model_type):
    swagger_types = {
        StringType: 'string',
        NameType: 'string',
        UUIDType: 'string',
        EmailType: 'string',
        EnumType: 'string',
        ArrowType: 'string',
        IntType: 'integer',
        BooleanType: 'boolean',
        ListType: 'array',
        DictType: 'object',
        ModelType: 'object',
    }

    data = {
        # Find the swagger type, if not found default to string
        # It would be nice to have complex types like uuid, emails, ect...
        # But swagger doesn't support it
        "type": swagger_types.get(model_type.__class__, "string")
    }

    if model_type.__class__ == EnumType:
        data['enum'] = [x.value for x in model_type.enum_class]

    if model_type.__class__ == ListType:
        if model_type.field.__class__ == ModelType:
            try:
                spec.components.schema(model_type.field.model_class.__name__,
                                       component=parse_model(spec, model_type.field.model_class))
            except DuplicateComponentNameError:
                pass
            data['items'] = {
                '$ref': '#/components/schemas/' + model_type.field.model_class.__name__
            }
        else:
            data['items'] = parse_model_type(spec, model_type.field)

    if model_type.__class__ == DictType:
        data['additionalProperties'] = parse_model_type(spec, model_type.field)

    if model_type.__class__ == ModelType:
        try:
            spec.components.schema(model_type.model_class.__name__, component=parse_model(spec, model_type.model_class))
        except DuplicateComponentNameError:
            pass
        data['additionalProperties'] = {
            '$ref': '#/components/schemas/' + model_type.model_class.__name__
        }

    return data
