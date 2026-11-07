# string

`string` ofrece operaciones ASCII sobre arrays de caracteres y buffers
terminados en `NUL`. Sus funciones públicas son `@unsafe` porque reciben
memoria del llamador; el compilador proporciona automáticamente los metadatos
`Len_t` y `Size_t` cuando se pasa un array.

## Entry module

La librería expone toda su API desde `main.bg`. El punto de entrada reúne la
inspección, comparación, búsqueda, copia, concatenación, clasificación ASCII,
transformaciones, trim, inversión, parseo decimal, alfabetos constantes y
codificación hexadecimal.

Los símbolos se consumen mediante el namespace de la librería:

```bg
library string as String

func example() int32:
    value: char[16] = "bagron"
    String.to_upper(value)
    if not String.equals_chain(value, "BAGRON"):
        return 1
    digits: chain = String.NumericString
    if digits[0] != "0":
        return 2
    return 0
```

Los alfabetos forman parte de la misma API. Sus constantes públicas
principales son:

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
library string as String

@unsafe
func example() int32:
    value: char[16] = "  bagron  "
    String.to_upper(value)
    String.trim_whitespace(value)
    if not String.equals_chain(value, "BAGRON"):
        return 1
    zero: char = "0"
    digits: chain = String.NumericString
    if digits[0] != zero:
        return 2
    return 0
```

Los elementos de un array `chain` constante son `char`; para evitar que un
literal de texto se interprete como `chain` en una comparación, declara el
carácter esperado en una variable `char`.
