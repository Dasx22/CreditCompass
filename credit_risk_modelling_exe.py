#"! D:\Machine Learning\CampusX\Credit_risk_modelling\myenv\Scripts\python.exe"

# -*- coding: utf-8 -*-
"""Credit_Risk_Modelling.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1yxIOMG6UBpAFwbnAYFnB7ktLDQvb-43V

# Importing Necessary Libraries
"""
  
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score
from scipy.stats import chi2_contingency
from statsmodels.stats.outliers_influence import variance_inflation_factor
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, precision_recall_fscore_support
import warnings
import os
import time

print("Program is running...")
print()
start_time = time.time()

"""# Load Dataset"""

a1 = pd.read_excel("D:\Machine Learning\Datasets\Credit Risk Dataset\case_study1.xlsx")
a2 = pd.read_excel("D:\Machine Learning\Datasets\Credit Risk Dataset\case_study2.xlsx")

df1 = a1.copy()   # Performs deep copy by default, for shallow copy: df1 = a1.copy(deep=False)
df2 = a2.copy()

df1.describe()

df1.info()

df1.shape

"""# Remove NULL"""

df1 = df1.loc[df1['Age_Oldest_TL'] != -99999]
df1.shape

columns_to_be_removed = []

for i in df2.columns:   # Returns a list of column names
  if df2.loc[df2[i] == -99999].shape[0] > 10_000:
    columns_to_be_removed.append(i)

columns_to_be_removed

df2.drop(columns_to_be_removed, axis=1, inplace=True)

df2.shape

for i in df2.columns:
  df2 = df2.loc[df2[i] != -99999]

df2.shape

df2.isna().sum()    # Used to get the number of rows with NA values
df1.isna().sum()

"""# Getting the common columns"""

for i in df1.columns:
  if i in df2.columns:
    print(i)

"""# Merging datasets"""

df = pd.merge(df1, df2, how='inner', left_on=['PROSPECTID'], right_on=['PROSPECTID'])   # inner join so that no nulls are present

df.shape

df.head()

df.isna().sum().sum()

"""# Feature Selection

## Categorical Data
"""

categorical_columns = []
for i in df.columns:
  if df[i].dtype == 'object':
    categorical_columns.append(i)

categorical_columns.remove('Approved_Flag')
categorical_columns

df['EDUCATION'].value_counts()

"""### Chi-square test"""

for i in categorical_columns:
  chi2, pval, _, _ = chi2_contingency(pd.crosstab(df[i], df['Approved_Flag']))
  print(i, '-->', pval)   # Since all the categorical features hv pval <= 0.05, we accept all the features

"""## Numerical Data"""

numerical_columns = []
for i in df.columns:
  if df[i].dtype != 'object' and i not in ['Approved_Flag', 'PROSPECTID']:
    numerical_columns.append(i)

len(numerical_columns)

"""### VIF check (sequential) - Multicollinearity check"""

# Using parallel VIF check leads to unwanted removal of features
vif_data = df[numerical_columns]
total_columns = vif_data.shape[1]
column_index = 0
columns_to_be_kept = []

for i in range(0, total_columns):
  vif_value = variance_inflation_factor(vif_data, column_index)
  print(column_index, '-->', vif_value)

  if vif_value <= 6:
    columns_to_be_kept.append(numerical_columns[i])
    column_index += 1

  else:
    vif_data = vif_data.drop(numerical_columns[i], axis=1)

len(columns_to_be_kept)

"""### Anova (oneway) test"""

from scipy.stats import f_oneway

columns_to_be_kept_numerical = []

for i in columns_to_be_kept:
  a = list(df[i])
  b = list(df['Approved_Flag'])

  grp_P1 = [value for value, grp in zip(a, b) if grp == 'P1']
  grp_P2 = [value for value, grp in zip(a, b) if grp == 'P2']
  grp_P3 = [value for value, grp in zip(a, b) if grp == 'P3']
  grp_P4 = [value for value, grp in zip(a, b) if grp == 'P4']

  f_statistic, p_value = f_oneway(grp_P1, grp_P2, grp_P3, grp_P4)

  if p_value <= 0.05:
    columns_to_be_kept_numerical.append(i)

len(columns_to_be_kept_numerical)

"""# Listing all the final features"""

features = columns_to_be_kept_numerical + ['MARITALSTATUS', 'EDUCATION', 'GENDER', 'last_prod_enq2', 'first_prod_enq2']
df = df[features + ['Approved_Flag']]

df.head()

df['MARITALSTATUS'].unique()

df['EDUCATION'].unique()

df['GENDER'].unique()

df['last_prod_enq2'].unique()

df['first_prod_enq2'].unique()

"""# Encoding

## Label Encoding for education
"""

df.loc[df['EDUCATION'] == 'SSC',['EDUCATION']]            = 1
df.loc[df['EDUCATION'] == '12TH',['EDUCATION']]           = 2
df.loc[df['EDUCATION'] == 'GRADUATE',['EDUCATION']]       = 3
df.loc[df['EDUCATION'] == 'UNDER GRADUATE',['EDUCATION']] = 3
df.loc[df['EDUCATION'] == 'POST-GRADUATE',['EDUCATION']]  = 4
df.loc[df['EDUCATION'] == 'OTHERS',['EDUCATION']]         = 1
df.loc[df['EDUCATION'] == 'PROFESSIONAL',['EDUCATION']]   = 3

# Education is ordinal data so we are doing label encoding

df['EDUCATION'].value_counts()

df['EDUCATION'] = df['EDUCATION'].astype(int)
df.info()

"""## One hot encoding for other categorical features"""

df_encoded = pd.get_dummies(df, columns=['MARITALSTATUS', 'EDUCATION', 'GENDER', 'last_prod_enq2', 'first_prod_enq2'])

df_encoded.shape

# """# Model Training

# ## Model 1 : Random Forest Classifier
# """

# y = df_encoded['Approved_Flag']
# x = df_encoded.drop(['Approved_Flag'], axis=1)

# x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

# rf_classifier = RandomForestClassifier(n_estimators=200, random_state=42)

# rf_classifier.fit(x_train, y_train)

# y_pred = rf_classifier.predict(x_test)

# accuracy = accuracy_score(y_test, y_pred)
# print(f'Accuracy: {accuracy}')
# precision, recall, f1_score, _ = precision_recall_fscore_support(y_test, y_pred)

# for i, v in enumerate(['p1', 'p2', 'p3', 'p4']):
#   print(f"Class {v}:")
#   print(f"Precision: {precision[i]}")
#   print(f"Recall: {recall[i]}")
#   print(f"F1 Score: {f1_score[i]}")
#   print()

#   # f1_score of p3 is very less

# """## Model 2: XGBoost"""

import xgboost as xgb
from sklearn.preprocessing import LabelEncoder

# xgb_classifier = xgb.XGBClassifier(objective='multi:softmax', num_class=4)

y = df_encoded['Approved_Flag']
x = df_encoded.drop(['Approved_Flag'], axis=1)

label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

y_encoded

x_train, x_test, y_train, y_test = train_test_split(x, y_encoded, test_size=0.2, random_state=42)

# xgb_classifier.fit(x_train, y_train)

# y_pred = xgb_classifier.predict(x_test)

# accuracy = accuracy_score(y_test, y_pred)
# print(f'Accuracy: {accuracy:.2f}')
# precision, recall, f1_score, _ = precision_recall_fscore_support(y_test, y_pred)

# for i, v in enumerate(['p1', 'p2', 'p3', 'p4']):
#   print(f"Class {v}:")
#   print(f"Precision: {precision[i]}")
#   print(f"Recall: {recall[i]}")
#   print(f"F1 Score: {f1_score[i]}")
#   print()

# """## Model 3: Decision Tree"""

# from sklearn.tree import DecisionTreeClassifier

# y = df_encoded['Approved_Flag']
# x = df_encoded.drop(['Approved_Flag'], axis=1)

# x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

# dt_model = DecisionTreeClassifier(max_depth=20, min_samples_split=10)
# dt_model.fit(x_train, y_train)
# y_pred = dt_model.predict(x_test)

# accuracy = accuracy_score(y_test, y_pred)
# print(f'Accuracy: {accuracy:.2f}')
# precision, recall, f1_score, _ = precision_recall_fscore_support(y_test, y_pred)

# for i, v in enumerate(['p1', 'p2', 'p3', 'p4']):
#   print(f"Class {v}:")
#   print(f"Precision: {precision[i]}")
#   print(f"Recall: {recall[i]}")
#   print(f"F1 Score: {f1_score[i]}")
#   print()

# """Here, out of the 3 models, **XGBoost** gives us the highest accuracy. So, we will **fine-tune** it by HP tuning, scaling(normalization), feature engg, plotting graphs etc. and try to get better results."""

# y.value_counts()

"""# Hyperparameter Tuning for XGBoost"""

# # Defining Hyperparameter grid
# param_grid = {
#     'colsample_bytree': [0.1, 0.3, 0.5, 0.7, 0.9],    # specifies the fraction of features (columns) to be randomly sampled for each tree in the ensemble
#     'learning_rate'   : [0.001, 0.01, 0.1, 1],
#     'max_depth'       : [3, 5, 8, 10],
#     'alpha'           : [1, 10, 100],
#     'n_estimators'    : [10, 50, 100]
# }

# answer_grid = {
#     'combination'     : [],
#     'train_accuracy'  : [],
#     'test_accuracy'   : [],
#     'colsample_bytree': [],
#     'learning_rate'   : [],
#     'max_depth'       : [],
#     'alpha'           : [],
#     'n_estimators'    : []
# }

# index = 0

# # Loop through each combination of hyperparameter
# for colsample_bytree in param_grid['colsample_bytree']:
#   for learning_rate in param_grid['learning_rate']:
#     for max_depth in param_grid['max_depth']:
#       for alpha in param_grid['alpha']:
#         for n_estimators in param_grid['n_estimators']:

#           index = index + 1

#           # Define and train XGBoost model
#           model = xgb.XGBClassifier(
#               objective='multi:softmax',
#               num_class=4,
#               colsample_bytree=colsample_bytree,
#               learning_rate=learning_rate,
#               max_depth=max_depth,
#               alpha=alpha,
#               n_estimators=n_estimators
#           )

#           y = df_encoded['Approved_Flag']
#           x = df_encoded.drop(['Approved_Flag'], axis=1)

#           label_encoder = LabelEncoder()
#           y_encoded = label_encoder.fit_transform(y)

#           x_train, x_test, y_train, y_test = train_test_split(x, y_encoded, test_size=0.2, random_state=42)

#           model.fit(x_train, y_train)

#           # Predict on train and test sets
#           y_pred_train = model.predict(x_train)
#           y_pred_test = model.predict(x_test)

#           # Calculate results
#           train_accuracy = accuracy_score(y_train, y_pred_train)    # used to check underfitting
#           test_accuracy = accuracy_score(y_test, y_pred_test)

#           # Include into list
#           answer_grid['combination'].append(index)
#           answer_grid['train_accuracy'].append(train_accuracy)
#           answer_grid['test_accuracy'].append(test_accuracy)
#           answer_grid['colsample_bytree'].append(colsample_bytree)
#           answer_grid['learning_rate'].append(learning_rate)
#           answer_grid['max_depth'].append(max_depth)
#           answer_grid['alpha'].append(alpha)
#           answer_grid['n_estimators'].append(n_estimators)

#           # Print results
#           print(f"Combination {index}")
#           print(f"colsample_bytree: {colsample_bytree}, learning_rate: {learning_rate}, max_depth: {max_depth}, alpha: {alpha}, n_estimators: {n_estimators}")
#           print(f"train_accuracy: {train_accuracy:.2f}")
#           print(f"test_accuracy: {test_accuracy:.2f}")
#           print('-' * 30)

# selecting the best hyperparameters - (Combination 690)
model = xgb.XGBClassifier(
              objective='multi:softmax',
              num_class=4,
              colsample_bytree=0.9,
              learning_rate=1,
              max_depth=3,
              alpha=10,
              n_estimators=100
          )

"""# Predict for unseen data"""

a3 = pd.read_excel("D:\\Machine Learning\\Datasets\\Credit Risk Dataset\\Unseen_Dataset.xlsx")

cols_in_df = list(df.columns)
cols_in_df.pop(42)

df_unseen = a3[cols_in_df]
df_unseen.head()

df_unseen['MARITALSTATUS'].unique()

df_unseen['EDUCATION'].unique()

df_unseen['GENDER'].unique()

df_unseen['last_prod_enq2'].unique()

df_unseen['first_prod_enq2'].unique()

df_unseen.loc[df_unseen['EDUCATION'] == 'SSC',['EDUCATION']]            = 1
df_unseen.loc[df_unseen['EDUCATION'] == '12TH',['EDUCATION']]           = 2
df_unseen.loc[df_unseen['EDUCATION'] == 'GRADUATE',['EDUCATION']]       = 3
df_unseen.loc[df_unseen['EDUCATION'] == 'UNDER GRADUATE',['EDUCATION']] = 3
df_unseen.loc[df_unseen['EDUCATION'] == 'POST-GRADUATE',['EDUCATION']]  = 4
df_unseen.loc[df_unseen['EDUCATION'] == 'OTHERS',['EDUCATION']]         = 1
df_unseen.loc[df_unseen['EDUCATION'] == 'PROFESSIONAL',['EDUCATION']]   = 3

df_unseen['EDUCATION'].value_counts()

df_unseen['EDUCATION'] = df_unseen['EDUCATION'].astype(int)

df_encoded_unseen = pd.get_dummies(df_unseen, columns=['MARITALSTATUS', 'EDUCATION', 'GENDER', 'last_prod_enq2', 'first_prod_enq2'])

df_encoded_unseen.shape

df_encoded_unseen.info()

k = df_encoded_unseen.describe()

model = xgb.XGBClassifier(
              objective='multi:softmax',
              num_class=4,
              colsample_bytree=0.9,
              learning_rate=1,
              max_depth=3,
              alpha=10,
              n_estimators=100
          )

model.fit(x_train, y_train)

y_pred_unseen = model.predict(df_encoded_unseen)

a3['Target_variable'] = y_pred_unseen

a3.head(10)

a3['Target_variable'].value_counts()

a3.to_excel("D:\Machine Learning\CampusX\Credit_risk_modelling\Final_Prediction.xlsx", index=False)

# print runtime
end_time = time.time()
elapsed_time = end_time - start_time
print("Total runtime of the program: " + str(round(elapsed_time, 2)) + "sec")

input('Press Enter to exit')

