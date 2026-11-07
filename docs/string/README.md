# string

`string` ofrece operaciones ASCII sobre arrays de caracteres y buffers
terminados en `NUL`. Sus funciones públicas son `@unsafe` porque reciben
memoria del llamador; el compilador proporciona automáticamente los metadatos
`Len_t` y `Size_t` cuando se pasa un array.

## Módulos

La librería contiene dos módulos:

- `string`: inspección, comparación, búsqueda, copia, concatenación,
  clasificación ASCII, transformaciones, trim, inversión y parseo decimal.
- `alphabet`: alfabetos constantes para validación, escaneo y serialización.
- `hex`: codificación, decodificación y formato hexadecimal que reutiliza los
  alfabetos hexadecimales de `alphabet`.

Los módulos se consumen por separado:

```bg
import { len, equals_chain, to_upper } from string
import { NumericString, AlphabetString } from alphabet
```

`alphabet` forma parte de la misma librería y se incluye al empaquetar el
directorio `string/`. Sus constantes públicas principales son:

| Grupo | Constantes |
| --- | --- |
| Numérico | `BinaryString`, `OctalString`, `NumericString`, `HexadecimalUpperString`, `HexadecimalLowerString`, `HexadecimalString` |
| Alfabético | `UppercaseAlphabetString`, `LowercaseAlphabetString`, `AlphabetString`, `AlphanumericString`, `Base36String` |
| Codificación | `Base64String`, `Base64UrlString`, `UrlSafeString` |
| Identificadores y símbolos | `IdentifierStartString`, `IdentifierPartString`, `SignString`, `HexadecimalMarkerString`, `SymbolString` |

## Contratos de texto

Las operaciones sobre `char[]` recorren hasta el primer `NUL` o hasta la
capacidad recibida. `copy`, `copy_chain`, `concat` y `concat_chain` no
truncan: si el destino no tiene espacio para el texto y su terminador,
ejecutan `trap()`.

Las funciones `trim_*`, `to_upper`, `to_lower`, `fill` y `reverse` modifican
el array en sitio. `parse_uint` y `parse_int` aceptan los dígitos decimales
iniciales y se detienen ante el primer carácter que no sea parte del número.

## Ejemplo

```bg
@unsafe
func example() int32:
    value: char[16] = "  bagron  "
    to_upper(value)
    trim_whitespace(value)
    if not equals_chain(value, "BAGRON"):
        return 1
    zero: char = "0"
    if NumericString[0] != zero:
        return 2
    return 0
```

Los elementos de un array `chain` constante son `char`; para evitar que un
literal de texto se interprete como `chain` en una comparación, declara el
carácter esperado en una variable `char`.
