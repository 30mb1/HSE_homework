N, W = [int(i) for i in input().split(' ')]

print (N, W)

items = []

for i in range(N):
    price, weight = [int(j) for j in input().split(' ')]
    items += [(price, weight, i + 1)]

items = sorted(items, key=lambda x: x[0] / x[1], reverse=True)

weight = 0
price = 0
answer = []

for it in items:
    if (it[1] + weight < W):
        price += it[0]
        weight += it[1]
        answer.append(it[2])

print (price)

for i in answer:
    print (i, end=' ')

print ()
