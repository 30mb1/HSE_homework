to_int = lambda x: 0 if x == 'W' else 1
even = lambda x: True if x % 2 == 0 else False

n, m = map(lambda x: int(x), input().split())

first = {}
second = {}

plate = [[0 for x in range(m)] for i in range(n)]
for i in range(n):
    plate[i] = [to_int(x) for x in input()]

    for j in range(m):
        if even(j + i):
            first[(i, j)] = plate[i][j]
        else:
            second[(i, j)] = plate[i][j]

# print (first)
# print (second)
# W - 0, B - 1
first_list = list(first.values())
second_list = list(second.values())
black_count_first = first_list.count(1)
black_count_second = second_list.count(1)

white_count_first = first_list.count(0)
white_count_second = second_list.count(0)

if black_count_first > black_count_second:
    first_color, second_color = 1, 0
elif black_count_first < black_count_second:
    first_color, second_color = 0, 1
elif white_count_first > white_count_second:
    first_color, second_color = 0, 1
else:
    first_color, second_color = 1, 0

# print (first_color)
first_paint = set()
second_paint = set()

for i in range(n):
    for j in range(m):
        if even(j + i):
            if first[(i, j)] != first_color: first_paint.add((i, j))
        else:
            if second[(i, j)] != second_color: second_paint.add((i, j))

def get_diag_indice(start):
    i, j = start
    res = set([(i, j)])
    while True:
        if i+1 < n and j+1 < m:
            res.add((i+1, j+1))
            i+=1
            j+=1
        else:
            return res

def get_back_diag_indice(start):
    i, j = start
    res = set([(i, j)])
    while True:
        if i-1 >= 0 and j+1 < m:
            res.add((i-1, j+1))
            i-=1
            j+=1
        else:
            return res

first_diags = []
second_diags = []

for i in range(n):
    if even(i):
        first_diags.append((get_diag_indice((i, 0)), 2))
    else:
        second_diags.append((get_diag_indice((i, 0)), 2))

for j in range(1, m):
    if even(j):
        first_diags.append((get_diag_indice((0, j)), 2))
    else:
        second_diags.append((get_diag_indice((0, j)), 2))

for i in range(n):
    if even(i):
        first_diags.append((get_back_diag_indice((i, 0)), 1))
    else:
        second_diags.append((get_back_diag_indice((i, 0)), 1))

for j in range(1, m):
    if even(j):
        first_diags.append((get_back_diag_indice((n - 1, j)), 1))
    else:
        second_diags.append((get_back_diag_indice((n - 1, j)), 1))

#
# print (first_paint)
# print (second_paint)
# print (first_diags)
first_res_diags = []
second_res_diags = []

# print (first_diags)

# print (second_diags)

if len(first_paint) != 0:
    while len(first_paint) > 0:
        best_intersection = 0
        best_diag = (set(), 0)
        for i in first_diags:
            tmp = i[0] & first_paint
            if len(tmp) > best_intersection:
                best_intersection = len(tmp)
                best_diag = i

        first_res_diags.append(best_diag)
        first_paint -= best_diag[0]

if len(second_paint) != 0:
    while len(second_paint) > 0:
        best_intersection = 0
        best_diag = (set(), 0)
        for i in second_diags:
            tmp = i[0] & second_paint
            if len(tmp) > best_intersection:
                best_intersection = len(tmp)
                best_diag = i

        second_res_diags.append(best_diag)
        second_paint -= best_diag[0]

# print (first_res_diags)
# print (second_res_diags)


tmp = { 1: 'B', 0: 'W'}

answer = 0
answer_str = []
if len(first_res_diags) != 0:
    answer += len(first_res_diags)
    for i in first_res_diags:
        elem = i[0].pop()
        answer_str.append(f'{i[1]} {elem[0]+1} {elem[1]+1} {tmp[first_color]}')

# print (second_color)
if len(second_res_diags) != 0:
    answer += len(second_res_diags)
    for i in second_res_diags:
        elem = i[0].pop()
        answer_str.append(f'{i[1]} {elem[0]+1} {elem[1]+1} {tmp[second_color]}')

print (answer)
print ('\n'.join(answer_str))
