import numpy as np
from collections import Counter


def compute_bias_variance(regressor, dependence_fun, x_generator=np.random.uniform, noise_generator=np.random.uniform,
                          sample_size=300, samples_num=300, objects_num=200, seed=1234):
    """
    В качестве допущения, будем оценивать $E_X\left[\mu(X)\right](x)$ как средний ответ на $x$ из samples_num
     алгоритмов, обученных на своих подвыборках $X$

    Рекомендации:
    * Создайте вектор объектов для оценивания интеграла по $x$, затем вектор правильных ответов на нем и вектор
      зашумленных правильных ответов. $\mathbb{E}[y|x]$ оценивается как сумма правильного ответа на объекте и
      мат. ожидания шума (который оценивается генерацией отдельной шумовой выборки длины objects_num и усреднением
      значений в ней). $\mathbb{E}_X [\mu(X)]$ оценивается как в предыдущей задаче: нужно обучить regressor на
      samples_num выборках длины sample_size и усреднить предсказания на сгенерированных ранее объектах.
    * Проверить правильность реализации можно на примерах, которые разбирались на семинаре и в домашней работе.

    :param regressor: объект sklearn-класса, реализующего регрессионный алгоритм (например, DecisionTreeRegressor,
     LinearRegression, Lasso, RandomForestRegressor ...)
    :param dependence_fun: функция, задающая истинную зависимость в данных. Принимает на вход вектор и возвращает вектор
     такой же длины. Примеры: np.sin, lambda x: x**2
    :param x_generator: функция, генерирующая одномерную выборку объектов и имеющая параметр size (число объектов в
     выборке). По умолчанию np.random.uniform
    :param noise_generator: функция, генерирующая одномерную выборку шумовых компонент (по одной на каждый объект) и
     имеющая параметр size (число объектов в выборке). По умолчанию np.random.uniform
    :param sample_size: число объектов в выборке
    :param samples_num: число выборок, которые нужно сгенерировать, чтобы оценить интеграл по X
    :param objects_num: число объектов, которые нужно сгенерировать, чтобы оценить интеграл по x
    :param seed: seed для функции np.random.seed; Ее вызов обязателен в начале функции и в течении выполнения
     переопределять его нельзя

    :return bias: смещение алгоритма regressor (число)
    :return variance: разброс алгоритма regressor (число)
    """

    # Буду пользоваться формулой V(Z) = E(Z^2) - (E(Z))^2 (для выборочных аналогов тоже верно)
    np.random.seed(seed)

    mean_noise = noise_generator(size=objects_num).mean()
    samples = x_generator(size=(samples_num, sample_size))
    noise = noise_generator(size=(samples_num, sample_size))
    objects = x_generator(size=objects_num)

    return compute_bias_variance_fixed_samples(regressor, dependence_fun, samples, objects, noise, mean_noise)


def compute_bias_variance_fixed_samples(regressor, dependence_fun, samples, objects, noise, mean_noise):
    """
    В качестве допущения, будем оценивать $E_X\left[\mu(X)\right](x)$ как средний ответ на $x$ из samples_num
    алгоритмов, обученных на своих подвыборках $X$
    Рекомендации:
    * $\mathbb{E}[y|x]$ оценивается как сумма правильного ответа на объекте и мат. ожидания шума
      $\mathbb{E}_X [\mu(X)]$ оценивается как в предыдущей задаче: нужно обучить regressor на samples_num выборках длины
       sample_size и усреднить предсказания на сгенерированных ранее объектах.
    :param regressor: объект sklearn-класса, реализующего регрессионный алгоритм (например, DecisionTreeRegressor,
     LinearRegression, Lasso, RandomForestRegressor ...)
    :param dependence_fun: функция, задающая истинную зависимость в данных. Принимает на вход вектор и возвращает вектор
     такой же длины. Примеры: np.sin, lambda x: x**2
    :param samples: samples_num выборк длины sample_size для оценки интеграла по X
    :param objects: objects_num объектов для оценки интеграла по x
    :param noise: шумовая компонента размерности (samples_num, sample_size)
    :param mean_noise: среднее шумовой компоненты
    :return bias: смещение алгоритма regressor (число)
    :return variance: разброс алгоритма regressor (число)
    """

    y_true = dependence_fun(objects)
    y_best = y_true + mean_noise

    samples_num = samples.shape[0]
    y_mean = np.zeros(objects.shape)          # E(\mu(X))
    y_mean_of_sq = np.zeros(objects.shape)    # E((\mu(X))^2)
    for sample, sample_noise in zip(samples, noise):
        y_train = dependence_fun(sample) + sample_noise
        y_pred = regressor.fit(sample[:, None], y_train).predict(objects[:, None])
        y_mean += y_pred / samples_num
        y_mean_of_sq += y_pred ** 2 / samples_num

    bias = np.mean((y_best - y_mean) ** 2)
    variance = np.mean(y_mean_of_sq - y_mean ** 2)

    return bias, variance


def find_best_split(feature_vector, target_vector, min_samples_leaf=None):
    """
    Под критерием Джини здесь подразумевается следующая функция:
    $$Q(R) = -\frac {|R_l|}{|R|}H(R_l) -\frac {|R_r|}{|R|}H(R_r)$$,
    $R$ — множество объектов, $R_l$ и $R_r$ — объекты, попавшие в левое и правое поддерево,
     $H(R) = 1-p_1^2-p_0^2$, $p_1$, $p_0$ — доля объектов класса 1 и 0 соответственно.

    Указания:
    * Пороги, приводящие к попаданию в одно из поддеревьев пустого множества объектов, не рассматриваются.
    * В качестве порогов, нужно брать среднее двух сосдених (при сортировке) значений признака
    * Поведение функции в случае константного признака может быть любым.
    * При одинаковых приростах Джини нужно выбирать минимальный сплит.
    * За наличие в функции циклов балл будет снижен. Векторизуйте! :)

    :param feature_vector: вещественнозначный вектор значений признака
    :param target_vector: вектор классов объектов,  len(feature_vector) == len(target_vector)

    :return thresholds: отсортированный по возрастанию вектор со всеми возможными порогами, по которым объекты можно
     разделить на две различные подвыборки, или поддерева
    :return ginis: вектор со значениями критерия Джини для каждого из порогов в thresholds len(ginis) == len(thresholds)
    :return threshold_best: оптимальный порог (число)
    :return gini_best: оптимальное значение критерия Джини (число)
    """

    if min_samples_leaf is None:
        min_samples_leaf = 1

    # Сортируем два вектора вместе
    argsort = np.argsort(feature_vector)
    feature_vector = feature_vector[argsort]
    target_vector = target_vector[argsort]

    # Если признак константный, возвращаем None
    if feature_vector[0] == feature_vector[-1]:
        return None

    # Посчитаем количество объектов класса 1 и общий объем выборки
    positives_amount = target_vector.sum()
    node_amount = target_vector.shape[0]

    # Посчитаем количество элементов в поддеревьях и долю объектов класса 1
    # Пока что считаем, что можем проводить разбиение между любыми двумя
    # признаками в отсортированном векторе признаков
    left_tree_amount = np.arange(1, target_vector.shape[0])
    right_tree_amount = np.arange(target_vector.shape[0] - 1, 0, -1)
    left_probas = np.cumsum(target_vector)[:-1] / left_tree_amount
    right_probas = (positives_amount - np.cumsum(target_vector)[:-1]) / right_tree_amount

    # Считаем пороги, вычисляем маску, не позволяющую бить по порогу,
    # который равен признаку
    raw_thresholds = (feature_vector[1:] + feature_vector[:-1]) / 2
    unique_mask = (feature_vector[1:] != feature_vector[:-1]) & (left_tree_amount >= min_samples_leaf) \
        & (right_tree_amount >= min_samples_leaf)

    if not np.any(unique_mask):
        return None

    # Обновляем информацию с учетом этой маски
    thresholds = raw_thresholds[unique_mask]
    left_probas = left_probas[unique_mask]
    right_probas = right_probas[unique_mask]
    left_tree_amount = left_tree_amount[unique_mask]
    right_tree_amount = right_tree_amount[unique_mask]

    # Вычисляем H(R) = 2 * p1 * (1 - p1) и индексы Джини
    h_left = 2 * left_probas * (1 - left_probas)
    h_right = 2 * right_probas * (1 - right_probas)
    ginis = -(left_tree_amount * h_left / node_amount + right_tree_amount * h_right / node_amount)
    max_index = np.argmax(ginis)

    return thresholds, ginis, thresholds[max_index], ginis[max_index]


class DecisionTree:
    def __init__(self, feature_types, max_depth=None, min_samples_split=None, min_samples_leaf=None):
        if np.any(list(map(lambda x: x != "real" and x != "categorical", feature_types))):
            raise ValueError("There is unknown feature type")

        self._tree = {}
        self._feature_types = feature_types
        self._max_depth = max_depth
        self._min_samples_split = min_samples_split
        self._min_samples_leaf = min_samples_leaf
        self._depth = None

    def _fit_node(self, sub_X, sub_y, node, depth):
        if self._depth is None or self._depth < depth:
            self._depth = depth

        if np.all(sub_y == sub_y[0]):
            node["type"] = "terminal"
            node["class"] = sub_y[0]
            return

        if (self._max_depth is not None and depth == self._max_depth) or \
                (self._min_samples_split is not None and sub_y.shape[0] < self._min_samples_split):
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

            # если все признаки равны, выходим
            if np.all(feature_vector[0] == feature_vector):
                continue

            best_split_found = find_best_split(feature_vector, sub_y, self._min_samples_leaf)
            if best_split_found is None:
                continue

            _, _, threshold, gini = best_split_found
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

        node["type"] = "nonterminal"

        node["feature_split"] = feature_best
        if self._feature_types[feature_best] == "real":
            node["threshold"] = threshold_best
        elif self._feature_types[feature_best] == "categorical":
            node["categories_split"] = threshold_best
        else:
            raise ValueError
        node["left_child"], node["right_child"] = {}, {}
        self._fit_node(sub_X[split], sub_y[split], node["left_child"], depth + 1)
        self._fit_node(sub_X[np.logical_not(split)], sub_y[np.logical_not(split)], node["right_child"], depth + 1)

    def _predict_node(self, x, node):
        if node["type"] == "terminal":
            return node["class"]

        feature_split = node["feature_split"]
        if (self._feature_types[feature_split] == "real" and x[feature_split] <= node["threshold"]) or \
                (self._feature_types[feature_split] == "categorical" and x[feature_split] in node["categories_split"]):
            return self._predict_node(x, node["left_child"])
        else:
            return self._predict_node(x, node["right_child"])

    def fit(self, X, y):
        self._fit_node(X, y, self._tree, 1)

    def predict(self, X):
        predicted = []
        for x in X:
            predicted.append(self._predict_node(x, self._tree))
        return np.array(predicted)

    def depth(self):
        return self._depth
