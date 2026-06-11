"""
Digital Signature Module — MahesaVault
RSA-PSS signing with SHA-256 for message integrity verification.
"""

import hashlib
from cryptography.hazmat.primitives.asymmetric import padding, utils
from cryptography.hazmat.primitives import hashes, serialization
import base64


def sign_message(message, private_key_pem):
    """Sign a message with RSA private key using PSS/SHA-256. Returns base64 signature."""
    priv_key = serialization.load_pem_private_key(
        private_key_pem.encode('utf-8'), password=None
    )
    signature = priv_key.sign(
        message.encode('utf-8'),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return base64.b64encode(signature).decode('utf-8')


def verify_signature(message, signature_b64, public_key_pem):
    """
    Verify RSA-PSS signature. Returns dict with verification result
    and SHA-256 hash of the original message.
    """
    pub_key = serialization.load_pem_public_key(
        public_key_pem.encode('utf-8')
    )
    signature = base64.b64decode(signature_b64)
    # Calculate SHA-256 hash for display
    msg_hash = hashlib.sha256(message.encode('utf-8')).hexdigest()
    try:
        pub_key.verify(
            signature,
            message.encode('utf-8'),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return {
            'valid': True,
            'message': 'Signature is VALID ✅ — Message integrity confirmed.',
            'sha256_hash': msg_hash
        }
    except Exception:
        return {
            'valid': False,
            'message': 'Signature is INVALID ❌ — Message may have been tampered.',
            'sha256_hash': msg_hash
        }
