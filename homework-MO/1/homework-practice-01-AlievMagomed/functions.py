import numpy
from math import sqrt


def prod_non_zero_diag(x):
    rows = len(x)
    columns = len(x[0])

    low = rows if rows <= columns else columns

    answer = 1

    for i in range(0, low):
        if x[i][i] != 0:
            answer *= x[i][i]

    return answer


def are_multisets_equal(x, y):

    x_dict = {}
    y_dict = {}

    for i in x:
        x_dict[i] = x_dict.get(i, 0) + 1

    for i in y:
        y_dict[i] = y_dict.get(i, 0) + 1

    if x_dict == y_dict:
        return True
    return False


def max_after_zero(x):
    max_ = 0

    for idx, elem in enumerate(x):
        try:
            if elem == 0 and x[idx + 1] >= max_:
                max_ = x[idx + 1]
        except IndexError:
            # we reached array end
            pass

    return max_


def run_length_encoding(x):
    prev = None
    keys = []
    count = []
    for i in x:
        if i != prev:
            keys.append(i)
            count.append(1)
            prev = i
        else:
            count[len(count) - 1] += 1

    return (keys, count)


def convert_image(img, coefs):
    res_array = [[0 for j in img[0]] for i in img]

    for idx, x in enumerate(img):
        for idy, y in enumerate(x):
            for idz, z in enumerate(y):
                res_array[idx][idy] += img[idx][idy][idz] * coefs[idz]

    return res_array


def pairwise_distance(x, y):
    res_array = []

    for x_elem in x:
        row = []
        for y_elem in y:
            dist = 0
            for i in range(len(x_elem)):
                dist += (x_elem[i] - y_elem[i])**2
            row.append(sqrt(dist))
        res_array.append(row)

    return res_array
