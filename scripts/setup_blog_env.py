"""Prepare one Compose .env file without printing or rotating deployed secrets."""
import os
import secrets
from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / '.env'
legacy = root / '.env.blog'
required = {'DJANGO_SECRET_KEY', 'JOURNAL_DB_PASSWORD', 'DATABASE_URL'}


def validate(content):
    values = {}
    for line in content.decode('utf-8-sig').splitlines():
        key, separator, value = line.partition('=')
        if separator:
            values[key.strip()] = value.strip().strip('"\'')
    missing = sorted(key for key in required if not values.get(key))
    if missing:
        raise SystemExit('Existing configuration is missing ' + ', '.join(missing) + '. Nothing was overwritten.')


if path.exists():
    validate(path.read_bytes())
    print('Existing .env preserved. Run: docker compose up -d --build')
else:
    if legacy.exists():
        content = legacy.read_bytes()
        validate(content)
        message = 'Copied existing .env.blog to .env; credentials and the original file were preserved.'
    else:
        password = secrets.token_urlsafe(36)
        content = '\n'.join([
            'JOURNAL_ENV=production',
            'PUBLIC_URL=https://isack.space',
            'DJANGO_SECRET_KEY=' + secrets.token_urlsafe(64),
            'JOURNAL_DB_PASSWORD=' + password,
            'DATABASE_URL=postgresql://journal:' + password + '@journal-db:5432/isack_journal',
            '# Configure SMTP below to enable email password recovery.',
            'EMAIL_HOST=', 'EMAIL_PORT=587', 'EMAIL_HOST_USER=', 'EMAIL_HOST_PASSWORD=',
            'EMAIL_USE_TLS=true', 'DEFAULT_FROM_EMAIL=Isack Journal <noreply@isack.space>', '',
        ]).encode('utf-8')
        message = 'Created .env with unique secrets. Keep it private and back it up securely.'
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, 'wb') as output:
        output.write(content)
    print(message)
    print('Run: docker compose up -d --build')
