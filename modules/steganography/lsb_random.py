"""
Random LSB Steganography Module — MahesaVault
Embeds secret data into pseudo-randomly shuffled pixel positions
using a PRNG seeded from the key. Without knowing the key/seed,
an attacker cannot reconstruct the pixel order to extract the message.
"""

import numpy as np
from modules.steganography.xor_cipher import xor_encrypt, xor_decrypt


# 16-bit EOF delimiter
EOF_DELIMITER = '1111111111111110'


def _generate_seed(key: str) -> int:
    """
    Generate a deterministic PRNG seed from a key string.
    
    Seed = sum of ASCII values of all characters in the key.
    This ensures the same key always produces the same pixel order.
    
    Args:
        key: The password/key string.
    
    Returns:
        Integer seed value.
    """
    return sum(ord(c) for c in key)


def embed_random(image: np.ndarray, message: str, key: str,
                 use_xor: bool = False) -> np.ndarray:
    """
    Embed a secret message using Random LSB steganography.
    
    Instead of embedding bits sequentially, pixel positions are
    shuffled using a PRNG seeded from the key. This distributes
    changes across the entire image, making steganalysis harder.
    
    Algorithm:
        1. Optionally XOR pre-encrypt the message
        2. Convert to binary + EOF delimiter
        3. Generate deterministic seed from key
        4. Create shuffled index array using np.random.shuffle
        5. Embed bits at shuffled positions
    
    Args:
        image: Cover image as numpy array (H, W, C).
        message: Secret message to embed.
        key: Password/key (required — used for PRNG seed).
        use_xor: Whether to apply XOR pre-encryption.
    
    Returns:
        Stego image with message embedded at random positions.
    
    Raises:
        ValueError: If key is empty or message exceeds capacity.
    """
    if not key:
        raise ValueError("Key must be at least 1 character for Random LSB")
    
    if use_xor:
        message = xor_encrypt(message, key)
    
    # Convert to binary and append EOF
    binary_data = ''.join(format(ord(c), '08b') for c in message)
    binary_data += EOF_DELIMITER
    
    # Flatten image for indexed access
    img_flat = image.flatten().copy()
    total_capacity = len(img_flat)
    
    if len(binary_data) > total_capacity:
        raise ValueError(
            f"Message too large for this image! "
            f"Need {len(binary_data)} bits, but image only has {total_capacity} channels. "
            f"Max characters: {(total_capacity - 16) // 8}"
        )
    
    # Generate deterministic seed and shuffle pixel indices
    seed = _generate_seed(key)
    rng = np.random.RandomState(seed)  # Use RandomState for reproducibility
    indices = np.arange(total_capacity)
    rng.shuffle(indices)
    
    # Embed bits at shuffled (pseudo-random) positions
    for i, bit in enumerate(binary_data):
        idx = indices[i]
        img_flat[idx] = (img_flat[idx] & 0xFE) | int(bit)
    
    stego_image = img_flat.reshape(image.shape)
    return stego_image


def extract_random(stego_image: np.ndarray, key: str,
                   use_xor: bool = False) -> str:
    """
    Extract a hidden message from a stego image using Random LSB.
    
    Reconstructs the same shuffled pixel order using the same key/seed,
    then reads LSBs from those positions until EOF delimiter is found.
    
    Args:
        stego_image: Stego image as numpy array.
        key: Password/key (must be the same used during embedding).
        use_xor: Whether to apply XOR decryption after extraction.
    
    Returns:
        The extracted secret message.
    
    Raises:
        ValueError: If key is empty or no valid message found.
    """
    if not key:
        raise ValueError("Key is required for Random LSB extraction")
    
    img_flat = stego_image.flatten()
    total_capacity = len(img_flat)
    
    # Reconstruct the same shuffled index order
    seed = _generate_seed(key)
    rng = np.random.RandomState(seed)
    indices = np.arange(total_capacity)
    rng.shuffle(indices)
    
    binary_data = ''
    
    for i in range(total_capacity):
        idx = indices[i]
        # Extract LSB from the shuffled position
        binary_data += str(img_flat[idx] & 1)
        
        # Check for EOF delimiter
        if len(binary_data) >= 16 and binary_data[-16:] == EOF_DELIMITER:
            message_bits = binary_data[:-16]
            
            chars = []
            for j in range(0, len(message_bits), 8):
                byte = message_bits[j:j+8]
                if len(byte) == 8:
                    chars.append(chr(int(byte, 2)))
            
            extracted_message = ''.join(chars)
            
            if use_xor:
                extracted_message = xor_decrypt(extracted_message, key)
            
            return extracted_message
    
    raise ValueError(
        "No valid message found — EOF delimiter not detected. "
        "Check that the key and method are correct."
    )
