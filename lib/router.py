from urllib.parse import urlencode, urlparse, parse_qs


class Router:

    def __init__(self, base_url, default_route):
        self._base_url = base_url
        self._default_route = [default_route]
        self._routes = {}

    def build_route(self, route, **kwargs):
        kwargs['route'] = route
        return f"{self._base_url}?{urlencode(kwargs)}"

    def call(self, query):
        args = parse_qs(urlparse(query).query)

        route = args.pop("route", self._default_route)[0]
        handler = self._routes.get(route, None)
        if handler is None:
            raise RuntimeError(f"Unregistered route: '{route}'")

        return handler(**args)

    def register_route(self, route, handler):
        self._routes[route] = handler
