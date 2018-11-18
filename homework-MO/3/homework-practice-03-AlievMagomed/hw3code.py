import numpy as np
from collections import Counter
from sklearn.base import BaseEstimator, TransformerMixin
from multiprocessing.pool import Pool


def compute_bias_variance(regressor, dependence_fun, x_generator=np.random.uniform, noise_generator=np.random.uniform,
                          sample_size=300, samples_num=300, objects_num=200, seed=1234):
    np.random.seed(seed)

    X_train = []
    noise = []

    # сгенерируем samples_num обучающих выборок и сохраним их
    for i in range(samples_num):
        X = x_generator(size=(sample_size))
        n = noise_generator(size=(sample_size))
        noise.append(n)
        X_train.append(X)

    # подготовим матрицу предсказаний
    # каждая строка - вектор ответов для одного объекта
    y_predict = np.zeros((objects_num, samples_num))

    # выборка для оценки
    X_test = x_generator(size=(objects_num))

    # найдем мат. ожидание шума
    noise_mean = np.mean(noise_generator(size=objects_num))

    return compute_bias_variance_fixed_samples(regressor, dependence_fun, X_train, X_test, noise, noise_mean)


def compute_bias_variance_fixed_samples(regressor, dependence_fun, samples, objects, noise, mean_noise):
    # определим размеры
    samples_num = len(samples)
    sample_size = len(samples[0])
    # подготовим матрицы для хранения предсказаний и разбросов
    y_predict = np.zeros((len(objects), samples_num))

    for i in range(samples_num):
        # создаем целевой вектор
        y = dependence_fun(samples[i]) + noise[i]
        regressor.fit(samples[i][:, np.newaxis], y)
        # помещаем предсказаний в матрицу - каждый столб это предсказание для очередной выборки
        # строка - предсказания для объекта на каждой выборке
        y_predict[:, i] = regressor.predict(objects[:, np.newaxis])

    # посчитаем средний ответ - среднее предсказание для каждого объекта по всем выборкам
    average_predict = np.mean(y_predict, axis=1)

    # считаем разброс - разность каждого предсказания и среднего ответа в квадрате
    variances = ((y_predict.T - average_predict)**2).T

    # вычисляем смещение - (идеальный ответ + мат. ожидание шума - средний ответ)^2
    y_bias = (dependence_fun(objects) + mean_noise - average_predict) ** 2
    # теперь возьмем среднее по всем строкам и получим средний разброс для каждого объекта
    y_var = np.mean(variances, axis=1)

    # возвращаем средние смещение и разброс по всем объектам
    return [np.mean(y_bias), np.mean(y_var)]


def find_best_split(feature_vector, target_vector):
    feature_vect = np.array(feature_vector)
    targets = np.array(target_vector)

    # создаем маску для сортировки и сортируем с ее помощью оба вектора
    sort_mask = np.argsort(feature_vect)
    feature_vect = feature_vect[sort_mask]
    targets = targets[sort_mask]

    # считаем кол-во объектов первоо класса и общее кол-во объектов
    class_one_all = np.sum(targets)
    objects_amount = len(targets)

    # создаем вектора разбиений на 1ое и 2ое поддерево
    objects_one = np.arange(1, objects_amount)
    objects_two = np.absolute(objects_one - objects_amount)

    # для каждого разбиения посчитаем долю объектов 1го класса
    left_prob = np.cumsum(targets)[:-1] / objects_one
    right_prob = (class_one_all - np.cumsum(targets)[:-1]) / objects_two

    # создаем вектор порогов
    thresholds = (feature_vect[1:] + feature_vect[:-1]) / 2

    # проверка на пороги, совпадающие с признаками
    good_thresholds = np.where(thresholds != feature_vect[1:])

    left_prob = left_prob[good_thresholds]
    right_prob = right_prob[good_thresholds]
    thresholds = thresholds[good_thresholds]
    objects_one = objects_one[good_thresholds]
    objects_two = objects_two[good_thresholds]

    h_left = 2 * left_prob * (1 - left_prob)
    h_right = 2 * right_prob * (1 - right_prob)

    jinis = objects_one * h_left / objects_amount + objects_two * h_right / objects_amount

    if len(jinis) == 0:
        return [], [], None, None

    ind = np.lexsort((thresholds, jinis))

    return thresholds, -1 * jinis, thresholds[ind[0]], -1 * jinis[ind[0]]


class DecisionTree(BaseEstimator):
    def __init__(self, feature_types, max_depth=None, min_samples_split=None, min_samples_leaf=None):
        if np.any(list(map(lambda x: x != "real" and x != "categorical", feature_types))):
            raise ValueError("There is unknown feature type")

        self._tree = {}
        self._feature_types = feature_types
        self._max_depth = max_depth
        self._min_samples_split = min_samples_split
        self._min_samples_leaf = min_samples_leaf

    # немного переписанная функция для корректной работой с cross_val_score
    def get_params(self, deep=None):
        params = {}
        for key, item in self.__dict__.items():
            params[key[1:]] = item
        params.pop('tree')
        return params

    def _fit_node(self, sub_X, sub_y, node, depth):
        if np.all(sub_y == sub_y[0]):
            node["type"] = "terminal"
            node["class"] = sub_y[0]
            return

        if self._min_samples_split is not None:
            if len(sub_X) < self._min_samples_split:
                node["type"] = "terminal"
                node["class"] = Counter(sub_y).most_common(1)[0][0]
                return

        if self._max_depth is not None:
            if depth == self._max_depth:
                node["type"] = "terminal"
                node["class"] = Counter(sub_y).most_common(1)[0][0]
                return

        feature_best, threshold_best, gini_best, split = None, None, None, None
        for feature in range(sub_X.shape[1]):
            feature_type = self._feature_types[feature]
            categories_map = {}

            if feature_type == "real":
                feature_vector = sub_X[:, feature]
            elif feature_type == "categorical":
                counts = Counter(sub_X[:, feature])
                clicks = Counter(sub_X[sub_y == 1, feature])
                ratio = {}
                for key, current_count in counts.items():
                    if key in clicks:
                        current_click = clicks[key]
                    else:
                        current_click = 0
                    ratio[key] = current_click / current_count
                sorted_categories = list(map(lambda x: x[0], sorted(ratio.items(), key=lambda x: x[1])))
                categories_map = dict(zip(sorted_categories, list(range(len(sorted_categories)))))
                feature_vector = np.array(list(map(lambda x: categories_map[x], sub_X[:, feature])))
            else:
                raise ValueError

            _, _, threshold, gini = find_best_split(feature_vector, sub_y)

            if gini is None:
                continue

            if gini_best is None or gini > gini_best:
                feature_best = feature
                gini_best = gini
                split = feature_vector < threshold

                if feature_type == "real":
                    threshold_best = threshold
                elif feature_type == "categorical":
                    threshold_best = list(map(lambda x: x[0],
                                              filter(lambda x: x[1] < threshold, categories_map.items())))
                else:
                    raise ValueError

        if feature_best is None:
            node["type"] = "terminal"
            node["class"] = Counter(sub_y).most_common(1)[0][0]
            return

        if self._min_samples_leaf is not None:
            if len(sub_X[split]) < self._min_samples_leaf or len(sub_X[np.logical_not(split)]) < self._min_samples_leaf:
                node["type"] = "terminal"
                node["class"] = Counter(sub_y).most_common(1)[0][0]
                return

        node["type"] = "nonterminal"

        node["feature_split"] = feature_best
        if self._feature_types[feature_best] == "real":
            node["threshold"] = threshold_best
        elif self._feature_types[feature_best] == "categorical":
            node["categories_split"] = threshold_best
        else:
            raise ValueError

        node["left_child"], node["right_child"] = {}, {}
        self._fit_node(sub_X[split], sub_y[split], node["left_child"], depth+1)
        self._fit_node(sub_X[np.logical_not(split)], sub_y[np.logical_not(split)], node["right_child"], depth+1)

    def _predict_node(self, x, node):
        while node["type"] != 'terminal':
            if "threshold" in node:
                if x[node["feature_split"]] < node["threshold"]:
                    node = node["left_child"]
                else:
                    node = node["right_child"]
            else:
                if x[node["feature_split"]] in node["categories_split"]:
                    node = node["left_child"]
                else:
                    node = node["right_child"]
        return node["class"]

    def fit(self, X, y):
        X = np.array(X)
        y = np.array(y)

        self._fit_node(X, y, self._tree, 1)

    def predict(self, X):
        predicted = []
        for x in X:
            predicted.append(self._predict_node(x, self._tree))
        return np.array(predicted)
