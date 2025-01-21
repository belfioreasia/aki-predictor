import pandas as pd


def to_binary(label, truth):
    """ 
        Map 'y' for aki and 'f' for sex to 1, and 
       'n' for aki and 'm' for sex to 0 
    """
    if label == truth: return 1
    elif label != truth: return 0
    else: 
        raise ValueError(f"Invalid '{truth}' label for binary conversion")
    

def to_label(binary_label, truth, false):
    """ 
        Map 'y' for aki and 'f' for sex to 1, and 
       'n' for aki and 'm' for sex to 0 
    """
    if binary_label == 1: return truth
    elif binary_label == 0: return false
    else: 
        raise ValueError(f"Invalid binary label '{binary_label}' for re-conversion")


def get_header(row_length, dataset_type):
    """
        Return the header for the dataset
    """
    try:
        header = ['' for _ in range(row_length)]
        header[:2] = ['age', 'sex']
        i = 2
        if dataset_type == 'train':
            header[i] = 'aki'
            i += 1
        elif dataset_type != 'test':
            raise Exception(f"Invalid dataset type: {dataset_type}")
        test_num = (row_length - i) // 2
        j = 0
        while (j < test_num) and (i < row_length):
            header[i] = f'creatinine_date_{j}'
            header[i+1] = f'creatinine_result_{j}'
            j += 1
            i += 2

        return header
    
    except Exception as e:
        print(f"An error occurred while creating header: {e}")
        return []


def get_longest_row(filepath):
    """
        Return the longest row in the dataset
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
    

def get_change_in_last_two_days(test_dates, test_results):
    """
        Return the change in creatinine levels in the last two days
    """
    try:
        elapsed_time = pd.Timedelta(0)
        useable_test_results = [test_results.iloc[-1]]
        creatinine_change = 0

        if len(test_dates) < 2:
            return (pd.Timedelta(0), 0)

        for test_num in range(len(test_dates)-2, -1, -1):
            elapsed_time += pd.Timedelta(test_dates.iloc[test_num+1] - test_dates.iloc[test_num])
            if elapsed_time <= pd.Timedelta(days=2):
                useable_test_results.append(test_results.iloc[test_num])
            else:
                test_num = -1
        
        # print(f"Useable test results: {useable_test_results} in {len(test_dates)} total tests")
        
        if len(useable_test_results) < 2:
            return (pd.Timedelta(0), 0)
        
        creatinine_change = useable_test_results[0] - min(useable_test_results[1:])
        return (elapsed_time, creatinine_change)
    except Exception as e:
        print(f"An error occurred while calculating the creatinine change within 48 hours: {e}")
        return (-1, -1)


def calculate_rv_ratio(c1, rv1, rv2, creatinine_test_dates):
    """
        Return the ratio of creatinine levels
    """
    try:
        if len(creatinine_test_dates) <= 1:
            elapsed_days = pd.Timedelta(0)
        else:
            elapsed_days = pd.Timedelta(creatinine_test_dates.iloc[-1] - creatinine_test_dates.iloc[-2]) # second most recent test result
        # print(f"Elapsed days: {elapsed_days}")

        # if elapsed_days < pd.Timedelta(0):
            # print(elapsed_days)
            # raise ValueError("The elapsed time between the last two tests is less than or equal to zero")
        if (elapsed_days >= pd.Timedelta(0)) and (elapsed_days <= pd.Timedelta(days=7)):
            # print(f"Elapsed days in [0,7]")
            return c1/rv1
        elif (elapsed_days > pd.Timedelta(days=7)) and (elapsed_days <= pd.Timedelta(days=365)):
            # print(f"Elapsed days in [7,365]")
            return c1/rv2
        elif (elapsed_days > pd.Timedelta(days=365)):
            # print(f"Elapsed days > 365")
            return 0
    except ValueError as ve:
        print(f"An error occurred while calculating the RV ratio: {ve}")
        return -1


def extract_patient_features(patient, creatinine_columns):
    """
        Return the formatted patient data
    """
    # get the last non-empty column of the patient data
    last_col = patient[::-1].notnull().idxmax()
    
    creatinine_test_dates = patient.loc[creatinine_columns[0]:last_col:2]
    creatinine_results = patient.loc[creatinine_columns[1]:last_col:2].astype(float)

    sex = to_binary(patient['sex'], 'f')
    age = patient['age']
    
    c1 = creatinine_results.iloc[-1] # most recent test result

    rv1 = creatinine_results.min() # lowest value
    rv2 = creatinine_results.astype(float).median(numeric_only=True) # median value
    
    rv_ratio = calculate_rv_ratio(c1, rv1, rv2, creatinine_test_dates)
    
    (elapsed_time, creatinine_change) = get_change_in_last_two_days(creatinine_test_dates, creatinine_results)
    # print(f"Creatinine change in {elapsed_time} = {creatinine_change}")

    return sex, age, c1, rv1, rv2, rv_ratio, creatinine_change


def process_patient_data(patient_data, creatinine_columns, data_type):
    """
        Return the processed patient data
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
        return ([], -1) if data_type == 'train' else []
    

def prepare_train_data(data):
    """
        Return the processed dataset for each patient
    """
    header_len = get_longest_row(data)
    header = get_header(header_len, 'train')

    creatinine_columns = [col for col in header if 'creatinine' in col]

    patient_data = pd.read_csv(data, sep=',', names=header, skiprows=1)

    # change every test date column into datetime type
    for col in creatinine_columns[::2]:
        patient_data[col] = pd.to_datetime(patient_data[col])

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
        Return the processed dataset for each patient
    """

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
