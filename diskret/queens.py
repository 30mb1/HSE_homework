
def next_col(current, n=8):
    length = len(current)
    if length == n:
        return
    dangerous = current + [item for l in [(val + length - i, val - length + i) for i, val in enumerate(current)] for item in l if item >= 0 and item <= n]



    for i in range(n):
        if i not in dangerous:
            yield i


def queens(n=8, columns=[]):
    if len(columns) == n:
        yield columns


    for i in next_col(columns, n):
        appended = columns + [i]
        for c in queens(n, appended):
            yield c


if __name__ == '__main__':

    N, K = [int(x) for x in input().split(' ')]
    queens_list = [-1 for i in range(N)]

    for i in range(K):
        x, y = [int(x) for x in input().split(' ')]
        queens_list[x - 1] = y - 1


    s = next(queens(N))


    for i in s:
        l = ["0" for j in range(N)]
        l[i] = "X"
        print (" ".join(l))

    print (s)
