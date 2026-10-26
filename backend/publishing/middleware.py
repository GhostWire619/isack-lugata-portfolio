from django.shortcuts import redirect
from django.utils.cache import patch_cache_control


class RequireAdminOTP:
    """An authenticated password session alone cannot access publishing tools."""
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        private = request.path.startswith(('/admin/', '/security/'))
        if request.path.startswith('/admin/') and request.path != '/admin/logout/' and request.user.is_authenticated and request.user.is_staff and not request.user.is_verified():
            if request.method == 'GET' and (request.path in ['/admin/', '/admin/articles/', '/admin/articles/new/', '/admin/advertising/preview/'] or request.path.endswith('/edit/')):
                request.session['journal_admin_next'] = request.get_full_path()
            response = redirect('/security/verify/')
        else:
            response = self.get_response(request)
        if private:
            patch_cache_control(response, no_store=True, private=True)
            response['X-Robots-Tag'] = 'noindex, nofollow'
        return response
