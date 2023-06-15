# Generated by Django 3.2.13 on 2023-04-25 20:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('biomarkers', '0010_statisticalvalidation_mean_squared_error'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='statisticalvalidation',
            name='type',
        ),
        migrations.AddField(
            model_name='statisticalvalidation',
            name='state',
            field=models.IntegerField(choices=[(1, 'Completed'), (2, 'Finished With Error'), (3, 'In Process'), (4, 'Waiting For Queue'), (5, 'No Samples In Common'), (6, 'Stopping'), (7, 'Stopped'), (8, 'Reached Attempts Limit')], default=1),
            preserve_default=False,
        ),
    ]