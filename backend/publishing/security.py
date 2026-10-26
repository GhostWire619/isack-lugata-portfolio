import base64
from io import BytesIO

import django_otp
import qrcode
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.plugins.otp_static.models import StaticDevice, StaticToken


def studio_destination(request):
    destination = request.session.pop('journal_admin_next', '/admin/')
    return destination if destination.startswith('/admin/') and not destination.startswith('/admin/login') else '/admin/'


@never_cache
@login_required
@require_http_methods(['GET', 'POST'])
def verify(request):
    if not request.user.is_active or not request.user.is_staff:
        return redirect('/admin/login/')
    if request.user.is_verified():
        return redirect(studio_destination(request))
    confirmed = TOTPDevice.objects.filter(user=request.user, confirmed=True).first()
    device = confirmed or TOTPDevice.objects.get_or_create(user=request.user, name='Journal authenticator', confirmed=False)[0]
    error = ''
    if request.method == 'POST':
        token = request.POST.get('token', '').strip().replace(' ', '')[:40]
        # The device implementation persists verification throttling and prevents token reuse.
        with transaction.atomic():
            locked = TOTPDevice.objects.select_for_update().get(pk=device.pk)
            valid = locked.verify_token(token)
            backup = None
            if not valid and confirmed:
                backup = StaticDevice.objects.select_for_update().filter(user=request.user, name='Journal recovery').first()
                valid = bool(backup and backup.verify_token(token))
            if valid:
                if not confirmed:
                    locked.confirmed = True
                    locked.save(update_fields=['confirmed'])
                django_otp.login(request, backup or locked)
                if not confirmed:
                    recovery, _ = StaticDevice.objects.get_or_create(user=request.user, name='Journal recovery')
                    recovery.token_set.all().delete()
                    codes = [StaticToken.random_token() for _ in range(10)]
                    StaticToken.objects.bulk_create([StaticToken(device=recovery, token=code) for code in codes])
                    return render(request, 'security/recovery.html', {'codes': codes, 'continue_url': studio_destination(request)})
                return redirect(studio_destination(request))
        error = 'That code could not be verified. Check your authenticator, or use a recovery code. Repeated attempts are temporarily throttled.'
    qr = None
    if not confirmed:
        image = qrcode.make(device.config_url)
        output = BytesIO()
        image.save(output, format='PNG')
        qr = base64.b64encode(output.getvalue()).decode()
    return render(request, 'security/verify.html', {'setup': not bool(confirmed), 'qr': qr, 'error': error})
