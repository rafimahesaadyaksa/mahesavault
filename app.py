"""
MahesaVault — The Dual-Protocol Secure Vault
Main entry point for the Streamlit application.

Run with: streamlit run app.py
"""

import os
import streamlit as st

# ─── PAGE CONFIG (must be first Streamlit call) ───
st.set_page_config(
    page_title="MahesaVault — Dual-Protocol Secure Vault",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── SESSION DEFAULTS ───
if "nav_page" not in st.session_state:
    st.session_state["nav_page"] = "🏠 Home"
if "mv_ops" not in st.session_state:
    st.session_state["mv_ops"] = []

PAGES = ["🏠 Home", "🕵️ Steganography", "🔒 Cryptography", "🔐 Dual-Lock", "🗄️ Secure Vault", "🧅 Onion Routing"]

# ─── LOAD CUSTOM CSS ───
css_path = os.path.join(os.path.dirname(__file__), "assets", "styles", "custom.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ─── SIDEBAR ───
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:18px 0 22px;">
        <div style="font-size:32px; margin-bottom:6px;">🔐</div>
        <div style="font-size:22px; font-weight:700;
                    font-family:'Cormorant Garamond',Georgia,serif;
                    background:linear-gradient(135deg, #00f5ff, #d4af37, #f472b6);
                    -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
            MahesaVault
        </div>
        <div style="font-size:9px; color:rgba(226,232,240,0.35);
                    font-family:'JetBrains Mono',monospace; letter-spacing:0.22em;
                    margin-top:6px;">
            CHAPTER: SECURE VAULT
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    default_idx = PAGES.index(st.session_state["nav_page"]) if st.session_state["nav_page"] in PAGES else 0
    page = st.radio(
        "Navigation",
        PAGES,
        index=default_idx,
        label_visibility="collapsed",
        key="sidebar_nav",
    )
    st.session_state["nav_page"] = page

    st.markdown("---")

    st.markdown("""
    <div style="padding:14px; background:rgba(20,28,46,0.6);
                border:1px solid rgba(255,255,255,0.06);
                border-radius:12px; backdrop-filter:blur(8px);">
        <div style="font-size:9px; color:rgba(226,232,240,0.4);
                    letter-spacing:0.15em; font-family:'JetBrains Mono',monospace;
                    margin-bottom:10px;">
            SYSTEM STATUS
        </div>
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
            <div style="width:6px; height:6px; border-radius:50%; background:#10b981;
                        box-shadow:0 0 8px #10b981;"></div>
            <span style="font-size:11px; color:#e2e8f0;">Encryption Engine</span>
        </div>
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
            <div style="width:6px; height:6px; border-radius:50%; background:#10b981;
                        box-shadow:0 0 8px #10b981;"></div>
            <span style="font-size:11px; color:#e2e8f0;">Stego Engine</span>
        </div>
        <div style="display:flex; align-items:center; gap:8px;">
            <div style="width:6px; height:6px; border-radius:50%; background:#d4af37;
                        box-shadow:0 0 8px #d4af37;"></div>
            <span style="font-size:11px; color:#e2e8f0;">Dual-Lock Ready</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-top:24px; font-size:9px; color:rgba(226,232,240,0.2);
                font-family:'JetBrains Mono',monospace; text-align:center;">
        MahesaVault v2.0 · 3D Edition
    </div>
    """, unsafe_allow_html=True)

# ─── PAGE ROUTING ───
if page == "🏠 Home":
    from ui.home import render
    render()
elif page == "🕵️ Steganography":
    from ui.stego_ui import render
    render()
elif page == "🔒 Cryptography":
    from ui.crypto_ui import render
    render()
elif page == "🔐 Dual-Lock":
    from ui.combined_ui import render
    render()
elif page == "🗄️ Secure Vault":
    from ui.vault_ui import render
    render()
elif page == "🧅 Onion Routing":
    from ui.onion_ui import render
    render()
