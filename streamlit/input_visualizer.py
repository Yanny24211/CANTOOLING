import time

import streamlit as st
import cantools
import pandas as pd

DBC_FILE_PATH = "C:\\Users\\deeps\\Desktop\\Deep Y4S2 Folders\\COE70B\\driver_cantooling_module\\CANTOOLING\\dbc\\nissan_versa_2014.dbc"
INLINE_DBC = cantools.database.load_file(DBC_FILE_PATH)

GEAR_MAP  = {48: "L", 32: "D", 24: "N", 16: "R", 8: "P", 0: "?"}
TURN_MAP  = {0: "Off", 1: "Left", 2: "Right", 3: "Hazards"}

def configure_streamlit_app():
    st.set_page_config(
        page_title="MJ03 - Risk Avoidance System",
        layout="wide",
        initial_sidebar_state="expanded",
    )

def configure_sidebar():
    st.sidebar.title("Settings")
    
    st.sidebar.subheader("Playback Speed")
    
    st.session_state.pb_speed = st.sidebar.select_slider(
        "Select playback rate", 
        options=[0.25, 0.5, 1.0, 2.0, 4.0, 8.0],
        # value=st.session_state.pb_speed
    )

    st.sidebar.subheader("Controls")
    ca, cb, cc = st.sidebar.columns(3)
    
    with ca:
        play_label = "▶" if not st.session_state.playing else "⏸"
        if st.button(play_label, use_container_width=True):
            st.session_state.playing = not st.session_state.playing
            
    with cb:
        if st.button("⏮", use_container_width=True):
            st.session_state.frame_idx = 0
            st.session_state.playing = False
            
    with cc:
        if st.button("⏭", use_container_width=True):
            # Ensure snapshots exist before jumping to end
            if st.session_state.snapshots:
                st.session_state.frame_idx = len(st.session_state.snapshots) - 1
            st.session_state.playing = False


@st.cache_resource
def get_default_db():
    db = cantools.database.Database()
    db.add_dbc_string(INLINE_DBC)
    return db


def parse_asc(content):
    frames = []
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith(("//", "date", "base", "no", "Begin", "End")):
            continue
        parts = line.split()
        if len(parts) < 6:
            continue
        try:
            ts = float(parts[0])
            can_id = int(parts[2], 16)
            dlc = int(parts[4])
            raw = bytes(int(x, 16) for x in parts[5:5 + dlc])
            frames.append({"ts": ts, "id": can_id, "data": raw})
        except Exception:
            continue
    return frames


def main():
    configure_streamlit_app()
    configure_sidebar()
    st.title("MJ03 - Risk Avoidance System | Telemetry Visualizer")
    st.divider()

    if st.session_state.playing:
        step = max(1, int(st.session_state.pb_speed))
        nxt  = idx + step
        if nxt >= len(snaps):
            nxt = 0
            st.session_state.playing = False
        st.session_state.frame_idx = nxt
        delay = max(0.05, 0.1 / st.session_state.pb_speed)
        time.sleep(delay)
        st.rerun()


if __name__ == "__main__":
    main()
