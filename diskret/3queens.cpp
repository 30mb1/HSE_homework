#include <iostream>
#include <vector>
#include <algorithm>
#include <utility>
#include <stdlib.h>
#include <list>
#include <time.h>
#include <chrono>
#include <stdio.h>

typedef std::vector<std::pair<int, int>> p_vec;
using namespace std::chrono;
std::vector<int> queens;
std::vector<int> slash;
std::vector<int> back_slash;
std::vector<int> column;
std::vector<std::list<int>> knight;
int N, K;

int i_move[8] = {-2, -2, -1, -1, 1, 1, 2, 2};
int j_move[8] = {-1, 1, 2, -2, -2, 2, 1, -1};

p_vec get_k_coord(int x, int y) {
    p_vec ans;
    for (int i = 0; i < 8; i++) {
        int n_x = x + i_move[i];
        int n_y = y + j_move[i];
        if (n_x >= 0 && n_x < N && n_y >= 0 && n_y < N) {
            ans.push_back(std::make_pair(n_x, n_y));
        }
    }
    return ans;
}

void del_old_pos(int x, int y) {
    queens[x] = -1;
    slash[x + y] -= 1;
    back_slash[(2*N+1)/2 - y + x] -= 1;
    column[y] -= 1;
    p_vec tmp = get_k_coord(x, y);
    for (auto & elem : tmp) {
        auto it = std::find(knight[elem.first].begin(), knight[elem.first].end(), elem.second);
        if (it != knight[elem.first].end()) {
            knight[elem.first].erase(it);
        }
    }
}

void set_new_pos(int x, int y) {
    queens[x] = y;
    slash[x + y] += 1;
    back_slash[(2*N+1)/2 - y + x] += 1;
    column[y] += 1;
    p_vec tmp = get_k_coord(x, y);
    for (auto &elem : tmp) {
        knight[elem.first].push_back(elem.second);
    }
}

void move_fig(int from_x, int from_y, int to_x, int to_y) {
    del_old_pos(from_x, from_y);
    set_new_pos(to_x, to_y);
}

bool is_attacked(int x, int y) {
    if (slash[x + y] - 1 > 0 || back_slash[(2*N+1)/2 - y + x] - 1 > 0 || column[y] - 1 > 0 \
        || std::find(knight[x].begin(), knight[x].end(), y) != knight[x].end() ) {
            return true;
        }
    return false;
}

int attack_count(int x, int y) {
    int answer = 0;
    answer += slash[x + y];
    answer += back_slash[(2*N+1)/2 - y + x];
    answer += column[y];
    for (auto &elem: knight[x]) {
        if (elem == y) {
            answer += 1;
        }
    }
    return answer;
}

int main(int argc, char const *argv[]) {
    std::cin >> N >> K;
    steady_clock::time_point clock_begin = steady_clock::now();
    slash.resize(2*N - 1, 0);
    back_slash.resize(2*N - 1, 0);
    column.resize(N, 0);
    queens.resize(N, -1);
    knight.resize(N, std::list<int> (0));
    std::vector<bool> ready_k(N, false);
    srand (time(NULL));

    for (int i = 0; i < K; i++) {
        int x, y;
        std::cin >> x >> y;
        set_new_pos(x - 1, y - 1);
        ready_k[x - 1] = true;
    }

    for (int row = 0; row < N; row++) {
        if (queens[row] == -1) {
            set_new_pos(row, row);
        }
    }

    bool sol_found = false;
    while (true) {
        std::vector<int> attacked;
        // determine rows with attacked queens
        for (int i = 0; i < N; i++) {
            if (ready_k[i] == true) { continue; }
            if (is_attacked(i, queens[i])) {
                attacked.push_back(i);
            }
        }

        // no queens under attack? Goal reached
        if (attacked.size() == 0) {
            sol_found = true;
            break;
        }

        // check if time limit reached
        steady_clock::time_point clock_end = steady_clock::now();
        duration<double> time_span = duration_cast<duration<double>>(clock_end - clock_begin);
        if (time_span.count() > 9.9) {
            break;
        }

        // select random queen, which is under attack and move it
        int rand_row = attacked[rand() % attacked.size()];
        int min_attacked = 1000000000, best_col;
        for (int i = 0; i < N; i++) {
            int tmp = attack_count(rand_row, i);
            if (i == queens[rand_row]) { continue; }
            // we need to find column, where it is minimum quantity of queens
            if (tmp < min_attacked) {
                min_attacked = tmp;
                best_col = i;
            // if there several colun with the same N queens, we need to randomly choose where to go
            } else if (tmp == min_attacked) {
                // we randomly choose which option to choose to move to
                int lucky = rand() % 2;
                if (lucky) { best_col = i; }
            }
        }

        move_fig(rand_row, queens[rand_row], rand_row, best_col);

    }

    if (sol_found) {
        std::cout << "YES" << '\n';
        for (auto &x: queens) {
            std::cout << x + 1 << '\n';
        }
    } else {
        std::cout << "NO" << '\n';
    }

    return 0;
}
