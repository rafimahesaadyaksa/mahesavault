"""
AES-256 Cipher Module — MahesaVault
AES-256 in CBC mode with PKCS7 padding.
Key: SHA-256 hash of user password → 32 bytes
IV: os.urandom(16), prepended to ciphertext
Output: base64 encoded
Key space: 2^256 — computationally infeasible to brute-force
"""

import os
import base64
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as sym_padding


def _derive_key(password):
    """Derive 32-byte AES key from password using SHA-256."""
    return hashlib.sha256(password.encode('utf-8')).digest()


def encrypt(plaintext, password):
    """
    AES-256 CBC encrypt. Returns base64(IV + ciphertext).
    """
    if not password:
        raise ValueError("Password must not be empty")
    key = _derive_key(password)
    iv = os.urandom(16)
    # PKCS7 pad plaintext to 128-bit block boundary
    padder = sym_padding.PKCS7(128).padder()
    padded = padder.update(plaintext.encode('utf-8')) + padder.finalize()
    # Encrypt
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    ct = encryptor.update(padded) + encryptor.finalize()
    # Prepend IV and base64 encode
    return base64.b64encode(iv + ct).decode('utf-8')


def decrypt(ciphertext_b64, password):
    """
    AES-256 CBC decrypt. Expects base64(IV + ciphertext).
    """
    if not password:
        raise ValueError("Password must not be empty")
    key = _derive_key(password)
    raw = base64.b64decode(ciphertext_b64)
    iv = raw[:16]
    ct = raw[16:]
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    decryptor = cipher.decryptor()
    padded = decryptor.update(ct) + decryptor.finalize()
    # Remove PKCS7 padding
    unpadder = sym_padding.PKCS7(128).unpadder()
    plaintext = unpadder.update(padded) + unpadder.finalize()
    return plaintext.decode('utf-8')


def get_info():
    """Return algorithm info dict for comparison tables."""
    return {
        'name': 'AES-256',
        'type': 'Symmetric',
        'key_size': '256 bits',
        'block_size': '128 bits',
        'mode': 'CBC',
        'rounds': 14,
        'key_space': '2^256',
        'standard': 'NIST (FIPS 197)',
        'status': '✅ Industry Standard'
    }
