"""
Automated Brute-Force / Heuristic LSB & MSB Extraction — MahesaVault

Attempts to extract hidden messages from stego images produced by
ANY steganography tool, by systematically trying many common encoding
conventions:

  1. Channel order: all permutations of (R, G, B) — 6 total
  2. Bit position: LSB (bit 0) and MSB (bit 7)
  3. Pixel traversal: row-major (normal) and column-major (transposed)
  4. Bit ordering within bytes: MSB-first (standard) and LSB-first
  5. Embedding mode: interleaved (R,G,B per pixel) vs per-channel
     (all R, then all G, then all B)
  6. EOF / termination: EOF delimiter, null-byte, length-prefixed (32-bit)
  7. Alpha channel: include or exclude alpha in 4-channel images

This module ONLY handles LSB/MSB extraction WITHOUT password or XOR.
"""

import numpy as np
from itertools import permutations
import re


# ─── Known EOF delimiters used by various stego tools ────────────────────────
KNOWN_DELIMITERS = [
    '1111111111111110',               # MahesaVault EOF (16 bits)
    '0000000000000000',               # Null-byte (16 zeros = two 0x00)
    '00000000',                       # Single null byte
    ''.join(format(ord(c), '08b')     # "$t3g0" marker
            for c in '$t3g0'),
    ''.join(format(ord(c), '08b')     # "STOP" marker
            for c in 'STOP'),
]

# Minimum message length in characters to accept as valid
MIN_MSG_LEN = 1
# Maximum bits to scan before giving up on a single combination
MAX_SCAN_BITS = 500_000


def _is_printable_text(text: str) -> bool:
    """
    Heuristic check: is the extracted string plausible human-readable text?
    Accepts ASCII printable characters (0x20-0x7E), common whitespace,
    and extended Latin characters up to 0xFF.
    """
    if not text or len(text) < MIN_MSG_LEN:
        return False
    # Count printable characters
    printable = sum(
        1 for c in text
        if (0x20 <= ord(c) <= 0x7E) or c in '\n\r\t'
    )
    ratio = printable / len(text)
    # Accept if ≥ 85% of characters are printable ASCII
    return ratio >= 0.85


def _extract_bits(flat_data: np.ndarray, bit_pos: int,
                  max_bits: int) -> str:
    """
    Extract bits from a flat array at the specified bit position.
    Returns a string of '0' and '1' characters.
    """
    n = min(len(flat_data), max_bits)
    mask = 1 << bit_pos
    bits = ((flat_data[:n] & mask) >> bit_pos).astype(np.uint8)
    return ''.join(bits.astype(str))


def _bits_to_text_msb_first(bits: str) -> str:
    """Convert bit string to text, reading each byte MSB-first (standard)."""
    chars = []
    for i in range(0, len(bits) - 7, 8):
        byte = bits[i:i+8]
        chars.append(chr(int(byte, 2)))
    return ''.join(chars)


def _bits_to_text_lsb_first(bits: str) -> str:
    """Convert bit string to text, reading each byte LSB-first (reversed)."""
    chars = []
    for i in range(0, len(bits) - 7, 8):
        byte = bits[i:i+8][::-1]  # reverse bit order within byte
        chars.append(chr(int(byte, 2)))
    return ''.join(chars)


def _try_delimiter_extraction(bits: str, delimiter: str,
                              bit_order: str) -> str | None:
    """
    Search for a delimiter in the bit stream and extract text before it.
    Returns the decoded text or None if delimiter not found / text invalid.

    For short delimiters (8 bits), only match at byte boundaries to prevent
    false positives where the delimiter matches inside a character's bits.
    """
    delim_len = len(delimiter)

    if delim_len <= 8:
        # Short delimiter — search only at byte boundaries
        idx = -1
        for pos in range(0, len(bits) - delim_len + 1, 8):
            if bits[pos:pos + delim_len] == delimiter:
                idx = pos
                break
    else:
        # Longer delimiters are unlikely to false-match; use fast find
        idx = bits.find(delimiter)

    if idx == -1 or idx == 0:
        return None
    # Message bits are everything before the delimiter
    msg_bits = bits[:idx]
    if len(msg_bits) % 8 != 0:
        # Trim to nearest byte boundary
        msg_bits = msg_bits[:len(msg_bits) - (len(msg_bits) % 8)]
    if len(msg_bits) < 8:
        return None

    if bit_order == 'msb':
        text = _bits_to_text_msb_first(msg_bits)
    else:
        text = _bits_to_text_lsb_first(msg_bits)

    if _is_printable_text(text):
        return text
    return None


def _try_length_prefix_extraction(bits: str, bit_order: str) -> str | None:
    """
    Some tools embed a 32-bit length prefix (number of message characters)
    before the actual message bits.
    """
    if len(bits) < 40:  # need at least 32 header + 8 data
        return None

    header = bits[:32]
    if bit_order == 'msb':
        msg_len = int(header, 2)
    else:
        msg_len = int(header[::-1], 2)

    # Sanity check: message length should be reasonable
    if msg_len <= 0 or msg_len > 100_000:
        return None

    needed_bits = 32 + msg_len * 8
    if needed_bits > len(bits):
        return None

    msg_bits = bits[32:needed_bits]
    if bit_order == 'msb':
        text = _bits_to_text_msb_first(msg_bits)
    else:
        text = _bits_to_text_lsb_first(msg_bits)

    if _is_printable_text(text):
        return text
    return None


def _try_no_delimiter_extraction(bits: str, bit_order: str) -> str | None:
    """
    Heuristic: Read characters until we hit a non-printable character.
    If the valid printable prefix is long enough, assume it's the message.
    This handles tools that embed raw strings without any delimiter.
    """
    chars = []
    # Read byte by byte
    for i in range(0, len(bits) - 7, 8):
        byte = bits[i:i+8]
        if bit_order == 'lsb':
            byte = byte[::-1]
        c = chr(int(byte, 2))
        
        # Check if printable (ASCII 0x20-0x7E + common whitespace)
        if (0x20 <= ord(c) <= 0x7E) or c in '\n\r\t':
            chars.append(c)
        else:
            break
            
    text = ''.join(chars)
    # Require at least 8 characters to avoid false positives from random noise
    if len(text) >= 8:
        return text
    return None


def _flatten_interleaved(image: np.ndarray, ch_order: tuple) -> np.ndarray:
    """
    Flatten image pixel-by-pixel with channels in the given order.
    Standard interleaved mode: for each pixel → read channels in ch_order.
    """
    reordered = image[..., list(ch_order)]
    return reordered.flatten()


def _flatten_per_channel(image: np.ndarray, ch_order: tuple) -> np.ndarray:
    """
    Flatten image channel-by-channel (all pixels from ch0, then ch1, then ch2).
    Some tools embed all bits in the Red channel first, then Green, then Blue.
    """
    channels = [image[..., c].flatten() for c in ch_order]
    return np.concatenate(channels)


def _flatten_column_major(image: np.ndarray, ch_order: tuple) -> np.ndarray:
    """
    Flatten image column-by-column (transpose) with interleaved channels.
    Some tools read pixels top-to-bottom, left-to-right instead of
    left-to-right, top-to-bottom.
    """
    transposed = np.transpose(image, (1, 0, 2))  # swap rows and columns
    reordered = transposed[..., list(ch_order)]
    return reordered.flatten()


def bruteforce_extract(image: np.ndarray, progress_callback=None) -> dict:
    """
    Automated brute-force extraction for LSB and MSB steganography
    WITHOUT password or XOR.

    Systematically tries all combinations of:
      - Channel orders: (0,1,2), (2,1,0), (0,2,1), ... (6 permutations)
      - Bit positions: 0 (LSB) and 7 (MSB)
      - Pixel traversal: row-major, column-major
      - Embedding mode: interleaved, per-channel
      - Bit ordering: MSB-first, LSB-first within each byte
      - EOF strategies: known delimiters, length-prefix

    For 4-channel (RGBA) images, also tries 3-channel subsets.

    Args:
        image: Stego image as numpy array (H, W, C) — BGR format from OpenCV.
        progress_callback: Optional callable(current, total) for progress.

    Returns:
        Dictionary with:
          - 'success': bool
          - 'message': extracted text (if success)
          - 'method': human-readable description of the winning combination
          - 'attempts': total number of combinations tried
          - 'results': list of all successful extractions (may be > 1)

    Raises:
        ValueError: If image has unsupported format.
    """
    if image.ndim != 3:
        raise ValueError("Brute-force extraction requires a color image (3+ channels).")

    n_channels = image.shape[2]
    results = []
    attempt = 0

    # Determine which channel subsets to try
    if n_channels == 4:
        # RGBA: try both (0,1,2) RGB-only and (0,1,2,3) with alpha
        channel_sets = [
            list(permutations(range(3))),      # 3-channel RGB subsets
            list(permutations(range(4), 3)),    # 3 of 4 channels
        ]
        channel_perms = []
        for cs in channel_sets:
            channel_perms.extend(cs)
        # Deduplicate while preserving order
        seen = set()
        unique_perms = []
        for p in channel_perms:
            if p not in seen:
                seen.add(p)
                unique_perms.append(p)
        channel_perms = unique_perms
    elif n_channels == 3:
        channel_perms = list(permutations(range(3)))
    else:
        raise ValueError(f"Unsupported number of channels: {n_channels}")

    bit_positions = [0, 7]                       # LSB, MSB
    bit_orders = ['msb', 'lsb']                  # bit order within byte
    traversals = ['row', 'column']               # pixel traversal
    embed_modes = ['interleaved', 'per_channel']  # embedding mode

    # Calculate total combinations for progress
    total = (len(channel_perms) * len(bit_positions) * len(bit_orders)
             * len(traversals) * len(embed_modes))

    for ch_order in channel_perms:
        # Prepare the image with only the selected channels
        if max(ch_order) < n_channels:
            img_subset = image
        else:
            continue  # skip invalid channel indices

        for traversal in traversals:
            for embed_mode in embed_modes:
                # Build flat data according to traversal and embed mode
                if traversal == 'row' and embed_mode == 'interleaved':
                    flat = _flatten_interleaved(img_subset, ch_order)
                elif traversal == 'row' and embed_mode == 'per_channel':
                    flat = _flatten_per_channel(img_subset, ch_order)
                elif traversal == 'column' and embed_mode == 'interleaved':
                    flat = _flatten_column_major(img_subset, ch_order)
                else:  # column + per_channel
                    transposed = np.transpose(img_subset, (1, 0, 2))
                    flat = _flatten_per_channel(transposed, ch_order)

                for bit_pos in bit_positions:
                    bits = _extract_bits(flat, bit_pos, MAX_SCAN_BITS)

                    for bit_order in bit_orders:
                        attempt += 1

                        if progress_callback:
                            progress_callback(attempt, total)

                        # ─── Strategy 1: Known delimiters ───
                        for delim in KNOWN_DELIMITERS:
                            text = _try_delimiter_extraction(
                                bits, delim, bit_order
                            )
                            if text:
                                ch_names = _channel_names(ch_order)
                                method = (
                                    f"{_bit_pos_name(bit_pos)} | "
                                    f"Channel: {ch_names} | "
                                    f"Traversal: {traversal}-major | "
                                    f"Mode: {embed_mode} | "
                                    f"Bit order: {bit_order.upper()}-first | "
                                    f"Delimiter: {_delim_name(delim)}"
                                )
                                results.append({
                                    'message': text,
                                    'method': method,
                                    'attempt': attempt,
                                })

                        # ─── Strategy 2: Length prefix ───
                        text = _try_length_prefix_extraction(bits, bit_order)
                        if text:
                            ch_names = _channel_names(ch_order)
                            method = (
                                f"{_bit_pos_name(bit_pos)} | "
                                f"Channel: {ch_names} | "
                                f"Traversal: {traversal}-major | "
                                f"Mode: {embed_mode} | "
                                f"Bit order: {bit_order.upper()}-first | "
                                f"Termination: 32-bit length prefix"
                            )
                            results.append({
                                'message': text,
                                'method': method,
                                'attempt': attempt,
                            })

                        # ─── Strategy 3: No delimiter (read until non-printable) ───
                        text = _try_no_delimiter_extraction(bits, bit_order)
                        if text:
                            ch_names = _channel_names(ch_order)
                            method = (
                                f"{_bit_pos_name(bit_pos)} | "
                                f"Channel: {ch_names} | "
                                f"Traversal: {traversal}-major | "
                                f"Mode: {embed_mode} | "
                                f"Bit order: {bit_order.upper()}-first | "
                                f"Termination: No delimiter (read until non-printable)"
                            )
                            results.append({
                                'message': text,
                                'method': method,
                                'attempt': attempt,
                            })

    # Deduplicate results by message content
    seen_msgs = set()
    unique_results = []
    for r in results:
        if r['message'] not in seen_msgs:
            seen_msgs.add(r['message'])
            unique_results.append(r)

    if unique_results:
        # Return the longest readable message as primary (most likely correct)
        best = max(unique_results, key=lambda r: len(r['message']))
        return {
            'success': True,
            'message': best['message'],
            'method': best['method'],
            'attempts': attempt,
            'results': unique_results,
        }

    return {
        'success': False,
        'message': '',
        'method': '',
        'attempts': attempt,
        'results': [],
    }


def _bit_pos_name(bit_pos: int) -> str:
    """Human-readable bit position name."""
    if bit_pos == 0:
        return "LSB (bit 0)"
    elif bit_pos == 7:
        return "MSB (bit 7)"
    return f"Bit {bit_pos}"


def _channel_names(ch_order: tuple) -> str:
    """Human-readable channel order."""
    mapping = {0: 'B', 1: 'G', 2: 'R', 3: 'A'}
    return '->'.join(mapping.get(c, str(c)) for c in ch_order)


def _delim_name(delim: str) -> str:
    """Human-readable delimiter name."""
    if delim == '1111111111111110':
        return 'MahesaVault EOF (0xFFFE)'
    elif delim == '0000000000000000':
        return 'Double null-byte'
    elif delim == '00000000':
        return 'Single null-byte'
    # Try to decode as ASCII
    try:
        chars = []
        for i in range(0, len(delim), 8):
            byte = delim[i:i+8]
            if len(byte) == 8:
                chars.append(chr(int(byte, 2)))
        name = ''.join(chars)
        if all(c.isprintable() for c in name):
            return f'"{name}" marker'
    except Exception:
        pass
    return f'Custom ({delim[:16]}...)'
