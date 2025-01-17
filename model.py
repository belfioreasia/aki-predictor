#!/usr/bin/env python3

import argparse
import csv
import random
from utils import *


def get_model_prediction(patient):
    try:
        aki_score = random.choice(["y", "n"])
        return to_label(aki_score, truth="y", false="n")
    except Exception as e:
        # Handle any potential exceptions
        print(f"An error occurred: {e}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="test.csv")
    parser.add_argument("--output", default="aki.csv")
    flags = parser.parse_args()
    r = csv.reader(open(flags.input))
    w = csv.writer(open(flags.output, "w"))
    w.writerow(("aki",))
    next(r) # skip headers
    
    for record in r:
        # TODO: Implement a better model
        patient = process_patient_data(record)

        w.writerow(get_model_prediction(patient))

if __name__ == "__main__":
    main()