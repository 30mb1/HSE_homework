#include <map>
#include <iostream>

int main(int argc, char const *argv[]) {

    std::map<int, int> kek = { {1, 2}, {3, 4}};

    std::cout << kek[999] << '\n';
    return 0;
}
