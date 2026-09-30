import mlflow
import dagshub


def main():
    dagshub.init(
        repo_owner="siddheshRajendraNimbalkar",
        repo_name="NeoAI1stPipeline",
        mlflow=True,
    )

    mlflow.set_experiment("NeoAI-Experiments")

    with mlflow.start_run():
        mlflow.log_param("test_parameter", 100)
        mlflow.log_metric("test_accuracy", 0.95)

        print("MLflow run completed successfully!")


if __name__ == "__main__":
    main()