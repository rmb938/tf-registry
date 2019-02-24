from typing import Callable, List

from ingredients_http.request_methods import RequestMethods
from ingredients_http.router import Router


class RegistryRouter(Router):
    def on_register(self, uri: str, action: Callable, methods: List[RequestMethods]):
        self.mount.api_spec.path(path=uri, router=self, func=action)
