import os
import argparse
import matplotlib.pyplot as plt
from numpy.core.multiarray import empty
import pandas as pd
import numpy as np
import sys
from keras.models import load_model
from keras.backend import clear_session
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import Dropout
from keras.layers import *
from sklearn.preprocessing import MinMaxScaler

if len(sys.argv) < 5:
    print("Too few arguments")
    quit()
elif len(sys.argv) > 5:
    print("Too many arguments")
    quit()

# Read the arguments
for i in range (1, len(sys.argv)):
    if(sys.argv[i] == "-d"):
        dataset_name = sys.argv[i+1]
    elif(sys.argv[i] == "-n"):
        num_time_series = int(sys.argv[i+1])

csv_path = os.path.join(os.path.abspath(__file__), "../../../dir/")
csv_path = os.path.join(csv_path, dataset_name)

model_path = os.path.join(os.path.abspath(__file__), "../../../models/")

# Read the input file
df = pd.read_csv(csv_path, header=None, delimiter='\t')
file_ids = df.iloc[:, [0]].values
df = df.drop(df.columns[0], axis=1)
df = df.transpose()

# Training data: 80%, Test data: 20%
train_size = int(len(df) * 0.80)
test_size = len(df) - train_size

sc = MinMaxScaler(feature_range = (0, 1))

# For each time series get a prediction
for step in range (0, num_time_series):
    X_train = []
    y_train = []
    
    training_set = df.iloc[:train_size, [step]].values
    training_set_scaled = sc.fit_transform(training_set)

    for i in range(60, train_size):
        X_train.append(training_set_scaled[i-60:i, 0])
        y_train.append(training_set_scaled[i, 0])

    X_train, y_train = np.array(X_train), np.array(y_train)
    X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))

    dataset_train = df.iloc[:train_size, [step]]
    dataset_test = df.iloc[train_size:, [step]]
    dataset_total = pd.concat((dataset_train, dataset_test), axis = 0)

    inputs = dataset_total[len(dataset_total) - len(dataset_test) - 60:].values
    inputs = inputs.reshape(-1,1)
    inputs = sc.transform(inputs)
    X_test = []
    for i in range(60, test_size+60):
        X_test.append(inputs[i-60:i, 0])

    X_test = np.array(X_test)
    X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))

    # Load model for this time series
    model = load_model(os.path.join(model_path, "Forecast_model" + str(step) +".h5"))

    # Get the prediction
    predicted_stock_price = model.predict(X_test)
    predicted_stock_price = sc.inverse_transform(predicted_stock_price)

    # Visualising the results
    plt.plot(dataset_test.values, color = 'red', label = 'Real values')
    plt.plot(predicted_stock_price, color = 'blue', label = 'Predicted values')
    plt.title('Time Series Prediction')
    plt.xlabel('Time')
    plt.ylabel('Value')
    plt.legend()
    fig = plt.gcf()
    fig.set_size_inches(18.5, 10.5)
    plt.savefig(os.path.join(os.path.abspath(__file__), "../../../dir/exports/q1/var1/graph"+ str(step) +".png"))
    plt.clf()

    del model
    clear_session()