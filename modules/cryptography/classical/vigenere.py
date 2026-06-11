"""
Vigenere Cipher Module — MahesaVault
Polyalphabetic substitution cipher using a repeating keyword.

Formula:
    Encryption: C_i = (P_i + K_{i mod m}) mod 26
    Decryption: P_i = (C_i - K_{i mod m} + 26) mod 26

Weakness: Kasiski test can find key length, then frequency analysis per group.
"""


def encrypt(plaintext: str, key: str) -> str:
    """
    Encrypt plaintext using Vigenere cipher.
    
    Each letter is shifted by the corresponding key letter's position.
    The key repeats cyclically across the plaintext.
    
    Args:
        plaintext: The message to encrypt.
        key: The keyword (alphabetic characters only).
    
    Returns:
        Encrypted ciphertext string.
    
    Raises:
        ValueError: If key is empty or contains non-alphabetic characters.
    """
    if not key:
        raise ValueError("Key must not be empty")
    
    key = key.upper()
    if not key.isalpha():
        raise ValueError("Key must contain only alphabetic characters")
    
    result = []
    key_index = 0
    
    for char in plaintext:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            # Get key shift value (A=0, B=1, ..., Z=25)
            k = ord(key[key_index % len(key)]) - ord('A')
            # Apply Vigenere formula
            shifted = (ord(char) - base + k) % 26
            result.append(chr(base + shifted))
            key_index += 1
        else:
            result.append(char)
    
    return ''.join(result)


def decrypt(ciphertext: str, key: str) -> str:
    """
    Decrypt ciphertext using Vigenere cipher.
    
    Args:
        ciphertext: The encrypted message.
        key: The keyword (same as used for encryption).
    
    Returns:
        Decrypted plaintext string.
    """
    if not key:
        raise ValueError("Key must not be empty")
    
    key = key.upper()
    if not key.isalpha():
        raise ValueError("Key must contain only alphabetic characters")
    
    result = []
    key_index = 0
    
    for char in ciphertext:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            k = ord(key[key_index % len(key)]) - ord('A')
            # Reverse Vigenere: subtract key shift
            shifted = (ord(char) - base - k + 26) % 26
            result.append(chr(base + shifted))
            key_index += 1
        else:
            result.append(char)
    
    return ''.join(result)


def show_steps(plaintext: str, key: str) -> str:
    """
    Show step-by-step Vigenere encryption with key expansion matrix.
    
    Args:
        plaintext: The message being encrypted.
        key: The keyword.
    
    Returns:
        Formatted string with step-by-step calculations.
    """
    key = key.upper()
    lines = []
    lines.append(f"**Vigenere Cipher — Key = \"{key}\"**\n")
    lines.append(f"Formula: C_i = (P_i + K_{{i mod {len(key)}}}) mod 26\n")
    
    # Show key expansion
    alpha_only = [c for c in plaintext if c.isalpha()]
    expanded_key = ''.join(key[i % len(key)] for i in range(len(alpha_only)))
    lines.append(f"**Key Expansion:** `{expanded_key}`\n")
    
    lines.append("| Position | P_i (letter) | P_i (num) | K_i (letter) | K_i (num) | (P+K) mod 26 | C_i |")
    lines.append("|----------|-------------|-----------|-------------|-----------|--------------|-----|")
    
    key_index = 0
    for char in plaintext:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            p_num = ord(char.upper()) - ord('A')
            k_char = key[key_index % len(key)]
            k_num = ord(k_char) - ord('A')
            c_num = (p_num + k_num) % 26
            c_char = chr(base + c_num)
            lines.append(
                f"| {key_index} | {char} | {p_num} | {k_char} | {k_num} | {c_num} | {c_char} |"
            )
            key_index += 1
    
    ciphertext = encrypt(plaintext, key)
    lines.append(f"\n**Plaintext:** `{plaintext}`")
    lines.append(f"**Ciphertext:** `{ciphertext}`")
    
    return '\n'.join(lines)
