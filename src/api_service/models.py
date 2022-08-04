from typing import Iterable, List, Optional, Union
from django.db import models
from django.contrib.auth import get_user_model
from common.methylation import get_methylation_platform_dataframe
from genes.models import Gene
from statistical_properties.models import SourceDataStatisticalProperties
from tags.models import Tag
from user_files.models import UserFile
from user_files.models_choices import FileType
from .models_choices import ExperimentType, ExperimentState, CorrelationMethod, PValuesAdjustmentMethod
from .websocket_functions import send_update_experiments_command
from datasets_synchronization.models import CGDSDataset
import pandas as pd
import numpy as np

# Names of the columns by convention in cBioPortal datasets
PATIENT_ID_COLUMN = 'PATIENT_ID'
SAMPLE_ID_COLUMN = 'SAMPLE_ID'
SAMPLES_TYPE_COLUMN = 'SAMPLES_TYPE'
PRIMARY_TYPE_VALUE = 'primary'
TCGA_CONVENTION = '-(0(1|6)|11)$'


def get_combination_class(experiment_type: ExperimentType):
    """
    Gets the corresponding Gene x GEM combination class for a specific Experiment's type
    @param experiment_type: Experiment's type
    @return: Corresponding combination class
    """
    if experiment_type == ExperimentType.MIRNA:
        return GeneMiRNACombination
    if experiment_type == ExperimentType.CNA:
        return GeneCNACombination
    return GeneMethylationCombination


class ExperimentSource(models.Model):
    """
    Represents a Pipeline source. A source could be a file (new or previously uploaded by
    the user), or a CGDS Dataset
    """
    user_file = models.ForeignKey(UserFile, on_delete=models.CASCADE, blank=True, null=True)
    cgds_dataset = models.ForeignKey(CGDSDataset, on_delete=models.CASCADE, blank=True, null=True)

    def get_valid_source(self) -> Union[UserFile, CGDSDataset]:
        """
        Gets the valid source depending of which has been uploaded by the user
        @return: Valid source: a UserFile or a CGDSDataset
        """
        return self.user_file if self.user_file else self.cgds_dataset

    def get_methylation_platform_df(self) -> Optional[pd.DataFrame]:
        """
        Gets (if corresponds) the Methylation CpG platform
        @return: List with the samples
        """
        valid_source = self.get_valid_source()
        if valid_source.file_type == FileType.METHYLATION and valid_source.is_cpg_site_id:
            return get_methylation_platform_dataframe(valid_source.platform)

        return None

    def get_samples(self) -> List[str]:
        """
        Gets the samples of a ExperimentSource
        @return: List with the samples
        """
        return self.get_valid_source().get_column_names()

    def get_specific_row_and_columns(self, row: str, columns_idx: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Gets a specific row and columns values from the source
        @param row: Row's identifier to retrieve it
        @param columns_idx: Indices of columns to filter, if None retrieves all the columns
        @raise KeyError if the row data is empty
        @return: List of values
        """
        row_data = self.get_valid_source().get_specific_row(row)
        if row_data.size == 0:
            raise KeyError

        if columns_idx is not None:
            row_data = row_data[columns_idx]
        return row_data

    def get_df(self) -> pd.DataFrame:
        """
        TODO: check if it's needed, it's only used in tests...
        Generates a DataFrame from an experiment source
        @return: A DataFrame with the data to work
        """
        return self.get_valid_source().get_df()

    def get_df_in_chunks(self) -> Iterable[pd.DataFrame]:
        """
        Returns an Iterator of a DataFrame in divided in chunks from an experiment source
        @return: A DataFrame Iterator with the data to work
        """
        return self.get_valid_source().get_df_in_chunks()

    @property
    def number_of_rows(self) -> int:
        """
        Gets the row count of the Source
        @return: Number of rows in the source
        """
        return self.get_valid_source().number_of_rows

    @property
    def number_of_samples(self) -> int:
        """
        Gets the samples count of the Source
        @return: Number of samples in the source
        """
        return self.get_valid_source().number_of_samples


class ExperimentClinicalSource(ExperimentSource):
    """
    For clinical source of an experiment. Needs an extra CGDSDataset field as cBioPortal has two clinical datasets:
    patients data and samples data
    """
    extra_cgds_dataset = models.ForeignKey(CGDSDataset, on_delete=models.CASCADE, blank=True, null=True)

    def get_methylation_platform_df(self) -> Optional[pd.DataFrame]:
        """
        Clinical source doesn't have Methylation Platform
        @return: List with the samples
        """
        return None

    def get_samples(self) -> List[str]:
        """
        Gets the samples of a ExperimentSource
        @return: List with the samples
        """
        if self.user_file:
            return self.user_file.get_row_indexes()

        # Returns a distinct concatenation of both source columns
        # IMPORTANT: samples are in rows and attributes are in columns
        samples = self.__get_cgds_datasets_joined_df()[SAMPLE_ID_COLUMN]
        return list(set(samples))

    def get_attributes(self) -> List[str]:
        """
        Gets the clinical attributes of the source without the special attributes like sample ids or patient ids
        @return: List with the samples
        """
        if self.user_file:
            return self.user_file.get_column_names()

        # Returns a distinct concatenation of both source columns
        # IMPORTANT: samples are in rows and attributes are in columns
        first_clinical_source_columns: List[str] = self.cgds_dataset.get_column_names()
        second_clinical_source_columns: List[str] = self.extra_cgds_dataset.get_column_names()
        columns_distinct = set(first_clinical_source_columns + second_clinical_source_columns)
        for column_to_remove in [SAMPLE_ID_COLUMN, PATIENT_ID_COLUMN]:
            if column_to_remove in columns_distinct:
                columns_distinct.remove(column_to_remove)
        return list(columns_distinct)

    def get_specific_row_and_columns(self, row: str, columns_idx: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Gets a specific row and columns values from the source
        @param row: Row's identifier to retrieve it
        @param columns_idx: Indices of columns to filter, if None retrieves all the columns
        @raise KeyError if the row data is empty
        @return: List of values
        """
        if self.user_file:
            row_data = self.user_file.get_specific_row(row)
        else:
            # IMPORTANT: samples are in rows and attributes are in columns
            row_data = self.__get_cgds_datasets_joined_df().set_index(SAMPLE_ID_COLUMN).loc[row].to_numpy()

        if row_data.size == 0:
            raise KeyError

        if columns_idx is not None:
            row_data = row_data[:, columns_idx]
        return row_data

    def get_specific_samples_and_attribute(
        self,
        samples: List[str],
        clinical_attribute: str
    ) -> np.ndarray:
        """
        Gets specific samples and a attribute values from the source
        @param samples: List of samples to retrieve
        @param clinical_attribute: Index of column to filter
        @raise KeyError if the row data is empty
        @return: List of values
        """
        if self.user_file:
            row_data = self.user_file.get_df().loc[samples]
        else:
            # IMPORTANT: samples are in rows and attributes are in columns
            row_data = self.__get_cgds_datasets_joined_df()
            row_data[PATIENT_ID_COLUMN] = row_data.index  # Creates a column of Patient ID from the index
            row_data = row_data.set_index(SAMPLE_ID_COLUMN).loc[samples]  # Sets Sample ID and index and get samples

            # If SAMPLES_TYPE_COLUMN exists as column keeps primary only, otherwise all the rows are considered
            # primary
            if SAMPLES_TYPE_COLUMN in row_data.columns:
                row_data = row_data[row_data[SAMPLES_TYPE_COLUMN].str.lower() == PRIMARY_TYPE_VALUE.lower()]
                if row_data.duplicated([PATIENT_ID_COLUMN]).any():
                    raise KeyError

        if row_data.size == 0:
            raise KeyError

        row_data = row_data[clinical_attribute].to_numpy()
        return row_data

    def __get_cgds_datasets_joined_df(self) -> pd.DataFrame:
        """
        Generates a join Pandas DataFrame for both CGDSDatasets of clinical data (cBioPortal has two clinical files)
        @return: Pandas DataFrame
        """
        df1: pd.DataFrame = self.cgds_dataset.get_df()  # The index is implicitly PATIENT_ID
        df2: pd.DataFrame = self.extra_cgds_dataset.get_df()
        df2 = df2.reset_index(level=0)
        # Replaces TCGA suffix: '-01' (primary tumor), -06 (metastatic) and '-11' (normal) to avoid breaking df join
        df2[PATIENT_ID_COLUMN] = df2[PATIENT_ID_COLUMN].str.replace(TCGA_CONVENTION, '', regex=True)
        df2 = df2.set_index(PATIENT_ID_COLUMN)
        return df1.join(df2)

    def get_df(self) -> pd.DataFrame:
        """
        Generates a DataFrame from an experiment source
        @return: A DataFrame with the data to work
        """
        if self.user_file:
            return self.user_file.get_df()

        return self.__get_cgds_datasets_joined_df()

    def get_df_in_chunks(self) -> Iterable[pd.DataFrame]:
        """
        It nos necessary to get the clinical data in chunks as it's little
        @return: A DataFrame Iterator with the data to work
        """
        return self.get_df()

    def get_survival_columns(self) -> List[str]:
        """
        Gets the related survival columns tuples to the UserFile or CGDSDataset
        @return:
        """
        return self.get_valid_source().survival_columns

    @property
    def number_of_rows(self) -> int:
        """
        Gets the row count of the Source
        @return: Number of rows in the source
        """
        if self.user_file:
            return self.user_file.number_of_rows
        return self.__get_cgds_datasets_joined_df().shape[0]

    @property
    def number_of_samples(self) -> int:
        """
        Gets the samples count of the Source
        @return: Number of samples in the source
        """
        if self.user_file:
            return self.user_file.number_of_samples
        return self.__get_cgds_datasets_joined_df().shape[1]


class Experiment(models.Model):
    """Base Class for common Experiment's fields"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    mRNA_source = models.ForeignKey(ExperimentSource, on_delete=models.CASCADE, related_name='mrna_source')
    gem_source = models.ForeignKey(ExperimentSource, on_delete=models.CASCADE, related_name='gem_source')
    clinical_source = models.ForeignKey(ExperimentClinicalSource, on_delete=models.SET_NULL,
                                        related_name='clinical_source', blank=True, null=True)
    submit_date = models.DateTimeField(auto_now_add=True, blank=False, null=True)
    minimum_coefficient_threshold = models.FloatField(default=0.7)
    minimum_std_gene = models.FloatField(default=0.0)
    minimum_std_gem = models.FloatField(default=0.2)
    state = models.IntegerField(choices=ExperimentState.choices)
    correlation_method = models.IntegerField(choices=CorrelationMethod.choices)
    p_values_adjustment_method = models.IntegerField(choices=PValuesAdjustmentMethod.choices)
    evaluated_row_count = models.PositiveIntegerField(blank=True, null=True)  # Row count evaluated during experiment
    result_total_row_count = models.PositiveIntegerField(blank=True, null=True)  # Row count resulting of the experiment
    result_final_row_count = models.PositiveIntegerField(blank=True, null=True)  # Row count after truncating
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, default=None)
    tag = models.ForeignKey(Tag, on_delete=models.SET_NULL, default=None, blank=True, null=True)
    type = models.IntegerField(choices=ExperimentType.choices)
    # Number of attempts to prevent a buggy experiment running forever
    attempt = models.PositiveSmallIntegerField(default=1)

    # TODO: analyze if this go here, maybe when refactor the GEM type for UserFile and CGDSDataset
    # TODO: this can be stored in the Methylation type entity. Set the corresponding nullity in the new schema
    correlate_with_all_genes = models.BooleanField(blank=False, null=False, default=True)

    @property
    def combinations(self):
        """Returns all the result of the experiment combinations"""
        # TODO: check if it could be more simpler getting fields 'genecnacombination', 'genemethylationcombination' or
        # TODO: 'genemirnacombination' depending of the experiment type (maybe change the relate_name to be prettier)
        model_class = self.get_combination_class()
        return model_class.objects.filter(experiment=self)

    def get_combination_class(self):
        """
        Gets the corresponding Combination class depending of the Experiment's type
        @return:
        """
        return get_combination_class(self.type)

    def get_clinical_columns(self) -> List[str]:
        """
        Gets a list of columns from the clinical data
        @return: List of fields in clinical data
        """
        return self.clinical_source.get_samples()

    def save(self, *args, **kwargs):
        """Every time the experiment status changes, uses websockets to update state in the frontend"""
        super().save(*args, **kwargs)

        # Sends a websockets message to update the experiment state in the frontend
        send_update_experiments_command(self.user.id)

    def delete(self, *args, **kwargs):
        """Deletes the instance and sends a websockets message to update state in the frontend"""
        super().delete(*args, **kwargs)

        # Sends a websockets message to update the experiment state in the frontend
        send_update_experiments_command(self.user.id)

    def __str__(self):
        return f'{self.pk} | {self.name}'


class GeneGEMCombination(models.Model):
    """Super class for Gene x GEM combination"""
    id = models.BigAutoField(primary_key=True)
    # It's set as string foreign key to sort by Django Rest Framework
    # No DB constraint due to missing genes extra data
    gene = models.ForeignKey(Gene, db_column='gene', on_delete=models.DO_NOTHING, db_constraint=False)
    gem = models.CharField(max_length=50)
    correlation = models.FloatField()
    p_value = models.FloatField()
    adjusted_p_value = models.FloatField(blank=True, null=True)
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    source_statistical_data = models.OneToOneField(
        SourceDataStatisticalProperties,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        default=None
    )

    class Meta:
        abstract = True

    @property
    def gene_name(self) -> str:
        """
        Gets the foreign key plain value (the name of the gene)
        @return: Name of the Gene
        """
        return self.gene_id

    def __str__(self):
        return f'{self.gene_name} | {self.gem}'


class GeneMiRNACombination(GeneGEMCombination):
    class Meta:
        db_table = 'gene_mirna_combination'


class GeneCNACombination(GeneGEMCombination):
    class Meta:
        db_table = 'gene_cna_combination'


class GeneMethylationCombination(GeneGEMCombination):
    class Meta:
        db_table = 'gene_methylation_combination'
