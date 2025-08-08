# Plan de Mejoras – Detector de Grietas y Fragmentación

Fecha: 2025-08-08  
Versión del documento: 1.0

## 1. Estado Actual
Arquitectura modular y clara:
- `app.py` coordina UI principal.
- Núcleo de procesamiento: `crack_detection.py`, `fragmentation.py`, `metrics.py`, `image_io.py`, `core/image_processor.py`.
- UI separada en `ui/` (componentes, tabs, calibración escala).
- Mejoras ya implementadas recientemente:
  - Cálculo de longitud de grietas (conteo de píxeles de esqueleto).
  - Cálculo de eje mayor y orientación (PCA) por grieta.
  - Tabla detallada con filtro por longitud en metros + estadísticas.
  - Calibración de escala interactiva con línea (persistencia en `session_state`).
  - Filtro de exclusión manual de grietas.

Limitaciones actuales:
- Longitud aproximada (no geodésica ponderada por diagonales).
- Sin exportación de resultados de grietas (solo fragmentación CSV).
- Sin cache de cómputos → recomputación innecesaria.
- No hay tests automatizados.
- Segmentación de fragmentación básica (Otsu, sin watershed).
- No se almacenan metadatos/escala en resultados descargados.

## 2. Objetivos Generales
1. Aumentar precisión de mediciones de discontinuidades.  
2. Mejorar rendimiento y reproducibilidad (cache, escalado controlado).  
3. Añadir exportaciones completas y trazabilidad (hash imagen, parámetros).  
4. Robustecer código con pruebas y validaciones.  
5. Preparar la base para algoritmos más avanzados (ML / clustering / watershed).  
6. Enriquecer análisis estructural (orientaciones, agrupaciones).  

## 3. Backlog Priorizado (Resumen)
Orden recomendado por impacto/rapidez:
- A. Rendimiento + Exportación básica
- B. Precisión longitud + Filtros avanzados
- C. Testing + Calidad
- D. Visualización avanzada orientaciones
- E. Fragmentación avanzada (watershed, curva granulométrica)
- F. Modularización para ML futuro
- G. Documentación y UX final

## 4. Detalle por Bloques
### A. Rendimiento y Exportación Inicial
- [ ] Cache de detección de grietas (`@st.cache_data`) – hash = (bytes imagen recortada + min_length_px).
- [ ] Cache de segmentación de fragmentación.
- [ ] Opción "Reducir resolución si > umbral" (slider de factor: 0.25–1.0) antes de procesar.
- [ ] Exportar CSV de grietas: ID, length_px, length_m, length_major_px, length_major_m, orientation_deg, area_px, escala_px_m, fecha, hash_imagen (sha256 8 chars), parámetros clave.
- [ ] Exportar ZIP (CSV grietas + JSON parámetros + resumen métricas + versión app).

### B. Precisión y Métricas Avanzadas de Grietas
- [ ] Longitud geodésica mejorada: contar pasos 8-conectados (h/v=1, diag=√2) → `length_geodesic_px`, derivar metros.
- [ ] Filtro primario por longitud real (m) además de área (UI slider dependiente de escala).
- [ ] Clasificación de orientación en familias (N–S, NE–SW, E–W, etc.) → columna `orientation_class`.
- [ ] Agrupación de grietas por intervalos de orientación (histograma / rosa de direcciones simple).

### C. Testing y Calidad
- [ ] Añadir `tests/test_metrics.py` (crack_frequency, rqd_from_frequency, q_system errores). 
- [ ] Test sintético `tests/test_crack_detection.py` con imagen generada (líneas horizontales/diagonales). 
- [ ] Integrar `pytest` en requirements (si no está) y sección en README.
- [ ] Opcional: `ruff` + `mypy` configuración básica.

### D. Visualización Orientaciones
- [ ] Dibujar vectores de orientación sobre centroides (línea corta codificada por color según familia).
- [ ] Leyenda de colores orientación.
- [ ] Botones UI: "Seleccionar todas", "Invertir selección".

### E. Fragmentación Avanzada
- [ ] Preprocesado adicional: apertura morfológica controlada.
- [ ] Watershed sobre gradiente para separar bloques pegados.
- [ ] Marcar partículas truncadas en borde de imagen (flag `edge_touch`).
- [ ] Curva acumulada (percent passing) y cálculo P10, P20, P50, P80, P90 (visual + export).
- [ ] Inclusión de metadatos de escala y parámetros en CSV de fragmentación.

### F. Modularización / Extensibilidad
- [ ] Crear `detectors/base.py` con `BaseCrackDetector (detect(image, params)-> results)`.
- [ ] Mover lógica actual a `detectors/simple.py`.
- [ ] Interfaz para futuros modelos ML (placeholder `DeepCrackDetector`).
- [ ] Cargar detector seleccionable desde sidebar.

### G. Documentación y UX
- [ ] Ampliar README: pipeline, significado de cada métrica, limitaciones.
- [ ] Añadir diagrama flujo (Mermaid) y tabla de columnas exportadas.
- [ ] Página de ayuda (expander o pestaña) con glosario (RQD, RMR, GSI, Q-System).
- [ ] Internacionalización inicial (diccionario EN/ES en `constants.py`).

## 5. Métricas de Éxito
| Objetivo | Métrica | Meta |
|----------|---------|------|
| Rendimiento | Tiempo detección < 2MPx | < 1.0 s | 
| Precisión longitud | Diferencia vs baseline sintético | < 5% |
| Reproducibilidad | Caché aciertos (Hit Rate) | > 70% |
| Calidad código | Cobertura tests módulo metrics | > 90% |
| Usabilidad | Pasos usuario para exportar | 1–2 clicks |

## 6. Riesgos y Mitigaciones
| Riesgo | Impacto | Mitigación |
|--------|---------|------------|
| Imagen muy grande | Memoria / latencia | Downscale previo configurable |
| Falta lib canvas en algunos entornos | Pérdida UX escala | Fallback numérico ya implementado |
| Sobre-detección de ruido | Métricas infladas | Filtro por longitud geodésica + morfología adicional |
| Cambios de API futuros (Streamlit) | Roturas | Versionar requirements y tests de humo |

## 7. Orden de Ejecución Detallado (Sprint 1–2)
1. Cache + export CSV/ZIP (Bloque A).  
2. Longitud geodésica + filtro en metros (B parcialmente).  
3. Tests métricas + test sintético grietas (C parcialmente).  
4. Orientación clasificada + vectores (B/D).  
5. Watershed fragmentación + curva acumulada (E).  
6. Modularización base detector (F).  
7. Documentación ampliada y glosario (G).  

## 8. Estructura de Datos Propuesta (CSV Grietas)
Campos:
```
image_hash, timestamp_utc, scale_px_per_m, crack_id, length_px, length_m,
length_geodesic_px, length_geodesic_m, length_major_px, length_major_m,
orientation_deg, orientation_class, area_px, included (bool),
min_length_filter_m, app_version
```

## 9. Ejemplo de Flujo Exportación
1. Usuario calibra escala (interactiva).  
2. Ajusta filtro longitud mínima (m).  
3. (Opcional) excluye algunas grietas.  
4. Clic "Exportar resultados" → genera ZIP con CSV + JSON + resumen.  

## 10. JSON de Parámetros (ejemplo)
```json
{
  "image_hash": "ab12cd34",
  "generated_at": "2025-08-08T12:34:56Z",
  "scale_px_per_m": 987.5,
  "min_crack_area_px": 50,
  "min_crack_length_m": 0.05,
  "excluded_ids": [3,7],
  "app_version": "2.1-dev",
  "module_versions": {"opencv": "4.9.x", "numpy": "1.26.x"}
}
```

## 11. Notas Técnicas
- Caché: asegurar convertir imagen a bytes deterministas (usar `cv2.imencode('.png', ...)`).
- Hash imagen: `hashlib.sha256(bytes)[:8]`.
- Longitud geodésica: extraer esqueleto; recorrer píxeles vecinos acumulando 1 o √2 según desplazamiento.
- Rosa de orientaciones: bins de 22.5° (16 clases) o 45° (8 clases) → elegir 8 para simplicidad.
- Watershed: usar distancia invertida de binaria segmentada + marcadores (opening + local maxima).

## 12. Dependencias Potenciales Futuras
- `scipy` (distance transform avanzada / peak local maxima) – verificar peso.
- `ruff` y `pytest` para lint/tests.
- `pyyaml` si se externaliza configuración.

## 13. Próximo Paso Inmediato
Implementar Bloque A (cache + export CSV/ZIP) salvo cambio de prioridad.

---
Documento vivo: actualizar versión al completar cada bloque.
