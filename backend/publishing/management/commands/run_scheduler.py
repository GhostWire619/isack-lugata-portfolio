import logging
import signal
import time
from django.core.management import BaseCommand, call_command
from django.db import close_old_connections


class Command(BaseCommand):
    help = 'Publish scheduled Wagtail revisions every minute. Run as one separate service.'
    def handle(self, *args, **options):
        running = True
        def stop(*_):
            nonlocal running
            running = False
        signal.signal(signal.SIGTERM, stop)
        signal.signal(signal.SIGINT, stop)
        while running:
            close_old_connections()
            try:
                call_command('publish_scheduled')
            except Exception:
                logging.exception('Scheduled publishing failed; retrying on the next interval.')
            for _ in range(60):
                if not running:
                    break
                time.sleep(1)
