"""
Onion Routing Simulator UI — MahesaVault
Simulates the Tor (The Onion Router) network concept using RSA encryption.
Visualizes how a message is wrapped in layers of encryption and peeled off at each node.
"""

import streamlit as st
import time
from modules.cryptography.advanced.paillier_cipher import generate_keys as p_keys
from modules.cryptography.modern.rsa_cipher import generate_keys, encrypt, decrypt
from ui.components.theme_3d import render_page_header, render_glass_message_box

def render():
    render_page_header(
        "🧅 Onion Routing Simulator",
        "Multi-Layer Encryption",
        "Visualize how the Tor Network wraps messages in layers of encryption."
    )
    
    st.markdown("### The Network Nodes")
    st.markdown("In this simulation, your message will travel through 3 nodes to reach the destination: **Entry Node**, **Relay Node**, and **Exit Node**.")
    
    # Generate keys for 3 nodes if not exist
    if 'onion_keys' not in st.session_state:
        with st.spinner("Generating RSA-2048 keys for all 3 nodes..."):
            st.session_state['onion_keys'] = {
                'entry': generate_keys(),
                'relay': generate_keys(),
                'exit': generate_keys(),
                'destination': generate_keys()
            }
            
    nodes = st.session_state['onion_keys']
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("**1. Entry Node**\n\nKnows who you are, but doesn't know the message.")
    with col2:
        st.warning("**2. Relay Node**\n\nKnows nothing. Only passes data from Entry to Exit.")
    with col3:
        st.error("**3. Exit Node**\n\nKnows the message, but doesn't know who you are.")
        
    st.markdown("---")
    
    st.markdown("### 1. Compose Message")
    message = st.text_area("Secret Message for Destination:")
    
    if st.button("Start Onion Routing Simulation", type="primary"):
        if not message:
            st.warning("Please enter a message.")
            return
            
        st.markdown("---")
        st.markdown("### 2. Wrapping the Onion (Client-side)")
        
        with st.status("Encrypting layers...", expanded=True) as status:
            st.write("Wrapping Layer 1 (Destination)...")
            layer1 = encrypt(message, nodes['destination'][1])
            time.sleep(1)
            
            st.write("Wrapping Layer 2 (Exit Node)...")
            layer2 = encrypt(layer1, nodes['exit'][1])
            time.sleep(1)
            
            st.write("Wrapping Layer 3 (Relay Node)...")
            layer3 = encrypt(layer2, nodes['relay'][1])
            time.sleep(1)
            
            st.write("Wrapping Layer 4 (Entry Node)...")
            final_onion = encrypt(layer3, nodes['entry'][1])
            time.sleep(1)
            
            status.update(label="Message fully encrypted!", state="complete", expanded=False)
            
        render_glass_message_box("THE ONION (Final Ciphertext sent to Entry Node)", final_onion[:200] + "...\n[TRUNCATED]", "#a855f7")
        
        st.markdown("---")
        st.markdown("### 3. Peeling the Onion (Network-side)")
        
        st.info("🔵 **Hop 1: Entry Node** receives the Onion. It peels its layer using its Private Key.")
        peeled_entry = decrypt(final_onion, nodes['entry'][0])
        st.code("Peeled to Layer 3:\n" + peeled_entry[:100] + "...", language="text")
        time.sleep(1.5)
        
        st.warning("🟡 **Hop 2: Relay Node** receives Layer 3. It peels its layer using its Private Key.")
        peeled_relay = decrypt(peeled_entry, nodes['relay'][0])
        st.code("Peeled to Layer 2:\n" + peeled_relay[:100] + "...", language="text")
        time.sleep(1.5)
        
        st.error("🔴 **Hop 3: Exit Node** receives Layer 2. It peels its layer using its Private Key.")
        peeled_exit = decrypt(peeled_relay, nodes['exit'][0])
        st.code("Peeled to Layer 1 (Destination payload):\n" + peeled_exit[:100] + "...", language="text")
        time.sleep(1.5)
        
        st.success("🟢 **Destination** receives Layer 1. It decrypts the final payload using its Private Key.")
        final_message = decrypt(peeled_exit, nodes['destination'][0])
        render_glass_message_box("DESTINATION RECEIVED:", final_message, "#10b981")
        
        st.balloons()
