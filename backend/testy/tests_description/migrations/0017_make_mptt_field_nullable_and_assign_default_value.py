from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('tests_description', '0016_alter_testsuite_level_alter_testsuite_lft_and_more'),
    ]
    operations = [
        migrations.AlterField(
            model_name='testsuite',
            name='level',
            field=models.PositiveIntegerField(editable=False, null=True, default=0),
        ),
        migrations.AlterField(
            model_name='testsuite',
            name='level',
            field=models.PositiveIntegerField(editable=False, null=True, default=0),
        ),
        migrations.AlterField(
            model_name='testsuite',
            name='lft',
            field=models.PositiveIntegerField(editable=False, null=True, default=0),
        ),
        migrations.AlterField(
            model_name='testsuite',
            name='rght',
            field=models.PositiveIntegerField(editable=False, null=True, default=0),
        ),
    ]
