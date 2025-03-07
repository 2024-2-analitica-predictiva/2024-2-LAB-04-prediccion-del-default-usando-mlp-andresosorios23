# flake8: noqa: E501
#
# En este dataset se desea pronosticar el default (pago) del cliente el próximo
# mes a partir de 23 variables explicativas.
#
#   LIMIT_BAL: Monto del credito otorgado. Incluye el credito individual y el
#              credito familiar (suplementario).
#         SEX: Genero (1=male; 2=female).
#   EDUCATION: Educacion (0=N/A; 1=graduate school; 2=university; 3=high school; 4=others).
#    MARRIAGE: Estado civil (0=N/A; 1=married; 2=single; 3=others).
#         AGE: Edad (years).
#       PAY_0: Historia de pagos pasados. Estado del pago en septiembre, 2005.
#       PAY_2: Historia de pagos pasados. Estado del pago en agosto, 2005.
#       PAY_3: Historia de pagos pasados. Estado del pago en julio, 2005.
#       PAY_4: Historia de pagos pasados. Estado del pago en junio, 2005.
#       PAY_5: Historia de pagos pasados. Estado del pago en mayo, 2005.
#       PAY_6: Historia de pagos pasados. Estado del pago en abril, 2005.
#   BILL_AMT1: Historia de pagos pasados. Monto a pagar en septiembre, 2005.
#   BILL_AMT2: Historia de pagos pasados. Monto a pagar en agosto, 2005.
#   BILL_AMT3: Historia de pagos pasados. Monto a pagar en julio, 2005.
#   BILL_AMT4: Historia de pagos pasados. Monto a pagar en junio, 2005.
#   BILL_AMT5: Historia de pagos pasados. Monto a pagar en mayo, 2005.
#   BILL_AMT6: Historia de pagos pasados. Monto a pagar en abril, 2005.
#    PAY_AMT1: Historia de pagos pasados. Monto pagado en septiembre, 2005.
#    PAY_AMT2: Historia de pagos pasados. Monto pagado en agosto, 2005.
#    PAY_AMT3: Historia de pagos pasados. Monto pagado en julio, 2005.
#    PAY_AMT4: Historia de pagos pasados. Monto pagado en junio, 2005.
#    PAY_AMT5: Historia de pagos pasados. Monto pagado en mayo, 2005.
#    PAY_AMT6: Historia de pagos pasados. Monto pagado en abril, 2005.
#
# La variable "default payment next month" corresponde a la variable objetivo.
#
# El dataset ya se encuentra dividido en conjuntos de entrenamiento y prueba
# en la carpeta "files/input/".
#
# Los pasos que debe seguir para la construcción de un modelo de
# clasificación están descritos a continuación.
#
#
# Paso 1.
# Realice la limpieza de los datasets:
# - Renombre la columna "default payment next month" a "default".
# - Remueva la columna "ID".
# - Elimine los registros con informacion no disponible.
# - Para la columna EDUCATION, valores > 4 indican niveles superiores
#   de educación, agrupe estos valores en la categoría "others".
# - Renombre la columna "default payment next month" a "default"
# - Remueva la columna "ID".
#
#
# Paso 2.
# Divida los datasets en x_train, y_train, x_test, y_test.
#
#
# Paso 3.
# Cree un pipeline para el modelo de clasificación. Este pipeline debe
# contener las siguientes capas:
# - Transforma las variables categoricas usando el método
#   one-hot-encoding.
# - Descompone la matriz de entrada usando componentes principales.
#   El pca usa todas las componentes.
# - Escala la matriz de entrada al intervalo [0, 1].
# - Selecciona las K columnas mas relevantes de la matrix de entrada.
# - Ajusta una red neuronal tipo MLP.
#
#
# Paso 4.
# Optimice los hiperparametros del pipeline usando validación cruzada.
# Use 10 splits para la validación cruzada. Use la función de precision
# balanceada para medir la precisión del modelo.
#
#
# Paso 5.
# Guarde el modelo (comprimido con gzip) como "files/models/model.pkl.gz".
# Recuerde que es posible guardar el modelo comprimido usanzo la libreria gzip.
#
#
# Paso 6.
# Calcule las metricas de precision, precision balanceada, recall,
# y f1-score para los conjuntos de entrenamiento y prueba.
# Guardelas en el archivo files/output/metrics.json. Cada fila
# del archivo es un diccionario con las metricas de un modelo.
# Este diccionario tiene un campo para indicar si es el conjunto
# de entrenamiento o prueba. Por ejemplo:
#
# {'dataset': 'train', 'precision': 0.8, 'balanced_accuracy': 0.7, 'recall': 0.9, 'f1_score': 0.85}
# {'dataset': 'test', 'precision': 0.7, 'balanced_accuracy': 0.6, 'recall': 0.8, 'f1_score': 0.75}
#
#
# Paso 7.
# Calcule las matrices de confusion para los conjuntos de entrenamiento y
# prueba. Guardelas en el archivo files/output/metrics.json. Cada fila
# del archivo es un diccionario con las metricas de un modelo.
# de entrenamiento o prueba. Por ejemplo:
#
# {'type': 'cm_matrix', 'dataset': 'train', 'true_0': {"predicted_0": 15562, "predicte_1": 666}, 'true_1': {"predicted_0": 3333, "predicted_1": 1444}}
# {'type': 'cm_matrix', 'dataset': 'test', 'true_0': {"predicted_0": 15562, "predicte_1": 650}, 'true_1': {"predicted_0": 2490, "predicted_1": 1420}}
#

import json
import gzip
import pickle

import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.decomposition import PCA
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import (
    precision_score,
    balanced_accuracy_score,
    recall_score,
    f1_score,
    confusion_matrix,
)
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def main() -> None:
    test_data = pd.read_csv("files/input/test_data.csv.zip")
    train_data = pd.read_csv("files/input/train_data.csv.zip")

    # Paso 1
    test_data = test_data.rename(columns={"default payment next month": "default"})
    train_data = train_data.rename(columns={"default payment next month": "default"})

    test_data = test_data.drop(columns="ID")
    train_data = train_data.drop(columns="ID")

    test_data = test_data[test_data["MARRIAGE"] != 0]
    train_data = train_data[train_data["MARRIAGE"] != 0]

    test_data = test_data[test_data["EDUCATION"] != 0]
    train_data = train_data[train_data["EDUCATION"] != 0]

    train_data.loc[train_data["EDUCATION"] > 4, "EDUCATION"] = 4
    test_data.loc[test_data["EDUCATION"] > 4, "EDUCATION"] = 4

    # Paso 2
    x_train = train_data.drop(columns="default")
    y_train = train_data["default"]
    x_test = test_data.drop(columns="default")
    y_test = test_data["default"]

    # Paso 3

    categorical_variables = ["SEX", "EDUCATION", "MARRIAGE"]
    preprocessor = ColumnTransformer(
        transformers=[("cat", OneHotEncoder(), categorical_variables)],
        remainder="passthrough",
    )

    scaled_variables = x_train.columns.difference(categorical_variables)
    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(), categorical_variables),
            ("scaler", StandardScaler(), scaled_variables),
        ]
    )
    pipeline = Pipeline(
        [
            ("preprocessor", preprocessor),
            ("feature_selection", SelectKBest()),
            ("pca", PCA()),
            ("classifier", MLPClassifier()),
        ]
    )

    # Paso 4. Definir la búsqueda de hiperparámetros para la optimización
    parameter_grid = {
        "pca__n_components": [None],
        "feature_selection__k": [20],
        "classifier__hidden_layer_sizes": [(50, 30, 40, 60), (50, 30, 30, 60)],
        "classifier__alpha": [0.13, 0.26],
        "classifier__random_state": [9, 21],
        "classifier__max_iter": [15000, 20000],
    }

    grid_search = GridSearchCV(
        pipeline,
        parameter_grid,
        cv=10,
        scoring="balanced_accuracy",
        n_jobs=-1,
        refit=True,
        verbose=2,
    )
    grid_search.fit(x_train, y_train)
    y_train_prediction = grid_search.predict(x_train)
    y_test_prediction = grid_search.predict(x_test)
    print(grid_search.best_params_)

    # Paso 5

    with gzip.open("files/models/model.pkl.gz", "wb") as f:
        pickle.dump(grid_search, f)

    # Paso 6

    metrics_train = {
        "type": "metrics",
        "dataset": "train",
        "precision": precision_score(y_train, y_train_prediction),
        "balanced_accuracy": balanced_accuracy_score(y_train, y_train_prediction),
        "recall": recall_score(y_train, y_train_prediction),
        "f1_score": f1_score(y_train, y_train_prediction),
    }

    metrics_test = {
        "type": "metrics",
        "dataset": "test",
        "precision": precision_score(y_test, y_test_prediction),
        "balanced_accuracy": balanced_accuracy_score(y_test, y_test_prediction),
        "recall": recall_score(y_test, y_test_prediction),
        "f1_score": f1_score(y_test, y_test_prediction),
    }

    metrics = [metrics_train, metrics_test]

    with open("files/output/metrics.json", "w") as f:
        for metric in metrics:
            f.write(f"{json.dumps(metric)}\n")

    # Paso 7

    confusion_matrix_train = confusion_matrix(y_train, y_train_prediction).tolist()

    confusion_matrix_test = confusion_matrix(y_test, y_test_prediction).tolist()

    confusion_matrix_train_result = {
        "type": "cm_matrix",
        "dataset": "train",
        "true_0": {
            "predicted_1": int(confusion_matrix_train[0][1]),
            "predicted_0": int(confusion_matrix_train[0][0]),
        },
        "true_1": {
            "predicted_0": int(confusion_matrix_train[1][0]),
            "predicted_1": int(confusion_matrix_train[1][1]),
        },
    }

    confusion_matrix_test_result = {
        "type": "cm_matrix",
        "dataset": "test",
        "true_0": {
            "predicted_0": int(confusion_matrix_test[0][0]),
            "predicted_1": int(confusion_matrix_test[0][1]),
        },
        "true_1": {
            "predicted_0": int(confusion_matrix_test[1][0]),
            "predicted_1": int(confusion_matrix_test[1][1]),
        },
    }

    confusion_matrix_results = [
        confusion_matrix_train_result,
        confusion_matrix_test_result,
    ]

    with open("files/output/metrics.json", "a") as f:
        for cm in confusion_matrix_results:
            f.write(f"{json.dumps(cm)}\n")


if __name__ == "__main__":
    main()
