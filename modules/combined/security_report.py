"""
Security Report Module — MahesaVault
Generates security analysis text for the Dual-Lock system.
"""


def generate_report(encode_info=None):
    """Generate formatted security analysis for Dual-Lock."""
    report = """
## 🔐 MahesaVault Dual-Lock — Security Analysis Report

### Architecture Overview
MahesaVault employs a **Double-Lock Architecture** combining two independent security layers:

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Layer 1 | AES-256-CBC Encryption | Data confidentiality |
| Layer 2 | Random LSB Steganography | Data concealment |

### Attack Scenario Analysis

#### Scenario 1: Image Interception
> An attacker intercepts the stego image during transmission.

- **Threat Level:** LOW
- The image appears as a normal photograph
- No visual artifacts indicate hidden data
- The attacker must first **suspect** steganography is being used
- **Result:** Attack fails ✅

#### Scenario 2: Steganalysis Detection
> An attacker knows LSB steganography was used and extracts the data.

- **Threat Level:** LOW
- Random LSB distributes changes across the entire image (not sequential)
- Without the correct key, the PRNG seed cannot be reconstructed
- Even if extracted, the data is AES-256 encrypted ciphertext
- **Result:** Attack yields only encrypted gibberish ✅

#### Scenario 3: Known Cipher Attack
> An attacker knows both the stego method AND the cipher used.

- **Threat Level:** MINIMAL
- AES-256 key space: 2^256 ≈ 1.16 × 10^77 possible keys
- Brute-force at 10^18 keys/sec would take ~3.67 × 10^51 years
- This exceeds the estimated age of the universe (1.38 × 10^10 years)
- **Result:** Computationally infeasible ✅

### Security Conclusion
The system's security reduces to the **strength of the user's password**, which generates both:
1. The AES-256 encryption key (via SHA-256 hash)
2. The PRNG seed for pixel shuffling (via ASCII sum)

**Recommendation:** Use a strong password (12+ characters, mixed case, numbers, symbols).
"""
    if encode_info:
        report += f"""
### Encoding Details
- Original message length: **{encode_info.get('original_length', 'N/A')}** characters
- Ciphertext length: **{encode_info.get('ciphertext_length', 'N/A')}** characters
- Encryption: **{encode_info.get('encryption', 'AES-256-CBC')}**
- Steganography: **{encode_info.get('steganography', 'Random LSB')}**
"""
    return report
