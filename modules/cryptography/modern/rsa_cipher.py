"""
RSA Cipher Module — MahesaVault
RSA 2048-bit with OAEP padding (SHA-256).
Based on integer factorization problem.
"""

import base64
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization


def generate_keys():
    """Generate RSA 2048-bit key pair. Returns (private_pem, public_pem)."""
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    priv_pem = private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption()
    ).decode('utf-8')
    pub_pem = private_key.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.SubjectPublicKeyInfo
    ).decode('utf-8')
    return priv_pem, pub_pem


def encrypt(plaintext, public_key_pem):
    """Encrypt with RSA public key using OAEP/SHA-256. Returns base64."""
    pub_key = serialization.load_pem_public_key(public_key_pem.encode('utf-8'))
    ct = pub_key.encrypt(
        plaintext.encode('utf-8'),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return base64.b64encode(ct).decode('utf-8')


def decrypt(ciphertext_b64, private_key_pem):
    """Decrypt with RSA private key."""
    priv_key = serialization.load_pem_private_key(
        private_key_pem.encode('utf-8'), password=None
    )
    ct = base64.b64decode(ciphertext_b64)
    pt = priv_key.decrypt(
        ct,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return pt.decode('utf-8')


def get_info():
    return {
        'name': 'RSA-2048',
        'type': 'Asymmetric',
        'key_size': '2048 bits',
        'block_size': 'Variable',
        'mode': 'OAEP',
        'key_space': '~2^112 effective',
        'standard': 'PKCS#1 / RFC 8017',
        'status': '✅ Industry (TLS/PKI)'
    }
