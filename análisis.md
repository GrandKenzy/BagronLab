# Análisis mínimo: problemas de BagronLab en Linux

Fecha: 2026-11-07. Entorno de prueba: Bagron 1.1.4, Linux x86_64.

| Problema observado | Causa | Estado |
| --- | --- | --- |
| La importación de `io.lib` fallaba al compilar para Linux. | El paquete precompilado declaraba `System = windows`, aunque las fuentes de `io` ya incluían un backend Linux. | Corregido en `io/main.bg` con `System "auto"`; **pendiente reemplazar el paquete publicado con Bagron actualizado**. |
| `string.lib`, dependencia de `io`, presentaba la misma incompatibilidad de plataforma. | Su paquete conservaba metadatos de destino Windows. | Corregido en `string/main.bg` con `System "auto"` y `Arch "auto"`; **pendiente reemplazar el paquete publicado con Bagron actualizado**. |
| El ejecutable Linux fallaba al enlazar con una relocación `R_X86_64_32S`. | Código objeto no compatible con el enlace PIC usado en la prueba. | Corregido upstream en Bagron: los objetos Linux usan relocación PIC y los paquetes portables se validan contra el host sin perder sus metadatos `auto`; **pendiente verificar en Linux**. |
| `io.println("Hola mundo")` no mostraba texto inmediatamente. | La salida está almacenada en un búfer. | No se considera un fallo del backend: llamar a `io.flush()` antes de terminar el proceso. |

## Prueba de humo

```bg
library io as io

@unsafe
func main() int32:
    io.println("Hola mundo")
    io.flush()
    return 0
```

Con los paquetes `lib1` regenerados y el ajuste PIC local, la prueba imprimió `Hola mundo` y terminó con código 0 en Linux x86_64. El ajuste PIC ya está integrado en Bagron; falta repetir la prueba sin el ajuste local.

## Pendiente

- Regenerar y sustituir en `build/` los paquetes distribuidos `io.lib` y `string.lib` usando el Bagron actualizado.
- Verificar de nuevo el enlace Linux sin depender del ajuste local.
