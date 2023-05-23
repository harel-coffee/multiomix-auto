from django.urls import path
from . import views

urlpatterns = [
    path(
        'biomarker-inference-experiments',
        views.BiomarkerStatisticalInferenceExperiments.as_view(),
        name='biomarker_inference_experiments'
    ),
    path('submit-inference-experiment', views.PredictionExperimentSubmit.as_view(), name='submit_inference_experiment'),
    path(
        'inference-experiment-samples-and-clusters',
        views.SampleAndClusterPredictionSamples.as_view(),
        name='inference_experiment_samples_and_clusters'
    ),
    path(
        'inference-experiment-samples-and-time',
        views.SampleAndTimePredictionSamples.as_view(),
        name='inference_experiment_samples_and_time'
    ),
]
