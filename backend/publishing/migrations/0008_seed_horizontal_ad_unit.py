from django.db import migrations


def seed_slot(apps, schema_editor):
    apps.get_model('publishing', 'PublicationSettings').objects.filter(adsense_article_slot='').update(adsense_article_slot='8873194178')


class Migration(migrations.Migration):
    dependencies = [('publishing', '0007_publicationsettings_adsense_square_slot_and_more')]
    operations = [migrations.RunPython(seed_slot, migrations.RunPython.noop)]
