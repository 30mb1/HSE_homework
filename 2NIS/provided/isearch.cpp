#include "isearch.h"
#include "limits"
#include <iostream>
#include <time.h>
#include <algorithm>


ISearch::ISearch()
{
    hweight = 1;
    breakingties = CN_SP_BT_GMAX;
}

ISearch::~ISearch(void) {}

int ISearch::open_count() {
    int count = 0;
    for (auto x: open) {
        count += x.size();
    }
    return count;
}

SearchResult ISearch::startSearch(ILogger *Logger, const Map &map, const EnvironmentOptions &options)
{
    clock_t tStart = clock();
    Node curNode;
    curNode.i = map.start_i;
    curNode.j = map.start_j;
    curNode.H = computeHFromCellToCell(curNode.i, curNode.j, map.goal_i, map.goal_j, options);
    curNode.F = hweight * curNode.H;
    curNode.g = 0;
    curNode.parent = nullptr;
    open.resize(map.getMapHeight());
    add_or_update(curNode);
    bool pathfound = false;
    sresult.pathfound = false;

    while (open_count() != 0) {
        Node best;
        best.F = HUGE_VAL;
        std::vector<Node>::iterator to_erase;
        int tmp;
        for (int i = 0; i < open.size(); i++) {
            std::vector<Node>::iterator it = open[i].begin();
            for (; it != open[i].end(); it++) {
                if (it->F < best.F) {
                    best = *it;
                    to_erase = it;
                    tmp = i;
                } else if (it->F == best.F) {
                    if ((breakingties == CN_SP_BT_GMAX && it->g >= best.g) ||
                       (breakingties == CN_SP_BT_GMIN && it->g <= best.g)) {
                           best = *it;
                           to_erase = it;
                           tmp = i;
                       }
                }
            }
        }
        open[tmp].erase(to_erase);

        // std::cout << "FIND MIN" << '\n';

        curNode = best;
        int x = curNode.i, y = curNode.j;
        // std::cout << "1. Got best node" << '\n';

        close.insert({x * map.getMapWidth() + y, curNode});
        // std::cout << "1.1. Inserted." << '\n';
        // std::cout << "1.2. Made pop." << '\n';

        // std::cout << "1.5. Some usual work" << '\n';

        // check if goal achieved
        if (map.goalAchieved(x, y)) {
            pathfound = true;
            break;
        }
        // std::cout << "2. Checked goal" << '\n';

        auto successors = findSuccessors(curNode, map, options);
        // std::cout << "3. Found successors" << '\n';
        auto parent = &close.at(x * map.getMapWidth() + y);

        for (auto node: successors) {
            node.parent = parent;
            node.H = computeHFromCellToCell(node.i, node.j, map.goal_i, map.goal_j, options);

            node.F = node.g + hweight * node.H;
            // std::cout << "--------> INSIDE" << '\n';
            // open[node.i].push_back(node);
            add_or_update(node);
            // std::cout << "OUTSIDE ---------->" << '\n';
        }
        // std::cout << "sTEP" << '\n';
    }

    sresult.nodescreated = close.size() + open_count();
    sresult.numberofsteps = close.size();
    //
    // std::cout << "Got sizes" << '\n';
    // std::cout << sresult.nodescreated << " " << sresult.numberofsteps << '\n';

    if (pathfound == true) {
        sresult.pathfound = true;
        makePrimaryPath(curNode);
        makeSecondaryPath();
    }
    sresult.time = (double)(clock() - tStart)/CLOCKS_PER_SEC;
    sresult.hppath = &hppath; //Here is a constant pointer
    sresult.lppath = &lppath;
    return sresult;
}

std::list<Node> ISearch::findSuccessors(Node curNode, const Map &map, const EnvironmentOptions &options)
{
    std::list<Node> successors;
    Node next_node;
    for (int i = -1; i < 2; i++) {
        for (int j = -1; j < 2; j++) {
            int x = curNode.i, y = curNode.j;
            // in case of 0/0 we don't move, continue
            if (i == 0 && j == 0) { continue; }
            if (map.CellOnGrid(x+i, y+j) && map.CellIsTraversable(x+i, y+j)) {
                // check if this cell is in close alredy
                auto res = close.find((x+i)*map.getMapWidth() + y+j);
                if (res != close.end()) { continue; }

                // several options check
                if (i != 0 && j != 0) {
                    // case for diagonal move
                    if (options.allowdiagonal == false) { continue; }
                    if (options.cutcorners == false) {
                        // check if there is obsticle on the way
                        if (map.CellIsObstacle(x, y+j) || map.CellIsObstacle(x+i, y)) { continue; }
                    }
                    if (options.allowsqueeze == false) {
                        if (map.CellIsObstacle(x, y+j) && map.CellIsObstacle(x+i, y)) { continue; }
                    }
                }

                // set new node params
                next_node.i = x + i;
                next_node.j = y + j;
                // case for straight and diagonal paths
                if (i == 0 || j == 0) {
                    next_node.g = curNode.g + 1;
                } else {
                    next_node.g = curNode.g + sqrt(2);
                }
                successors.push_back(next_node);
            }

        }
    }
    return successors;
}

void ISearch::makePrimaryPath(Node curNode)
{
    Node cur_node = curNode;
    while (cur_node.parent) {
        lppath.push_front(cur_node);
        cur_node = *cur_node.parent;
    }
    lppath.push_front(cur_node);
}

void ISearch::makeSecondaryPath()
{
    std::list<Node>::iterator it = lppath.begin();
    hppath.push_back(*it);
    for (; it != --lppath.end();) {
        int i = it->i, j = it->j;
        it++;
        int n_i = it->i, n_j = it->j;
        int di = n_i - i, dj = n_j - j;
        it++;
        int dn_i = it->i - n_i, dn_j = it->j - n_j;
        if (dn_i != di || dn_j != dj) {
            it--;
            hppath.push_back(*it);
        } else {
            it--;
        }
    }
}

void ISearch::add_or_update(Node newNode)
{
    int x = newNode.i;
    if (open[x].size() == 0) {
        open[x].push_back(newNode);
        return;
    }
    std::vector<Node>::iterator it = open[x].begin(), pos = open[x].end();
    bool found = false;
    for (; it != open[x].end(); ++it) {
        // same node
        if (it->j == newNode.j) {
            // worse heurestic
            if (newNode.F >= it->F) return;
            open[x].erase(it);
            break;
        }
    }
    open[newNode.i].push_back(newNode);
}
