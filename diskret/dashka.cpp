#include <vector>
#include <iostream>
#include <list>

using namespace std;

int N, M, K, T, x, y;


bool khun(int v, vector<int> &scnd_d, vector<int> &result, vector<std::vector<int>> &graph, vector<bool> &used) {
    for (auto to : graph[v]) {
        if (!used[to]) {
            used[to] = true;
            if (scnd_d[to] == -1 || khun(scnd_d[to], scnd_d, result, graph, used)) {
                result.push_back(to);
                result.push_back(v);
                return true;
            }
            used[to] = false;
        }
    }
    return false;
}


int main() {
    cin >> N >> M >> K;
    vector<vector<int>> graph(N);
    vector<int> frst_d(N, -1), scnd_d(M, -1), result;
    //vector<bool> used(M);

    for (int i = 0; i < K; ++i) {
        x = 0;
        y = 0;
        std::cin >> x >> y;
        graph[x-1].push_back(y-1);
    }

    cin >> T;

    for (int i = 0; i < T; ++i) {
        x = 0;
        y = 0;
        cin >> x >> y;
        frst_d[x-1] = y-1;
        scnd_d[y-1] = x-1;
    }

    for (int i = 0; i < N; i++) {
        if (frst_d[i] == -1) {
            vector<bool> used(M, false);
            if (khun(i, scnd_d, result, graph, used)) {
                break;
            }
        }
    }

    cout << result.size() << endl;
    int sz = result.size();
    if (sz != 0) {
        for (int i = sz - 1; i >= 0; i--) {
            cout << result[i] + 1 << ' ';
        }
        cout << endl;
    }
    return 0;
}
