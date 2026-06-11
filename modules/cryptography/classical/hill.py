"""
Hill Cipher Module — MahesaVault
Classical cipher using matrix multiplication mod 26.
Supports 2×2 and 3×3 key matrices.
"""

import numpy as np
from math import gcd


def _mod_inverse(a, m):
    """Compute modular multiplicative inverse of a mod m."""
    g, x, _ = _extended_gcd(a % m, m)
    if g != 1:
        raise ValueError(f"No modular inverse for {a} mod {m}")
    return x % m


def _extended_gcd(a, b):
    """Extended GCD: returns (gcd, x, y) where a*x + b*y = gcd."""
    if a == 0:
        return b, 0, 1
    g, x, y = _extended_gcd(b % a, a)
    return g, y - (b // a) * x, x


def _matrix_mod_inverse(matrix, mod=26):
    """Compute modular inverse of a matrix mod 26."""
    det = int(round(np.linalg.det(matrix))) % mod
    det_inv = _mod_inverse(det, mod)
    n = matrix.shape[0]
    if n == 2:
        adj = np.array([[matrix[1][1], -matrix[0][1]],
                        [-matrix[1][0], matrix[0][0]]])
    else:
        cofactors = np.zeros_like(matrix, dtype=float)
        for i in range(n):
            for j in range(n):
                minor = np.delete(np.delete(matrix, i, axis=0), j, axis=1)
                cofactors[i][j] = ((-1) ** (i + j)) * np.linalg.det(minor)
        adj = cofactors.T
    return (det_inv * adj).astype(int) % mod


def parse_key_matrix(key_str, size=2):
    """Parse comma-separated ints into n×n matrix. E.g. '3,3,2,5' for 2×2."""
    try:
        values = [int(x.strip()) for x in key_str.split(',')]
    except ValueError:
        raise ValueError("Key must be comma-separated integers")
    expected = size * size
    if len(values) != expected:
        raise ValueError(f"Need {expected} values for {size}×{size}, got {len(values)}")
    matrix = np.array(values).reshape(size, size)
    det = int(round(np.linalg.det(matrix))) % 26
    if gcd(det, 26) != 1:
        raise ValueError(f"Det={det} not coprime with 26. Matrix not invertible.")
    return matrix


def encrypt(plaintext, key_matrix):
    """Encrypt using Hill cipher: C = K × P (mod 26)."""
    n = key_matrix.shape[0]
    text = ''.join(c for c in plaintext.upper() if c.isalpha())
    while len(text) % n != 0:
        text += 'X'
    result = []
    for i in range(0, len(text), n):
        vec = np.array([ord(c) - ord('A') for c in text[i:i+n]])
        enc = key_matrix.dot(vec) % 26
        result.extend(chr(int(v) + ord('A')) for v in enc)
    return ''.join(result)


def decrypt(ciphertext, key_matrix):
    """Decrypt using Hill cipher with modular inverse matrix."""
    return encrypt(ciphertext, _matrix_mod_inverse(key_matrix))


def show_steps(plaintext, key_matrix):
    """Show step-by-step Hill cipher matrix multiplication."""
    n = key_matrix.shape[0]
    text = ''.join(c for c in plaintext.upper() if c.isalpha())
    while len(text) % n != 0:
        text += 'X'
    lines = [f"**Hill Cipher — {n}×{n} Key Matrix**\n", "**Key Matrix K:**\n```"]
    for row in key_matrix:
        lines.append("  [" + ", ".join(f"{int(v):3d}" for v in row) + "]")
    lines.append("```\n")
    lines.append(f"**Padded plaintext:** `{text}`\n")
    result_all = []
    for i in range(0, len(text), n):
        block = text[i:i+n]
        vec = [ord(c) - ord('A') for c in block]
        res = key_matrix.dot(vec) % 26
        chars = [chr(int(v) + ord('A')) for v in res]
        result_all.extend(chars)
        lines.append(f"Block \"{block}\": {vec} → K×P mod 26 = {[int(v) for v in res]} → `{''.join(chars)}`")
    lines.append(f"\n**Ciphertext:** `{''.join(result_all)}`")
    return '\n'.join(lines)
