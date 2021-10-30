import sympy

e = 315313
N = 402047

for i in range(1, N, 2):
    if sympy.isprime(i) and N % i == 0:
        p = i
        q = N//i
        d = pow(e,-1,(p-1)*(q-1))
        print(d)
        break

