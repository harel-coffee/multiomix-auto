from django.urls import path
from . import views

urlpatterns = [
    path('', views.biomarkers_action, name='biomarkers'),
    path('api', views.BiomarkerList.as_view(), name='biomarkers_api'),
    path('api/<int:pk>/', views.BiomarkerDetail.as_view()),
    path('create', views.BiomarkerCreate.as_view(), name='biomarkers_create'),
    path('gene-symbols', views.GeneSymbols.as_view(), name='gene_symbols'),
    path('gene-symbols-finder', views.GeneSymbols.as_view(), name='gene_symbols_finder'),
    path('clone_biomarker', views.BiomarkerClone.as_view(), name='clone_biomarker'),
    path('clone_biomarker/<int:pk>/', views.BiomarkerClone.as_view(), name='clone_biomarker'),
    path('mirna-codes', views.MiRNACodes.as_view(), name='mirna_codes'),
    path('mirna-codes-finder', views.MiRNACodes.as_view(), name='mirna_codes_finder'),
    path('methylation-sites', views.MethylationSites.as_view(), name='methylation_sites'),
    path('methylation-sites-finder', views.MethylationSites.as_view(), name='methylation_sites_finder'),
    path('biomarker-trained-models', views.TrainedModelsOfBiomarker.as_view(), name='biomarker_trained_models'),
    path('biomarker-molecules', views.BiomarkerMolecules.as_view(), name='biomarker_molecules'),
]
