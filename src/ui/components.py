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
