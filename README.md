# MahesaVault — Dual-Protocol Secure Vault

MahesaVault is a steganography and cryptography application built with Streamlit that combines classical and modern encryption techniques with image-based steganography to provide dual-layer security.

## Features

### 🔐 Cryptography Module
- **Classical Ciphers (3)**:
  - Caesar Cipher
  - Vigenere Cipher  
  - Playfair Cipher
- **Modern Ciphers (2)**:
  - AES-256 (military-grade encryption)
  - RSA-2048 (public-key cryptography)
- Digital Signature (RSA-PSS / SHA-256)
- Mathematical step-by-step visualization for classical ciphers
- Key generator for RSA and AES keys

### 🕵️ Steganography Module
- **LSB (Least Significant Bit) Techniques**:
  - Sequential LSB Embedding
  - Random LSB Embedding (key-dependent)
- XOR pre-encryption layer
- Steganalysis tools:
  - RGB Histogram Comparison
  - Bit-Plane Visualization
  - Error Map Analysis
- Quality metrics: PSNR, MSE, SSIM

### 🔐 Dual-Lock Module
- Flagship feature combining AES-256 encryption with Random LSB steganography
- Encrypt-then-Hide methodology
- Single password protection for both layers
- Security report generation
- Beyond 2^256 resistance

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd en-de-vault-lite
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

## Project Structure

```
en-de-vault-lite/
├── app.py                  # Main Streamlit application
├── requirements.txt       # Python dependencies
├── README.md              # This file
├── assets/                # Static assets (images, CSS)
│   ├── sample_images/     # Sample cover images
│   └── styles/            # Custom CSS
├── files/                 # Documentation
│   ├── ARCHITECTURE.md    # Detailed technical specification
│   ├── DESIGN.md          # Design principles
│   └── PROMPT.md          # Prompt engineering guidelines
├── modules/               # Core functionality
│   ├── cryptography/      # Encryption/decryption algorithms
│   │   ├── classical/     # Caesar, Vigenere, Playfair, Hill, Affine
│   │   ├── modern/        # AES, RSA, DES, 3DES, Blowfish, ChaCha20
│   │   ├── key_generator.py
│   │   ├── digital_signature.py
│   │   └── math_visualizer.py
│   ├── steganography/     # Steganography algorithms
│   │   ├── lsb_sequential.py
│   │   ├── lsb_random.py
│   │   ├── xor_cipher.py
│   │   ├── quality_metrics.py
│   │   ├── capacity.py
│   │   └── steganalysis.py
│   └── combined/          # Dual-lock and security reporting
│       ├── dual_lock.py
│       └── security_report.py
└── ui/                    # User interface components
    ├── __init__.py
    ├── home.py            # Landing page with 3D cards
    ├── stego_ui.py        # Steganography interface
    ├── crypto_ui.py       # Cryptography interface
    ├── combined_ui.py     # Dual-lock interface
    └── components/        # Reusable UI components
        ├── __init__.py
        ├── theme_3d.py    # 3D visual effects
        ├── metric_card.py
        └── histogram_plot.py
```

## Usage

### Cryptography Tab
1. Select either "Encrypt" or "Decrypt" tab
2. Choose between Classical or Modern ciphers
3. Enter your text and key/password
4. Click the encrypt/decrypt button
5. View results and mathematical steps (for classical ciphers)

### Steganography Tab
1. Navigate to the "Encoder" tab to hide messages:
   - Upload a PNG cover image
   - Enter your secret message
   - Set a password (for Random LSB/XOR)
   - Select LSB method (Sequential or Random)
   - Click "Generate Stego Image"
   - Download the stego image
2. Use the "Decoder" tab to extract messages:
   - Upload a stego image
   - Enter the password used during embedding
   - Select the same LSB method
   - Click "Extract Message"

### Dual-Lock Tab
1. Provides combined AES-256 encryption + LSB steganography
2. Single password protects both layers
3. Generate security reports for analysis

## Security Notes

- **Classical ciphers** are educational and should not be used for real security
- **Modern ciphers** (AES-256, RSA-2048) provide industry-standard security
- **Steganography** provides security through obscurity - best combined with encryption
- **Dual-Lock** offers the strongest protection by combining both approaches
- Always verify integrity using the built-in security reports and validation tools

## License

This project is for educational and demonstrative purposes.

## Acknowledgements

Built with Streamlit, OpenCV, NumPy, and the cryptography library.