"""Funciones para analizar fragmentación y tamaño de partículas en imágenes.

Se aplica un umbral de Otsu para segmentar partículas/bloques y se calculan
los diámetros equivalentes (en metros) aplicando una escala px/m definida
por el usuario.
"""
from __future__ import annotations

from math import pi, sqrt
from typing import List, Tuple

import cv2
import numpy as np

__all__ = [
    "particle_sizes",
]


def _preprocess(image: np.ndarray) -> np.ndarray:
    """Convierte a escala de grises y aplica desenfoque suave."""
    if len(image.shape) == 3 and image.shape[2] == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    return gray


def particle_sizes(
    image: np.ndarray,
    *,
    scale_px_per_meter: float,
    min_area_px: int = 200,
) -> Tuple[List[float], np.ndarray]:
    """Detecta partículas y devuelve sus diámetros equivalentes.

    Parameters
    ----------
    image : np.ndarray
        Imagen RGB o en escala de grises.
    scale_px_per_meter : float
        Relación píxeles/metro para convertir áreas y diámetros.
    min_area_px : int, default 200
        Áreas menores se descartan como ruido.

    Returns
    -------
    diameters_m : list[float]
        Lista de diámetros equivalentes por partícula (en metros).
    labeled_rgb : np.ndarray
        Imagen RGB con partículas coloreadas para visualización.
    """
    gray = _preprocess(image)

    # Umbral de Otsu para segmentar partículas (asumimos bloques más oscuros)
    # Invertir para que las partículas sean foreground
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    thresh_inv = cv2.bitwise_not(thresh)

    # Etiquetado de componentes
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(
        thresh_inv, connectivity=8
    )

    diameters_m: list[float] = []
    # Generar imagen coloreada
    labeled_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    rng = np.random.default_rng(42)
    colors = rng.integers(0, 255, size=(num_labels, 3), dtype=np.uint8)
    for i in range(1, num_labels):  # saltar fondo
        area = stats[i, cv2.CC_STAT_AREA]
        if area < min_area_px:
            continue
        # Calcular diámetro equivalente (m)
        area_m2 = area / (scale_px_per_meter**2)
        diameter_m = 2.0 * sqrt(area_m2 / pi)
        diameters_m.append(diameter_m)

        # Colorear partícula
        labeled_rgb[labels == i] = colors[i]

    return diameters_m, labeled_rgb
