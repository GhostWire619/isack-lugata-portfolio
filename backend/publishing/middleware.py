from django.shortcuts import redirect
from django.utils.cache import patch_cache_control


class RequireAdminOTP:
    """An authenticated password session alone cannot access publishing tools."""
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        private = request.path.startswith(('/admin/', '/security/'))
        if request.path.startswith('/admin/') and request.path != '/admin/logout/' and request.user.is_authenticated and request.user.is_staff and not request.user.is_verified():
            if request.method == 'GET' and (request.path.startswith('/admin/ai/') or request.path in ['/admin/', '/admin/articles/', '/admin/articles/new/', '/admin/advertising/preview/', '/admin/analytics/'] or request.path.endswith('/edit/')):
                request.session['journal_admin_next'] = request.get_full_path()
            response = redirect('/security/verify/')
        else:
            response = self.get_response(request)
        if private:
            patch_cache_control(response, no_store=True, private=True)
            response['X-Robots-Tag'] = 'noindex, nofollow'
        return response


class ProtocolCORS:
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        from django.conf import settings
        from django.http import HttpResponse
        protocol = request.path.startswith(('/oauth/', '/.well-known/')) or request.path.rstrip('/') == '/mcp'
        origin = request.headers.get('Origin')
        allowed = request.path.startswith(('/oauth/', '/.well-known/')) or origin in settings.MCP_ALLOWED_ORIGINS
        if protocol and request.method == 'OPTIONS':
            response = HttpResponse(status=204 if allowed else 403)
        else:
            response = self.get_response(request)
        if protocol:
            response['Cache-Control'] = 'no-store'
            if allowed:
                response['Access-Control-Allow-Origin'] = '*' if request.path.startswith(('/oauth/', '/.well-known/')) else origin or settings.PUBLIC_URL
                response['Access-Control-Allow-Headers'] = 'Authorization, Content-Type, MCP-Protocol-Version, Accept'
                response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
                response['Access-Control-Expose-Headers'] = 'WWW-Authenticate, X-OAuth-Diagnostic-ID'
        return response
