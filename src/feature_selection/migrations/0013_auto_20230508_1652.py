# Generated by Django 3.2.13 on 2023-05-08 16:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feature_selection', '0012_auto_20230508_1647'),
    ]

    operations = [
        migrations.AddField(
            model_name='svmparameters',
            name='max_iterations',
            field=models.SmallIntegerField(default=1000),
        ),
        migrations.AddField(
            model_name='svmparameters',
            name='random_state',
            field=models.SmallIntegerField(blank=True, null=True),
        ),
    ]