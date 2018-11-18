import scipy.optimize
import numpy as np

if __name__ == '__main__':
    n, m = map(int, raw_input().split())
    A = np.zeros((n - 2, m), dtype=np.int64)
    c = np.zeros(m, dtype=np.int64)
    bounds = []

    for i in range(0, m):
        a, b, f = map(int, raw_input().split())
        bounds.append((0, f))
        if a == b:
            continue
        if a == 1:
            c[i] = -1
        if b == 1:
            c[i] = 1
        if a not in [1, n]:
            A[a - 2, i] = -1
        if b not in [1, n]:
            A[b - 2, i] = 1

    print (A)
    print (np.zeros(n - 2))
    result = scipy.optimize.linprog(c, A_eq=A, b_eq=np.zeros(n - 2), bounds=bounds)
    max_flow = -int(result.fun)
    values = map(int, result.x.tolist())

    print(max_flow)
    print(' '.join(map(str, values)))
