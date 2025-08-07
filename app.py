"""Aplicación Streamlit para detección de grietas y cálculos geotécnicos.

Esta aplicación permite:
- Cargar imágenes desde archivo o cámara
- Detectar grietas automáticamente
- Calcular métricas geotécnicas (RQD, RMR, GSI, Q-System)
- Analizar fragmentación de rocas
- Diseñar parámetros de voladura

Ejecuta con:
    streamlit run app.py

Autor: Sistema de Detección de Grietas
Versión: 2.0 - Refactorizada
"""

import streamlit as st

from src.core.image_processor import ImageProcessor
from src.ui.components import (
    configurar_sidebar, 
    cargar_imagen, 
    mostrar_metricas_resumen
)
from src.ui.tabs import tab_fracturas, tab_fragmentacion
from src.utils.constants import PAGE_CONFIG, APP_TITLE, MESSAGES


def main() -> None:
    """
    Función principal de la aplicación Streamlit.
    
    Configura la interfaz, maneja el flujo de la aplicación y coordina
    el procesamiento de imágenes con el análisis geotécnico.
    """
    # Configuración de la página
    st.set_page_config(**PAGE_CONFIG)
    st.title(APP_TITLE)
    
    # Configuración de la barra lateral
    min_crack_length_px = configurar_sidebar()
    
    # Carga de imagen
    image_source = cargar_imagen()
    
    if image_source is not None:
        # Procesar imagen
        processor = ImageProcessor()
        image_orig = processor.load_and_display_image(image_source)
        image = processor.crop_image_roi(image_orig)
        
        # Pestañas de análisis
        fract_tab, frag_tab = st.tabs(["Fracturas", "Fragmentación"])
        
        with fract_tab:
            # Análisis de fracturas y métricas geotécnicas
            resultados = tab_fracturas(image, min_crack_length_px)
            
            # Mostrar resumen de resultados
            mostrar_metricas_resumen(**resultados)
        
        with frag_tab:
            # Análisis de fragmentación
            tab_fragmentacion(image)
    
    else:
        st.info(MESSAGES["no_image"])


if __name__ == "__main__":
    main()
