
def Cp_scaler(origin_var, n = 5): # n: 소수 몇째 자리부터 반올림할건지
    # 소수 n 자리 이하 반올림
    a = round(origin_var, n)
    multi_var = int(a * (10**n))
    # 뻥튀기 한 정수 반환
    return multi_var

def Cp_descaler(multi_var, n = 5): # n: 소수 몇째 자리부터 반올림할건지
    return multi_var/ (10**n)