"""
Combined Dual-Lock UI Page — MahesaVault
3D cinematic workflow + encrypt-then-hide pipeline.
"""

import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import cv2
from PIL import Image
from io import BytesIO

from modules.combined.dual_lock import dual_lock_encode, dual_lock_decode
from modules.combined.security_report import generate_report
from modules.steganography.quality_metrics import get_all_metrics
from ui.components.metric_card import render_metrics_row
from ui.components.theme_3d import (
    render_page_header,
    render_glass_message_box,
    log_operation,
)


def _load_image(uploaded_file):
    img = Image.open(uploaded_file).convert('RGB')
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)


def _image_to_bytes(img_array):
    img_rgb = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(img_rgb)
    buf = BytesIO()
    pil_img.save(buf, format='PNG')
    return buf.getvalue()


def _show_image(img_array, caption=""):
    rgb = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)
    st.image(rgb, caption=caption, use_container_width=True)


def _render_3d_workflow():
    """Parallax-style 3D pipeline diagram."""
    workflow_html = """
    <!DOCTYPE html>
    <html><head>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono&display=swap" rel="stylesheet">
    <style>
      body { margin:0; background:transparent; font-family:'JetBrains Mono',monospace; color:#e8ecf4; }
      .wf-label { text-align:center; margin:8px 0; }
      .wf-label span {
        font-size:9px; letter-spacing:0.2em; padding:4px 12px; border-radius:4px;
      }
      .enc span { background:rgba(0,245,255,0.1); color:#00f5ff; }
      .dec span { background:rgba(244,114,182,0.1); color:#f472b6; }
      .wf-row {
        display:flex; align-items:center; justify-content:center;
        flex-wrap:wrap; gap:4px; padding:12px 8px;
      }
      .wf-step {
        background:linear-gradient(145deg, rgba(22,30,48,0.95), rgba(8,10,18,0.98));
        border:1px solid rgba(255,255,255,0.08);
        border-radius:14px;
        padding:16px 18px;
        min-width:120px;
        text-align:center;
        transform: perspective(600px) rotateX(4deg);
        box-shadow: 0 16px 32px rgba(0,0,0,0.45);
        transition: transform 0.35s ease, box-shadow 0.35s ease;
      }
      .wf-step:hover {
        transform: perspective(600px) rotateX(0deg) translateY(-6px);
        box-shadow: 0 24px 48px rgba(0,245,255,0.12);
      }
      .wf-step.cyan { border-color:rgba(0,245,255,0.35); }
      .wf-step.pink { border-color:rgba(244,114,182,0.35); }
      .wf-step.gold { border-color:rgba(212,175,55,0.35); }
      .wf-icon { font-size:26px; margin-bottom:6px; }
      .wf-t { font-size:9px; color:rgba(226,232,240,0.4); text-transform:uppercase; letter-spacing:0.1em; }
      .wf-v { font-size:12px; margin-top:4px; font-weight:600; }
      .wf-arrow { font-size:20px; padding:0 4px; opacity:0.7; }
      .wf-arrow.c { color:#00f5ff; }
      .wf-arrow.p { color:#f472b6; }
    </style>
    </head><body>
    <div class="wf-label enc"><span>▶ ENCODING PIPELINE</span></div>
    <div class="wf-row">
      <div class="wf-step"><div class="wf-icon">📝</div><div class="wf-t">Input</div><div class="wf-v">Plaintext</div></div>
      <span class="wf-arrow c">→</span>
      <div class="wf-step pink"><div class="wf-icon">🔒</div><div class="wf-t">Layer 1</div><div class="wf-v">AES-256</div></div>
      <span class="wf-arrow c">→</span>
      <div class="wf-step cyan"><div class="wf-icon">🕵️</div><div class="wf-t">Layer 2</div><div class="wf-v">LSB Random</div></div>
      <span class="wf-arrow c">→</span>
      <div class="wf-step gold"><div class="wf-icon">🖼️</div><div class="wf-t">Output</div><div class="wf-v">Stego PNG</div></div>
    </div>
    <div class="wf-label dec"><span>◀ DECODING PIPELINE</span></div>
    <div class="wf-row">
      <div class="wf-step gold"><div class="wf-icon">🖼️</div><div class="wf-t">Input</div><div class="wf-v">Stego PNG</div></div>
      <span class="wf-arrow p">→</span>
      <div class="wf-step cyan"><div class="wf-icon">🕵️</div><div class="wf-t">Layer 2</div><div class="wf-v">Extract</div></div>
      <span class="wf-arrow p">→</span>
      <div class="wf-step pink"><div class="wf-icon">🔓</div><div class="wf-t">Layer 1</div><div class="wf-v">Decrypt</div></div>
      <span class="wf-arrow p">→</span>
      <div class="wf-step"><div class="wf-icon">📝</div><div class="wf-t">Output</div><div class="wf-v">Plaintext</div></div>
    </div>
    </body></html>
    """
    components.html(workflow_html, height=320, scrolling=False)


def render():
    """Render the Dual-Lock combined module page."""
    render_page_header(
        "🔐",
        "Dual-Lock Module",
        "Double-layer security: AES-256 encryption + Random LSB steganography.",
        accent="#d4af37",
    )

    _render_3d_workflow()
    st.markdown("---")

    enc_tab, dec_tab, report_tab = st.tabs([
        "🔐 Encrypt & Hide", "🔓 Extract & Decrypt", "📋 Security Report"
    ])

    with enc_tab:
        st.markdown("##### Step 1: Enter your secret message")
        dl_msg = st.text_area("Secret Message", height=100,
                               placeholder="Enter the message to protect...",
                               key="dl_msg")

        st.markdown("##### Step 2: Upload cover image & set password")
        c1, c2 = st.columns(2)
        with c1:
            dl_cover = st.file_uploader("Cover Image (PNG)", type=['png', 'jpg', 'jpeg'],
                                         key="dl_cover")
            if dl_cover:
                cover = _load_image(dl_cover)
                _show_image(cover, "Cover Image")

        with c2:
            dl_pwd = st.text_input("Password (used for both AES + LSB seed)",
                                    type="password", key="dl_pwd")
            st.caption("🔑 Satu password menghasilkan kunci AES (SHA-256) dan seed PRNG LSB.")

        if st.button("🔐 DUAL-LOCK ENCODE", type="primary",
                     use_container_width=True, key="dl_enc_btn"):
            if not dl_msg:
                st.error("Enter a secret message!")
            elif not dl_cover:
                st.error("Upload a cover image!")
            elif not dl_pwd:
                st.error("Password is required!")
            else:
                try:
                    with st.spinner("🔒 Layer 1: AES-256 Encrypting..."):
                        cover = _load_image(dl_cover)
                    with st.spinner("🕵️ Layer 2: LSB Random Embedding..."):
                        stego, ct, info = dual_lock_encode(cover, dl_msg, dl_pwd)

                    st.session_state['dl_original'] = cover
                    st.session_state['dl_stego'] = stego
                    st.session_state['dl_info'] = info

                    st.success("✅ Dual-Lock encoding complete!")
                    log_operation("Dual-Lock", "Encrypt & Hide", "success")

                    c1, c2 = st.columns(2)
                    with c1:
                        _show_image(cover, "Original")
                    with c2:
                        _show_image(stego, "Stego (secret hidden)")

                    metrics = get_all_metrics(cover, stego)
                    render_metrics_row(metrics)

                    with st.expander("🔤 View Intermediate Ciphertext"):
                        st.code(ct, language=None)

                    st.download_button(
                        "⬇️ Download Protected Image",
                        data=_image_to_bytes(stego),
                        file_name="mahesavault_duallock.png",
                        mime="image/png",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

    with dec_tab:
        st.markdown("##### Upload stego image & enter password")
        dl_stego_file = st.file_uploader("Stego Image (PNG)", type=['png'],
                                          key="dl_dec_file")
        if dl_stego_file:
            stego_dec = _load_image(dl_stego_file)
            _show_image(stego_dec, "Stego Image")

        dl_dec_pwd = st.text_input("Password", type="password", key="dl_dec_pwd")

        if st.button("🔓 DUAL-LOCK DECODE", type="primary",
                     use_container_width=True, key="dl_dec_btn"):
            if not dl_stego_file:
                st.error("Upload the stego image!")
            elif not dl_dec_pwd:
                st.error("Password is required!")
            else:
                try:
                    with st.spinner("🕵️ Layer 2: Extracting hidden data..."):
                        stego_dec = _load_image(dl_stego_file)
                    with st.spinner("🔓 Layer 1: AES-256 Decrypting..."):
                        plaintext, ct, info = dual_lock_decode(stego_dec, dl_dec_pwd)

                    st.success("✅ Dual-Lock decoding complete!")
                    log_operation("Dual-Lock", "Extract & Decrypt", "success")

                    render_glass_message_box("DECRYPTED MESSAGE", plaintext, "#10b981")
                    st.code(plaintext, language=None)

                    with st.expander("🔤 View Extracted Ciphertext"):
                        st.code(ct, language=None)
                except Exception as e:
                    st.error(f"❌ Decoding failed: {str(e)}")

    with report_tab:
        info = st.session_state.get('dl_info', None)
        report = generate_report(info)
        st.markdown(report)
