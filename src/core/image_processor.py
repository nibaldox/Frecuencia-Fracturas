"""Procesador central de imágenes para la aplicación."""

import numpy as np
from PIL import Image
from streamlit_cropper import st_cropper
import streamlit as st

from src import image_io


class ImageProcessor:
    """
    Clase para manejar el procesamiento central de imágenes.
    """
    
    def __init__(self):
        """Inicializa el procesador de imágenes."""
        self.original_image = None
        self.cropped_image = None
    
    def load_and_display_image(self, image_source) -> np.ndarray:
        """
        Carga y muestra la imagen original.
        
        Args:
            image_source: Fuente de imagen (archivo o cámara)
            
        Returns:
            np.ndarray: Imagen original como array numpy
        """
        self.original_image = image_io.load_image(image_source)
        st.image(
            self.original_image, 
            caption="Imagen original", 
            use_container_width=True
        )
        return self.original_image
    
    def crop_image_roi(self, image: np.ndarray) -> np.ndarray:
        """
        Permite al usuario seleccionar una región de interés (ROI) de la imagen.
        
        Args:
            image: Imagen original
            
        Returns:
            np.ndarray: Imagen recortada
        """
        st.subheader("✂️ Seleccionar muestra (ROI)")
        cropped_pil = st_cropper(
            Image.fromarray(image), 
            realtime_update=False, 
            box_color='red'
        )
        self.cropped_image = np.array(cropped_pil)
        st.image(
            self.cropped_image, 
            caption="Muestra seleccionada", 
            use_container_width=True
        )
        return self.cropped_image
    
    def get_processed_image(self) -> np.ndarray:
        """
        Retorna la imagen procesada (recortada si existe, original si no).
        
        Returns:
            np.ndarray: Imagen procesada
        """
        return self.cropped_image if self.cropped_image is not None else self.original_image
