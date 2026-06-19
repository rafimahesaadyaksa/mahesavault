# Tests without pytest
import numpy as np
import io
import wave
import base64

from modules.steganography.lsb_sequential import embed_file_sequential, extract_file_sequential
from modules.steganography.lsb_random import embed_file_random, extract_file_random
from modules.steganography.audio_stego import embed_audio, extract_audio, embed_file_audio, extract_file_audio
from modules.steganography.steganalysis import chi_square_attack

def test_file_steganography_sequential():
    cover = np.zeros((100, 100, 3), dtype=np.uint8)
    filename = "test.txt"
    file_bytes = b"Hello, File Steganography!"
    
    stego = embed_file_sequential(cover, filename, file_bytes)
    ext_filename, ext_bytes = extract_file_sequential(stego)
    
    assert ext_filename == filename
    assert ext_bytes == file_bytes

def test_file_steganography_random():
    cover = np.zeros((100, 100, 3), dtype=np.uint8)
    filename = "secret.bin"
    file_bytes = b"Secret bytes \x00\x01\x02"
    key = "secure_password"
    
    stego = embed_file_random(cover, filename, file_bytes, key)
    ext_filename, ext_bytes = extract_file_random(stego, key)
    
    assert ext_filename == filename
    assert ext_bytes == file_bytes

def test_audio_steganography():
    dummy_wav = io.BytesIO()
    with wave.open(dummy_wav, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(44100)
        w.writeframes(b'\x00\x00' * 1000)
    
    wav_bytes = dummy_wav.getvalue()
    msg = "Hidden in Audio"
    
    stego_wav = embed_audio(wav_bytes, msg)
    extracted = extract_audio(stego_wav)
    
    assert extracted == msg

def test_audio_file_steganography():
    dummy_wav = io.BytesIO()
    with wave.open(dummy_wav, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(44100)
        w.writeframes(b'\x00\x00' * 2000)
    
    wav_bytes = dummy_wav.getvalue()
    filename = "data.pdf"
    file_bytes = b"PDF FORMAT"
    key = "audio_key"
    
    stego_wav = embed_file_audio(wav_bytes, filename, file_bytes, key, use_xor=True)
    ext_filename, ext_bytes = extract_file_audio(stego_wav, key, use_xor=True)
    
    assert ext_filename == filename
    assert ext_bytes == file_bytes

def test_chi_square_attack():
    img = np.random.randint(0, 256, (100, 100), dtype=np.uint8)
    x, probs = chi_square_attack(img)
    
    assert len(x) == len(probs)
    assert x[-1] == 100.0
    # Since it's random, probability of embedding should be very high (close to 1.0)
    assert probs[-1] > 0.9
