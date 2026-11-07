# Pruebas de mem

Biblioteca: `mem 0.1.0`. Bagron mínimo probado: 1.1.4.

La prueba `main.bg` utiliza `library mem as Mem` para verificar que un
consumidor externo puede importar los símbolos del paquete. Incluye
rangos válidos e inválidos, copias de buffer, movimiento con solapamiento,
comparación de octetos sin signo, orden inverso y conversiones de byte[].

```sh
python3 scripts/build_mem.py
# Coloca build/mem.lib en el directorio global de bibliotecas del compilador.
bagron tests/mem/main.bg -o build/mem-test
./build/mem-test
echo $?
```

El valor esperado es 0, sin salida en stdout. Cada número de salida distinto
de cero corresponde a la condición con ese mismo número en el test.

Los dos buffers reservados en la prueba se liberan mediante `Del` antes de
salir, incluso si alguna condición falla. No hay dependencia de IO.
La prueba se ejecutó en Linux x86_64; Windows queda pendiente.
