import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os, sys
import utils.weather_ai as weather_ai
from utils import weather_ai
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Coimbatore Health AI",
    page_icon="💓",
    layout="wide"
)

# ================= ULTRA MODERN UI THEME =================
st.markdown("""
<style>

/* Animated Gradient Background */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #1f1c2c, #928DAB);
    background-size: 400% 400%;
    animation: gradientBG 15s ease infinite;
}

@keyframes gradientBG {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

/* Glass Card */
.glass-card {
    background: rgba(255, 255, 255, 0.1);
    padding: 20px;
    border-radius: 20px;
    backdrop-filter: blur(15px);
    box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
    color: white;
    text-align: center;
    transition: 0.3s;
}

.glass-card:hover {
    transform: scale(1.05);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(to bottom, #141E30, #243B55);
    color: white;
}

/* Buttons */
.stButton>button {
    background: linear-gradient(to right, #ff512f, #dd2476);
    color: white;
    border-radius: 10px;
    font-weight: bold;
    height: 3em;
}

.stButton>button:hover {
    background: linear-gradient(to right, #24c6dc, #514a9d);
}

/* Titles */
h1, h2, h3 {
    color: white !important;
    text-align: center;
}

.block-container {
    padding-top: 2rem;
}

</style>
""", unsafe_allow_html=True)


# ---- PAGE CONFIG ----
st.set_page_config(page_title="Coimbatore Health AI", layout="wide")

# ---- Fix project root ----
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# ---- IMPORT CORE MODULES ----
from utils.predictor import load_model, predict
from utils.forecast import forecast_cases

# ---- OPTIONAL MODULES SAFE LOAD ----
DB_ENABLED = False
PDF_ENABLED = False
ALERT_ENABLED = False

try:
    from utils.db import init_db, insert_report
    DB_ENABLED = True
except:
    pass

try:
    from utils.pdf_report import generate_pdf
    PDF_ENABLED = True
except:
    pass

try:
    from utils.alerts import send_alert   # <-- Fast2SMS inside this
    ALERT_ENABLED = True
except:
    pass

# ---- OPTIONAL GIS ----
MAP_ENABLED = False
try:
    import folium
    from streamlit_folium import st_folium
    MAP_ENABLED = True
except:
    pass


# ================= SESSION INIT =================
if "logged" not in st.session_state:
    st.session_state.logged = False

if "alert_sent" not in st.session_state:
    st.session_state.alert_sent = False


# ================= LOGIN =================
if not st.session_state.logged:
    st.sidebar.subheader("🔐 Admin Login")
    u = st.sidebar.text_input("Username")
    p = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        if u == "admin" and p == "1234":
            st.session_state.logged = True
        else:
            st.sidebar.error("Invalid credentials")
    st.stop()


# ================= LOAD MODEL =================
model = load_model()


# ================= LOAD DATA =================
data_path = os.path.join(BASE_DIR, "data", "dataset.csv")

try:
    df = pd.read_csv(data_path)
except:
    st.error("dataset.csv not found in /data folder")
    st.stop()

uploaded = st.sidebar.file_uploader("Upload dataset", type=["csv"])
if uploaded:
    df = pd.read_csv(uploaded)

df.columns = df.columns.str.strip().str.lower()


# ================= COLUMN MAP =================
col_map = {}
for c in df.columns:
    if c in ["ward","area","zone","location"]:
        col_map["ward"]=c
    elif c in ["rainfall","rain","precipitation"]:
        col_map["rainfall"]=c
    elif c in ["ph","p_h","waterph"]:
        col_map["ph"]=c
    elif c in ["turbidity","turb","clarity"]:
        col_map["turbidity"]=c
    elif c in ["cases","patients","count","disease_cases"]:
        col_map["cases"]=c

required = ["ward","rainfall","ph","turbidity","cases"]
missing = [r for r in required if r not in col_map]

if missing:
    st.error(f"Dataset missing columns: {missing}")
    st.stop()

ward_col = col_map["ward"]
rain_col = col_map["rainfall"]
ph_col = col_map["ph"]
turb_col = col_map["turbidity"]
case_col = col_map["cases"]


# ================= TITLE =================
st.title("💧 Smart Community Health Monitoring System")
st.caption("AI Early Warning for Water-Borne Diseases")


# ================= INPUT =================
st.sidebar.header("Environmental Inputs")

ward = st.sidebar.selectbox("Ward", df[ward_col].unique())
rainfall = st.sidebar.slider("Rainfall", 0, 200, 50)
ph = st.sidebar.slider("Water pH", 5.0, 9.0, 7.0)
turbidity = st.sidebar.slider("Turbidity", 0.0, 10.0, 3.0)
cases = st.sidebar.slider("Reported Cases", 0, 30, 5)

prediction = predict(model, [rainfall, ph, turbidity, cases])

# Reset alert if not High
if prediction != "High":
    st.session_state.alert_sent = False


# ================= RISK DISPLAY =================
st.subheader("📊 Current Risk")

c1,c2,c3 = st.columns(3)
c1.metric("Rainfall", rainfall)
c2.metric("Cases", cases)
c3.metric("Risk", prediction)

if prediction=="High":
    st.error("🚨 High outbreak risk detected")
elif prediction=="Medium":
    st.warning("⚠ Moderate risk")
else:
    st.success("✅ Low risk")


# ================= FAST2SMS + EMAIL ALERT =================
if ALERT_ENABLED and prediction == "High" and not st.session_state.alert_sent:
    try:
        send_alert(ward, prediction, df, ward_col, case_col)
        st.session_state.alert_sent = True
        st.success("🚨 Email + SMS Alert Sent Successfully!")
    except Exception as e:
        st.error(f"Alert Failed: {e}")


# ================= FORECAST =================
st.markdown("---")
st.subheader("📈 7-Day Forecast")

forecast = forecast_cases(cases)
fig, ax = plt.subplots()
ax.plot(forecast, marker='o')
st.pyplot(fig)
plt.close(fig)
# ================= WEATHER AI FORECAST =================
st.markdown("---")
st.subheader("🌦 14-Day Weather AI Analysis (Live Data)")

try:
    weather_df = weather_ai.fetch_weather_data(days=14)

    # Display table
    st.dataframe(weather_df)

    # Plot rainfall forecast
    fig2, ax2 = plt.subplots()
    ax2.plot(weather_df["rainfall"], marker='o')
    ax2.set_title("14-Day Rainfall Forecast (mm)")
    ax2.set_xlabel("Day")
    ax2.set_ylabel("Rainfall (mm)")
    st.pyplot(fig2)
    plt.close(fig2)

    # Predict next day rainfall
    next_day_prediction = weather_ai.predict_next_day_rainfall(weather_df)

    st.success(f"🔮 Predicted Next-Day Rainfall: {next_day_prediction} mm")

    # AI Risk Insight
    if next_day_prediction > 20:
        st.error("⚠ Heavy rainfall expected — Possible water contamination risk")
    elif next_day_prediction > 5:
        st.warning("Moderate rainfall expected")
    else:
        st.info("Low rainfall expected")

except Exception as e:
    st.error(f"Weather API Error: {e}")


# ================= DATABASE =================
if DB_ENABLED:
    if st.button("Save Report"):
        init_db()
        insert_report((ward,rainfall,ph,turbidity,cases,prediction))
        st.success("Saved")


# ================= DOWNLOAD CSV =================
st.download_button(
    "Download Dataset",
    df.to_csv(index=False),
    file_name="report.csv"
)