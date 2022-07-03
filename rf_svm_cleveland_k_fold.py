# -*- coding: utf-8 -*-
"""RF_SVM_cleveland_k_fold

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1PHd01kKBQBnlRKJeHJzJAqujGIgA8gb-
"""

!wget https://developer.nvidia.com/compute/cuda/9.0/Prod/local_installers/cuda-repo-ubuntu1704-9-0-local_9.0.176-1_amd64-deb
!dpkg -i cuda-repo-ubuntu1704-9-0-local_9.0.176-1_amd64-deb
!ls /var/cuda-repo-9-0-local | grep .pub
!apt-key add /var/cuda-repo-9-0-local/7fa2af80.pub
!apt-get update
!sudo apt-get install cuda-9.0
!pip install thundersvm
from thundersvm import SVC
!pip install skfeature-chappers

import pandas as pd
import numpy as np
import sys 
import random
from sklearn import model_selection, pipeline, preprocessing
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.model_selection import train_test_split, cross_val_score, KFold,StratifiedKFold,GridSearchCV
from sklearn.feature_selection import RFE, SelectFromModel, SelectKBest, chi2
from sklearn.preprocessing import StandardScaler, MinMaxScaler

dataset = pd.read_csv('https://raw.githubusercontent.com/Prasenjit123/Fortified-Chain2.0/main/cleveland.csv')
dataset_input = dataset.iloc[:, :-1]
dataset_label = dataset.iloc[:, -1]

number_of_folds = 10

def k_fold_cross_validation(dataset_input,dataset_label,k):
   train_data = []
   test_data = []
   train_label = []
   test_label = []
   for i in range(len(dataset_input)):
       if i%number_of_folds == k:
         test_data.append(dataset_input.iloc[i,:]) 
         test_label.append(dataset_label.iloc[i]) 
       else:
         train_data.append(dataset_input.iloc[i,:])
         train_label.append(dataset_label.iloc[i])
   train_data  = np.array(train_data)
   train_label = np.array(train_label)
   test_data   = np.array(test_data)
   test_label  = np.array(test_label)
   return (train_data, train_label, test_data, test_label)

# NB Classifier
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score, confusion_matrix
avg_acc = 0
for k in range(number_of_folds):
  train_data, train_label, test_data, test_label = k_fold_cross_validation(dataset_input, dataset_label, k)
  train_data_normalized = StandardScaler().fit_transform(train_data)
  train_means = np.mean(train_data, axis=0)
  train_SDs = np.std(train_data, axis=0)
  test_data = (test_data - train_means)/train_SDs

  clf_NB = GaussianNB()
  clf_NB.fit(train_data_normalized, train_label)
  scores = clf_NB.predict(test_data)
  avg_acc = avg_acc + round(accuracy_score(test_label, scores)*100,2)   

print(f'acc: {round(avg_acc/number_of_folds,2)}')

# RF Classifier
from sklearn.ensemble import RandomForestClassifier
avg_acc = 0
for k in range(number_of_folds):
  train_data, train_label, test_data, test_label = k_fold_cross_validation(dataset_input, dataset_label, k)
  train_data_normalized = StandardScaler().fit_transform(train_data)
  train_means = np.mean(train_data, axis=0)
  train_SDs = np.std(train_data, axis=0)
  test_data = (test_data - train_means)/train_SDs

  clf_RF = RF_clf = RandomForestClassifier(n_estimators = 100) 
  clf_RF.fit(train_data_normalized, train_label)
  scores = clf_NB.predict(test_data)
  avg_acc = avg_acc + round(accuracy_score(test_label, scores)*100,2)   

print(f'acc: {round(avg_acc/number_of_folds,2)}')

# SVM Classifier
avg_acc = 0
for k in range(number_of_folds):
  train_data, train_label, test_data, test_label = k_fold_cross_validation(dataset_input, dataset_label, k)
  train_data_normalized = StandardScaler().fit_transform(train_data)
  train_means = np.mean(train_data, axis=0)
  train_SDs = np.std(train_data, axis=0)
  test_data = (test_data - train_means)/train_SDs
  all_scores = []
  for C in [0.01, 0.1, 1, 10, 100, 1000]:
    for gamma in [0.0001, 0.001, 0.01, 0.1,1]: 
      clf_SVM = SVC(kernel='rbf', C=C, gamma=gamma, random_state=0, verbose=True)
      clf_SVM.fit(train_data_normalized, train_label)
      scores = round((clf_SVM.score(test_data,test_label))*100,2)
      all_scores.append(scores)  
  avg_acc = avg_acc + np.max(all_scores)    

print(f'acc: {round(avg_acc/number_of_folds,2)}')

# PCA as feature selector
# PCA+SVM Classifier
from sklearn.decomposition import PCA
avg_accuracies = [] 
for n in [2,3,4,5,6,7,8,9,10,11,12,13]:
  avg_acc = 0
  for k in range(number_of_folds):
    train_data, train_label, test_data, test_label = k_fold_cross_validation(dataset_input, dataset_label, k)
    train_data_normalized = StandardScaler().fit_transform(train_data)
    train_means = np.mean(train_data, axis=0)
    train_SDs = np.std(train_data, axis=0)
    test_data = (test_data - train_means)/train_SDs
    
    pca = PCA(n_components=n)
    train_data_transformed = pca.fit_transform(train_data_normalized)
    test_data = pca.fit_transform(test_data)
    all_scores = []
    for C in [0.01, 0.1, 1, 10, 100, 1000]:
      for gamma in [0.0001, 0.001, 0.01, 0.1,1]: 
        clf_SVM = SVC(kernel='rbf', C=C, gamma=gamma, random_state=0, verbose=True)
        clf_SVM.fit(train_data_transformed, train_label)
        scores = round((clf_SVM.score(test_data,test_label))*100,2)
        all_scores.append(scores)  
    #print(np.max(all_scores))
    avg_acc = avg_acc + np.max(all_scores)    

  print(f'feature = {n}, acc: {avg_acc/number_of_folds}') 
  avg_accuracies.append(avg_acc/number_of_folds)   

print("\n Best Accuracy: ", round(np.max(avg_accuracies),2))

# Random Forest as feature selector
# RF+SVM Classifier
from sklearn.ensemble import RandomForestClassifier
clf_RF = RandomForestClassifier(n_estimators=100, n_jobs=-1, random_state=1, criterion = "entropy")
avg_accuracies = [] 
for n in [2,3,4,5,6,7,8,9,10,11,12,13]:
  rfe = RFE(estimator = clf_RF, n_features_to_select = n, verbose =  3) 
  avg_acc = 0
  for k in range(number_of_folds):
    train_data, train_label, test_data, test_label = k_fold_cross_validation(dataset_input, dataset_label, k)
    train_data_normalized = StandardScaler().fit_transform(train_data)
    train_means = np.mean(train_data, axis=0)
    train_SDs = np.std(train_data, axis=0)
    test_data = (test_data - train_means)/train_SDs
    rfe.fit(train_data_normalized, train_label)
    train_data_transformed = rfe.transform(train_data_normalized)
    test_data = rfe.transform(test_data)

    all_scores = []
    for C in [0.01, 0.1, 1, 10, 100, 1000]:
      for gamma in [0.0001, 0.001, 0.01, 0.1,1]: 
        clf_SVM = SVC(kernel='rbf', C=C, gamma=gamma, random_state=0, verbose=True)
        clf_SVM.fit(train_data_transformed, train_label)
        scores = round((clf_SVM.score(test_data,test_label))*100,2)
        all_scores.append(scores)  
    #print(np.max(all_scores))
    avg_acc = avg_acc + np.max(all_scores)    

  print(f'feature = {n}, acc: {avg_acc/number_of_folds}') 
  avg_accuracies.append(avg_acc/number_of_folds)   

print("\n Best Accuracy: ", round(np.max(avg_accuracies),2))

# xgboost as feature selector
# xgboost+SVM Classifier
from xgboost import XGBClassifier
clf_XGB = XGBClassifier(base_score=0.5, booster='gbtree', colsample_bylevel=1, colsample_bynode=1, colsample_bytree=1)
avg_accuracies = []
for n in [2,3,4,5,6,7,8,9,10,11,12,13]:
  rfe = RFE(estimator = clf_XGB, n_features_to_select = n, verbose =  3) 
  avg_acc = 0
  for k in range(number_of_folds):
     train_data, train_label, test_data, test_label = k_fold_cross_validation(dataset_input, dataset_label, k)
     train_data_normalized = StandardScaler().fit_transform(train_data)
     train_means = np.mean(train_data, axis=0)
     train_SDs = np.std(train_data, axis=0)
     test_data = (test_data - train_means)/train_SDs
     rfe.fit(train_data_normalized, train_label)
     train_data_transformed = rfe.transform(train_data_normalized)
     test_data = rfe.transform(test_data)

     all_scores = []
     for C in [0.01, 0.1, 1, 10, 100, 1000]:
       for gamma in [0.0001, 0.001, 0.01, 0.1,1]: 
         clf_SVM = SVC(kernel='rbf', C=C, gamma=gamma, random_state=0, verbose=True)
         clf_SVM.fit(train_data_transformed, train_label)
         scores = round((clf_SVM.score(test_data,test_label))*100,2)
         all_scores.append(scores)  
     #print(np.max(all_scores))
     avg_acc = avg_acc + np.max(all_scores)    

  print(f'feature = {n}, acc: {avg_acc/number_of_folds}')
  avg_accuracies.append(avg_acc/number_of_folds)   

print("\n Best Accuracy: ", np.max(avg_accuracies))

# Chi_squre as feature selector
# Chi_squre+SVM classifier
avg_accuracies = []
for n in [2,3,4,5,6,7,8,9,10,11,12,13]:
  ch = SelectKBest(score_func=chi2, k=n)
  avg_acc = 0
  for k in range(number_of_folds):
    train_data, train_label, test_data, test_label = k_fold_cross_validation(dataset_input, dataset_label,k)
    train_data_normalized = StandardScaler().fit_transform(train_data)
    train_data_normalized = MinMaxScaler().fit_transform(train_data_normalized)
    train_means = np.mean(train_data, axis=0)
    train_SDs = np.std(train_data, axis=0)
    test_data = (test_data - train_means)/train_SDs
    ch.fit(train_data_normalized, train_label)
    train_data_transformed = ch.fit_transform(train_data_normalized, train_label)    
     
    all_scores = []
    for C in [0.01, 0.1, 1, 10, 100, 1000]:
      for gamma in [0.0001, 0.001, 0.01, 0.1,1]: 
        clf_SVM = SVC(kernel='rbf', C=C, gamma=gamma, random_state=0, verbose=True)
        clf_SVM.fit(train_data_transformed, train_label)
        scores = round((clf_SVM.score(test_data,test_label))*100,2)   
        all_scores.append(scores)  
    #print(np.max(all_scores))
    avg_acc = avg_acc + np.max(all_scores)    

  print(f'feature = {n}, acc: {avg_acc/number_of_folds}')  
  avg_accuracies.append(avg_acc/number_of_folds)   

print("\n Best Accuracy: ", round(np.max(avg_accuracies),2))

# Lasso as feature selector
from sklearn.linear_model import Lasso
from sklearn.pipeline import Pipeline
pipeline = Pipeline([
                     ('scaler',StandardScaler()),
                     ('model',Lasso())
])
search = GridSearchCV(pipeline, {'model__alpha':np.arange(0.1,10,0.1)}, cv = 5, scoring="neg_mean_squared_error",verbose=3)

avg_acc = 0
for k in range(number_of_folds):
  train_data, train_label, test_data, test_label = k_fold_cross_validation(dataset_input, dataset_label,k)
  train_data_normalized = StandardScaler().fit_transform(train_data)
  train_means = np.mean(train_data, axis=0)
  train_SDs = np.std(train_data, axis=0)
  test_data = (test_data - train_means)/train_SDs
  search.fit(train_data_normalized, train_label)
  coefficients = search.best_estimator_.named_steps['model'].coef_
  importance = np.abs(coefficients)
  features = np.arange(13)
  selected_features = np.array(features)[importance != 0]
  train_data_transformed = train_data_normalized[:,selected_features]
  test_data = test_data[:,selected_features]

  all_scores = []
  for C in [0.01, 0.1, 1, 10, 100, 1000]:
    for gamma in [0.0001, 0.001, 0.01, 0.1,1]: 
      clf_SVM = SVC(kernel='rbf', C=C, gamma=gamma, random_state=0, verbose=True)
      clf_SVM.fit(train_data_transformed, train_label)
      scores = round((clf_SVM.score(test_data,test_label))*100,2)  
      all_scores.append(scores)  
  #print(np.max(all_scores))
  avg_acc = avg_acc + np.max(all_scores)    

print(f'feature = {selected_features}, acc: {round(avg_acc/number_of_folds,2)}')