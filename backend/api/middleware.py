from django.http import HttpResponse

class SimpleCorsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Handle the preflight OPTIONS request
        if request.method == "OPTIONS":
            # Preflight requests don't need a body, just the right headers
            response = HttpResponse(status=204) # 204 No Content
            # Allow the specific origin that's making the request
            response["Access-Control-Allow-Origin"] = request.headers.get("Origin", "*")
            # Allow credentials (cookies)
            response["Access-Control-Allow-Credentials"] = "true"
            # Specify allowed methods
            response["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            # Allow the headers the client is asking for
            response["Access-Control-Allow-Headers"] = request.headers.get("Access-Control-Request-Headers", "*")
            # Cache the preflight response for 1 day
            response["Access-Control-Max-Age"] = "86400"
            return response

        # For all other actual requests, process as usual
        response = self.get_response(request)

        # Add the CORS header to the actual response, too
        origin = request.headers.get("Origin")
        if origin and ("vercel.app" in origin or "localhost" in origin):
            response["Access-Control-Allow-Origin"] = origin
            response["Access-Control-Allow-Credentials"] = "true"

        return response 