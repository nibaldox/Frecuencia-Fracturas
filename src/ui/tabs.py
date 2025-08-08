"""Lógica de las pestañas de la aplicación."""

import streamlit as st
import numpy as np
import pandas as pd
from typing import Optional
import hashlib

from src import crack_detection, image_io, metrics, fragmentation
from src.ui.components import (
    mostrar_deteccion_grietas,
    selector_grietas_excluir,
    input_escala,
    input_rmr,
    configuracion_display,
)


def tab_fracturas(image: np.ndarray, min_crack_length_px: int) -> dict:
    """
    Maneja la lógica de la pestaña de análisis de fracturas.
    
    Args:
        image: Imagen a analizar
        min_crack_length_px: Longitud mínima de grieta en píxeles
        
    Returns:
        dict: Diccionario con los resultados del análisis
    """
    # Detección de grietas
    edges, crack_mask, crack_info = crack_detection.detect_cracks(
        image, min_length_px=min_crack_length_px
    )

    # Configuración de display (altura máx / modo compacto)
    max_h, compact = configuracion_display()

    # Crear overlay y anotaciones
    base_overlay = image_io.overlay_mask(image, crack_mask, color=(255, 0, 0))
    excluded_ids = selector_grietas_excluir(crack_info)
    annotated = image_io.annotate_cracks(
        base_overlay, crack_info, excluded_ids=set(excluded_ids)
    )
    
    # Mostrar resultados de detección
    # Llamada robusta (si el servidor mantiene versión previa sin parámetros nuevos)
    try:
        mostrar_deteccion_grietas(edges, annotated, max_height=max_h, compact=compact)
    except TypeError:
        # Fallback a versión anterior (sin redimensionamiento configurable)
        mostrar_deteccion_grietas(edges, annotated)

    # Métricas geotécnicas
    st.header("3️⃣ Métricas geotécnicas")
    # Hash de la imagen (ROI) para validar reutilización de escala calibrada
    image_hash = hashlib.sha256(image.tobytes()).hexdigest()[:8]

    global_scale = st.session_state.get("global_scale_px_m")
    global_hash = st.session_state.get("global_scale_img_hash")
    force_manual = st.session_state.get("force_manual_scale", False)

    scale_val: float
    if global_scale and global_hash == image_hash and not force_manual:
        col_g1, col_g2 = st.columns([4,1])
        with col_g1:
            st.info(f"Usando escala calibrada global: {global_scale:.1f} px/m (img {image_hash})")
        with col_g2:
            if st.button("Editar manual", key="btn_manual_scale"):
                st.session_state["force_manual_scale"] = True
                st.experimental_rerun()
        scale_val = float(global_scale)
    else:
        if global_scale and global_hash != image_hash:
            st.warning("La escala calibrada pertenece a otra imagen; introduce una nueva escala manual o recalibra en Fragmentación.")
        scale_val = input_escala()
        col_m1, col_m2 = st.columns([3,2])
        with col_m1:
            if st.button("Volver a escala calibrada" , disabled=not (global_scale and global_hash==image_hash), key="btn_back_global"):
                st.session_state["force_manual_scale"] = False
                st.experimental_rerun()
        with col_m2:
            if st.button("Limpiar escala global", key="btn_clear_global"):
                for k in ("global_scale_px_m","global_scale_img_hash"):
                    st.session_state.pop(k, None)
                st.session_state["force_manual_scale"] = True
                st.experimental_rerun()

    # Mostrar tabla detallada de grietas con longitud y orientación
    if crack_info:
        with st.expander("Detalles de grietas detectadas"):
            import pandas as pd
            # Filtro longitud mínima en metros (derivado) opcional
            min_len_m = st.number_input(
                "Longitud mínima (m) para incluir en tabla (0 = sin filtro)",
                min_value=0.0,
                value=0.0,
                step=0.05,
                key="min_len_filter_m",
            )
            rows = []
            for c in crack_info:
                if c["id"] in excluded_ids:
                    continue
                length_m = c.get("length_px", 0) / scale_val if scale_val > 0 else None
                if min_len_m > 0 and (length_m is None or length_m < min_len_m):
                    continue
                rows.append(
                    {
                        "ID": c["id"],
                        "Longitud_px": c.get("length_px"),
                        "Longitud_m": round(length_m, 4) if length_m is not None else None,
                        "Longitud_eje_mayor_px": round(c.get("length_major_px", 0), 1),
                        "Longitud_eje_mayor_m": round(c.get("length_major_px", 0) / scale_val, 4)
                        if scale_val > 0
                        else None,
                        "Orientacion_deg": None if c.get("orientation_deg") is None else round(c.get("orientation_deg"), 1),
                        "Area_px": c.get("area"),
                    }
                )
            if rows:
                df_cracks = pd.DataFrame(rows)
                st.dataframe(df_cracks, use_container_width=True, hide_index=True)
                # Estadísticas rápidas de longitud
                lengths_m = [r["Longitud_m"] for r in rows if r["Longitud_m"] is not None]
                if lengths_m:
                    st.markdown("**Estadísticas de longitudes (m):**")
                    col_a, col_b, col_c, col_d = st.columns(4)
                    col_a.metric("Promedio", f"{np.mean(lengths_m):.4f}")
                    col_b.metric("Mediana", f"{np.median(lengths_m):.4f}")
                    col_c.metric("Máx", f"{np.max(lengths_m):.4f}")
                    col_d.metric("Cuenta", len(lengths_m))
            else:
                st.info("No hay grietas que cumplan el filtro actual.")
    
    # Calcular métricas básicas
    valid_count = len(crack_info) - len(excluded_ids)
    frequency = metrics.crack_frequency(
        valid_count, image.shape[1], scale_px_per_meter=scale_val
    )
    rqd = metrics.rqd_from_frequency(frequency)

    # Parámetros adicionales
    st.header("4️⃣ Parámetros adicionales (opcional)")
    rmr_total = input_rmr()
    gsi_val = metrics.gsi_from_rmr(rmr_total) if rmr_total > 0 else None

    # Q-System
    q_val = _mostrar_q_system(rqd)
    
    # Diseño de voladura
    q_spec = _mostrar_diseno_voladura()
    
    # Fragmentación Kuz-Ram
    xm_val = _mostrar_fragmentacion_kuz_ram()

    return {
        'valid_count': valid_count,
        'frequency': frequency,
        'rqd': rqd,
        'rmr_total': rmr_total,
        'gsi_val': gsi_val,
        'q_val': q_val,
        'q_spec': q_spec,
        'xm_val': xm_val
    }


def tab_fragmentacion(image: np.ndarray) -> None:
    """
    Maneja la lógica de la pestaña de análisis de fragmentación.
    
    Args:
        image: Imagen a analizar para fragmentación
    """
    from src.ui.scale_calibration import ScaleCalibrator, show_advanced_fragmentation_stats
    
    st.header("🧩 Análisis de Fragmentación")
    
    # Calibración de escala
    calibrator = ScaleCalibrator()
    scale_frag = calibrator.show_calibration_interface(image)
    
    if scale_frag is None:
        st.warning("⚠️ Por favor, calibra la escala antes de continuar con el análisis.")
        return
    else:
        # Guardar escala global reutilizable con hash
        image_hash = hashlib.sha256(image.tobytes()).hexdigest()[:8]
        st.session_state["global_scale_px_m"] = float(scale_frag)
        st.session_state["global_scale_img_hash"] = image_hash
        # Si se estaba forzando modo manual, lo liberamos para permitir reutilización
        if st.session_state.get("force_manual_scale"):
            st.session_state["force_manual_scale"] = False
    
    # Separador visual
    st.divider()
    
    # Parámetros de detección
    st.subheader("⚙️ Parámetros de Detección")
    
    col1, col2 = st.columns(2)
    with col1:
        min_area_px = st.slider(
            "Tamaño mínimo de partícula (px)",
            min_value=50,
            max_value=1000,
            value=200,
            step=50,
            key="min_area_frag",
            help="Partículas menores se descartarán como ruido"
        )
    
    with col2:
        # Mostrar tamaño mínimo en metros
        min_area_m2 = min_area_px / (scale_frag ** 2)
        min_diameter_m = 2 * (min_area_m2 / 3.14159) ** 0.5
        st.metric(
            "Tamaño mínimo equivalente",
            f"{min_diameter_m * 100:.2f} cm",
            help="Diámetro mínimo equivalente en centímetros"
        )
    
    # Análisis de tamaños de partículas
    st.subheader("🔍 Detección de Partículas")
    
    with st.spinner("Analizando fragmentación..."):
        diameters_m, labeled_img = fragmentation.particle_sizes(
            image, 
            scale_px_per_meter=scale_frag,
            min_area_px=min_area_px
        )
    
    # Mostrar imagen segmentada
    st.image(
        labeled_img, 
        caption=f"Partículas segmentadas (Escala: {scale_frag:.1f} px/m)", 
        use_container_width=True
    )
    
    # Resultados y estadísticas
    if diameters_m:
        show_advanced_fragmentation_stats(diameters_m)
        
        # Opción de descarga
        st.subheader("💾 Exportar Resultados")
        
        # Preparar datos para descarga
        import pandas as pd
        
        results_df = pd.DataFrame({
            "Particula": range(1, len(diameters_m) + 1),
            "Diametro_m": diameters_m,
            "Diametro_cm": [d * 100 for d in diameters_m],
            "Area_m2": [(d/2)**2 * 3.14159 for d in diameters_m]
        })
        
        # Agregar estadísticas de resumen
        summary_stats = {
            "Estadistica": ["Numero_particulas", "Diametro_medio_cm", "Diametro_mediano_cm", 
                           "Desviacion_estandar_cm", "D10_cm", "D50_cm", "D90_cm"],
            "Valor": [
                len(diameters_m),
                np.mean(diameters_m) * 100,
                np.median(diameters_m) * 100,
                np.std(diameters_m) * 100,
                np.percentile(diameters_m, 10) * 100,
                np.percentile(diameters_m, 50) * 100,
                np.percentile(diameters_m, 90) * 100
            ]
        }
        
        summary_df = pd.DataFrame(summary_stats)
        
        # Botón de descarga
        csv_data = results_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📊 Descargar datos detallados (CSV)",
            data=csv_data,
            file_name=f"fragmentacion_detallada_{scale_frag:.0f}pxm.csv",
            mime="text/csv"
        )
        
        csv_summary = summary_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📊 Descargar resumen estadístico (CSV)",
            data=csv_summary,
            file_name=f"fragmentacion_resumen_{scale_frag:.0f}pxm.csv",
            mime="text/csv"
        )
        
    else:
        st.warning("⚠️ No se detectaron partículas con los parámetros actuales.")
        st.info("💡 **Sugerencias:**")
        st.markdown("- Reduce el tamaño mínimo de partícula")
        st.markdown("- Verifica que la imagen tenga suficiente contraste")
        st.markdown("- Ajusta la calibración de escala")


def _mostrar_q_system(rqd: float) -> Optional[float]:
    """
    Muestra los controles para el cálculo del Q-System.
    
    Args:
        rqd: Valor RQD calculado
        
    Returns:
        Valor Q calculado o None si hay error
    """
    q_val = None
    with st.expander("Q-System (Barton)"):
        rqd_input = st.number_input(
            "RQD (%)", min_value=0.0, max_value=100.0, value=rqd, key="rqd_input"
        )
        jn = st.number_input(
            "Jn – Número de familias de juntas (Joint set number)",
            min_value=0.1, max_value=20.0, value=9.0, key="jn"
        )
        jr = st.number_input(
            "Jr – Rugosidad de la junta (Joint roughness)",
            min_value=0.1, max_value=5.0, value=2.0, key="jr"
        )
        ja = st.number_input(
            "Ja – Alteración de la junta (Joint alteration)",
            min_value=0.1, max_value=5.0, value=2.0, key="ja"
        )
        jw = st.number_input(
            "Jw – Condición de agua (Joint water)",
            min_value=0.05, max_value=1.0, value=1.0, step=0.05, key="jw"
        )
        srf = st.number_input(
            "SRF – Factor de reducción de tensión (Stress Reduction Factor)",
            min_value=0.5, max_value=10.0, value=1.0, key="srf"
        )
        
        try:
            q_val = metrics.q_system(rqd_input, jn, jr, ja, jw, srf)
            st.markdown(f"**Q = {q_val}**")
        except ValueError:
            st.error("Todos los factores deben ser positivos y mayores a cero.")
    
    return q_val


def _mostrar_diseno_voladura() -> Optional[float]:
    """
    Muestra los controles para el diseño de voladura Langefors-Kihlström.
    
    Returns:
        Carga específica calculada o None si hay error
    """
    q_spec = None
    with st.expander("Diseño de voladura L–K"):
        fe = st.number_input("Eficiencia fe", min_value=0.1, value=1.0, key="fe")
        S_val = st.number_input("Espaciamiento S (m)", min_value=0.1, value=3.0, key="S")
        B_val = st.number_input("Burden B (m)", min_value=0.1, value=3.0, key="B")
        c_val = st.number_input("Constante de roca c", min_value=0.1, value=1.0, key="c")
        E_val = st.number_input("Energía explosiva E (MJ/kg)", min_value=0.1, value=4.0, key="E")
        
        try:
            q_spec = metrics.blast_lk(fe, S_val, B_val, c_val, E_val)
            st.markdown(f"**Carga específica q = {q_spec} kg/m³**")
        except ValueError:
            st.error("Verifique que c y E sean > 0.")
    
    return q_spec


def _mostrar_fragmentacion_kuz_ram() -> Optional[float]:
    """
    Muestra los controles para el cálculo de fragmentación Kuz-Ram.
    
    Returns:
        Tamaño medio calculado o None si hay error
    """
    xm_val = None
    with st.expander("Fragmentación Kuz–Ram"):
        A_val = st.number_input("Factor de roca A", min_value=0.1, value=5.0, key="A")
        V_val = st.number_input("Volumen de banco V (m³)", min_value=0.1, value=1000.0, key="V")
        Q_mass = st.number_input(
            "Carga de explosivo Q (kg)", min_value=0.1, value=100.0, key="Qmass"
        )
        RWS_val = st.number_input(
            "Resistencia relativa RWS", min_value=0.1, value=2.3, key="RWS"
        )
        
        try:
            xm_val = metrics.kuz_ram(A_val, V_val, Q_mass, RWS_val)
            st.markdown(f"**Tamaño medio Xm = {xm_val} cm**")
        except ValueError:
            st.error("Todos los parámetros deben ser mayores a cero.")
    
    return xm_val
