"""Componente para calibración visual de escala en imágenes."""

import streamlit as st
import numpy as np
from PIL import Image, ImageDraw
import math
from typing import Optional, Tuple

try:
    from streamlit_drawable_canvas import st_canvas  # type: ignore
    _HAS_CANVAS = True
except Exception:  # noqa: BLE001
    _HAS_CANVAS = False

try:
    from streamlit_image_coordinates import streamlit_image_coordinates  # type: ignore
    _HAS_CLICK_COORDS = True
except Exception:  # noqa: BLE001
    _HAS_CLICK_COORDS = False


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
        
        st.markdown("**📏 Herramienta de medición:**")

        if not _HAS_CANVAS and not _HAS_CLICK_COORDS:
            st.info("Sin canvas ni módulo de clics. Usando entrada manual de puntos.")
            return self._manual_point_input_flow(image, reference_length)
        if not _HAS_CANVAS and _HAS_CLICK_COORDS:
            return self._click_two_point_flow(image, reference_length)

        # Canvas interactivo
        st.caption(
            "Dibuja UNA sola línea sobre el objeto de longitud conocida (herramienta Line)."
        )
        reset = st.button("🔄 Reset línea", key="reset_scale_line")
        if reset:
            st.session_state.pop("scale_canvas", None)
        try:
            canvas_result = st_canvas(
                fill_color="rgba(0, 0, 0, 0)",
                stroke_width=3,
                stroke_color="#ff0000",
                background_image=Image.fromarray(image),
                update_streamlit=True,
                height=image.shape[0],
                width=image.shape[1],
                drawing_mode="line",
                key="scale_canvas",
            )
        except AttributeError:
            # Intentar flujo de clics si está disponible antes de caer al manual
            if _HAS_CLICK_COORDS:
                st.warning(
                    "Canvas incompatible con la versión de Streamlit. Cambiando a modo de dos clics."
                )
                return self._click_two_point_flow(image, reference_length)
            st.warning(
                "Canvas incompatible con la versión de Streamlit. Usando entrada manual de puntos."
            )
            return self._manual_point_input_flow(image, reference_length)

        pixel_distance = None
        x1 = y1 = x2 = y2 = None  # placeholders
        data = getattr(canvas_result, "json_data", None)
        if data and data.get("objects"):
            # Buscar la primera línea dibujada
            for obj in data["objects"]:
                if obj.get("type") == "line":
                    # Fabric.js line: x1,y1,x2,y2 relativos al canvas
                    x1 = obj.get("x1")
                    y1 = obj.get("y1")
                    x2 = obj.get("x2")
                    y2 = obj.get("y2")
                    if None not in (x1, y1, x2, y2):
                        pixel_distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
                    break

        if pixel_distance and pixel_distance > 1 and reference_length > 0:
            calculated_scale = pixel_distance / reference_length
            st.session_state["calculated_scale_px_m"] = calculated_scale
            st.success("✅ **Calibración completada:**")
            st.metric("Distancia medida", f"{pixel_distance:.1f} px")
            st.metric("Longitud real", f"{reference_length:.3f} m")
            st.metric("Escala calculada", f"{calculated_scale:.1f} px/m")
            if None not in (x1, y1, x2, y2):
                self._show_reference_line(
                    image,
                    (int(x1), int(y1)),
                    (int(x2), int(y2)),
                    pixel_distance,
                    reference_length,
                )
            return calculated_scale

        saved_scale = st.session_state.get("calculated_scale_px_m")
        if saved_scale:
            st.info(f"Escala previa almacenada: {saved_scale:.1f} px/m (usa la misma imagen y línea para recalibrar)")
            return saved_scale
        st.info("Dibuja una línea para medir la referencia.")
        return None

    # --- Métodos auxiliares -------------------------------------------------
    def _manual_point_input_flow(self, image: np.ndarray, reference_length: float) -> Optional[float]:
        """Flujo de entrada manual de puntos de referencia.

        Parameters
        ----------
        image : np.ndarray
            Imagen referencia para mostrar línea.
        reference_length : float
            Longitud real (m) indicada por el usuario.
        """
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Punto inicial:**")
            x1 = st.number_input("X1 (píxeles)", min_value=0, value=100, key="x1_ref")
            y1 = st.number_input("Y1 (píxeles)", min_value=0, value=100, key="y1_ref")
        with col2:
            st.markdown("**Punto final:**")
            x2 = st.number_input("X2 (píxeles)", min_value=0, value=200, key="x2_ref")
            y2 = st.number_input("Y2 (píxeles)", min_value=0, value=100, key="y2_ref")
        pixel_distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        if pixel_distance > 0 and reference_length > 0:
            calculated_scale = pixel_distance / reference_length
            st.success("✅ **Calibración completada:**")
            st.metric("Distancia medida", f"{pixel_distance:.1f} píxeles")
            st.metric("Longitud real", f"{reference_length:.3f} metros")
            st.metric("Escala calculada", f"{calculated_scale:.1f} px/m")
            self._show_reference_line(
                image, (int(x1), int(y1)), (int(x2), int(y2)), pixel_distance, reference_length
            )
            return calculated_scale
        return None

    def _click_two_point_flow(self, image: np.ndarray, reference_length: float) -> Optional[float]:
        """Flujo de calibración por dos clics sobre la imagen (sin canvas)."""
        st.caption("Haz dos clics en la imagen: inicio y fin del objeto de referencia.")
        if "scale_click_points" not in st.session_state:
            st.session_state.scale_click_points = []
        reset = st.button("🔄 Reset puntos", key="reset_click_points")
        if reset:
            st.session_state.scale_click_points = []
        result = streamlit_image_coordinates(Image.fromarray(image), key="click_scale_img")
        if result and result.get("x") is not None:
            # Registrar nuevo punto sólo si cambia
            pt = (int(result["x"]), int(result["y"]))
            if not st.session_state.scale_click_points or st.session_state.scale_click_points[-1] != pt:
                st.session_state.scale_click_points.append(pt)
        pts = st.session_state.scale_click_points
        if len(pts) >= 2:
            (x1, y1), (x2, y2) = pts[-2], pts[-1]
            pixel_distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            if pixel_distance > 1 and reference_length > 0:
                calculated_scale = pixel_distance / reference_length
                st.session_state["calculated_scale_px_m"] = calculated_scale
                st.success("✅ **Calibración completada:**")
                st.metric("Distancia medida", f"{pixel_distance:.1f} px")
                st.metric("Longitud real", f"{reference_length:.3f} m")
                st.metric("Escala calculada", f"{calculated_scale:.1f} px/m")
                self._show_reference_line(image, (x1, y1), (x2, y2), pixel_distance, reference_length)
                return calculated_scale
        else:
            st.info(f"Puntos capturados: {len(pts)} / 2")
        saved_scale = st.session_state.get("calculated_scale_px_m")
        if saved_scale:
            st.info(f"Escala previa almacenada: {saved_scale:.1f} px/m")
            return saved_scale
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
