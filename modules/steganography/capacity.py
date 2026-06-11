"""
Capacity Calculator Module — MahesaVault
Calculates the maximum number of characters that can be embedded
in a cover image using LSB steganography.
"""

import numpy as np


def calculate_capacity(image: np.ndarray) -> dict:
    """
    Calculate the embedding capacity of an image for LSB steganography.
    
    Formula: max_chars = (height * width * channels - 16) // 8
    
    The -16 accounts for the 16-bit EOF delimiter that must be appended.
    The // 8 converts from bits to characters (8 bits per ASCII character).
    
    Args:
        image: Cover image as numpy array (H, W, C).
    
    Returns:
        Dictionary containing:
            - 'total_pixels': Total number of pixels in the image
            - 'total_channels': Total number of channel values (H*W*C)
            - 'total_bits': Total embeddable bits (minus EOF delimiter)
            - 'max_chars': Maximum number of ASCII characters
            - 'height': Image height in pixels
            - 'width': Image width in pixels
            - 'channels': Number of color channels
    """
    height, width = image.shape[:2]
    channels = image.shape[2] if len(image.shape) == 3 else 1
    
    total_pixels = height * width
    total_channels = total_pixels * channels
    
    # Reserve 16 bits for EOF delimiter
    total_embeddable_bits = total_channels - 16
    max_chars = total_embeddable_bits // 8
    
    return {
        'total_pixels': total_pixels,
        'total_channels': total_channels,
        'total_bits': total_embeddable_bits,
        'max_chars': max_chars,
        'height': height,
        'width': width,
        'channels': channels
    }
