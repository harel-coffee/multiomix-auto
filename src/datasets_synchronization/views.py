from django.db.models import OuterRef, F, Subquery
from django.contrib.auth.decorators import login_required
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from common.pagination import StandardResultsSetPagination
from common.response import ResponseStatus
from .enums import SyncCGDSStudyResponseCode, SyncStrategy
from .models import CGDSStudy, CGDSDatasetSynchronizationState
from rest_framework import generics, permissions, filters
from user_files.models_choices import FileType
from .serializers import CGDSStudySerializer
from django.shortcuts import render
from .synchronization_service import global_synchronization_service


@login_required
def cgds_panel_action(request):
    """Gets the datasets' panel template"""
    return render(request, "frontend/cgds.html")


class CGDSStudyList(generics.ListCreateAPIView):
    """REST endpoint: list and creation for CGDSStudy model"""
    def get_queryset(self):
        cgds_studies = CGDSStudy.objects
        file_type = self.request.GET.get('file_type')
        only_last_version = self.request.GET.get('only_last_version', 'false') == 'true'

        if file_type is not None:
            file_type = int(file_type)
            if file_type == FileType.MRNA.value:
                cgds_studies = cgds_studies.filter(
                    mrna_dataset__isnull=False,
                    mrna_dataset__state=CGDSDatasetSynchronizationState.SUCCESS
                )
            elif file_type == FileType.MIRNA.value:
                cgds_studies = cgds_studies.filter(
                    mirna_dataset__isnull=False,
                    mirna_dataset__state=CGDSDatasetSynchronizationState.SUCCESS
                )
            elif file_type == FileType.CNA.value:
                cgds_studies = cgds_studies.filter(
                    cna_dataset__isnull=False,
                    cna_dataset__state=CGDSDatasetSynchronizationState.SUCCESS
                )
            elif file_type == FileType.METHYLATION.value:
                cgds_studies = cgds_studies.filter(
                    methylation_dataset__isnull=False,
                    methylation_dataset__state=CGDSDatasetSynchronizationState.SUCCESS)
            elif file_type == FileType.CLINICAL.value:
                cgds_studies = cgds_studies.filter(
                    clinical_patient_dataset__isnull=False,
                    clinical_patient_dataset__state=CGDSDatasetSynchronizationState.SUCCESS,
                    clinical_sample_dataset__isnull=False,
                    clinical_sample_dataset__state=CGDSDatasetSynchronizationState.SUCCESS
                )
        else:
            cgds_studies = cgds_studies.all()

        if only_last_version:
            # Filters by max version and sorts by name
            cgds_studies = cgds_studies.alias(
                max_version=Subquery(
                    CGDSStudy.objects.filter(url=OuterRef('url'))
                    .order_by('-version')
                    .values('version')[:1]
                )
            ).filter(version=F('max_version')).order_by('name')
        else:
            # Otherwise sorts by name and version
            cgds_studies = cgds_studies.order_by('name', '-version')

        return cgds_studies

    serializer_class = CGDSStudySerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['name', 'description']
    ordering_fields = '__all__'


class CGDSStudyDetail(generics.RetrieveUpdateDestroyAPIView):
    """REST endpoint: get, modify or delete for CGDSStudy model"""
    queryset = CGDSStudy.objects.all()
    serializer_class = CGDSStudySerializer
    permission_classes = [permissions.IsAuthenticated]


class SyncCGDSStudy(APIView):
    permission_classes = [permissions.IsAdminUser]  # Only admin users can synchronize CGDS studies

    @staticmethod
    def post(request: Request):
        """Synchronizes a CGDS Study to get its datasets"""
        cgds_study_id = request.data.get('CGDSStudyId')
        if not cgds_study_id:
            response = {
                'status': ResponseStatus(
                    SyncCGDSStudyResponseCode.NOT_ID_IN_REQUEST,
                    message='Missing id in request'
                ).to_json(),
            }

            return Response(response)

        # Retrieves object from DB
        try:
            cgds_study: CGDSStudy = CGDSStudy.objects.get(pk=cgds_study_id)

            default_sync_strategy = SyncStrategy.NEW_VERSION
            sync_strategy_value = request.data.get('strategy', default_sync_strategy)
            try:
                sync_strategy = SyncStrategy(sync_strategy_value)
            except ValueError:
                sync_strategy = default_sync_strategy

            # Gets SynchronizationService and adds the study
            global_synchronization_service.add_cgds_study(cgds_study, sync_strategy)

            # Makes a successful response
            response = {
                'status': ResponseStatus(
                    SyncCGDSStudyResponseCode.SUCCESS,
                    message='The CGDS Study was added to the synchronization queue'
                ).to_json(),
            }
        except CGDSStudy.DoesNotExist:
            # If the study does not exist, show an error in the frontend
            response = {
                'status': ResponseStatus(
                    SyncCGDSStudyResponseCode.CGDS_STUDY_DOES_NOT_EXIST,
                    message='The CGDS Study selected does not exist'
                ).to_json(),
            }

        return Response(response)
