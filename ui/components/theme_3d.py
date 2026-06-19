"""
3D Cinematic Theme — MahesaVault
Inspired by Millanova Chapter: elegant depth, glass panels, particle ambience.
"""

from __future__ import annotations

import html
import streamlit as st
import streamlit.components.v1 as components

NAV_PAGES = {
    "stego": "🕵️ Steganography",
    "crypto": "🔒 Cryptography",
    "dual": "🔐 Dual-Lock",
}


def escape_text(value: str) -> str:
    """Escape user content for safe HTML injection."""
    return html.escape(str(value), quote=True)


def inject_particle_background(height: int = 0):
    """
    Fixed Three.js particle field — Millanova-style ambient depth.
    height=0 → minimal spacer (particles are position:fixed in iframe).
    """
    particle_html = """
    <!DOCTYPE html>
    <html><head>
    <style>
      * { margin:0; padding:0; box-sizing:border-box; }
      html, body { width:100%; height:100%; overflow:hidden; background:transparent; }
      #c { position:fixed; inset:0; width:100%; height:100%; pointer-events:none; }
    </style>
    </head><body>
    <canvas id="c"></canvas>
    <script>
    (function(){
      const canvas = document.getElementById('c');
      const ctx = canvas.getContext('2d');
      let w, h, particles = [];
      const colors = ['rgba(0,245,255,', 'rgba(244,114,182,', 'rgba(212,175,55,'];
      function resize(){
        w = canvas.width = window.innerWidth;
        h = canvas.height = window.innerHeight;
      }
      function init(){
        resize();
        particles = [];
        const n = Math.min(120, Math.floor((w*h)/12000));
        for(let i=0;i<n;i++){
          particles.push({
            x: Math.random()*w, y: Math.random()*h,
            z: Math.random()*1.5+0.2,
            vx: (Math.random()-0.5)*0.25,
            vy: (Math.random()-0.5)*0.25,
            c: colors[i%3]
          });
        }
      }
      function draw(){
        ctx.clearRect(0,0,w,h);
        for(let i=0;i<particles.length;i++){
          const p = particles[i];
          p.x += p.vx * p.z; p.y += p.vy * p.z;
          if(p.x<0) p.x=w; if(p.x>w) p.x=0;
          if(p.y<0) p.y=h; if(p.y>h) p.y=0;
          const s = 1.2 * p.z;
          ctx.beginPath();
          ctx.arc(p.x, p.y, s, 0, Math.PI*2);
          ctx.fillStyle = p.c + (0.15 + p.z*0.12) + ')';
          ctx.fill();
          for(let j=i+1;j<particles.length;j++){
            const q = particles[j];
            const dx=p.x-q.x, dy=p.y-q.y;
            const dist = Math.sqrt(dx*dx+dy*dy);
            if(dist < 100){
              ctx.strokeStyle = 'rgba(226,232,240,' + (0.03*(1-dist/100)) + ')';
              ctx.lineWidth = 0.5;
              ctx.beginPath();
              ctx.moveTo(p.x,p.y); ctx.lineTo(q.x,q.y);
              ctx.stroke();
            }
          }
        }
        requestAnimationFrame(draw);
      }
      window.addEventListener('resize', init);
      init(); draw();
    })();
    </script>
    </body></html>
    """
    components.html(particle_html, height=height or 1, scrolling=False)


def render_page_header(icon: str, title: str, subtitle: str, accent: str = "#00f5ff"):
    """Cinematic module header with glass depth."""
    st.markdown(f"""
    <div class="mv-page-hero" style="--accent:{accent};">
        <div class="mv-page-hero-glow"></div>
        <div class="mv-page-eyebrow">◆ PROTOCOL ACTIVE ◆</div>
        <h2 class="mv-page-title">{icon} {escape_text(title)}</h2>
        <p class="mv-page-sub">{escape_text(subtitle)}</p>
    </div>
    """, unsafe_allow_html=True)


def render_glass_message_box(label: str, content: str, accent: str = "#00f5ff"):
    """Safe glass panel for extracted/decrypted text."""
    safe = escape_text(content)
    st.markdown(f"""
    <div class="mv-glass-box" style="--accent:{accent};">
        <div class="mv-glass-label">{escape_text(label)}</div>
        <div class="mv-glass-content">{safe}</div>
    </div>
    """, unsafe_allow_html=True)


def set_nav(page_key: str):
    """Navigate via session state (Streamlit-native)."""
    if page_key in NAV_PAGES:
        st.session_state["nav_page"] = NAV_PAGES[page_key]
        st.session_state["nav_from_home"] = True


def render_nav_launcher():
    """Quick-launch buttons that work inside Streamlit."""
    st.markdown('<div class="mv-launcher-label">Pilih protokol operasi</div>',
                unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🕵️ Steganography", use_container_width=True, key="nav_stego"):
            set_nav("stego")
            st.rerun()
    with c2:
        if st.button("🔒 Cryptography", use_container_width=True, key="nav_crypto"):
            set_nav("crypto")
            st.rerun()
    with c3:
        if st.button("🔐 Dual-Lock", use_container_width=True, key="nav_dual"):
            set_nav("dual")
            st.rerun()


def log_operation(module: str, action: str, status: str = "success"):
    """Append to session operation vault."""
    if "mv_ops" not in st.session_state:
        st.session_state["mv_ops"] = []
    st.session_state["mv_ops"].insert(0, {
        "module": module,
        "action": action,
        "status": status,
    })
    st.session_state["mv_ops"] = st.session_state["mv_ops"][:12]


def render_operation_vault():
    """Show recent operations in a glass timeline."""
    ops = st.session_state.get("mv_ops", [])
    if not ops:
        st.caption("Belum ada operasi — jalankan encode/encrypt untuk melihat riwayat.")
        return
    rows = ""
    for op in ops[:6]:
        color = "#10b981" if op["status"] == "success" else "#ef4444"
        rows += f"""
        <div class="mv-op-row">
            <span class="mv-op-dot" style="background:{color};"></span>
            <span class="mv-op-mod">{escape_text(op['module'])}</span>
            <span class="mv-op-act">{escape_text(op['action'])}</span>
        </div>"""
    st.markdown(f'<div class="mv-op-vault">{rows}</div>', unsafe_allow_html=True)
