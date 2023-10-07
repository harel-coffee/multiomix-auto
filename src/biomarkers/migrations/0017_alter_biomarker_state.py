# Generated by Django 3.2.20 on 2023-08-01 23:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('biomarkers', '0016_alter_biomarker_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='biomarker',
            name='state',
            field=models.IntegerField(choices=[(1, 'Completed'), (2, 'Finished With Error'), (3, 'In Process'), (4, 'Waiting For Queue'), (5, 'No Samples In Common'), (6, 'Stopping'), (7, 'Stopped'), (8, 'Reached Attempts Limit'), (9, 'No Features Found'), (10, 'No Valid Samples'), (11, 'No Valid Molecules'), (12, 'Number Of Samples Fewer Than Cv Folds'), (13, 'Timeout Exceeded')]),
        ),
    ]