import pandas as pd

def to_binary(label, truth):
    """ 
        Maps a string label to a binary one based on the given parameters. 
        Used to covert 'sex' field (m/f to 0/1) and 'aki' field (n/y to 0/1) to binary labels.
        Raises a 'ValueError' if the label is not equal to any accepted value.

        inputs: 
            - label (string): the input label to be converted
            - truth (string): the label to be converted to 1
        outputs:
            - (int): 1 if the label is equal to the truth, 0 otherwise
    """
    if label == truth: return 1
    elif label != truth: return 0
    else: 
        raise ValueError(f"Invalid '{label}' label for binary conversion")

def to_label(binary_label, truth, false):
    """ 
        Maps a binary label to a string one based on the given parameters. 
        Used to covert the model 'aki' prediction (0/1 to n/y).
        Raises a 'ValueError' if the label is not equal to any accepted value.
        
        inputs: 
            - binary_label (string): the input label to be converted
            - truth (string): the label corresponding to input 1
            - false (string): the label corresponding to input 0
        outputs:
            - (string): the label corresponding to the binary input
    """
    if binary_label == 1: return truth
    elif binary_label == 0: return false
    else: 
        raise ValueError(f"Invalid binary label '{binary_label}' for re-conversion")

def get_longest_row(filepath):
    """ 
        Finds the row with the most entries in the dataset (i.e. the patient 
        with the highest number of blood tests taken).
        
        inputs: 
            - filepath (string): the path to the dataset file
        outputs:
            - (int): the length of the longest row found in the dataset
    """
    try:
        file = open(filepath, 'r')
        lines = file.readlines()
        longest_row = 0
        for line in lines:
            curr_row = len(line.split(','))
            longest_row = max(longest_row, curr_row)
        return longest_row
    except Exception as e:
        print(f"An error occurred while reading file {filepath}: {e}")
        return -1

def get_header(row_length, dataset_type):
    """ 
        Creates a sutable header for the dataset based on the number of tests taken.
        
        inputs: 
            - row_length (int): the length of the current row in the dataset. Should accomodate:
                                - one entry for 'age'
                                - one entry for 'sex'
                                - one entry for 'aki' (only for the training set)
                                - two entries for each test taken (date and result)*
            - dataset_type (string): the type of dataset (train/test)
                                     If euqal to 'train', includes the 'aki' column
        outputs:
            - (list): a list of strings representing the column names of the dataset
    """
    try:
        header = ['' for _ in range(row_length)]
        header[:2] = ['age', 'sex']
        i = 2
        # add the 'aki' column if the dataset is the training set
        if dataset_type == 'train':
            header[i] = 'aki'
            i += 1
        
        # calculate the number of taken tests
        test_num = (row_length - i) // 2
        j = 0
        while (j < test_num) and (i < row_length):
            header[i] = f'creatinine_date_{j}'
            header[i+1] = f'creatinine_result_{j}'
            j += 1
            i += 2 # * move to the next test by skipping two values
        return header
    except Exception as e:
        print(f"An error occurred while creating header: {e}")
        return []

def get_change_in_last_two_days(test_dates, test_results):
    """ 
        Calculates the change (in mg/dL) in creatinine levels in the two days prior
        to the last taken blood test.
        
        inputs: 
            - test_dates (list): a list with the dates of the blood tests taken. 
                                 Should be in 'DD/MM/YYYY HH:MM:SS' format.
                                 Should be sorted in ascending order.
                                 Should have the same length as test_results.
            - test_results (list): a list with the creatinine levels measured with 
                                   each blood tests taken.
                                   Should be sorted in ascending order.
                                   Should have the same length as test_results.
        outputs:
            - (pd.Timedelta): the time elapsed between the last test and the first one taken within 48 hours
            - (float): the overall change in creatinine levels within the last 48 hours
    """
    try:
        if len(test_dates) != len(test_results):
            raise ValueError(f"The number of test dates ({len(test_dates)}) and test results ({len(test_results)}) doesn't match.")
        
        elapsed_time = pd.Timedelta(0)
        useable_test_results = [test_results.iloc[-1]] # store all test results within 48 hours
        creatinine_change = 0

        if len(test_dates) < 2: # if only one test has been taken overall, there's no calculable change
            return (pd.Timedelta(0), 0)

        for test_num in range(len(test_dates)-2, -1, -1):
            elapsed_time += pd.Timedelta(test_dates.iloc[test_num+1] - test_dates.iloc[test_num])
            if elapsed_time <= pd.Timedelta(days=2):
                useable_test_results.append(test_results.iloc[test_num])
            else:
                test_num = -1
                
        if len(useable_test_results) < 2: # if only one test has been taken within 48 hours there's no value change
            return (pd.Timedelta(0), 0)
        
        creatinine_change = useable_test_results[0] - min(useable_test_results[1:])
        return (elapsed_time, creatinine_change)
    except Exception as e:
        print(f"An error occurred while calculating the creatinine change within 48 hours: {e}")
        return (-1, -1)

def calculate_rv_ratio(c1, rv1, rv2, creatinine_test_dates):
    """ 
        Calculates the rv ratio based on the time elapsed between the two most recently taken blood tests.
        Calculations follow the guidelines described in the NHS algorithm specifications.
        
        inputs: 
            - c1 (float): the most recent creatinine level measured
            - rv1 (float): the minimum creatinine level measured
            - rv2 (float): the median creatinine level measured
            - creatinine_test_dates (list): a list with the dates of the blood tests taken.
        outputs:
            - (float): the appropriate rv ratio calculated based on the time elapsed between the tests
    """
    try:
        if len(creatinine_test_dates) <= 1:
            elapsed_days = pd.Timedelta(0)
        else:
            elapsed_days = pd.Timedelta(creatinine_test_dates.iloc[-1] - creatinine_test_dates.iloc[-2]) # second most recent test result

        # if elapsed_days < pd.Timedelta(0):
        #     print(elapsed_days)
        #     raise ValueError("The elapsed time between the last two tests is less than or equal to zero")
        if (elapsed_days >= pd.Timedelta(0)) and (elapsed_days <= pd.Timedelta(days=7)):
            # print(f"Elapsed days in [0,7]")
            return c1/rv1
        elif (elapsed_days > pd.Timedelta(days=7)) and (elapsed_days <= pd.Timedelta(days=365)):
            # print(f"Elapsed days in [7,365]")
            return c1/rv2
        elif (elapsed_days > pd.Timedelta(days=365)):
            # print(f"Elapsed days > 365")
            return 0
    except Exception as e:
        print(f"An error occurred while calculating the RV ratio: {e}")
        return -1

def extract_patient_features(patient, creatinine_columns):
    """ 
        Extracts the features to be used for the model training and testing from the individual's 
        clinical data. Following the NHS algorithms specifications, the features are described 
        below in the output section.
        
        inputs: 
            - patient (pd.Series): the patient's clinical data
            - creatinine_columns (list): the list of columns names containing the creatinine 
                                         test dates and results
        outputs:
            - sex (int): 0 if the patient is male, 1 if the patient is female
            - age (int)
            - c1 (float): the most recent creatinine level measured
            - rv1 (float): the minimum creatinine level measured
            - rv2 (float): the median creatinine level measured
            - rv_ratio (float): the appropriate rv ratio calculated based on the time elapsed between the tests
            - creatinine_change (float): the change in creatinine levels in the two days prior to the
                                         last taken blood test. Also referred to as 'D'.
    """
    # get the last non-empty column of the patient data
    last_col = patient[::-1].notnull().idxmax()
    
    creatinine_test_dates = patient.loc[creatinine_columns[0]:last_col:2] # even rows contain test dates
    creatinine_results = patient.loc[creatinine_columns[1]:last_col:2].astype(float) # odd rows contain test results

    sex = to_binary(patient['sex'], 'f')
    age = patient['age']
    
    c1 = creatinine_results.iloc[-1]
    rv1 = creatinine_results.min()
    rv2 = creatinine_results.median(numeric_only=True)
    
    rv_ratio = calculate_rv_ratio(c1, rv1, rv2, creatinine_test_dates)
    
    (elapsed_time, creatinine_change) = get_change_in_last_two_days(creatinine_test_dates, creatinine_results)
    # print(f"Creatinine change in {elapsed_time} = {creatinine_change}")

    return sex, age, c1, rv1, rv2, rv_ratio, creatinine_change

def process_patient_data(patient_data, creatinine_columns, data_type):
    """ 
        Formatts the clinical data in a suitable format (see 'extract_patient_features' function).
        Handles individual-level data.
        
        inputs: 
            - patient (pd.Series): the patient's clinical data
            - creatinine_columns (list): the list of columns names containing the creatinine 
                                         test dates and results
            - data_type (string): the type of dataset ('train'/'test')
        outputs:
            - (pd.Series): formatted features extracted from the patient's clinical data (described
                           in the 'extract_patient_features' function).
                           Includes the 'aki' column if the dataset is the training set.
    """
    try:
        sex, age, c1, rv1, rv2, rv_ratio, creatinine_change = extract_patient_features(patient_data, creatinine_columns)
        if data_type == 'train':
            aki_diagnosis = to_binary(patient_data['aki'], 'y')
            return pd.Series((sex, age, c1, rv1, rv2, rv_ratio, creatinine_change, aki_diagnosis))
        else:
            return pd.Series((sex, age, c1, rv1, rv2, rv_ratio, creatinine_change))
    except Exception as e:
        print(f"An error occurred while processing patient data: {e}")
        return ((),)

def prepare_train_data(data):
    """ 
        Formats the clinical data of the training dataset in a suitable format (see 
        'extract_patient_features' function). Handles bulk-level data for the creation of 
        a training dataset of patient features.
        
        inputs: 
            - data (string): the path to the training dataset file
        outputs:
            - (pd.Dataframe): formatted features extracted from the patient's clinical data
                              (described in the 'extract_patient_features' function).
                              Includes the 'aki' column if the dataset is the training set.
    """
    header_len = get_longest_row(data)
    header = get_header(header_len, 'train')

    creatinine_columns = [col for col in header if 'creatinine' in col]

    # create dataframe with the created header, skippiing the given one in the file
    patient_data = pd.read_csv(data, sep=',', names=header, skiprows=1)

    # change every test date column into datetime type to allow for time calculations
    for col in creatinine_columns[::2]:
        patient_data[col] = pd.to_datetime(patient_data[col])

    # format the dataset for each patient entry
    formatted_dataset = patient_data.apply(lambda patient_record: process_patient_data(patient_record, creatinine_columns, data_type = 'train'), axis=1)
    
    formatted_dataset = pd.DataFrame(formatted_dataset)
    formatted_dataset.rename(columns={0: 'sex', 
                                        1: 'age',
                                        2: 'c1',
                                        3: 'rv1',
                                        4: 'rv2',
                                        5: 'rv_ratio',
                                        6: 'D',
                                        7: 'aki'}, 
                            inplace=True)
    return formatted_dataset

def prepare_test_data(data):
    """ 
        Handles the formatting of the individual-level target data for the creation of 
        a test (or evaluation) dataset of patient features (see 'extract_patient_features' function).
        
        inputs: 
            - data (string): the file line/entry containing the patient's clinical data
        outputs:
            - (pd.Series): formatted features extracted from the patient's clinical data
                            (described in the 'extract_patient_features' function).
                            Includes the 'aki' column if the dataset is the training set.
    """
    # remove empty entries from the data and remove any presence of 'y'/'n' aki labels
    # (eg. to handle entries in the training dataset)
    data = [d for d in data if ((d != '') and (d != 'y') and (d != 'n'))]

    header_len = len(data)
    header = get_header(header_len, 'test')

    creatinine_columns = [col for col in header if 'creatinine' in col]

    patient_data = {col_i:data_i for col_i, data_i in zip(header, data)}

    # change every test date column into datetime type
    for col in creatinine_columns[::2]:
        patient_data[col] = pd.to_datetime(patient_data[col])

    patient = pd.Series(patient_data)

    formatted_patient = process_patient_data(patient, creatinine_columns, data_type = 'test')
    
    formatted_patient.rename({  0: 'sex', 
                                1: 'age',
                                2: 'c1',
                                3: 'rv1',
                                4: 'rv2',
                                5: 'rv_ratio',
                                6: 'D',}, 
                                inplace=True)
    return formatted_patient