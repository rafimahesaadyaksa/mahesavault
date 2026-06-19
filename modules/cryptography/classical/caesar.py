"""
Caesar Cipher Module — MahesaVault
Classical substitution cipher that shifts each letter by a fixed key value.

Formula:
    Encryption: E(x) = (x + k) mod 26
    Decryption: D(x) = (x - k + 26) mod 26

Security: Only 25 possible keys → trivially broken by brute force.
"""


def encrypt(plaintext: str, shift: int) -> str:
    """
    Encrypt plaintext using Caesar cipher.
    
    Each alphabetic character is shifted by 'shift' positions in the alphabet.
    Non-alphabetic characters are preserved unchanged.
    
    Args:
        plaintext: The message to encrypt.
        shift: The shift value (key), typically 1-25.
    
    Returns:
        Encrypted ciphertext string.
    """
    result = []
    shift = shift % 26  # Normalize shift to range [0, 25]
    
    for char in plaintext:
        if char.isalpha():
            # Determine base ASCII value (uppercase vs lowercase)
            base = ord('A') if char.isupper() else ord('a')
            # Apply shift with modular arithmetic
            shifted = (ord(char) - base + shift) % 26
            result.append(chr(base + shifted))
        else:
            result.append(char)
    
    return ''.join(result)


def decrypt(ciphertext: str, shift: int) -> str:
    """
    Decrypt ciphertext using Caesar cipher (reverse shift).
    
    Args:
        ciphertext: The encrypted message.
        shift: The shift value (same key used for encryption).
    
    Returns:
        Decrypted plaintext string.
    """
    # Decryption is encryption with negated shift
    return encrypt(ciphertext, -shift)


def show_steps(plaintext: str, shift: int) -> str:
    """
    Show step-by-step mathematical calculation of Caesar encryption.
    
    Displays the ASCII transformation for each letter:
    Letter → Numeric → Shift → Mod 26 → Result
    
    Args:
        plaintext: The message being encrypted.
        shift: The shift key value.
    
    Returns:
        Formatted string with step-by-step calculations.
    """
    lines = []
    lines.append(f"**Caesar Cipher — Shift = {shift}**\n")
    lines.append(f"Formula: E(x) = (x + {shift}) mod 26\n")
    lines.append("| Letter | x (pos) | x + k | (x+k) mod 26 | Result |")
    lines.append("|--------|---------|-------|---------------|--------|")
    
    shift = shift % 26
    
    for char in plaintext:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            x = ord(char) - base
            x_plus_k = x + shift
            result_num = x_plus_k % 26
            result_char = chr(base + result_num)
            lines.append(f"| {char} | {x} | {x_plus_k} | {result_num} | {result_char} |")
        else:
            lines.append(f"| {char} | — | — | — | {char} |")
    
    ciphertext = encrypt(plaintext, shift)
    lines.append(f"\n**Plaintext:** `{plaintext}`")
    lines.append(f"**Ciphertext:** `{ciphertext}`")
    
    return '\n'.join(lines)
