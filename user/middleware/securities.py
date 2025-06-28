# middlewares/securities.py

class SessionSecurityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = request.META.get('REMOTE_ADDR')
        ua = request.META.get('HTTP_USER_AGENT')

        session_ip = request.session.get('ip')
        session_ua = request.session.get('ua')

        if session_ip and session_ua:
            if session_ip != ip or session_ua != ua:
                request.session.flush()  # or logout
        else:
            request.session['ip'] = ip
            request.session['ua'] = ua

        return self.get_response(request)
