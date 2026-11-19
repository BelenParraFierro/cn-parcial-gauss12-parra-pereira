"""
Eliminación: con y sin pivoteo, contador de flops:

Para resolver Ax = b, el archivo hace dos cosas por separado:
1. factorizar: descompone A en PA = LU.
    P es la matriz de permutación, o sea qué filas se intercambiaron.
    L es triangular inferior con unos en la diagonal y guarda los multiplicadores.
    U es triangular superior: es la matriz ya eliminada.
2. resolver: con L, U y P ya calculados, saca x para cualquier b sin volver a factorizar.
"""

import math

PIVOTEOS = ("ninguno", "parcial", "parcial_escalado")


def factorizar(A, pivoteo, cont, traza=None):
    """
    Devuelve dict con L, U, perm y estadísticas de mantisa.
    """
    if pivoteo not in PIVOTEOS:
        raise ValueError(pivoteo)
    n = len(A)
    U = [fila[:] for fila in A]
    L = [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
    perm = list(range(n))
    max_A = max(abs(v) for fila in A for v in fila)
    max_hist = max_A
    max_mult = 0.0
    bits_absorcion = 0.0     # peor pérdida por alineamiento de exponentes
    bits_cancelacion = 0.0   # peor cancelación en una resta
    pivotes = []
    residuo_anulacion = 0.0  # mayor |a(i,k) - m*a(k,k)| antes de fijar el 0

    escala = None
    if pivoteo == "parcial_escalado":
        cont.fase("escalas")
        escala = []
        for i in range(n):            # s_i = max_j |a_ij| (una vez, al inicio)
            s = abs(U[i][0])
            for j in range(1, n):
                cont.suma("comparaciones")
                if abs(U[i][j]) > s:
                    s = abs(U[i][j])
            escala.append(s)

    for k in range(n - 1):
        cont.fase(f"paso {k + 1}")
        # elección de pivote
        p = k
        if pivoteo == "parcial":
            mejor = abs(U[k][k])
            for i in range(k + 1, n):
                cont.suma("comparaciones")
                if abs(U[i][k]) > mejor:
                    mejor, p = abs(U[i][k]), i
        elif pivoteo == "parcial_escalado":
            mejor = abs(U[k][k]) / escala[k]
            cont.suma("div_pivoteo")
            for i in range(k + 1, n):
                r = abs(U[i][k]) / escala[i]
                cont.suma("div_pivoteo")
                cont.suma("comparaciones")
                if r > mejor:
                    mejor, p = r, i
        if p != k:
            cont.suma("intercambios")
            U[k], U[p] = U[p], U[k]
            perm[k], perm[p] = perm[p], perm[k]
            if escala is not None:
                escala[k], escala[p] = escala[p], escala[k]
            for j in range(k):                       # multiplicadores ya guardados
                L[k][j], L[p][j] = L[p][j], L[k][j]
        piv = U[k][k]
        if piv == 0.0:
            raise ZeroDivisionError(f"pivote nulo en paso {k + 1}")
        pivotes.append((k + 1, perm[k] + 1, piv))

        # eliminación
        filak = U[k]
        for i in range(k + 1, n):
            filai = U[i]
            m = filai[k] / piv
            cont.suma("div_mult")
            L[i][k] = m
            max_mult = max(max_mult, abs(m))
            for j in range(k, n):                     # barrido desde la columna k
                prod = m * filak[j]
                cont.suma("mult_A")
                viejo = filai[j]
                nuevo = viejo - prod
                cont.suma("res_A")
                filai[j] = nuevo
                if j == k:                            # columna que se anula
                    residuo_anulacion = max(residuo_anulacion, abs(nuevo))
                    filai[k] = 0.0                    # cero exacto en U
                    continue
                # diagnóstico de mantisa (no son flops del algoritmo)
                if viejo != 0.0 and abs(prod) > abs(viejo):
                    bits_absorcion = max(bits_absorcion,
                                         math.log2(abs(prod) / abs(viejo)))
                mayor = max(abs(prod), abs(viejo))
                if nuevo != 0.0 and mayor > abs(nuevo):
                    bits_cancelacion = max(bits_cancelacion,
                                           math.log2(mayor / abs(nuevo)))
                if abs(nuevo) > max_hist:
                    max_hist = abs(nuevo)
        if traza is not None:
            traza.append((k + 1, perm[k] + 1, [f[:] for f in U], residuo_anulacion))

    if U[n - 1][n - 1] == 0.0:
        raise ZeroDivisionError("pivote nulo en el último paso")
    pivotes.append((n, perm[n - 1] + 1, U[n - 1][n - 1]))
    return {
        "L": L, "U": U, "perm": perm, "pivotes": pivotes,
        "max_mult": max_mult,
        "crecimiento": max_hist / max_A,
        "bits_absorcion": bits_absorcion,
        "bits_cancelacion": bits_cancelacion,
        "residuo_anulacion": residuo_anulacion,
    }


def resolver(fac, b, cont):
    """Resuelve Ax = b reutilizando PA = LU (sin refactorizar)."""
    L, U, perm = fac["L"], fac["U"], fac["perm"]
    n = len(b)
    y = [b[perm[i]] for i in range(n)]
    # Actualización de b (sustitución progresiva con L unitaria), por pasos k
    for k in range(n - 1):
        cont.fase(f"paso {k + 1}")
        yk = y[k]
        for i in range(k + 1, n):
            prod = L[i][k] * yk
            cont.suma("mult_b")
            y[i] = y[i] - prod
            cont.suma("res_b")
    # Sustitución regresiva
    cont.fase("sust. regresiva")
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        s = y[i]
        for j in range(i + 1, n):
            prod = U[i][j] * x[j]
            cont.suma("mult_sust")
            s = s - prod
            cont.suma("res_sust")
        x[i] = s / U[i][i]
        cont.suma("div_sust")
    return x


def resolver_transpuesta(fac, c):
    """Resuelve A^T z = c con los mismos factores (sólo para estimar κ)."""
    L, U, perm = fac["L"], fac["U"], fac["perm"]
    n = len(c)
    w = [0.0] * n
    for i in range(n):                     # U^T w = c
        s = c[i]
        for j in range(i):
            s -= U[j][i] * w[j]
        w[i] = s / U[i][i]
    u = [0.0] * n
    for i in range(n - 1, -1, -1):         # L^T u = w
        s = w[i]
        for j in range(i + 1, n):
            s -= L[j][i] * u[j]
        u[i] = s
    z = [0.0] * n
    for i in range(n):                     # z = P^T u
        z[perm[i]] = u[i]
    return z


def resolver_sin_contar(fac, b):
    """Misma solución que resolver(), sin instrumentación (refinamiento / κ)."""
    from conteo import Contador
    return resolver(fac, b, Contador("auxiliar"))
