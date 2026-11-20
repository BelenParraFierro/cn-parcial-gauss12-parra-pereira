# Conteo de operaciones por paso

Convención: 1 flop = 1 operación aritmética elemental (+, -, *, /). Los números salen del contador instrumentado en el código (conteo.py), no de una fórmula.

Incluye eliminación, actualización de b y sustitución regresiva. La búsqueda de pivote, las divisiones del pivoteo escalado y los intercambios se cuentan aparte (sobrecosto de estabilidad). No incluye el refinamiento ni la verificación.

### Corrida: ninguno

| Fase | Div. (multiplicadores) | Mult. A | Restas A | Mult. b | Restas b | Mult/Div paso | Sum/Res paso | Flops paso | Comparac. pivote | Div. pivote | Intercambios |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| paso 1 | 11 | 132 | 132 | 11 | 11 | 154 | 143 | 297 | 0 | 0 | 0 |
| paso 2 | 10 | 110 | 110 | 10 | 10 | 130 | 120 | 250 | 0 | 0 | 0 |
| paso 3 | 9 | 90 | 90 | 9 | 9 | 108 | 99 | 207 | 0 | 0 | 0 |
| paso 4 | 8 | 72 | 72 | 8 | 8 | 88 | 80 | 168 | 0 | 0 | 0 |
| paso 5 | 7 | 56 | 56 | 7 | 7 | 70 | 63 | 133 | 0 | 0 | 0 |
| paso 6 | 6 | 42 | 42 | 6 | 6 | 54 | 48 | 102 | 0 | 0 | 0 |
| paso 7 | 5 | 30 | 30 | 5 | 5 | 40 | 35 | 75 | 0 | 0 | 0 |
| paso 8 | 4 | 20 | 20 | 4 | 4 | 28 | 24 | 52 | 0 | 0 | 0 |
| paso 9 | 3 | 12 | 12 | 3 | 3 | 18 | 15 | 33 | 0 | 0 | 0 |
| paso 10 | 2 | 6 | 6 | 2 | 2 | 10 | 8 | 18 | 0 | 0 | 0 |
| paso 11 | 1 | 2 | 2 | 1 | 1 | 4 | 3 | 7 | 0 | 0 | 0 |
| sust. regresiva | div. diagonal: 12 | mult: 66 | restas: 66 | – | – | 78 | 66 | 144 | 0 | 0 | 0 |
| **Total** | 66 | 572 | 572 | 66 | 66 | **782** | **704** | **1486** | 0 | 0 | 0 |

Flops totales (eliminación + actualización de b + sustitución regresiva): **1486** = 782 mult/div + 704 sum/res.  
Sobrecosto de estabilidad (no incluido en los flops): 0 comparaciones, 0 divisiones de pivoteo escalado, 0 intercambios de fila.

Cota de referencia: 1486 flops. Conteo medido: 1486 (+0.0 %). Dentro de ±10 %: sí.

### Corrida: parcial

| Fase | Div. (multiplicadores) | Mult. A | Restas A | Mult. b | Restas b | Mult/Div paso | Sum/Res paso | Flops paso | Comparac. pivote | Div. pivote | Intercambios |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| paso 1 | 11 | 132 | 132 | 11 | 11 | 154 | 143 | 297 | 11 | 0 | 1 |
| paso 2 | 10 | 110 | 110 | 10 | 10 | 130 | 120 | 250 | 10 | 0 | 1 |
| paso 3 | 9 | 90 | 90 | 9 | 9 | 108 | 99 | 207 | 9 | 0 | 1 |
| paso 4 | 8 | 72 | 72 | 8 | 8 | 88 | 80 | 168 | 8 | 0 | 1 |
| paso 5 | 7 | 56 | 56 | 7 | 7 | 70 | 63 | 133 | 7 | 0 | 1 |
| paso 6 | 6 | 42 | 42 | 6 | 6 | 54 | 48 | 102 | 6 | 0 | 1 |
| paso 7 | 5 | 30 | 30 | 5 | 5 | 40 | 35 | 75 | 5 | 0 | 0 |
| paso 8 | 4 | 20 | 20 | 4 | 4 | 28 | 24 | 52 | 4 | 0 | 1 |
| paso 9 | 3 | 12 | 12 | 3 | 3 | 18 | 15 | 33 | 3 | 0 | 1 |
| paso 10 | 2 | 6 | 6 | 2 | 2 | 10 | 8 | 18 | 2 | 0 | 0 |
| paso 11 | 1 | 2 | 2 | 1 | 1 | 4 | 3 | 7 | 1 | 0 | 1 |
| sust. regresiva | div. diagonal: 12 | mult: 66 | restas: 66 | – | – | 78 | 66 | 144 | 0 | 0 | 0 |
| **Total** | 66 | 572 | 572 | 66 | 66 | **782** | **704** | **1486** | 66 | 0 | 9 |

Flops totales (eliminación + actualización de b + sustitución regresiva): **1486** = 782 mult/div + 704 sum/res.  
Sobrecosto de estabilidad (no incluido en los flops): 66 comparaciones, 0 divisiones de pivoteo escalado, 9 intercambios de fila.

Cota de referencia: 1486 flops. Conteo medido: 1486 (+0.0 %). Dentro de ±10 %: sí.

### Corrida: parcial_escalado

| Fase | Div. (multiplicadores) | Mult. A | Restas A | Mult. b | Restas b | Mult/Div paso | Sum/Res paso | Flops paso | Comparac. pivote | Div. pivote | Intercambios |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| escalas | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 132 | 0 | 0 |
| paso 1 | 11 | 132 | 132 | 11 | 11 | 154 | 143 | 297 | 11 | 12 | 1 |
| paso 2 | 10 | 110 | 110 | 10 | 10 | 130 | 120 | 250 | 10 | 11 | 0 |
| paso 3 | 9 | 90 | 90 | 9 | 9 | 108 | 99 | 207 | 9 | 10 | 1 |
| paso 4 | 8 | 72 | 72 | 8 | 8 | 88 | 80 | 168 | 8 | 9 | 1 |
| paso 5 | 7 | 56 | 56 | 7 | 7 | 70 | 63 | 133 | 7 | 8 | 1 |
| paso 6 | 6 | 42 | 42 | 6 | 6 | 54 | 48 | 102 | 6 | 7 | 1 |
| paso 7 | 5 | 30 | 30 | 5 | 5 | 40 | 35 | 75 | 5 | 6 | 1 |
| paso 8 | 4 | 20 | 20 | 4 | 4 | 28 | 24 | 52 | 4 | 5 | 1 |
| paso 9 | 3 | 12 | 12 | 3 | 3 | 18 | 15 | 33 | 3 | 4 | 1 |
| paso 10 | 2 | 6 | 6 | 2 | 2 | 10 | 8 | 18 | 2 | 3 | 0 |
| paso 11 | 1 | 2 | 2 | 1 | 1 | 4 | 3 | 7 | 1 | 2 | 0 |
| sust. regresiva | div. diagonal: 12 | mult: 66 | restas: 66 | – | – | 78 | 66 | 144 | 0 | 0 | 0 |
| **Total** | 66 | 572 | 572 | 66 | 66 | **782** | **704** | **1486** | 198 | 77 | 8 |

Flops totales (eliminación + actualización de b + sustitución regresiva): **1486** = 782 mult/div + 704 sum/res.  
Sobrecosto de estabilidad (no incluido en los flops): 198 comparaciones, 77 divisiones de pivoteo escalado, 8 intercambios de fila.

Cota de referencia: 1486 flops. Conteo medido: 1486 (+0.0 %). Dentro de ±10 %: sí.

