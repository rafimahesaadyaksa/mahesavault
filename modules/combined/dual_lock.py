"""
Dual-Lock Module — MahesaVault
Combines AES-256 encryption with Random LSB steganography.
Workflow: plaintext → AES-256 encrypt → LSB embed → stego PNG
Decode:   stego PNG → LSB extract → AES-256 decrypt → plaintext
"""

import numpy as np
from modules.cryptography.modern import aes_cipher
from modules.steganography.lsb_random import embed_random, extract_random


def dual_lock_encode(image, plaintext, password):
    """
    Full dual-lock encoding pipeline.
    Step 1: AES-256 encrypt plaintext
    Step 2: Embed ciphertext into image via Random LSB
    Returns (stego_image, ciphertext, info_dict).
    """
    if not password:
        raise ValueError("Password is required for Dual-Lock")
    if not plaintext:
        raise ValueError("Message must not be empty")

    # LAYER 1: AES-256 encryption
    ciphertext = aes_cipher.encrypt(plaintext, password)

    # LAYER 2: Random LSB steganography (no XOR — AES is enough)
    stego_image = embed_random(image, ciphertext, password, use_xor=False)

    info = {
        'original_length': len(plaintext),
        'ciphertext_length': len(ciphertext),
        'ciphertext_preview': ciphertext[:64] + '...' if len(ciphertext) > 64 else ciphertext,
        'encryption': 'AES-256-CBC',
        'steganography': 'Random LSB (PRNG)',
        'key_derivation': 'SHA-256(password)',
    }
    return stego_image, ciphertext, info


def dual_lock_decode(stego_image, password):
    """
    Full dual-lock decoding pipeline.
    Step 1: Extract ciphertext via Random LSB
    Step 2: AES-256 decrypt to recover plaintext
    Returns (plaintext, ciphertext, info_dict).
    """
    if not password:
        raise ValueError("Password is required for Dual-Lock")

    # LAYER 2 reversed: LSB extraction
    ciphertext = extract_random(stego_image, password, use_xor=False)

    # LAYER 1 reversed: AES-256 decryption
    plaintext = aes_cipher.decrypt(ciphertext, password)

    info = {
        'ciphertext_length': len(ciphertext),
        'plaintext_length': len(plaintext),
        'decryption': 'AES-256-CBC',
        'extraction': 'Random LSB (PRNG)',
    }
    return plaintext, ciphertext, info
