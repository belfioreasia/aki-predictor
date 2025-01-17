import pandas as pd
from utils import *

def nhs_aki_algo(patient, data_type = 'train'):
    """
    """
    [sex, age, c1, rv1, rv2, rv_ratio, D] = process_patient_data(patient, data_type)

    (low_ri, high_ri) = get_reference_interval(sex, age)

    elapsed_days = 0
    if elapsed_days <= 0:
        print("Error: invalid elapsed time between most recent creatinine test results.")
        return 0
    elif (elapsed_days > 0) and (elapsed_days <= 7):
        rv_ratio = c1/rv1
    elif (elapsed_days > 7) and (elapsed_days <= 365):
        rv_ratio = c1/rv2
    elif elapsed_days > 365:
        return 0
    
    if rv_ratio >= 1.5:
        return 1
    elif D > 26:
        return 1
    else:
        return 0
        

