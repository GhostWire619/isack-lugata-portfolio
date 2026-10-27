"""Bounded public HTTPS image downloads; DNS is pinned for every redirect."""
import http.client
import ipaddress
import socket
import ssl
import time
from urllib.parse import urlsplit, urljoin

MAX_BYTES = 10 * 1024 * 1024


def public_target(url):
    try:
        parsed = urlsplit(url)
        if (parsed.scheme != 'https' or not parsed.hostname or parsed.username or
                parsed.password or parsed.port not in (None, 443) or parsed.fragment or
                any(ord(c) <= 32 or ord(c) == 127 for c in url)):
            raise ValueError
        host = parsed.hostname.encode('idna').decode('ascii')
        addresses = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
        if not addresses or any(not ipaddress.ip_address(item[4][0]).is_global or ipaddress.ip_address(item[4][0]).is_multicast for item in addresses):
            raise ValueError
        return host, addresses[0][4][0], parsed.path or '/', parsed.query
    except (ValueError, UnicodeError, OSError):
        raise ValueError('Use a public HTTPS image URL on port 443; private network addresses are blocked.') from None


class PinnedHTTPSConnection(http.client.HTTPSConnection):
    def __init__(self, host, address, timeout):
        super().__init__(host, timeout=timeout, context=ssl.create_default_context())
        self.address = address

    def connect(self):
        raw = socket.create_connection((self.address, 443), self.timeout)
        try:
            self.sock = self._context.wrap_socket(raw, server_hostname=self.host)
        except Exception:
            raw.close()
            raise


def download_image(url):
    deadline = time.monotonic() + 20
    try:
        for hop in range(4):
            host, address, path, query = public_target(url)
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError
            connection = PinnedHTTPSConnection(host, address, min(5, remaining))
            try:
                connection.request('GET', path + ('?' + query if query else ''), headers={
                    'Accept': 'image/jpeg,image/png,image/webp', 'Accept-Encoding': 'identity',
                    'User-Agent': 'SideNotes-ImageImporter/1.0'})
                response = connection.getresponse()
                if response.status in (301, 302, 303, 307, 308):
                    location = response.getheader('Location')
                    if not location or hop == 3:
                        raise ValueError('Image URL redirected too many times or has no destination.')
                    url = urljoin(url, location)
                    continue
                if response.status != 200:
                    raise ValueError(f'Image host returned HTTP {response.status}. Choose a publicly downloadable image URL.')
                if response.getheader('Content-Type', '').split(';')[0].strip().lower() not in ('image/jpeg', 'image/png', 'image/webp'):
                    raise ValueError('URL must return a JPEG, PNG or WebP image, not a webpage.')
                if response.getheader('Content-Encoding', 'identity').lower() != 'identity':
                    raise ValueError('Image host returned an unsupported compressed response.')
                length = response.getheader('Content-Length')
                if length and (not length.isdigit() or int(length) > MAX_BYTES):
                    raise ValueError('Remote image exceeds the 10 MB download limit.')
                data = bytearray()
                while True:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        raise TimeoutError
                    if connection.sock:
                        connection.sock.settimeout(min(5, remaining))
                    chunk = response.read1(min(65536, MAX_BYTES + 1 - len(data)))
                    if not chunk:
                        return bytes(data)
                    data.extend(chunk)
                    if len(data) > MAX_BYTES:
                        raise ValueError('Remote image exceeds the 10 MB download limit.')
            finally:
                connection.close()
    except (OSError, http.client.HTTPException):
        raise ValueError('Image download failed or timed out. Try another public image URL; no image was saved.') from None
