import pandas as pd # add to requirements.txt
import numpy as np  # add to requirements.txt


def format_data(dataframe):
    """
        Format the data in the dataframe, converting the columns
        to the appropriate types and returning the processed dataframe

        inputs:
            - dataframe: the source dataframe
        output:
            - dataframe: the formatted DataFrame with the following columns:
                - age
                - sex
                - n 'creatinine_result_i' columns
                - n-1 'elapsed_exam_i-(i+1)' columns
                - min_creatinine
                - avg_creatinine
                - max_creatinine
            - aki_values: the binary aki values of the original dataframe
    """
    # Convert

    aki_values = dataframe['aki']
    dataframe.drop(columns=['aki'], inplace=True)
    return (dataframe, aki_values)


def process_data(dataframe):
    """
        Process the data in the dataframe, converting the columns
        to the appropriate types and returning the processed dataframe

        inputs:
            - dataframe: the source dataframe
        output:
            - dataframe: the formatted dataframe with the following columns:
                - age
                - sex
                - n 'creatinine_result_i' columns
                - n-1 'elapsed_exam_i-(i+1)' columns
                - min_creatinine
                - avg_creatinine
                - max_creatinine
            - aki_values: the binary aki values of the original dataframe
    """
    # Preprocess the data
    (dataframe, aki_values) = format_data(dataframe)
    return (dataframe, aki_values)


def calculate_elapsed_time(dataframe, total_tests):
    """
        Calculate the elapsed days between each blood test

        inputs: 
            - dataframe: the source dataframe
        output:
            - elapsed_days: dataframe with n-1 columns corresponding to the
                            elapsed days between each n blood test
    """
    columns = get_creatinine_dataframe_columns(total_tests, 'date')
    exams_time_difference = {}
    prev = 0
    for next in range(1, total_tests):
        exams_time_difference[f'elapsed_exam_{prev}-{next}'] = (dataframe.loc[:][columns[next]]-dataframe.loc[:][columns[prev]])
        prev = next

    elapsed_days = pd.DataFrame(exams_time_difference).astype('timedelta64[ns]').apply(lambda x: x.dt.days)

    return elapsed_days


def get_creatinine_stats(dataframe, total_tests):
    columns = get_creatinine_dataframe_columns(total_tests, 'result')
    creatinine_stats = {}
    creatinine_stats['min_creatinine'] = dataframe.loc[:][columns].min(axis=1)
    creatinine_stats['avg_creatinine'] = dataframe.loc[:][columns].mean(axis=1)
    creatinine_stats['max_creatinine'] = dataframe.loc[:][columns].max(axis=1)

    creatine_ds = pd.DataFrame(creatinine_stats)
    return creatine_ds


def get_creatinine_dataframe_columns(total_tests, col_type):
    """
        Return a list of creatinine columns in the dataset in the
        form 'creatinine_x_5', with x equal to:
            - 'result', if col_type is the result of the test
            - 'date', if col_type is the date of the test

        inputs:
            - total_tests: the maximum number of creatinine tests taken by any patient
            - col_type: the type of the column, either 'result' or 'date'
        output:
            - creatinine_columns: list of column names
    """
    creatinine_columns = []
    for i in range(total_tests):
        creatinine_columns.append(f'creatinine_{col_type}_{i}')
    return creatinine_columns


def convert_to_datetime(dataframe, columns):
    """
        Convert the given dataframe columns in the list 'columns' 
        to datetime type
        
        inputs:
            - dataframe: the source dataframe
            - columns: list of column names to convert 
        output:
            - dataframe: the processed dataframe
    """
    for column in columns:
        dataframe[column] = pd.to_datetime(dataframe[column])
    return dataframe


def to_binary(x):
    """ 
        Map the aki and sex columns of the dataframe
        to binary values

       output:
            - 0: if the aki value is 'n' or if the sex value is 'm'
            - 1: if the aki value is 'y' or if the sex value is 'f'
    """
    if x == 'y': return 1
    elif x == 'f': return 1
    else: return 0