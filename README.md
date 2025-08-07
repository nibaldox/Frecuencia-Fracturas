# 📷 Detector de Grietas Geotécnico

## Versión 2.0 - Refactorizada

Aplicación moderna en **Python + Streamlit** para detectar grietas en imágenes y calcular parámetros geotécnicos clave. Incluye análisis de frecuencia de discontinuidades, RQD, GSI, RMR, Q-System y cálculos de voladura/fragmentación.

## ✨ Características Principales

- 📷 **Carga de imágenes**: Desde archivo
- 🔍 **Detección automática**: Algoritmos avanzados de detección de grietas
- 📊 **Métricas geotécnicas**: RQD, RMR, GSI, Q-System completos
- 💥 **Diseño de voladura**: Cálculos Langefors-Kihlström
- 🧩 **Análisis de fragmentación**: Modelo Kuz-Ram y detección de partículas
- 📏 **Calibración visual de escala**: Selecciona puntos de referencia para mediciones precisas
- 📈 **Estadísticas avanzadas**: Diámetros, distribución y métricas detalladas de fragmentación
- ✂️ **Selección ROI**: Recorte interactivo de áreas de interés
- 📊 **Reportes visuales**: Resúmenes, histogramas y métricas en tiempo real
- 💾 **Exportación de datos**: Resultados en formato CSV para análisis posterior

## 🛠️ Requisitos del Sistema

- **Python** ≥ 3.9
- **Sistema operativo**: Windows, macOS, Linux
- **Memoria RAM**: Mínimo 4GB recomendado

## 📊 Exportación de Resultados

La aplicación permite exportar los resultados del análisis para su posterior procesamiento:

- **Datos de fragmentación**: Exporta las métricas detalladas de cada partícula detectada
- **Estadísticas resumidas**: Incluye todas las métricas calculadas en un formato tabular
- **Formato CSV**: Compatible con hojas de cálculo y herramientas de análisis de datos
- **Nombres descriptivos**: Los archivos exportados incluyen marcas de tiempo para fácil seguimiento

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone <repository-url>
cd calculo-ff
```

### 2. Crear entorno virtual (recomendado)

```bash
# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
# En Windows:
.venv\Scripts\activate
# En macOS/Linux:
source .venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

## 🏃 Uso de la Aplicación

### Iniciar la aplicación

```bash
streamlit run app.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`

### Flujo de trabajo

1. **📷 Cargar imagen**:
   - Sube una imagen desde archivo (JPG, PNG)

2. **✂️ Seleccionar ROI**:
   - Recorta la región de interés interactivamente
   - Ajusta el área de análisis según necesites

3. **🔍 Análisis de Fracturas**:
   - Visualiza grietas detectadas automáticamente
   - Excluye grietas no relevantes si es necesario
   - Configura parámetros de escala y análisis

4. **🧩 Análisis de Fragmentación**:
   - Detecta y mide partículas automáticamente
   - Calcula diámetros y distribuciones de tamaño

5. **📊 Resultados**:
   - Revisa métricas calculadas en tiempo real
   - Exporta resultados para análisis posterior

## 🏢 Arquitectura del Proyecto

### Estructura Modular (v2.0)

```text
calculo-ff/
├── app.py                    # 🏠 Aplicación principal Streamlit
├── plan_implementacion.md    # 📝 Seguimiento de desarrollo
├── src/                      # 📚 Módulos principales
│   ├── ui/                   # 🎨 Interfaz de usuario
│   │   ├── __init__.py
│   │   ├── components.py     # Componentes reutilizables
│   │   └── tabs.py           # Lógica de pestañas
│   ├── core/                 # ⚙️ Lógica de procesamiento
│   │   ├── __init__.py
│   │   └── image_processor.py # Procesamiento de imágenes
│   ├── utils/                # 🔧 Utilidades y constantes
│   │   ├── __init__.py
│   │   └── constants.py      # Configuraciones
│   ├── crack_detection.py    # 🔍 Algoritmos de detección
│   ├── fragmentation.py      # 🧩 Análisis de fragmentación
│   ├── image_io.py           # 📷 Manejo de imágenes
│   └── metrics.py            # 📊 Cálculos geotécnicos
├── Docs/                     # 📚 Documentación técnica
├── requirements.txt          # 📦 Dependencias Python
├── README.md                 # 📝 Este archivo
└── .gitignore                # 🚫 Exclusiones de Git
```

### Principios de Diseño

- **🧩 Modularidad**: Separación clara de responsabilidades
- **🔄 Reutilización**: Componentes reutilizables y bien documentados
- **📚 Clean Code**: Código limpio y fácil de mantener
- **📈 Escalabilidad**: Arquitectura preparada para futuras extensiones
- **📝 Documentación**: Docstrings completos y comentarios explicativos

## 📏 Calibración Visual de Escala

La aplicación incluye una herramienta avanzada para calibrar la escala de medición en imágenes, permitiendo mediciones precisas de fragmentos y grietas:

### Características de la Calibración Visual

- **Selección de puntos de referencia**: Define dos puntos en la imagen que representen una distancia conocida
- **Ajuste fino de coordenadas**: Control preciso de las posiciones X e Y de los puntos de referencia
- **Visualización en tiempo real**: Muestra la línea de calibración sobre la imagen
- **Cálculo automático de escala**: Convierte píxeles a unidades reales (metros, centímetros, etc.)
- **Configuración de longitud de referencia**: Especifica la distancia real entre los puntos seleccionados

### Cómo usar la calibración visual:

1. **Activa la calibración** en la pestaña de Análisis de Fragmentación
2. **Selecciona dos puntos** en la imagen que representen una distancia conocida
3. **Ajusta las coordenadas** si es necesario para mayor precisión
4. **Especifica la longitud real** entre los puntos en metros
5. **La escala se aplica automáticamente** a todas las mediciones posteriores

## 📊 Métricas y Cálculos

### Parámetros Geotécnicos

- **RQD** (Rock Quality Designation)
- **RMR** (Rock Mass Rating)
- **GSI** (Geological Strength Index)
- **Q-System** (Barton et al.)

### Diseño de Voladura

- **Langefors-Kihlström** (Carga específica)
- **Kuz-Ram** (Fragmentación)

### Análisis de Imágenes

- **Detección de grietas** con OpenCV
- **Segmentación de partículas** automática
- **Cálculo de frecuencias** y distribuciones
- **Estadísticas avanzadas**:
  - Diámetros mínimos, máximos y medios
  - Desviación estándar y mediana
  - Percentiles (D10, D25, D50, D75, D90)
  - Coeficiente de uniformidad (Cu)
  - Histograma de distribución de tamaños

## 🔧 Desarrollo y Contribución

Se siguen los principios de *Clean Code*. Todo el código está comentado y anotado. Los *pull requests* son bienvenidos.

## Licencia

MIT

## Creado por N.A.V
