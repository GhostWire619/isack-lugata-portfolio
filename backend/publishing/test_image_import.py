from io import BytesIO
from unittest.mock import patch, MagicMock
from django.test import SimpleTestCase
from .image_import import public_target, download_image, MAX_BYTES


class ImageDownloadTests(SimpleTestCase):
    def test_blocks_private_dns_and_bad_schemes(self):
        for url in ('http://example.com/a', 'https://user:pass@example.com/a',
                    'https://example.com:8443/a', 'file:///tmp/a', 'https://example.com/\na'):
            with self.assertRaises(ValueError):
                public_target(url)
        for address in ('127.0.0.1', '10.0.0.1', '169.254.169.254', '::1', 'fc00::1'):
            with patch('publishing.image_import.socket.getaddrinfo', return_value=[(2, 1, 6, '', (address, 443))]):
                with self.assertRaises(ValueError):
                    public_target('https://example.com/a')

    def response(self, status=200, headers=None, data=b'photo'):
        response = MagicMock(status=status)
        values = {'Content-Type': 'image/jpeg', **(headers or {})}
        response.getheader.side_effect = lambda name, default=None: values.get(name, default)
        response.read1.side_effect = BytesIO(data).read1
        return response

    @patch('publishing.image_import.socket.getaddrinfo', return_value=[(2, 1, 6, '', ('93.184.216.34', 443))])
    def test_download_pins_public_address_and_bounds_body(self, dns):
        with patch('publishing.image_import.PinnedHTTPSConnection') as connection:
            connection.return_value.getresponse.return_value = self.response()
            self.assertEqual(download_image('https://example.com/photo.jpg'), b'photo')
            self.assertEqual(connection.call_args.args[:2], ('example.com', '93.184.216.34'))
            connection.return_value.close.assert_called()
            for response in (self.response(headers={'Content-Length': str(MAX_BYTES + 1)}),
                             self.response(headers={'Content-Type': 'text/html'}),
                             self.response(data=b'x' * (MAX_BYTES + 1)), self.response(status=403)):
                connection.return_value.getresponse.return_value = response
                with self.assertRaises(ValueError):
                    download_image('https://example.com/photo.jpg')

    def test_redirect_rechecks_dns_before_connecting(self):
        with patch('publishing.image_import.socket.getaddrinfo', side_effect=[
                [(2, 1, 6, '', ('93.184.216.34', 443))], [(2, 1, 6, '', ('127.0.0.1', 443))]]), \
                patch('publishing.image_import.PinnedHTTPSConnection') as connection:
            connection.return_value.getresponse.return_value = self.response(302, {'Location': 'https://internal.example/photo.jpg'})
            with self.assertRaises(ValueError):
                download_image('https://example.com/photo.jpg')
            self.assertEqual(connection.call_count, 1)

    def test_timeout_has_actionable_error(self):
        with patch('publishing.image_import.public_target', return_value=('example.com', '93.184.216.34', '/', '')), \
                patch('publishing.image_import.PinnedHTTPSConnection', side_effect=TimeoutError):
            with self.assertRaisesMessage(ValueError, 'timed out'):
                download_image('https://example.com/photo.jpg')
