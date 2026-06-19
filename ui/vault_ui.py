"""
Secure Vault UI — MahesaVault
Allows users to login, save, and retrieve encrypted messages.
"""

import streamlit as st
from modules.database.db_manager import create_user, authenticate_user, save_vault_item, get_vault_items, delete_vault_item
from ui.components.theme_3d import render_page_header, render_glass_message_box

def render():
    render_page_header(
        "🗄️ Secure Vault",
        "Encrypted Cloud Database",
        "Store and retrieve your encrypted files and messages securely."
    )
    
    # Initialize session state for auth
    if 'user_id' not in st.session_state:
        st.session_state['user_id'] = None
    if 'username' not in st.session_state:
        st.session_state['username'] = None
        
    if st.session_state['user_id'] is None:
        _render_auth()
    else:
        _render_dashboard()

def _render_auth():
    st.markdown("### Authentication Required")
    
    tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                if username and password:
                    user_id = authenticate_user(username, password)
                    if user_id:
                        st.session_state['user_id'] = user_id
                        st.session_state['username'] = username
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")
                else:
                    st.warning("Please enter both username and password.")
                    
    with tab2:
        with st.form("register_form"):
            new_username = st.text_input("Choose Username")
            new_password = st.text_input("Choose Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            register = st.form_submit_button("Create Account")
            
            if register:
                if new_username and new_password:
                    if new_password == confirm_password:
                        if create_user(new_username, new_password):
                            st.success("Account created successfully! You can now log in.")
                        else:
                            st.error("Username already exists. Please choose another.")
                    else:
                        st.error("Passwords do not match.")
                else:
                    st.warning("Please fill out all fields.")

def _render_dashboard():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"### Welcome to your Vault, **{st.session_state['username']}**!")
    with col2:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state['user_id'] = None
            st.session_state['username'] = None
            st.rerun()
            
    st.markdown("---")
    
    # Save new item
    with st.expander("➕ Save New Item to Vault", expanded=False):
        with st.form("save_item_form"):
            title = st.text_input("Title / Identifier")
            item_type = st.selectbox("Item Type", ["TEXT", "FILE_B64", "IMAGE_B64"])
            algo = st.selectbox("Encryption Used", ["None", "AES-256", "RSA-2048", "ChaCha20", "LWE (PQC)", "Paillier"])
            content = st.text_area("Content (Ciphertext or Base64)", height=150)
            
            save_btn = st.form_submit_button("Save to Vault")
            if save_btn:
                if title and content:
                    if save_vault_item(st.session_state['user_id'], title, content, item_type, algo):
                        st.success("Item saved successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to save item.")
                else:
                    st.warning("Please provide a title and content.")
                    
    st.markdown("---")
    st.markdown("### Your Stored Items")
    
    items = get_vault_items(st.session_state['user_id'])
    
    if not items:
        st.info("Your vault is empty. Save some encrypted items above!")
    else:
        for item in items:
            with st.container():
                st.markdown(f"""
                <div style="padding:15px; border:1px solid #1e293b; border-radius:8px; margin-bottom:10px; background:rgba(15,23,42,0.6);">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <h4 style="margin:0; color:#00f5ff;">{item['title']}</h4>
                        <span style="font-size:12px; color:#64748b;">{item['created_at']}</span>
                    </div>
                    <div style="display:flex; gap:10px; margin-top:8px; margin-bottom:12px;">
                        <span style="background:#1e293b; padding:2px 8px; border-radius:4px; font-size:12px;">Type: {item['item_type']}</span>
                        <span style="background:#1e293b; padding:2px 8px; border-radius:4px; font-size:12px;">Algo: {item['encryption_algo']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander("View Content"):
                    st.code(item['content'], language="text")
                    if st.button(f"🗑️ Delete Item", key=f"del_{item['id']}"):
                        if delete_vault_item(item['id'], st.session_state['user_id']):
                            st.success("Item deleted!")
                            st.rerun()
                        else:
                            st.error("Failed to delete.")
