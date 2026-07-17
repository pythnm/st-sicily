import streamlit as st
import pandas as pd
import pydeck as pdk
from io import StringIO

# Page configuration
st.set_page_config(
    page_title="Sicily Holiday Trip 2026",
    page_icon="🏖️",
    layout="wide"
)

# CSS styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #FF6B35;
        text-align: center;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #004E89;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">🇮🇹 Sicily Holiday Trip 2026 🏖️</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Milano → Sicilia → Milano | 19 Luglio - 8 Agosto</p>', unsafe_allow_html=True)

# --- DATA ---
csv_data = """DATA;DA;A;KM;TEMPO;NOTTE
domenica 19 luglio 2026;MILANO;TERRANUOVA BRACCIOLINI;346;3H31';1
lunedì 20 luglio 2026;TERRANUOVA BR.;NAPOLI PORTO;432;4 H 16';traghetto
martedì 21 luglio 2026;PALERMO;SAN VITO LO CAPO;109;1h 43';3
mercoledì 22 luglio 2026;;SAN VITO LO CAPO;;;
giovedì 23 luglio 2026;;SAN VITO LO CAPO;;;
venerdì 24 luglio 2026;SAN VITO;ERICE - MARSALA;89;1h 09';1
sabato 25 luglio 2026;MARSALA;LIDO ROSSELLO;125;1h 53';2
domenica 26 luglio 2026;;LIDO ROSSELLO;;;
lunedì 27 luglio 2026;LIDO ROSSELLO;AGRIGENTO - RAGUSA IBLA;155;2h 47';1
martedì 28 luglio 2026;RAGUSA IBLA;MARZAMEMI;60;57';2
mercoledì 29 luglio 2026;;MARZAMEMI;;;
giovedì 30 luglio 2026;MARZAMEMI;NOTO;24;31';1
venerdì 31 luglio 2026;NOTO;SIRACUSA;39;34';2
sabato 1 agosto 2026;;SIRACUSA;;;
domenica 2 agosto 2026;SIRACUSA;CATANIA - ETNA;99;1h 47';1
lunedì 3 agosto 2026;ETNA;TAORMINA - GOLE ALCANTARA - CEFALU;237;4h 27';3
martedì 4 agosto 2026;;CEFALU;;;
mercoledì 5 agosto 2026;;CEFALU;;;
giovedì 6 agosto 2026;CEFALU;PALERMO;70;1h 00';traghetto
venerdì 7 agosto 2026;NAPOLI;FIRENZE;473;4 H 48';1
sabato 8 agosto 2026;FIRENZE;MILANO;318;3H23';
"""

# ✅ COORDINATES
COORDINATES = {
    "MILANO": {"lat": 45.4642, "lon": 9.1900},
    "TERRANUOVA BRACCIOLINI": {"lat": 43.5500, "lon": 11.5833},
    "TERRANUOVA BR.": {"lat": 43.5500, "lon": 11.5833},
    "NAPOLI PORTO": {"lat": 40.8397, "lon": 14.2679},
    "NAPOLI": {"lat": 40.8397, "lon": 14.2679},
    "PALERMO PORTO": {"lat": 38.1253, "lon": 13.3588},
    "PALERMO": {"lat": 38.1157, "lon": 13.3615},
    "SAN VITO LO CAPO": {"lat": 38.1747, "lon": 12.7339},
    "SAN VITO": {"lat": 38.1747, "lon": 12.7339},
    "ERICE": {"lat": 38.0372, "lon": 12.5872},
    "ERICE - MARSALA": {"lat": 37.7986, "lon": 12.4372},
    "MARSALA": {"lat": 37.7986, "lon": 12.4372},
    "LIDO ROSSELLO": {"lat": 37.3897, "lon": 13.4890},
    "AGRIGENTO": {"lat": 37.3111, "lon": 13.5766},
    "AGRIGENTO - RAGUSA IBLA": {"lat": 36.9269, "lon": 14.7325},
    "RAGUSA IBLA": {"lat": 36.9269, "lon": 14.7325},
    "MARZAMEMI": {"lat": 36.7414, "lon": 15.1167},
    "NOTO": {"lat": 36.8900, "lon": 15.0700},
    "SIRACUSA": {"lat": 37.0755, "lon": 15.2866},
    "CATANIA": {"lat": 37.5079, "lon": 15.0830},
    "CATANIA - ETNA": {"lat": 37.5079, "lon": 15.0830},
    "ETNA": {"lat": 37.7510, "lon": 14.9934},
    "TAORMINA": {"lat": 37.8526, "lon": 15.2853},
    "GOLE ALCANTARA": {"lat": 37.8967, "lon": 15.1600},
    "TAORMINA - GOLE ALCANTARA - CEFALU": {"lat": 38.0336, "lon": 14.0228},
    "CEFALU": {"lat": 38.0336, "lon": 14.0228},
    "FIRENZE": {"lat": 43.7696, "lon": 11.2558},
}

# ✅ LEGS TO EXCLUDE FROM MAP (return journey)
MAP_EXCLUDED_LEGS = [
    ("CEFALU", "PALERMO"),       # return ferry start
    ("PALERMO PORTO", "NAPOLI PORTO"),  # return ferry sea
    ("NAPOLI", "FIRENZE"),       # return road
    ("FIRENZE", "MILANO"),       # return road
]

# Load data
df = pd.read_csv(StringIO(csv_data), sep=";")

# --- SIDEBAR ---
st.sidebar.header("🗺️ Trip Navigation")
st.sidebar.markdown("---")

total_km = pd.to_numeric(df['KM'], errors='coerce').sum()
total_days = len(df)
travel_days = df[df['DA'].notna() & (df['DA'] != '')].shape[0]

st.sidebar.metric("📅 Total Days", total_days)
st.sidebar.metric("🚗 Travel Days", travel_days)
st.sidebar.metric("📏 Total KM", f"{int(total_km):,}")

st.sidebar.markdown("---")
st.sidebar.header("🔍 Filter")

selected_day = st.sidebar.selectbox(
    "Select a specific day:",
    ["All days"] + df['DATA'].tolist()
)

# --- MAIN CONTENT ---
tab1, tab2, tab3 = st.tabs(["📋 Itinerary Table", "🗺️ Interactive Map", "📊 Trip Stats"])

# --- TAB 1: TABLE (unchanged, shows everything) ---
with tab1:
    st.subheader("📋 Complete Itinerary")

    if selected_day == "All days":
        display_df = df.copy()
    else:
        display_df = df[df['DATA'] == selected_day].copy()

    def highlight_rows(row):
        if row.get('NOTTE') == 'traghetto':
            return ['background-color: #1565C0; color: #FFFFFF; font-weight: bold'] * len(row)
        elif pd.isna(row.get('DA')) or row.get('DA') == '':
            return ['background-color: #2E7D32; color: #FFFFFF; font-weight: bold'] * len(row)
        else:
            return ['background-color: #E65100; color: #FFFFFF; font-weight: bold'] * len(row)

    styled_df = display_df.style.apply(highlight_rows, axis=1).format(
        {"KM": lambda x: str(int(x)) if pd.notna(x) and x != '' else ''}
    )
    st.dataframe(styled_df, use_container_width=True, height=600)

    st.markdown("""
    **Legend:**
    - 🟠 **Orange**: Travel day
    - 🟢 **Green**: Rest/Stay day
    - 🔵 **Blue**: Ferry crossing
    """)

# --- TAB 2: MAP (Sicily + outward journey only) ---
with tab2:
    st.subheader("🗺️ Trip Route on Map - Sicily & Outward Journey")

    # ✅ STOPS: only locations NOT in return journey
    RETURN_STOPS = {"NAPOLI", "FIRENZE"}  # exclude these from map stops

    stops = []
    seen = set()

    # Fixed stop list for map - outward + Sicily only
    MAP_STOPS_ORDER = [
        "MILANO",
        "TERRANUOVA BR.",
        "NAPOLI PORTO",
        "PALERMO",
        "SAN VITO LO CAPO",
        "ERICE - MARSALA",
        "MARSALA",
        "LIDO ROSSELLO",
        "AGRIGENTO - RAGUSA IBLA",
        "RAGUSA IBLA",
        "MARZAMEMI",
        "NOTO",
        "SIRACUSA",
        "CATANIA - ETNA",
        "ETNA",
        "TAORMINA",
        "GOLE ALCANTARA",
        "CEFALU",
        "PALERMO PORTO",  # end of Sicily leg
    ]

    DISPLAY_NAMES = {
        "MILANO": "Milano 🏠",
        "TERRANUOVA BR.": "Terranuova Br.",
        "NAPOLI PORTO": "Napoli Porto 🚢",
        "PALERMO": "Palermo 🚢",
        "PALERMO PORTO": "Palermo Porto 🚢",
        "SAN VITO LO CAPO": "San Vito Lo Capo 🏖️",
        "ERICE - MARSALA": "Erice / Marsala",
        "MARSALA": "Marsala 🍷",
        "LIDO ROSSELLO": "Lido Rossello 🏖️",
        "AGRIGENTO - RAGUSA IBLA": "Agrigento / Ragusa Ibla",
        "RAGUSA IBLA": "Ragusa Ibla",
        "MARZAMEMI": "Marzamemi 🐟",
        "NOTO": "Noto",
        "SIRACUSA": "Siracusa",
        "CATANIA - ETNA": "Catania / Etna 🌋",
        "ETNA": "Etna 🌋",
        "TAORMINA": "Taormina",
        "GOLE ALCANTARA": "Gole Alcantara",
        "CEFALU": "Cefalù 🏖️",
    }

    for loc in MAP_STOPS_ORDER:
        if loc in COORDINATES:
            stops.append({
                "name": DISPLAY_NAMES.get(loc, loc),
                "lat": COORDINATES[loc]["lat"],
                "lon": COORDINATES[loc]["lon"],
            })

    stops_df = pd.DataFrame(stops)

    # ✅ ROUTE LINES: outward + Sicily only, NO return legs
    route_lines = []

    def add_segment(from_key, to_key, is_ferry=False, label=""):
        if from_key in COORDINATES and to_key in COORDINATES:
            route_lines.append({
                "start_lat": COORDINATES[from_key]["lat"],
                "start_lon": COORDINATES[from_key]["lon"],
                "end_lat": COORDINATES[to_key]["lat"],
                "end_lon": COORDINATES[to_key]["lon"],
                "name": label or f"{from_key} → {to_key}",
                "color": [0, 120, 255] if is_ferry else [255, 107, 53],
                "width": 5 if is_ferry else 3,
            })

    # ✅ Outward road: Milano → Terranuova → Napoli Porto
    add_segment("MILANO", "TERRANUOVA BR.", False, "Milano → Terranuova Br.")
    add_segment("TERRANUOVA BR.", "NAPOLI PORTO", False, "Terranuova → Napoli Porto")

    # ✅ Outward ferry: Napoli → Palermo
    add_segment("NAPOLI PORTO", "PALERMO PORTO", True, "⛴️ Traghetto: Napoli → Palermo")

    # ✅ Sicily road legs
    add_segment("PALERMO", "SAN VITO LO CAPO", False, "Palermo → San Vito Lo Capo")
    add_segment("SAN VITO LO CAPO", "ERICE - MARSALA", False, "San Vito → Erice/Marsala")
    add_segment("ERICE - MARSALA", "LIDO ROSSELLO", False, "Marsala → Lido Rossello")
    add_segment("LIDO ROSSELLO", "AGRIGENTO - RAGUSA IBLA", False, "Lido Rossello → Agrigento/Ragusa")
    add_segment("AGRIGENTO - RAGUSA IBLA", "MARZAMEMI", False, "Ragusa → Marzamemi")
    add_segment("MARZAMEMI", "NOTO", False, "Marzamemi → Noto")
    add_segment("NOTO", "SIRACUSA", False, "Noto → Siracusa")
    add_segment("SIRACUSA", "CATANIA - ETNA", False, "Siracusa → Catania/Etna")

    # ✅ Multi-stop: Etna → Taormina → Gole Alcantara → Cefalù
    add_segment("ETNA", "TAORMINA", False, "Etna → Taormina")
    add_segment("TAORMINA", "GOLE ALCANTARA", False, "Taormina → Gole Alcantara")
    add_segment("GOLE ALCANTARA", "CEFALU", False, "Gole Alcantara → Cefalù")

    # ✅ Cefalù → Palermo Porto (end of Sicily, board return ferry - shown as road)
    add_segment("CEFALU", "PALERMO PORTO", False, "Cefalù → Palermo Porto")

    # ❌ NO return ferry, NO Napoli→Firenze, NO Firenze→Milano

    routes_df = pd.DataFrame(route_lines)

    # Map controls
    col1, col2 = st.columns([1, 3])

    with col1:
        map_style = st.radio(
            "Map Style:",
            ["Road", "Voyager", "Dark"],
            index=0
        )

        map_styles = {
            "Road": "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
            "Voyager": "https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json",
            "Dark": "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json"
        }

        show_labels = st.checkbox("Show labels", value=True)
        show_routes = st.checkbox("Show routes", value=True)

        st.markdown("---")
        st.markdown("""
        **Legend:**
        - 🟠 Orange lines: Road
        - 🔵 Blue lines: Ferry ⛴️
        - 🔴 Dots: Stops
        """)

    with col2:
        layers = []

        # Stops
        layers.append(
            pdk.Layer(
                "ScatterplotLayer",
                data=stops_df,
                get_position=["lon", "lat"],
                get_radius=7000,
                get_fill_color=[220, 60, 30, 220],
                pickable=True,
                auto_highlight=True,
            )
        )

        # Labels
        if show_labels:
            layers.append(
                pdk.Layer(
                    "TextLayer",
                    data=stops_df,
                    get_position=["lon", "lat"],
                    get_text="name",
                    get_size=13,
                    get_color=[20, 20, 20, 255],
                    get_pixel_offset=[0, -18],
                    get_text_anchor="'middle'",
                    get_alignment_baseline="'bottom'",
                )
            )

        # Routes
        if show_routes and len(routes_df) > 0:
            layers.append(
                pdk.Layer(
                    "LineLayer",
                    data=routes_df,
                    get_source_position=["start_lon", "start_lat"],
                    get_target_position=["end_lon", "end_lat"],
                    get_color="color",
                    get_width="width",
                    pickable=True,
                )
            )

        # ✅ Map centered on Italy to show both Milano and Sicily
        view_state = pdk.ViewState(
            latitude=39.5,
            longitude=14.5,
            zoom=5.5,
            pitch=0,
        )

        deck = pdk.Deck(
            layers=layers,
            initial_view_state=view_state,
            map_style=map_styles[map_style],
            tooltip={
                "text": "{name}",
                "style": {
                    "backgroundColor": "white",
                    "color": "black",
                    "fontSize": "13px",
                    "padding": "6px 10px",
                    "borderRadius": "4px"
                }
            }
        )

        st.pydeck_chart(deck, use_container_width=True)

# --- TAB 3: STATS ---
with tab3:
    st.subheader("📊 Trip Statistics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("📅 Total Days", total_days)
    with col2:
        st.metric("🚗 Travel Days", travel_days)
    with col3:
        rest_days = total_days - travel_days
        st.metric("🏖️ Rest Days", rest_days)
    with col4:
        st.metric("📏 Total Distance", f"{int(total_km)} km")

    st.markdown("---")

    st.subheader("🏨 Accommodation Stays")

    stays = []
    current_location = None
    nights = 0

    for _, row in df.iterrows():
        dest = row['A'] if pd.notna(row['A']) and row['A'] != '' else None
        notte = row['NOTTE'] if pd.notna(row['NOTTE']) and row['NOTTE'] != '' else None

        if dest:
            if current_location and nights > 0:
                stays.append({"Location": current_location, "Nights": nights})
            current_location = dest
            try:
                nights = int(notte) if notte and notte != 'traghetto' else 0
            except (ValueError, TypeError):
                nights = 0

    if current_location and nights > 0:
        stays.append({"Location": current_location, "Nights": nights})

    stays_df = pd.DataFrame(stays)
    if not stays_df.empty:
        st.bar_chart(stays_df.set_index("Location")["Nights"])
        st.dataframe(stays_df, use_container_width=True)

    st.markdown("---")

    st.subheader("📏 Daily Distances (km)")

    travel_data = df[df['KM'].notna() & (df['KM'] != '')].copy()
    travel_data['KM_numeric'] = pd.to_numeric(travel_data['KM'], errors='coerce').astype('Int64')
    travel_data = travel_data[travel_data['KM_numeric'].notna()]

    if not travel_data.empty:
        chart_data = travel_data[['DATA', 'KM_numeric']].set_index('DATA')
        st.bar_chart(chart_data)

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: gray;'>🇮🇹 Sicily Trip Planner 2026 | "
    "Milano → Sicilia → Milano</p>",
    unsafe_allow_html=True
)