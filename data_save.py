import pickle

def pickle_wb(info_list, i: int):
    with open("data.pickle {}".format(i), "wb") as f:
        pickle.dump(info_list[0], f) # distance
        pickle.dump(info_list[1], f) # proc
        pickle.dump(info_list[2], f) # ready
        pickle.dump(info_list[3], f) # mchm_list

def pickle_rb(i: int):
    with open("data.pickle {}".format(i),"rb") as fr:
        data_dist = pickle.load(fr)
        data_proc = pickle.load(fr)
        data_ready = pickle.load(fr)
        data_ml = pickle.load(fr)
        loc = pickle.load(fr)
        proc_full = pickle.load(fr)
        proc_pre = pickle.load(fr)

    data_list = [data_dist, data_proc, data_ready, data_ml, loc, proc_full, proc_pre]
    return data_list

def pickle_res_wb(cplex_sol, cp_sol, cplex_time, cp_time, i): # 결과 저장 > 최적해, 시간
    with open("data.pickle_res {}".format(i), "wb") as f:
        pickle.dump(cplex_sol, f)
        pickle.dump(cp_sol, f)
        pickle.dump(cplex_time, f)
        pickle.dump(cp_time, f)

def pickle_res_rb(i: int):
    with open("data.pickle_res {}".format(i),"rb") as fr:
        cplex_sol = pickle.load(fr)
        cp_sol = pickle.load(fr)
        cplex_time = pickle.load(fr)
        cp_time = pickle.load(fr)

    res_list = [cplex_sol, cp_sol, cplex_time, cp_time]
    return res_list




