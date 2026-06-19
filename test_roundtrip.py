"""Quick roundtrip test for all core MahesaVault modules."""
import sys
sys.path.insert(0, '.')

passed = 0
failed = 0

def test(name, condition):
    global passed, failed
    if condition:
        print(f"  PASS: {name}")
        passed += 1
    else:
        print(f"  FAIL: {name}")
        failed += 1

print("=== MahesaVault Core Tests ===\n")

# XOR
from modules.steganography.xor_cipher import xor_encrypt, xor_decrypt
msg = "Hello MahesaVault!"
enc = xor_encrypt(msg, "secret")
dec = xor_decrypt(enc, "secret")
test("XOR roundtrip", dec == msg)

# Caesar
from modules.cryptography.classical.caesar import encrypt as ce, decrypt as cd
test("Caesar roundtrip", cd(ce("HELLO", 3), 3) == "HELLO")

# Vigenere
from modules.cryptography.classical.vigenere import encrypt as ve, decrypt as vd
test("Vigenere roundtrip", vd(ve("HELLO", "KEY"), "KEY") == "HELLO")

# Affine
from modules.cryptography.classical.affine import encrypt as ae, decrypt as ad
test("Affine roundtrip", ad(ae("HELLO", 5, 8), 5, 8) == "HELLO")

# AES
from modules.cryptography.modern.aes_cipher import encrypt as aese, decrypt as aesd
ct = aese("Test message", "password123")
test("AES-256 roundtrip", aesd(ct, "password123") == "Test message")

# DES (3DES)
from modules.cryptography.modern.des_cipher import encrypt as dese, decrypt as desd
ct2 = dese("Test DES", "mypassword")
test("DES(3DES) roundtrip", desd(ct2, "mypassword") == "Test DES")

# ChaCha20
from modules.cryptography.modern.chacha20_cipher import encrypt as cce, decrypt as ccd
ct3 = cce("ChaCha test", "pass123")
test("ChaCha20 roundtrip", ccd(ct3, "pass123") == "ChaCha test")

# Blowfish
from modules.cryptography.modern.blowfish_cipher import encrypt as bfe, decrypt as bfd
ct4 = bfe("Blowfish test", "pass456")
test("Blowfish roundtrip", bfd(ct4, "pass456") == "Blowfish test")

# LSB Sequential
import numpy as np
from modules.steganography.lsb_sequential import embed_sequential, extract_sequential
img = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
stego = embed_sequential(img.copy(), "Secret!", "key", use_xor=True)
extracted = extract_sequential(stego, "key", use_xor=True)
test("Sequential LSB roundtrip", extracted == "Secret!")

# LSB Random
from modules.steganography.lsb_random import embed_random, extract_random
stego2 = embed_random(img.copy(), "Random secret", "mykey", use_xor=True)
extracted2 = extract_random(stego2, "mykey", use_xor=True)
test("Random LSB roundtrip", extracted2 == "Random secret")

# Quality Metrics
from modules.steganography.quality_metrics import get_all_metrics
metrics = get_all_metrics(img, stego)
test("PSNR > 30 dB", metrics['psnr'] > 30)
test("SSIM > 0.99", metrics['ssim'] > 0.99)

# Capacity
from modules.steganography.capacity import calculate_capacity
cap = calculate_capacity(img)
test("Capacity calculation", cap['max_chars'] > 0)

# Dual Lock
from modules.combined.dual_lock import dual_lock_encode, dual_lock_decode
big_img = np.random.randint(0, 256, (200, 200, 3), dtype=np.uint8)
dl_stego, dl_ct, dl_info = dual_lock_encode(big_img.copy(), "Dual lock test!", "strongpwd")
dl_plain, _, _ = dual_lock_decode(dl_stego, "strongpwd")
test("Dual-Lock full pipeline", dl_plain == "Dual lock test!")

print(f"\n=== Results: {passed} passed, {failed} failed ===")
if failed == 0:
    print("ALL TESTS PASSED!")
