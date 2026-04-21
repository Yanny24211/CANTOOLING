import streamlit as st
import pandas as pd
import time
import json
import os
from PIL import Image

def configure_streamlit_app():
    st.set_page_config(
        page_title="MJ03 - Risk Avoidance System",
        layout="wide",
        initial_sidebar_state="expanded",
    )

def load_telemetry_data(file_path):
    if not os.path.exists(file_path):
        return []
    with open(file_path, 'r') as f:
        content = f.read()
    try:
        valid_json_string = content.replace("}{", "},{")
        raw_list = json.loads(f"[{valid_json_string}]")
        flattened_list = []
        for snapshot in raw_list:
            flat_entry = {}
            for msg_id in snapshot:
                flat_entry.update(snapshot[msg_id])
            flattened_list.append(flat_entry)
        return flattened_list
    except:
        return []

def main():
    configure_streamlit_app()
    
    if 'frame_idx' not in st.session_state:
        st.session_state.frame_idx = 0
    if 'playing' not in st.session_state:
        st.session_state.playing = False
    if 'snapshots' not in st.session_state:
        st.session_state.snapshots = []

    st.title("MJ03 - Risk Avoidance System | Telemetry Visualizer")
    st.divider()

    # --- Sidebar ---
    st.sidebar.title("Settings")
    json_path = r"C:\Users\deeps\Desktop\Deep Y4S2 Folders\COE70B\driver_cantooling_module\CANTOOLING\raw_decoded_signals.json"
    
    if st.sidebar.button("Load Data"):
        st.session_state.snapshots = load_telemetry_data(json_path)
        st.session_state.frame_idx = 0
        st.rerun()

    st.sidebar.subheader("Controls")
    ca, cb, cc = st.sidebar.columns(3)
    with ca:
        if st.button("▶" if not st.session_state.playing else "⏸", use_container_width=True):
            st.session_state.playing = not st.session_state.playing
            st.rerun()
    with cb:
        if st.button("⏮", use_container_width=True):
            st.session_state.frame_idx = 0
            st.session_state.playing = False
            st.rerun()
    with cc:
        if st.button("⏭", use_container_width=True):
            if st.session_state.snapshots:
                st.session_state.frame_idx = len(st.session_state.snapshots) - 1
            st.session_state.playing = False
            st.rerun()

    # --- Layout ---
    col1, col2 = st.columns([1, 1.2])

    with col1:
        st.subheader("Vehicle HUD")
        wheel_placeholder = st.empty()
        
        # Performance/Speed Metrics
        m1, m2 = st.columns(2)
        speed_metric = m1.empty()
        gear_metric = m2.empty()
        
    with col2:
        st.subheader("Telemetry History")
        chart_placeholder = st.empty()

        # Pedal Inputs (Throttle & Brake)
        st.write("---")
        st.write("**Pedal Inputs**")
        
        # Throttle Bar (Green)
        t_label = st.empty()
        throttle_bar = st.empty()
        
        # Brake Bar (Red)
        b_label = st.empty()
        brake_bar = st.empty()

    try:
        # Load pre-resized wheel
        wheel_img = Image.open("media_assets/steering_wheel2.png").convert("RGBA")
    except:
        wheel_img = Image.new("RGBA", (300, 300), (200, 200, 200, 255))

    if st.session_state.snapshots:
        total_frames = len(st.session_state.snapshots)
        
        while st.session_state.playing and st.session_state.frame_idx < total_frames:
            data = st.session_state.snapshots[st.session_state.frame_idx]
            
            # 1. Update Steering
            angle = data.get("Steering", 0)
            wheel_placeholder.image(wheel_img.rotate(-angle), use_container_width=True)

            # 2. Update Basic Metrics
            speed_metric.metric("Speed", f"{data.get('Speed', 0):.1f} km/h")
            gear_metric.metric("Gear", data.get("Gear_Position", "N"))
            
            # 3. Update Input Bars
            t_val = float(data.get('Throttle', 0)) / 100.0
            t_label.text(f"Throttle: {data.get('Throttle', 0):.1f}%")
            throttle_bar.progress(min(max(t_val, 0.0), 1.0))
            
            # Since Streamlit progress bars aren't red by default, we use a simple hack:
            # We display the Brake percentage as text alongside the progress bar.
            b_val = float(data.get('Brake', 0)) / 100.0
            b_label.text(f"Brake: {data.get('Brake', 0):.1f}%")
            brake_bar.progress(min(max(b_val, 0.0), 1.0))

            # 4. Decoupled Chart (Update every 15 frames for speed)
            if st.session_state.frame_idx % 15 == 0:
                history_end = st.session_state.frame_idx + 1
                history_start = max(0, history_end - 100)
                chart_df = pd.DataFrame(st.session_state.snapshots[history_start:history_end])
                cols = [c for c in ["Speed", "Throttle", "Brake"] if c in chart_df.columns]
                chart_placeholder.line_chart(chart_df[cols])

            st.session_state.frame_idx += 1
            time.sleep(0.01) # Near real-time playback
            
            if st.session_state.frame_idx >= total_frames:
                st.session_state.playing = False
                st.rerun()

        # Static Display for Pause
        if not st.session_state.playing:
            idx = min(st.session_state.frame_idx, total_frames - 1)
            data = st.session_state.snapshots[idx]
            wheel_placeholder.image(wheel_img.rotate(-data.get("Steering", 0)), use_container_width=True)
            speed_metric.metric("Speed", f"{data.get('Speed', 0):.1f} km/h")
            gear_metric.metric("Gear", data.get("Gear_Position", "N"))
            t_label.text(f"Throttle: {data.get('Throttle', 0):.1f}%")
            throttle_bar.progress(min(max(float(data.get('Throttle', 0))/100, 0.0), 1.0))
            b_label.text(f"Brake: {data.get('Brake', 0):.1f}%")
            brake_bar.progress(min(max(float(data.get('Brake', 0))/100, 0.0), 1.0))
    else:
        st.info("Awaiting telemetry data...")

if __name__ == "__main__":
    main()
