"""Constantes y configuraciones de la aplicación."""

# Configuración de la página
PAGE_CONFIG = {
    "page_title": "Detector de Grietas Geotécnico",
    "layout": "wide"
}

# Configuración de la aplicación
APP_TITLE = "📷 Detector de Grietas Geotécnico"

# Configuración por defecto de parámetros
DEFAULT_VALUES = {
    "min_crack_length_px": 50,
    "scale_px_per_meter": 1000,
    "rmr_total": 50.0,
    "jn": 9.0,
    "jr": 2.0,
    "ja": 2.0,
    "jw": 1.0,
    "srf": 1.0,
    "fe": 1.0,
    "S": 3.0,
    "B": 3.0,
    "c": 1.0,
    "E": 4.0,
    "A": 5.0,
    "V": 1000.0,
    "Q_mass": 100.0,
    "RWS": 2.3,
    "scale_frag": 1000,
    "min_area_px": 200,
    "reference_length_m": 1.0
}

# Rangos de valores permitidos
VALUE_RANGES = {
    "min_crack_length_px": {"min": 10, "max": 200, "step": 10},
    "scale_px_per_meter": {"min": 10, "step": 10},
    "rmr_total": {"min": 0.0, "max": 100.0},
    "rqd_input": {"min": 0.0, "max": 100.0},
    "jn": {"min": 0.1, "max": 20.0},
    "jr": {"min": 0.1, "max": 5.0},
    "ja": {"min": 0.1, "max": 5.0},
    "jw": {"min": 0.05, "max": 1.0, "step": 0.05},
    "srf": {"min": 0.5, "max": 10.0},
    "fe": {"min": 0.1},
    "S": {"min": 0.1},
    "B": {"min": 0.1},
    "c": {"min": 0.1},
    "E": {"min": 0.1},
    "A": {"min": 0.1},
    "V": {"min": 0.1},
    "Q_mass": {"min": 0.1},
    "RWS": {"min": 0.1},
    "min_area_px": {"min": 50, "max": 1000, "step": 50},
    "reference_length_m": {"min": 0.001, "step": 0.1}
}

# Tipos de archivo permitidos
ALLOWED_IMAGE_TYPES = ["jpg", "jpeg", "png"]

# Colores para overlays
CRACK_COLOR = (255, 0, 0)  # Rojo para grietas

# Mensajes de la aplicación
MESSAGES = {
    "no_image": "Cargue una imagen para comenzar.",
    "no_particles": "No se detectaron partículas con el umbral actual.",
    "q_system_error": "Todos los factores deben ser positivos y mayores a cero.",
    "blast_error": "Verifique que c y E sean > 0.",
    "kuz_ram_error": "Todos los parámetros deben ser mayores a cero."
}
