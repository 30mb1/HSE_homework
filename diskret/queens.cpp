#include <iostream>
#include <vector>
#include <map>
#include <algorithm>

int N, K;
std::map <int, int> k_queens;

std::vector<int> next_elem(std::vector<int>& curr, std::vector<bool> slash,
    std::vector<bool> back_slash, std::vector<bool> vert) {
    int length = curr.size();

    if (k_queens.find(length) != k_queens.end()) {
        return { k_queens[length] };
    } else {
        std::vector<int> vars_to_check;
        std::vector<bool> dangerous (N, false);
        if (length >= 1) {
            vars_to_check.push_back(curr[length - 1] - 2);
            vars_to_check.push_back(curr[length - 1] + 2);
        }
        if (length >= 2) {
            vars_to_check.push_back(curr[length - 2] - 1);
            vars_to_check.push_back(curr[length - 2] + 1);
        }

        auto res = k_queens.find(length + 1);
        if (res != k_queens.end()) {
            vars_to_check.push_back(k_queens[length + 1] - 2);
            vars_to_check.push_back(k_queens[length + 1] + 2);
        }
        res = k_queens.find(length + 2);
        if (res != k_queens.end()) {
            vars_to_check.push_back(k_queens[length + 2] - 1);
            vars_to_check.push_back(k_queens[length + 2] + 1);
        }

        for (auto x : vars_to_check) {
            if (x >= 0 && x <= N) {
                dangerous[x] = true;
            }
        }

        std::vector<int> answer;
        for (int i = 0; i < N; i++) {
            if (!slash[length + i] && !back_slash[(2*N+1)/2 + length - i] && !vert[i] && !dangerous[i]) {
                answer.push_back(i);
            }
        }
        return answer;
    }

}


std::vector<int> queens(std::vector<int>& curr, std::vector<bool> slash,
    std::vector<bool> back_slash, std::vector<bool> vert) {
    if (curr.size() == N) { return curr; }

    auto pos_vars = next_elem(curr, slash, back_slash, vert);
    if (pos_vars.size() == 0) { return {}; }

    for (auto x : pos_vars) {
        // std::cout << x << '\n';
        std::vector<int> tmp = curr;
        tmp.push_back(x);
        int len = tmp.size();

        slash[len - 1 + x] = true;
        vert[x] = true;
        back_slash[(2*N+1)/2 - x + len - 1] = true;

        tmp = queens(tmp, slash, back_slash, vert);

        slash[len - 1 + x] = false;
        vert[x] = false;
        back_slash[(2*N+1)/2 - x + len - 1] = false;

        if (tmp.size() != 0) {
            return tmp;
        }
    }
    return {};

}

int main(int argc, char const *argv[]) {
    std::cin >> N >> K;
    std::vector<bool> slash (2*N - 1, false);
    std::vector<bool> back_slash(2*N - 1, false);
    std::vector<bool> vert(N, false);

    for (int i = 0; i < K; i++) {
        int x, y;
        std::cin >> x >> y;
        k_queens[x - 1] = y - 1;
        slash[(x - 1) + (y - 1)] = true;
        back_slash[(2*N+1)/2 - (y - 1) + (x - 1)] = true;
        vert[y - 1] = true;
    }

    std::vector<int> curr;
    std::vector<int> res = queens(curr, slash, back_slash, vert);
    if (res.size() != 0) {
        std::cout << "YES" << '\n';
        for (auto x: res) {
            std::cout << x + 1 << '\n';
        }
    } else {
        std::cout << "NO" << '\n';
    }

    return 0;
}
