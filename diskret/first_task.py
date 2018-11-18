used = []
edge_map = []
matching_map = {}

def khun_dfs(vert):
    global used
    global edge_map
    global matching_map
    global kuhn_success

    if used[vert]: return False

    used[vert] = True
    for v in edge_map[vert]:
        if matching_map[v] == -1 or khun_dfs(matching_map[v]) is True:
            matching_map[v] = vert
            return True;

    return False

def get_input():
    return map(lambda x: int(x), input().split())

n, m, k = get_input()

edge_map = [[] for i in range(n)]

for i in range(k):
    from_, to_ = get_input()
    edge_map[from_ - 1].append(to_ - 1)

t, = get_input()

before_khun = set()

matching_map = {i : -1 for i in range(m)}

for i in range(t):
    from_, to_ = get_input()
    matching_map[to_ - 1] = from_ - 1
    before_khun.add((from_ - 1, to_ - 1))

success = False

for i in range(n):
    used = [False for i in range(n)]
    if i in matching_map.values(): continue
    if khun_dfs(i):
        success = True
        break

if not success:
    print (0)
else:
    after_khun = set()
    for i in range(m):
        if (matching_map[i] != -1):
            after_khun.add((matching_map[i], i))

    answer = sorted(list(after_khun - before_khun), key=lambda x: x[0], reverse=True)
    print (len(answer) * 2)
    answer_string = []
    for pair in answer:
        answer_string.append(f'{pair[0] + 1} {pair[1] + 1}')
    print (' '.join(answer_string))
