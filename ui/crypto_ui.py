"""
Cryptography UI Page — MahesaVault
5 tabs: Encrypt, Decrypt, Key Generator, Security Comparison, Digital Signature.
"""

import streamlit as st
import hashlib

from modules.cryptography.classical import caesar, vigenere, playfair, hill, affine
from modules.cryptography.modern import (
    aes_cipher, rsa_cipher, des_cipher, triple_des_cipher,
    blowfish_cipher, chacha20_cipher
)
from modules.cryptography.key_generator import generate_rsa_keys, generate_aes_key
from modules.cryptography.advanced.lwe_cipher import generate_keys as lwe_gen, encrypt as lwe_enc, decrypt as lwe_dec
from modules.cryptography.advanced.paillier_cipher import generate_keys as paillier_gen, encrypt as paillier_enc, decrypt as paillier_dec, add_encrypted as paillier_add
import json
from modules.cryptography.digital_signature import sign_message, verify_signature
from modules.cryptography.math_visualizer import get_classical_steps, get_comparison_table
from ui.components.theme_3d import render_page_header, log_operation


CLASSICAL = ["Caesar Cipher", "Vigenere Cipher", "Playfair Cipher"]
MODERN = ["AES-256", "RSA-2048"]


def _encrypt_classical(name, text, key):
    """Dispatch encryption to the selected classical cipher."""
    if name == "Caesar Cipher":
        return caesar.encrypt(text, int(key))
    elif name == "Vigenere Cipher":
        return vigenere.encrypt(text, key)
    elif name == "Playfair Cipher":
        return playfair.encrypt(text, key)
    elif name == "Hill Cipher":
        mat = hill.parse_key_matrix(key)
        return hill.encrypt(text, mat)
    elif name == "Affine Cipher":
        parts = key.split(',')
        return affine.encrypt(text, int(parts[0].strip()), int(parts[1].strip()))


def _decrypt_classical(name, text, key):
    """Dispatch decryption to the selected classical cipher."""
    if name == "Caesar Cipher":
        return caesar.decrypt(text, int(key))
    elif name == "Vigenere Cipher":
        return vigenere.decrypt(text, key)
    elif name == "Playfair Cipher":
        return playfair.decrypt(text, key)
    elif name == "Hill Cipher":
        mat = hill.parse_key_matrix(key)
        return hill.decrypt(text, mat)
    elif name == "Affine Cipher":
        parts = key.split(',')
        return affine.decrypt(text, int(parts[0].strip()), int(parts[1].strip()))


def _encrypt_modern(name, text, key):
    """Dispatch encryption to the selected modern cipher."""
    if name == "AES-256":
        return aes_cipher.encrypt(text, key)
    elif name == "RSA-2048":
        return rsa_cipher.encrypt(text, key)  # key = public_key_pem
    elif name == "DES (via 3DES)":
        return des_cipher.encrypt(text, key)
    elif name == "3DES (Triple DES)":
        return triple_des_cipher.encrypt(text, key)
    elif name == "Blowfish":
        return blowfish_cipher.encrypt(text, key)
    elif name == "ChaCha20":
        return chacha20_cipher.encrypt(text, key)


def _decrypt_modern(name, text, key):
    """Dispatch decryption to the selected modern cipher."""
    if name == "AES-256":
        return aes_cipher.decrypt(text, key)
    elif name == "RSA-2048":
        return rsa_cipher.decrypt(text, key)  # key = private_key_pem
    elif name == "DES (via 3DES)":
        return des_cipher.decrypt(text, key)
    elif name == "3DES (Triple DES)":
        return triple_des_cipher.decrypt(text, key)
    elif name == "Blowfish":
        return blowfish_cipher.decrypt(text, key)
    elif name == "ChaCha20":
        return chacha20_cipher.decrypt(text, key)


def _key_hint(cipher_name):
    """Return a hint string for the key format."""
    hints = {
        "Caesar Cipher": "Integer shift (e.g., 3)",
        "Vigenere Cipher": "Keyword (e.g., SECRET)",
        "Playfair Cipher": "Keyword (e.g., MONARCHY)",
        "Hill Cipher": "Comma-separated matrix (e.g., 3,3,2,5)",
        "Affine Cipher": "a,b (e.g., 5,8 — a must be coprime with 26)",
    }
    return hints.get(cipher_name, "Password / Key")


def render():
    """Render the Cryptography module page."""
    render_page_header(
        "🔒",
        "Cryptography Module",
        "Classical & modern ciphers with mathematical analysis.",
        accent="#f472b6",
    )

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🔐 Encrypt", "🔓 Decrypt", "🔑 Key Generator",
        "📊 Security Comparison", "✍️ Digital Signature", "🌌 Advanced Crypto"
    ])

    # ─── TAB 1: ENCRYPT ───
    with tab1:
        plaintext = st.text_area("Plaintext", height=100,
                                  placeholder="Enter message to encrypt...",
                                  key="crypto_pt")

        col_c, col_m = st.columns(2)

        with col_c:
            st.markdown("""<div style="color:#00f5ff; font-weight:600;
                          font-family:'Courier New',monospace; font-size:14px;">
                          CLASSICAL CIPHER</div>""", unsafe_allow_html=True)
            c_cipher = st.selectbox("Select Classical", CLASSICAL, key="c_enc_sel")
            c_key = st.text_input(f"Key ({_key_hint(c_cipher)})", key="c_enc_key")

            if st.button("Encrypt (Classical)", key="c_enc_btn",
                         use_container_width=True):
                if plaintext and c_key:
                    try:
                        result = _encrypt_classical(c_cipher, plaintext, c_key)
                        st.session_state['c_enc_result'] = result
                        log_operation("Cryptography", f"Encrypt {c_cipher}", "success")
                        st.code(result, language=None)
                        # Show math steps
                        steps = get_classical_steps(c_cipher, plaintext, c_key)
                        with st.expander("📐 Mathematical Steps"):
                            st.markdown(steps)
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.warning("Enter plaintext and key")

        with col_m:
            st.markdown("""<div style="color:#f472b6; font-weight:600;
                          font-family:'Courier New',monospace; font-size:14px;">
                          MODERN CIPHER</div>""", unsafe_allow_html=True)
            m_cipher = st.selectbox("Select Modern", MODERN, key="m_enc_sel")

            if m_cipher == "RSA-2048":
                m_key = st.text_area("Public Key (PEM)", height=100,
                                      key="m_enc_key_rsa",
                                      placeholder="Paste RSA public key...")
            else:
                m_key = st.text_input("Password", type="password",
                                       key="m_enc_key")

            if m_cipher == "DES (via 3DES)":
                st.caption("⚠️ DES deprecated since 1999. Using 3DES internally.")

            if st.button("Encrypt (Modern)", key="m_enc_btn",
                         use_container_width=True):
                if plaintext and m_key:
                    try:
                        result = _encrypt_modern(m_cipher, plaintext, m_key)
                        st.session_state['m_enc_result'] = result
                        log_operation("Cryptography", f"Encrypt {m_cipher}", "success")
                        st.code(result, language=None)
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.warning("Enter plaintext and key")

    # ─── TAB 2: DECRYPT ───
    with tab2:
        ciphertext = st.text_area("Ciphertext", height=100,
                                   placeholder="Enter ciphertext to decrypt...",
                                   key="crypto_ct")

        col_cd, col_md = st.columns(2)

        with col_cd:
            st.markdown("""<div style="color:#00f5ff; font-weight:600;
                          font-family:'Courier New',monospace; font-size:14px;">
                          CLASSICAL CIPHER</div>""", unsafe_allow_html=True)
            cd_cipher = st.selectbox("Select Classical", CLASSICAL, key="c_dec_sel")
            cd_key = st.text_input(f"Key ({_key_hint(cd_cipher)})", key="c_dec_key")

            if st.button("Decrypt (Classical)", key="c_dec_btn",
                         use_container_width=True):
                if ciphertext and cd_key:
                    try:
                        result = _decrypt_classical(cd_cipher, ciphertext, cd_key)
                        st.code(result, language=None)
                    except Exception as e:
                        st.error(f"Error: {e}")

        with col_md:
            st.markdown("""<div style="color:#f472b6; font-weight:600;
                          font-family:'Courier New',monospace; font-size:14px;">
                          MODERN CIPHER</div>""", unsafe_allow_html=True)
            md_cipher = st.selectbox("Select Modern", MODERN, key="m_dec_sel")

            if md_cipher == "RSA-2048":
                md_key = st.text_area("Private Key (PEM)", height=100,
                                       key="m_dec_key_rsa",
                                       placeholder="Paste RSA private key...")
            else:
                md_key = st.text_input("Password", type="password",
                                        key="m_dec_key")

            if st.button("Decrypt (Modern)", key="m_dec_btn",
                         use_container_width=True):
                if ciphertext and md_key:
                    try:
                        result = _decrypt_modern(md_cipher, ciphertext, md_key)
                        st.code(result, language=None)
                    except Exception as e:
                        st.error(f"Error: {e}")

    # ─── TAB 3: KEY GENERATOR ───
    with tab3:
        st.markdown("##### 🔑 Cryptographic Key Generator")
        key_type = st.selectbox("Key Type", ["RSA 2048-bit", "AES-256"],
                                 key="keygen_type")

        if st.button("🔄 Generate Keys", type="primary",
                     use_container_width=True, key="keygen_btn"):
            if key_type == "RSA 2048-bit":
                with st.spinner("Generating RSA key pair..."):
                    keys = generate_rsa_keys()
                st.success("✅ RSA-2048 key pair generated!")
                c1, c2 = st.columns(2)
                with c1:
                    st.text_area("🔐 Private Key", keys['private_key'],
                                 height=300, key="rsa_priv")
                with c2:
                    st.text_area("🔓 Public Key", keys['public_key'],
                                 height=300, key="rsa_pub")
            else:
                keys = generate_aes_key()
                st.success(f"✅ AES-{keys['key_size_bits']} key generated!")
                st.text_input("Base64 Key", keys['key_base64'], key="aes_b64")
                st.text_input("Hex Key", keys['key_hex'], key="aes_hex")

    # ─── TAB 4: SECURITY COMPARISON ───
    with tab4:
        st.markdown("##### 📊 Security Comparison — Classical vs Modern")
        st.markdown(get_comparison_table())

        # Key space bar chart
        st.markdown("**Key Space Size (log₂ scale)**")
        import pandas as pd
        chart_data = pd.DataFrame({
            'Cipher': ['Caesar', 'Affine', 'Vigenere(5)', 'Hill 2×2',
                       'DES', '3DES', 'AES-128', 'RSA-2048',
                       'AES-256', 'ChaCha20'],
            'Key Space (log₂)': [4.6, 8.3, 23.5, 18.8,
                                  56, 112, 128, 112,
                                  256, 256]
        })
        st.bar_chart(chart_data.set_index('Cipher'))

    # ─── TAB 5: DIGITAL SIGNATURE ───
    with tab5:
        st.markdown("##### ✍️ Digital Signature (RSA-PSS / SHA-256)")

        sig_tab1, sig_tab2 = st.tabs(["Sign", "Verify"])

        with sig_tab1:
            sig_msg = st.text_area("Message to sign", key="sig_msg",
                                    placeholder="Enter message...")
            sig_priv = st.text_area("Private Key (PEM)", height=200,
                                     key="sig_priv",
                                     placeholder="Paste RSA private key...")
            if st.button("✍️ Sign Message", key="sig_btn",
                         use_container_width=True):
                if sig_msg and sig_priv:
                    try:
                        sig = sign_message(sig_msg, sig_priv)
                        st.success("✅ Message signed!")
                        st.text_area("Signature (Base64)", sig, key="sig_out")
                    except Exception as e:
                        st.error(f"Error: {e}")

        with sig_tab2:
            ver_msg = st.text_area("Original Message", key="ver_msg")
            ver_sig = st.text_area("Signature (Base64)", key="ver_sig")
            ver_pub = st.text_area("Public Key (PEM)", height=200,
                                    key="ver_pub",
                                    placeholder="Paste RSA public key...")
            if st.button("🔍 Verify Signature", key="ver_btn",
                         use_container_width=True):
                if ver_msg and ver_sig and ver_pub:
                    try:
                        result = verify_signature(ver_msg, ver_sig, ver_pub)
                        if result['valid']:
                            st.success(result['message'])
                        else:
                            st.error(result['message'])
                        # Show SHA-256 hash
                        st.markdown(f"""
                        <div style="background:#141c2e; border:1px solid rgba(16,185,129,0.3);
                                    border-radius:12px; padding:16px; margin-top:12px;">
                            <div style="font-size:10px; color:rgba(226,232,240,0.4);
                                        letter-spacing:0.1em; margin-bottom:6px;
                                        font-family:'Courier New',monospace;">
                                SHA-256 HASH OF ORIGINAL MESSAGE
                            </div>
                            <div style="font-family:'Courier New',monospace;
                                        color:#10b981; font-size:13px; word-break:break-all;">
                                {result['sha256_hash']}
                            </div>
                            <div style="font-size:11px; color:rgba(226,232,240,0.35);
                                        margin-top:8px;">
                                This hash proves message integrity — any modification
                                to the message would produce a completely different hash.
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Error: {e}")
