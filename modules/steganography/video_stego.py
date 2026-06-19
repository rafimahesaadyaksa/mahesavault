"""
Video Steganography Module — MahesaVault
Embeds and extracts secret data into video frames using LSB.
Uses OpenCV to decompose video into frames, embed data across
multiple frames, and reassemble into a lossless AVI output.
"""

import cv2
import numpy as np
import tempfile
import os
import base64
from modules.steganography.lsb_sequential import EOF_DELIMITER
from modules.steganography.xor_cipher import xor_encrypt, xor_decrypt


def _get_frame_capacity(frame):
    """Get the bit capacity of a single frame."""
    return frame.shape[0] * frame.shape[1] * frame.shape[2]


def embed_video(input_video_path: str, message: str, output_path: str = None,
                key: str = "", use_xor: bool = False) -> str:
    """
    Embed a secret message into a video file using LSB steganography.
    Data is spread across multiple frames for better concealment.
    
    Args:
        input_video_path: Path to the cover video file.
        message: The secret message to hide.
        output_path: Path for the output stego video. Auto-generated if None.
        key: Optional key for XOR encryption.
        use_xor: Whether to apply XOR encryption.
        
    Returns:
        Path to the output stego video file (.avi).
    """
    if use_xor and key:
        message = xor_encrypt(message, key)
    
    # Convert message to binary
    binary_data = ''.join(format(ord(c), '08b') for c in message)
    binary_data += EOF_DELIMITER
    
    cap = cv2.VideoCapture(input_video_path)
    if not cap.isOpened():
        raise ValueError("Cannot open video file!")
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Calculate total capacity across all frames
    sample_ret, sample_frame = cap.read()
    if not sample_ret:
        raise ValueError("Cannot read video frames!")
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset to start
    
    bits_per_frame = _get_frame_capacity(sample_frame)
    total_capacity = bits_per_frame * total_frames
    
    if len(binary_data) > total_capacity:
        raise ValueError(
            f"Message too large! Need {len(binary_data)} bits, "
            f"but video has capacity for {total_capacity} bits "
            f"across {total_frames} frames."
        )
    
    # Output path
    if output_path is None:
        output_path = tempfile.mktemp(suffix='.avi')
    
    # Use lossless codec (uncompressed or FFV1)
    fourcc = cv2.VideoWriter_fourcc(*'FFV1')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    bit_idx = 0
    total_bits = len(binary_data)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        if bit_idx < total_bits:
            # Flatten frame to modify LSBs
            flat = frame.flatten()
            bits_to_embed = min(total_bits - bit_idx, len(flat))
            
            for i in range(bits_to_embed):
                flat[i] = (flat[i] & 0xFE) | int(binary_data[bit_idx])
                bit_idx += 1
            
            frame = flat.reshape(frame.shape)
        
        out.write(frame)
    
    cap.release()
    out.release()
    
    return output_path


def extract_video(video_path: str, key: str = "",
                  use_xor: bool = False) -> str:
    """
    Extract a hidden message from a stego video file.
    
    Args:
        video_path: Path to the stego video.
        key: Optional key for XOR decryption.
        use_xor: Whether to apply XOR decryption.
        
    Returns:
        The extracted message string.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError("Cannot open video file!")
    
    binary_data = ''
    found = False
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        flat = frame.flatten()
        
        for pixel_val in flat:
            binary_data += str(pixel_val & 1)
            
            # Check for EOF delimiter
            if len(binary_data) >= 16 and binary_data[-16:] == EOF_DELIMITER:
                found = True
                break
        
        if found:
            break
    
    cap.release()
    
    if not found:
        raise ValueError("No hidden message found — EOF delimiter not detected.")
    
    # Remove delimiter and convert to text
    message_bits = binary_data[:-16]
    chars = []
    for i in range(0, len(message_bits), 8):
        byte = message_bits[i:i+8]
        if len(byte) == 8:
            chars.append(chr(int(byte, 2)))
    
    message = ''.join(chars)
    
    if use_xor and key:
        message = xor_decrypt(message, key)
    
    return message


def embed_file_video(input_video_path: str, filename: str, file_bytes: bytes,
                     output_path: str = None, key: str = "",
                     use_xor: bool = False) -> str:
    """Embed a file into a video. Returns output video path."""
    b64_data = base64.b64encode(file_bytes).decode('utf-8')
    payload = f"{filename}|{b64_data}"
    return embed_video(input_video_path, payload, output_path, key, use_xor)


def get_video_info(video_path: str) -> dict:
    """Get video metadata for UI display."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return {}
    
    info = {
        'fps': cap.get(cv2.CAP_PROP_FPS),
        'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        'total_frames': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
        'duration_sec': int(cap.get(cv2.CAP_PROP_FRAME_COUNT) / max(cap.get(cv2.CAP_PROP_FPS), 1)),
    }
    
    ret, frame = cap.read()
    if ret:
        bits_per_frame = frame.shape[0] * frame.shape[1] * frame.shape[2]
        info['capacity_bits'] = bits_per_frame * info['total_frames']
        info['capacity_chars'] = info['capacity_bits'] // 8
    
    cap.release()
    return info
