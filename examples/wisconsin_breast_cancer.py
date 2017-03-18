from __future__ import unicode_literals, division

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from active_learning.active_learning import ActiveLearner
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import SGDClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import load_breast_cancer
from sklearn.svm import SVC
import numpy as np
import tempfile
import sys
import os


if __name__ == '__main__':
    all_random, all_uncertainty = [], []
    AL = ActiveLearner(strategy='max_margin')
    clf = LogisticRegression()
    data = load_breast_cancer()

    for _ in range(100):
        X_train, X_test, y_train, y_test = train_test_split(
            data.data, data.target, test_size=0.5)
        
        X_labeled, X_unlabeled, y_labeled, y_oracle = train_test_split(
            X_train, y_train, test_size=0.8)
        
        random, uncertainty = [], []

        for num_queries in (5, 10, 15, 20, 25, 30):
            random_queries = np.random.choice(X_unlabeled.shape[0], num_queries, replace=False)
            X_augmented = np.concatenate((X_labeled, X_unlabeled[random_queries, :]))
            y_augmented = np.concatenate((y_labeled, y_oracle[random_queries]))
            clf.fit(X_augmented, y_augmented)
            random.append(np.sum(clf.predict(X_test) == y_test) / np.shape(X_test)[0])
        
            clf.fit(X_labeled, y_labeled)
            idx = AL.rank(clf, X_unlabeled, num_queries)
            X_augmented = np.concatenate((X_labeled, X_unlabeled[idx, :]))
            y_augmented = np.concatenate((y_labeled, y_oracle[idx]))
            clf.fit(X_augmented, y_augmented)
            uncertainty.append(np.sum(clf.predict(X_test) == y_test) / np.shape(X_test)[0])

        all_uncertainty.append(uncertainty)
        all_random.append(random)

    print np.mean(np.array(all_random), axis=0)
    print np.mean(np.array(all_uncertainty), axis=0)