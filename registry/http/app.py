import enum
import json

from ingredients_http.app import HTTPApplication


class Application(HTTPApplication):

    def setup(self):
        super().setup()
        old_json_encoder = json.JSONEncoder.default

        def json_encoder(self, o):  # pragma: no cover
            if isinstance(o, enum.Enum):
                return str(o.value)

            return old_json_encoder(self, o)

        json.JSONEncoder.default = json_encoder
