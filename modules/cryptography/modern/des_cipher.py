"""
DES (via 3DES) Cipher Module — MahesaVault
Standard DES deprecated since 1999. Uses 3DES (Triple DES) internally.
"""

import os
import base64
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as sym_padding

DEPRECATION_NOTE = (
    "⚠️ DES was deprecated by NIST in 1999 due to its 56-bit key being "
    "vulnerable to brute-force. This implementation uses 3DES (Triple DES) "
    "for compatibility. DES → 3DES → AES represents the evolution of "
    "symmetric encryption standards."
)


def encrypt(plaintext, password):
    """Encrypt using 3DES CBC. Key: SHA-256 truncated to 24 bytes."""
    if not password:
        raise ValueError("Password must not be empty")
    key = hashlib.sha256(password.encode('utf-8')).digest()[:24]
    iv = os.urandom(8)
    padder = sym_padding.PKCS7(64).padder()
    padded = padder.update(plaintext.encode('utf-8')) + padder.finalize()
    cipher = Cipher(algorithms.TripleDES(key), modes.CBC(iv))
    enc = cipher.encryptor()
    ct = enc.update(padded) + enc.finalize()
    return base64.b64encode(iv + ct).decode('utf-8')


def decrypt(ciphertext_b64, password):
    """Decrypt 3DES CBC."""
    if not password:
        raise ValueError("Password must not be empty")
    key = hashlib.sha256(password.encode('utf-8')).digest()[:24]
    raw = base64.b64decode(ciphertext_b64)
    iv, ct = raw[:8], raw[8:]
    cipher = Cipher(algorithms.TripleDES(key), modes.CBC(iv))
    dec = cipher.decryptor()
    padded = dec.update(ct) + dec.finalize()
    unpadder = sym_padding.PKCS7(64).unpadder()
    return (unpadder.update(padded) + unpadder.finalize()).decode('utf-8')


def get_info():
    return {
        'name': 'DES (via 3DES)', 'type': 'Symmetric',
        'key_size': '56 bits (DES) / 168 bits (3DES)',
        'block_size': '64 bits', 'mode': 'CBC',
        'key_space': '2^56 (DES) / 2^112 (3DES)',
        'standard': 'NIST (withdrawn 2005)',
        'status': '❌ Deprecated', 'note': DEPRECATION_NOTE
    }
