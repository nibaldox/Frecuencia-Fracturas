"""Módulo de métricas geotécnicas.

Funciones implementadas:
    crack_frequency(crack_count, img_width_px, scale_px_per_meter=1000)
    rqd_from_frequency(frequency)
    gsi(...), rmr(...), q_system(...)

Nota: Las funciones avanzadas (GSI, RMR, Q-System, etc.) se implementarán en
versiones futuras. Por ahora devuelven ``None`` como marcador de posición.
"""
from __future__ import annotations

from typing import Optional

__all__ = [
    "crack_frequency",
    "rqd_from_frequency",
    "gsi_from_rmr",
    "rmr",  # placeholder
    "q_system",
    "blast_lk",
    "kuz_ram",
]


def crack_frequency(
    crack_count: int,
    img_width_px: int,
    *,
    scale_px_per_meter: float = 1000.0,
) -> float:
    """Calcula la frecuencia de discontinuidades (grietas/m).

    Asume que la imagen está aproximadamente a escala, con ``scale_px_per_meter``
    píxeles por metro. Por defecto utiliza 1000 px ≈ 1 m (1 px ≈ 1 mm).

    Parameters
    ----------
    crack_count : int
        Número de grietas detectadas.
    img_width_px : int
        Ancho de la imagen en píxeles.
    scale_px_per_meter : float, optional
        Factor de conversión de píxeles a metros.

    Returns
    -------
    float
        Frecuencia de grietas (grietas por metro).
    """
    if img_width_px <= 0 or scale_px_per_meter <= 0:
        raise ValueError("Dimensiones no válidas para frecuencia de grietas.")

    width_m = img_width_px / scale_px_per_meter
    if width_m == 0:
        return 0.0
    frequency = crack_count / width_m
    return round(frequency, 2)


def rqd_from_frequency(frequency: float) -> float:
    """Calcula el RQD a partir de la frecuencia de grietas.

    Fórmula simplificada usada en la documentación:
        RQD = max(0, 100 - 3.3 × frequency)

    Parameters
    ----------
    frequency : float
        Frecuencia de grietas (grietas por metro).

    Returns
    -------
    float
        Valor RQD [%].
    """
    rqd = 100 - 3.3 * frequency
    return max(0.0, round(rqd, 2))


# --- Cálculos geotécnicos avanzados ----------------------------------------

def gsi_from_rmr(rmr_total: float) -> float:
    """Calcula el GSI a partir de un RMR total.

    Recomendación de Hoek (1994): GSI ≈ RMR₈₉ – 5 para RMR > 18.
    Para valores menores se aplica la misma resta pero se trunca a 0.
    """
    return max(0.0, round(rmr_total - 5.0, 2))


def rmr(*args, **kwargs) -> Optional[float]:  # noqa: D401,E501 ANN001
    """Placeholder: el cálculo detallado de RMR se implementará más adelante."""
    return None


def q_system(
    rqd_percent: float,
    jn: float,
    jr: float,
    ja: float,
    jw: float,
    srf: float,
) -> float:
    """Calcula el valor Q del Q-System de Barton.

    Parameters
    ----------
    rqd_percent : float
        RQD en porcentaje (0-100).
    jn, jr, ja, jw, srf : float
        Factores del Q-System.
    """
    if any(v <= 0 for v in (jn, jr, ja, jw, srf)):
        raise ValueError("Todos los factores deben ser positivos.")
    rqd = max(0.01, rqd_percent / 100.0)  # convertir a fracción y evitar cero
    q_val = (rqd / jn) * (jr / ja) * (jw / srf)
    return round(q_val, 3)


def blast_lk(fe: float, S: float, B: float, c: float, E: float) -> float:
    """Carga específica de voladura según Langefors-Kihlström.

    q = (55 * sqrt(fe * S * B)) / (c * sqrt(E))
    """
    import math

    numerator = 55.0 * math.sqrt(fe * S * B)
    denominator = c * math.sqrt(E)
    if denominator == 0:
        raise ValueError("El denominador no puede ser cero.")
    q_spec = numerator / denominator
    return round(q_spec, 3)


def kuz_ram(A: float, V: float, Q_mass: float, RWS: float) -> float:
    """Tamaño medio de fragmentación (Xm) según Kuz–Ram.

    Xm = A * (V/Q)^0.8 * Q^(-19/30) * (115/RWS)^(19/30)
    Devuelve Xm en centímetros.
    """
    import math

    if any(v <= 0 for v in (A, V, Q_mass, RWS)):
        raise ValueError("Variables deben ser positivas.")
    xm = (
        A
        * (V / Q_mass) ** 0.8
        * (Q_mass ** (-19.0 / 30.0))
        * ((115.0 / RWS) ** (19.0 / 30.0))
    )
    return round(xm, 2)
