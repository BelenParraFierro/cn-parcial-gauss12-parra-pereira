# Informe El pivote: eliminación gaussiana 12×12

## 1. Identificación

| Campo       | Detalle                                                                                                                                     |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| Estudiante  | Belén Parra Fierro<br />Cristóbal Pereira Saez                                                                                            |
| Sección    | 2                                                                                                                                           |
| Asignatura  | Computación Numérica (INF-321)                                                                                                            |
| Docentes    | Juan Manuel Cabezas Contardo · Pedro Pesante                                                                                               |
| Fecha       | Talca, noviembre de 2026                                                                                                                    |
| Repositorio | [github.com/BelenParraFierro/cn-parcial-gauss12-parra-pereira.git](https://github.com/BelenParraFierro/cn-parcial-gauss12-parra-pereira.git) |

Todas las cifras de este informe salen de `python src/main.py` (archivos en `resultados/`).

## 2. Planteamiento

Se resuelve **Ax = b** con A densa de 12×12 (144 elementos no nulos, 9 cifras significativas cada uno) y b entregado con 20 dígitos. Lo que hace difícil el caso:

- **Escalas de fila incompatibles.** El máximo por fila, sᵢ = maxⱼ|aᵢⱼ|, va desde 8.0×10⁻⁵ (F5) hasta 9.7×10⁵ (F6): diez órdenes de magnitud entre filas. Las filas impares son "pequeñas" (10⁻⁵ a 10⁻²) y las pares "grandes" (10³ a 10⁶).
- **Pivote inicial minúsculo.** a(1,1) = 1.3407×10⁻⁸, muy por debajo incluso de su propia fila (s₁ = 9.27×10⁻⁵).
- **Casi dependencia lineal.** F7 está muy cerca de una combinación de F3 y F5 (sección 6).

Consecuencia: κ₂(A) ≈ 3.08×10¹³ según el enunciado (nuestro estimador da κ₁(A) ≈ 4.47×10¹³, sección 6), así que el costo no es sólo de flops: es de **bits de mantisa**. La matriz no tiene ceros, por lo que no se puede ahorrar saltándolos; el ahorro tiene que venir de no repetir trabajo.

Los datos se leen dos veces desde el mismo CSV: como `float` (para el algoritmo) y como `fractions.Fraction` (representación exacta de los decimales, incluidos los 20 dígitos de b, que un double no alcanza a guardar). La segunda copia se usa sólo para verificar.

## 3. Estrategia de eliminación

Se factoriza **PA = LU** (L unitaria inferior, U superior) y después se resuelve con sustitución progresiva y regresiva (`src/gauss.py`). Las decisiones para no exceder el mínimo:

1. **Un multiplicador por fila.** En el paso k, m(i,k) = a(i,k)/a(k,k) se calcula una sola vez, se guarda en L[i][k] y se reutiliza en las columnas k…12 de la fila i y en bᵢ.
2. **Barrido desde la columna k (como exige T1).** En la columna k se calcula a(i,k) − m·a(k,k), que en aritmética exacta da 0. En punto flotante queda un residuo de redondeo. El código registra el mayor de esos residuos (aparece en `traza_eliminacion.txt`, por ejemplo 1.5×10⁻¹¹ en la corrida escalada, despreciable frente a filas de hasta 10⁶) y después fija `0.0`. Así los 66 elementos quedan **exactamente nulos** y la anulación se puede comprobar.
3. **El barrido no toca la subdiagonal anulada:** el paso k sólo recorre filas k+1…12 y columnas k…12. Las columnas 1…k−1 ya anuladas nunca se vuelven a tocar.
4. **Una sola factorización y nunca la inversa.** `resolver(fac, b)` reutiliza L, U y perm. El refinamiento iterativo y el estimador de κ usan los mismos factores.
5. **Pivoteo parcial escalado** (corrida principal). Las escalas sᵢ se calculan **una sola vez** sobre A original y se intercambian con las filas. En el paso k se elige la fila p con el mayor |a(i,k)|/sᵢ. Los intercambios de fila son intercambios de referencias (O(1), sin mover datos).

## 4. Conteo de operaciones

Convención: **1 flop = 1 operación aritmética elemental** (+, −, ×, ÷) en punto flotante. `abs()` no se cuenta. Las comparaciones, las divisiones |a(i,k)|/sᵢ del pivoteo escalado y los intercambios se cuentan **aparte**, como sobrecosto de estabilidad. Cada contador se incrementa en `gauss.py` al lado de la operación que cuenta (`cont.suma("mult_A")`, etc.). Ningún número sale de una fórmula.

Corrida principal (pivoteo parcial escalado). Tabla completa en `resultados/conteo_flops.md`:

| Paso            |     Div. (m) |       Mult. A |      Restas A |      Mult. b |     Restas b |      Mult/Div |       Sum/Res |          Flops |
| --------------- | -----------: | ------------: | ------------: | -----------: | -----------: | ------------: | ------------: | -------------: |
| 1               |           11 |           132 |           132 |           11 |           11 |           154 |           143 |            297 |
| 2               |           10 |           110 |           110 |           10 |           10 |           130 |           120 |            250 |
| 3               |            9 |            90 |            90 |            9 |            9 |           108 |            99 |            207 |
| 4               |            8 |            72 |            72 |            8 |            8 |            88 |            80 |            168 |
| 5               |            7 |            56 |            56 |            7 |            7 |            70 |            63 |            133 |
| 6               |            6 |            42 |            42 |            6 |            6 |            54 |            48 |            102 |
| 7               |            5 |            30 |            30 |            5 |            5 |            40 |            35 |             75 |
| 8               |            4 |            20 |            20 |            4 |            4 |            28 |            24 |             52 |
| 9               |            3 |            12 |            12 |            3 |            3 |            18 |            15 |             33 |
| 10              |            2 |             6 |             6 |            2 |            2 |            10 |             8 |             18 |
| 11              |            1 |             2 |             2 |            1 |            1 |             4 |             3 |              7 |
| Sust. regresiva |   12 (diag.) |            66 |            66 |           – |           – |            78 |            66 |            144 |
| **Total** | **66** | **572** | **572** | **66** | **66** | **782** | **704** | **1486** |

En el paso k, con r = 12 − k filas bajo el pivote, se hacen r divisiones (multiplicadores), r·(r+1) multiplicaciones y r·(r+1) restas en A (columnas k…12), y r + r en b. Para la sustitución regresiva son 12 divisiones, 66 multiplicaciones y 66 restas.

**Comparación con la cota.** La cota de referencia del enunciado es ≈ 1486 flops y la implementación hace **1486 (0.0 %)**. Así se reparten: eliminación de A, 66 + 572 + 572 = 1210; actualización de b, 132; sustitución regresiva, 144. Ninguna operación es redundante: no se recalcula ningún multiplicador, no se vuelve a la subdiagonal anulada y no se calcula la inversa. Las 132 operaciones de la columna k (66 mult. + 66 restas) son las que exige el barrido "de la columna k en adelante" de T1. Si se omitieran asignando el cero directamente, el total bajaría a 1354. La eliminación de A (1210) supera a 2n³/3 = 1152 porque esa fórmula es sólo el término dominante: la expresión completa es 2n³/3 + n²/2 − 7n/6 = 1210.

**Sobrecosto del pivoteo (aparte):**

| Pivoteo          |                    Comparaciones | Div. de pivoteo | Intercambios |
| ---------------- | -------------------------------: | --------------: | -----------: |
| Ninguno          |                                0 |               0 |            0 |
| Parcial simple   |                               66 |               0 |            9 |
| Parcial escalado | 198 (132 escalas + 66 búsqueda) |              77 |            8 |

Los flops del algoritmo son los mismos (1486) en las tres corridas: el pivoteo no agrega aritmética de eliminación, sólo búsqueda.

## 5. Análisis de mantisa y pivoteo

Mismo código, tres corridas (la tercera, pivoteo parcial simple, se agrega como control). El error se mide **por componente** contra la solución exacta racional: error relativo máx. = máxᵢ |xᵢ − xᵢ\*|/|xᵢ\*| y dígitos correctos de cada incógnita = −log₁₀(|xᵢ − xᵢ\*|/|xᵢ\*|). Bits correctos = −log₂(error relativo máx.) y bits perdidos = 53 − bits correctos. Las cifras salen de la tabla que imprime `main.py` y de `traza_eliminacion.txt`.

| Corrida                    | max\|m(i,k)\| | Crecimiento ρ |     Error relativo máx. | Bits correctos |  Bits perdidos | Dígitos correctos (mín.) |
| -------------------------- | ------------: | -------------: | -----------------------: | -------------: | -------------: | -------------------------: |
| Sin pivoteo                |  2.75×10¹³ |     2.64×10³ |             7.51×10⁻⁸ |           23.7 |           29.3 |                        7.1 |
| Parcial simple             |          0.62 |           1.00 |           2.00×10⁻¹⁰ |           32.2 |           20.8 |                        9.7 |
| **Parcial escalado** |    2.47×10⁹ |           1.78 | **8.54×10⁻¹¹** | **33.4** | **19.6** |             **10.1** |

El error máximo por componente siempre cae en las incógnitas más pequeñas, x₃ ≈ 4.4×10⁻³ y x₆ ≈ −6.3×10⁻³: un error absoluto parejo pesa mucho más en términos relativos sobre ellas. Medido en norma (‖x − x\*‖∞/‖x\*‖∞), el error de la corrida escalada es 2.36×10⁻¹³, que coincide con la primera corrección del refinamiento ‖d‖/‖x‖ en `residuo.txt`.

ρ = máx. |a(i,j)| alcanzado durante la eliminación / máx. |a(i,j)| de A. Además, el código mide en cada actualización a(i,j) − m·a(k,j) la peor **absorción** (log₂ de |m·a(k,j)|/|a(i,j)|, que son los bits de a(i,j) empujados fuera de la mantisa al alinear exponentes) y la peor **cancelación** (log₂ del operando mayor / |resultado|):

| Corrida          | Absorción máx. | Cancelación máx. |
| ---------------- | ---------------: | -----------------: |
| Sin pivoteo      |        18.1 bits |          14.3 bits |
| Parcial simple   |         7.3 bits |          13.5 bits |
| Parcial escalado |         6.3 bits |           6.3 bits |

**Por qué el pivote a(1,1) es inaceptable.** En relación con su propia fila, a(1,1)/s₁ = 1.45×10⁻⁴, mientras que F8 tiene |a(8,1)|/s₈ = 1. Usarlo como pivote da multiplicadores m(i,1) = a(i,1)/a(1,1) de hasta 2.75×10¹³ (F6). Entonces m·a(1,j) ≈ 2.75×10¹³ · 10⁻⁵ ≈ 10⁹, mientras que la fila 6 original vale ~10⁵–10⁶. Al restar, los exponentes se alinean al de m·a(1,j) y los bits bajos de a(6,j) salen de los 53 bits de mantisa (hasta 18 bits en el peor elemento). **Esa información se pierde de forma irrecuperable.** Lo que queda en la fila 6 es básicamente "−m·F1", y por eso el segundo pivote sale −2.54×10⁷, inflado por la contaminación. La matriz crece por un factor 2.6×10³ (≈ 11 bits más) y los pasos siguientes cancelan. Total: 29.3 bits perdidos y sólo 7.1 dígitos correctos en x₃ y x₆. El sistema igual se resuelve, porque ningún pivote se anula, y eso es justamente lo peligroso: el resultado se ve razonable pero tiene la mitad de los dígitos.

**Por qué el escalado elige mejor, aunque su multiplicador máximo sea 2.5×10⁹.** Lo que destruye bits no es |m| a secas, sino |m|·sₖ/sᵢ: el tamaño de lo que se resta comparado con la fila que lo recibe. Cuando el pivote es de una fila pequeña (p. ej. F1, s ≈ 10⁻⁴) y se elimina en una fila grande (s ≈ 10⁵), m ≈ 10⁹ es lo natural y m·a(k,j) queda del mismo orden que la fila destino. El escalado garantiza |a(i,k)|/sᵢ ≤ |a(k,k)|/sₖ, o sea |m|·sₖ/sᵢ ≤ 1, y por eso la absorción y la cancelación quedan acotadas en ~6 bits. El pivoteo simple elige por magnitud absoluta y por lo tanto siempre prefiere las filas grandes. Aquí funciona razonablemente (ρ = 1), pero con 13.5 bits de cancelación, y su último pivote sale −2.7×10⁻⁷ de F5, una fila pequeña que llega al final con su información ya erosionada. Es el error de "el mayor valor absoluto a secas elige mal" del enunciado: en este caso cuesta ~1.2 bits (error 2.3× mayor).

## 6. Condicionamiento

| Cantidad                       |        Valor | Cómo se obtuvo                                                       |
| ------------------------------ | -----------: | --------------------------------------------------------------------- |
| κ₁(A)                        | 4.47×10¹³ | Estimador de Hager con la LU propia (`verificacion.estimar_kappa1`) |
| Cota κ₁(A)·ε               | 9.92×10⁻³ | `residuo.txt` (ε = 2⁻⁵²)                                        |
| Dígitos que garantiza la cota |         2.00 | −log₁₀(κ₁·ε)                                                   |
| κ₂(A)                        | 3.08×10¹³ | Valor de referencia del enunciado (tabla 3.1)                         |

El estimador de Hager estima ‖A⁻¹‖₁ resolviendo con A y Aᵀ a partir de los mismos factores L, U (`resolver_sin_contar` y `resolver_transpuesta`) y complementa con el vector alternante de Higham por si el método se estanca. **No se forma la inversa.** κ₁(A) = ‖A‖₁·‖A⁻¹‖₁ estimado.

**Cota clásica.** ‖δx‖/‖x‖ ≲ κ(A)·ε = 4.47×10¹³ · 2.22×10⁻¹⁶ ≈ **9.9×10⁻³**: garantiza apenas 2 dígitos. Sin embargo, el error observado es 2.4×10⁻¹³ en norma y 8.5×10⁻¹¹ en el peor componente (10.1 dígitos), diez órdenes mejor que la cota en norma.

**Por qué la cota es pesimista aquí.** La cota supone una perturbación δA del tamaño de ε·‖A‖, igual para todas las filas. Pero la eliminación con pivoteo escalado es estable **fila por fila**: el error hacia atrás de la fila i es del orden de ε·sᵢ, proporcional a su propia escala. La mayor parte de κ(A) ≈ 10¹³ viene sólo de la disparidad de escalas (10⁻⁵…10⁵, diez órdenes), que no amplifica errores relativos a cada fila. Como diagnóstico aparte (calculado con numpy, no forma parte de `main.py`), al equilibrar las filas (D⁻¹A con D = diag(sᵢ)) el condicionamiento baja a κ₂(D⁻¹A) ≈ 8.1×10³. Ese es el condicionamiento que realmente "ve" el algoritmo: κ(D⁻¹A)·ε ≈ 2×10⁻¹² ⇒ **≈ 11–12 dígitos recuperables**, coherente con los 10.1–13.1 dígitos por incógnita que se obtienen sin refinar. La cota con κ(A) está bien como peor caso, pero el residuo y la solución verificada son los que deciden.

**La casi dependencia oculta (F7 ≈ c₃F3 + c₅F5).** El condicionamiento que queda tras equilibrar tiene una causa concreta. La función `verificacion.casi_dependencia(A, 6, 2, 4)` ajusta F7 como combinación de F3 y F5 por mínimos cuadrados y da F7 ≈ 4.177·F3 + 583.2·F5 con residuo relativo 2.3×10⁻³ (esta función está en el repositorio pero `main.py` no la llama; el valor se obtuvo ejecutándola aparte). F7 está a una perturbación pequeña de ser combinación de F3 y F5. El pivoteo escalado lo "detecta" solo: en `traza_eliminacion.txt` se ve que deja F7 para el último lugar, y su pivote final (U₁₂,₁₂ = 1.57×10⁻⁴) es apenas 2.5×10⁻³ de la escala de su fila (s₇ = 6.33×10⁻²), la misma magnitud que el residuo del ajuste.

## 7. Resultados

Valores tras **dos pasadas** de refinamiento iterativo sobre la corrida con pivoteo escalado (`resultados/solucion.csv`). Cada incógnita se escribe con exactamente los dígitos que se afirman correctos.

**Cómo se fijan los dígitos afirmados.** En `main.py`, los dígitos de cada incógnita se miden contra la solución exacta racional (−log₁₀ del error relativo) y se limitan a 16, porque un double (53 bits ≈ 15.95 dígitos) no puede defender más. Tras el refinamiento todas las incógnitas tienen entre 16.06 (x₂) y 17.3 (x₇) dígitos correctos, así que las 12 quedan en 16. Esto es coherente con una estimación que no usa la solución exacta: la segunda corrección del refinamiento es ‖d‖/‖x‖ = 6.0×10⁻¹⁷ (`residuo.txt`), o sea un error del orden de 10⁻¹⁶ (16 dígitos).

| i  | xᵢ reportado               | Dígitos afirmados |
| -- | --------------------------- | -----------------: |
| 1  | 7.384915627000000×10⁻¹   |                 16 |
| 2  | −1.205937416800000         |                 16 |
| 3  | 4.387195200000000×10⁻³   |                 16 |
| 4  | −9.172645380000000×10⁻² |                 16 |
| 5  | 2.846109372500000           |                 16 |
| 6  | −6.281540900000000×10⁻³ |                 16 |
| 7  | 1.473820591600000           |                 16 |
| 8  | −3.849271640000000×10⁻² |                 16 |
| 9  | 9.152648037000000×10⁻¹   |                 16 |
| 10 | −2.607139485200000         |                 16 |
| 11 | 5.187362940000000×10⁻²   |                 16 |
| 12 | −1.084937162500000         |                 16 |

Los 16 dígitos reportados coinciden exactamente con la solución exacta del sistema: la solución verdadera usada para construir b tiene 10 cifras significativas, y b es consistente con ella, por eso los dígitos 11 a 16 son ceros. Sin refinar, la corrida escalada ya tenía entre 10.1 (x₃, x₆) y 13.1 (x₁) dígitos correctos.

## 8. Verificación

**Residuo en precisión extendida.** r = b − Ax se calcula en aritmética racional exacta (`fractions.Fraction`), convirtiendo x de double a racional sin pérdida y usando b con sus 20 dígitos (`resultados/residuo.txt`, que reporta cada componente de r y su norma infinito antes y después del refinamiento).

| Etapa                     | ‖r‖∞ (antes) | Corrección ‖d‖/‖x‖ |
| ------------------------- | --------------: | ----------------------: |
| Pasada 1 (sobre x₀)      |  2.29×10⁻¹⁰ |          2.36×10⁻¹³ |
| Pasada 2 (sobre x₁)      |  2.60×10⁻¹⁰ |          6.02×10⁻¹⁷ |
| Después del refinamiento |  2.60×10⁻¹⁰ |                      – |

**Refinamiento iterativo.** xₖ₊₁ = xₖ + dₖ con A dₖ = rₖ, donde rₖ es exacto y dₖ se obtiene con **los mismos L, U** (276 flops por pasada, sin refactorizar). La primera corrección (2.4×10⁻¹³) es justamente el error en norma de x₀, y la segunda (6.0×10⁻¹⁷) ya está bajo ε: el refinamiento llegó al piso del double (el redondeo de x a 53 bits) y una tercera pasada no cambiaría nada.

**Lo que dice (y lo que no dice) el residuo.** ‖r‖∞ no baja con el refinamiento aunque el error baje ~4000×. Esto se debe a que ‖r‖∞ está dominado por la fila 6 (escala 10⁶), donde el solo hecho de guardar x en double ya produce |r₆| ≈ s₆·‖x‖·ε ≈ 10⁻¹⁰. El efecto del refinamiento sí se ve en las filas pequeñas: r₇ (la fila casi dependiente) pasa de −1.4×10⁻¹⁷ a −9.8×10⁻¹⁹ y r₁₂ de 5.2×10⁻¹¹ a −9.4×10⁻¹². Es decir, un residuo sin normalizar por fila puede engañar en ambos sentidos.

**Control con biblioteca.** `numpy.linalg.solve` (LAPACK, pivoteo parcial sin escalar) da como mínimo 10.0 dígitos correctos, y su diferencia relativa máxima con nuestra solución sin refinar es 1.97×10⁻¹⁰ (valores de `residuo.txt`; pueden variar levemente según la plataforma y la librería BLAS, por ejemplo en Linux se obtuvo 9.7 dígitos y 1.04×10⁻¹⁰). Es prácticamente lo mismo que nuestra corrida "parcial simple" (9.7 dígitos). Sólo se usa como control: el resultado reportado es el de la implementación propia.

## 9. Conclusiones

**Compromiso elegido: pivoteo parcial escalado + una pasada de refinamiento con residuo exacto.** El costo de eliminación es el mínimo (1486 flops, igual a la cota: un multiplicador por fila, sin volver a la subdiagonal anulada, sin inversa). La estabilidad cuesta 198 comparaciones, 77 divisiones y 8 intercambios: es O(n²), frente a O(n³) de la eliminación, y no agrega ningún flop a esta. A cambio se recuperan 9.7 bits respecto de no pivotear (de 23.7 a 33.4 bits correctos en el peor componente, de 7.1 a 10.1 dígitos mínimos), y dos pasadas de refinamiento llevan todas las incógnitas al límite del double (16 dígitos) por 276 flops por pasada más un residuo exacto. La secuencia más barata (sin pivoteo, 0 comparaciones) es la que pierde 29 bits. **El pivote mínimo a(1,1) no se puede aceptar a ningún precio.**

**Con n = 1000:**

- La eliminación cuesta ≈ 2n³/3 ≈ 6.7×10⁸ flops y el pivoteo ~n² ≈ 10⁶ comparaciones (0.15 %), así que pivotear sigue siendo gratis en proporción.
- Usaría una LU por bloques (BLAS-3/LAPACK `dgetrf`) para aprovechar caché, y equilibraría las filas una vez al inicio (`dgeequ`) en vez de escalar en cada búsqueda.
- Estimaría κ con Hager (`dgecon`, O(n²)).
- Haría el refinamiento con residuo en precisión doble-doble o cuádruple, no con `Fraction` (O(n²) racional con números enormes no escala).
- Si κ(D⁻¹A) es moderado, se puede factorizar en float32 y refinar en float64 (precisión mixta) para duplicar la velocidad.
- Las trazas completas por paso dejarían de ser factibles; registraría sólo ρ, pivotes y |m| máximo por paso.

## 10. Reproducibilidad

| Elemento | Versión                                                           |
| -------- | ------------------------------------------------------------------ |
| Python   | 3.14 (el código usa sólo características de Python ≥ 3.10)     |
| numpy    | 2.5.5                                                              |
| mpmath   | 1.4.1                                                              |
| Comando  | `pip install -r requirements.txt` y luego `python src/main.py` |

`main.py` regenera los cuatro archivos de `resultados/` en menos de 1 s. Se probó en un entorno virtual limpio creado sólo con `requirements.txt`.

**Uso de asistentes de IA.** Se usó Claude (Anthropic) como apoyo. Los resultados numéricos se generaron y verificaron ejecutando el código del repositorio.

**Fuentes.**

- R. L. Burden, J. D. Faires, A. M. Burden. *Análisis numérico*, 10.ª ed. Cengage, 2017. Cap. 6 (pivoteo parcial escalado).
- N. J. Higham. *Accuracy and Stability of Numerical Algorithms*, 2.ª ed. SIAM, 2002. Cap. 9 (factor de crecimiento, estabilidad), cap. 12 (refinamiento iterativo), cap. 15 (estimación de condición).
- W. W. Hager. "Condition estimates". *SIAM J. Sci. Stat. Comput.* 5(2), 311–316, 1984.
- G. H. Golub, C. F. Van Loan. *Matrix Computations*, 4.ª ed. Johns Hopkins, 2013. Cap. 3.
- IEEE Std 754-2019, *Standard for Floating-Point Arithmetic*.
