import streamlit as st
import datetime

# ====================== CLOCK CONFIGURATION ======================
# Each entry: planets (in sequence), reference default values.
# Actual prediction values come from the Settings preset mappings.

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

# ====================== COLOR ENGINE ======================
def blend_hex(c1_hex, c2_hex, ratio_c1):
    """Blend two hex colors by a ratio (ratio_c1 = weight of c1)."""
    c1 = tuple(int(c1_hex[i:i+2], 16) for i in (1, 3, 5))
    c2 = tuple(int(c2_hex[i:i+2], 16) for i in (1, 3, 5))
    blended = tuple(int(c1[i] * ratio_c1 + c2[i] * (1 - ratio_c1)) for i in range(3))
    return f"#{blended[0]:02X}{blended[1]:02X}{blended[2]:02X}"

DARK_GREEN   = "#006400"
LIGHT_RED    = "#FF9999"
LIGHT_YELLOW = "#FFFF99"
WHITE        = "#FFFFFF"
LIGHT_BLUE   = "#87CEEB"
GRAY_WHITE   = "#C8C8C8"

LEFT_COLORS = {
    12: DARK_GREEN,
    1:  blend_hex(DARK_GREEN, LIGHT_RED, 0.66),
    2:  blend_hex(LIGHT_RED, DARK_GREEN, 0.66),
    3:  LIGHT_RED,
    4:  blend_hex(LIGHT_RED, LIGHT_YELLOW, 0.66),
    5:  blend_hex(LIGHT_YELLOW, LIGHT_RED, 0.66),
    6:  LIGHT_YELLOW,
    7:  blend_hex(LIGHT_YELLOW, WHITE, 0.66),
    8:  blend_hex(WHITE, LIGHT_YELLOW, 0.66),
    9:  WHITE,
    10: blend_hex(WHITE, DARK_GREEN, 0.66),
    11: blend_hex(DARK_GREEN, WHITE, 0.66),
}

RIGHT_COLORS = {
    12: LIGHT_BLUE,
    1:  blend_hex(LIGHT_BLUE, LIGHT_RED, 0.66),
    2:  blend_hex(LIGHT_RED, LIGHT_BLUE, 0.66),
    3:  LIGHT_RED,
    4:  blend_hex(LIGHT_RED, LIGHT_YELLOW, 0.66),
    5:  blend_hex(LIGHT_YELLOW, LIGHT_RED, 0.66),
    6:  LIGHT_YELLOW,
    7:  blend_hex(LIGHT_YELLOW, WHITE, 0.66),
    8:  blend_hex(GRAY_WHITE, LIGHT_YELLOW, 0.66),
    9:  GRAY_WHITE,
    10: blend_hex(GRAY_WHITE, LIGHT_BLUE, 0.66),
    11: blend_hex(LIGHT_BLUE, GRAY_WHITE, 0.66),
}

def get_text_color(bg_hex):
    """Return black or white depending on background brightness."""
    r, g, b = int(bg_hex[1:3], 16), int(bg_hex[3:5], 16), int(bg_hex[5:7], 16)
    brightness = (r * 299 + g * 587 + b * 114) / 1000
    return "#000000" if brightness > 128 else "#FFFFFF"

# ====================== DIAMOND GRID LAYOUT ======================
# (row, col) → clock hour  (7×7 grid, diamond shape)
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

# Sensible defaults: Mercury=1, Sun=1, Moon=2, Mars=3, Venus=3, Saturn=2, Jupiter=4, Rahu=4, Ketu=1
DEFAULT_A = {"Mercury": 1, "Sun": 1, "Moon": 2, "Mars": 3,
             "Venus": 3, "Saturn": 2, "Jupiter": 4, "Rahu": 4, "Ketu": 1}

for m in modes:
    key_a, key_b = f"map_a_{m.lower()}", f"map_b_{m.lower()}"
    max_val = 2 if m == "Binary" else (3 if m == "Trivalent" else 4)
    if key_a not in st.session_state:
        st.session_state[key_a] = {p: min(DEFAULT_A[p], max_val) for p in planets_list}
    if key_b not in st.session_state:
        st.session_state[key_b] = {p: max_val for p in planets_list}

st.set_page_config(page_title="Tattva Lab v31", layout="wide")

# ====================== GLOBAL STYLING ======================
st.markdown("""
<style>
    /* Diamond grid buttons */
    .stButton button {
        height: 88px !important;               
        font-size: 36px !important;            
        font-weight: 700 !important;
        border-radius: 12px !important;
        white-space: pre-wrap !important;
        line-height: 1.15 !important;
        padding: 8px 4px !important;
    }

    .stButton button:hover {
        filter: brightness(2.25);
        transform: scale(1.50);
    }
</style>
""", unsafe_allow_html=True)


def inject_clock_colors(side, clock_config, clock_colors, selected_hours, run_id):
    """Inject CSS for colors + LARGE & BOLDER planet symbols."""
    rules = []
    for hour, cfg in clock_config.items():
        btn_key = f"{side}_{hour}"
        label   = cfg["label"]
        bg      = clock_colors[hour]
        tc      = get_text_color(bg)
        border  = "3px solid #111111" if btn_key in selected_hours else "1px solid rgba(0,0,0,0.15)"

        font_size = "36px" if " + " not in label else "28px"

        rules.append(f"""
        button[aria-label="{label}"], button[title="{label}"] {{
            background-color: {bg} !important;
            color: {tc} !important;
            border: {border} !important;
            font-size: {font_size} !important;
            font-weight: 1500 !important;
            line-height: 2.05 !important;
            letter-spacing: -1px !important;
            padding: 6px 4px !important;
            font-family: "Segoe UI Symbol", "Apple Symbols", sans-serif !important;
        }}""")

    st.markdown(f"<style>{''.join(rules)}</style>", unsafe_allow_html=True)

def get_predicted_values(selected_hours, active_map, max_val):
    """Collect unique prediction values capped at mode thresholds."""
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

                if row_cols[c - 1].button(
                    label,
                    key=f"{btn_key}_{st.session_state['run_id']}",
                    width='stretch',
                    type="primary" if is_sel else "secondary"
                ):
                    if is_sel:
                        st.session_state['selected_hours'].remove(btn_key)
                    else:
                        st.session_state['selected_hours'].append(btn_key)
                    st.rerun()
            else:
                row_cols[c - 1].empty()


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

    inject_clock_colors("L", LEFT_CLOCK,  LEFT_COLORS,  st.session_state['selected_hours'], st.session_state['run_id'])
    inject_clock_colors("R", RIGHT_CLOCK, RIGHT_COLORS, st.session_state['selected_hours'], st.session_state['run_id'])

    col_l, col_m, col_r = st.columns([4, 2, 4])

    with col_l:
        st.subheader("Left")
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
                st.write("System Prediction:")
                for v in predicted:
                    if v <= len(labels):
                        st.info(f"✨ {v}) {labels[v - 1]}")

    with col_r:
        st.subheader("Right")
        render_diamond_grid("R", RIGHT_CLOCK, st.container())

    st.divider()
    st.subheader("🎯 Log Outcome")

    # In-memory session toast feedback confirmation replacement
    if st.session_state['last_log']:
        st.success(st.session_state['last_log'])

    if not st.session_state['selected_hours']:
        st.info("Select one or more clock positions on the grids above to begin an observation.")
    else:
        selected_display = "  ·  ".join(st.session_state['selected_hours'])
        st.write(f"**Selected:** {selected_display}")

        predicted       = get_predicted_values(st.session_state['selected_hours'], current_active_map, max_val_mode)
        predicted_ints  = list(dict.fromkeys(predicted))   

        if predicted_ints:
            pred_label_str = ", ".join([f"{v}) {labels[v-1]}" for v in predicted_ints if v <= len(labels)])
            st.write(f"**System Predicts →** {pred_label_str}")

        o_cols = st.columns(len(labels))
        for i, lbl in enumerate(labels):
            if o_cols[i].button(f"{lbl}", key=f"o_{i}_{st.session_state['run_id']}",
                                width='stretch', type="primary"):
                verdict = "Right" if (i + 1) in predicted_ints else "Wrong"
                
                # Registering volatile log confirmation summary
                st.session_state['last_log'] = f"✅ Volatile Session Log Captured: **{lbl}** → Marked as **{verdict}** (Magic: {magic_num})"
                
                st.session_state['selected_hours'] = []
                st.session_state['run_id'] += 1
                st.rerun()

# ==========================================
# TAB 2 — SETTINGS
# ==========================================
with tab2:
    st.title("⚙️ Settings")
    st.info(
        "**How predictions work:** Each planet has a value per preset. When you select a clock "
        "position, the app looks up that position's planet(s) and their current preset values — "
        "those become the system's prediction. Pure hours (12, 3, 6, 9) have one planet; "
        "transitional hours have two, producing two simultaneous predictions."
    )

    m_choice    = st.radio("Configure Mapping for Mode:", modes, horizontal=True)
    max_map_val = 2 if m_choice == "Binary" else (3 if m_choice == "Trivalent" else 4)

    col_set_a, col_set_b = st.columns(2)
    with col_set_a:
        st.subheader("Preset A")
        key_a   = f"map_a_{m_choice.lower()}"
        new_map_a = {
            p: st.number_input(f"{p}", 1, max_map_val,
                               int(st.session_state[key_a].get(p, 1)),
                               key=f"s_a_{m_choice}_{p}")
            for p in planets_list
        }
        if st.button(f"💾 Save Preset A  ·  {m_choice}"):
            st.session_state[key_a] = new_map_a
            st.success("Preset A saved!")

    with col_set_b:
        st.subheader("Preset B")
        key_b   = f"map_b_{m_choice.lower()}"
        new_map_b = {
            p: st.number_input(f"{p}", 1, max_map_val,
                               int(st.session_state[key_b].get(p, max_map_val)),
                               key=f"s_b_{m_choice}_{p}")
            for p in planets_list
        }
        if st.button(f"💾 Save Preset B  ·  {m_choice}"):
            st.session_state[key_b] = new_map_b
            st.success("Preset B saved!")

    st.divider()
    st.subheader("🗺️ Clock Position Reference Table")
    st.caption("Colors and planet assignments for both grids — for reference when building presets.")

    cr1, cr2 = st.columns(2)
    with cr1:
        st.markdown("**Left Grid (Internal) — Jupiter · Venus · Mercury · Moon**")
        left_ref = [
            {
                "O'Clock": h,
                "Planets":        " + ".join(LEFT_CLOCK[h]["planets"]),
                "Default Values": str(LEFT_CLOCK[h]["ref_vals"]),
                "Hex Color":      LEFT_COLORS[h],
            }
            for h in [12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        ]
        st.dataframe(left_ref, width='stretch', hide_index=True)

    with cr2:
        st.markdown("**Right Grid (External) — Rahu · Mars · Sun · Saturn**")
        right_ref = [
            {
                "O'Clock": h,
                "Planets":        " + ".join(RIGHT_CLOCK[h]["planets"]),
                "Default Values": str(RIGHT_CLOCK[h]["ref_vals"]),
                "Hex Color":      RIGHT_COLORS[h],
            }
            for h in [12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        ]
        st.dataframe(right_ref, width='stretch', hide_index=True)

st.caption("Tattva Lab v31  •  Chronos Diamond Matrix  •  Clock-Based Spatial Logger with System Prediction (Memory Mode)")