import numpy as np
from scipy.spatial.distance import euclidean
from scipy.special import expit
from sklearn.base import BaseEstimator
from numpy import logaddexp
import time

class LogReg(BaseEstimator):
    def __init__(self, lambda_1=0.0, lambda_2=1.0, gd_type='full',
                 tolerance=1e-6, max_iter=1000, w0=None, alpha=0.001, history=False):
        """
        lambda_1: L1 regularization param
        lambda_2: L2 regularization param
        gd_type: 'full' or 'stochastic'
        tolerance: for stopping gradient descent
        max_iter: maximum number of steps in gradient descent
        w0: np.array of shape (d) - init weights
        alpha: learning rate
        """
        self.lambda_1 = lambda_1
        self.lambda_2 = lambda_2
        self.gd_type = gd_type
        self.tolerance = tolerance
        self.max_iter = max_iter
        self.w0 = w0
        self.alpha = alpha
        self.w = None
        self.loss_history = []
        self.iteration_time = []
        self.history = history

    def fit(self, X, y):
        # нормируем матрицу объектов признаков
        X = np.array(X)
        y = np.array(y)

        # инициализируем массив весов
        if self.w0 is not None:
            self.w = self.w0
        else:
            self.w = np.zeros(X[0].size)

        for i in range(self.max_iter):
            from_ = time.time()
            w_new = self.w - self.alpha * self.calc_gradient(X, y)
            
            if self.history:
                time_wasted = time.time() - from_
                self.loss_history.append(self.calc_loss(X, y))
                self.iteration_time.append(time_wasted)
            
            if euclidean(w_new, self.w) < self.tolerance:
                self.w = w_new
                break
                
            self.w = w_new


        return self

    def predict_proba(self, X):
        """
        X: np.array of shape (l, d)
        ---
        output: np.array of shape (l, 2) where
        first column has probabilities of -1
        second column has probabilities of +1
        """
        if self.w is None:
            raise Exception('Not trained yet')

        X = np.array(X)

        predictions = np.empty((2, len(X)))
        t = expit(np.dot(X, self.w))
        predictions[0] = np.ones(len(X)) - t
        predictions[1] = t
        predictions = predictions.T

        return predictions

    def predict(self, X):
        """
        X: np.array of shape (l, d)
        ---
        output: np.array of shape (l, 2) where
        first column has probabilities of -1
        second column has probabilities of +1
        """

        X = np.array(X)
        if self.w is None:
            raise Exception('Not trained yet')

        predictions = np.zeros(len(X), dtype=int)
        for i in range(len(X)):
            t = expit(np.dot(self.w, X[i]))

            if t > 0.5:
                predictions[i] = 1
            else:
                predictions[i] = 0

        return predictions

    def calc_gradient(self, X, y):
        """
        X: np.array of shape (l, d) (l can be equal to 1 if stochastic)
        y: np.array of shape (l)
        ---
        output: np.array of shape (d)
        """
        grad = np.zeros(len(X[0]))
        
        if self.gd_type == 'full':
            grad = np.dot(y * expit(-y * np.dot(X, self.w)), -X)
            grad /= len(X)
        else:
            rand_idx = np.random.randint(0, len(X))
            tmp = y[rand_idx] * X[rand_idx]
            tmp /= -(1 + np.exp(y[rand_idx] * np.dot(self.w, X[rand_idx])))
            grad += tmp
            
            
        grad += self.lambda_2 * self.w

        return grad

    def calc_loss(self, X, y):
        """
        X: np.array of shape (l, d)
        y: np.array of shape (l)
        ---
        output: float
        """
        total_loss = (np.log(1 / expit(y * (np.dot(X, self.w))))).sum() / len(X)

        total_loss += (self.lambda_2 / 2) * np.linalg.norm(self.w)**2

        return total_loss

