import tempfile
import numpy as np
from typing import Union, Optional, cast, List, Literal, Tuple
import pandas as pd
from api_service.models import ExperimentSource
from common.exceptions import NoSamplesInCommon
from feature_selection.models import FSExperiment, TrainedModel
from inferences.models import InferenceExperiment
from statistical_properties.models import StatisticalValidation
from user_files.models_choices import FileType

# Common event values
COMMON_INTEREST_VALUES = ['DEAD', 'DECEASE', 'DEATH']

ExperimentObjType = Union[FSExperiment, InferenceExperiment, StatisticalValidation, TrainedModel]


def get_samples_intersection(source: ExperimentSource, last_intersection: np.ndarray) -> np.ndarray:
    """
    Gets the intersection of the samples of the current source with the last intersection.
    @param source: Source to get the samples from.
    @param last_intersection: Last intersection of samples.
    @return: Intersection of the samples of the current source with the last intersection.
    """
    # Clean all the samples name to prevent issues with CGDS suffix
    current_samples = source.get_samples()

    if last_intersection is not None:
        cur_intersection = np.intersect1d(
            last_intersection,
            current_samples
        )
    else:
        cur_intersection = np.array(current_samples)
    last_intersection = cast(np.ndarray, cur_intersection)
    return last_intersection


def get_common_samples(experiment: ExperimentObjType) -> np.ndarray:
    """
    Gets a sorted Numpy array with the samples ID in common between both ExperimentSources.
    @param experiment: Feature Selection experiment.
    @return: Sorted Numpy array with the samples in common
    """
    # NOTE: the intersection is already sorted by Numpy
    last_intersection: Optional[np.ndarray] = None

    for source in experiment.get_all_sources():
        if source is None:
            continue

        last_intersection = get_samples_intersection(source, last_intersection)

    # Checks empty intersection
    last_intersection = cast(np.ndarray, last_intersection)
    if last_intersection.size == 0:
        raise NoSamplesInCommon

    return last_intersection


def process_chunk(chunk: pd.DataFrame, file_type: FileType, molecules: List[str],
                    samples_in_common: np.ndarray) -> pd.DataFrame:
    """Processes a chunk of a DataFrame adding the file type to the index and keeping just the samples in common."""
    # Only keeps the samples in common
    chunk = chunk[samples_in_common]

    # Keeps only existing molecules in the current chunk
    molecules_to_extract = np.intersect1d(chunk.index, molecules)
    chunk = chunk.loc[molecules_to_extract]

    # Adds type to disambiguate between genes of 'mRNA' type and 'CNA' type
    chunk.index = chunk.index + f'_{file_type}'

    return chunk


def generate_molecules_file(experiment: ExperimentObjType, samples_in_common: np.ndarray) -> str:
    """
    Generates the molecules DataFrame for a specific InferenceExperiment with the samples in common and saves
    it in disk.
    """
    with tempfile.NamedTemporaryFile(mode='a', delete=False) as temp_file:
        molecules_temp_file_path = temp_file.name

        for source, molecules, file_type in experiment.get_sources_and_molecules():
            if source is None:
                continue

            for chunk in source.get_df_in_chunks():
                chunk = process_chunk(chunk, file_type, molecules, samples_in_common)

                # Saves in disk
                chunk.to_csv(temp_file, header=temp_file.tell() == 0, sep='\t', decimal='.')

    return molecules_temp_file_path


def clean_dataset(df: pd.DataFrame, axis: Literal['rows', 'columns']) -> pd.DataFrame:
    """
    Removes NaN and Inf values.
    :param df: DataFrame to clean.
    :param axis: Axis to remove the Nans values.
    :return: Cleaned DataFrame.
    """
    assert isinstance(df, pd.DataFrame), "df needs to be a pd.DataFrame"

    # Taken from https://stackoverflow.com/a/45746209/7058363
    with pd.option_context('mode.use_inf_as_na', True):
        df = df.dropna(axis=axis, how='all')

    return df


def clinical_df_to_struct_array(clinical_df: pd.DataFrame) -> np.ndarray:
    """
    Converts a Pandas DataFrame with clinical data to a Numpy structured array with the columns 'event' and 'time'.
    @param clinical_df: Clinical data as a Pandas DataFrame.
    @return: Clinical data as a Numpy structured array.
    """
    clinical_data = np.core.records.fromarrays(clinical_df.to_numpy().transpose(), names='event, time',
                                               formats='bool, float')
    return clinical_data


def format_data(molecules_temp_file_path: str, clinical_temp_file_path: str,
                is_regression: bool) -> Tuple[pd.DataFrame, pd.DataFrame, np.ndarray]:
    """
    Reads both molecules and clinical data and formats them to be used in the models.
    @param molecules_temp_file_path: Molecular data file path.
    @param clinical_temp_file_path: Clinical data file path.
    @param is_regression: Whether the experiment is a regression or not.
    @return: Molecules as Pandas DataFrame and the clinical data as a Pandas DataFrame and as a Numpy structured array.
    """
    # Gets molecules and clinical DataFrames
    molecules_df = pd.read_csv(molecules_temp_file_path, sep='\t', decimal='.', index_col=0)
    clinical_df = pd.read_csv(clinical_temp_file_path, sep='\t', decimal='.', index_col=0)

    # In case of regression removes time == 0 in the datasets to prevent errors in the models fit() method
    if is_regression:
        time_column = clinical_df.columns.tolist()[1]  # The time column is ALWAYS the second one at this point
        clinical_df = clinical_df[clinical_df[time_column] > 0]

    # Keeps only the samples in common
    valid_samples = clinical_df.index
    molecules_df = molecules_df[valid_samples]  # Samples are as columns in molecules_df

    # Removes molecules with NaN values
    molecules_df = clean_dataset(molecules_df, axis='rows')

    # Formats clinical data to a Numpy structured array
    clinical_data = clinical_df_to_struct_array(clinical_df)

    return molecules_df, clinical_df, clinical_data


def replace_event_col_for_booleans(value: Union[int, str]) -> bool:
    """Replaces string or integer events in datasets to booleans values to make survival analysis later."""
    return value in [1, '1'] or any(candidate in value for candidate in COMMON_INTEREST_VALUES)