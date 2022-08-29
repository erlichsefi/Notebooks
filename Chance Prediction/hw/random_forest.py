from unittest import result
from keras.models import Sequential
from keras.layers import Dense, Activation
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestRegressor


def train_column(data, column, frame=60):
    train_data = data.loc[:, [column]].values.reshape(-1, 1)
    data_samples = train_data.shape[0] - frame - 1
    X = []
    y = []
    for i in range(0, data_samples):
        X.append(train_data[i : i + frame])
        y.append(train_data[i + frame + 1])
    X = np.array(X)
    y = np.array(y)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False
    )
    n_samples, nx, ny = X_train.shape
    X_train = X_train.reshape(n_samples, nx * ny)
    y_train = y_train.reshape(
        n_samples,
    )
    n_samples, nx, ny = X_test.shape
    X_test = X_test.reshape(n_samples, nx * ny)
    y_test = y_test.reshape(
        n_samples,
    )
    y_hat = random_forest(X_train, y_train, X_test)
    y_hat_round = np.round(y_hat)
    test_accuracy = sklearn.metrics.accuracy_score(y_test, y_hat_round)
    print("max value", np.amax(y_hat))
    print("test accuracy", test_accuracy)

    return y_hat, test_accuracy


def train(data):
    frame = 11
    columns = data.columns[2:]
    result = pd.DataFrame([])
    accuracy_score = []
    for column in columns:
        y_hat, accuracy = train_column(data, column, frame)
        accuracy_score.append(accuracy)
        result[column] = pd.DataFrame(y_hat)
    result = add_date(data, result)
    result = transform_to_2_highest_value(data, result)
    print(accuracy_score, "accuracy", np.average(accuracy_score))

    return result


def transform_to_2_highest_value(data, raw_result):
    columns = list(raw_result.columns)
    result = []
    for index, row in raw_result.iterrows():
        highest = 0
        second = 0
        new_row = []
        highest_card = 0
        second_card = 0
        is_highest_card = "failed to predict"
        is_second_card = "failed to predict"
        for column in columns:
            if column == "Date":
                new_row.append(row[column])
            elif highest < row[column]:
                highest = row[column]
                highest_card = column
        for column in columns:
            if column == "Date":
                continue
            elif row[column] < highest and row[column] >= second:
                second = row[column]
                second_card = column
        data_row = data.loc[index]
        if data_row[highest_card] == 1:
            is_highest_card = "predicted correctly"
        if data_row[second_card] == 1:
            is_second_card = "predicted correctly"
        new_row.extend(
            [
                highest_card,
                highest * 100,
                is_highest_card,
                second_card,
                second * 100,
                is_second_card,
            ]
        )
        result.append(new_row)
    result = pd.DataFrame(
        result,
        columns=[
            "Date",
            "Highest_card",
            "Highest_percentage",
            "Is_highest_card",
            "Second_highest_card",
            "Second_Percentage",
            "is_second_card",
        ],
    )

    return result


def add_date(data, result):
    start_point = data.shape[0] - result.shape[0]
    date = pd.DataFrame(data.loc[start_point:, ["Date "]])
    result.insert(0, "Date", date)
    result["Date"] = result["Date"].dt.strftime("%m/%d/%Y")

    return result


def random_forest(X, y, X_test, y_test):
    model = RandomForestRegressor(n_estimators=1000)
    print("--------training random forest-----------")
    model.fit(X, y)
    y_pre = model.predict(X)
    y_pre_round = np.round(y_pre)
    train_accuracy = sklearn.metrics.accuracy_score(y_pre_round, y)
    print("trainning accuracy: ", train_accuracy)
    yhat = model.predict(X_test)
    yhat_round = np.round(yhat)
    test_accuracy = sklearn.metrics.accuracy_score(yhat_round, y_test)
    print("test accuracy: ", test_accuracy)

    return yhat


def train_daily(X, y, raw_y):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False
    )
    result = pd.DataFrame()
    print("many train: ",y_train.shape[1])
    for i in range(0, y_train.shape[1]):
        result[i] = random_forest(X_train, y_train[:, i], X_test, y_test[:, i])
    result = pd.DataFrame(result)
    result.columns = ["7", "8", "9", "10", "J", "Q", "K", "A"]
    raw_y.columns = ["7", "8", "9", "10", "J", "Q", "K", "A", "Date"]
    date = raw_y.loc[y_train.shape[0] :, ["Date"]].reset_index(drop=True)
    raw_y = raw_y.loc[y_train.shape[0] :, :].reset_index(drop=True)
    result["Date"] = date
    highest_value_result = transform_to_2_highest_value(raw_y, result)
    highest_value_result.to_excel("result.xlsx")

    return highest_value_result
