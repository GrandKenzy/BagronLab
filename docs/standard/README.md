# standard

`standard` conserva la API de alto nivel y compatibilidad histórica de Bagron,
pero sus componentes se organizan ahora como librerías independientes. Cada
librería tiene su propio `main.bg`; los módulos internos solo se mantienen
cuando la separación aporta una responsabilidad real:

```text
BagronLab/
├── io/main.bg       └── io/modules/{error,input,output}.bg
├── time/main.bg     └── time/modules/time.bg
├── mmap/main.bg     └── mmap/modules/mmap.bg
├── mem/main.bg      └── mem/modules/mem.bg
├── os/main.bg       └── os/modules/os.bg
└── string/main.bg   (API completa: texto, alfabetos y hexadecimal)
```

Las cláusulas `System` y `Arch` se declaran únicamente en el `main.bg` de cada
librería. Los módulos importados heredan ese target y no repiten la selección.

Los módulos delegan la comunicación nativa en las librerías canónicas del
laboratorio:

- Windows usa `windows.lib`, con declaraciones Microsoft x64 de `kernel32.dll`.
- Linux usa `gnulibrary.lib`, con funciones raw de syscalls x86_64.

## Selección de plataforma

La selección de plataforma sigue este patrón cuando una librería necesita una
ABI nativa:

```bg
#if OS, "windows"
library "windows.lib" as Win
#elif OS, "linux"
library "gnulibrary.lib" as Gnu
#end
```

Los módulos consumen esos namespaces. No deben añadir `extern` por módulo para
repetir declaraciones de `kernel32`, libc o syscalls. La carpeta `standard/`
conserva el agregador y los artefactos históricos; las seis carpetas en la raíz
de `BagronLab` son las unidades nuevas de librería.

## Responsabilidades

Las librerías ofrecen interfaces cómodas como `os.File`, `io.print`, funciones
de tiempo y utilidades de memoria. `windows` y `gnulibrary` siguen siendo la
fuente de verdad de sus respectivas ABI; `standard` no es una libc ni un
reemplazo de las librerías nativas.

En `io`, `print` y `println` conservan sus firmas actuales. Las demás funciones
de salida reciben directamente un parámetro obligatorio `nl: bool`: al pasar
`true` agregan un salto de línea y al pasar `false` continúan en la misma línea.
No existen funciones separadas `newline` ni `println_*`.

`io.write_buffer` escribe exactamente el número de bytes indicado de un
`buffer[]`, incluidos los ceros internos. El buffer se presta durante la
llamada; `count` no puede superar su longitud dinámica. `print_buffer` conserva
la semántica de texto terminado en NUL.

`io/main.bg` selecciona `windows.lib` para Windows y `gnulibrary.lib` para Linux
con `#if OS`/`#elif OS`; la API de `io` no expone diferencias entre ambos targets.

### Archivos y rutas

`os/modules/path.bg` analiza y normaliza rutas sin abrir descriptores. Las
operaciones que modifican el sistema de archivos viven en
`os/modules/file.bg`: la clase `File` abre, lee, escribe, reposiciona, sincroniza
y cierra recursos nativos; las funciones auxiliares crean, renombran y eliminan
archivos o directorios.

Los paquetes `windows.lib` y `gnulibrary.lib` se mantienen como dependencias
de `standard/libs/` y se regeneran desde `BagronLab/windows` y
`BagronLab/gnulibrary` cuando cambian sus fuentes.

## Empaquetado portable de `io` y `string` (lib1)

El codigo fuente de ambas bibliotecas selecciona `windows` o `gnulibrary`
en tiempo de compilacion mediante `#if OS`, pero el paquete `lib1` debe
declarar `System "auto"` **fuera** de esos condicionales. De lo contrario,
el generador conserva el target del sistema donde se empaqueto la biblioteca
(por ejemplo, `windows`) y rechaza su importacion desde Linux, aun cuando
el codigo fuente tenga un backend Linux.

`io/main.bg` mantiene `Arch "amd"`, ya que sus backends nativos actuales
cubren AMD64. `string/main.bg` mantiene `Arch "auto"`.

Para regenerar los artefactos despues de un cambio de fuentes, empaquetar
`string` primero y actualizar su copia instalada antes de empaquetar `io`,
porque `io` depende de `string`:

```sh
bagron library --v1 string -o build/string.lib --name string --version 1.1.7
bagron install --library --v1 string --name string --version 1.1.7
bagron library --v1 io -o build/io.lib --name io --version 1.1.8
bagron verify build/string.lib
bagron verify build/io.lib
bagron inspect build/io.lib
```

Los manifiestos de ambos paquetes deben declarar `targets.System = "auto"`.
Reemplazar tambien los binarios publicados e instalar los paquetes regenerados
antes de probarlos: editar solamente `main.bg` no cambia un `io.lib` anterior
que tenga `System = "windows"` en el manifiesto.
