import arrow
import arrow.parser
from schematics.exceptions import ConversionError
from schematics.types import StringType, BaseType


class NameType(StringType):

    def __init__(self, **kwargs):
        super().__init__(min_length=3, regex='^[a-zA-Z][a-zA-Z0-9]*$', **kwargs)


class ArrowType(BaseType):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_native(self, value, context=None):
        if not isinstance(value, arrow.Arrow):
            try:
                value = arrow.get(value)
            except arrow.parser.ParserError:
                raise ConversionError('Could not parse %s. Should be ISO 8601.' % value)
        return value

    def to_primitive(self, value, context=None):
        return value.isoformat()
