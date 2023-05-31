# Generated by Django 3.2.13 on 2023-04-27 17:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feature_selection', '0008_alter_trainedmodel_best_fitness_value'),
    ]

    operations = [
        migrations.AddField(
            model_name='trainedmodel',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='trainedmodel',
            name='name',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
    ]
