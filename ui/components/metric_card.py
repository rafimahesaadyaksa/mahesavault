"""
Metric Card Component — MahesaVault
Reusable metric display for PSNR/MSE/SSIM values.
"""

import streamlit as st


def render_metric_card(label, value, unit="", description="", color="#00f5ff"):
    """Render a 3D glass metric card."""
    st.markdown(f"""
    <div class="mv-metric-3d">
        <div style="font-size:10px; color:rgba(226,232,240,0.5);
                    text-transform:uppercase; letter-spacing:0.12em;
                    font-family:'JetBrains Mono',monospace; margin-bottom:8px;">
            {label}
        </div>
        <div style="font-size:28px; color:{color}; font-weight:700;
                    font-family:'Cormorant Garamond',serif;">
            {value}{unit}
        </div>
        <div style="font-size:11px; color:rgba(226,232,240,0.4); margin-top:6px;">
            {description}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_metrics_row(metrics_dict):
    """Render PSNR, MSE, SSIM in a 3-column layout."""
    c1, c2, c3 = st.columns(3)
    with c1:
        psnr = metrics_dict['psnr']
        psnr_display = f"{psnr:.2f}" if psnr != float('inf') else "∞"
        status = "✅ Excellent" if psnr > 40 else "✅ Good" if psnr > 30 else "⚠️ Low"
        render_metric_card("PSNR", psnr_display, " dB", status, "#00f5ff")
    with c2:
        mse = metrics_dict['mse']
        render_metric_card("MSE", f"{mse:.6f}", "", "Lower = Better", "#f472b6")
    with c3:
        ssim = metrics_dict['ssim']
        render_metric_card("SSIM", f"{ssim:.6f}", "", "1.0 = Identical", "#10b981")
