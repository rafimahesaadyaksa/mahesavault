"""
Triple DES (3DES) Cipher Module — MahesaVault
Applies DES three times with independent keys for stronger security.
"""

import os
import base64
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as sym_padding


def encrypt(plaintext, password):
    """Encrypt using 3DES CBC with 24-byte key."""
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
        'name': '3DES (Triple DES)', 'type': 'Symmetric',
        'key_size': '168 bits (3×56)', 'block_size': '64 bits',
        'mode': 'CBC', 'key_space': '2^112 effective',
        'standard': 'NIST SP 800-67',
        'status': '⚠️ Legacy (use AES instead)'
    }
