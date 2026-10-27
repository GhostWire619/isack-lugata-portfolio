import logging
import signal
import time
from datetime import timedelta
from django.core.management import BaseCommand, call_command
from django.db import close_old_connections
from django.utils import timezone


class Command(BaseCommand):
    help = 'Publish scheduled Wagtail revisions every minute. Run as one separate service.'
    def handle(self, *args, **options):
        running = True
        def stop(*_):
            nonlocal running
            running = False
        signal.signal(signal.SIGTERM, stop)
        signal.signal(signal.SIGINT, stop)
        last_cleanup = 0
        while running:
            close_old_connections()
            try:
                call_command('publish_scheduled')
                if time.monotonic() - last_cleanup > 86400:
                    from publishing.models import PageView
                    PageView.objects.filter(created_at__lt=timezone.now() - timedelta(days=90)).delete()
                    call_command('cleartokens', verbosity=0)
                    last_cleanup = time.monotonic()
            except Exception:
                logging.exception('Scheduled publishing failed; retrying on the next interval.')
            for _ in range(60):
                if not running:
                    break
                time.sleep(1)
