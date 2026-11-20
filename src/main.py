"""
Punto de entrada único que reproduce todo.
"""

import sys
import verificacion as ver
from fractions import Fraction
from pathlib import Path
from conteo import Contador
from gauss import factorizar, resolver

# Configuración de rutas con pathlib
AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
DATOS = RAIZ / "datos"
DATOS.mkdir(parents=True, exist_ok=True)
RES = RAIZ / "resultados"
RES.mkdir(parents=True, exist_ok=True)

# Configurar el path para importaciones locales
if str(AQUI) not in sys.path:
    sys.path.insert(0, str(AQUI))

# Constantes
EPS = 2.0 ** -52                  # épsilon de máquina (double)
COTA_MINIMA = 1486                # cota de referencia del enunciado (flops)
TOLERANCIA = 0.10                 # ±10 % admitido sobre la cota
CORRIDAS = ("ninguno", "parcial", "parcial_escalado")
PRINCIPAL = "parcial_escalado"    # corrida cuya solución se reporta
PASADAS = 2                       # pasadas de refinamiento iterativo
MAX_DIGITOS = 16                  # un double (53 bits) no garantiza más


def correr(pivoteo, A, b):
    """Una corrida completa: factoriza y resuelve con el MISMO contador."""
    cont = Contador(pivoteo)
    traza = []
    fac = factorizar(A, pivoteo, cont, traza)
    x = resolver(fac, b, cont)
    return {"cont": cont, "traza": traza, "fac": fac, "x": x}

def error_relativo_max(x, x_ref):
    return float(max(abs(Fraction(a) - e) / abs(e) for a, e in zip(x, x_ref)))

#---------------------------------------------------
#----------- Escritura de resultados ---------------
#---------------------------------------------------

def tabla_comparacion(corridas, xe):
    """Tabla de T2: comparación cuantitativa entre corridas."""
    lin = ["| Corrida | Mult. máx. | Crecimiento | Bits absorción "
           "| Bits cancelación | Error relativo máx. | Dígitos correctos (mín.) |",
           "|---|---:|---:|---:|---:|---:|---:|"]
    for nombre in CORRIDAS:
        c = corridas[nombre]
        f = c["fac"]
        digs = ver.digitos_correctos(c["x"], xe)
        lin.append(f"| {nombre} | {f['max_mult']:.3e} | {f['crecimiento']:.3e} "
                   f"| {f['bits_absorcion']:.1f} | {f['bits_cancelacion']:.1f} "
                   f"| {error_relativo_max(c['x'], xe):.2e} | {min(digs):.1f} |")
    return "\n".join(lin)

def escribir_traza(ruta, corridas):
    """Matriz tras cada uno de los 11 pasos, para la corrida principal y la sin pivoteo."""
    with open(ruta, "w", encoding="utf-8") as f:
        f.write("TRAZA DE LA ELIMINACIÓN: matriz U tras cada uno de los 11 pasos\n")
        f.write("Formato: %+.9e. Los ceros bajo la diagonal son exactos.\n")
        for nombre in (PRINCIPAL, "ninguno"):
            c = corridas[nombre]
            fac = c["fac"]
            f.write(f"\n{'=' * 78}\nCORRIDA: {nombre}\n{'=' * 78}\n")
            f.write(f"multiplicador máximo   = {fac['max_mult']:.6e}\n")
            f.write(f"factor de crecimiento  = {fac['crecimiento']:.6e}\n")
            f.write(f"bits de absorción      = {fac['bits_absorcion']:.2f}\n")
            f.write(f"bits de cancelación    = {fac['bits_cancelacion']:.2f}\n")
            for paso, fila_orig, U, res in c["traza"]:
                f.write(f"\n--- Paso {paso}: pivote = {U[paso - 1][paso - 1]:+.6e} "
                        f"(fila original F{fila_orig}); "
                        f"residuo de anulación, máx. acumulado = {res:.3e}\n")
                for fila in U:
                    f.write(" ".join(f"{v:+.9e}" for v in fila) + "\n")

def linea_cota(cont):
    flops = cont.flops()
    dif = (flops - COTA_MINIMA) / COTA_MINIMA * 100
    dentro = abs(dif) <= TOLERANCIA * 100
    return (f"Cota de referencia: {COTA_MINIMA} flops. Conteo medido: {flops} "
            f"({dif:+.1f} %). Dentro de ±{TOLERANCIA * 100:.0f} %: "
            f"{'sí' if dentro else 'no'}.\n")

def escribir_conteo(ruta, corridas):
    with open(ruta, "w", encoding="utf-8") as f:
        f.write("# Conteo de operaciones por paso\n\n")
        f.write("Convención: 1 flop = 1 operación aritmética elemental "
                "(+, -, *, /). Los números salen del contador instrumentado "
                "en el código (conteo.py), no de una fórmula.\n\n")
        f.write("Incluye eliminación, actualización de b y sustitución regresiva. "
                "La búsqueda de pivote, las divisiones del pivoteo escalado y los "
                "intercambios se cuentan aparte (sobrecosto de estabilidad). "
                "No incluye el refinamiento ni la verificación.\n\n")
        for nombre in CORRIDAS:
            c = corridas[nombre]["cont"]
            f.write(c.tabla_markdown() + "\n")
            f.write(linea_cota(c) + "\n")

def escribir_solucion(ruta, x, afirmados):
    """Cada incógnita escrita con exactamente los dígitos que se afirman correctos."""
    with open(ruta, "w", encoding="utf-8") as f:
        f.write("indice,valor,digitos_afirmados\n")
        for i, (v, d) in enumerate(zip(x, afirmados), 1):
            f.write(f"{i},{v:.{d - 1}e},{d}\n")

def escribir_residuo(ruta, r0, r1, hist, x_propia, x_np, kappa, xe):
    lin = [f"VERIFICACIÓN (corrida: {PRINCIPAL})",
           "Residuo r = b - A x en aritmética exacta (fracciones, sin redondeo).",
           "",
           ver.texto_residuo("Residuo ANTES del refinamiento:", r0), "",
           "Refinamiento iterativo:"]
    for k, h in enumerate(hist, 1):
        lin.append(f"  pasada {k}: ||r||_inf antes = {h['norma_r']:.6e}; "
                   f"||d||/||x|| = {h['correccion_rel']:.3e}")
    lin += ["", ver.texto_residuo("Residuo DESPUÉS del refinamiento:", r1), ""]

    cota, dig_cota = ver.cota_error(kappa, EPS)
    lin += ["Condicionamiento:",
            f"  kappa_1(A) estimado (Hager) = {kappa:.4e}",
            f"  cota kappa*eps (eps = 2^-52) = {cota:.3e}",
            f"  dígitos que la cota garantiza = {dig_cota:.2f}", ""]

    if x_np is not None:
        dif = max(abs(a - c) / abs(a) for a, c in zip(x_propia, x_np))
        dig_np = ver.digitos_correctos(x_np, xe)
        lin += ["Control con numpy.linalg.solve (solo contraste):",
                f"  máx. |x_propia - x_numpy| / |x_propia| = {dif:.3e}",
                f"  dígitos correctos de numpy (mín.) = {min(dig_np):.1f}"]
    else:
        lin += ["Control con numpy: no disponible (numpy no instalado)."]

    with open(ruta, "w", encoding="utf-8") as f:
        f.write("\n".join(lin) + "\n")



def main():
    RES.mkdir(parents=True, exist_ok=True)

    # Leer datos como texto; float() solo para el algoritmo en doble precisión.
    A_txt, b_txt = ver.leer_textos(DATOS / "matriz_a.csv", DATOS / "vector_b.csv")
    A = [[float(v) for v in fila] for fila in A_txt]
    b = [float(v) for v in b_txt]
    A_fr, b_fr = ver.a_fracciones(A_txt, b_txt)
    xe = ver.solucion_exacta(A_fr, b_fr)          # referencia exacta

    corridas = {p: correr(p, A, b) for p in CORRIDAS}
    pr = corridas[PRINCIPAL]

    # Verificación de la corrida principal
    r0 = ver.residuo_exacto(A_fr, b_fr, pr["x"])
    x_ref, hist = ver.refinamiento(pr["fac"], A_fr, b_fr, pr["x"], PASADAS)
    r1 = ver.residuo_exacto(A_fr, b_fr, x_ref)
    digs = ver.digitos_correctos(x_ref, xe)
    afirmados = [int(min(d, MAX_DIGITOS)) for d in digs]
    kappa = ver.estimar_kappa1(A, pr["fac"])
    x_np = ver.control_numpy(A, b)

    # Archivos de resultados/
    escribir_solucion(RES / "solucion.csv", x_ref, afirmados)
    escribir_traza(RES / "traza_eliminacion.txt", corridas)
    escribir_conteo(RES / "conteo_flops.md", corridas)
    escribir_residuo(RES / "residuo.txt", r0, r1, hist, pr["x"], x_np, kappa, xe)

    # Resumen por consola
    print(tabla_comparacion(corridas, xe))
    print()
    for p in CORRIDAS:
        print(f"{p:17s} flops = {corridas[p]['cont'].flops()}  "
              f"sobrecosto = {corridas[p]['cont'].sobrecosto()}")
    print(f"\nkappa_1 estimado = {kappa:.4e}")
    print(f"||r||_inf: antes = {float(ver.norma_inf(r0)):.3e}, "
          f"después = {float(ver.norma_inf(r1)):.3e}")
    print(f"dígitos afirmados por incógnita: {afirmados}")
    print(f"\nArchivos escritos en {RES}")


if __name__ == "__main__":
    main()