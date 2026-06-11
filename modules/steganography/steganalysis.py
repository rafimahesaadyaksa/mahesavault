"""
Steganalysis Module — MahesaVault
Provides visual analysis tools for detecting steganographic modifications:
- RGB Histogram comparison (original vs stego)
- Bit-Plane Slicer (8 planes for forensic analysis)
- Error Map Generator (pixel difference visualization)
"""

import numpy as np
import cv2
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for Streamlit
import matplotlib.pyplot as plt
from io import BytesIO


def rgb_histogram_comparison(original: np.ndarray, stego: np.ndarray) -> plt.Figure:
    """
    Generate side-by-side RGB histogram comparison between original and stego images.
    
    Histograms show the distribution of pixel intensity values per channel.
    If steganography is well-implemented (LSB), histograms should be nearly identical.
    
    Args:
        original: Original cover image (BGR format from OpenCV).
        stego: Stego image (BGR format).
    
    Returns:
        Matplotlib Figure with 6 subplots (3 channels × 2 images).
    """
    fig, axes = plt.subplots(3, 2, figsize=(14, 10))
    fig.patch.set_facecolor('#0d0d0d')
    
    colors = ['#3b82f6', '#22c55e', '#ef4444']  # Blue, Green, Red (BGR order)
    channel_names = ['Blue', 'Green', 'Red']
    titles = ['Original', 'Stego']
    images = [original, stego]
    
    for row, (color, name) in enumerate(zip(colors, channel_names)):
        for col, (img, title) in enumerate(zip(images, titles)):
            ax = axes[row][col]
            ax.set_facecolor('#111827')
            
            # Calculate histogram for this channel
            hist = cv2.calcHist([img], [row], None, [256], [0, 256])
            ax.plot(hist, color=color, linewidth=0.8, alpha=0.9)
            ax.fill_between(range(256), hist.flatten(), alpha=0.15, color=color)
            
            ax.set_xlim([0, 256])
            ax.set_title(f'{title} — {name} Channel', color='#e2e8f0',
                        fontsize=10, fontfamily='monospace')
            ax.tick_params(colors='#64748b', labelsize=8)
            ax.spines['bottom'].set_color('#1e293b')
            ax.spines['left'].set_color('#1e293b')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
    
    fig.suptitle('RGB Histogram Comparison — Steganalysis',
                color='#00f5ff', fontsize=14, fontfamily='monospace', fontweight='bold')
    plt.tight_layout()
    return fig


def bit_plane_slice(image: np.ndarray) -> list:
    """
    Extract all 8 bit planes from an image for forensic analysis.
    
    Each bit plane i is calculated as: plane_i = (img >> i) & 1 * 255
    
    Bit plane 0 (LSB) is the most interesting for steganalysis —
    it should appear random if no steganography is present,
    but may show patterns if data was embedded sequentially.
    
    Args:
        image: Input image as numpy array (can be color or grayscale).
    
    Returns:
        List of 8 numpy arrays, each representing a bit plane (0=LSB to 7=MSB).
    """
    # Convert to grayscale if color image
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    bit_planes = []
    for i in range(8):
        # Extract bit i: shift right by i positions, then mask with 1
        # Multiply by 255 to make visible (0 → 0, 1 → 255)
        plane = ((gray >> i) & 1) * 255
        bit_planes.append(plane.astype(np.uint8))
    
    return bit_planes


def bit_plane_figure(image: np.ndarray) -> plt.Figure:
    """
    Generate a figure showing all 8 bit planes of an image.
    
    Args:
        image: Input image as numpy array.
    
    Returns:
        Matplotlib Figure with 8 subplots showing each bit plane.
    """
    planes = bit_plane_slice(image)
    
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    fig.patch.set_facecolor('#0d0d0d')
    
    for i, (plane, ax) in enumerate(zip(planes, axes.flatten())):
        ax.imshow(plane, cmap='gray')
        ax.set_title(f'Bit Plane {i} {"(LSB)" if i == 0 else "(MSB)" if i == 7 else ""}',
                    color='#e2e8f0', fontsize=10, fontfamily='monospace')
        ax.axis('off')
        ax.set_facecolor('#0d0d0d')
    
    fig.suptitle('Bit-Plane Visualization — Forensic Analysis',
                color='#00f5ff', fontsize=14, fontfamily='monospace', fontweight='bold')
    plt.tight_layout()
    return fig


def error_map(original: np.ndarray, stego: np.ndarray,
              threshold: int = 0) -> tuple:
    """
    Generate an error map showing pixel differences between original and stego.
    
    Uses cv2.absdiff to compute absolute differences, then applies
    a threshold to create a binary map of changed pixels.
    
    Args:
        original: Original cover image.
        stego: Stego image.
        threshold: Threshold value for binary map (0 = any change).
    
    Returns:
        Tuple of (difference_image, binary_map) as numpy arrays.
    """
    # Compute absolute pixel-wise difference
    diff = cv2.absdiff(original, stego)
    
    # Amplify for visibility (LSB changes are only ±1)
    diff_amplified = np.clip(diff * 128, 0, 255).astype(np.uint8)
    
    # Create binary map: 1 where any channel changed
    if len(diff.shape) == 3:
        gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    else:
        gray_diff = diff
    
    _, binary_map = cv2.threshold(gray_diff, threshold, 255, cv2.THRESH_BINARY)
    
    return diff_amplified, binary_map


def error_map_figure(original: np.ndarray, stego: np.ndarray) -> plt.Figure:
    """
    Generate a figure with the error map visualization.
    
    Args:
        original: Original cover image.
        stego: Stego image.
    
    Returns:
        Matplotlib Figure with difference and binary map subplots.
    """
    diff_amp, binary = error_map(original, stego)
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.patch.set_facecolor('#0d0d0d')
    
    # Original difference (amplified)
    axes[0].imshow(cv2.cvtColor(diff_amp, cv2.COLOR_BGR2RGB) if len(diff_amp.shape) == 3 else diff_amp, cmap='hot')
    axes[0].set_title('Amplified Difference Map', color='#e2e8f0',
                     fontsize=11, fontfamily='monospace')
    axes[0].axis('off')
    
    # Binary change map
    axes[1].imshow(binary, cmap='gray')
    axes[1].set_title('Binary Change Map (Changed Pixels)', color='#e2e8f0',
                     fontsize=11, fontfamily='monospace')
    axes[1].axis('off')
    
    # Overlay on original
    overlay = original.copy()
    if len(overlay.shape) == 3:
        # Highlight changed pixels in cyan
        mask = binary > 0
        overlay[mask] = [255, 245, 0]  # Cyan in BGR
    axes[2].imshow(cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB) if len(overlay.shape) == 3 else overlay)
    axes[2].set_title('Changed Pixels Overlay', color='#e2e8f0',
                     fontsize=11, fontfamily='monospace')
    axes[2].axis('off')
    
    fig.suptitle('Error Map — Pixel Modification Analysis',
                color='#00f5ff', fontsize=14, fontfamily='monospace', fontweight='bold')
    plt.tight_layout()
    return fig
