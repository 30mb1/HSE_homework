#include <stdlib.h>
#include <stdio.h>
#include "glpk.h"
#include <iostream>
#include <vector>
#include <utility>


int main(void) {
  glp_prob *mip = glp_create_prob();
  glp_set_prob_name(mip, "C solver");
  glp_set_obj_dir(mip, GLP_MIN);

  int n, m;
  std::cin >> n >> m;


  double warehouse [n][2];
  for (int i = 0; i < n; i++) {
      double q, w;
      std::cin >> q >> w;
      warehouse[i][0] = q;
      warehouse[i][1] = w;
  }

  double demand [m];
  for (int i = 0; i < m; i++) {
      double q;
      std::cin >> q;
      demand[i] = q;
  }

  double use_cost [n][m];
  for (int i = 0; i < n; i++) {
      for (int j = 0; j < m; j++) {
          double q;
          std::cin >> q;
          use_cost[i][j] = q;
      }
  }

  // n constraints for every warehouse i.e x_k*demand_c - capacity_k <= 0
  // m constraints for every client i.e sum_c (x_k * demand_c) = 1
  glp_add_rows(mip, n+m);
  for (int i = 0; i < n; i++) {
      char buff[100];
      snprintf(buff, sizeof(buff), "c_%i", i+1);
      glp_set_row_name(mip, i + 1, buff);
      glp_set_row_bnds(mip, i + 1, GLP_UP, 0.0, 0.0);
  }

  for (int i = n; i < n + m; i++) {
      char buff[100];
      snprintf(buff, sizeof(buff), "c_%i", i+1);
      glp_set_row_name(mip, i + 1, buff);
      glp_set_row_bnds(mip, i + 1, GLP_FX, 1.0, 1.0);
  }


  glp_add_cols(mip, n*m + n);

  for (int i = 0; i < n*m; i++) {
      char buff[100];
      snprintf(buff, sizeof(buff), "x_%i", i+1);
      glp_set_col_name(mip, i + 1, buff);
      glp_set_col_bnds(mip, i + 1, GLP_DB, 0.0, 1.0);
      glp_set_col_kind(mip, i + 1, GLP_CV);
      glp_set_obj_coef(mip, i + 1, use_cost[i / m][i % m]);
  }

  for (int i = n*m; i < n*m + n; i++) {
      char buff[100];
      snprintf(buff, sizeof(buff), "x_%i", i+1);
      glp_set_col_name(mip, i + 1, buff);
      // glp_set_col_bnds(mip, i + 1, GLP_DB, 0.0, 1.0);
      glp_set_col_kind(mip, i + 1, GLP_BV);
      glp_set_obj_coef(mip, i + 1, warehouse[i - n*m][1]);
  }


  int ia[1+n*(m + 1) + m*n], ja[1+n*(m + 1) + m*n];
  double ar[1+n*(m + 1) + m*n];

  int num = 1;
  for (int i = 0; i < n; i++) {
      // std::cout << "c" << i + 1 << ": ";
      for (int j = 0; j < m; j++) {
          ia[num] = i + 1;
          // std::cout << '(' << i + 1 << ' ' << i*m + j + 1 * (i + 1) << ')';
          ja[num] = i*m + j + 1;
          ar[num] = demand[j];
          // std::cout << " + " << '(' << i + 1 << ' ' << i*m + j + 1 << ')' << demand[j] << ' ';
          num++;
      }
      ia[num] = i + 1;
      ja[num] = n*m + i + 1;
      ar[num] = -1 * warehouse[i][0];
      // std::cout << ar[num] << '(' << i + 1 << ' ' << n*m + i + 1 << ')' << '\n';
      // std::cout << i + 1 << ' ' << m * (i + 1) + 1 * (i + 1) << ' ';
      num++;
  }

  for (int i = 0; i < m; i++) {
      // std::cout << "c" << i + n + 1 << ": ";
      for (int j = 0; j < n; j++) {
          ia[num] = i + n + 1;
          // std::cout << i + n + 1 << ' ' << j * m + i + 1 << ' ';
          ja[num] = j * m + i + 1;
          ar[num] = 1;
          // std::cout << " + " << '(' << i + n + 1 << ' ' << j * m + i + 1 << ')' << 1 << ' ';
          num++;
      }
  }

  glp_load_matrix(mip, n*(m + 1) + m*n, ia, ja, ar);

  glp_iocp parm;
  glp_init_iocp(&parm);
  // presolve to ON
  parm.presolve = GLP_ON;
  parm.msg_lev = GLP_MSG_OFF;
  parm.tm_lim = 4700;
  parm.br_tech = GLP_BR_MFV;
  parm.bt_tech = GLP_BT_BFS;
  parm.pp_tech = GLP_PP_ROOT;
  parm.fp_heur = GLP_ON;
  parm.mir_cuts = GLP_ON;
  parm.mip_gap = 0.001;

  glp_intopt(mip, &parm);

  double answ[n*m + n];
  for (int i = 0; i < n*m + n; i++) {
      answ[i] = glp_mip_col_val(mip, i + 1);
  }

  int warehouse_count = 0;
  std::vector<int> indexes;
  for (int i = n*m; i < n*m + n; i++) {
      warehouse_count += answ[i];
      if (answ[i] == 1) {
          indexes.push_back(i - n*m + 1);
      }
  }
  std::cout << warehouse_count << '\n';
  for (auto x: indexes) {
      std::cout << x << ' ';
  }
  std::cout << '\n';
  std::cout.precision(6);
  for (auto x: indexes) {
      for (int i = (x - 1) * m; i < (x - 1) * m + m; i++) {
          std::cout << std::fixed << answ[i] << ' ';
      }
      std::cout << '\n';
  }

  glp_delete_prob(mip);
  return 0;
}
