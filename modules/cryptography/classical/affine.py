"""
Affine Cipher Module — MahesaVault
E(x) = (a*x + b) mod 26, where gcd(a, 26) = 1
D(x) = a⁻¹ * (x - b) mod 26
Valid a values: {1,3,5,7,9,11,15,17,19,21,23,25}
Key space: 12 × 26 = 312 possible keys
"""

from math import gcd

VALID_A = [1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25]


def _mod_inverse(a, m=26):
    """Modular inverse using extended Euclidean algorithm."""
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    raise ValueError(f"No modular inverse for a={a} mod {m}")


def encrypt(plaintext, a, b):
    """Encrypt: E(x) = (a*x + b) mod 26."""
    if gcd(a, 26) != 1:
        raise ValueError(f"'a' must be coprime with 26. Valid: {VALID_A}")
    result = []
    for char in plaintext:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            x = ord(char) - base
            result.append(chr(base + (a * x + b) % 26))
        else:
            result.append(char)
    return ''.join(result)


def decrypt(ciphertext, a, b):
    """Decrypt: D(x) = a⁻¹ * (x - b) mod 26."""
    if gcd(a, 26) != 1:
        raise ValueError(f"'a' must be coprime with 26. Valid: {VALID_A}")
    a_inv = _mod_inverse(a)
    result = []
    for char in ciphertext:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            x = ord(char) - base
            result.append(chr(base + (a_inv * (x - b)) % 26))
        else:
            result.append(char)
    return ''.join(result)


def show_steps(plaintext, a, b):
    """Show step-by-step Affine cipher calculation."""
    lines = [f"**Affine Cipher — a={a}, b={b}**\n",
             f"Formula: E(x) = ({a}·x + {b}) mod 26\n",
             f"gcd({a}, 26) = {gcd(a, 26)} ✓\n",
             "| Letter | x | a·x+b | mod 26 | Result |",
             "|--------|---|-------|--------|--------|"]
    for char in plaintext:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            x = ord(char) - base
            ax_b = a * x + b
            r = ax_b % 26
            lines.append(f"| {char} | {x} | {ax_b} | {r} | {chr(base + r)} |")
        else:
            lines.append(f"| {char} | — | — | — | {char} |")
    ct = encrypt(plaintext, a, b)
    lines.append(f"\n**Plaintext:** `{plaintext}`")
    lines.append(f"**Ciphertext:** `{ct}`")
    return '\n'.join(lines)
