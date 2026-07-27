import streamlit as st
import datetime

# ====================== CLOCK CONFIGURATION ======================
# Each entry: planets (in sequence), reference default values.
LEFT_CLOCK = {
    12: {"planets": ["Jupiter"],           "ref_vals": [4],   "label": "\u2643"},
    1:  {"planets": ["Jupiter", "Venus"],  "ref_vals": [4,3], "label": "\u2643 + \u2640"},
    2:  {"planets": ["Venus", "Jupiter"],  "ref_vals": [3,4], "label": "\u2640 + \u2643"},
    3:  {"planets": ["Venus"],             "ref_vals": [3],   "label": "\u2640"},
    4:  {"planets": ["Venus", "Mercury"],  "ref_vals": [3,1], "label": "\u2640 + \u263F"},
    5:  {"planets": ["Mercury", "Venus"],  "ref_vals": [1,3], "label": "\u263F + \u2640"},
    6:  {"planets": ["Mercury"],           "ref_vals": [1],   "label": "\u263F"},
    7:  {"planets": ["Mercury", "Moon"],   "ref_vals": [1,2], "label": "\u263F + \u263D"},
    8:  {"planets": ["Moon", "Mercury"],   "ref_vals": [2,1], "label": "\u263D + \u263F"},
    9:  {"planets": ["Moon"],              "ref_vals": [2],   "label": "\u263D"},
    10: {"planets": ["Moon", "Jupiter"],   "ref_vals": [2,4], "label": "\u263D + \u2643"},
    11: {"planets": ["Jupiter", "Moon"],   "ref_vals": [4,2], "label": "\u2643 + \u263D"},
}

RIGHT_CLOCK = {
    12: {"planets": ["Rahu"],             "ref_vals": [4],   "label": "☊"},
    1:  {"planets": ["Rahu", "Mars"],     "ref_vals": [4,3], "label": "☊ + \u2642"},
    2:  {"planets": ["Mars", "Rahu"],     "ref_vals": [3,4], "label": "\u2642 + ☊"},
    3:  {"planets": ["Mars"],             "ref_vals": [3],   "label": "\u2642"},
    4:  {"planets": ["Mars", "Sun"],      "ref_vals": [3,1], "label": "\u2642 + \u263C"},
    5:  {"planets": ["Sun", "Mars"],      "ref_vals": [1,3], "label": "\u263C + \u2642"},
    6:  {"planets": ["Sun"],              "ref_vals": [1],   "label": "\u263C"},
    7:  {"planets": ["Sun", "Saturn"],    "ref_vals": [1,2], "label": "\u263C + \u2644"},
    8:  {"planets": ["Saturn", "Sun"],    "ref_vals": [2,1], "label": "\u2644 + \u263C"},
    9:  {"planets": ["Saturn"],           "ref_vals": [2],   "label": "\u2644"},
    10: {"planets": ["Saturn", "Rahu"],   "ref_vals": [2,4], "label": "\u2644 + ☊"},
    11: {"planets": ["Rahu", "Saturn"],   "ref_vals": [4,2], "label": "☊ + \u2644"},
}

# ====================== DIAMOND GRID LAYOUT ======================
# (row, col) → clock hour (7×7 grid, diamond shape)
DIAMOND_MAP = {
    (1, 4): 12, (2, 5): 1,  (3, 6): 2,  (4, 7): 3,
    (5, 6): 4,  (6, 5): 5,  (7, 4): 6,  (6, 3): 7,
    (5, 2): 8,  (4, 1): 9,  (3, 2): 10, (2, 3): 11
}

# ====================== SESSION STATE ======================
if 'run_id' not in st.session_state:        st.session_state['run_id'] = 0
if 'selected_hours' not in st.session_state: st.session_state['selected_hours'] = []
if 'active_preset' not in st.session_state:  st.session_state['active_preset'] = "Preset A"
if 'last_log' not in st.session_state:       st.session_state['last_log'] = None

planets_list = ["Mercury", "Sun", "Moon", "Mars", "Venus", "Saturn", "Jupiter", "Rahu", "Ketu"]
modes = ["Binary", "Trivalent", "Quaternary"]

# Default Target Logic Variant Mapping Configuration Set
DEFAULTS = {
    "binary": {
        "map_a": {
            "Mercury": 1, "Sun": 1, "Moon": 1, "Mars": 1,
            "Venus": 2, "Saturn": 2, "Jupiter": 2, "Rahu": 2, "Ketu": 2
        },
        "map_b": {
            "Mercury": 2, "Sun": 2, "Moon": 2, "Mars": 2,
            "Venus": 1, "Saturn": 1, "Jupiter": 1, "Rahu": 1, "Ketu": 1
        }
    },
    "trivalent": {
        "map_a": {
            "Mercury": 1, "Sun": 1, "Moon": 1, "Mars": 1,
            "Venus": 2, "Saturn": 2, "Jupiter": 2, "Rahu": 2, "Ketu": 3
        },
        "map_b": {
            "Mercury": 2, "Sun": 2, "Moon": 2, "Mars": 2,
            "Venus": 1, "Saturn": 1, "Jupiter": 1, "Rahu": 1, "Ketu": 3
        }
    },
    "quaternary": {
        "map_a": {
            "Mercury": 1, "Sun": 1, "Moon": 2, "Mars": 2,
            "Venus": 3, "Saturn": 3, "Jupiter": 4, "Rahu": 4, "Ketu": 4
        },
        "map_b": {
            "Mercury": 4, "Sun": 4, "Moon": 3, "Mars": 3,
            "Venus": 2, "Saturn": 2, "Jupiter": 1, "Rahu": 1, "Ketu": 1
        }
    }
}

for m in modes:
    m_lower = m.lower()
    key_a, key_b = f"map_a_{m_lower}", f"map_b_{m_lower}"
    if key_a not in st.session_state:
        st.session_state[key_a] = DEFAULTS[m_lower]["map_a"].copy()
    if key_b not in st.session_state:
        st.session_state[key_b] = DEFAULTS[m_lower]["map_b"].copy()

st.set_page_config(page_title="Tattva Lab v31", layout="wide")

# ====================== PREMIUM DARK GLASSMORPHISM STYLING ======================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');

    /* Global container styling */
    .main, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #0B0F19 !important;
        font-family: 'Outfit', sans-serif !important;
        color: #F3F4F6 !important;
    }
    
    /* Sidebar styling override */
    [data-testid="stSidebar"] {
        background-color: #0F172A !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
    
    /* Global Typography overrides */
    h1, h2, h3, h4, h5, h6, p, span, label, div {
        font-family: 'Outfit', sans-serif !important;
    }

    /* Target only our diamond grid buttons using symbol matching to keep them square */
    .stButton button[aria-label*="♃"], .stButton button[title*="♃"],
    .stButton button[aria-label*="♀"], .stButton button[title*="♀"],
    .stButton button[aria-label*="☿"], .stButton button[title*="☿"],
    .stButton button[aria-label*="☌"], .stButton button[title*="☌"],
    .stButton button[aria-label*="☾"], .stButton button[title*="☌"],
    .stButton button[aria-label*="☊"], .stButton button[title*="☊"],
    .stButton button[aria-label*="♂"], .stButton button[title*="♂"],
    .stButton button[aria-label*="☼"], .stButton button[title*="☼"],
    .stButton button[aria-label*="♄"], .stButton button[title*="♄"],
    .stButton button[aria-label*="☿"], .stButton button[title*="☿"] {
        height: auto !important;
        aspect-ratio: 1 / 1 !important;
        font-weight: 800 !important;
        border-radius: 12px !important;
        white-space: pre-wrap !important;
        line-height: 1.15 !important;
        padding: 4px 2px !important;
        font-family: "Segoe UI Symbol", "Apple Symbols", 'Outfit', sans-serif !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    /* Target Unicode ranges for Moon symbol just in case (\u263D) */
    .stButton button[aria-label*="☾"], .stButton button[title*="☾"],
    .stButton button[aria-label*="☽"], .stButton button[title*="☽"],
    .stButton button[aria-label*="☿"], .stButton button[title*="☿"],
    .stButton button[aria-label*="♃"], .stButton button[title*="♃"],
    .stButton button[aria-label*="♀"], .stButton button[title*="♀"],
    .stButton button[aria-label*="☿"], .stButton button[title*="☿"] {
        height: auto !important;
        aspect-ratio: 1 / 1 !important;
    }

    /* Unselected button (Secondary) styling */
    .stButton button[data-testid="stBaseButton-secondary"] {
        background-color: #1E293B !important;
        color: #94A3B8 !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
    }

    .stButton button[data-testid="stBaseButton-secondary"]:hover {
        background-color: #334155 !important;
        color: #F8FAFC !important;
        border-color: rgba(255, 255, 255, 0.2) !important;
        transform: translateY(-2px) scale(1.04) !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
    }

    /* Selected button (Primary) styling with vivid gradient and glow */
    .stButton button[data-testid="stBaseButton-primary"] {
        background-image: linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        box-shadow: 0 0 15px rgba(139, 92, 246, 0.5) !important;
    }

    .stButton button[data-testid="stBaseButton-primary"]:hover {
        background-image: linear-gradient(135deg, #60A5FA 0%, #A78BFA 100%) !important;
        transform: translateY(-2px) scale(1.04) !important;
        box-shadow: 0 0 20px rgba(139, 92, 246, 0.75), 0 4px 12px rgba(0, 0, 0, 0.3) !important;
    }

    /* Grid buttons with compound labels containing a plus symbol get smaller font size */
    .stButton button[aria-label*="+"], .stButton button[title*="+"] {
        font-size: 20px !important;
    }
    
    /* Grid buttons with single labels get larger font size */
    .stButton button:not([aria-label*="+"]):not([title*="+"]) {
        font-size: 30px !important;
    }

    /* Outcome log buttons (Secondary but in horizontal blocks) should not be square */
    [data-testid="stHorizontalBlock"] .stButton button {
        aspect-ratio: auto !important;
        height: 48px !important;
        font-size: 16px !important;
        font-weight: 600 !important;
    }

    /* Styling for notes text area and magic number inputs */
    div[data-baseweb="input"] input, div[data-baseweb="textarea"] textarea {
        background-color: #1E293B !important;
        color: #F3F4F6 !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 8px !important;
    }

    /* Style block container borders */
    [data-testid="stVerticalBlockBorderContainer"] {
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 12px !important;
        background-color: rgba(30, 41, 59, 0.4) !important;
        backdrop-filter: blur(10px) !important;
        padding: 16px !important;
    }
</style>
""", unsafe_allow_html=True)


def get_predicted_values(selected_hours, active_map, max_val):
    predicted = []
    for key in selected_hours:
        side, hour_str = key.split('_')
        hour = int(hour_str)
        clock_cfg = LEFT_CLOCK if side == 'L' else RIGHT_CLOCK
        for planet in clock_cfg[hour]["planets"]:
            val = active_map.get(planet, 1)
            if val <= max_val and val not in predicted:
                predicted.append(val)
    return predicted


def toggle_hour(btn_key):
    if btn_key in st.session_state['selected_hours']:
        st.session_state['selected_hours'].remove(btn_key)
    else:
        st.session_state['selected_hours'].append(btn_key)


def render_diamond_grid(side, clock_config, container):
    for r in range(1, 8):
        row_cols = container.columns(7)
        for c in range(1, 8):
            if (r, c) in DIAMOND_MAP:
                hour    = DIAMOND_MAP[(r, c)]
                cfg     = clock_config[hour]
                btn_key = f"{side}_{hour}"
                label   = cfg["label"]
                is_sel  = btn_key in st.session_state['selected_hours']

                row_cols[c - 1].button(
                    label,
                    key=f"{btn_key}_{st.session_state['run_id']}",
                    type="primary" if is_sel else "secondary",
                    use_container_width=True,
                    on_click=toggle_hour,
                    args=(btn_key,)
                )
            else:
                row_cols[c - 1].empty()


@st.fragment
def render_matrix_logger_panel(obs_mode, current_set, labels, max_val_mode, current_active_map):
    col_l, col_m, col_r = st.columns([4, 2, 4])

    with col_l:
        st.subheader("Left Grid")
        render_diamond_grid("L", LEFT_CLOCK, st.container())

    with col_m:
        st.markdown(f"**Preset:** {st.session_state['active_preset']}  \n**Mode:** {obs_mode}  \n**Set:** {current_set}")
        st.divider()

        raw_magic = st.text_input("✨ Magic Number", value="0", key=f"m_{st.session_state['run_id']}")
        try:    magic_num = int(raw_magic)
        except: magic_num = 0

        user_note = st.text_area("📝 Notes", max_chars=200, height=90, key=f"n_{st.session_state['run_id']}")

        if st.session_state['selected_hours']:
            predicted = get_predicted_values(st.session_state['selected_hours'], current_active_map, max_val_mode)
            if predicted:
                st.write("**System Prediction:**")
                for v in predicted:
                    if v <= len(labels):
                        st.markdown(f"🔳 **{v}) {labels[v - 1]}**")

    with col_r:
        st.subheader("Right Grid")
        render_diamond_grid("R", RIGHT_CLOCK, st.container())

    st.divider()
    st.subheader("🎯 Log Outcome")

    if st.session_state['last_log']:
        st.info(st.session_state['last_log'])

    if not st.session_state['selected_hours']:
        st.caption("Select position structures on the grids above to formulate a current active state evaluation context.")
    else:
        selected_display = "  ·  ".join(st.session_state['selected_hours'])
        st.write(f"**Selected Positions:** {selected_display}")

        predicted       = get_predicted_values(st.session_state['selected_hours'], current_active_map, max_val_mode)
        predicted_ints  = list(dict.fromkeys(predicted))   

        if predicted_ints:
            pred_label_str = ", ".join([f"{v}) {labels[v-1]}" for v in predicted_ints if v <= len(labels)])
            st.write(f"**System Matrix Target:** {pred_label_str}")

        o_cols = st.columns(len(labels))
        for i, lbl in enumerate(labels):
            if o_cols[i].button(f"{lbl}", key=f"o_{i}_{st.session_state['run_id']}", use_container_width=True):
                verdict = "Right" if (i + 1) in predicted_ints else "Wrong"
                
                st.session_state['last_log'] = f"Logged Selection: **{lbl}** → Marked: **{verdict}** (Magic Axis Value: {magic_num})"
                st.session_state['selected_hours'] = []
                st.session_state['run_id'] += 1
                st.rerun()


# ====================== TAB DEFINITIONS ======================
tab1, tab2 = st.tabs([
    "🚀 Spatial Logger",
    "⚙️ Settings"
])

# ==========================================
# TAB 1 — CHRONOS DIAMOND MATRIX LOGGER
# ==========================================
with tab1:
    with st.sidebar:
        st.header("🎮 Live Controls")
        st.session_state['active_preset'] = st.radio("Active Logic Mapping", ["Preset A", "Preset B"])
        st.divider()
        obs_mode = st.radio("Logic Mode", modes)

        logic_config = {
            "Binary": {
                "Direction":  ["Left", "Right"],
                "Decision":   ["Yes", "No"],
                "Trend":      ["Up", "Down"],
                "Polarity":   ["Positive", "Negative"],
                "OddEven":   ["Odd", "Even"],
            },
            "Trivalent": {
                "Game": ["Dragon", "Tie", "Tiger"],
                "Symmetry":   ["Left", "Both", "Right"],
                "Trend":      ["Rise", "Flat", "Fall"],
                "Position":   ["Long", "Neutral", "Short"],
                "Energy":     ["Active", "Neutral", "Passive"],
            },
            "Quaternary": {
                "Primary":    ["1", "2", "3", "4"],
                "Strategy":   ["Buy", "Sell", "Add", "Wait"],
                "Sentiment":  ["Reversal", "Bullish", "Bearish", "Corrective"],
                "Element":    ["Earth", "Water", "Fire", "Air"],
                "Direction":  ["North", "West", "East", "South"],
                "Matka":      ["1Q", "2Q", "3Q", "4Q"]
            }
        }
        current_set = st.selectbox("Semantic Set", list(logic_config[obs_mode].keys()))
        labels = logic_config[obs_mode][current_set]

        if st.button("🔄 Clear All Selections"):
            st.session_state['selected_hours'] = []
            st.session_state['run_id'] += 1
            st.session_state['last_log'] = None
            st.rerun()

    map_key = f"map_{'a' if st.session_state['active_preset'] == 'Preset A' else 'b'}_{obs_mode.lower()}"
    current_active_map = st.session_state[map_key]
    max_val_mode = 2 if obs_mode == "Binary" else (3 if obs_mode == "Trivalent" else 4)

    render_matrix_logger_panel(obs_mode, current_set, labels, max_val_mode, current_active_map)

# ==========================================
# TAB 2 — SETTINGS
# ==========================================
with tab2:
    st.title("⚙️ Configuration Reference Matrix")

    m_choice    = st.radio("Target Logic Variant Mapping Configuration Set:", modes, horizontal=True)
    max_map_val = 2 if m_choice == "Binary" else (3 if m_choice == "Trivalent" else 4)

    col_set_a, col_set_b = st.columns(2)
    with col_set_a:
        st.subheader("Preset Alignment Map A")
        key_a   = f"map_a_{m_choice.lower()}"
        new_map_a = {
            p: st.number_input(f"{p} Value Mapping", 1, max_map_val,
                               int(st.session_state[key_a].get(p, 1)),
                               key=f"s_a_{m_choice}_{p}")
            for p in planets_list
        }
        if st.button(f"Save Configuration Set A [{m_choice}]"):
            st.session_state[key_a] = new_map_a
            st.success("Set A state cached.")

    with col_set_b:
        st.subheader("Preset Alignment Map B")
        key_b   = f"map_b_{m_choice.lower()}"
        new_map_b = {
            p: st.number_input(f"{p} Value Mapping", 1, max_map_val,
                               int(st.session_state[key_b].get(p, max_map_val)),
                               key=f"s_b_{m_choice}_{p}")
            for p in planets_list
        }
        if st.button(f"Save Configuration Set B [{m_choice}]"):
            st.session_state[key_b] = new_map_b
            st.success("Set B state cached.")

    st.divider()
    st.subheader("🗺️ Structural Layout Matrix Mapping Table")

    cr1, cr2 = st.columns(2)
    with cr1:
        st.markdown("**Left Matrix Components (Jupiter · Venus · Mercury · Moon)**")
        left_ref = [
            {
                "Hour Index": h,
                "Structural Assignments": " + ".join(LEFT_CLOCK[h]["planets"]),
                "Static Vectors": str(LEFT_CLOCK[h]["ref_vals"]),
            }
            for h in [12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        ]
        st.dataframe(left_ref, width='stretch', hide_index=True)

    with cr2:
        st.markdown("**Right Matrix Components (Rahu · Mars · Sun · Saturn)**")
        right_ref = [
            {
                "Hour Index": h,
                "Structural Assignments": " + ".join(RIGHT_CLOCK[h]["planets"]),
                "Static Vectors": str(RIGHT_CLOCK[h]["ref_vals"]),
            }
            for h in [12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        ]
        st.dataframe(right_ref, width='stretch', hide_index=True)

st.caption("Tattva Lab v31 • Monochrome Space Platform • No Local Storage Dependency Tracking Enabled")