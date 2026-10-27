from django.urls import path
from wagtail.admin.auth import require_admin_access
from oauth2_provider import views
from .oauth import JournalAuthorizationView

app_name = 'oauth2_provider'
urlpatterns = [
    path('.well-known/oauth-authorization-server', views.OAuthServerMetadataView.as_view(), name='oauth-server-metadata'),
    path('.well-known/oauth-protected-resource', views.OAuthProtectedResourceMetadataView.as_view(), name='oauth-resource-metadata'),
    path('.well-known/oauth-protected-resource/mcp', views.OAuthProtectedResourceMetadataView.as_view()),
    path('admin/ai/authorize/', require_admin_access(JournalAuthorizationView.as_view()), name='authorize'),
    path('oauth/token/', views.TokenView.as_view(), name='token'),
    path('oauth/revoke/', views.RevokeTokenView.as_view(), name='revoke-token'),
    path('oauth/register/', views.DynamicClientRegistrationView.as_view(), name='dcr-register'),
    path('oauth/register/<str:client_id>/', views.DynamicClientRegistrationManagementView.as_view(), name='dcr-register-management'),
]
