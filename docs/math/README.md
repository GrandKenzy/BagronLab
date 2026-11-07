# math 1.2.0 — Matemáticas para Bagron

La biblioteca `math` amplía sus nueve módulos originales con operaciones de
estadística, aritmética entera, teoría de números, trigonometría inversa,
interpolación, geometría 3D, funciones hiperbólicas, exponenciales y
clasificación de valores IEEE-754.

**Estado:** fuentes 1.2.0 en desarrollo. No es una release binaria publicada.
Se mantienen los nombres y firmas públicos existentes de `math 1.1.5`.
No se depende de libc, libm ni funciones nativas duplicadas: los algoritmos
nuevos están escritos en Bagron.

## Módulos

| Archivo | API principal |
| --- | --- |
| `basics.bg` | abs, fabs, min, max, clamp |
| `round.bg` | trunc, floor, ceil, round |
| `sqrt.bg` | sqrt, usqrt |
| `cbrt.bg` | cbrt, ucbrt |
| `pow.bg` | powi, powu |
| `consts.bg` | PI, EULER, TAU, HALF_PI y constantes |
| `trig.bg` | sin, cos, tan |
| `logs.bg` | exp, ln, log10 |
| `geo.bg` | hypot |
| `integers.bg` | gcd, lcm_checked, factorial_checked, is_prime, mul_mod, pow_mod, potencias de dos |
| `statistics.bg` | stats_mean, stats_variance, stats_sample_variance, stats_minmax |
| `inverse_trig.bg` | atan, atan2, asin_checked, acos_checked |
| `interpolation.bg` | lerp, inverse_lerp, saturate, smoothstep, smootherstep, remap |
| `angles.bg` | radians, degrees, normalize_angle, angle_delta |
| `geometry_ext.bg` | hypot3, distance2, distance3, dot2, cross2 |
| `hyperbolic.bg` | sinh, cosh, tanh |
| `exponentials.bg` | log2, log_base_checked, exp2, expm1, log1p_checked |
| `real_power.bg` | pow_real_checked |
| `floating.bg` | isnan, isinf, isfinite, signbit, copysign |
| `checked.bg` | sqrt_checked, ln_checked, log10_checked |

La API existente usa **double** cuando `ARCHB == 64` y **float** cuando
`ARCHB == 32`. Las funciones enteras nuevas operan con `uint64`
independientemente del tamaño de palabra. Las ramas de 32 y 64 bits
superaron la validación de fuente `lib1`, pero solo Linux x86_64 tuvo
pruebas de ejecución.

## Ejemplos

```bg
clause System "auto"
clause Arch "amd"
library math as Math
import { gcd, is_prime, stats_mean, sqrt_checked } from Math

@unsafe
func main() int32:
    if gcd(24, 18) != 6:
        return 1
    if not is_prime(97):
        return 2

    data: double[4]
    data[0] = 1.0
    data[1] = 2.0
    data[2] = 3.0
    data[3] = 4.0

    average: double = 0.0
    if not stats_mean(data, $average):
        return 3

    root: double = 0.0
    if not sqrt_checked(81.0, $root):
        return 4
    return 0
```

Los argumentos ocultos de arreglos `Len_t` y `Size_t` se pasan
automáticamente. Para `stats_*`, `Size_t` debe corresponder al tamaño
de un elemento `float` (4) o `double` (8), y el arreglo no debe estar
vacío. La varianza poblacional divide por `n`; la muestral por `n-1`
y requiere al menos dos elementos.

## Dominios, overflow y precisión

- `sqrt_checked`, `ln_checked`, `log10_checked`, `asin_checked`,
  `acos_checked`, `log_base_checked` y `pow_real_checked` indican
  errores de dominio con `false`; dejan la salida intacta cuando fallan.
- **Compatibilidad:** `sqrt(x)` sigue devolviendo 0 para valores negativos
  y `ln(x)` sigue devolviendo 0 para argumentos no positivos. No alteramos
  esos contratos históricos en una versión menor. Usar las variantes
  `*_checked` cuando se necesite distinguir errores de resultados válidos.
- `pow_real_checked` admite bases no negativas; define `0^0 = 1`,
  rechaza `0` a exponentes negativos y no informa por separado el overflow
  flotante de `exp`. Bases negativas con exponentes enteros deben usar
  `powi`.
- `factorial_checked` admite 0 a 20 y detecta overflow de `uint64`.
  `lcm_checked` y `next_power_of_two_checked` informan de overflow.
  `powu` conserva las reglas de overflow unsigned del lenguaje.
- `mul_mod` y `pow_mod` evitan overflow intermedio. Modulo 0 o 1
  devuelven 0. `is_prime` usa Miller-Rabin determinista con siete bases
  para el dominio completo `uint64`; no es una primitiva criptográfica
  de tiempo constante.
- `isfinite`, `isinf`, `signbit` y `copysign` usan el layout IEEE-754
  binario de `float` y `double`. `copysign` preserva el signo de cero.
- `expm1` y `log1p_checked` tienen series especiales cerca de cero;
  para magnitudes grandes reutilizan `exp` y `ln`.
- `atan2(0,0)` se define como 0 en esta biblioteca; no afirma todas las
  reglas de ceros con signo de la biblioteca estándar C.
- `smoothstep` y `smootherstep` devuelven 0 si `edge0 >= edge1`.
  `normalize_angle` pierde precisión para entradas extremadamente grandes.
- Los algoritmos de Taylor/Newton continúan siendo aproximaciones: no se
  promete redondeo correcto IEEE-754 para todo el rango representable.
  Las funciones que contienen NaN pueden propagarlo de distintas maneras;
  los arrays de estadísticas no filtran valores NaN.

## Correcciones a funciones existentes

- `usqrt(UINT64_MAX)` y `usqrt(UINT32_MAX)` ahora utilizan un máximo
  seguro en la búsqueda binaria; antes podían alcanzar un divisor cero
  y provocar una excepción aritmética en el código generado.
- `sqrt`, `cbrt`, `exp` y `trunc` manejan explícitamente infinitos.
  `trunc` conserva `-0.0`.
- Constantes tipadas `QUARTER_PI` y `ATAN_HALF` mejoran la precisión
  de la trigonometría inversa y evitan la promoción de literales sin tipo.
- `pow.bg` existente se deja intacto; mantiene su implementación y
  cambios más recientes en el repositorio.

## Compilar y probar

Requiere Bagron 1.1.4 o posterior.

```sh
python3 scripts/build_math.py
bagron verify build/math.lib

# Después de instalar math.lib actualizado en las libs del compilador:
bagron tests/math/main.bg -o build/math-smoke
./build/math-smoke

bagron tests/math/numeric.bg -o build/math-numeric
./build/math-numeric
```

Los ejecutables devuelven `0` cuando todas las comprobaciones pasan;
de lo contrario devuelven el identificador del caso fallido. Las pruebas
locales incluyeron **121 comparaciones numéricas** con referencias de Python
y suites adicionales de dominios, overflow e infinitos en Linux x86_64.

La compilación `lib1` se comprobó para rutas de fuente 64 y 32 bits.
La ejecución Windows y 32-bit nativa está pendiente, así como benchmarks
comparativos y pruebas amplias con sanitizadores.

**No publicar `math 1.2.0` como release binaria** hasta ejecutar pruebas
sobre el artefacto empaquetado desde el estado final del repositorio y
actualizar los hashes del manifiesto Central junto al binario.
