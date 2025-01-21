#!/usr/bin/env python3

import argparse
import csv
from sklearn.linear_model import SGDClassifier as SGD
import numpy as np
from utils import *

def main():
    try: 
        parser = argparse.ArgumentParser()
        parser.add_argument("--input", default="test.csv")
        parser.add_argument("--output", default="aki.csv")
        flags = parser.parse_args()
        r = csv.reader(open(flags.input))
        w = csv.writer(open(flags.output, "w"))
        w.writerow(("aki",))
        next(r) # skip headers

        model = SGD(loss="hinge", penalty="l2", max_iter=100)
        train_data = prepare_train_data('data/training.csv') # extract features from input data
        X_train = train_data.loc[:,'sex':'D'] # input features
        Y_train = train_data.loc[:,'aki'] # target labels
        model.fit(X_train.values, Y_train.values) # train SGD model

        for row in r:
            patient = prepare_test_data(row) # format input data for model prediction
            y_pred = model.predict(np.array(patient).reshape(1, -1))
            aki_pred = to_label(y_pred[0], 'y', 'n') # convert binary prediction to 'y'/'n' labels
            w.writerow((aki_pred,))

    except Exception as e:
        print(f"An error occurred while running the prediction: {e}")

if __name__ == "__main__":
    main()