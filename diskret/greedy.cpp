#include <stdlib.h>
#include <time.h>
#include <vector>
#include <limits.h>
#include <algorithm>
#include <iostream>

std::vector<double> v;
double coeff1, coeff2;

struct Item {
    Item(int a, int b, int c) {
        weight = b;
        price = a;
        num = c;
    }
    int weight;
    int price;
    int num;
};

// custom sort function
bool myfunction (Item i, Item j) {
    double first = coeff1 * (double)i.price / (double)j.price;

    double second = coeff2 * (double)i.weight / (double)j.weight;

    return ( first > second );
}

int main(int argc, char const *argv[]) {
    int N, W, density;

    std::cin >> N >> W;

    std::vector<Item> knapsack;

    for (int i = 0; i < N; i++) {
        int a, b;
        std::cin >> a >> b;

        knapsack.push_back(Item(a, b, i));
    }

    // for (double i = 0.2; i <= 1; i+= 0.2) {
    //     v.push_back(i);
    // }

    v.push_back(1);

    int best_price = 0;
    std::vector<int> best_answer;

    for (auto x: v) {
        coeff1 = x;
        for (auto x2: v) {
            coeff2 = x2;
            std::sort(knapsack.begin(), knapsack.end(), myfunction);

            int cur_weight = 0;
            int cur_price = 0;

            std::vector<int> answer;

            for (auto i: knapsack) {
                if (cur_weight + i.weight <= W) {
                    cur_weight += i.weight;
                    cur_price += i.price;
                    answer.push_back(i.num);
                }
            }

            // std::cout << cur_price << '\n';

            if (cur_price > best_price) {
                best_price = cur_price;
                best_answer = answer;
            }
            // for (auto i: answer) {
            //     std::cout << i + 1 << ' ';
            // }
            // std::cout << '\n';
        }
    }

    std::cout << best_price << '\n';

    for (auto i: best_answer) {
        std::cout << i + 1 << ' ';
    }
    std::cout << '\n';

    return 0;
}
