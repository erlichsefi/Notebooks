from statistics import correlation, mode
import pandas as pd
import os
from sklearn import neural_network
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import plot_tree, DecisionTreeClassifier, export_graphviz
from sklearn.metrics import accuracy_score
import models.random_forest
from datetime import datetime

import plot_lib
import transform

now = datetime.now()
data = pd.read_excel("update_chance.xlsx")
data["Date "] = pd.to_datetime(data["Date "], dayfirst=True)
# plot_lib.plot(data)
print(data["Date "])

X, y, raw_y = transform.to_dummies_daily(data)
print(X.shape[2], y.shape)
X = X.reshape(X.shape[0], X.shape[2])
Corr = pd.DataFrame(X)
print("correlation matrix: ")
corr_matrix = Corr.corr()
print(corr_matrix)
print("X shape: ", X.shape, "y shape: ", y.shape)
result = models.random_forest.train_daily(X, y, raw_y)
result = pd.DataFrame(result)
print(
    "result for predict highest value is: ",
    result["Is_highest_card"].value_counts(normalize=True).mul(100).astype(str) + "%",
)
print(
    "result for predict second-highest value is: ",
    result["is_second_card"].value_counts(normalize=True).mul(100).astype(str) + "%",
)
print("running time: ", (datetime.now() - now))
