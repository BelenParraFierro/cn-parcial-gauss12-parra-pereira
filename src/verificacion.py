"""
Verificación independiente (T4): residuo calculado en precisión extendida,
refinamiento iterativo y contraste contra numpy (solo como control).

Todo se calcula con fracciones exactas (con fractions.Fraction) a partir de los
textos de los CSV, por lo que ningun dato de entrada se trunca ni se redondea.
"""

import math
from fractions import Fraction

from gauss import resolver_sin_contar, resolver_transpuesta


def leer_textos(ruta_a, ruta_b):
    f_a = open(ruta_a, encoding="utf-8")
    A_txt = [l.strip().split(",") for l in f_a if l.strip()]
    f_a.close()

    f_b = open(ruta_b, encoding="utf-8")
    b_txt = [l.strip() for l in f_b if l.strip()]
    f_b.close()

    return A_txt, b_txt

def a_fracciones(A_txt, b_txt):
    """Textos de los CSV -> fracciones exactas (sin pasar nunca por float)."""
    A = [[Fraction(v) for v in fila] for fila in A_txt]
    b = [Fraction(v) for v in b_txt]
    return A, b


def norma_inf(v):
    return max(abs(t) for t in v)

def residuo_exacto(A_fr, b_fr, x):
    """r = b - A x en aritmetica exacta."""
    n = len(b_fr)
    xf = [Fraction(v) for v in x]
    r = []
    for i in range(n):
        s = Fraction(0)
        for j in range(n):
            s += A_fr[i][j] * xf[j]
        r.append(b_fr[i] - s)
    return r

def refinamiento(fac, A_fr, b_fr, x, pasadas=1):
    """
    Refinamiento iterativo. En cada pasada:
        r = b - A x
        d = resolver(LU, r)
        x = x + d
    Devuelve x_final e historial.
    """
    historial = []
    for _ in range(pasadas):
        r = residuo_exacto(A_fr, b_fr, x)
        d = resolver_sin_contar(fac, [float(t) for t in r])
        correccion_rel = norma_inf(d) / norma_inf(x)
        x = [xi + di for xi, di in zip(x, d)]
        historial.append({"norma_r": float(norma_inf(r)),
                          "correccion_rel": correccion_rel})
    return x, historial

def solucion_exacta(A_fr, b_fr):
    """
    Referencia: eliminación gaussiana con fracciones. No hay redondeo, así que
    cualquier pivote no nulo sirve.
    """
    n = len(b_fr)
    M = [fila[:] + [b_fr[i]] for i, fila in enumerate(A_fr)]
    for k in range(n):
        p = next(i for i in range(k, n) if M[i][k] != 0)
        M[k], M[p] = M[p], M[k]
        for i in range(k + 1, n):
            m = M[i][k] / M[k][k]
            for j in range(k, n + 1):
                M[i][j] -= m * M[k][j]
    x = [Fraction(0)] * n
    for i in range(n - 1, -1, -1):
        s = M[i][n] - sum(M[i][j] * x[j] for j in range(i + 1, n))
        x[i] = s / M[i][i]
    return x

def digitos_correctos(x, x_ref):
    """Digitos significativos correctos de cada x[i]: -log10(error relativo)."""
    out = []
    for a, e in zip(x, x_ref):
        dif = abs(Fraction(a) - e)
        out.append(math.inf if dif == 0 else -math.log10(float(dif / abs(e))))
    return out


def control_numpy(A, b):
    """Solo como control."""
    try:
        import numpy as np
    except ImportError:
        return None
    return [float(v) for v in np.linalg.solve(np.array(A), np.array(b))]


def texto_residuo(titulo, r):
    """Líneas para residuo.txt: cada componente de r y su norma infinito."""
    lin = [titulo]
    for i, v in enumerate(r, 1):
        lin.append(f"  r[{i:2d}] = {float(v):+.6e}")
    lin.append(f"  ||r||_inf = {float(norma_inf(r)):.6e}")
    return "\n".join(lin)

#---------------------------------------------------
#----------- Condicionamiento ----------------------
#---------------------------------------------------

def norma1_matriz(A):
    """||A||_1 = mayor suma de |a_ij| por columna."""
    n = len(A)
    return max(sum(abs(A[i][j]) for i in range(n)) for j in range(n))

def estimar_norma1_inversa(fac, max_iter=5):
    """Estima ||A^-1||_1 sin calcular la inversa (método de Hager)."""
    n = len(fac["U"])
    x = [1.0 / n] * n
    est = 0.0
    j_ant = None
    for _ in range(max_iter):
        y = resolver_sin_contar(fac, x)               # y = A^-1 x
        est = max(est, sum(abs(v) for v in y))
        s = [1.0 if v >= 0 else -1.0 for v in y]
        z = resolver_transpuesta(fac, s)              # z = A^-T s
        j = max(range(n), key=lambda i: abs(z[i]))
        if abs(z[j]) <= sum(zi * xi for zi, xi in zip(z, x)) or j == j_ant:
            break
        x = [0.0] * n
        x[j] = 1.0
        j_ant = j
    # Vector alternante de Higham, por si Hager se estanca
    alt = [(-1) ** i * (1.0 + i / (n - 1)) for i in range(n)]
    y = resolver_sin_contar(fac, alt)
    return max(est, 2.0 * sum(abs(v) for v in y) / (3.0 * n))


def estimar_kappa1(A, fac):
    """kappa_1(A) ~ ||A||_1 * ||A^-1||_1 (estimado)."""
    return norma1_matriz(A) * estimar_norma1_inversa(fac)


def cota_error(kappa, eps):
    """Cota kappa*eps y los dígitos que garantiza."""
    cota = kappa * eps
    return cota, -math.log10(cota)


def casi_dependencia(A, i, j, k):
    """Ajusta fila_i ~ a*fila_j + c*fila_k (mínimos cuadrados).
    Devuelve (a, c, error relativo). Índices desde 0."""
    fi, fj, fk = A[i], A[j], A[k]
    pjj = sum(v * v for v in fj)
    pkk = sum(v * v for v in fk)
    pjk = sum(u * v for u, v in zip(fj, fk))
    bj = sum(u * v for u, v in zip(fi, fj))
    bk = sum(u * v for u, v in zip(fi, fk))
    det = pjj * pkk - pjk * pjk
    a = (bj * pkk - bk * pjk) / det
    c = (pjj * bk - pjk * bj) / det
    res = math.sqrt(sum((u - a * v - c * w) ** 2 for u, v, w in zip(fi, fj, fk)))
    return a, c, res / math.sqrt(sum(v * v for v in fi))