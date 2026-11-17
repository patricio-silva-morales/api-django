from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('helpdesk', '0001_initial'),
    ]

    operations = [
        # AGREGADO: usa el mismo orden que el listado.
        migrations.AddIndex(
            model_name='ticket',
            index=models.Index(
                fields=['fechaCreacion', 'id'],
                name='tickets_fecha_id_idx',
            ),
        ),
    ]
