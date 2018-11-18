import numpy as np


def prod_non_zero_diag(x):
    diag_elems = np.diagonal(x)
    return np.prod(diag_elems[np.nonzero(diag_elems)])


def are_multisets_equal(x, y):
    return np.array_equal(np.bincount(x), np.bincount(y))


def max_after_zero(x):
    # got all after-zero elements indexes
    after_zero = np.where(x == 0)[0] + 1

    # get rid of indexes that are out of range
    return x[after_zero[np.where(after_zero < x.size)]].max()


def run_length_encoding(x):
    # https://mail.scipy.org/pipermail/numpy-discussion/2007-October/029378.html
    pos = np.where(np.diff(x) != 0)[0]

    pos = np.concatenate(([0], pos + 1, [x.size]))

    series = (np.array([pos[:-1], pos[1:]])).T

    return (x[series[:, 0]], (np.diff(series)).T[0])


def convert_image(img, coefs):
    return np.tensordot(img, coefs, axes=([2], [0]))


def pairwise_distance(x, y):
    return np.sqrt(((x[:, :, None] - y[:, :, None].T)**2).sum(1))
