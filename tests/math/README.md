# Pruebas de math 1.2.0

Las pruebas están escritas en Bagron e importan `library math as Math`.
Se requiere que `math.lib` se haya generado a partir de las fuentes actuales
e instalado en el directorio de bibliotecas visible para el compilador.

```sh
python3 scripts/build_math.py
bagron verify build/math.lib

# Instalar math.lib en las libs del compilador.
bagron tests/math/main.bg -o build/math-check
./build/math-check
echo $?

bagron tests/math/numeric.bg -o build/math-numeric
./build/math-numeric
echo $?
```

## Cobertura

- `main.bg`: 37 verificaciones agrupadas de enteros, primalidad,
  factorial, overflow, interpolación, estadística, trigonometría inversa,
  geometría, dominio y valores especiales de IEEE-754.
- `numeric.bg`: **121 comparaciones** contra valores matemáticos de
  referencia generados para funciones `sin`, `cos`, `exp`, `ln`,
  `sqrt`, `cbrt`, `atan` y `tanh`, con tolerancia relativa 1e-6.

En el entorno de desarrollo se ejecutaron también suites adicionales con
raíces enteras de `UINT64_MAX`, `NaN`, infinitos, potencias y límites
de signo. La prueba de compilación de fuente `lib1` pasó tanto para rutas
de 64 como de 32 bits. La ejecución nativa de 32 bits y Windows queda
pendiente, al igual que la verificación CI sobre el paquete publicado.

**Importante:** los resultados de `numeric.bg` miden los casos enumerados,
no prueban precisión matemática óptima para todo el dominio de entrada.
