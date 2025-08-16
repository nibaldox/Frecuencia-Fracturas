"""Módulo utilitario para operaciones de entrada/salida de imágenes.

Funciones:
    load_image(source) -> np.ndarray
    overlay_mask(image, mask, color=(255,0,0), alpha=0.4) -> np.ndarray

Se utiliza Pillow para abrir imágenes y OpenCV/Numpy para la manipulación.
"""
from __future__ import annotations

import io
from pathlib import Path
from typing import Tuple

import cv2
import numpy as np
from PIL import Image

__all__ = ["load_image", "overlay_mask", "annotate_cracks"]


def _pil_to_np(img_pil: Image.Image) -> np.ndarray:
    """Convierte un objeto Pillow Image a un array RGB uint8."""
    return np.array(img_pil.convert("RGB"))


def load_image(source) -> np.ndarray:  # noqa: ANN001
    """Carga una imagen desde distintos tipos de entrada.

    Parameters
    ----------
    source
        Puede ser:
        • `streamlit.runtime.uploaded_file_manager.UploadedFile`
        • `PIL.Image.Image`
        • Bytes (``bytes``)
        • Ruta de archivo (``str`` o ``Path``)

    Returns
    -------
    np.ndarray
        Imagen en formato RGB (H, W, 3) dtype uint8.
    """
    # Streamlit UploadedFile / cámara -> tiene método read()
    if hasattr(source, "read"):
        data = source.read()
        # Reiniciar puntero para que Streamlit no pierda el archivo
        if hasattr(source, "seek"):
            try:
                source.seek(0)
            except Exception:  # noqa: BLE001
                pass
        img_pil = Image.open(io.BytesIO(data))
        return _pil_to_np(img_pil)

    # Ya es PIL.Image.Image
    if isinstance(source, Image.Image):
        return _pil_to_np(source)

    # Ruta de archivo
    if isinstance(source, (str, Path)):
        img_pil = Image.open(source)
        return _pil_to_np(img_pil)

    raise TypeError("Formato de imagen no soportado: %s" % type(source))


def overlay_mask(
    image: np.ndarray,
    mask: np.ndarray,
    *,
    color: Tuple[int, int, int] = (255, 0, 0),
    alpha: float = 0.4,
) -> np.ndarray:
    """Superpone una máscara binaria sobre una imagen RGB.

    Parameters
    ----------
    image
        Imagen RGB original (H, W, 3).
    mask
        Máscara binaria (H, W) dtype bool o uint8.
    color
        Color RGB a utilizar para la superposición.
    alpha
        Transparencia del overlay (0 = invisible, 1 = opaco).

    Returns
    -------
    np.ndarray
        Imagen RGB con la máscara coloreada.
    """
    if mask.dtype != np.uint8:
        mask_uint8 = mask.astype(np.uint8) * 255
    else:
        mask_uint8 = mask

    overlay = image.copy()
    overlay[mask_uint8 > 0] = color

    blended = cv2.addWeighted(image, 1 - alpha, overlay, alpha, 0)
    return blended


def annotate_cracks(
    image: np.ndarray,
    crack_info: list[dict],
    *,
    excluded_ids: set[int] | None = None,
) -> np.ndarray:
    """Dibuja etiquetas numéricas en el centroide de cada grieta.

    Parameters
    ----------
    image : np.ndarray
        Imagen RGB.
    crack_info : list[dict]
        Lista de diccionarios con claves ``id`` y ``centroid``.
    excluded_ids : set[int], optional
        IDs de grietas a excluir (se dibujan en color gris).

    Returns
    -------
    np.ndarray
        Imagen RGB con anotaciones.
    """
    import cv2

    annotated = image.copy()
    font = cv2.FONT_HERSHEY_SIMPLEX
    # Escala dinámica para que se vea bien en distintas resoluciones
    base_dim = max(image.shape[0], image.shape[1])
    font_scale = max(0.6, base_dim / 800)
    thickness = int(max(1, base_dim / 500))

    excluded_ids = excluded_ids or set()

    for crack in crack_info:
        cid = crack["id"]
        cx, cy = crack["centroid"]
        color_fg = (150, 150, 150) if cid in excluded_ids else (0, 255, 255)  # amarillo
        # Contorno negro para mejorar contraste
        cv2.putText(
            annotated,
            str(cid),
            (cx, cy),
            font,
            font_scale,
            (0, 0, 0),
            thickness + 2,
            cv2.LINE_AA,
        )
        cv2.putText(
            annotated,
            str(cid),
            (cx, cy),
            font,
            font_scale,
            color_fg,
            thickness,
            cv2.LINE_AA,
        )
    return annotated
