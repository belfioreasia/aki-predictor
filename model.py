#!/usr/bin/env python3

import argparse
import csv
from sklearn.linear_model import SGDClassifier as SGD
from sklearn.metrics import fbeta_score
import numpy as np
from utils import *

def create_model(loss = "hinge", penalty = "l2", max_iter = 100, train_val_split = 0.8):
    """ 
        Creates a SGD Classifier with the given parameters. Trains and validates the model using 
        the 'data/training.csv' data file (split based on the value of the 'train_val_split' parameter).
        Checks the performance of the model using the F3 score calculated on the validation
        dataset and throws an exception if the score is below 0.7 (NHS algorithm threshold).

        inputs: 
            - loss (string): the chosen loss function (defaults to 'hinge' to define a SVM)
            - penalty (string): the regularization term (defaults to 'l2')
            - max_iter (int): the number of total epochs for model training (defaults to 100)
            - train_val_split (float): the portion of training dataset to be used for validation
                                       (defaults to 0.8 for 80% training and 20% validation split)
        outputs:
            - (SGDClassifier): trained model
    """
    model = SGD(loss = loss, penalty = penalty, max_iter = max_iter)
        
    # Model training
    print("Starting Model Training...")
    train_data = prepare_train_data('data/training.csv') # extract features from input data
    train_split = len(train_data) * train_val_split # split training data into training (80%) and validation (20%) sets
    X_train = train_data.loc[:train_split,'sex':'D'] # input features
    Y_train = train_data.loc[:train_split,'aki'] # target labels
    model.fit(X_train.values, Y_train.values)
    print("Model Training Complete.")

    # Model Valudation
    X_test = train_data.loc[train_split:,'sex':'D']
    Y_test = train_data.loc[train_split:,'aki']
    test_pred = model.predict(X_test.values)
    f3_score = fbeta_score(Y_test, test_pred, beta=3)
    if f3_score < 0.7:
        raise Exception(f"Model performance ({f3_score}) is below the required threshold of 0.7.")
    else:
        print(f"Model performance meets F3 score requirements ({f3_score})")
    return model

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

        model = create_model() # create and train model

        print("Starting Model Prediction...")
        for row in r:
            patient = prepare_test_data(row) # format input data for model prediction
            y_pred = model.predict(np.array(patient).reshape(1, -1))
            aki_pred = to_label(y_pred[0], 'y', 'n') # convert binary prediction to 'y'/'n' labels
            w.writerow((aki_pred,))
        print("Model Prediction Complete.")

    except Exception as e:
        print(f"An error occurred while running the prediction: {e}")

if __name__ == "__main__":
    main()