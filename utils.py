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
        while (j <= test_num) and (i < row_length):
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
        elapsed_days = pd.Timedelta(creatinine_test_dates.iloc[-1] - creatinine_test_dates.iloc[-2]) # second most recent test result
        # print(f"Elapsed days: {elapsed_days}")

        if elapsed_days <= pd.Timedelta(0):
            raise ValueError("The elapsed time between the last two tests is less than or equal to zero")
        elif (elapsed_days > pd.Timedelta(0)) and (elapsed_days <= pd.Timedelta(days=7)):
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


def format_patient_data(patient, non_empty_columns, non_creatinine_columns):
    """
        Return the formatted patient data
    """
    creatinine_test_dates = patient[non_creatinine_columns:non_empty_columns:2]
    creatinine_results = patient[(non_creatinine_columns+1):non_empty_columns:2]

    sex = to_binary(patient['sex'], 'f')
    age = patient['age']

    c1 = creatinine_results.iloc[-1] # most recent test result

    rv1 = creatinine_results.min() # lowest value 
    rv2 = creatinine_results.median() # median value

    rv_ratio = calculate_rv_ratio(c1, rv1, rv2, creatinine_test_dates)

    (elapsed_time, creatinine_change) = get_change_in_last_two_days(creatinine_test_dates, creatinine_results)
    # print(f"Creatinine change in {elapsed_time} = {creatinine_change}")

    return [sex, age, c1, rv1, rv2, rv_ratio, creatinine_change]


def process_patient_data(patient_data, data_type):
    """
        Return the processed patient data
    """
    try:
        non_creatinine_columns = 2
        if data_type == 'train':
            non_creatinine_columns += 1

        non_empty_columns = patient_data.count()

        patient = format_patient_data(patient_data, non_empty_columns, non_creatinine_columns)
        
        if data_type == 'train':
            aki_diagnosis = to_binary(patient_data['aki'], 'y')
            return (patient, aki_diagnosis)
        else:
            return patient
    except Exception as e:
        print(f"An error occurred while processing patient data: {e}")
        return ([], -1) if data_type == 'train' else []


def nhs_aki_algo(patient):
    """
    """
    [sex, age, c1, rv1, rv2, rv_ratio, D] = patient

    # (low_ri, high_ri) = get_reference_interval(sex, age)
    
    if rv_ratio >= 1.5:
        return 1
    elif D > 26:
        return 1
    else:
        return 0


def get_reference_interval(sex, age):
    """
        Return the Population Reference Interval (RI) based on
        age and sex of patient.
        source: resources/annual_conference_2016_-_recognition_of_aki.pdf
        https://www.google.com/url?sa=t&source=web&rct=j&opi=89978449&url=https://www.nwts.nhs.uk/_file/gCDJ8vu46p_275810.pdf&ved=2ahUKEwifj_P0mfuKAxWqXUEAHQ0oKQEQFnoECBcQAQ&usg=AOvVaw01O_TsELBULOw3GvBNEv3p
    """
    if age > 16:
        if sex == 'm': return (59, 104)
        else: return (45, 84)
    elif age == 16: 
        if sex == 'm': return (54, 99)
        else: return (48, 81)
    elif age == 15: 
        if sex == 'm': return (47, 98)
        else: return (44, 79)
    elif age == 14: 
        if sex == 'm': return (40, 83)
        else: return (43, 75)
    elif age == 13: 
        if sex == 'm': return (38, 76)
        else: return (38, 74)
    elif age == 12: return (36, 67)
    elif age == 11: return (36, 64)
    elif 9 <= age < 11: return (28, 57)
    elif 7 <= age < 9: return (30, 48)
    elif 5 <= age < 7: return (25, 42)
    elif 3 <= age < 5: return (23, 37)
    elif 1 <= age < 3: return (15, 31)
    elif age < 1: return (14, 81)