"""
Audio Steganography Module — MahesaVault
Embeds and extracts secret data into the Least Significant Bits (LSB)
of uncompressed WAV audio files.
"""

import wave
import numpy as np
import io
import base64
from modules.steganography.xor_cipher import xor_encrypt, xor_decrypt
from modules.steganography.lsb_sequential import EOF_DELIMITER


def embed_audio(input_wav_bytes: bytes, message: str, key: str = "",
                use_xor: bool = False) -> bytes:
    """
    Embed a secret message into a WAV audio file's LSB.
    
    Args:
        input_wav_bytes: The original WAV file as bytes.
        message: The plaintext message to hide.
        key: The key for XOR encryption (if use_xor is True).
        use_xor: Whether to apply XOR encryption to the message.
        
    Returns:
        The stego WAV file as bytes.
    """
    if use_xor:
        if not key:
            raise ValueError("Key must be at least 1 character for XOR encryption")
        message = xor_encrypt(message, key)
        
    binary_data = ''.join(format(ord(c), '08b') for c in message)
    binary_data += EOF_DELIMITER
    
    # Read audio frames
    with wave.open(io.BytesIO(input_wav_bytes), 'rb') as wave_read:
        params = wave_read.getparams()
        n_channels = params.nchannels
        sampwidth = params.sampwidth
        n_frames = params.nframes
        
        # We only support 8-bit, 16-bit, 24-bit, 32-bit integer PCM
        if sampwidth not in (1, 2, 3, 4):
            raise ValueError(f"Unsupported sample width: {sampwidth} bytes. Only standard PCM is supported.")
            
        frames = wave_read.readframes(n_frames)
        
    # Convert frames to a mutable bytearray
    frame_bytes = bytearray(frames)
    
    # Check capacity. Each frame has (sampwidth * n_channels) bytes.
    # We can embed 1 bit per byte.
    total_capacity = len(frame_bytes)
    
    if len(binary_data) > total_capacity:
        raise ValueError(
            f"Message too large! Need {len(binary_data)} bits, "
            f"but audio only has {total_capacity} bytes available."
        )
        
    # Embed data into the LSB of each byte
    for i, bit in enumerate(binary_data):
        frame_bytes[i] = (frame_bytes[i] & 0xFE) | int(bit)
        
    # Write back to a new WAV file in memory
    output_io = io.BytesIO()
    with wave.open(output_io, 'wb') as wave_write:
        wave_write.setparams(params)
        wave_write.writeframes(bytes(frame_bytes))
        
    return output_io.getvalue()


def extract_audio(stego_wav_bytes: bytes, key: str = "",
                  use_xor: bool = False) -> str:
    """
    Extract a hidden message from a stego WAV file.
    
    Args:
        stego_wav_bytes: The stego WAV file as bytes.
        key: The key for XOR decryption.
        use_xor: Whether to apply XOR decryption.
        
    Returns:
        The extracted message.
    """
    with wave.open(io.BytesIO(stego_wav_bytes), 'rb') as wave_read:
        frames = wave_read.readframes(wave_read.getnframes())
        
    binary_data = ''
    extracted_message = ''
    
    for i in range(len(frames)):
        binary_data += str(frames[i] & 1)
        
        if len(binary_data) >= 16 and binary_data[-16:] == EOF_DELIMITER:
            message_bits = binary_data[:-16]
            
            chars = []
            for j in range(0, len(message_bits), 8):
                byte = message_bits[j:j+8]
                if len(byte) == 8:
                    chars.append(chr(int(byte, 2)))
                    
            extracted_message = ''.join(chars)
            break
    else:
        raise ValueError("No valid message found — EOF delimiter not detected.")
        
    if use_xor:
        if not key:
            raise ValueError("Key is required for XOR decryption")
        extracted_message = xor_decrypt(extracted_message, key)
        
    return extracted_message


def embed_file_audio(input_wav_bytes: bytes, filename: str, file_bytes: bytes,
                     key: str = "", use_xor: bool = False) -> bytes:
    """
    Embed a file into a WAV audio file.
    Format: [FILENAME]|[BASE64_DATA]
    """
    b64_data = base64.b64encode(file_bytes).decode('utf-8')
    payload = f"{filename}|{b64_data}"
    return embed_audio(input_wav_bytes, payload, key, use_xor)


def extract_file_audio(stego_wav_bytes: bytes, key: str = "",
                       use_xor: bool = False) -> tuple[str, bytes]:
    """
    Extract a hidden file from a stego WAV audio file.
    Returns (filename, file_bytes).
    """
    extracted_text = extract_audio(stego_wav_bytes, key, use_xor)
    
    if '|' not in extracted_text:
        raise ValueError("Valid file header not found in extracted audio data.")
        
    filename, b64_data = extracted_text.split('|', 1)
    try:
        file_bytes = base64.b64decode(b64_data)
        return filename, file_bytes
    except Exception as e:
        raise ValueError(f"Failed to decode file data: {e}")
