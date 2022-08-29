from calendar import weekday
import pandas as pd
import numpy as np


def to_dummies_group_by_date(data):
    data_dummies = pd.get_dummies(data)
    new_data = data_dummies.groupby(data_dummies["Date "]).max().reset_index()
    new_data.to_excel("data_dumies.xlsx")

    return new_data


def to_dummies_daily(data):
    data_dummies = pd.get_dummies(
        data, columns=["Spade card", "Diamond card", "Heart card", "Club card"]
    )
    new_data = pd.DataFrame()
    for index, row in data_dummies.iterrows():
        new_data.at[index, "Date"] = row["Date "]
        new_data.at[index, "weekday"] = row["Date "].weekday()
        new_data.at[index, "month"] = row["Date "].month
        new_data.at[index, "year"] = row["Date "].year
    for i in ["7", "8", "9", "10", "J", "Q", "K", "A"]:
        new_data[i] = (
            data_dummies["Spade card_{}".format(i)]
            | data_dummies["Diamond card_{}".format(i)]
            | data_dummies["Heart card_{}".format(i)]
            | data_dummies["Club card_{}".format(i)]
        )
    new_data.reset_index(drop=True)
    X, y, raw_y = split_X_Y_daily(new_data)
    raw_y = pd.DataFrame(raw_y)

    return X, y, raw_y


def split_X_Y_daily(data, frame=1):
    data = data.iloc[::-1].reset_index(drop=True)
    datalen = len(data)
    X = []
    y = []
    raw_y = []
    for index, row in data.iterrows():
        Xi = []
        if index > datalen - frame - 1:
            break
        yi = data.iloc[index + frame, 4:].values.tolist()
        for i in range(0, frame):
            Xi.append(data.iloc[index + i, 1:].values.tolist())
        X.append(Xi)
        for i in range(0, 7):
            if index + frame + i > datalen - 100:
                break
            if (
                data.loc[index + frame, ["Date"]].values
                == data.loc[index + frame + i, ["Date"]].values
            ):
                yi = np.logical_or(yi, data.iloc[index + frame + i, 4:].values.tolist())
        np.append(
            data.loc[index + frame, ["weekday"]].values,
            data.loc[index + frame, ["month"]].values,
        )
        raw_yi = yi
        raw_yi = np.multiply(np.array(raw_yi), 1)
        raw_yi = np.append(raw_yi, data.loc[index + frame, ["Date"]].values)
        y.append(yi)
        raw_y.append(raw_yi)

    y = np.multiply(np.array(y), 1)
    X = np.array(X)

    return X, y, raw_y
