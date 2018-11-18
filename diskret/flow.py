from scipy.optimize import linprog

in_str = raw_input()
in_str = in_str.split()
n, m = int(in_str[0]), int(in_str[1])

A = []
objective = []
for i in range(m):
    objective.append(0)
for i in range(n):
    tmp = []
    for i in range(m):
        tmp.append(0)
    A.append(tmp)

bounds = []
for i in range(m):
    in_str = raw_input()
    in_str = in_str.split()
    x, y, max_cap = int(in_str[0]), int(in_str[1]), int(in_str[2])
    bounds.append((0, max_cap))
    if x == y: continue # useless
    if x == 1 or y == 1:
        if x == 1:
            objective[i] = -1
        if y == 1:
            objective[i] = 1
    if x != n:
        A[x - 1][i] = -1
    if y != n:
        A[y - 1][i] = 1

A.pop(0)
A.pop(len(A) - 1)

last_case = []
for i in range(m):
    last_case.append(A[0][i] + A[-1][i])
A.append(last_case)

b = []
for i in range(len(A)):
    b.append(0)

res = linprog(objective, A_eq=A, b_eq=b, bounds=bounds)

print (int(res.fun * -1))
answer = list(res.x)
for i in range(len(answer)):
    answer[i] = str(int(answer[i]))
print (' '.join(answer))
