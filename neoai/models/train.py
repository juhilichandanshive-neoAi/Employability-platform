import json
import os

import mlflow
import mlflow.sklearn
import yaml

from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split


def load_params():
    with open("params.yaml", "r") as file:
        return yaml.safe_load(file)


def main():
    params = load_params()

    data = load_iris()

    X_train, X_test, y_train, y_test = train_test_split(
        data.data,
        data.target,
        test_size=params["data"]["test_size"],
        random_state=params["data"]["random_state"],
    )

    model_params = params["model"]

    model = RandomForestClassifier(
        n_estimators=model_params["n_estimators"],
        max_depth=model_params["max_depth"],
        random_state=model_params["random_state"],
    )

    mlflow.set_experiment("NeoAI-Experiments")

    with mlflow.start_run():
        model.fit(X_train, y_train)

        predictions = model.predict(X_test)
        accuracy = accuracy_score(y_test, predictions)

        mlflow.log_params(model_params)
        mlflow.log_metric("accuracy", accuracy)

        os.makedirs("models", exist_ok=True)
        os.makedirs("reports/evaluation", exist_ok=True)

        mlflow.sklearn.log_model(
            model,
            name="random_forest_model",
        )

        with open("models/model.pkl", "wb") as file:
            import pickle
            pickle.dump(model, file)

        with open("reports/evaluation/metrics.json", "w") as file:
            json.dump({"accuracy": accuracy}, file, indent=4)

        print(f"Accuracy: {accuracy:.4f}")


if __name__ == "__main__":
    main()