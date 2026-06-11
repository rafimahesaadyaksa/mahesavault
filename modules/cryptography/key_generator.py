"""
Key Generator Module — MahesaVault
Generate RSA key pairs and AES keys.
"""

import os
import base64
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization


def generate_rsa_keys(key_size=2048):
    """Generate RSA key pair. Returns dict with private_pem, public_pem."""
    private_key = rsa.generate_private_key(
        public_exponent=65537, key_size=key_size
    )
    priv_pem = private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption()
    ).decode('utf-8')
    pub_pem = private_key.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.SubjectPublicKeyInfo
    ).decode('utf-8')
    return {'private_key': priv_pem, 'public_key': pub_pem, 'key_size': key_size}


def generate_aes_key(size=32):
    """Generate random AES key. Returns dict with key_bytes and key_b64."""
    key_bytes = os.urandom(size)
    key_b64 = base64.b64encode(key_bytes).decode('utf-8')
    key_hex = key_bytes.hex()
    return {
        'key_base64': key_b64,
        'key_hex': key_hex,
        'key_size_bits': size * 8
    }
