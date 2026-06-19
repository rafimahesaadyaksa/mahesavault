"""Test script for brute-force extraction module."""
import numpy as np
from modules.steganography.lsb_sequential import embed_sequential
from modules.steganography.bruteforce_extract import bruteforce_extract

EOF_DELIMITER = '1111111111111110'

# Test 1: Standard MahesaVault embedding (BGR, interleaved, LSB, row-major)
print("=== Test 1: Standard MahesaVault embed + brute-force extract ===")
img = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
msg = "Hello from MahesaVault!"
stego = embed_sequential(img, msg)
result = bruteforce_extract(stego)
print(f"  Success: {result['success']}")
print(f"  Message: {result['message']}")
print(f"  Method:  {result['method']}")
print(f"  Attempts: {result['attempts']}")
print(f"  Match:   {result['message'] == msg}")
assert result['success'] and result['message'] == msg, "TEST 1 FAILED"
print("  [OK] PASSED\n")

# Test 2: Simulate external tool using RGB channel order (not BGR)
print("=== Test 2: Simulated external tool (RGB order, LSB) ===")
img2 = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
# Swap channels before embedding (simulate RGB tool)
img2_rgb = img2[..., [2, 1, 0]]  # BGR -> RGB
stego2_rgb = embed_sequential(img2_rgb, "External tool message")
# Swap back to BGR (as if loaded by OpenCV)
stego2 = stego2_rgb[..., [2, 1, 0]]
result2 = bruteforce_extract(stego2)
print(f"  Success: {result2['success']}")
print(f"  Message: {result2['message']}")
print(f"  Method:  {result2['method']}")
print(f"  Match:   {result2['message'] == 'External tool message'}")
assert result2['success'] and result2['message'] == "External tool message", "TEST 2 FAILED"
print("  [OK] PASSED\n")

# Test 3: MSB embedding
print("=== Test 3: MSB embedding ===")
img3 = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
msg3 = "MSB hidden"
# Manually embed in MSB (bit 7)
binary = ''.join(format(ord(c), '08b') for c in msg3) + EOF_DELIMITER
flat = img3.flatten().copy()
for i, bit in enumerate(binary):
    flat[i] = (flat[i] & 0x7F) | (int(bit) << 7)
stego3 = flat.reshape(img3.shape)
result3 = bruteforce_extract(stego3)
print(f"  Success: {result3['success']}")
print(f"  Message: {result3['message']}")
print(f"  Method:  {result3['method']}")
print(f"  Match:   {result3['message'] == msg3}")
assert result3['success'] and result3['message'] == msg3, "TEST 3 FAILED"
print("  [OK] PASSED\n")

# Test 4: Per-channel embedding (all R channel first, then G, then B)
print("=== Test 4: Per-channel embedding (R->G->B separately) ===")
img4 = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8).copy()
msg4 = "Per-channel mode"
binary4 = ''.join(format(ord(c), '08b') for c in msg4) + EOF_DELIMITER
# Embed into channels sequentially: all of R, then G, then B
flat_r = img4[..., 0].flatten().copy()
flat_g = img4[..., 1].flatten().copy()
flat_b = img4[..., 2].flatten().copy()
all_channels = np.concatenate([flat_b, flat_g, flat_r])  # BGR order
for i, bit in enumerate(binary4):
    all_channels[i] = (all_channels[i] & 0xFE) | int(bit)
# Reconstruct
n = flat_r.shape[0]
img4[..., 0] = all_channels[2*n:3*n].reshape(img4.shape[:2])  # R was last in concat
img4[..., 1] = all_channels[n:2*n].reshape(img4.shape[:2])    # G was middle
img4[..., 2] = all_channels[:n].reshape(img4.shape[:2])        # B was first
result4 = bruteforce_extract(img4)
print(f"  Success: {result4['success']}")
print(f"  Message: {result4['message']}")
print(f"  Method:  {result4['method']}")
print(f"  Match:   {result4['message'] == msg4}")
assert result4['success'] and result4['message'] == msg4, "TEST 4 FAILED"
print("  [OK] PASSED\n")

# Test 5: Null-byte terminator (single 0x00)
print("=== Test 5: Null-byte terminator ===")
img5 = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
msg5 = "Null terminated"
binary5 = ''.join(format(ord(c), '08b') for c in msg5) + '00000000'
flat5 = img5.flatten().copy()
for i, bit in enumerate(binary5):
    flat5[i] = (flat5[i] & 0xFE) | int(bit)
stego5 = flat5.reshape(img5.shape)
result5 = bruteforce_extract(stego5)
print(f"  Success: {result5['success']}")
print(f"  Message: {result5['message']}")
print(f"  Method:  {result5['method']}")
print(f"  Match:   {result5['message'] == msg5}")
assert result5['success'] and result5['message'] == msg5, "TEST 5 FAILED"
print("  [OK] PASSED\n")

# Test 6: Column-major traversal
print("=== Test 6: Column-major pixel traversal ===")
img6 = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
msg6 = "Column major"
binary6 = ''.join(format(ord(c), '08b') for c in msg6) + EOF_DELIMITER
# Transpose and embed (simulate column-major traversal)
transposed = np.transpose(img6, (1, 0, 2))
flat6 = transposed.flatten().copy()
for i, bit in enumerate(binary6):
    flat6[i] = (flat6[i] & 0xFE) | int(bit)
transposed_stego = flat6.reshape(transposed.shape)
stego6 = np.transpose(transposed_stego, (1, 0, 2))
result6 = bruteforce_extract(stego6)
print(f"  Success: {result6['success']}")
print(f"  Message: {result6['message']}")
print(f"  Method:  {result6['method']}")
print(f"  Match:   {result6['message'] == msg6}")
assert result6['success'] and result6['message'] == msg6, "TEST 6 FAILED"
print("  [OK] PASSED\n")

# Test 7: No delimiter (raw string embedded)
print("=== Test 7: No delimiter (read until non-printable) ===")
img7 = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
msg7 = "Raw string without any terminator"
binary7 = ''.join(format(ord(c), '08b') for c in msg7)
flat7 = img7.flatten().copy()
for i, bit in enumerate(binary7):
    flat7[i] = (flat7[i] & 0xFE) | int(bit)
stego7 = flat7.reshape(img7.shape)
result7 = bruteforce_extract(stego7)
print(f"  Success: {result7['success']}")
print(f"  Message: {result7['message']}")
print(f"  Method:  {result7['method']}")
print(f"  Match:   {result7['message'] == msg7}")
assert result7['success'] and result7['message'] == msg7, "TEST 7 FAILED"
print("  [OK] PASSED\n")

print("=" * 50)
print("ALL 7 TESTS PASSED!")
print("=" * 50)
