from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('tests_representation', '0029_testplan_attributes'),
    ]
    operations = [
        migrations.AlterField(
            model_name='testplan',
            name='level',
            field=models.PositiveIntegerField(editable=False, null=True, default=0),
        ),
        migrations.AlterField(
            model_name='testplan',
            name='level',
            field=models.PositiveIntegerField(editable=False, null=True, default=0),
        ),
        migrations.AlterField(
            model_name='testplan',
            name='lft',
            field=models.PositiveIntegerField(editable=False, null=True, default=0),
        ),
        migrations.AlterField(
            model_name='testplan',
            name='rght',
            field=models.PositiveIntegerField(editable=False, null=True, default=0),
        ),
    ]
