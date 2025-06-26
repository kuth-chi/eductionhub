class LogRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print("Authorization Header:", request.META.get('HTTP_AUTHORIZATION'))
        return self.get_response(request)