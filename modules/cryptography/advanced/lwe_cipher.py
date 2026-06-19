"""
LWE (Learning With Errors) Lattice-Based Cipher
=================================================
A post-quantum cryptographic cipher based on the hardness of the
Learning With Errors problem over lattices.

This is an **educational implementation** — not suitable for production use.

Security Basis:
    The LWE problem: given (A, b = A·s + e mod q), recovering the secret
    vector s is computationally hard when small noise e is added. This
    hardness is believed to hold even against quantum computers.

Encoding:
    Each character is encoded as 8 bits. Each bit is encrypted individually
    as its own (u, v) ciphertext pair, giving 8 ciphertext pairs per char.

MahesaVault Project — Advanced Cryptography Module
"""

import numpy as np


# ---------------------------------------------------------------------------
# Key generation
# ---------------------------------------------------------------------------

def generate_keys(n=64, q=257, error_std=3):
    """
    Generate an LWE key pair.

    Parameters
    ----------
    n : int
        Lattice dimension (size of the secret vector and matrix side).
    q : int
        Modulus for all arithmetic. Should be prime for best results.
    error_std : float
        Standard deviation of the Gaussian error vector.

    Returns
    -------
    dict
        {
            'public_key': (A, b),   — A is n×n matrix, b is length-n vector
            'private_key': s,       — secret vector of length n
            'params': {'n': n, 'q': q}
        }
    """
    # Random n×n matrix mod q
    A = np.random.randint(0, q, size=(n, n))

    # Secret vector mod q
    s = np.random.randint(0, q, size=n)

    # Small Gaussian error vector, rounded to ints, taken mod q
    e = np.round(np.random.normal(0, error_std, size=n)).astype(int) % q

    # Public vector b = A·s + e  (mod q)
    b = (A @ s + e) % q

    return {
        'public_key': (A, b),
        'private_key': s,
        'params': {'n': n, 'q': q},
    }


# ---------------------------------------------------------------------------
# Encryption  (bit-level)
# ---------------------------------------------------------------------------

def _char_to_bits(ch):
    """Convert a single character to a list of 8 bits (MSB first)."""
    val = ord(ch)
    return [(val >> (7 - i)) & 1 for i in range(8)]


def _encrypt_bit(bit, A, b, q):
    """
    Encrypt a single bit (0 or 1).

    Parameters
    ----------
    bit : int
        The plaintext bit (0 or 1).
    A : ndarray
        Public matrix (n×n).
    b : ndarray
        Public vector (length n).
    q : int
        Modulus.

    Returns
    -------
    tuple(ndarray, int)
        (u, v) ciphertext pair.
    """
    n = A.shape[0]

    # Random binary selector vector
    r = np.random.randint(0, 2, size=n)

    u = (r @ A) % q                         # length-n vector
    v = int((r @ b + bit * (q // 2)) % q)   # scalar

    return (u, v)


def encrypt(message_str, public_key, params):
    """
    Encrypt a plaintext string.

    Each character is split into 8 bits; every bit is encrypted as its own
    (u, v) ciphertext pair.  The returned list therefore has
    ``8 * len(message_str)`` entries.

    Parameters
    ----------
    message_str : str
        Plaintext to encrypt.
    public_key : tuple(ndarray, ndarray)
        (A, b) from ``generate_keys``.
    params : dict
        ``{'n': ..., 'q': ...}`` from ``generate_keys``.

    Returns
    -------
    list[tuple(ndarray, int)]
        List of (u, v) ciphertext pairs — 8 per character.
    """
    A, b = public_key
    q = params['q']

    ciphertext = []
    for ch in message_str:
        bits = _char_to_bits(ch)
        for bit in bits:
            ciphertext.append(_encrypt_bit(bit, A, b, q))
    return ciphertext


# ---------------------------------------------------------------------------
# Decryption  (bit-level)
# ---------------------------------------------------------------------------

def _decrypt_bit(u, v, s, q):
    """
    Decrypt a single (u, v) ciphertext pair back to a bit.

    Computes d = (v − u·s) mod q, then decides whether d is closer to 0
    (bit = 0) or to q//2 (bit = 1).
    """
    d = int((v - u @ s) % q)

    half_q = q // 2
    # Distance to 0 (wrapping around q)
    dist_to_zero = min(d, q - d)
    # Distance to q//2
    dist_to_half = abs(d - half_q)

    return 1 if dist_to_half < dist_to_zero else 0


def decrypt(ciphertext, private_key, params):
    """
    Decrypt a list of (u, v) ciphertext pairs back to a string.

    Every 8 consecutive pairs are reassembled into one character.

    Parameters
    ----------
    ciphertext : list[tuple(ndarray, int)]
        Output of ``encrypt``.
    private_key : ndarray
        Secret vector *s* from ``generate_keys``.
    params : dict
        ``{'n': ..., 'q': ...}`` from ``generate_keys``.

    Returns
    -------
    str
        Recovered plaintext string.
    """
    s = private_key
    q = params['q']

    bits = [_decrypt_bit(u, v, s, q) for u, v in ciphertext]

    # Reassemble every 8 bits into a character
    chars = []
    for i in range(0, len(bits), 8):
        byte_bits = bits[i:i + 8]
        if len(byte_bits) < 8:
            break
        val = 0
        for b in byte_bits:
            val = (val << 1) | b
        chars.append(chr(val))

    return ''.join(chars)


# ---------------------------------------------------------------------------
# Module info
# ---------------------------------------------------------------------------

def get_info():
    """Return metadata about this cipher module."""
    return {
        'name': 'LWE Lattice-Based Cipher',
        'type': 'Symmetric-style lattice cipher (educational)',
        'security_basis': 'Learning With Errors (LWE) problem',
        'post_quantum': True,
        'key_components': {
            'public_key': '(A, b) — random matrix and noisy product',
            'private_key': 's — secret vector',
        },
        'encoding': 'Bit-level: each character → 8 bits, each bit → one (u,v) ciphertext',
        'default_params': {'n': 64, 'q': 257, 'error_std': 3},
        'warning': 'Educational implementation — NOT for production use.',
    }


# ---------------------------------------------------------------------------
# Quick self-test
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    print('=== LWE Cipher Self-Test ===')
    keys = generate_keys()
    pub = keys['public_key']
    priv = keys['private_key']
    params = keys['params']

    plaintext = 'Hello, LWE!'
    ct = encrypt(plaintext, pub, params)
    recovered = decrypt(ct, priv, params)

    print(f'Plaintext : {plaintext}')
    print(f'Ciphertext: {len(ct)} (u,v) pairs  ({len(ct)//8} chars × 8 bits)')
    print(f'Decrypted : {recovered}')
    assert recovered == plaintext, f'MISMATCH: got {recovered!r}'
    print('✓ Self-test passed.')
