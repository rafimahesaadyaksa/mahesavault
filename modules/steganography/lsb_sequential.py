"""
Sequential LSB Steganography Module — MahesaVault
Embeds secret data into the Least Significant Bits of image pixels
sequentially from pixel (0,0), reading each pixel's RGB channels.
Uses EOF delimiter '1111111111111110' (16 bits) to mark end of message.
"""

import numpy as np
from modules.steganography.xor_cipher import xor_encrypt, xor_decrypt


# 16-bit EOF delimiter to mark end of embedded data
EOF_DELIMITER = '1111111111111110'


def embed_sequential(image: np.ndarray, message: str, key: str = "",
                     use_xor: bool = False) -> np.ndarray:
    """
    Embed a secret message into an image using Sequential LSB.
    
    Bits are embedded sequentially starting from pixel (0,0),
    traversing each pixel's RGB channels in order.
    
    Algorithm:
        1. Optionally XOR pre-encrypt the message with the key
        2. Convert message to binary string + append EOF delimiter
        3. Check capacity (total available bits >= message bits)
        4. For each bit, clear the LSB of the current pixel channel
           and set it to the message bit: pixel = (pixel & 0xFE) | bit
    
    Args:
        image: Cover image as numpy array (H, W, C).
        message: Secret message to embed.
        key: Password/key for XOR pre-encryption.
        use_xor: Whether to apply XOR pre-encryption before embedding.
    
    Returns:
        Stego image as numpy array with the message embedded.
    
    Raises:
        ValueError: If message is too large or key is empty when XOR is enabled.
    """
    if use_xor:
        if not key:
            raise ValueError("Key must be at least 1 character for XOR encryption")
        message = xor_encrypt(message, key)
    
    # Convert message characters to 8-bit binary representation
    binary_data = ''.join(format(ord(c), '08b') for c in message)
    # Append EOF delimiter so extraction knows where to stop
    binary_data += EOF_DELIMITER
    
    # Flatten image to 1D array for sequential access
    img_flat = image.flatten().copy()
    total_capacity = len(img_flat)
    
    if len(binary_data) > total_capacity:
        raise ValueError(
            f"Message too large for this image! "
            f"Need {len(binary_data)} bits, but image only has {total_capacity} channels. "
            f"Max characters: {(total_capacity - 16) // 8}"
        )
    
    # Embed each bit into the LSB of sequential pixel channels
    for i, bit in enumerate(binary_data):
        # Clear LSB with AND 0xFE (11111110), then set to message bit
        img_flat[i] = (img_flat[i] & 0xFE) | int(bit)
    
    # Reshape back to original image dimensions
    stego_image = img_flat.reshape(image.shape)
    return stego_image


def _extract_sequential_bits(stego_image: np.ndarray, key: str = "",
                             use_xor: bool = False, bit_pos: int = 0) -> str:
    """
    Internal extraction function that reads bits from a specified bit position
    (0 for LSB, 7 for MSB) sequentially from pixel (0,0) until EOF delimiter.

    Args:
        stego_image: Stego image as numpy array.
        key: Password/key for XOR decryption.
        use_xor: Whether to apply XOR decryption after extraction.
        bit_pos: Bit position to extract (0 = LSB, 7 = MSB).

    Returns:
        The extracted secret message.

    Raises:
        ValueError: If no valid message is found or extraction fails.
    """
    img_flat = stego_image.flatten()

    binary_data = ''
    extracted_message = ''

    mask = 1 << bit_pos
    for i in range(len(img_flat)):
        # Extract bit at position bit_pos
        binary_data += str((img_flat[i] & mask) >> bit_pos)

        # Check for EOF delimiter every 8 bits (after at least 16 bits)
        if len(binary_data) >= 16 and binary_data[-16:] == EOF_DELIMITER:
            # Remove EOF delimiter and convert binary to text
            message_bits = binary_data[:-16]

            # Convert every 8 bits to a character
            chars = []
            for j in range(0, len(message_bits), 8):
                byte = message_bits[j:j+8]
                if len(byte) == 8:
                    char_val = int(byte, 2)
                    chars.append(chr(char_val))

            extracted_message = ''.join(chars)
            break
    else:
        raise ValueError("No valid message found — EOF delimiter not detected")

    # Apply XOR decryption if it was used during embedding
    if use_xor:
        if not key:
            raise ValueError("Key is required for XOR decryption")
        extracted_message = xor_decrypt(extracted_message, key)

    return extracted_message


def extract_sequential_bruteforce(stego_image: np.ndarray) -> str:
    """
    Attempt to extract a message using sequential bit extraction across
    different channel permutations and bit positions (LSB/MSB) without
    requiring a key or XOR decryption.

    Tries all permutations of the three color channels and both bit
    positions (0 for LSB, 7 for MSB). Uses the EOF delimiter to detect
    successful extraction.

    Args:
        stego_image: Stego image as numpy array (expected in BGR format
                     as loaded by _load_image).

    Returns:
        The extracted secret message.

    Raises:
        ValueError: If no valid message is found across all combinations.
    """
    from itertools import permutations

    if stego_image.ndim != 3 or stego_image.shape[2] != 3:
        raise ValueError("Brute-force extraction only supports 3-channel images.")

    # All permutations of channel indices (0,1,2)
    channel_permutations = list(permutations([0, 1, 2], 3))
    # Bit positions to try: 0 = LSB, 7 = MSB
    bit_positions = [0, 7]

    for ch_order in channel_permutations:
        # Reorder channels according to permutation
        permuted_img = stego_image[..., ch_order]
        for bit_pos in bit_positions:
            try:
                # Attempt extraction with no key/XOR
                msg = _extract_sequential_bits(
                    permuted_img, key="", use_xor=False, bit_pos=bit_pos
                )
                # If we get here, extraction succeeded
                return msg
            except ValueError:
                # EOF not found for this combination; try next
                continue
            except Exception:
                # Other unexpected errors; skip this combination
                continue

    raise ValueError(
        "No valid message found across all channel permutations and bit positions. "
        "Ensure the image contains a sequentially LSB/MSB embedded message without XOR."
    )


def extract_sequential(stego_image: np.ndarray, key: str = "",
                       use_xor: bool = False) -> str:
    """
    Extract a hidden message from a stego image using Sequential LSB (bit position 0).
    This function maintains backward compatibility with existing code.

    Reads LSBs sequentially from pixel (0,0), accumulating bits
    until the EOF delimiter is found.

    Args:
        stego_image: Stego image as numpy array.
        key: Password/key for XOR decryption.
        use_xor: Whether to apply XOR decryption after extraction.

    Returns:
        The extracted secret message.

    Raises:
        ValueError: If no valid message is found or extraction fails.
    """
    return _extract_sequential_bits(stego_image, key, use_xor, bit_pos=0)
