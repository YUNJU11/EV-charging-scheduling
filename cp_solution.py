from docplex.cp.model import *

def Cp_solution(evschedule):
    evschedule.input_cp()

    mdl = CpoModel()

    tasks_m = []

    for i in range(evschedule.Mch_n):
        tasks_mm = [] # 각 machine의 Job들
        for j in range(evschedule.Job_n + 1): # +1: dummy job(ready time)
            if j == 0:  # ready time(dummy job) 추가
                t = interval_var(name='M{}_J{}'.format(i, j), optional=True, size=evschedule.task_dur[j][i])
                tasks_mm.append(t)
            else:
                for k in range(evschedule.Chg_n):
                    t = interval_var(name='M{}_J{}_C{}'.format(i, j, k), optional=True, size=evschedule.task_dur[j][k])
                    tasks_mm.append(t)
        tasks_m.append(tasks_mm)


    # tasks = [interval_var(name='J{}'.format(i)) for i in range(evschedule.nb_tasks)]
    tasks = [interval_var(name='J{}'.format(i)) for i in range(evschedule.Job_n+1)]

    # 각 job은 하나의 machine에서만 실행 (J0 제외: dummy job은 모든 machine에 추가되어야 함)
    mdl.add(alternative(tasks[i + 1], [row[(i + 1) * evschedule.Chg_n - c] for c in range(evschedule.Chg_n) for row in tasks_m]) for i in range(evschedule.Job_n))

    # j 하나씩은 적어도 선택
    for j in range(evschedule.Job_n):
        mdl.add(equal(sum([presence_of(tasks_m[i][(j+1)*evschedule.Chg_n - c]) for c in range(evschedule.Chg_n) for i in range(evschedule.Mch_n)]) , 1))

    # 모든 machine에 dummy job 존재
    mdl.add(equal(presence_of(tasks_m[i][0]), 1) for i in range(evschedule.Mch_n))

    # 이동식 충전소 충전 용량 제한
    for i in range(evschedule.Mchm_n):
        mdl.add(less_or_equal(
            sum([times(presence_of(tasks_m[evschedule.Mchf_n + i][j]),
                       evschedule.chg_cp[(j + 1) // evschedule.Chg_n - 1]) for j in range(1, evschedule.nb_tasks)]),
            evschedule.Mmcapa_cp))


    # setup time
    seq_var = []

    for i in range(evschedule.Mch_n):
        s = sequence_var(tasks_m[i], types=evschedule.task_type, name='M{}'.format(i))
        seq_var.append(s)

    # 이동식 충전소 setup time
    mdl.add(no_overlap(seq_var[evschedule.Mchf_n + i], evschedule.mchm_list_cp[i], 1) for i in range(evschedule.Mchm_n))

    # 고정식 충전소 setup time
    mdl.add(no_overlap(seq_var[i], evschedule.set_time[i], 1) for i in range(evschedule.Mchf_n))

    # 모든 machine의 seq 맨 앞 : dummy job
    mdl.add(first(seq_var[i], tasks_m[i][0]))

    objective_A = sum(
        [times(times(presence_of(tasks_m[i][j]), evschedule.cost[(j + evschedule.Chg_n - 1) % evschedule.Chg_n]),
               evschedule.chg_cp[(j - 1) // evschedule.Chg_n]) for j
         in range(1, evschedule.nb_tasks) for i in range(evschedule.Mch_n)])


    # tardiness
    T_j = [max([minus(end_of(tasks[j+1]), evschedule.duedate_cp[j]), 0]) for j in range(evschedule.Job_n)]
    objective_B = times(evschedule.delay_cost, sum( T_j ))

    a = 0.5
    b = 0.5

    mdl.add(minimize(a * objective_A + b * objective_B))

    res = mdl.solve(FailLimit=10000, TimeLimit=10)

    return res



