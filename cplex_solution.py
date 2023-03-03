import docplex.mp.model as cpx

def Cplex_solution(evschedule):
    evschedule.input_cplex()

    V = 9999
    M = 9999
    N = 9999

    opt_model = cpx.Model()

    ### decision variables
    x_ijkc = {(i, j, k, c): opt_model.binary_var(name="x_{0}_{1}_{2}_{3}".format(i, j, k, c)) for i in evschedule.set_M
              for j in
              (evschedule.set_J + [0]) for k in evschedule.set_J if j != k for c in evschedule.set_C}

    c_ij = {(i, j): opt_model.continuous_var(lb=0, ub=opt_model.infinity, name="c_{0}_{1}".format(i, j)) for i in
            evschedule.set_M for j in (evschedule.set_J + [0])}

    s_ij = {(i, j): opt_model.continuous_var(lb=0, ub=opt_model.infinity, name="s_{0}_{1}".format(i, j)) for i in
            evschedule.set_FM for j in evschedule.set_J}

    T_j = {(j): opt_model.continuous_var(lb=0, ub=opt_model.infinity, name = "T_{0}".format(j)) for j in evschedule.set_J}

    ### constraints
    constraint_1 = {k: opt_model.add_constraint(ct=opt_model.sum(
        x_ijkc[i, j, k, c] for j in (evschedule.set_J + [0]) if j != k for i in evschedule.set_M for c in
        evschedule.set_C) == 1,
                                                ctname="constraint_1_{0}".format(k)) for k in evschedule.set_J}

    constraint_2 = {j: opt_model.add_constraint(ct=opt_model.sum(
        x_ijkc[i, j, k, c] for k in evschedule.set_J if j != k for i in evschedule.set_M for c in
        evschedule.set_C) <= 1,
                                                ctname="constraint_2_{0}".format(j)) for j in evschedule.set_J}

    constraint_3 = {i: opt_model.add_constraint(
        ct=opt_model.sum(x_ijkc[i, 0, k, c] for k in evschedule.set_J for c in evschedule.set_C) <= 1,
        ctname="constraint_3_{0}".format(i)) for i in evschedule.set_M}

    constraint_4 = {(i, j, k): opt_model.add_constraint(ct=opt_model.sum(
        x_ijkc[i, h, j, c] for h in (evschedule.set_J + [0]) if (h != k and h != j) for c in
        evschedule.set_C) >= opt_model.sum(x_ijkc[i, j, k, c] for c in evschedule.set_C),
                                                        ctname="constraint_4_{0}_{1}_{2}".format(i, j, k)) for i in
                    evschedule.set_M for j in evschedule.set_J for k in evschedule.set_J if j != k}

    constraint_5 = {(i, j, k): opt_model.add_constraint(
        ct=c_ij[i, k] + V * (1 - opt_model.sum(x_ijkc[i, j, k, c] for c in evschedule.set_C)) >= c_ij[
            i, j] + opt_model.sum(x_ijkc[i, j, k, c] * evschedule.p_jc[k, c] for c in evschedule.set_C) + s_ij[i, k],
        ctname="constraint_5_{0}_{1}_{2}".format(i, j, k)) for i in evschedule.set_FM for j in (evschedule.set_J + [0])
                    for k in evschedule.set_J if j != k}

    constraint_6 = {(i, j, k): opt_model.add_constraint(
        ct=c_ij[i, k] + V * (1 - opt_model.sum(x_ijkc[i, j, k, c] for c in evschedule.set_C)) >= c_ij[
            i, j] + opt_model.sum(
            x_ijkc[i, j, k, c] * (evschedule.p_jc[k, c] + evschedule.t_ijk[i, j, k]) for c in evschedule.set_C),
        ctname="constraint_6_{0}_{1}_{2}".format(i, j, k)) for i in evschedule.set_MM for j in (evschedule.set_J + [0])
                    for k in evschedule.set_J if j != k}

    constraint_7 = {i: opt_model.add_constraint(ct=c_ij[i, 0] == evschedule.r_i[i], ctname="constraint_7_{0}".format(i))
                    for i in evschedule.set_M}

    constraint_8 = {(i, j): opt_model.add_constraint(ct=c_ij[i, j] >= 0, ctname="constraint_8_{0}_{1}".format(i, j)) for
                    i in evschedule.set_M for j in evschedule.set_J}

    constraint_9 = {(i, j, k): opt_model.add_constraint(
        ct=s_ij[i, k] >= -M * (1 - opt_model.sum(x_ijkc[i, j, k, c] for c in evschedule.set_C)) + evschedule.d_ij[
            i, k] - c_ij[i, j],
        ctname="constraint_10_{0}_{1}_{2}".format(i, j, k)) for i in evschedule.set_FM for j in (evschedule.set_J + [0])
                     for k in evschedule.set_J if j != k}

    constraint_10 = {(i, k): opt_model.add_constraint(ct=c_ij[i, k] <= N * opt_model.sum(
        x_ijkc[i, j, k, c] for c in evschedule.set_C for j in (evschedule.set_J + [0]) if j != k),
                                                      ctname="constraint_11_{0}_{1}".format(i, k)) for i in
                     evschedule.set_M for k in evschedule.set_J}

    # 이동형 충전소 충전 용량 제한
    constraint_11 = {i: opt_model.add_constraint(ct=opt_model.sum(
        x_ijkc[i, j, k, c] * evschedule.chg_j[k] for j in evschedule.set_J + [0] for k in evschedule.set_J if j != k
        for c in evschedule.set_C) <= evschedule.Mmcapa,
                                                 ctname="constraint_12_{0}_{1}".format(i,c)) for i in evschedule.set_MM for c in evschedule.set_C}

    # Tardiness
    constraint_13 = {(i,j): opt_model.add_constraint(ct=c_ij[i,j]-evschedule.d_j[j] <= T_j[j]) for i in evschedule.set_M for j in evschedule.set_J}

    constraint_14 = {j: opt_model.add_constraint(ct=T_j[j] >= 0) for j in evschedule.set_J}


    ### objective
    objective_A = opt_model.sum(
        evschedule.cost[c] * x_ijkc[i, j, k, c] * evschedule.chg_j[k] for i in evschedule.set_M for j in
        evschedule.set_J + [0] for k in evschedule.set_J if j != k for c in evschedule.set_C)

    objective_B = evschedule.delay_cost * opt_model.sum(T_j[j] for j in evschedule.set_J)

    a = 0.5
    b = 0.5

    # for minimization
    opt_model.minimize(a * objective_A + b * objective_B)

    opt_model.set_time_limit(10)  # 시간 제한 : 1시간
    opt_model.solve()

    return opt_model
