import docplex.mp.model as cpx
from docplex.cp.model import *
import random
from cp_scaler import *
from get_distance import *
import pandas as pd
import numpy as np

class Input:

    # Set and indices
    def __init__(self, Job_n, Mchf_n, Mchm_n, Chg_n = 2):
        self.Job_n = Job_n
        self.Mchf_n = Mchf_n # 고정식 충전소 개수
        self.Mchm_n = Mchm_n # 이동식 충전소 개수
        self.Mch_n = Mchf_n + Mchm_n # 총 충전소 개수
        self.Chg_n = Chg_n

    # Parameter
    def user_input(self, distance, chg, ready, mchm_list, duedate, Mmcapa=80, Cost = [0.15, 0.07], Delay_cost=15, Velo=[50,6]):
        self.velo = Velo
        self.Mmcapa = Mmcapa
        self.cost = Cost
        self.delay_cost = Delay_cost

        self.distance = np.round(distance,5)
        self.chg = np.round(chg,5)

        li = [[0 for c in range(self.Chg_n)] for j in range(self.Job_n)]

        for j in range(self.Job_n):
            for c in range(self.Chg_n):
                li[j][c] = self.chg[j] / self.velo[c]

        self.proc = li

        self.ready = np.round(ready,5)
        self.mchm_list = np.round(mchm_list,5)
        self.duedate = np.round(duedate,5)


    def random_input(self):
        # 충전 속도
        self.velo = [50, 6]
        # 이동형 충전소 충전용량
        self.Mmcapa = 80
        # 충전 비용
        self.cost = [0.15,0.07]
        # Delayed Cost
        self.delay_cost = 15

        ### distance : job j와 machine i 사이의 거리 (단위: 시간)
        self.distance = [[np.round(random.uniform(0.01, 0.33),5) for j in range(self.Job_n)] for i in range(self.Mchf_n+self.Mchm_n)]

        ### charging amount
        self.chg = [np.round(random.uniform(1,90),5) for j in range(self.Job_n)]

        ### processing time
        li = [[0 for c in range(self.Chg_n)] for j in range(self.Job_n)]

        for j in range(self.Job_n):
            for c in range(self.Chg_n):
                li[j][c] = self.chg[j] / self.velo[c]

        self.proc = li

        ### ready time : machine i 의 ready time (충전중인 차가 있는 경우)
        self.ready = [np.round(random.uniform(0, 2),5) for i in range(self.Mch_n)]

        ### duedate
        # self.duedate = [np.round(random.uniform(0,100),5) for j in range(self.Job_n)]
        self.duedate = [2 for j in range(self.Job_n)]

        ### mchm_list: job 간 거리 (setup time)
        self.mchm_list = [[[0 for k in range(self.Job_n + 1)] for j in range(self.Job_n + 1)] for i in
                          range(self.Mchm_n)]

        for i in range(self.Mchm_n):
            for j in range(self.Job_n + 1):
                for k in range(self.Job_n + 1):
                    if j != k:
                        if j == 0:
                            self.mchm_list[i][j][k] = self.distance[i - self.Mchf_n][k-1]
                        elif k == 0:
                            self.mchm_list[i][j][k] = -1
                        elif k > j:
                            self.mchm_list[i][j][k] = np.round(random.uniform(1, 0.33),5)
                            self.mchm_list[i][k][j] = self.mchm_list[i][j][k]


    def ex_input(self):
        # 충전 속도
        self.velo = [50, 6]
        # 이동형 충전소 충전용량
        self.Mmcapa = 80
        # 충전 비용
        self.cost = [0.15,0.07]
        # Delayed Cost
        self.delay_cost = 1

        ### distance : job j와 machine i 사이의 거리 (단위: 시간)
        self.distance = [[1,2,1],[1,1,3]]

        ### charging amount
        self.chg = [20,80,30]

        ### processing time
        li = [[0 for c in range(self.Chg_n)] for j in range(self.Job_n)]

        for j in range(self.Job_n):
            for c in range(self.Chg_n):
                li[j][c] = self.chg[j] / self.velo[c]

        self.proc = li

        ### ready time : machine i 의 ready time (충전중인 차가 있는 경우)
        self.ready = [0,0]

        ### duedate
        # self.duedate = [np.round(random.uniform(0,100),5) for j in range(self.Job_n)]
        self.duedate = [1,1,1]

        ### mchm_list: job 간 거리 (setup time)
        self.mchm_list = [[[0,1,1,3],[-1,0,2,1],[-1,2,0,2],[-1,1,3,0]]]


    def input_cplex(self): # input을 cplex에 필요한 형태로 바꾸기
        # job (j)
        self.set_J = [(i + 1) for i in range(self.Job_n)]

        # machine (i)
        self.set_FM = [(i + 1) for i in range(self.Mchf_n)]
        self.set_MM = [(self.Mchf_n + i + 1) for i in range(self.Mchm_n)]
        self.set_M = self.set_FM + self.set_MM

        # charging type (c)
        self.set_C = [i for i in range(self.Chg_n)]

        # distance
        self.d_ij = {(i, j): self.distance[i-1][j-1] for i in self.set_M for j in self.set_J}

        # charging amount
        self.chg_j = {(j): self.chg[j-1] for j in self.set_J}

        # charging velocity
        self.velo_c = {(c): self.velo[c] for c in self.set_C}

        # processing time
        self.p_jc = {(j,c): self.proc[j-1][c] for j in self.set_J for c in self.set_C}

        # ready time
        self.r_i = {i: self.ready[i-1] for i in self.set_M}

        # time between job
        self.t_ijk = {(i, j, k): self.mchm_list[i - self.Mchf_n - 1][j][k] for i in self.set_MM for j in self.set_J + [0] for k in self.set_J if k != j}

        # due date
        self.d_j = {j: self.duedate[j-1] for j in self.set_J}

    def input_cp(self): # input을 cp에 필요한 형태로 바꾸기
        # Scaling: 실수 -> 정수
        self.distance_cp = [[Cp_scaler(self.distance[i][j]) for j in range(self.Job_n)] for i in range(self.Mchf_n+self.Mchm_n)]
        self.chg_cp = [Cp_scaler(self.chg[j]) for j in range(self.Job_n)]
        self.proc_cp = [[Cp_scaler(self.proc[j][c]) for c in range(self.Chg_n)] for j in range(self.Job_n)]
        self.ready_cp = [Cp_scaler(self.ready[i]) for i in range(self.Mch_n)]
        self.Mmcapa_cp = Cp_scaler(self.Mmcapa)
        self.duedate_cp = [Cp_scaler(self.duedate[j]) for j in range(self.Job_n)]
        self.cost_cp = [Cp_scaler(self.cost[c]) for c in range(self.Chg_n)]

        # task type : 각 job은 모두 다른 type ( +1: dummy job(ready time) )
        self.task_type = [ i for i in range( self.Job_n * self.Chg_n + 1 ) ]

        # dummy job 포함 job 개수 ( 충전 타입 포함 )
        self.nb_tasks = len(self.task_type)

        # 급속, 완속 둘 다 있는거
        self.task_dur = [self.ready_cp if i == 0 else self.proc_cp[i-1] for i in range(self.Job_n+1)]

        # 이동식 충전소 set time
        self.mchm_list_cp = [[[0 for k in range(self.nb_tasks)] for j in range(self.nb_tasks)] for i in
                         range(self.Mchm_n)]

        for i in range(self.Mchm_n):
            for j in range(self.nb_tasks):  # job_n + 1
                for k in range(self.nb_tasks):
                    if self.mchm_list[i][(j + self.Chg_n - 1)//self.Chg_n][(k + self.Chg_n - 1)//self.Chg_n] == -1:
                        self.mchm_list_cp[i][j][k] = INTERVAL_MAX
                    else:
                        self.mchm_list_cp[i][j][k] = Cp_scaler(self.mchm_list[i][(j + self.Chg_n - 1)//self.Chg_n][(k + self.Chg_n - 1)//self.Chg_n])

        # 고정식 충전소의 machine 별 setup time : job j -> k
        self.set_time = [[[0 for k in range(self.nb_tasks)] for j in range(self.nb_tasks)] for i in
                         range(self.Mchf_n)]

        for i in range(self.Mchf_n):
            for j in range(self.nb_tasks):
                for k in range(self.nb_tasks):
                    if k == 0:
                        self.set_time[i][j][k] = INTERVAL_MAX
                    elif j == 0:
                        # 맨 처음 job은 ready time 만 고려하면 됨 -> ready - distance
                        self.set_time[i][j][k] = max(0, self.distance_cp[i][(k+self.Chg_n-1)//self.Chg_n-1] - self.ready_cp[i])
                    elif (j + self.Chg_n - 1) // self.Chg_n != (k + self.Chg_n - 1) // self.Chg_n: # 서로 다른 job 일때
                                self.set_time[i][j][k] = max(0, self.distance_cp[i][
                                    (k + self.Chg_n - 1) // self.Chg_n - 1] - max(
                                    self.distance_cp[i][(j + self.Chg_n - 1) // self.Chg_n - 1],
                                    self.ready_cp[i]) - self.task_dur[(j + self.Chg_n - 1) // self.Chg_n][(j+1)%2])




