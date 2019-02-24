from urllib.parse import urlencode

import cherrypy
from cherrypy import _json as json
from ingredients_http.errors.validation import ResponseValidationError
from schematics import Model
from schematics.exceptions import DataError


def model_out_pagination(cls=None, list_name=None):
    def model_handler(*args, **kwargs):
        nonlocal list_name

        if list_name is None:
            list_name = cherrypy.serving.request.path_info.split("/")[-1]
        data = {
            list_name: []
        }

        values, marker = cherrypy.serving.request._model_inner_handler(*args, **kwargs)
        for value in values:
            if issubclass(value.__class__, Model) is False:
                raise cherrypy.HTTPError(500, "Output Model class (" + value.__class__.__name__ +
                                         ") is not a subclass of  " + Model.__module__ + "." + Model.__name__)
            if cls is not None and value.__class__ != cls:
                raise cherrypy.HTTPError(500, "Output Model class (" + value.__class__.__name__ +
                                         ") does not match given class " + cls.__name__)
            try:
                value.validate()
            except DataError as e:
                raise ResponseValidationError(e)

            data[list_name].append(value.to_native())

        data[list_name + "_links"] = []
        if marker is not None:
            req_params = cherrypy.serving.request.params

            for k, v in dict(req_params).items():
                if v is None:
                    del req_params[k]

            req_params['marker'] = marker
            data[list_name + "_links"] = [
                {
                    "href": cherrypy.url(qs=urlencode(req_params)),
                    "rel": "next"
                }
            ]

        return json.encode(data)

    request = cherrypy.serving.request
    if request.handler is None:  # pragma: no cover
        return
    request._model_inner_handler = request.handler
    request.handler = model_handler
    cherrypy.serving.response.headers['Content-Type'] = 'application/json'
