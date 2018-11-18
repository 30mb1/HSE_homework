#include <iostream>
#include <vector>
#include <list>
#include <algorithm>

int N, M, K, T;
std::vector<std::vector<int>> graph;
std::vector<int> matching;
std::vector<bool> left_used;
std::vector<int> result;
std::vector<bool> used;

bool khun_dfs(int vert) {
    for (int i = 0; i < graph[vert].size(); i++) {
        int to_ = graph[vert][i];
        if (used[to_]) { continue; }
        used[to_] = true;
        if (matching[to_] == -1 || khun_dfs(matching[to_])) {
            result.push_back(to_);
            result.push_back(vert);
            return true;
        }
        used[to_] = false;
    }
    return false;
}

int main() {
    std::cin >> N >> M >> K;
    matching.resize(M, -1);
    graph.resize(N);
    left_used.resize(N, false);
    used.resize(M);

    for (int i = 0; i < K; i++) {
        int from_, to_;
        std::cin >> from_ >> to_;
        graph[from_ - 1].push_back(to_ - 1);
    }

    std::cin >> T;

    for (int i = 0; i < T; i++) {
        int from_, to_;
        std::cin >> from_ >> to_;
        matching[to_ - 1] = from_ - 1;
        left_used[from_ - 1] = true;
    }

    for (int i = 0; i < N; i++) {
        if (left_used[i] == false) {
            std::fill (used.begin(), used.end(), false);
            if (khun_dfs(i)) { break; }
        }
    }

    std::cout << result.size() << std::endl;

    if (result.size() != 0) {
        for (int i = result.size() - 1; i >= 0; i--) {
            std::cout << result[i] + 1 << ' ';
        }
        std::cout << std::endl;
    }

    return 0;
}
