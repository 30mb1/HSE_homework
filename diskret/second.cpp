#include <algorithm>
#include <iostream>
#include <vector>
#include <string>
#include <set>


int N, M;
std::vector<std::vector<int>> chess;
std::vector<std::set<int>> first_diags, second_diags;
std::set<int> to_paint;

std::set<int> get_first_diag(int i, int j) {
    std::set<int> diag;
    while (true) {
        if (i < N && j >= 0) {
            diag.insert(i*M + j);
            i++;
            j--;
        } else { break; }
    }
    return diag;
}

std::set<int> get_second_diag(int i, int j) {
    std::set<int> diag;
    while (true) {
        if (i < N && j < M) {
            diag.insert(i*M + j);
            i++;
            j++;
        } else { break; }
    }
    return diag;
}


void get_diag_indeces() {
    // get all diags of 1st type
    for (int i = 0; i < M; i++) {
        first_diags.push_back(get_first_diag(0, i));
        second_diags.push_back(get_second_diag(0, i));

    }
    for (int i = 1; i < N; i++) {
        first_diags.push_back(get_first_diag(i, M-1));
        second_diags.push_back(get_second_diag(i, 0));
    }
    return;
}

bool even(int i) {
    if (i % 2 == 0) { return true; }
    return false;
}

std::vector<int> matching, result;
std::vector<bool> left_used, used, right_used;
std::vector<std::vector<int>> graph;

bool khun_dfs(int vert) {
    if (used[vert] == true) { return false; }
    used[vert] = true;
    for (int i = 0; i < graph[vert].size(); i++) {
        int to_ = graph[vert][i];
        // if (used[to_]) { continue; }
        // used[to_] = true;
        if (matching[to_] == -1 || khun_dfs(matching[to_])) {
            matching[to_] = vert;
            // left_used[vert] = true;
            return true;
        }
        // used[to_] = false;
    }
    return false;
}

std::vector<std::vector<int>> oriented_graph;

void dfs(int vert) {
    used[vert] = true;
    for (int i = 0; i < oriented_graph[vert].size(); i++) {
        int to_ = oriented_graph[vert][i];
        if (used[to_]) { continue; }
        dfs(to_);
    }
    return;
}

int main(int argc, char const *argv[]) {
    std::cin >> N >> M;

    chess.resize(N);
    matching.resize(M+N-1, -1);
    left_used.resize(N+M-1, false);
    used.resize(N+M-1);
    graph.resize(N+M-1);

    for (int i = 0; i < N; i++) {
        std::string line;
        std::cin >> line;
        for (int v = 0; v < M; v++) {
            if (line[v] == 'W') {
                chess[i].push_back(0);
            } else {
                chess[i].push_back(1);
            }
        }
    }

    get_diag_indeces();

    // int first_color = 1, second_color = 0;

    int first_color = 1, second_color = 0;

    for (int i = 0; i < N; i++) {
        for (int j = 0; j < M; j++) {
            if (even(i+j)) {
                if (chess[i][j] != first_color) { to_paint.insert(i*M + j); }
            } else {
                if (chess[i][j] != second_color) { to_paint.insert(i*M + j); }
            }
        }
    }

    for (int i = 0; i < first_diags.size(); i++) {
        std::vector<int> v(N+M-1);
        std::vector<int>::iterator it;
        auto first = first_diags[i];
        auto second = to_paint;

        it=std::set_intersection (first.begin(), first.end(), second.begin(), second.end(), v.begin());
        v.resize(it-v.begin());

        if (v.size() != 0) {
            for (int j = 0; j < second_diags.size(); j++) {
                std::vector<int>::iterator it2;
                std::vector<int> v2(N+M-1);
                auto first2 = second_diags[j];
                auto second2 = v;

                it2=std::set_intersection (first2.begin(), first2.end(), second2.begin(), second2.end(), v2.begin());
                v2.resize(it2-v2.begin());

                if (v2.size() != 0) {
                    graph[i].push_back(j);
                }
            }
        }
    }

    for (int i = 0; i < graph.size(); i++) {
        // if (left_used[i] == false) {
            std::fill (used.begin(), used.end(), false);
            khun_dfs(i);
        // }
    }
    for (auto x: matching) {
        if (x != -1) {
            left_used[x] = true;
        }
    }

    oriented_graph.resize(((N+M-1) * 2));

    for (int i = 0; i < graph.size(); i++) {
        if (left_used[i] == true) {
            for (auto x: graph[i]) {
                if (matching[x] == i) {
                    oriented_graph[x + N+M-1].push_back(i);
                } else {
                    oriented_graph[i].push_back(x + N+M-1);
                }
            }
        } else {
            for (auto x: graph[i]) {
                oriented_graph[i].push_back(x + N+M-1);
            }
        }
    }

    used.resize(((N+M-1) * 2));
    std::fill (used.begin(), used.end(), false);

    for (int i = 0; i < graph.size(); i++) {
        if (left_used[i] == false) {
            dfs(i);
        }
    }

    std::vector<int> left_res, right_res;

    for (int i = 0; i < oriented_graph.size(); i++) {
        if (i < graph.size()) {
            if (used[i] == false) {
                left_res.push_back(i);
            }
        } else {
            if (used[i] == true) {
                right_res.push_back(i - graph.size());
            }
        }
    }

    std::swap(first_color, second_color);

    to_paint.clear();
    graph = std::vector<std::vector<int>> (N+M-1);
    used = std::vector<bool> (N+M-1);
    left_used = std::vector<bool> (N+M-1, false);
    matching = std::vector<int> (N+M-1, -1);
    oriented_graph = std::vector<std::vector<int>> ((N+M-1) * 2);


    for (int i = 0; i < N; i++) {
        for (int j = 0; j < M; j++) {
            if (even(i+j)) {
                if (chess[i][j] != first_color) { to_paint.insert(i*M + j); }
            } else {
                if (chess[i][j] != second_color) { to_paint.insert(i*M + j); }
            }
        }
    }

    for (int i = 0; i < first_diags.size(); i++) {
        std::vector<int> v(N+M-1);
        std::vector<int>::iterator it;
        auto first = first_diags[i];
        auto second = to_paint;

        it=std::set_intersection (first.begin(), first.end(), second.begin(), second.end(), v.begin());
        v.resize(it-v.begin());

        if (v.size() != 0) {
            for (int j = 0; j < second_diags.size(); j++) {
                std::vector<int>::iterator it2;
                std::vector<int> v2(N+M-1);
                auto first2 = second_diags[j];
                auto second2 = v;

                it2=std::set_intersection (first2.begin(), first2.end(), second2.begin(), second2.end(), v2.begin());
                v2.resize(it2-v2.begin());

                if (v2.size() != 0) {
                    graph[i].push_back(j);
                }
            }
        }
    }

    for (int i = 0; i < graph.size(); i++) {
        // if (left_used[i] == false) {
            std::fill (used.begin(), used.end(), false);
            khun_dfs(i);
        // }
    }

    for (auto x: matching) {
        if (x != -1) {
            left_used[x] = true;
        }
    }

    oriented_graph.resize(((N+M-1) * 2));

    for (int i = 0; i < graph.size(); i++) {
        if (left_used[i] == true) {
            for (auto x: graph[i]) {
                if (matching[x] == i) {
                    oriented_graph[x + N+M-1].push_back(i);
                } else {
                    oriented_graph[i].push_back(x + N+M-1);
                }
            }
        } else {
            for (auto x: graph[i]) {
                oriented_graph[i].push_back(x + N+M-1);
            }
        }
    }

    used.resize(((N+M-1) * 2));
    std::fill (used.begin(), used.end(), false);

    for (int i = 0; i < graph.size(); i++) {
        if (left_used[i] == false) {
            dfs(i);
        }
    }

    std::vector<int> left_res2, right_res2;

    for (int i = 0; i < oriented_graph.size(); i++) {
        if (i < graph.size()) {
            if (used[i] == false) {
                left_res2.push_back(i);
            }
        } else {
            if (used[i] == true) {
                right_res2.push_back(i - graph.size());
            }
        }
    }

    std::swap(first_color, second_color);
    if ((left_res.size() + right_res.size()) > (left_res2.size() + right_res2.size())) {
        std::swap(first_color, second_color);
        left_res = left_res2;
        right_res = right_res2;
    }


    std::cout << left_res.size() + right_res.size() << '\n';

    for (auto x: left_res) {
        auto tmp = *first_diags[x].begin();
        int i = (tmp / M) + 1;
        int j = (tmp % M) + 1;
        char color;
        if (even(i+j)) {
            if (first_color == 1) {
                color = 'B';
            } else {
                color = 'W';
            }
        } else {
            if (second_color == 1) {
                color = 'B';
            } else {
                color = 'W';
            }
        }
        std::cout << 1 << " " << i << " " << j << " " << color << '\n';
    }

    for (auto x: right_res) {
        auto tmp = *second_diags[x].begin();
        int i = (tmp / M) + 1;
        int j = (tmp % M) + 1;
        char color;
        if (even(i+j)) {
            if (first_color == 1) {
                color = 'B';
            } else {
                color = 'W';
            }
        } else {
            if (second_color == 1) {
                color = 'B';
            } else {
                color = 'W';
            }
        }
        std::cout << 2 << " " << i << " " << j << " " << color << '\n';
    }

    return 0;
}
