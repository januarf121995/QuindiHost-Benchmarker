# Plan de Implementación - QuindíoHost Benchmarker MVP v1.0

Este plan detalla el diseño y la implementación de **QuindíoHost Benchmarker**, un software de escritorio para Carlos y María que centraliza la gestión del portafolio local (Cafetero Stays) y realiza análisis de precios competitivos contra los datos extraídos de Airbnb en Armenia.

## Diseño Visual "Fuera de lo Común" (Diferencial)

Para lograr un software que **no parezca en lo absoluto una página web** ni use estructuras de front tradicionales, proponemos un diseño inspirado en **instrumentos de telemetría industrial / consolas de audio profesionales**:
- **Esquema de Color**: Fondo grafito mate oscuro (`#12131C`), acentos en verde cibernético/neón (`#00F5A0`), naranja de advertencia (`#FF9E00`), y rojo crítico (`#FF4B4B`).
- **Layout Físico**: Paneles divididos por biseles marcados y texturas metálicas, simulando un hardware de control de rack analógico.
- **Visualizadores**: En lugar de tablas HTML estándar, usaremos medidores digitales tipo LED, cuadrículas de telemetría y botones táctiles industriales con efectos de iluminación y relieve.
- **Interactividad**: Perillas/dials visuales, interruptores de palanca analógicos simulados para activar/desactivar filtros de categorías (`trending`, `cabins`, `design`).

---

## Preguntas Abiertas para el Usuario

> [!IMPORTANT]
> **Por favor, revisa y responde a las siguientes preguntas en tu retroalimentación:**
> 
> 1. **¿Cómo prefieres lanzar la aplicación de escritorio?**
>    - **Opción A (Recomendada)**: Un ejecutable/script directo en Python usando `customtkinter` / `Tkinter` que abre una ventana nativa de Windows totalmente estilizada.
>    - **Opción B**: Una aplicación web local (HTML5/CSS3/JS) abierta en modo quiosco o aplicación independiente que simula un sistema operativo de ciencia ficción en pantalla completa.
> 
> 2. **Integración de Datos Iniciales**:
>    - ¿Deseas que carguemos los 15 lofts propios (Cafetero Stays) como registros por defecto usando la información del modelo de datos para que la app inicie con datos listos para probar?

---

## Cambios Propuestos

### 1. Backend y Base de Datos (SQLite)
Crearemos un script de inicialización e ingesta de datos en Python que:
- Lea los 8 archivos de la carpeta `Datos AirBnB Armenia`.
- Consolide los competidores en la tabla `competidores_scraper` calculando un `precio_base_cop` como el promedio de los precios históricos de cada listing.
- Cree la tabla `alojamientos_propios` con registros iniciales de prueba para Carlos.
- Calcule automáticamente la relación de cercanía o categoría (`relacion_benchmark`) y los estados competitivos según las reglas del PRD.

#### [NEW] [db_init.py](file:///c:/Users/janua/Documents/QUINDÍOHOST%20BENCHMARKER/db_init.py)
Script en Python para leer los libros Excel, crear la base de datos `quindiohost.db` (SQLite) y estructurar las tablas de acuerdo al modelo de datos.

### 2. Frontend de Escritorio (Python - Tkinter + Canvas / CustomTkinter)
Implementaremos la aplicación con componentes nativos de alta fidelidad estética.

#### [NEW] [app.py](file:///c:/Users/janua/Documents/QUINDÍOHOST%20BENCHMARKER/app.py)
Código principal del software de escritorio. Contendrá la interfaz del terminal industrial, la lógica de simulación de tarifas (US05) y filtros avanzados (US06).

---

## Plan de Verificación

### Pruebas Automatizadas
- Ejecución de `db_init.py` para validar la migración correcta de los registros desde los archivos Excel (conteo de listings por categoría).
- Pruebas unitarias de cálculo del badge de `estado_competitivo` según las reglas del PRD.

### Verificación Manual
- Validar que al cambiar el precio de un loft propio, el indicador de estado se actualice en tiempo real en menos de 2 segundos (RNF02).
- Probar el filtrado estricto por categoría e interactuar con los selectores del tablero analógico.
