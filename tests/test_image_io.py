import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.append(str(Path(__file__).resolve().parents[1]))
from src.image_io import load_image


def test_load_image_from_path(tmp_path):
    # Crear una imagen simple y guardarla
    img = Image.new("RGB", (10, 10), color="red")
    img_path = tmp_path / "img.png"
    img.save(img_path)

    # Cargar la imagen usando Path
    arr = load_image(Path(img_path))

    assert arr.shape == (10, 10, 3)
    assert arr.dtype == np.uint8
    # Canal rojo completo, verde y azul cero
    assert np.all(arr[:, :, 0] == 255)
    assert np.all(arr[:, :, 1:] == 0)
