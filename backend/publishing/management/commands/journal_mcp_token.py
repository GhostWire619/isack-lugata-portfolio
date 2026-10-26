import json
from datetime import timedelta
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from publishing.models import MCPConnection, JournalIndexPage
from publishing.studio import can_write


class Command(BaseCommand):
    help = 'Issue an expiring MCP access token to a private file, or revoke a connection.'

    def add_arguments(self, parser):
        parser.add_argument('--username')
        parser.add_argument('--name', default='MCP client')
        parser.add_argument('--hours', type=int, default=24)
        parser.add_argument('--write', action='store_true')
        parser.add_argument('--output', help='New private file for the credential. Existing files are never overwritten.')
        parser.add_argument('--revoke', type=int, help='Connection ID to revoke.')

    def handle(self, *args, **options):
        if options['revoke']:
            if not MCPConnection.objects.filter(pk=options['revoke']).update(revoked_at=timezone.now()):
                raise CommandError('Connection not found.')
            self.stdout.write('Connection revoked.')
            return
        if not options['username'] or not options['output'] or not 1 <= options['hours'] <= 720:
            raise CommandError('Provide --username, --output and --hours between 1 and 720.')
        user = get_user_model().objects.filter(username=options['username'], is_active=True, is_staff=True).first()
        if not user or not can_write(user, JournalIndexPage.objects.first()):
            raise CommandError('Choose an active Studio user with journal writing permission.')
        output = Path(options['output'])
        output.parent.mkdir(parents=True, exist_ok=True)
        # Create privately and exclusively before minting a credential.
        import os
        try:
            descriptor = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            raise CommandError('Output file exists. Choose a new private filename.')
        connection = None
        try:
            connection, token = MCPConnection.issue(user=user, name=options['name'],
                expires_at=timezone.now() + timedelta(hours=options['hours']), can_write=options['write'])
            with os.fdopen(descriptor, 'w', encoding='utf-8') as handle:
                json.dump({'connection_id': connection.pk, 'token': token,
                    'expires_at': connection.expires_at.isoformat()}, handle)
        except Exception:
            if connection:
                connection.delete()
            output.unlink(missing_ok=True)
            raise
        self.stdout.write(f'Connection {connection.pk} created. Credential saved to the private output file.')
