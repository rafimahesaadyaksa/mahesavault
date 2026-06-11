"""
Home Page — MahesaVault Landing
3D cinematic experience (Millanova-inspired): depth, tilt cards, particles.
"""

import streamlit as st
import streamlit.components.v1 as components

from ui.components.theme_3d import (
    inject_particle_background,
    render_nav_launcher,
    render_operation_vault,
)


def _render_3d_protocol_cards():
    """Immersive 3D tilt + flip cards inside HTML component."""
    cards_html = """
    <!DOCTYPE html>
    <html><head>
    <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&family=JetBrains+Mono&display=swap" rel="stylesheet">
    <style>
      * { box-sizing: border-box; margin: 0; padding: 0; }
      body {
        background: transparent;
        font-family: 'Inter', sans-serif;
        color: #e8ecf4;
        overflow-x: hidden;
      }
      .mv-hero {
        text-align: center;
        padding: 8px 16px 28px;
      }
      .mv-hero-eyebrow {
        font-family: 'JetBrains Mono', monospace;
        font-size: 10px;
        letter-spacing: 0.4em;
        color: rgba(212,175,55,0.7);
        margin-bottom: 12px;
      }
      .mv-hero-title {
        font-family: 'Cormorant Garamond', serif;
        font-size: clamp(42px, 6vw, 64px);
        font-weight: 700;
        line-height: 1.05;
        background: linear-gradient(120deg, #fff 0%, #00f5ff 40%, #f472b6 85%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: mv-shimmer 8s ease-in-out infinite;
      }
      @keyframes mv-shimmer {
        0%,100% { filter: brightness(1); }
        50% { filter: brightness(1.15); }
      }
      .mv-hero-sub {
        margin-top: 12px;
        font-size: 14px;
        color: rgba(226,232,240,0.5);
        max-width: 520px;
        margin-left: auto;
        margin-right: auto;
        line-height: 1.6;
      }
      .cards-wrap {
        display: flex;
        justify-content: center;
        gap: 24px;
        flex-wrap: wrap;
        padding: 10px 12px 30px;
        perspective: var(--perspective, 1400px);
      }
      .card-scene {
        width: 300px;
        height: 420px;
        perspective: 1100px;
      }
      .card-3d {
        width: 100%;
        height: 100%;
        position: relative;
        transform-style: preserve-3d;
        transition: transform 0.75s cubic-bezier(0.23, 1, 0.32, 1);
        cursor: pointer;
        will-change: transform;
      }
      .card-scene:hover .card-3d,
      .card-3d.flipped { transform: rotateY(180deg); }
      .card-face {
        position: absolute;
        inset: 0;
        backface-visibility: hidden;
        -webkit-backface-visibility: hidden;
        border-radius: 18px;
        padding: 28px 24px;
        display: flex;
        flex-direction: column;
        align-items: center;
        overflow: hidden;
        background: linear-gradient(160deg, rgba(22,30,48,0.95), rgba(8,10,18,0.98));
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 30px 60px rgba(0,0,0,0.55),
                    inset 0 1px 0 rgba(255,255,255,0.08);
      }
      .card-front { transform: rotateY(0deg); }
      .card-back {
        transform: rotateY(180deg);
        align-items: flex-start;
      }
      .card-shine {
        position: absolute;
        inset: 0;
        background: linear-gradient(105deg, transparent 40%, rgba(255,255,255,0.04) 50%, transparent 60%);
        pointer-events: none;
        opacity: 0;
        transition: opacity 0.4s;
      }
      .card-scene:hover .card-shine { opacity: 1; }
      .card-glow {
        position: absolute;
        inset: -1px;
        border-radius: 18px;
        opacity: 0;
        transition: opacity 0.4s;
        pointer-events: none;
      }
      .stego .card-glow { box-shadow: 0 0 40px rgba(0,245,255,0.25); border: 1px solid rgba(0,245,255,0.35); }
      .crypto .card-glow { box-shadow: 0 0 40px rgba(244,114,182,0.25); border: 1px solid rgba(244,114,182,0.35); }
      .dual .card-glow { box-shadow: 0 0 40px rgba(212,175,55,0.2); border: 1px solid rgba(212,175,55,0.35); }
      .card-scene:hover .card-glow { opacity: 1; }
      .icon-wrap { position: relative; margin-bottom: 18px; }
      .icon-wrap svg { width: 64px; height: 64px; }
      .ping-ring {
        position: absolute; width: 80px; height: 80px;
        border-radius: 50%; border: 1px solid;
        top: 50%; left: 50%; transform: translate(-50%,-50%);
        animation: ping 2.2s ease-out infinite;
      }
      .stego .ping-ring { border-color: #00f5ff; }
      .crypto .ping-ring { border-color: #f472b6; }
      .dual .ping-ring { border-color: #d4af37; }
      @keyframes ping {
        0% { transform: translate(-50%,-50%) scale(0.85); opacity: 0.5; }
        100% { transform: translate(-50%,-50%) scale(1.5); opacity: 0; }
      }
      .card-title {
        font-family: 'Cormorant Garamond', serif;
        font-size: 28px;
        font-weight: 700;
        margin-bottom: 8px;
      }
      .stego .card-title { color: #00f5ff; }
      .crypto .card-title { color: #f472b6; }
      .dual .card-title { color: #d4af37; }
      .card-tagline {
        font-size: 12px;
        color: rgba(226,232,240,0.55);
        text-align: center;
        line-height: 1.55;
        margin-bottom: 16px;
      }
      .badge-row { display: flex; flex-wrap: wrap; gap: 6px; justify-content: center; }
      .badge {
        font-family: 'JetBrains Mono', monospace;
        font-size: 9px;
        padding: 4px 8px;
        border-radius: 4px;
      }
      .stego .badge { background: rgba(0,245,255,0.1); color: #00f5ff; border: 1px solid rgba(0,245,255,0.2); }
      .crypto .badge { background: rgba(244,114,182,0.1); color: #f472b6; border: 1px solid rgba(244,114,182,0.2); }
      .dual .badge { background: rgba(212,175,55,0.1); color: #d4af37; border: 1px solid rgba(212,175,55,0.2); }
      .card-hint {
        margin-top: auto;
        font-family: 'JetBrains Mono', monospace;
        font-size: 10px;
        color: rgba(226,232,240,0.25);
        letter-spacing: 0.08em;
      }
      .back-title {
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        letter-spacing: 0.2em;
        color: rgba(226,232,240,0.45);
        margin-bottom: 8px;
      }
      .card-divider { width: 100%; height: 1px; background: rgba(255,255,255,0.06); margin-bottom: 12px; }
      .feat-list { list-style: none; width: 100%; flex: 1; font-size: 11px; }
      .feat-list li {
        padding: 5px 0;
        border-bottom: 1px solid rgba(255,255,255,0.04);
        color: rgba(226,232,240,0.7);
        display: flex; gap: 8px;
      }
      .stego .chk { color: #00f5ff; }
      .crypto .chk { color: #f472b6; }
      .dual .chk { color: #d4af37; }
      .specs-row { display: flex; gap: 8px; width: 100%; margin-bottom: 12px; }
      .spec-box {
        flex: 1;
        text-align: center;
        padding: 8px 4px;
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 8px;
      }
      .spec-lbl { font-size: 8px; text-transform: uppercase; letter-spacing: 0.1em; color: rgba(226,232,240,0.4); }
      .spec-val { font-family: 'JetBrains Mono', monospace; font-size: 10px; margin-top: 4px; }
      .hex-ticker {
        width: 100%;
        overflow: hidden;
        border-top: 1px solid rgba(255,255,255,0.05);
        padding: 10px 0;
        font-family: 'JetBrains Mono', monospace;
        font-size: 10px;
        color: rgba(0,245,255,0.2);
      }
      .hex-inner { display: inline-block; white-space: nowrap; animation: ticker 28s linear infinite; }
      @keyframes ticker { 0% { transform: translateX(0); } 100% { transform: translateX(-50%); } }
      @media (max-width: 768px) {
        .card-scene { width: 92vw; max-width: 340px; }
        .card-scene:hover .card-3d { transform: none; }
        .card-3d.flipped { transform: rotateY(180deg); }
      }
    </style>
    </head><body>
    <div class="mv-hero">
      <div class="mv-hero-eyebrow">◆ CHAPTER: SECURE VAULT ◆</div>
      <h1 class="mv-hero-title">MahesaVault</h1>
      <p class="mv-hero-sub">Immersive dual-protocol environment — conceal with steganography, fortify with cryptography.</p>
    </div>

    <div class="cards-wrap">
      <div class="card-scene" data-tilt>
        <div class="card-3d stego" tabindex="0">
          <div class="card-face card-front">
            <div class="card-glow"></div><div class="card-shine"></div>
            <div class="icon-wrap">
              <svg viewBox="0 0 24 24" fill="none" stroke="#00f5ff" stroke-width="1.5">
                <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>
                <line x1="3" y1="3" x2="21" y2="21" stroke-width="2"/>
              </svg>
              <div class="ping-ring"></div>
            </div>
            <h2 class="card-title">Steganography</h2>
            <p class="card-tagline">Conceal existence within digital carriers — LSB spatial embedding.</p>
            <div class="badge-row">
              <span class="badge">LSB Sequential</span>
              <span class="badge">LSB Random</span>
              <span class="badge">XOR Layer</span>
            </div>
            <p class="card-hint">hover / tap to reveal →</p>
          </div>
          <div class="card-face card-back">
            <div class="card-glow"></div>
            <div class="back-title">STEGO PROTOCOL</div>
            <div class="card-divider"></div>
            <ul class="feat-list">
              <li><span class="chk">✓</span> Image Carrier Injection</li>
              <li><span class="chk">✓</span> PSNR / MSE / SSIM</li>
              <li><span class="chk">✓</span> Histogram Steganalysis</li>
              <li><span class="chk">✓</span> Bit-Plane Forensics</li>
            </ul>
            <div class="specs-row">
              <div class="spec-box"><span class="spec-lbl">Domain</span><span class="spec-val">Spatial</span></div>
              <div class="spec-box"><span class="spec-lbl">Format</span><span class="spec-val">PNG</span></div>
            </div>
          </div>
        </div>
      </div>

      <div class="card-scene" data-tilt>
        <div class="card-3d crypto" tabindex="0">
          <div class="card-face card-front">
            <div class="card-glow"></div><div class="card-shine"></div>
            <div class="icon-wrap">
              <svg viewBox="0 0 24 24" fill="none" stroke="#f472b6" stroke-width="1.5">
                <rect x="3" y="11" width="18" height="11" rx="2"/>
                <path d="M7 11V7a5 5 0 0 1 10 0v4"/><circle cx="12" cy="16" r="1"/>
              </svg>
              <div class="ping-ring"></div>
            </div>
            <h2 class="card-title">Cryptography</h2>
            <p class="card-tagline">Classical heritage meets modern military-grade encryption.</p>
            <div class="badge-row">
              <span class="badge">AES-256</span>
              <span class="badge">RSA-2048</span>
            </div>
            <p class="card-hint">hover / tap to reveal →</p>
          </div>
          <div class="card-face card-back">
            <div class="card-glow"></div>
            <div class="back-title">CRYPTO PROTOCOL</div>
            <div class="card-divider"></div>
            <ul class="feat-list">
              <li><span class="chk">✓</span> 3 Classical Ciphers</li>
              <li><span class="chk">✓</span> 2 Modern Algorithms</li>
              <li><span class="chk">✓</span> Digital Signature</li>
              <li><span class="chk">✓</span> Math Visualizer</li>
            </ul>
            <div class="specs-row">
              <div class="spec-box"><span class="spec-lbl">Key</span><span class="spec-val">256-bit</span></div>
              <div class="spec-box"><span class="spec-lbl">Hash</span><span class="spec-val">SHA-256</span></div>
            </div>
          </div>
        </div>
      </div>

      <div class="card-scene" data-tilt>
        <div class="card-3d dual" tabindex="0">
          <div class="card-face card-front">
            <div class="card-glow"></div><div class="card-shine"></div>
            <div class="icon-wrap">
              <svg viewBox="0 0 24 24" fill="none" stroke="#d4af37" stroke-width="1.5">
                <path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/>
                <path d="M2 12l10 5 10-5"/>
              </svg>
              <div class="ping-ring"></div>
            </div>
            <h2 class="card-title">Dual-Lock</h2>
            <p class="card-tagline">Flagship: AES-256 encrypt-then-hide in one password.</p>
            <div class="badge-row">
              <span class="badge">AES + LSB</span>
              <span class="badge">2 Layers</span>
            </div>
            <p class="card-hint">hover / tap to reveal →</p>
          </div>
          <div class="card-face card-back">
            <div class="card-glow"></div>
            <div class="back-title">DUAL-LOCK FLAGSHIP</div>
            <div class="card-divider"></div>
            <ul class="feat-list">
              <li><span class="chk">✓</span> Encrypt-then-Hide</li>
              <li><span class="chk">✓</span> Single Password Truth</li>
              <li><span class="chk">✓</span> Security Report</li>
              <li><span class="chk">✓</span> Beyond 2^256 resistance</li>
            </ul>
            <div class="specs-row">
              <div class="spec-box"><span class="spec-lbl">L1</span><span class="spec-val">AES</span></div>
              <div class="spec-box"><span class="spec-lbl">L2</span><span class="spec-val">LSB</span></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="hex-ticker">
      <div class="hex-inner">
        4d 61 68 65 73 61 56 61 75 6c 74 — Secure Protocol — AES-256 | LSB Random | Dual-Lock Active &nbsp;&nbsp;&nbsp;
        4d 61 68 65 73 61 56 61 75 6c 74 — Secure Protocol — AES-256 | LSB Random | Dual-Lock Active &nbsp;&nbsp;&nbsp;
      </div>
    </div>

    <script>
    document.querySelectorAll('.card-scene').forEach(scene => {
      const card = scene.querySelector('.card-3d');
      scene.addEventListener('mousemove', e => {
        const r = scene.getBoundingClientRect();
        const x = (e.clientX - r.left) / r.width - 0.5;
        const y = (e.clientY - r.top) / r.height - 0.5;
        const flip = card.classList.contains('flipped') || scene.matches(':hover');
        if (!flip) card.style.transform = `rotateY(${x*8}deg) rotateX(${-y*8}deg)`;
      });
      scene.addEventListener('mouseleave', () => {
        if (!card.classList.contains('flipped')) card.style.transform = '';
      });
      card.addEventListener('click', () => {
        if (window.matchMedia('(max-width:768px)').matches) {
          card.classList.toggle('flipped');
        }
      });
    });
    </script>
    </body></html>
    """
    components.html(cards_html, height=720, scrolling=False)


def _run_quick_demo():
    """One-click pipeline demo for visitors."""
    import numpy as np
    from modules.combined.dual_lock import dual_lock_encode, dual_lock_decode

    with st.spinner("Menjalankan demo Dual-Lock..."):
        img = np.random.randint(0, 256, (120, 120, 3), dtype=np.uint8)
        msg = "MahesaVault Demo OK"
        pwd = "demo2025"
        stego, _, _ = dual_lock_encode(img.copy(), msg, pwd)
        plain, _, _ = dual_lock_decode(stego, pwd)
    ok = plain == msg
    if ok:
        st.success("Demo berhasil — pipeline encrypt → hide → extract → decrypt valid.")
        from ui.components.theme_3d import log_operation
        log_operation("Dual-Lock", "Quick Demo", "success")
    else:
        st.error("Demo gagal — hubungi developer.")


def render():
    """Render cinematic home with 3D cards and working navigation."""
    inject_particle_background()

    _render_3d_protocol_cards()

    st.markdown("---")
    render_nav_launcher()

    st.markdown("---")
    col_a, col_b = st.columns([1, 1])

    with col_a:
        st.markdown("##### ⚡ Quick Demo")
        st.caption("Uji pipeline Dual-Lock tanpa upload gambar.")
        if st.button("Jalankan Demo Pipeline", use_container_width=True, key="home_demo"):
            _run_quick_demo()

    with col_b:
        st.markdown("##### 📜 Operation Vault")
        render_operation_vault()

    # Feature highlights
    st.markdown("---")
    st.markdown("""
    <div style="display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:16px; margin-top:8px;">
      <div class="mv-metric-3d" style="--accent:#00f5ff;">
        <div style="font-size:10px; letter-spacing:0.15em; color:rgba(226,232,240,0.45); font-family:monospace;">STEGO</div>
        <div style="font-size:22px; color:#00f5ff; font-family:serif; margin:8px 0;">LSB + XOR</div>
        <div style="font-size:11px; color:rgba(226,232,240,0.5);">PSNR &gt; 50 dB typical</div>
      </div>
      <div class="mv-metric-3d">
        <div style="font-size:10px; letter-spacing:0.15em; color:rgba(226,232,240,0.45); font-family:monospace;">CRYPTO</div>
        <div style="font-size:22px; color:#f472b6; font-family:serif; margin:8px 0;">5 Ciphers</div>
        <div style="font-size:11px; color:rgba(226,232,240,0.5);">3 Classical + 2 Modern</div>
      </div>
      <div class="mv-metric-3d">
        <div style="font-size:10px; letter-spacing:0.15em; color:rgba(226,232,240,0.45); font-family:monospace;">DUAL-LOCK</div>
        <div style="font-size:22px; color:#d4af37; font-family:serif; margin:8px 0;">2^256+</div>
        <div style="font-size:11px; color:rgba(226,232,240,0.5);">Combined key resistance</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
