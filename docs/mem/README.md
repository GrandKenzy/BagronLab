# mem 0.1.0 — Buffers y memoria portable

La biblioteca `mem` proporciona operaciones de relleno, limpieza, copia,
movimiento, comparación y búsqueda en memoria propiedad del llamador.
Implementación 100% Bagron, sin libc, `malloc` ni dependencias del sistema.

## Contrato de seguridad

- Arrays compatibles: `buffer[]` y `byte[]`. El compilador suministra
  `Len_t` y, para `byte[]`, `Size_t`.
- Los rangos se validan ANTES del acceso, comprobando
  `start <= length` y `count <= length - start` para evitar overflow.
- Un rango vacío en el extremo final es válido.
- `copy` y `copy_bytes` no admiten regiones solapadas; para mover bytes
  dentro del mismo arreglo se usan `move_within` y `move_bytes`.
- La biblioteca no asigna, no libera ni retiene memoria. El llamador
  mantiene el ownership y utiliza `Del` donde corresponda.
- Las operaciones están marcadas `@unsafe`: validar longitudes no comprueba
  que los punteros sean válidos ni garantiza que el almacenamiento siga vivo.
- `zero` y `zero_bytes` no garantizan borrado seguro frente al optimizador.
  `equal` y `equal_bytes` no son comparaciones de tiempo constante.
- Bagron 1.1.4 exige tamaño constante al declarar `buffer[N]`. La memoria
  dinámica a partir de una capacidad calculada se deja para otra fase.

## API para buffer[]

| Función | Resultado |
| --- | --- |
| `fill(data, start, count, value)` | Rellenar; bool |
| `zero(data, start, count)` | Limpiar a cero; bool |
| `copy(dst, src, dst_start, src_start, count)` | Copiar sin alias; bool |
| `move_within(data, dst_start, src_start, count)` | Movimiento con solapamiento; bool |
| `equal(a, b, a_start, b_start, count)` | Igualdad; bool |
| `index_of(data, start, value)` | Índice o `length` si no aparece |
| `count_value(data, start, count, value)` | Coincidencias; cero si el rango es inválido |
| `reverse(data, start, count)` | Invertir en el mismo buffer; bool |

## API para byte[]

`fill_bytes`, `zero_bytes`, `copy_bytes`, `move_bytes`, `equal_bytes`,
`index_of_bytes` y `reverse_bytes` son equivalentes para `byte[]`.

- `compare_bytes`: orden lexicográfico de octetos sin signo. Devuelve
  -1, 0 o 1; -2 si un rango es inválido.
- `into_buffer` copia de `byte[]` a `buffer[]`.
- `from_buffer` copia de `buffer[]` a `byte[]`.

Los argumentos ocultos `Len_t` y `Size_t` los genera el compilador.

## Ejemplo

```bg
clause System "auto"
clause Arch "auto"
library mem as Mem
import { fill, move_within, zero } from Mem

@unsafe
func main() int32:
    data: buffer[16] = 0
    result: int32 = 0
    if not fill(data, 0, 16, 65):
        result = 1
    if not move_within(data, 4, 0, 8):
        result = 2
    if not zero(data, 0, 4):
        result = 3
    Del data
    return result
```

## Empaquetado y tests

Con Bagron 1.1.4 o posterior:

```sh
bagron library --v1 mem -o build/mem.lib --name mem --version 0.1.0
bagron verify build/mem.lib
bagron inspect build/mem.lib
```

Después de instalar `mem.lib` en el directorio global de bibliotecas del
compilador:

```sh
bagron tests/mem/main.bg -o test-mem
./test-mem
echo $?
```

El test termina con código 0 si todos los casos pasan. Verificado por ahora
en Linux x86_64, no todavía en Windows.

## Futuras fases

- Vista de memoria sin ownership y límites estrictos.
- API de memoria dinámica con ownership explícito usando las bibliotecas
  nativas `gnulibrary` y `windows`, tras validar sus respectivas ABI.
- Pruebas de alias, benchmarks y sanitizadores del backend.
