
def pos_var(current, n, k_queens):
    length = len(current)
    if length == n: return

    if length in k_queens.keys():
        return [k_queens[length]]
    else:
        dangerous = list(current)
        dangerous += list(k_queens.values())

        for l in [(j + length - i, j - length + i) for i, j in enumerate(current)]:
            for item in l:
                if item >= 0 and item <= n:  # Check coordinate is located between board limits
                    dangerous.append(item)

        banned = []
        if length >= 1:
            banned += [current[-1] - 2, current[-1] + 2]
        if length >= 2:
            banned += [current[-2] - 1, current[-2] + 1]

        for l in [(j + i - length, j - i + length) for i, j in k_queens.items()]:
            for item in l:
                if item >= 0 and item <= n:  # Check coordinate is located between board limits
                    dangerous.append(item)

        if k_queens.get(length + 1):
            banned += [k_queens[length + 1] - 2, k_queens[length + 1] + 2]
        if k_queens.get(length + 2):
            banned += [k_queens[length + 2] - 1, k_queens[length + 2] + 1]

        for item in banned:
            if item >= 0 and item <= n:  # Check coordinate is located between board limits
                dangerous.append(item)

        res = []
        for i in range(n):
            if i not in dangerous:  # Check that vertical line is already used by some queen
                res.append(i)

        return res


def queens(n, columns, k_queens):
    if len(columns) == n:
        return columns

    for i in pos_var(columns, n, k_queens):
        appended = columns + [i]

        tmp = queens(n, appended, k_queens)
        if tmp: return tmp


if __name__ == '__main__':
    N, K = [int(x) for x in raw_input().split(' ')]
    k_queens = {}

    for i in range(K):
        x, y = [int(x) for x in raw_input().split(' ')]
        k_queens[x - 1] = y - 1


    s = queens(N, [], k_queens)
    if s:
        print ('YES')
        for i in s:
            print (i+1)
    else:
        print ('NO')
