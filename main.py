from input import *
from cplex_solution import *
from cp_solution import *
from get_distance import *
import pandas as pd
import numpy as np
from data_save import *

def main():

    df = pd.DataFrame({'Job_n': [],
                       'Cplex_sol': [],
                       'Cp_sol': [],
                       'cplex_time': [],
                       'Cp_time': [],
                       'Cplex_status': [],
                       'Cp_status': []
                       })

    row = 0

    for i in range(1,5,100):

        example = Input(Job_n=i, Mchf_n=5, Mchm_n=5)

        ### user input ###
        # info_list = pickle_rb(i)
        # duedate = [1] * i
        # example.user_input(distance, chg, ready, mchm_list, duedate)
        # example.user_input(info_list[0], info_list[6], info_list[2], info_list[3], duedate)

        ### random input ###
        example.random_input()

        ### example input ###
        # example.ex_input()

        # CP optimizer

        cp_opt = Cp_solution(example)
        cp_opt.print_solution()

        cp_sol = Cp_descaler(cp_opt.solution.objective_values[0]) if cp_opt.solve_status == 'Feasible' or cp_opt.solve_status == 'Optimal' else cp_opt.solve_status
        cp_time = cp_opt.solveTime
        cp_status = cp_opt.solve_status

        # MILP optimizer

        cplex_opt = Cplex_solution(example)
        cplex_sol = cplex_opt.objective_value if cplex_opt.solve_status.name in ['OPTIMAL_SOLUTION','FEASIBLE_SOLUTION'] else cplex_opt.solve_status
        cplex_time = cplex_opt.solve_details.time if cplex_opt.solve_status.name in ['OPTIMAL_SOLUTION','FEASIBLE_SOLUTION'] else cplex_opt.solve_status
        cplex_status = cplex_opt.solve_status.name

        print('({}) cp value: {}'.format(i, cp_sol))
        print('cp status: {}'.format(cp_status))
        print('cplex value: {}'.format(cplex_sol))
        print('cplex status: {}'.format(cplex_status))

        df.loc[row] = [i, cplex_sol, cp_sol, cplex_time, cp_time, cplex_status, cp_status]
        pickle_res_wb(cplex_sol, cp_sol, cplex_time, cp_time, i)

        row += 1

        # 결과 csv 저장
    df.to_csv('ny_result_1.csv', index=False)

if (__name__ == "__main__"):
    main()