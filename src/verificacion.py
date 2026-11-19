"""
Residuo en precisión extendida y refinamiento:
•	Residuo r = b − Ax calculado en precisión extendida (decimal, mpmath o fractions), con la norma infinito reportada.
•	Un refinamiento iterativo (al menos una pasada) mostrando la mejora o su ausencia.
•	Contraste contra una rutina de biblioteca (numpy.linalg.solve, scipy) solo como control: no sustituye la implementación propia.
"""

def leer_textos(ruta_a, ruta_b):
    f_a = open(ruta_a, encoding="utf-8")
    A_txt = [l.strip().split(",") for l in f_a if l.strip()]
    f_a.close()

    f_b = open(ruta_b, encoding="utf-8")
    b_txt = [l.strip() for l in f_b if l.strip()]
    f_b.close()

    return A_txt, b_txt