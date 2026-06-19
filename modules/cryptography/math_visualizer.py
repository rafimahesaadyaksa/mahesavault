"""
Math Visualizer Module — MahesaVault
Generates step-by-step mathematical explanations for each cipher.
"""

from modules.cryptography.classical import caesar, vigenere, playfair, hill, affine


def get_classical_steps(cipher_name, plaintext, key):
    """Get step-by-step math for the selected classical cipher."""
    if cipher_name == "Caesar Cipher":
        return caesar.show_steps(plaintext, int(key))
    elif cipher_name == "Vigenere Cipher":
        return vigenere.show_steps(plaintext, key)
    elif cipher_name == "Playfair Cipher":
        return playfair.show_steps(plaintext, key)
    elif cipher_name == "Hill Cipher":
        mat = hill.parse_key_matrix(key)
        return hill.show_steps(plaintext, mat)
    elif cipher_name == "Affine Cipher":
        parts = key.split(',')
        a, b = int(parts[0].strip()), int(parts[1].strip())
        return affine.show_steps(plaintext, a, b)
    return "Select a cipher to see mathematical steps."


def get_comparison_table():
    """Return markdown comparison table of all ciphers."""
    return """
| Cipher | Type | Key Space | Brute Force | Complexity | Status |
|--------|------|-----------|-------------|------------|--------|
| Caesar | Classical | 2^4.6 (25 keys) | Instant | O(n) | ❌ Obsolete |
| Vigenere | Classical | 26^m | Minutes-Hours | O(n·m) | ❌ Obsolete |
| Playfair | Classical | ~26^25 | Years | O(n) | ❌ Obsolete |
| Hill (2×2) | Classical | 26^4 | Hours | O(n·k²) | ❌ Obsolete |
| Affine | Classical | 312 | Instant | O(n) | ❌ Obsolete |
| AES-256 | Modern | 2^256 | Beyond feasible | O(n) | ✅ NIST Standard |
| RSA-2048 | Modern | ~2^112 | Decades | O(n³) | ✅ Industry (TLS) |
| DES (3DES) | Modern | 2^112 | Months-Years | O(n) | ❌ Deprecated |
| 3DES | Modern | 2^112 | Months-Years | O(n) | ⚠️ Legacy |
| Blowfish | Modern | 2^448 | Infeasible | O(n) | ⚠️ Legacy |
| ChaCha20 | Modern | 2^256 | Beyond feasible | O(n) | ✅ Modern (TLS 1.3) |
"""
