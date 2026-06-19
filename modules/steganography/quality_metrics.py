"""
Quality Metrics Module — MahesaVault
Calculates image quality metrics to measure steganographic distortion:
- MSE (Mean Squared Error)
- PSNR (Peak Signal-to-Noise Ratio)
- SSIM (Structural Similarity Index Measure)
"""

import numpy as np
from skimage.metrics import structural_similarity as ssim


def calculate_mse(original: np.ndarray, stego: np.ndarray) -> float:
    """
    Calculate Mean Squared Error between original and stego images.
    
    MSE = (1/N) * Σ(I_original(i,j) - I_stego(i,j))²
    
    Lower MSE = less distortion. For LSB changes, MSE ≈ 0.25 per modified pixel.
    
    Args:
        original: Original cover image as numpy array.
        stego: Stego image as numpy array.
    
    Returns:
        MSE value (float). 0.0 means identical images.
    """
    # Convert to float64 to avoid overflow during squared difference
    err = np.mean((original.astype(np.float64) - stego.astype(np.float64)) ** 2)
    return float(err)


def calculate_psnr(original: np.ndarray, stego: np.ndarray) -> float:
    """
    Calculate Peak Signal-to-Noise Ratio between original and stego images.
    
    PSNR = 10 * log10(MAX² / MSE)  where MAX = 255 for 8-bit images.
    
    Higher PSNR = better quality. Target: PSNR > 30 dB (imperceptible).
    LSB steganography typically achieves PSNR ≈ 50-55 dB.
    
    Args:
        original: Original cover image as numpy array.
        stego: Stego image as numpy array.
    
    Returns:
        PSNR value in decibels (dB). Returns float('inf') for identical images.
    """
    mse = calculate_mse(original, stego)
    
    if mse == 0:
        return float('inf')  # Identical images
    
    max_pixel = 255.0
    psnr = 10.0 * np.log10((max_pixel ** 2) / mse)
    return float(psnr)


def calculate_ssim(original: np.ndarray, stego: np.ndarray) -> float:
    """
    Calculate Structural Similarity Index between original and stego images.
    
    SSIM ∈ [0, 1] → 1.0 = identical images.
    LSB steganography typically achieves SSIM > 0.9999.
    
    Uses scikit-image implementation with channel_axis for multichannel images.
    
    Args:
        original: Original cover image as numpy array.
        stego: Stego image as numpy array.
    
    Returns:
        SSIM value (float between 0 and 1).
    """
    # Determine if image is multichannel (RGB) or grayscale
    if len(original.shape) == 3 and original.shape[2] >= 3:
        # Multichannel image — specify channel axis
        score = ssim(original, stego, channel_axis=2, data_range=255)
    else:
        # Grayscale image
        score = ssim(original, stego, data_range=255)
    
    return float(score)


def get_all_metrics(original: np.ndarray, stego: np.ndarray) -> dict:
    """
    Calculate all quality metrics at once.
    
    Args:
        original: Original cover image.
        stego: Stego image.
    
    Returns:
        Dictionary with 'mse', 'psnr', and 'ssim' values.
    """
    return {
        'mse': calculate_mse(original, stego),
        'psnr': calculate_psnr(original, stego),
        'ssim': calculate_ssim(original, stego)
    }
