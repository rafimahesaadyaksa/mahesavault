"""
Paillier Homomorphic Encryption
================================
A pure-Python implementation of the Paillier cryptosystem, which supports
**additive homomorphic encryption**: given Enc(a) and Enc(b), one can
compute Enc(a + b) *without* knowing the plaintexts.

Security Basis:
    Decisional Composite Residuosity Assumption (DCRA) — distinguishing
    n-th residues modulo n² is hard when n = p·q for large primes p, q.

MahesaVault Project — Advanced Cryptography Module
"""

import math
import random
import secrets


# ===================================================================
# Helper / utility functions
# ===================================================================

def is_prime(n, k=20):
    """
    Miller-Rabin primality test.

    Parameters
    ----------
    n : int
        Number to test.
    k : int
        Number of witness rounds (higher → more reliable).

    Returns
    -------
    bool
        True if *n* is probably prime.
    """
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0:
        return False

    # Write n-1 as 2^r · d with d odd
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2

    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def generate_prime(bits):
    """
    Generate a random prime of approximately *bits* bit-length.

    Uses ``secrets`` for cryptographic randomness and Miller-Rabin for
    primality testing.
    """
    while True:
        # Ensure the high bit is set so the number is truly `bits` bits long
        candidate = secrets.randbits(bits) | (1 << (bits - 1)) | 1
        if is_prime(candidate):
            return candidate


def mod_inverse(a, m):
    """
    Compute the modular multiplicative inverse of *a* mod *m* using the
    extended Euclidean algorithm.

    Raises ``ValueError`` if the inverse does not exist.
    """
    if m == 1:
        return 0
    g, x, _ = _extended_gcd(a % m, m)
    if g != 1:
        raise ValueError(f'Modular inverse does not exist (gcd={g})')
    return x % m


def _extended_gcd(a, b):
    """Return (gcd, x, y) such that a·x + b·y = gcd(a, b)."""
    if a == 0:
        return b, 0, 1
    g, x1, y1 = _extended_gcd(b % a, a)
    return g, y1 - (b // a) * x1, x1


def lcm(a, b):
    """Least common multiple of *a* and *b*."""
    return abs(a * b) // math.gcd(a, b)


def _L(x, n):
    """Paillier L-function: L(x) = (x − 1) / n  (integer division)."""
    return (x - 1) // n


def _random_coprime(n):
    """Return a random integer in [2, n-1] that is coprime to *n*."""
    while True:
        r = secrets.randbelow(n - 2) + 2        # range [2, n-1]
        if math.gcd(r, n) == 1:
            return r


# ===================================================================
# Key generation
# ===================================================================

def generate_keys(bits=512):
    """
    Generate a Paillier key pair.

    Parameters
    ----------
    bits : int
        Total bit-length of *n* (= p·q).  Each prime is ``bits // 2`` bits.

    Returns
    -------
    dict
        {
            'public_key':  (n, g),
            'private_key': (lam, mu),
            'n_squared':   n²
        }
    """
    half = bits // 2

    # Generate two distinct primes of equal size
    p = generate_prime(half)
    q = generate_prime(half)
    while q == p:
        q = generate_prime(half)

    n = p * q
    n_sq = n * n
    g = n + 1                              # simplest valid generator

    lam = lcm(p - 1, q - 1)

    # μ = L(g^λ mod n²)⁻¹ mod n
    g_lam = pow(g, lam, n_sq)
    mu = mod_inverse(_L(g_lam, n), n)

    return {
        'public_key': (n, g),
        'private_key': (lam, mu),
        'n_squared': n_sq,
    }


# ===================================================================
# Encrypt / Decrypt  (integer level)
# ===================================================================

def encrypt(plaintext_int, public_key, n_squared):
    """
    Encrypt a non-negative integer.

    Parameters
    ----------
    plaintext_int : int
        Message  m  with  0 ≤ m < n.
    public_key : tuple(int, int)
        (n, g).
    n_squared : int
        n².

    Returns
    -------
    int
        Ciphertext  c = g^m · r^n  mod n².
    """
    n, g = public_key
    r = _random_coprime(n)
    # c = g^m · r^n  mod n²
    c = (pow(g, plaintext_int, n_squared) * pow(r, n, n_squared)) % n_squared
    return c


def decrypt(ciphertext_int, private_key, public_key, n_squared):
    """
    Decrypt a Paillier ciphertext back to a plaintext integer.

    Parameters
    ----------
    ciphertext_int : int
        Ciphertext produced by ``encrypt``.
    private_key : tuple(int, int)
        (λ, μ).
    public_key : tuple(int, int)
        (n, g).
    n_squared : int
        n².

    Returns
    -------
    int
        Recovered plaintext integer.
    """
    n, _g = public_key
    lam, mu = private_key
    # m = L(c^λ mod n²) · μ  mod n
    c_lam = pow(ciphertext_int, lam, n_squared)
    m = (_L(c_lam, n) * mu) % n
    return m


# ===================================================================
# Homomorphic operations
# ===================================================================

def add_encrypted(c1, c2, n_squared):
    """
    Homomorphically add two ciphertexts.

    Given  c₁ = Enc(m₁)  and  c₂ = Enc(m₂), returns  Enc(m₁ + m₂).

    Parameters
    ----------
    c1, c2 : int
        Paillier ciphertexts.
    n_squared : int
        n².

    Returns
    -------
    int
        Ciphertext encrypting  m₁ + m₂.
    """
    return (c1 * c2) % n_squared


# ===================================================================
# String-level convenience wrappers
# ===================================================================

def encrypt_string(message, public_key, n_squared):
    """
    Encrypt a string by encrypting each character's ordinal value.

    Returns a list of ciphertext integers (one per character).
    """
    return [encrypt(ord(ch), public_key, n_squared) for ch in message]


def decrypt_string(ciphertexts, private_key, public_key, n_squared):
    """
    Decrypt a list of Paillier ciphertexts back to a string.
    """
    return ''.join(
        chr(decrypt(c, private_key, public_key, n_squared))
        for c in ciphertexts
    )


# ===================================================================
# Module info
# ===================================================================

def get_info():
    """Return metadata about this cipher module."""
    return {
        'name': 'Paillier Homomorphic Encryption',
        'type': 'Asymmetric, additive homomorphic',
        'security_basis': 'Decisional Composite Residuosity Assumption (DCRA)',
        'homomorphic_property': 'Additive — Enc(a) * Enc(b) = Enc(a + b)',
        'key_components': {
            'public_key': '(n, g) — modulus and generator',
            'private_key': '(λ, μ) — derived from p, q',
        },
        'default_params': {'bits': 512},
        'warning': 'Educational implementation — NOT for production use.',
    }


# ===================================================================
# Quick self-test
# ===================================================================

if __name__ == '__main__':
    print('=== Paillier Cipher Self-Test ===')
    keys = generate_keys(bits=256)
    pub = keys['public_key']
    priv = keys['private_key']
    nsq = keys['n_squared']

    # --- Integer encryption round-trip ---
    m = 42
    c = encrypt(m, pub, nsq)
    d = decrypt(c, priv, pub, nsq)
    print(f'Encrypt({m}) → decrypt → {d}')
    assert d == m, f'MISMATCH: expected {m}, got {d}'

    # --- Homomorphic addition ---
    a, b = 15, 25
    ca = encrypt(a, pub, nsq)
    cb = encrypt(b, pub, nsq)
    c_sum = add_encrypted(ca, cb, nsq)
    result = decrypt(c_sum, priv, pub, nsq)
    print(f'Enc({a}) ⊕ Enc({b}) → decrypt → {result}')
    assert result == a + b, f'MISMATCH: expected {a+b}, got {result}'

    # --- String round-trip ---
    msg = 'Hello, Paillier!'
    ct = encrypt_string(msg, pub, nsq)
    pt = decrypt_string(ct, priv, pub, nsq)
    print(f'String encrypt/decrypt: {msg!r} → {pt!r}')
    assert pt == msg, f'MISMATCH: expected {msg!r}, got {pt!r}'

    print('✓ All self-tests passed.')
