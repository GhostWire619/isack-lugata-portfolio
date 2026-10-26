"""Create private production configuration once, without printing credentials."""
import os
import secrets
from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / '.env.blog'
if path.exists():
    raise SystemExit('.env.blog already exists. Existing secrets have been preserved.')
password = secrets.token_urlsafe(36)
contents = '\n'.join([
    'JOURNAL_ENV=production',
    'PUBLIC_URL=https://isack.space',
    'DJANGO_SECRET_KEY=' + secrets.token_urlsafe(64),
    'JOURNAL_DB_PASSWORD=' + password,
    'DATABASE_URL=postgresql://journal:' + password + '@journal-db:5432/isack_journal',
    '# Configure SMTP below to enable email password recovery.',
    'EMAIL_HOST=', 'EMAIL_PORT=587', 'EMAIL_HOST_USER=', 'EMAIL_HOST_PASSWORD=',
    'EMAIL_USE_TLS=true', 'DEFAULT_FROM_EMAIL=Isack Journal <noreply@isack.space>', '',
])
descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
with os.fdopen(descriptor, 'w', encoding='utf8') as output:
    output.write(contents)
print('Created .env.blog with unique secrets. Keep it private and back it up securely.')
