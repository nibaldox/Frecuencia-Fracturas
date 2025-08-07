"""Componente para calibración visual de escala en imágenes."""

import streamlit as st
import numpy as np
from PIL import Image, ImageDraw
import math
from typing import Optional, Tuple


class ScaleCalibrator:
    """
    Clase para manejar la calibración visual de escala en imágenes.
    
    Permite al usuario seleccionar dos puntos en la imagen para definir
    una longitud conocida y calcular automáticamente la escala píxeles/metro.
    """
    
    def __init__(self):
        """Inicializa el calibrador de escala."""
        self.point1 = None
        self.point2 = None
        self.scale_px_per_meter = None
        self.reference_length_m = None
    
    def show_calibration_interface(self, image: np.ndarray) -> Optional[float]:
        """
        Muestra la interfaz de calibración de escala.
        
        Args:
            image: Imagen para calibrar la escala
            
        Returns:
            Escala calculada en píxeles/metro o None si no está calibrada
        """
        st.subheader("📏 Calibración de Escala")
        
        # Opciones de calibración
        calibration_method = st.radio(
            "Método de calibración:",
            ["Manual (introducir escala)", "Visual (seleccionar referencia)"],
            horizontal=True
        )
        
        if calibration_method == "Manual (introducir escala)":
            return self._manual_scale_input()
        else:
            return self._visual_scale_calibration(image)
    
    def _manual_scale_input(self) -> float:
        """
        Permite introducir la escala manualmente.
        
        Returns:
            Escala en píxeles/metro
        """
        scale_val = st.number_input(
            "Escala manual (px/m)",
            min_value=10,
            value=1000,
            step=10,
            key="manual_scale_frag",
            help="Introduce la escala conocida en píxeles por metro"
        )
        return scale_val
    
    def _visual_scale_calibration(self, image: np.ndarray) -> Optional[float]:
        """
        Implementa la calibración visual de escala.
        
        Args:
            image: Imagen para calibrar
            
        Returns:
            Escala calculada o None si no está completa
        """
        st.markdown("**Instrucciones:**")
        st.markdown("1. 📐 Introduce la longitud real de un objeto conocido en la imagen")
        st.markdown("2. 📏 Usa la herramienta de línea para medir ese objeto")
        st.markdown("3. ✅ La escala se calculará automáticamente")
        
        # Input de longitud de referencia
        reference_length = st.number_input(
            "Longitud real del objeto de referencia (metros)",
            min_value=0.001,
            value=1.0,
            step=0.1,
            format="%.3f",
            key="reference_length",
            help="Introduce la longitud real en metros del objeto que vas a medir"
        )
        
        # Simulación de selección de línea (en una implementación real usarías streamlit-drawable-canvas)
        st.markdown("**📏 Herramienta de medición:**")
        
        # Por ahora, usamos inputs numéricos para simular la selección de puntos
        # En una implementación completa, esto sería una interfaz de dibujo interactiva
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Punto inicial:**")
            x1 = st.number_input("X1 (píxeles)", min_value=0, value=100, key="x1_ref")
            y1 = st.number_input("Y1 (píxeles)", min_value=0, value=100, key="y1_ref")
        
        with col2:
            st.markdown("**Punto final:**")
            x2 = st.number_input("X2 (píxeles)", min_value=0, value=200, key="x2_ref")
            y2 = st.number_input("Y2 (píxeles)", min_value=0, value=100, key="y2_ref")
        
        # Calcular distancia en píxeles
        pixel_distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        
        if pixel_distance > 0:
            # Calcular escala
            calculated_scale = pixel_distance / reference_length
            
            # Mostrar resultados
            st.success(f"✅ **Calibración completada:**")
            st.metric("Distancia medida", f"{pixel_distance:.1f} píxeles")
            st.metric("Longitud real", f"{reference_length:.3f} metros")
            st.metric("Escala calculada", f"{calculated_scale:.1f} px/m")
            
            # Mostrar línea de referencia en la imagen
            self._show_reference_line(image, (x1, y1), (x2, y2), pixel_distance, reference_length)
            
            return calculated_scale
        
        return None
    
    def _show_reference_line(
        self, 
        image: np.ndarray, 
        point1: Tuple[int, int], 
        point2: Tuple[int, int],
        pixel_distance: float,
        real_length: float
    ) -> None:
        """
        Muestra la imagen con la línea de referencia dibujada.
        
        Args:
            image: Imagen original
            point1: Primer punto de la línea
            point2: Segundo punto de la línea
            pixel_distance: Distancia en píxeles
            real_length: Longitud real en metros
        """
        # Convertir a PIL para dibujar
        pil_image = Image.fromarray(image)
        draw = ImageDraw.Draw(pil_image)
        
        # Dibujar línea de referencia
        line_color = (255, 0, 0)  # Rojo
        line_width = 3
        draw.line([point1, point2], fill=line_color, width=line_width)
        
        # Dibujar puntos
        point_radius = 5
        for point in [point1, point2]:
            bbox = [
                point[0] - point_radius, point[1] - point_radius,
                point[0] + point_radius, point[1] + point_radius
            ]
            draw.ellipse(bbox, fill=line_color)
        
        # Mostrar imagen con línea de referencia
        st.image(
            pil_image, 
            caption=f"Línea de referencia: {pixel_distance:.1f} px = {real_length:.3f} m",
            use_container_width=True
        )


def show_advanced_fragmentation_stats(diameters_m: list) -> None:
    """
    Muestra estadísticas avanzadas de fragmentación.
    
    Args:
        diameters_m: Lista de diámetros en metros
    """
    if not diameters_m:
        return
    
    import pandas as pd
    
    # Convertir a centímetros para mejor visualización
    diameters_cm = [d * 100 for d in diameters_m]
    
    # Estadísticas básicas
    st.subheader("📊 Estadísticas de Fragmentación")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Número de partículas", len(diameters_cm))
        st.metric("Diámetro mínimo", f"{min(diameters_cm):.2f} cm")
    
    with col2:
        st.metric("Diámetro medio", f"{np.mean(diameters_cm):.2f} cm")
        st.metric("Diámetro máximo", f"{max(diameters_cm):.2f} cm")
    
    with col3:
        st.metric("Desviación estándar", f"{np.std(diameters_cm):.2f} cm")
        st.metric("Mediana", f"{np.median(diameters_cm):.2f} cm")
    
    # Percentiles
    st.subheader("📈 Análisis Granulométrico")
    
    percentiles = [10, 25, 50, 75, 90]
    perc_values = np.percentile(diameters_cm, percentiles)
    
    perc_col1, perc_col2 = st.columns(2)
    
    with perc_col1:
        for i, (p, v) in enumerate(zip(percentiles[:3], perc_values[:3])):
            st.metric(f"D{p}", f"{v:.2f} cm")
    
    with perc_col2:
        for i, (p, v) in enumerate(zip(percentiles[3:], perc_values[3:])):
            st.metric(f"D{p}", f"{v:.2f} cm")
    
    # Coeficiente de uniformidad
    if perc_values[4] > 0 and perc_values[0] > 0:  # D90 y D10
        cu = perc_values[4] / perc_values[0]  # D90/D10
        st.metric("Coeficiente de Uniformidad (Cu)", f"{cu:.2f}")
    
    # Histograma
    st.subheader("📊 Distribución de Tamaños")
    
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(5, 3))
    ax.hist(diameters_cm, bins=20, color="#4c72b0", edgecolor="black")
    ax.set_xlabel("Diámetro (cm)")
    ax.set_ylabel("Frecuencia")
    ax.set_title("Histograma de tamaños de partículas")
    st.pyplot(fig)
    
    # Tabla detallada
    with st.expander("📋 Datos detallados"):
        df_detailed = pd.DataFrame({
            "Partícula": range(1, len(diameters_cm) + 1),
            "Diámetro (cm)": diameters_cm,
            "Diámetro (m)": diameters_m
        })
        st.dataframe(df_detailed, use_container_width=True)
