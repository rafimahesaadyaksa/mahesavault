"""
XOR Cipher Module — MahesaVault
Implements cyclic XOR pre-encryption for steganography.
XOR is self-inverse: encrypt(encrypt(msg, key), key) == msg
"""


def xor_encrypt(message: str, key: str) -> str:
    """
    Encrypt a message using cyclic XOR with the given key.
    
    Each character of the message is XORed with the corresponding
    character of the key (cycling through the key as needed).
    
    Formula: E(m_i) = chr(ord(m_i) XOR ord(k_{i mod len(k)}))
    
    Args:
        message: The plaintext message to encrypt.
        key: The encryption key (must be at least 1 character).
    
    Returns:
        The XOR-encrypted string.
    
    Raises:
        ValueError: If the key is empty.
    """
    if not key:
        raise ValueError("Key must be at least 1 character")
    
    encrypted_chars = []
    key_len = len(key)
    
    for i, char in enumerate(message):
        # XOR each character with the corresponding key character (cyclic)
        xor_value = ord(char) ^ ord(key[i % key_len])
        encrypted_chars.append(chr(xor_value))
    
    return ''.join(encrypted_chars)


def xor_decrypt(ciphertext: str, key: str) -> str:
    """
    Decrypt a XOR-encrypted message.
    
    Since XOR is self-inverse, decryption uses the same operation
    as encryption: D(c_i) = chr(ord(c_i) XOR ord(k_{i mod len(k)}))
    
    Args:
        ciphertext: The encrypted message.
        key: The decryption key (same as encryption key).
    
    Returns:
        The decrypted plaintext string.
    """
    # XOR is its own inverse — same operation as encryption
    return xor_encrypt(ciphertext, key)
