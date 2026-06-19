"""
Blowfish Cipher Module — MahesaVault
Blowfish symmetric cipher in CBC mode.
"""

import os
import base64
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as sym_padding
from cryptography.hazmat.decrepit.ciphers.algorithms import Blowfish


def encrypt(plaintext, password):
    """Encrypt using Blowfish CBC. Key: SHA-256 truncated to 16 bytes."""
    if not password:
        raise ValueError("Password must not be empty")
    key = hashlib.sha256(password.encode('utf-8')).digest()[:16]
    iv = os.urandom(8)  # Blowfish block = 64 bits
    padder = sym_padding.PKCS7(64).padder()
    padded = padder.update(plaintext.encode('utf-8')) + padder.finalize()
    cipher = Cipher(Blowfish(key), modes.CBC(iv))
    enc = cipher.encryptor()
    ct = enc.update(padded) + enc.finalize()
    return base64.b64encode(iv + ct).decode('utf-8')


def decrypt(ciphertext_b64, password):
    """Decrypt Blowfish CBC."""
    if not password:
        raise ValueError("Password must not be empty")
    key = hashlib.sha256(password.encode('utf-8')).digest()[:16]
    raw = base64.b64decode(ciphertext_b64)
    iv, ct = raw[:8], raw[8:]
    cipher = Cipher(Blowfish(key), modes.CBC(iv))
    dec = cipher.decryptor()
    padded = dec.update(ct) + dec.finalize()
    unpadder = sym_padding.PKCS7(64).unpadder()
    return (unpadder.update(padded) + unpadder.finalize()).decode('utf-8')


def get_info():
    return {
        'name': 'Blowfish', 'type': 'Symmetric',
        'key_size': '32-448 bits', 'block_size': '64 bits',
        'mode': 'CBC', 'key_space': 'Up to 2^448',
        'standard': 'Non-standard (Schneier, 1993)',
        'status': '⚠️ Legacy (use AES instead)'
    }
