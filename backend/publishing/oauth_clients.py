"""Negotiate public-client auth from current CIMD capability documents."""
from oauth2_provider.cimd import CIMDError, SafeMetadataFetcher
from oauth2_provider.settings import oauth2_settings


class JournalClientMetadataFetcher(SafeMetadataFetcher):
    def fetch(self, client_id):
        # Keep DOT's HTTPS, pinned public-IP, size, timeout and no-redirect checks.
        try:
            metadata, max_age = super().fetch(client_id)
        except Exception as error:
            from .oauth_diagnostics import metadata_failed
            metadata_failed(client_id, error)
            raise
        methods = metadata.get('token_endpoint_auth_methods_supported')
        if methods is not None:
            if not isinstance(methods, list) or not methods or not all(isinstance(method, str) for method in methods):
                raise CIMDError('Client authentication methods must be a non-empty array of strings.')
            # ChatGPT advertises a legacy private_key_jwt preference alongside
            # a plural capability list. This server supports public clients
            # with mandatory S256 PKCE, so select the explicitly shared method.
            if 'none' not in methods or 'none' not in oauth2_settings.OAUTH2_TOKEN_ENDPOINT_AUTH_METHODS_SUPPORTED:
                raise CIMDError('No supported public-client authentication method.')
            metadata = {**metadata, 'token_endpoint_auth_method': 'none'}
        return metadata, max_age
