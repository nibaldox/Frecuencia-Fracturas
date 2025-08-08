"""Componentes reutilizables de la interfaz de usuario.

Incluye:
 - Métricas resumen
 - Carga de imagen
 - Visualización configurable (altura máx, modo compacto)
 - Selectores y entradas varias
 - Redimensionamiento seguro para mantener la UI ordenada
"""

from __future__ import annotations

import streamlit as st
import numpy as np
from typing import List, Dict, Any, Optional, Tuple

try:  # opcional para redimensionar más eficiente
    import cv2  # type: ignore
except Exception:  # noqa: BLE001
    cv2 = None  # type: ignore


def mostrar_metricas_resumen(
    valid_count: int,
    frequency: float,
    rqd: float,
    rmr_total: float,
    gsi_val: Optional[float] = None,
    q_val: Optional[float] = None,
    q_spec: Optional[float] = None,
    xm_val: Optional[float] = None,
) -> None:
    """Muestra métricas clave en columnas compactas."""
    st.header("📊 Resumen de resultados")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Grietas detectadas", valid_count)
        st.metric("Frecuencia (grietas/m)", f"{frequency:.2f}")
        st.metric("RQD (%)", f"{rqd:.1f}")
        if gsi_val is not None:
            st.metric("GSI", f"{gsi_val:.1f}")
    with col2:
        st.metric("RMR", f"{rmr_total:.1f}")
        if q_val is not None:
            st.metric("Q-System", f"{q_val:.3f}")
        if q_spec is not None:
            st.metric("Carga específica q (kg/m³)", f"{q_spec:.2f}")
        if xm_val is not None:
            st.metric("Tamaño medio Xm (cm)", f"{xm_val:.2f}")


def configurar_sidebar() -> int:
    """Configura parámetros base en la barra lateral."""
    st.sidebar.header("⚙️ Configuración")
    min_crack_length_px = st.sidebar.slider(
        "Longitud mínima de grieta (px)", 10, 200, value=50, step=10
    )
    return min_crack_length_px


def configuracion_display() -> Tuple[int, bool]:
    """Controles de apariencia (altura máx y modo compacto)."""
    st.sidebar.subheader("🖼️ Visualización")
    max_h = st.sidebar.slider(
        "Altura máx. imágenes (px)", 300, 1000, 500, 50,
        help="Sólo cambia la visualización, no el procesamiento."
    )
    compact = st.sidebar.checkbox(
        "Modo compacto (usar pestañas)", value=False,
        help="Ahorra espacio vertical agrupando imágenes."
    )
    return max_h, compact


def cargar_imagen():  # noqa: ANN201
    """Widget de carga de imagen."""
    st.header("1️⃣ Cargar imagen")
    uploaded_file = st.file_uploader(
        "Seleccione una imagen de la grieta (jpg, png)",
        type=["jpg", "jpeg", "png"],
    )
    return uploaded_file


def _resize_for_display(img: np.ndarray, max_height: int) -> np.ndarray:
    """Redimensiona manteniendo aspecto si excede altura máxima."""
    if max_height <= 0:
        return img
    h, w = img.shape[:2]
    if h <= max_height:
        return img
    scale = max_height / h
    new_size = (int(w * scale), max_height)
    if cv2 is not None:
        return cv2.resize(img, new_size, interpolation=cv2.INTER_AREA)
    return img


def mostrar_deteccion_grietas(
    edges: np.ndarray,
    annotated: np.ndarray,
    *,
    max_height: int = 500,
    compact: bool = False,
) -> None:
    """Render de detección de grietas (layout flexible)."""
    st.header("2️⃣ Detección de grietas")
    edges_disp = _resize_for_display(edges, max_height)
    ann_disp = _resize_for_display(annotated, max_height)

    if compact:
        t1, t2 = st.tabs(["Grietas", "Bordes"])
        with t1:
            st.image(ann_disp, use_container_width=True, caption="Grietas detectadas")
        with t2:
            st.image(
                edges_disp,
                clamp=True,
                use_container_width=True,
                caption="Bordes / Esqueletización",
            )
    else:
        col1, col2 = st.columns([3, 2])
        with col1:
            st.subheader("Grietas detectadas")
            st.image(ann_disp, use_container_width=True)
        with col2:
            st.subheader("Bordes / Esqueletización")
            st.image(edges_disp, clamp=True, use_container_width=True)


def selector_grietas_excluir(crack_info: List[Dict[str, Any]]) -> List[int]:
    """Selector de grietas a excluir."""
    all_ids = [c["id"] for c in crack_info]
    excluded_ids = st.multiselect(
        "IDs de grietas a excluir", options=all_ids, help="Deselecciona ruido o falsas detecciones."
    )
    return excluded_ids


def input_escala() -> float:
    """Input de escala px/m manual si se conoce."""
    scale_val = st.number_input(
        "Escala – píxeles por metro (px/m)",
        min_value=10,
        value=1000,
        step=10,
        key="scale_px",
    )
    return scale_val


def input_rmr() -> float:
    """Input de RMR total."""
    rmr_total = st.number_input(
        "RMR total – Rock Mass Rating (Valoración del Macizo Rocoso) [0-100]",
        min_value=0.0,
        max_value=100.0,
        value=50.0,
        key="rmr_total",
    )
    return rmr_total

"""Componentes reutilizables de la interfaz de usuario."""

import streamlit as st
import numpy as np
from typing import List, Dict, Any, Optional


def mostrar_metricas_resumen(
    valid_count: int,
    frequency: float,
    rqd: float,
    rmr_total: float,
    gsi_val: Optional[float] = None,
    q_val: Optional[float] = None,
    q_spec: Optional[float] = None,
    xm_val: Optional[float] = None
) -> None:
    """
    Muestra un resumen de las métricas calculadas en formato de columnas.
    
    Args:
        valid_count: Número de grietas detectadas válidas
        frequency: Frecuencia de grietas por metro
        rqd: Rock Quality Designation
        rmr_total: Rock Mass Rating total
        gsi_val: Geological Strength Index (opcional)
        q_val: Valor del Q-System (opcional)
        q_spec: Carga específica de voladura (opcional)
        xm_val: Tamaño medio de fragmentación (opcional)
    """
    st.header("📊 Resumen de resultados")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Grietas detectadas", valid_count)
        st.metric("Frecuencia (grietas/m)", f"{frequency:.2f}")
        st.metric("RQD (%)", f"{rqd:.1f}")
        if gsi_val is not None:
            st.metric("GSI", f"{gsi_val:.1f}")
    
    with col2:
        st.metric("RMR", f"{rmr_total:.1f}")
        if q_val is not None:
            st.metric("Q-System", f"{q_val:.3f}")
        if q_spec is not None:
            st.metric("Carga específica q (kg/m³)", f"{q_spec:.2f}")
        if xm_val is not None:
            st.metric("Tamaño medio Xm (cm)", f"{xm_val:.2f}")


def configurar_sidebar() -> int:
    """
    Configura la barra lateral con controles de configuración.
    
    Returns:
        int: Longitud mínima de grieta en píxeles
    """
    st.sidebar.header("⚙️ Configuración")
    min_crack_length_px = st.sidebar.slider(
        "Longitud mínima de grieta (px)", 
        10, 200, 
        value=50, 
        step=10
    )
    return min_crack_length_px


def cargar_imagen():
    """
    Muestra los controles para cargar una imagen desde archivo.
    
    Returns:
        Imagen cargada desde archivo, o None si no hay imagen
    """
    st.header("1️⃣ Cargar imagen")
    uploaded_file = st.file_uploader(
        "Seleccione una imagen de la grieta (jpg, png)",
        type=["jpg", "jpeg", "png"],
    )
    
    return uploaded_file


def mostrar_deteccion_grietas(edges: np.ndarray, annotated: np.ndarray) -> None:
    """
    Muestra los resultados de la detección de grietas en dos columnas.
    
    Args:
        edges: Imagen de bordes/esqueletización
        annotated: Imagen con grietas anotadas
    """
    st.header("2️⃣ Detección de grietas")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Bordes / Esqueletización")
        st.image(edges, clamp=True)
    
    with col2:
        st.subheader("Grietas detectadas")
        st.image(annotated, use_container_width=True)


def selector_grietas_excluir(crack_info: List[Dict[str, Any]]) -> List[int]:
    """
    Muestra un selector múltiple para excluir grietas del análisis.
    
    Args:
        crack_info: Lista de información de grietas detectadas
        
    Returns:
        Lista de IDs de grietas a excluir
    """
    all_ids = [c["id"] for c in crack_info]
    excluded_ids = st.multiselect(
        "IDs de grietas a excluir", 
        options=all_ids
    )
    return excluded_ids


def input_escala() -> float:
    """
    Muestra el input para configurar la escala de píxeles por metro.
    
    Returns:
        Valor de escala en píxeles por metro
    """
    scale_val = st.number_input(
        "Escala – píxeles por metro (px/m)",
        min_value=10,
        value=1000,
        step=10,
        key="scale_px",
    )
    return scale_val


def input_rmr() -> float:
    """
    Muestra el input para el Rock Mass Rating.
    
    Returns:
        Valor del RMR
    """
    rmr_total = st.number_input(
        "RMR total – Rock Mass Rating (Valoración del Macizo Rocoso) [0-100]",
        min_value=0.0,
        max_value=100.0,
        value=50.0,
        key="rmr_total",
    )
    return rmr_total
