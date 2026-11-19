"""
Punto de entrada único que reproduce todo.
"""

from pathlib import Path
import sys

import verificacion as ver

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
EPS = 2.0 ** -52                              # épsilon de máquina (double)
COTA_MINIMA = 1486


def main():
    # Leer datos y pasarlos de str a float.
    A_txt, b_txt = ver.leer_textos(DATOS / "matriz_a.csv",
                                   DATOS / "vector_b.csv")
    A = [[float(v) for v in fila] for fila in A_txt]
    b = [float(v) for v in b_txt]

    # solucion.csv: incógnitas con todos los dígitos reportados.
    f = open(DATOS / 'solucion.csv', 'w', encoding='utf-8')

    f.close()

    # traza_eliminacion.txt: matriz tras cada uno de los 11 pasos.
    f = open(DATOS / 'traza_eliminacion.txt', 'w', encoding='utf-8')
    
    f.close()

    # conteo_flops.md: tabla de operaciones por paso.
    f = open(DATOS / 'conteo_flops.md', 'w', encoding='utf-8')
    
    f.close()

    # residuo.txt: r y su norma infinito.
    f = open(DATOS / 'residuo.txt', 'w', encoding='utf-8')
    
    f.close()


if __name__ == "__main__":
    main()