"""
ChaCha20 Cipher Module — MahesaVault
Modern stream cipher, alternative to AES.
"""

import os
import base64
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms


def encrypt(plaintext, password):
    """Encrypt using ChaCha20. Key: SHA-256 of password. Nonce: 16 bytes random."""
    if not password:
        raise ValueError("Password must not be empty")
    key = hashlib.sha256(password.encode('utf-8')).digest()  # 32 bytes
    nonce = os.urandom(16)  # ChaCha20 nonce
    cipher = Cipher(algorithms.ChaCha20(key, nonce), mode=None)
    enc = cipher.encryptor()
    ct = enc.update(plaintext.encode('utf-8')) + enc.finalize()
    return base64.b64encode(nonce + ct).decode('utf-8')


def decrypt(ciphertext_b64, password):
    """Decrypt ChaCha20."""
    if not password:
        raise ValueError("Password must not be empty")
    key = hashlib.sha256(password.encode('utf-8')).digest()
    raw = base64.b64decode(ciphertext_b64)
    nonce, ct = raw[:16], raw[16:]
    cipher = Cipher(algorithms.ChaCha20(key, nonce), mode=None)
    dec = cipher.decryptor()
    return (dec.update(ct) + dec.finalize()).decode('utf-8')


def get_info():
    return {
        'name': 'ChaCha20', 'type': 'Symmetric (Stream)',
        'key_size': '256 bits', 'block_size': 'Stream (no block)',
        'mode': 'Stream', 'key_space': '2^256',
        'standard': 'RFC 8439 (IETF)',
        'status': '✅ Modern (used in TLS 1.3)'
    }
