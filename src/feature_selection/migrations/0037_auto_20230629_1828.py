# Generated by Django 3.2.13 on 2023-06-29 18:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feature_selection', '0036_alter_trainedmodel_state'),
    ]

    operations = [
        migrations.AddField(
            model_name='clusteringtimesrecord',
            name='algorithm',
            field=models.IntegerField(choices=[(1, 'K Means'), (2, 'Spectral')], default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='clusteringtimesrecord',
            name='number_of_clusters',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='rftimesrecord',
            name='number_of_trees',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
    ]