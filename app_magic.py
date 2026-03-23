import streamlit as st
from main_page2 import scrape_magicbricks   

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="AI-Powered Real Estate Market Analysis",
    layout="wide"
)

# -------------------------------------------------
# CUSTOM CSS
# -------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif;
}

.main { 
    background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%); 
}

.block-container { 
    padding-top: 2.5rem; 
    padding-bottom: 2.5rem; 
}

.header-wrapper { 
    display: flex; 
    justify-content: center; 
    margin-bottom: 40px; 
    animation: fadeInDown 0.8s ease-out;
}

.header-box {
    background: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.5);
    padding: 40px;
    border-radius: 20px;
    width: 90%;
    max-width: 1100px;
    box-shadow: 0 8px 32px rgba(135, 142, 169, 0.15);
    text-align: center;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.header-box:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 40px rgba(135, 142, 169, 0.25);
}

.header-box h1 {
    color: #2c3e50;
    font-size: 42px;
    font-weight: 700;
    margin-bottom: 10px;
    background: linear-gradient(45deg, #ff9a9e 0%, #fecfef 99%, #fecfef 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.02);
}

.header-box p { 
    color: #5a6c7d; 
    font-size: 18px; 
    font-weight: 400;
}

.section {
    background: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.6);
    padding: 30px;
    border-radius: 20px;
    box-shadow: 0 10px 30px rgba(135, 142, 169, 0.1);
    margin-bottom: 32px;
    transition: all 0.3s ease;
    animation: fadeInUp 0.8s ease-out;
}

.section:hover {
    box-shadow: 0 15px 35px rgba(135, 142, 169, 0.15);
}

.section-title {
    font-size: 22px;
    font-weight: 600;
    color: #34495e;
    margin-bottom: 25px;
    border-bottom: 2px solid #f0f2f5;
    padding-bottom: 10px;
    display: inline-block;
}

.stButton>button {
    background: linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%);
    color: white;
    font-weight: 600;
    font-size: 16px;
    padding: 12px 35px;
    border-radius: 30px;
    border: none;
    box-shadow: 0 4px 15px rgba(161, 140, 209, 0.4);
    transition: all 0.3s ease;
}

.stButton>button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(161, 140, 209, 0.6);
    background: linear-gradient(135deg, #fbc2eb 0%, #a18cd1 100%);
}

.stButton>button:active {
    transform: translateY(1px);
}

/* LOGO POSITION */
.logo-container {
    position: absolute;
    top: 20px;
    left: 40px;
    z-index: 1000;
}

@keyframes fadeInDown {
    from { opacity: 0; transform: translateY(-20px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Metrics Styling */
div[data-testid="metric-container"] {
    background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%);
    border-radius: 15px;
    padding: 15px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    border: 1px solid rgba(255,255,255,0.8);
    transition: transform 0.2s ease;
}

div[data-testid="metric-container"]:hover {
    transform: scale(1.02);
}

div[data-testid="stMetricValue"] {
    color: #2c3e50;
    font-weight: 700;
}

div[data-testid="stMetricLabel"] {
    font-weight: 500;
    color: #7f8c8d;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# LOGO 
# -------------------------------------------------
st.markdown('<div class="logo-container">', unsafe_allow_html=True)
st.image("data_vidwan_logo.png.jpeg", width=180)   
st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------------------------
# HEADER
# -------------------------------------------------
st.markdown("""
<div class="header-wrapper">
    <div class="header-box">
        <h1>AI-Powered Web Crawler for Real Estate Analytics</h1>
        <p>Extracting, analyzing, and visualizing property market data across Gujarat</p>
    </div>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------
# CITY LIST
# -------------------------------------------------
GUJARAT_CITIES = [
    "Ahmedabad", "Surat", "Vadodara", "Rajkot",
    "Bhavnagar", "Bharuch", "Jamnagar", "Junagadh"
]

# -------------------------------------------------
# FILTER SECTION
# -------------------------------------------------
st.markdown("<div class='section'>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>Search & Filter Properties</div>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    cities = st.multiselect("Cities", GUJARAT_CITIES, default=["Ahmedabad"])

with col2:
    bhk = st.selectbox("BHK", ["Any", "1", "2", "3"], index=2)

with col3:
    furnishing = st.selectbox(
        "Furnishing",
        ["Any", "Unfurnished", "Semi-Furnished", "Fully Furnished"]
    )

st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------
# ACTION
# -------------------------------------------------
if st.button("Run Market Analysis"):

    if not cities:
        st.warning("Please select at least one city.")
        st.stop()

    bhk_value = None if bhk == "Any" else int(bhk)

    with st.spinner("Analyzing property listings..."):
        df = scrape_magicbricks(
            cities=cities,
            bhk=bhk_value,
            furnishing=furnishing,
            max_rows=900
        )

    if df.empty:
        st.warning("No listings found.")
    else:
        # -------------------------------------------------
        # SUMMARY
        # -------------------------------------------------
        st.markdown("<div class='section'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Market Summary</div>", unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        c1.metric("Listings", len(df))
        c2.metric("Avg Price (INR)", int(df["price"].mean()))
        c3.metric("Cities", df["city"].nunique())

        st.markdown("</div>", unsafe_allow_html=True)

        # -------------------------------------------------
        # TABS
        # -------------------------------------------------
        tab1, tab2 = st.tabs(
            ["Dataset", "Download"]
        )

        with tab1:
            st.dataframe(df.head(50), use_container_width=True)

        with tab2:
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download CSV",
                csv,
                "gujarat_property_data.csv",
                "text/csv"
            )

# -------------------------------------------------
# FOOTER
# -------------------------------------------------
st.markdown("""
<hr>
<p style="text-align:center; font-size:13px; color:#64748b;">
Real Estate Market Analysis | Streamlit
</p>
""", unsafe_allow_html=True)