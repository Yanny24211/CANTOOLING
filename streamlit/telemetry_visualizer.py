import streamlit as st
import pandas as pd
import time
import json
import os
import re
from PIL import Image
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

def configure_streamlit_app():
    st.set_page_config(
        page_title="MJ03 - Risk Avoidance System",
        layout="wide",
        initial_sidebar_state="expanded",
    )

def load_telemetry_data(file_path):
    print(f"Attempting to load telemetry data from: {file_path}")
    if not os.path.exists(file_path):
        st.error(f"FILE NOT FOUND: {file_path}")
        return []
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()

        flattened_list = []
        decoder = json.JSONDecoder()
        pos = 0

        current_state = {
            "Steering": 0.0, "Speed": 0.0, "Throttle": 0.0,
            "Brake": 0.0, "Gear_Position": "N"
        }

        while pos < len(content):
            match = re.search(r'\S', content[pos:])
            if not match: break
            pos += match.start()
            try:
                snapshot, index = decoder.raw_decode(content[pos:])
                for msg_id in snapshot:
                    if isinstance(snapshot[msg_id], dict):
                        current_state.update(snapshot[msg_id])

                flattened_list.append(current_state.copy())
                pos += index
            except json.JSONDecodeError: break

        print(f"Loaded {len(flattened_list)} telemetry snapshots.")
        return flattened_list
    except Exception as e:
        st.error(f"System Error: {e}")
        return []

def main():
    configure_streamlit_app()

    if 'frame_idx' not in st.session_state: st.session_state.frame_idx = 0
    if 'playing' not in st.session_state: st.session_state.playing = False
    if 'snapshots' not in st.session_state: st.session_state.snapshots = []
    if 'pb_speed' not in st.session_state: st.session_state.pb_speed = 1.0
    if 'active_path' not in st.session_state:
        st.session_state.active_path = r"C:\Users\deeps\Desktop\Deep Y4S2 Folders\COE70B\driver_cantooling_module\CANTOOLING\raw_decoded_signals.json"

    st.title("MJ03 - Risk Avoidance System | Telemetry Visualizer")
    st.divider()

    st.sidebar.title("Settings")
    paths = {
        "DE": r"C:\Users\deeps\Desktop\Deep Y4S2 Folders\COE70B\driver_cantooling_module\CANTOOLING\raw_decoded_signals.json",
        "90": r"C:\Users\deeps\Desktop\Deep Y4S2 Folders\COE70B\driver_cantooling_module\CANTOOLING\raw_decoded_signals90.json",
        "91": r"C:\Users\deeps\Desktop\Deep Y4S2 Folders\COE70B\driver_cantooling_module\CANTOOLING\raw_decoded_signals91.json"
    }

    st.sidebar.subheader("Select Dataset")
    b_cols = st.sidebar.columns(3)
    if b_cols[0].button("DE", width="stretch"):
        st.session_state.active_path, st.session_state.snapshots, st.session_state.frame_idx = paths["DE"], load_telemetry_data(paths["DE"]), 0
        st.rerun()
    if b_cols[1].button("90", width="stretch"):
        st.session_state.active_path, st.session_state.snapshots, st.session_state.frame_idx = paths["90"], load_telemetry_data(paths["90"]), 0
        st.rerun()
    if b_cols[2].button("91", width="stretch"):
        st.session_state.active_path, st.session_state.snapshots, st.session_state.frame_idx = paths["91"], load_telemetry_data(paths["91"]), 0
        st.rerun()

    st.sidebar.info(f"Active: {os.path.basename(st.session_state.active_path)}")

    st.sidebar.subheader("Playback Speed")
    st.session_state.pb_speed = st.sidebar.select_slider(
        "Speed Multiplier", options=[0.1, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0], value=1.0
    )

    st.sidebar.subheader("Controls")
    ca, cb, cc = st.sidebar.columns(3)
    with ca:
        if st.button("▶" if not st.session_state.playing else "⏸", width="stretch"):
            st.session_state.playing = not st.session_state.playing
            st.rerun()
    with cb:
        if st.button("⏮", width="stretch"):
            st.session_state.frame_idx, st.session_state.playing = 0, False
            st.rerun()
    with cc:
        if st.button("⏭", width="stretch"):
            if st.session_state.snapshots: st.session_state.frame_idx = len(st.session_state.snapshots) - 1
            st.session_state.playing = False
            st.rerun()

    col1, col2 = st.columns([1, 1.2])
    with col1:
        st.subheader("Vehicle HUD")
        wheel_placeholder = st.empty()
        m1, m2, m3 = st.columns(3)
        speed_metric, gear_metric, angle_metric = m1.empty(), m2.empty(), m3.empty()

    with col2:
        st.subheader("Telemetry History")
        chart_placeholder = st.empty()
        st.write("---")
        progress_label = st.empty()
        log_progress = st.empty()
        st.write("**Pedal Inputs**")
        t_label, throttle_bar = st.empty(), st.empty()
        b_label, brake_bar = st.empty(), st.empty()

    try:
        wheel_img = Image.open("media_assets/steering_wheel.png").convert("RGBA")
    except:
        wheel_img = Image.new("RGBA", (300, 300), (200, 200, 200, 255))

    # Color Mapping: Green Throttle, Red Brake, Bright Blue Speed
    CHART_COLORS = {"Throttle": "#00FF00", "Brake": "#FF0000", "Speed": "#00CCFF"}

    if st.session_state.snapshots:
        total_frames = len(st.session_state.snapshots)

        while st.session_state.playing and st.session_state.frame_idx < total_frames:
            start_loop = time.time()
            data = st.session_state.snapshots[st.session_state.frame_idx]

            angle = data.get("Steering", 0)
            wheel_placeholder.image(wheel_img.rotate(-angle), width="stretch")
            speed_metric.metric("Speed", f"{data.get('Speed', 0):.1f} km/h")
            gear_metric.metric("Gear", data.get("Gear_Position", "N"))
            angle_metric.metric("Steering", f"{angle:.1f}°")

            progress_label.text(f"Segment: {st.session_state.frame_idx + 1} / {total_frames}")
            log_progress.progress((st.session_state.frame_idx + 1) / total_frames)

            t_raw, b_raw = float(data.get('Throttle', 0)), float(data.get('Brake', 0))
            t_label.text(f"Throttle: {t_raw:.1f}%")
            throttle_bar.progress(min(max(t_raw / 100.0, 0.0), 1.0))
            b_label.text(f"Brake: {b_raw:.1f}%")
            brake_bar.progress(min(max(b_raw / 100.0, 0.0), 1.0))

            if st.session_state.frame_idx % 10 == 0:
                h_start = max(0, st.session_state.frame_idx - 100)
                chart_df = pd.DataFrame(st.session_state.snapshots[h_start:st.session_state.frame_idx + 1])
                plot_cols = [c for c in ["Speed", "Throttle", "Brake"] if c in chart_df.columns]
                chart_placeholder.line_chart(chart_df[plot_cols], color=[CHART_COLORS[c] for c in plot_cols])

            st.session_state.frame_idx += 1

            # Sync to 16Hz (Capstone Review Speed)
            elapsed = time.time() - start_loop
            sleep_duration = (0.0625 / st.session_state.pb_speed) - elapsed
            if sleep_duration > 0:
                time.sleep(sleep_duration)

            if st.session_state.frame_idx >= total_frames:
                st.session_state.playing = False
                st.rerun()

        if not st.session_state.playing:
            idx = min(st.session_state.frame_idx, total_frames - 1)
            data = st.session_state.snapshots[idx]
            angle = data.get("Steering", 0)
            wheel_placeholder.image(wheel_img.rotate(-angle), width="stretch")
            speed_metric.metric("Speed", f"{data.get('Speed', 0):.1f} km/h")
            gear_metric.metric("Gear", data.get("Gear_Position", "N"))
            angle_metric.metric("Steering", f"{angle:.1f}°")

            progress_label.text(f"Segment: {idx + 1} / {total_frames}")
            log_progress.progress((idx + 1) / total_frames)

            t_r, b_r = float(data.get('Throttle', 0)), float(data.get('Brake', 0))
            t_label.text(f"Throttle: {t_r:.1f}%")
            throttle_bar.progress(min(max(t_r / 100.0, 0.0), 1.0))
            b_label.text(f"Brake: {b_r:.1f}%")
            brake_bar.progress(min(max(b_r / 100.0, 0.0), 1.0))

            h_start = max(0, idx - 100)
            chart_df = pd.DataFrame(st.session_state.snapshots[h_start:idx+1])
            plot_cols = [c for c in ["Speed", "Throttle", "Brake"] if c in chart_df.columns]
            chart_placeholder.line_chart(chart_df[plot_cols], color=[CHART_COLORS[c] for c in plot_cols])
    else:
        st.info("Awaiting telemetry data...")

if __name__ == "__main__":
    main()
