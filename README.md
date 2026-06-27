# QuindíoHost Benchmarker // Telemetría de Precios MVP v1.0

Este repositorio contiene la implementación del **QuindíoHost Benchmarker**, un software de escritorio desarrollado para **Cafetero Stays** en Armenia, Quindío. Permite a los administradores de rentas vacacionales simular tarifas base, analizar la competitividad comercial del portafolio y reaccionar ante alertas reputacionales utilizando datos extraídos del scraper de Airbnb.

---

## 🚀 Características Principales

*   **Interfaz de Escritorio de Telemetría**: Una UI premium diseñada con `customtkinter` inspirada en consolas de control industrial y hardware de audio analógico (completamente alejada del diseño web tradicional).
*   **Base de Datos SQLite**: Almacenamiento local estructurado bajo un modelo de datos relacional que vincula el inventario propio con el scraper de la competencia.
*   **Simulador en Caliente ("Reactor de Precios")**: Permite deslizar precios y recalcular automáticamente el estado competitivo (`Excellent`, `Precio Alto`, `Alerta de Reseñas`, `Crítico`) en menos de 2 segundos.
*   **Renderizador de Planos CAD**: Visualizador interactivo de planos vectoriales tipo blueprint (en un Tkinter Canvas) correspondiente a la categoría del loft seleccionado (`design`, `cabins`, `trending`).
*   **Gestión de Inventario (CRUD)**: Creación, edición y baja de propiedades del portafolio nativas desde el software.
*   **Carga Asíncrona de Imágenes**: Descarga y visualización en segundo plano de las fotografías de la competencia mediante hilos de ejecución independientes para un rendimiento fluido.

---

## 🛠️ Requisitos e Instalación

### 1. Clonar el repositorio
```bash
git clone <URL_DE_TU_REPOSITORIO>
cd QUINDIOHOST-BENCHMARKER
```

### 2. Instalar dependencias
Asegúrate de tener Python 3.10+ instalado. Ejecuta el siguiente comando para instalar las librerías necesarias:
```bash
pip install pandas openpyxl customtkinter Pillow
```

### 3. Inicializar la Base de Datos
El sistema utiliza los libros de Excel ubicados en la carpeta `Datos AirBnB Armenia` como fuente de verdad para la competencia. Para procesar e importar los datos por primera vez a la base de datos local SQLite (`quindiohost.db`), ejecuta:
```bash
python db_init.py
```

### 4. Lanzar la Aplicación
Una vez inicializada la base de datos, inicia la consola de control:
```bash
python app.py
```

---

## 📊 Modelo de Datos Relacional

El sistema estructura la información en tres tablas principales en SQLite:
1.  **`alojamientos_propios`**: Registra el portafolio interno administrado por la agencia (con precio actual, categoría propia, calificación y zona).
2.  **`competidores_scraper`**: Almacena los registros del mercado externo en Armenia extraídos del scraper.
3.  **`relacion_benchmark`**: Tabla intermedia que asocia qué alojamientos competidores directos afectan a cada loft propio para el análisis comparativo.

---

## 🎨 Capturas y Estructura Visual

*   **Fondo principal**: Grafito Mate (`#0B0C10` / `#1F2833`)
*   **Acción/Foco**: Cian Eléctrico (`#66FCF1`)
*   **Métricas y LED de Estado**:
    *   🟢 Verde (`Excellent`): Precio competitivo y buena reputación.
    *   🟡 Naranja (`Precio Alto`): Precio por encima del promedio del mercado.
    *   🔴 Rojo (`Alerta de Reseñas` / `Crítico`): Baja calificación o combinación de precio alto y baja reputación.
