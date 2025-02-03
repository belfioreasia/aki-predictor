
# Acute Kidney Injury (AKI) Predictor

A Machine Learning model for the prediction of Acute Kidney Injury (AKI) from clinical temporal changes of creatinine levels.\
Trained on 7000+ clinical samples, this ML model can correctly predict the presence of AKI with **>98%** accuracy.

## Requirements

The project is written in `python`. The following third party packages are required to ensure full project functionality:

- [**numpy**](https://numpy.org/doc/stable/index.html): python package for mathematical and scientific computing. Actively maintained (Last Updated: December 2024), open-source and commercially supported.

- [**pandas**](https://pandas.pydata.org/): python package for data analysis, particularly suitable for handling relational and labelled data. Actively maintained (Last Updated: September 2024) and open-source.

- [**scikit-learn**](https://scikit-learn.org/stable/index.html): python package for data modeling and machine learning algorithms. Actively maintained (Last Updated: January 2025), open-source and commercially supported.

All requirements (along with the used versions) can be found in the [requirements.txt](requirements.txt) file.


## Model

[**SGD Classifier**](https://scikit-learn.org/1.5/modules/generated/sklearn.linear_model.SGDClassifier.html):
A Support Vector Machine (SVM) trained using Stochastic Gradient Descend (SGD).

**Model Hyperparameters**
- '*hinge*': loss function (defines a linear SVM).
- '*l2*': regularization term.
- '*100*': number of maximum epochs.


## Data

To enable prediction, the input clinical data must include:

- Sex (column 'sex): as 'f' (female) or 'm' (male)
- Age (column 'age'): an Integer
- Dates of blood tests taken (columns 'creatinine_date_x'): in the format 'DD/MM/YY HH:MM:SS'
- Results of each blood test (columns 'creatinine_result_x'): indicates the measured creatinine level, as an Integer

For each blood test, ensure that the date of the test is immediately followed by the test result:
> *Example Input Fields*\
> age, sex, creatinine_date_0, creatinine_result_0, creatinine_date_1, creatinine_result_1, creatinine_date_2, ...

The model output stored in the chosen file will contain 'y' if AKI has been detected, 'n' otherwise. 
Each line in the output file corresponds to the individual clinical data stored in the corresponding line in the input file.


## Example Usage
Clone this repository on your local device and enter the directory storing the 'model.py' file.\
To automatically install requirements:
```console
../bin/pip3 install -r requirements.txt
```

To get a prediction:
```console
python3 model.py --input={input_data_path}.csv --output={output_data_path}.csv
```
with 'input_data_path' being the path to the file with the target individual's clinical data, and 'output_data_path' being the desired path to store the prediction results.

The model will output 'y' if AKI has been detected, 'n' otherwise. Each line in the chosen output file will contain the prediction of the corresponding individual in the input file (same line).

> [!NOTE]\
> Instructions on Docker usage coming soon.


## Authors

- Belfiore Asia (*ab6124*)
    
    CID:02129867\
    Msc Advanced Computing,
    Imperial College London

