"""Algoritmo simple para detección de grietas basado en bordes.

Este módulo utiliza Canny + operaciones morfológicas para detectar discontinuidades
(lineales) en la imagen y calcula un recuento de grietas.

Funciones
---------
    detect_cracks(image: np.ndarray, min_length_px: int = 50)
        Devuelve bordes, máscara binaria de grietas y n.º de grietas.
"""
from __future__ import annotations

from typing import Tuple

import cv2
import numpy as np
from skimage.morphology import skeletonize

__all__ = ["detect_cracks"]


def detect_cracks(
    image: np.ndarray,
    *,
    min_length_px: int = 50,
) -> Tuple[np.ndarray, np.ndarray, list[dict]]:
    """Detecta grietas y devuelve bordes, máscara y total de grietas.

    Parameters
    ----------
    image : np.ndarray
        Imagen RGB (H, W, 3) uint8.
    min_length_px : int, optional
        Longitud/área mínima en píxeles para considerar un segmento como grieta.

    Returns
    -------
    edges : np.ndarray
        Imagen binaria de bordes.
    crack_mask : np.ndarray
        Máscara binaria (bool) con las grietas filtradas.
    crack_count : int
        Número de grietas detectadas.
    """
    # 1. Pre-proceso: escala de grises y suavizado
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # 2. Detección de bordes (Canny)
    edges = cv2.Canny(blurred, 50, 150)

    # 3. Operaciones morfológicas para conectar bordes cercanos
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    edges_closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=1)

    # 4. Skeletonize para afinar las líneas (opcional)
    edges_bool = edges_closed > 0
    skeleton = skeletonize(edges_bool).astype(np.uint8) * 255

    # 5. Etiquetado de componentes conectadas
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(skeleton, connectivity=8)

    crack_mask = np.zeros_like(skeleton, dtype=bool)
    crack_info: list[dict] = []

    for i in range(1, num_labels):  # saltar fondo (0)
        area = stats[i, cv2.CC_STAT_AREA]
        if area >= min_length_px:
            crack_mask[labels == i] = True
            # Centroid from stats
            cx = int(stats[i, cv2.CC_STAT_LEFT] + stats[i, cv2.CC_STAT_WIDTH] / 2)
            cy = int(stats[i, cv2.CC_STAT_TOP] + stats[i, cv2.CC_STAT_HEIGHT] / 2)
            crack_info.append({"id": i, "area": int(area), "centroid": (cx, cy)})

    return skeleton, crack_mask, crack_info
