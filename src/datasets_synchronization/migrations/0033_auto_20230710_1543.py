# Generated by Django 3.2.13 on 2023-07-10 15:43
import logging

from django.db import migrations
from django.db.models import Subquery, OuterRef, F

from datasets_synchronization.models import CGDSDatasetSynchronizationState, CGDSStudy


def set_state_to_studies_with_prefix(apps, schema_editor):
    """
    Sets the state of all datasets with a sample with suffix '-03' to NOT_SYNCHRONIZED to prevent NoSamplesInCommon
    issue during DataFrame joins.
    """
    # Gets only the last version of each study
    studies = CGDSStudy.objects.alias(
        max_version=Subquery(
            CGDSStudy.objects.filter(url=OuterRef('url'))
            .order_by('-version')
            .values('version')[:1]
        )
    ).filter(version=F('max_version'))

    for study in studies:
        for dataset in study.get_all_valid_datasets():
            if dataset.state == CGDSDatasetSynchronizationState.SUCCESS:
                samples = dataset.get_column_names()
                # Checks if any of the samples has a suffix '-03'
                if any([sample.endswith('-03') for sample in samples]):
                    print(f"Setting state to CGDSDatasetSynchronizationState.NOT_SYNCHRONIZED for dataset {dataset}")
                    dataset.state = CGDSDatasetSynchronizationState.NOT_SYNCHRONIZED
                    dataset.save(update_fields=['state'])


class Migration(migrations.Migration):

    dependencies = [
        ('datasets_synchronization', '0032_auto_20230624_0029'),
    ]

    operations = [
        migrations.RunPython(set_state_to_studies_with_prefix),
    ]
