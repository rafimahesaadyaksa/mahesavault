"""
Steganography UI Page — MahesaVault
Three tabs: Encoder, Decoder, Analysis & Steganalysis.
"""

import streamlit as st
import numpy as np
import cv2
from PIL import Image
from io import BytesIO

from modules.steganography.lsb_sequential import embed_sequential, extract_sequential
from modules.steganography.lsb_random import embed_random, extract_random
from modules.steganography.bruteforce_extract import bruteforce_extract
from modules.steganography.quality_metrics import get_all_metrics
from modules.steganography.capacity import calculate_capacity
from modules.steganography.steganalysis import (
    rgb_histogram_comparison, bit_plane_figure, error_map_figure,
    chi_square_figure
)
from modules.steganography.ai_detector import detect_steganography
import matplotlib.pyplot as plt

from ui.components.metric_card import render_metrics_row
from ui.components.theme_3d import (
    render_page_header,
    render_glass_message_box,
    log_operation,
)


def _load_image(uploaded_file):
    """Load uploaded file as numpy array (BGR for OpenCV)."""
    img = Image.open(uploaded_file).convert('RGB')
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)


def _image_to_bytes(img_array):
    """Convert numpy array to PNG bytes for download."""
    img_rgb = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(img_rgb)
    buf = BytesIO()
    pil_img.save(buf, format='PNG')
    return buf.getvalue()


def _show_image(img_array, caption=""):
    """Display OpenCV BGR image in Streamlit."""
    rgb = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)
    st.image(rgb, caption=caption, use_container_width=True)


def render():
    """Render the Steganography module page."""
    render_page_header(
        "🕵️",
        "Steganography Module",
        "Embed secret messages within images using LSB steganography.",
        accent="#00f5ff",
    )

    tab1, tab2, tab3 = st.tabs(["🔒 Encoder (Embed)", "🔓 Decoder (Extract)",
                                 "📊 Analysis & Steganalysis"])

    # ─── TAB 1: ENCODER ───
    with tab1:
        col_upload, col_config = st.columns([1, 1])

        with col_upload:
            st.markdown("##### 📤 Cover Media")
            media_type = st.radio("Media Type", ["Image (PNG/JPG)", "Audio (WAV)", "Video (AVI)"], key="stego_media_type")
            
            if media_type == "Image (PNG/JPG)":
                cover_file = st.file_uploader(
                    "Upload PNG cover image", type=['png', 'jpg', 'jpeg'],
                    key="stego_cover"
                )
                if cover_file:
                    cover_img = _load_image(cover_file)
                    _show_image(cover_img, "Cover Image")
                    cap = calculate_capacity(cover_img)
                    st.info(
                        f"📐 {cap['width']}×{cap['height']} | "
                        f"{cap['channels']}ch | "
                        f"Max: **{cap['max_chars']:,}** characters"
                    )
            elif media_type == "Audio (WAV)":
                cover_file = st.file_uploader(
                    "Upload WAV audio file", type=['wav'],
                    key="stego_cover_audio"
                )
                if cover_file:
                    st.audio(cover_file)
                    st.info("🎵 Audio file loaded successfully.")
            else:
                cover_file = st.file_uploader(
                    "Upload Video file", type=['avi', 'mp4', 'mkv'],
                    key="stego_cover_video"
                )
                if cover_file:
                    st.video(cover_file)
                    st.info("🎥 Video file loaded successfully. Note: Output will be converted to .AVI to preserve LSB data losslessly.")

        with col_config:
            st.markdown("##### ⚙️ Configuration")
            payload_type = st.radio("Payload Type", ["Text", "File"], horizontal=True, key="stego_payload_type")
            
            if payload_type == "Text":
                secret_msg = st.text_area("Secret Message", height=120,
                                           placeholder="Enter your secret message here...",
                                           key="stego_msg")
                secret_file = None
            else:
                secret_file = st.file_uploader("Secret File to Hide", key="stego_secret_file")
                secret_msg = None
                
            stego_key = st.text_input("Password / Key", type="password",
                                       key="stego_key")
                                       
            if media_type == "Image (PNG/JPG)":
                method = st.selectbox("LSB Method",
                                       ["Sequential LSB", "Random LSB"],
                                       key="stego_method")
            elif media_type == "Audio (WAV)":
                method = "Audio LSB"
                st.info("Audio Steganography uses Sequential LSB.")
            else:
                method = "Video LSB"
                st.info("Video Steganography uses Frame-Level LSB.")
                
            use_xor = st.checkbox("Use XOR pre-encryption", key="stego_xor")

            if st.button("🔐 Generate Stego Media", type="primary",
                         use_container_width=True, key="stego_gen"):
                if not cover_file:
                    st.error(f"Please upload a cover {media_type.split(' ')[0].lower()} first!")
                elif payload_type == "Text" and not secret_msg:
                    st.error("Please enter a secret message!")
                elif payload_type == "File" and not secret_file:
                    st.error("Please upload a secret file to hide!")
                elif (method == "Random LSB" or use_xor) and not stego_key:
                    st.error("Key is required for Random LSB / XOR encryption!")
                elif method == "Sequential LSB" and stego_key and not use_xor:
                    st.error("⚠️ Anda memasukkan Password, tetapi tidak mencentang 'Use XOR pre-encryption'. Silakan centang kotak tersebut agar password berfungsi!")
                else:
                    try:
                        with st.spinner("Embedding secret data..."):
                            from modules.steganography.lsb_sequential import embed_file_sequential
                            from modules.steganography.lsb_random import embed_file_random
                            from modules.steganography.audio_stego import embed_audio, embed_file_audio
                            from modules.steganography.video_stego import embed_video, embed_file_video
                            import tempfile
                            import os
                            
                            if media_type == "Image (PNG/JPG)":
                                cover_img = _load_image(cover_file)
                                if method == "Sequential LSB":
                                    if payload_type == "Text":
                                        stego = embed_sequential(cover_img, secret_msg, stego_key, use_xor)
                                    else:
                                        stego = embed_file_sequential(cover_img, secret_file.name, secret_file.getvalue(), stego_key, use_xor)
                                else:
                                    if payload_type == "Text":
                                        stego = embed_random(cover_img, secret_msg, stego_key, use_xor)
                                    else:
                                        stego = embed_file_random(cover_img, secret_file.name, secret_file.getvalue(), stego_key, use_xor)
    
                                # Store in session state for analysis tab
                                st.session_state['original_img'] = cover_img
                                st.session_state['stego_img'] = stego
                                
                                st.success("✅ Message embedded successfully!")
                                log_operation("Steganography", f"Embed ({method})", "success")
        
                                # Show stego image
                                _show_image(stego, "Stego Image (message hidden)")
        
                                # Quality metrics
                                metrics = get_all_metrics(cover_img, stego)
                                st.session_state['stego_metrics'] = metrics
                                render_metrics_row(metrics)
        
                                # Download button
                                stego_bytes = _image_to_bytes(stego)
                                st.download_button(
                                    "⬇️ Download Stego Image",
                                    data=stego_bytes,
                                    file_name="mahesavault_stego.png",
                                    mime="image/png",
                                    use_container_width=True
                                )
                            elif media_type == "Audio (WAV)":
                                # Audio Steganography
                                wav_bytes = cover_file.getvalue()
                                if payload_type == "Text":
                                    stego_audio_bytes = embed_audio(wav_bytes, secret_msg, stego_key, use_xor)
                                else:
                                    stego_audio_bytes = embed_file_audio(wav_bytes, secret_file.name, secret_file.getvalue(), stego_key, use_xor)
                                
                                st.success("✅ Audio embedded successfully!")
                                log_operation("Steganography", "Embed Audio LSB", "success")
                                
                                st.audio(stego_audio_bytes, format='audio/wav')
                                
                                st.download_button(
                                    "⬇️ Download Stego Audio",
                                    data=stego_audio_bytes,
                                    file_name="mahesavault_stego.wav",
                                    mime="audio/wav",
                                    use_container_width=True
                                )
                            else:
                                # Video Steganography
                                ext = os.path.splitext(cover_file.name)[1].lower()
                                temp_in = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
                                temp_in.write(cover_file.getvalue())
                                temp_in.close()
                                
                                temp_out = tempfile.mktemp(suffix=".avi")
                                
                                if payload_type == "Text":
                                    out_path = embed_video(temp_in.name, secret_msg, temp_out, stego_key, use_xor)
                                else:
                                    out_path = embed_file_video(temp_in.name, secret_file.name, secret_file.getvalue(), temp_out, stego_key, use_xor)
                                    
                                st.success("✅ Video embedded successfully!")
                                log_operation("Steganography", "Embed Video LSB", "success")
                                
                                with open(out_path, 'rb') as f:
                                    stego_video_bytes = f.read()
                                    
                                st.video(stego_video_bytes, format='video/avi')
                                st.download_button(
                                    "⬇️ Download Stego Video",
                                    data=stego_video_bytes,
                                    file_name="mahesavault_stego.avi",
                                    mime="video/avi",
                                    use_container_width=True
                                )
                                
                                os.unlink(temp_in.name)
                                os.unlink(out_path)
                                
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

    # ─── TAB 2: DECODER ───
    with tab2:
        st.markdown("##### 📥 Extract Hidden Message")

        stego_file = st.file_uploader(
            "Upload stego media (PNG / WAV / AVI / MP4 / MKV)", type=['png', 'wav', 'avi', 'mp4', 'mkv'],
            key="stego_decode_file"
        )

        if stego_file:
            ext = stego_file.name.lower().split('.')[-1]
            if ext == 'wav':
                st.audio(stego_file)
            elif ext in ['avi', 'mp4', 'mkv']:
                st.video(stego_file)
            else:
                stego_img = _load_image(stego_file)
                _show_image(stego_img, "Stego Image")

        # ─── SECTION A: Manual Extraction (known method) ───
        st.markdown("---")
        st.markdown("""
        <div style="padding:10px 16px; background:rgba(0,245,255,0.06);
                    border-left:3px solid #00f5ff; border-radius:0 8px 8px 0;
                    margin-bottom:16px;">
            <span style="font-size:13px; font-weight:600; color:#00f5ff;
                         font-family:'JetBrains Mono',monospace;">
                🔑 MANUAL EXTRACTION — Known Method & Key
            </span>
            <br>
            <span style="font-size:11px; color:rgba(226,232,240,0.6);">
                Use this if you know the exact method, key, and XOR setting
                used during embedding.
            </span>
        </div>
        """, unsafe_allow_html=True)

        dec_key = st.text_input("Password / Key", type="password",
                                 key="stego_dec_key")
        dec_method = st.selectbox("LSB Method used during embedding",
                                   ["Sequential LSB", "Random LSB", "Audio LSB (WAV)", "Video LSB (AVI)"],
                                   key="stego_dec_method")
        dec_xor = st.checkbox("XOR was used during embedding",
                               key="stego_dec_xor")

        if st.button("🔓 Extract Message / File", type="primary",
                     use_container_width=True, key="stego_extract"):
            if not stego_file:
                st.error("Please upload stego media!")
            elif (dec_method == "Random LSB" or dec_xor) and not dec_key:
                st.error("Key is required!")
            else:
                try:
                    with st.spinner("Extracting hidden data..."):
                        if stego_file.name.lower().endswith('.wav'):
                            from modules.steganography.audio_stego import extract_audio
                            msg = extract_audio(stego_file.getvalue(), dec_key, dec_xor)
                        elif stego_file.name.lower().endswith(('.avi', '.mp4', '.mkv')) or dec_method == "Video LSB (AVI)":
                            from modules.steganography.video_stego import extract_video
                            import tempfile
                            import os
                            ext = os.path.splitext(stego_file.name)[1].lower()
                            temp_in = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
                            temp_in.write(stego_file.getvalue())
                            temp_in.close()
                            msg = extract_video(temp_in.name, dec_key, dec_xor)
                            os.unlink(temp_in.name)
                        else:
                            stego_img = _load_image(stego_file)
                            if dec_method == "Sequential LSB":
                                msg = extract_sequential(stego_img, dec_key, dec_xor)
                            else:
                                msg = extract_random(stego_img, dec_key, dec_xor)

                    st.success("✅ Extraction successful!")
                    log_operation("Steganography", f"Extract ({dec_method})", "success")
                    
                    # Auto-detect if it's a file payload
                    import base64
                    is_file = False
                    if '|' in msg:
                        filename, potential_b64 = msg.split('|', 1)
                        if len(potential_b64) > 0 and len(potential_b64) % 4 == 0:
                            try:
                                file_bytes = base64.b64decode(potential_b64)
                                is_file = True
                            except:
                                pass
                                
                    if is_file:
                        render_glass_message_box("EXTRACTED FILE", f"Filename: {filename}\nSize: {len(file_bytes)} bytes", "#f472b6")
                        st.download_button(
                            "⬇️ Download Hidden File",
                            data=file_bytes,
                            file_name=filename,
                            use_container_width=True
                        )
                    else:
                        render_glass_message_box("EXTRACTED MESSAGE", msg, "#00f5ff")
                        st.code(msg, language=None)
                except Exception as e:
                    st.error(f"❌ Extraction failed: {str(e)}")

        # ─── SECTION B: Automated Brute-Force / Heuristic Extraction ───
        st.markdown("---")
        st.markdown("""
        <div style="padding:14px 18px; background:linear-gradient(135deg,
                    rgba(212,175,55,0.08), rgba(244,114,182,0.06));
                    border-left:3px solid #d4af37; border-radius:0 10px 10px 0;
                    margin-bottom:16px;">
            <span style="font-size:14px; font-weight:700; color:#d4af37;
                         font-family:'JetBrains Mono',monospace;">
                🔬 AUTOMATED BRUTE-FORCE EXTRACTION
            </span>
            <br>
            <span style="font-size:11px; color:rgba(226,232,240,0.65);
                         line-height:1.6;">
                Heuristic extraction for images from <b>any steganography tool</b>.
                Tries all combinations of channel order (RGB/BGR/etc.), bit position
                (LSB/MSB), pixel traversal (row/column), embedding mode
                (interleaved/per-channel), bit ordering (MSB-first/LSB-first),
                and multiple EOF strategies — <b>tanpa password & tanpa XOR</b>.
            </span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="padding:8px 14px; background:rgba(239,68,68,0.06);
                    border:1px solid rgba(239,68,68,0.15); border-radius:8px;
                    margin-bottom:12px;">
            <span style="font-size:10px; color:rgba(239,68,68,0.8);
                         font-family:'JetBrains Mono',monospace;">
                ⚠️ CATATAN: Hanya mendukung LSB & MSB tanpa password/XOR.
                Gambar terenkripsi (Random LSB + key) tidak bisa di-bruteforce.
            </span>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🔬 Brute-Force Extract (Universal — No Key)",
                     use_container_width=True, key="stego_brute_extract",
                     type="secondary"):
            if not stego_file:
                st.error("Please upload a stego image!")
            else:
                stego_img = _load_image(stego_file)
                progress_bar = st.progress(0, text="Scanning combinations...")

                def update_progress(current, total):
                    pct = min(current / total, 1.0)
                    progress_bar.progress(
                        pct,
                        text=f"Scanning... {current}/{total} combinations "
                             f"({pct*100:.0f}%)"
                    )

                try:
                    result = bruteforce_extract(
                        stego_img,
                        progress_callback=update_progress,
                    )
                    progress_bar.progress(1.0, text="Scan complete!")

                    if result['success']:
                        st.success(
                            f"✅ Pesan berhasil diekstrak! "
                            f"({result['attempts']} kombinasi dicoba, "
                            f"{len(result['results'])} hasil ditemukan)"
                        )
                        log_operation("Steganography",
                                      "Brute-force Extract", "success")

                        # ─── Show winning method details ───
                        st.markdown("""
                        <div style="padding:12px 16px;
                                    background:rgba(16,185,129,0.08);
                                    border:1px solid rgba(16,185,129,0.2);
                                    border-radius:10px; margin:8px 0 16px;">
                            <div style="font-size:10px; color:rgba(16,185,129,0.7);
                                        letter-spacing:0.1em;
                                        font-family:'JetBrains Mono',monospace;
                                        margin-bottom:8px;">
                                🎯 METODE YANG BERHASIL
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        st.code(result['method'], language=None)

                        # ─── Show extracted message / file ───
                        import base64
                        is_file = False
                        if '|' in result['message']:
                            filename, potential_b64 = result['message'].split('|', 1)
                            if len(potential_b64) > 0 and len(potential_b64) % 4 == 0:
                                try:
                                    file_bytes = base64.b64decode(potential_b64)
                                    is_file = True
                                except:
                                    pass
                        
                        if is_file:
                            render_glass_message_box("EXTRACTED FILE (Brute-force)", f"Filename: {filename}\nSize: {len(file_bytes)} bytes", "#f472b6")
                            st.download_button(
                                "⬇️ Download Hidden File",
                                data=file_bytes,
                                file_name=filename,
                                use_container_width=True,
                                key="stego_brute_download"
                            )
                        else:
                            render_glass_message_box(
                                "EXTRACTED MESSAGE (Brute-force)",
                                result['message'], "#d4af37"
                            )
                            st.code(result['message'], language=None)

                        # ─── If multiple results found, show alternatives ───
                        if len(result['results']) > 1:
                            with st.expander(
                                f"📋 Semua hasil ({len(result['results'])} "
                                f"pesan ditemukan)", expanded=False
                            ):
                                for i, r in enumerate(result['results']):
                                    st.markdown(f"**Hasil #{i+1}**")
                                    st.caption(r['method'])
                                    st.code(r['message'], language=None)
                                    st.markdown("---")

                    else:
                        st.error(
                            f"❌ Tidak ditemukan pesan tersembunyi setelah "
                            f"mencoba {result['attempts']} kombinasi.\n\n"
                            f"Kemungkinan penyebab:\n"
                            f"- Gambar menggunakan password/key (Random LSB)\n"
                            f"- Gambar menggunakan XOR encryption\n"
                            f"- Gambar tidak mengandung pesan steganografi\n"
                            f"- Metode steganografi yang digunakan tidak "
                            f"didukung (bukan LSB/MSB)"
                        )
                        log_operation("Steganography",
                                      "Brute-force Extract", "failed")

                except Exception as e:
                    progress_bar.empty()
                    st.error(f"❌ Brute-force extraction error: {str(e)}")

    # ─── TAB 3: ANALYSIS ───
    with tab3:
        st.markdown("##### 📊 Steganalysis & Visual Forensics")
        
        analysis_mode = st.radio("Analysis Mode", ["Analyze Arbitrary Image", "Compare Generated Stego (Encoder)"], horizontal=True)
        
        target_img = None
        original_img = None
        
        if analysis_mode == "Analyze Arbitrary Image":
            st.info("Upload any PNG/JPG image to analyze it for hidden steganography.")
            upload_target = st.file_uploader("Upload Image for Steganalysis", type=['png', 'jpg', 'jpeg'], key="steganalysis_upload")
            if upload_target:
                target_img = _load_image(upload_target)
                _show_image(target_img, "Image to Analyze")
        else:
            if 'original_img' not in st.session_state or 'stego_img' not in st.session_state:
                st.warning("⚠️ Generate a stego image in the Encoder tab first to see comparison analysis.")
            else:
                original_img = st.session_state['original_img']
                target_img = st.session_state['stego_img']
                
                # Side-by-side comparison
                st.markdown("**Original vs Stego Image**")
                c1, c2 = st.columns(2)
                with c1:
                    _show_image(original_img, "Original")
                with c2:
                    _show_image(target_img, "Stego")
        
                # Metrics
                if 'stego_metrics' in st.session_state:
                    render_metrics_row(st.session_state['stego_metrics'])
                    
                st.markdown("---")
        
                # RGB Histogram
                st.markdown("**RGB Histogram Comparison**")
                fig_hist = rgb_histogram_comparison(original_img, target_img)
                st.pyplot(fig_hist)
                plt.close(fig_hist)
        
                st.markdown("---")
        
                # Error Map
                st.markdown("**Error Map — Pixel Modifications**")
                fig_err = error_map_figure(original_img, target_img)
                st.pyplot(fig_err)
                plt.close(fig_err)

        if target_img is not None:
            st.markdown("---")
            st.markdown("### Single Image Analysis")

            # AI-Powered Detector
            st.markdown("**🤖 AI-Powered Steganalysis Detector**")
            st.markdown("*Uses a heuristic ensemble (Chi-Square, Entropy, SPA, etc.) to detect hidden data with high accuracy.*")
            
            if st.button("Run AI Detection on Image", type="primary"):
                with st.spinner("Analyzing image features..."):
                    report = detect_steganography(target_img)
                    
                    if report['prediction'] == "STEGO":
                        st.error(f"🚨 **STEGANOGRAPHY DETECTED!** Confidence: {report['confidence']:.1f}%")
                    elif report['prediction'] == "SUSPICIOUS":
                        st.warning(f"⚠️ **SUSPICIOUS IMAGE.** Confidence: {report['confidence']:.1f}%")
                    else:
                        st.success(f"✅ **CLEAN IMAGE.** Confidence: {report['confidence']:.1f}%")
                    
                    # Show breakdown
                    with st.expander("View Detection Heuristics Breakdown"):
                        for key, val in report['indicators'].items():
                            st.markdown(f"- **{key}**: {val['detail']} (Score: {val['score']:.2f})")
                            
            st.markdown("---")

            # Bit-Plane Visualization
            st.markdown("**Bit-Plane Visualization**")
            fig_bp = bit_plane_figure(target_img)
            st.pyplot(fig_bp)
            plt.close(fig_bp)
    
            st.markdown("---")
    
            # Chi-Square Attack
            st.markdown("**Chi-Square Steganalysis Attack**")
            st.markdown("*A statistical attack to detect LSB steganography based on PoV frequency analysis.*")
            fig_chi = chi_square_figure(target_img)
            st.pyplot(fig_chi)
            plt.close(fig_chi)

        st.markdown("---")

        # Comparison table
        st.markdown("**Sequential vs Random LSB Comparison**")
        st.markdown("""
| Parameter | Sequential LSB | Random LSB |
|-----------|---------------|------------|
| Visibility | Imperceptible | Imperceptible |
| PSNR | ~50 dB | ~52 dB |
| Security | Low (no key needed) | High (key-dependent seed) |
| Change Distribution | Concentrated at image start | Distributed across image |
| Steganalysis Resistance | Weak | Strong |
        """)
