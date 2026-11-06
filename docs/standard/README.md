# standard

`standard` conserva la API de alto nivel y compatibilidad histórica de Bagron,
pero sus componentes se organizan ahora como librerías independientes. Cada
librería tiene su propio `main.bg` y su carpeta `modules/`:

```text
BagronLab/
├── io/main.bg       └── io/modules/io.bg
├── time/main.bg     └── time/modules/time.bg
├── mmap/main.bg     └── mmap/modules/mmap.bg
├── mem/main.bg      └── mem/modules/mem.bg
├── os/main.bg       └── os/modules/os.bg
└── string/main.bg   └── string/modules/{string,alphabet}.bg
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

### Archivos y rutas

`os/modules/path.bg` analiza y normaliza rutas sin abrir descriptores. Las
operaciones que modifican el sistema de archivos viven en
`os/modules/file.bg`: la clase `File` abre, lee, escribe, reposiciona, sincroniza
y cierra recursos nativos; las funciones auxiliares crean, renombran y eliminan
archivos o directorios.

Los paquetes `windows.lib` y `gnulibrary.lib` se mantienen como dependencias
de `standard/libs/` y se regeneran desde `BagronLab/windows` y
`BagronLab/gnulibrary` cuando cambian sus fuentes.
