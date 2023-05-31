# Generated by Django 3.2.13 on 2023-04-21 18:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api_service', '0052_auto_20220923_2322'),
        ('feature_selection', '0006_auto_20230417_1930'),
        ('datasets_synchronization', '0029_auto_20220923_2322'),
        ('biomarkers', '0006_alter_biomarker_state'),
    ]

    operations = [
        migrations.CreateModel(
            name='StatisticalValidationSourceResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('c_index', models.FloatField(blank=True, null=True)),
                ('log_likelihood', models.FloatField(blank=True, null=True)),
                ('roc_auc', models.FloatField(blank=True, null=True)),
                ('source', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='statistical_validations_result', to='api_service.experimentsource')),
            ],
        ),
        migrations.CreateModel(
            name='StatisticalValidation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.IntegerField(choices=[(1, 'Clustering'), (2, 'Use Trained Model'), (3, 'Differential Expression'), (4, 'Train New Model')])),
                ('c_index', models.FloatField()),
                ('log_likelihood', models.FloatField()),
                ('roc_auc', models.FloatField()),
                ('biomarker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='statistical_validations', to='biomarkers.biomarker')),
                ('clinical_source', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='statistical_validations_as_clinical', to='api_service.experimentclinicalsource')),
                ('cna_source_result', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='statistical_validations_as_cna', to='biomarkers.statisticalvalidationsourceresult')),
                ('methylation_source_result', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='statistical_validations_as_methylation', to='biomarkers.statisticalvalidationsourceresult')),
                ('mirna_source_result', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='statistical_validations_as_mirna', to='biomarkers.statisticalvalidationsourceresult')),
                ('mrna_source_result', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='statistical_validations_as_mrna', to='biomarkers.statisticalvalidationsourceresult')),
                ('survival_column_tuple_cgds', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='statistical_validations', to='datasets_synchronization.survivalcolumnstuplecgdsdataset')),
                ('survival_column_tuple_user_file', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='statistical_validations', to='datasets_synchronization.survivalcolumnstupleuserfile')),
                ('trained_model', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='statistical_validations', to='feature_selection.trainedmodel')),
            ],
        ),
    ]
