# Generated by Django 3.2.13 on 2022-10-17 22:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('genes', '0002_auto_20210114_2331'),
        ('biomarkers', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='biomarker',
            name='genes',
            field=models.ManyToManyField(blank=True, related_name='biomarkers', to='genes.Gene'),
        ),
        migrations.AddField(
            model_name='biomarker',
            name='upload_date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]