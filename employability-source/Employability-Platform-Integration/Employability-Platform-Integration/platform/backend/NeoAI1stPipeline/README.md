# Salary Prediction Pipeline

An end-to-end machine learning pipeline for predicting industry job salaries using Python, Scikit-learn, XGBoost, MLflow, and DVC.

The pipeline covers data preprocessing, feature engineering, salary outlier removal, model training, 5-fold cross-validation, model comparison, visualization, final model generation, and salary prediction.

---

## Dataset

### Raw Dataset

```text
data/raw/Merged_industry_jobs_industry_jobs.csv
```

### Processed Dataset

```text
data/processed/Cleaned_Merged_Industry_Jobs.csv
```

### Outlier-Free Dataset

```text
data/processed/Cleaned_Merged_Industry_Jobs_Zero_Outliers.csv
```

The outlier-free dataset is created using the IQR method. Salary outlier rows are removed completely from the dataset rather than replacing their salary values with zero.

---

# Project Structure

```text
NeoAI1stPipeline/
│
├── data/
│   ├── raw/
│   │   └── Merged_industry_jobs_industry_jobs.csv
│   │
│   └── processed/
│       ├── Cleaned_Merged_Industry_Jobs.csv
│       └── Cleaned_Merged_Industry_Jobs_Zero_Outliers.csv
│
├── models/
│   ├── best_salary_model.pkl
│   ├── best_salary_model_cv.pkl
│   ├── best_salary_model_zero_outliers.pkl
│   ├── best_salary_model_zero_outliers_cv.pkl
│   └── final_salary_model.pkl
│
├── reports/
│   ├── evaluation/
│   │   ├── model_comparison.csv
│   │   ├── model_comparison_zero_outliers.csv
│   │   ├── cross_validation_results.csv
│   │   ├── cross_validation_results_zero_outliers.csv
│   │   └── combined_cross_validation_results.csv
│   │
│   └── visualizations/
│       ├── mean_r2_comparison.png
│       ├── fold_r2_comparison.png
│       └── best_model_comparison.png
│
├── src/
│   └── neoai/
│       ├── data/
│       │   ├── ingestion.py
│       │   ├── preprocessing.py
│       │   └── remove_salary_outliers.py
│       │
│       ├── features/
│       │   └── build_features.py
│       │
│       ├── models/
│       │   ├── train_salary.py
│       │   ├── train_salary_zero_outliers.py
│       │   ├── cross_val_score.py
│       │   ├── cross_val_score_zero_outliers.py
│       │   ├── compare_validation_results.py
│       │   ├── visualize_validation_results.py
│       │   ├── save_final_model.py
│       │   ├── predict_salary.py
│       │   └── transformers.py
│       │
│       └── pipelines/
│           └── preprocess_pipeline.py
│
├── dvc.yaml
├── dvc.lock
├── params.yaml
├── requirements.txt
└── README.md
```

---

# Installation

## 1. Clone the repository

```powershell
git clone <repository-url>
cd NeoAI1stPipeline
```

## 2. Create a virtual environment

```powershell
python -m venv venv
```

## 3. Activate the virtual environment

```powershell
.\venv\Scripts\Activate.ps1
```

## 4. Install dependencies

```powershell
pip install -r requirements.txt
```

---

# Complete Pipeline

The complete pipeline is managed by DVC.

Run:

```powershell
dvc repro
```

Check the pipeline status:

```powershell
dvc status
```

The pipeline automatically executes stages whose dependencies or source files have changed.

---

# Pipeline Workflow

```text
Raw Dataset
     │
     ▼
Preprocessing
     │
     ▼
Feature Engineering
     │
     ├──────────────────────────────┐
     │                              │
     ▼                              ▼
Original Dataset             Outlier Removal
     │                              │
     ▼                              ▼
Model Training              Zero-Outlier Dataset
     │                              │
     ▼                              ▼
5-Fold Cross-Validation      Model Training
     │                              │
     │                              ▼
     │                       5-Fold Cross-Validation
     │                              │
     └──────────────┬───────────────┘
                    ▼
          Validation Comparison
                    │
                    ▼
             Visualizations
                    │
                    ▼
              Final Model
                    │
                    ▼
             Salary Prediction
```

---

# Preprocessing

The preprocessing pipeline cleans and prepares the raw job dataset.

Run preprocessing independently:

```powershell
python -m src.neoai.pipelines.preprocess_pipeline
```

Output:

```text
data/processed/Cleaned_Merged_Industry_Jobs.csv
```

Dataset shape after each stage:

```text
Raw shape:       (260, 16)
After cleaning:  (164, 17)
Final shape:     (164, 27)
```

---

# Feature Engineering

The final model uses 18 engineered features:

```text
 1. Role_Group_Cloud Engineer
 2. Role_Group_DevOps Engineer
 3. Role_Group_Network Engineer
 4. Role_Group_Other
 5. Role_Group_Security/SOC Analyst
 6. Role_Group_Site Reliability Engineer
 7. Experience_Encoded
 8. Company_Freq
 9. PythonRequired_scaled
10. LinuxRequired_scaled
11. NetworkingRequired_scaled
12. AWSRequired_scaled
13. AzureRequired_scaled
14. DockerRequired_scaled
15. KubernetesRequired_scaled
16. TerraformRequired_scaled
17. CyberSecurityRequired_scaled
18. CommunicationRequired_scaled
```

Salary-related target columns are excluded from the model features to prevent salary leakage.

Raw text and identifier fields such as company, role, and job links are not directly used as model features.

---

# Outlier Handling

Salary outliers are detected using the Interquartile Range (IQR) method.

```text
Q1 = 25th percentile
Q3 = 75th percentile

IQR = Q3 - Q1

Lower Bound = Q1 - 1.5 × IQR
Upper Bound = Q3 + 1.5 × IQR
```

Rows outside the calculated boundaries are removed.

The pipeline does NOT replace outlier salary values with zero.

Actual IQR values from the last pipeline run:

```text
Q1:           3.3750 LPA
Q3:           6.3625 LPA
IQR:          2.9875 LPA
Lower Bound: -1.1062 LPA
Upper Bound: 10.8438 LPA

Rows before removal: 164
Rows removed:          9
Rows after removal:  155
```

The resulting dataset is:

```text
data/processed/Cleaned_Merged_Industry_Jobs_Zero_Outliers.csv
```

Run the outlier-removal stage independently:

```powershell
python -m src.neoai.data.remove_salary_outliers
```

---

# Training Flows

The pipeline has two distinct training flows.

## Baseline Training (train/test split)

Scripts: `train_salary.py`, `train_salary_zero_outliers.py`

Quick sanity-check using an 80/20 train/test split. Uses 7 raw numeric features only — no pipeline transformers. Results are logged to MLflow. The saved models are not used for final prediction.

```text
Features (7): Role_Group_Cloud Engineer, Role_Group_DevOps Engineer,
              Role_Group_Network Engineer, Role_Group_Other,
              Role_Group_Security/SOC Analyst,
              Role_Group_Site Reliability Engineer, Experience_Encoded
```

Baseline results — original dataset (test split):

```text
Model                   MAE     RMSE      R²
SVR                   1.3071   1.8628  -0.0597
RandomForestRegressor  1.8506   2.4691  -0.8617
LinearRegression       2.0463   2.4748  -0.8703
XGBRegressor           1.9935   2.6674  -1.1727
```

Baseline results — zero-outlier dataset (test split):

```text
Model              MAE     RMSE      R²
RandomForest     1.5206   1.8857   0.1554
XGBRegressor     1.5281   1.8863   0.1549
LinearRegression  1.5111   1.9001   0.1425
SVR              1.6221   2.1037  -0.0511
```

## Final Model Training (5-fold CV pipeline)

Scripts: `cross_val_score.py`, `cross_val_score_zero_outliers.py`

Uses the full 18-feature sklearn Pipeline with fold-safe transformers. This is the path that produces the final model.

```text
Features (18): Role_Group_* (6 dummies) + Experience_Encoded + Company_Freq
               + 10 skill scaled columns
```

# Models Evaluated

The pipeline evaluates the following regression models:

1. Linear Regression
2. Random Forest Regressor
3. Support Vector Regression (SVR)
4. XGBoost Regressor

---

# Model Configuration

The XGBoost configuration used by the final model is:

```text
objective         = reg:squarederror
n_estimators      = 200
max_depth         = 6
learning_rate     = 0.05
subsample         = 0.8
colsample_bytree  = 0.8
random_state      = 42
n_jobs            = -1
```

---

# 5-Fold Cross-Validation

The project uses 5-fold cross-validation.

For every model:

```text
Fold 1
Fold 2
Fold 3
Fold 4
Fold 5
```

The model is trained on four folds and evaluated on the remaining fold.

This process is repeated five times.

The following metrics are calculated for every fold:

- MAE
- RMSE
- R²

The final validation report contains:

- Mean MAE
- Standard deviation of MAE
- Mean RMSE
- Standard deviation of RMSE
- Mean R²
- Standard deviation of R²
- Individual fold results

---

# Evaluation Reports

All evaluation reports are stored in:

```text
reports/evaluation/
```

### Original Dataset

```text
reports/evaluation/cross_validation_results.csv
```

### Zero-Outlier Dataset

```text
reports/evaluation/cross_validation_results_zero_outliers.csv
```

### Combined Results

```text
reports/evaluation/combined_cross_validation_results.csv
```

Full combined CV results from last pipeline run (sorted by mean R²):

```text
Dataset                Model              Mean MAE  Mean RMSE  Mean R²   R² Std
Zero Outliers Dataset  XGBRegressor       0.8311    1.3641     0.5651    0.0864
Zero Outliers Dataset  RandomForest       0.9432    1.4172     0.5337    0.0672
Zero Outliers Dataset  SVR                0.9744    1.6762     0.3285    0.2160
Original Dataset       SVR                1.5448    2.7257     0.1963    0.6771
Zero Outliers Dataset  LinearRegression   1.4621    1.9168     0.1318    0.2469
Original Dataset       XGBRegressor       1.2229    2.4960    -0.0472    1.5536
Original Dataset       RandomForest       1.4485    2.5870    -0.0715    1.5171
Original Dataset       LinearRegression   2.6288    3.6312    -0.2331    0.7629
```

The combined report contains:

```text
dataset
model

mean_mae
std_mae

mean_rmse
std_rmse

mean_r2
std_r2

fold_1_mae
fold_2_mae
fold_3_mae
fold_4_mae
fold_5_mae

fold_1_rmse
fold_2_rmse
fold_3_rmse
fold_4_rmse
fold_5_rmse

fold_1_r2
fold_2_r2
fold_3_r2
fold_4_r2
fold_5_r2
```

---

# Final Model Selection

Model selection is based on the 5-fold cross-validation results.

The sole selection criterion is:

- Mean R² (highest value wins)

MAE and RMSE are recorded in the evaluation reports for reference but do not influence model selection.

For the zero-outlier dataset, the completed 5-fold validation produced:

```text
Model: XGBRegressor

Mean MAE:  0.8311 LPA
Mean RMSE: 1.3641 LPA
Mean R²:   0.5651
```

Standard deviations:

```text
MAE Std:  0.1085 LPA
RMSE Std: 0.1336 LPA
R² Std:   0.0864
```

Per-fold breakdown:

```text
         Fold 1   Fold 2   Fold 3   Fold 4   Fold 5
MAE      0.8394   0.7657   0.7714   1.0382   0.7411
RMSE     1.3587   1.2643   1.2358   1.6142   1.3476
R²       0.5616   0.6242   0.6940   0.4637   0.4819
```

The selected zero-outlier cross-validation model is:

```text
XGBRegressor
```

---

# Final Model

The final integration model is:

```text
models/final_salary_model.pkl
```

It is generated from:

```text
models/best_salary_model_zero_outliers_cv.pkl
```

The final model is a scikit-learn Pipeline with four steps:

```text
CompanyFrequencyEncoder
        ↓
   SkillScaler
        ↓
FinalFeatureSelector
        ↓
   XGBRegressor
```

- `CompanyFrequencyEncoder` — encodes the Company column as a normalized frequency value learned from the training data
- `SkillScaler` — applies StandardScaler to the 10 raw skill columns and outputs `*_scaled` versions
- `FinalFeatureSelector` — selects and enforces the exact 18-feature order required by the model
- `XGBRegressor` — the trained gradient boosting regressor (`n_features_in_ = 18`)

Final XGBoost configuration:

```text
n_estimators      = 200
max_depth         = 6
learning_rate     = 0.05
subsample         = 0.8
colsample_bytree  = 0.8
objective         = reg:squarederror
random_state      = 42
n_jobs            = -1
```

---

# Generate Final Model

Run:

```powershell
python -m src.neoai.models.save_final_model
```

Output:

```text
models/final_salary_model.pkl
```

---

# Prediction

The prediction module is:

```text
src/neoai/models/predict_salary.py
```

The module exposes a reusable `predict_salary()` function for integration and a `main()` entry point for standalone testing.

## Integration Interface

```python
from src.neoai.models.predict_salary import predict_salary

salary = predict_salary({
    "Company": "Infosys",
    "Role": "DevOps Engineer",
    "Experience": "Fresher",
    "PythonRequired": 7,
    "LinuxRequired": 8,
    "NetworkingRequired": 5,
    "AWSRequired": 7,
    "AzureRequired": 4,
    "DockerRequired": 7,
    "KubernetesRequired": 6,
    "TerraformRequired": 5,
    "CyberSecurityRequired": 3,
    "CommunicationRequired": 8,
})

print(f"{salary:.2f} LPA")
```

`predict_salary()` accepts either a `dict` or a single-row `pd.DataFrame`.

It returns a `float` representing the predicted salary in LPA.

## Required Input Columns

```text
Company
Role
Experience
PythonRequired
LinuxRequired
NetworkingRequired
AWSRequired
AzureRequired
DockerRequired
KubernetesRequired
TerraformRequired
CyberSecurityRequired
CommunicationRequired
```

Skill columns accept integer values on a 1–10 scale (1 = low requirement, 10 = high requirement), matching the training data range.

`Role` and `Experience` are raw text strings. The function applies the same static feature engineering used during training (`add_static_features`) before passing the input to the pipeline.

## Run standalone

```powershell
python -m src.neoai.models.predict_salary
```

Sample output:

```text
Input:
  Company: Infosys
  Role: DevOps Engineer
  Experience: Fresher
  PythonRequired: 7
  LinuxRequired: 8
  NetworkingRequired: 5
  AWSRequired: 7
  AzureRequired: 4
  DockerRequired: 7
  KubernetesRequired: 6
  TerraformRequired: 5
  CyberSecurityRequired: 3
  CommunicationRequired: 8

Predicted salary: 4.97 LPA
```

---

# Individual Pipeline Stages

## Preprocessing

```powershell
python -m src.neoai.pipelines.preprocess_pipeline
```

## Train Original Dataset

```powershell
python -m src.neoai.models.train_salary
```

## Cross-Validate Original Dataset

```powershell
python -m src.neoai.models.cross_val_score
```

## Remove Salary Outliers

```powershell
python -m src.neoai.data.remove_salary_outliers
```

## Train Zero-Outlier Dataset

```powershell
python -m src.neoai.models.train_salary_zero_outliers
```

## Cross-Validate Zero-Outlier Dataset

```powershell
python -m src.neoai.models.cross_val_score_zero_outliers
```

## Compare Validation Results

```powershell
python -m src.neoai.models.compare_validation_results
```

## Generate Visualizations

```powershell
python -m src.neoai.models.visualize_validation_results
```

## Generate Final Model

```powershell
python -m src.neoai.models.save_final_model
```

## Predict Salary

```powershell
python -m src.neoai.models.predict_salary
```

---

# Visualizations

The visualization stage generates:

```text
reports/visualizations/mean_r2_comparison.png
reports/visualizations/fold_r2_comparison.png
reports/visualizations/best_model_comparison.png
```

Run:

```powershell
python -m src.neoai.models.visualize_validation_results
```

---

# DVC Workflow

DVC is used to manage the reproducible machine learning pipeline.

Main DVC files:

```text
dvc.yaml
dvc.lock
```

The pipeline contains the following stages:

```text
preprocess
     ↓
train
     ↓
cross_validate
     ↓
remove_salary_outliers
     ↓
train_zero_outliers
     ↓
cross_validate_zero_outliers
     ↓
compare_validation_results
     ↓
visualize_validation_results
     ↓
save_final_model
```

DVC automatically tracks dependencies and outputs between stages.

---

# Reproduce the Complete Pipeline

Run the entire pipeline:

```powershell
dvc repro
```

Check the pipeline status:

```powershell
dvc status
```

View pipeline differences:

```powershell
dvc diff
```

Push DVC-tracked data and model artifacts to the configured remote:

```powershell
dvc push
```

---

# Git Workflow

After successfully running the pipeline:

```powershell
git status
```

Check changes:

```powershell
git diff
```

Add source and configuration changes:

```powershell
git add src/ dvc.yaml dvc.lock params.yaml requirements.txt README.md
```

Commit:

```powershell
git commit -m "Update salary prediction pipeline"
```

Push:

```powershell
git push origin main
```

---

# Final Outputs

## Dataset

```text
data/processed/Cleaned_Merged_Industry_Jobs.csv
```

## Outlier-Free Dataset

```text
data/processed/Cleaned_Merged_Industry_Jobs_Zero_Outliers.csv
```

## Final Model

```text
models/final_salary_model.pkl
```

## Original Dataset CV Results

```text
reports/evaluation/cross_validation_results.csv
```

## Zero-Outlier CV Results

```text
reports/evaluation/cross_validation_results_zero_outliers.csv
```

## Combined CV Results

```text
reports/evaluation/combined_cross_validation_results.csv
```

## Visualizations

```text
reports/visualizations/
```

---

# Final Model Summary

```text
Final Dataset:
Cleaned_Merged_Industry_Jobs_Zero_Outliers.csv

Final Model:
XGBRegressor

Final Model Location:
models/final_salary_model.pkl

Pipeline Steps:
CompanyFrequencyEncoder → SkillScaler → FinalFeatureSelector → XGBRegressor

Feature Count:
18

5-Fold Mean MAE:
0.8311 LPA

5-Fold Mean RMSE:
1.3641 LPA

5-Fold Mean R²:
0.5651
```

---

# Reproducibility

To reproduce the project from a clean environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
dvc repro
```

After successful execution, the pipeline generates the processed datasets, trained models, validation reports, visualizations, and final salary prediction model.

---

# Technologies Used

- Python
- Pandas
- NumPy
- Scikit-learn 1.5.2
- XGBoost 3.4.1
- SciPy 1.13.1
- MLflow
- DVC
- Joblib
- Matplotlib
- Seaborn

---

# Final Project Result

The final salary prediction pipeline uses the zero-outlier dataset and an XGBoost regression model.

```text
Dataset
    ↓
Preprocessing
    ↓
Feature Engineering
    ↓
IQR Outlier Removal
    ↓
5-Fold Cross-Validation
    ↓
Model Comparison
    ↓
XGBRegressor
    ↓
Final Model
    ↓
Salary Prediction
```

Final model:

```text
models/final_salary_model.pkl
```

Final 5-fold validation metrics:

```text
MAE  = 0.8311 LPA
RMSE = 1.3641 LPA
R²   = 0.5651
```
