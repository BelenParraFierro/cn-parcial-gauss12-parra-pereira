# cn-parcial-gauss12-parra-pereira

Este repositorio resuelve un sistema lineal denso de 12×12 mal condicionado con eliminación gaussiana propia: costo mínimo instrumentado, pivoteo parcial escalado y verificación en precisión extendida.

## Autoría

Belén Parra Fierro · Cristóbal Pereira Saez · Computación Numérica (INF-321) · Ingeniería Civil Informática, Universidad Católica del Maule · Noviembre 2026

## Requisitos

- Python 3.10 o superior (probado en 3.14)
- Dependencias con versión fija:

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Ejecución

```bash
python src/main.py
```

Se demora menos de 1 segundo y regenera:

| Archivo                              | Contenido                                                         |
| ------------------------------------ | ----------------------------------------------------------------- |
| `resultados/solucion.csv`          | 12 incógnitas con 16 dígitos y los dígitos afirmados           |
| `resultados/traza_eliminacion.txt` | Matriz tras cada uno de los 11 pasos (con y sin pivoteo)          |
| `resultados/conteo_flops.md`       | Operaciones por paso para las tres corridas                       |
| `resultados/residuo.txt`           | r = b − Ax exacto, ‖r‖∞, refinamiento, κ₁(A), control numpy |

## Estructura

```
cn-parcial-gauss12-parra-pereira/
├─ readme.md                 # tarjeta de presentación y cómo ejecutar
├─ informe.md                # informe técnico y análisis de error
├─ requirements.txt          # dependencias con versión fija
├─ datos/
│  ├─ matriz_a.csv           # A densa, 12x12, 144 valores sin truncar
│  └─ vector_b.csv           # b con los 20 dígitos entregados
├─ src/
│  ├─ gauss.py               # eliminación: con y sin pivoteo, contador de flops
│  ├─ conteo.py              # instrumentación y reporte del costo operacional
│  ├─ verificacion.py        # residuo en precisión extendida y refinamiento
│  └─ main.py                # punto de entrada único que reproduce todo
├─ resultados/
│  ├─ solucion.csv           # incógnitas con todos los dígitos reportados
│  ├─ traza_eliminacion.txt  # matriz tras cada uno de los 11 pasos
│  ├─ conteo_flops.md        # tabla de operaciones por paso
│  └─ residuo.txt            # r y su norma infinito
└─ .gitignore
```

## Resultado resumido

| i | xᵢ (10 dígitos) |  | i  | xᵢ (10 dígitos) |
| - | ----------------: | - | -- | ----------------: |
| 1 |      0.7384915627 |  | 7  |       1.473820592 |
| 2 |     −1.205937417 |  | 8  |   −0.03849271640 |
| 3 |    0.004387195200 |  | 9  |      0.9152648037 |
| 4 |   −0.09172645380 |  | 10 |     −2.607139485 |
| 5 |       2.846109373 |  | 11 |     0.05187362940 |
| 6 |  −0.006281540900 |  | 12 |     −1.084937163 |

- Flops totales: **1486** (cota de referencia 1486)
- ‖r‖∞ del residuo exacto: **2.6×10⁻¹⁰** (tras 2 pasadas de refinamiento)
- Dígitos afirmados: **16** en las 12 incógnitas

## Informe

Análisis completo en [informe.md](informe.md).

## Licencia

Trabajo académico para la Prueba Parcial de INF-321 (UCM). Se permite su uso con fines de evaluación docente; no se autoriza su reutilización como entrega de terceros.
