#include <stdlib.h>
#include <time.h>
#include <vector>
#include <limits.h>
#include <algorithm>
#include <iostream>

#define MAXPOP 100
std::vector<int> weights;
std::vector<int> prices;
int max_price = 0;
int min_weight = INT_MAX;
double middle_weight = 0;
double middle_price = 0;
std::vector<int> numbers;

struct Knapsack {
    std::vector<bool> items;
    Knapsack(int count) {
        items = std::vector<bool> (count);
    }
	int fitness;
	double likelihood;
    int weight;
    int price;

	// Test for equality.
	bool operator ==(Knapsack first) {
		for (int i = 0 ;i < items.size(); i++) {
			if (first.items[i] != items[i]) return false;
		}
		return true;
	}
};

class GeneticSolver {
	public:
        GeneticSolver(int weight, int count, int density_) {
            max_weight = weight;
            items_count = count;
            density = density_;
        }
		int Solve();

		// Returns a given Knapsack.
		Knapsack GetGene(int i) { return population[i];}
        std::vector<float> History();
        Knapsack Result();

	protected:
		int max_weight, items_count, density;

		std::vector<Knapsack> population;// Population.
        std::vector<float> fitnes_story;

        Knapsack best_one = Knapsack(0);

		int Fitness(Knapsack &);// Fitness function.
		void GenerateLikelihoods();	// Generate likelihoods.
		double MultInv();// Creates the multiplicative inverse.
		double CreateFitnesses();
		void CreateNewPopulation();
		int GetIndex(double val);

		Knapsack Breed(int p1, int p2);

};


int GeneticSolver::Solve() {
	// Generate initial population.
	srand((unsigned)time(NULL));

	for(int i = 0; i < MAXPOP; i++) { // Fill the population with numbers between
        population.push_back(Knapsack(items_count));
        int cur_weight = 0;
		for (int j = 0; j < items_count; j++) {
            if (rand() % 101 < 16) {
                population[i].items[j] = 1;
                cur_weight += population[i].items[j] * weights[i];
                if (cur_weight > max_weight) {
                    population[i].items[j] = 0;
                    break;
                }
            }
		}
	}
    double avg_fit = 0;


    avg_fit = CreateFitnesses();
    // std::cout << "BEGINNING - " << best_one.price << '\n';
    //
	// if (fitness = CreateFitnesses()) {
	// 	return fitness;
	// }

	int iterations = 0;// Keep record of the iterations.

	while (iterations < 50) {// Repeat until solution found, or over 50 iterations.
        // for (auto i: population) {
        //     std::cout << i.fitness << '\n';
        // }
		GenerateLikelihoods();// Create the likelihoods.
        // for (auto x: population) {
        //     std::cout << (double)x.likelihood << ' ';
        // }
        // std::cout << '\n';
		CreateNewPopulation();
        double avg_fit_new = CreateFitnesses();
        // if (avg_fit_new >= avg_fit) {
        //     break;
        // }
        avg_fit = avg_fit_new;
        fitnes_story.push_back(avg_fit);
		// if (fitness = CreateFitnesses()) {
		// 	return fitness;
		// }
        // std::cout << "Iteration - " << iterations << '\n';

		iterations++;
	}

    for (auto i: numbers) {
        if (best_one.weight < max_weight && \
            best_one.weight + weights[i] < max_weight && \
            best_one.items[i] == 0) {
                best_one.weight += weights[i];
                best_one.price += prices[i];
            }
            if (max_weight - best_one.weight < min_weight) {
                break;
            }
    }

	return 0;
}

std::vector<float> GeneticSolver::History() {
    return fitnes_story;
};

Knapsack GeneticSolver::Result() {
    return best_one;
};

int GeneticSolver::Fitness(Knapsack &cur) {
    int total_price = 0;
    int total_weight = 0;
    //
    // for (auto i: cur.items) {
    //     total_price += prices[i];
    //     total_weight += weights[i];
    // }


    for (int i = 0; i < items_count; i++) {
        total_price += cur.items[i] * prices[i];
        total_weight += cur.items[i] * weights[i];
    }
    if (total_weight > max_weight) {
        total_price = 0;
    }
    cur.weight = total_weight;
    cur.price = total_price;

    if (total_price > best_one.price) {
        best_one = cur;
    }

    // std::cout << total_price << '\n';

    return cur.fitness = abs(total_price - max_price);
}

double GeneticSolver::CreateFitnesses() {
	long long int avgfit = 0;
	int fitness = 0;
	for(int i = 0; i < MAXPOP; i++) {
		fitness = Fitness(population[i]);
		avgfit += fitness;
	}

	return (double)avgfit / (double)MAXPOP;
}


double GeneticSolver::MultInv() {
	double sum = 0;
	for(int i = 0; i < MAXPOP; i++) {
		sum += 1 / ( (double)population[i].fitness );
	}
	return sum;
}


void GeneticSolver::GenerateLikelihoods() {
	double multinv = MultInv();

    // std::cout << multinv << '\n';

	double last = 0;
	for(int i = 0; i < MAXPOP; i++) {
		population[i].likelihood = last = last + ((1/((double)population[i].fitness) / multinv) * 1000);
	}
}


int GeneticSolver::GetIndex(double val) {
	double last = 0;
	for(int i = 0; i < MAXPOP; i++) {
		if (last <= val && val <= population[i].likelihood) return i;
		else last = population[i].likelihood;
	}

	return MAXPOP - 1;
}


Knapsack GeneticSolver::Breed(int p1, int p2) {
	int crossover = rand() % (items_count - 1) + 1;// Create the crossover point (not first).
	int first = rand() % 101;// Which parent comes first?

	Knapsack child = population[p1];// Child is all first parent initially.
	int initial = 0, final_ = items_count;// The crossover boundaries.

	if (first < 50) {
        initial = crossover;

    } else {
        final_ = crossover;
    }

    int diff = max_weight - population[p1].weight + max_weight - population[p2].weight;


    int cur_weight = 0;
    bool mutated = false;
	for(int i = initial; i < final_; i++) { // Crossover!
		child.items[i] = population[p2].items[i];

        if (mutated == false) {
            if (rand() % 101 < 5) {
                if (diff > 0) {
                    child.items[i] = 1;
                } else {
                    child.items[i] = 0;
                }
                mutated = true;
            }
        }
	}

	return child;// Return the kid...
}

void GeneticSolver::CreateNewPopulation() {
    std::vector<Knapsack> temp_pop;
	for(int i = 0; i < MAXPOP; i++) {
		int parent1 = 0, parent2 = 0, iterations = 0;
		while(parent1 == parent2) {
			parent1 = GetIndex((double)(rand() % 1001));
			parent2 = GetIndex((double)(rand() % 1001));

			if (++iterations > 25) {
                break;
            }
		}


        // std::cout << parent1 << " " << parent2 << " ";
        temp_pop.push_back(Breed(parent1, parent2));
	}

    population = temp_pop;
}

// custom sort function
bool myfunction (int i, int j) {
    double first = (double)prices[i] / (double)weights[i];
    double second = (double)prices[j] / (double)weights[j];

    return ( first > second );
}

int main(int argc, char const *argv[]) {
    int N, W, density;

    std::cin >> N >> W;

    for (int i = 0; i < N; i++) {
        numbers.push_back(i);
        int a, b;
        std::cin >> a >> b;
        middle_weight += (double)b / (double)N;
        // middle_price +=(double)a / (double)N;
        if (a > max_price) {
            max_price = a;
        }
        if (b < min_weight) {
            min_weight = b;
        }
        prices.push_back(a);
        weights.push_back(b);
    }

    std::sort(numbers.begin(), numbers.end(), myfunction);

    density = ((double)(W / middle_weight) / (double)N) * 100;
    // std::cout  << '\n';

    max_price = (W / middle_weight) * max_price;

    // std::cout << max_price << '\n';
    // std::cout << density << '\n';

    GeneticSolver knapsack_killer2000(W, N, density);

    knapsack_killer2000.Solve();

    // std::cout << "Solved" << '\n';

    // auto tmp = knapsack_killer2000.History();
    auto result = knapsack_killer2000.Result();

    int cur_weight = 0;
    int cur_price = 0;
    std::vector<int> answer;

    for (int i = 0; i < N; i++) {
        if (cur_weight + weights[i] <= W and result.items[i] != 0) {
            cur_weight += weights[i];
            cur_price += prices[i];
            answer.push_back(i);
        }
    }

    std::cout << cur_price << '\n';
    for (auto i: answer) {
        std::cout << i + 1 << ' ';
    }
    std::cout << '\n';

    return 0;
}
