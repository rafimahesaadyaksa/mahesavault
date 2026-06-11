"""
Histogram Plot Component — MahesaVault
Reusable histogram comparison plot with proper figure cleanup.
"""

import matplotlib.pyplot as plt
import streamlit as st
from modules.steganography.steganalysis import rgb_histogram_comparison


def render_histogram(original, stego):
    """Render RGB histogram comparison chart in Streamlit."""
    fig = rgb_histogram_comparison(original, stego)
    st.pyplot(fig)
    plt.close(fig)
