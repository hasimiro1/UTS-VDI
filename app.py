import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Dashboard Global 2 Database", page_icon="🌍", layout="wide"
)

st.title("🌍 Dashboard Interaktif Ekonomi & Populasi Global")
st.markdown(
    "Integrasi **2 Database Berelasi** (Demografi Gapminder & Ekonomi Makro"
    " Dunia) berdasarkan relasi nama negara."
)


@st.cache_data
def load_and_merge_data():
    # Database 1: Demografi & Harapan Hidup
    url_db1 = "https://raw.githubusercontent.com/plotly/datasets/master/gapminderDataFiveYear.csv"
    df_db1 = pd.read_csv(url_db1)

    # Database 2: GDP Makro & Kode Negara (ISO-3)
    url_db2 = "https://raw.githubusercontent.com/plotly/datasets/master/2014_world_gdp_with_codes.csv"
    df_db2 = pd.read_csv(url_db2)

    # Samakan nama kolom relasi (Primary/Foreign Key)
    df_db2 = df_db2.rename(
        columns={"COUNTRY": "country", "GDP (BILLIONS)": "macro_gdp_billions"}
    )

    # Relasikan (Inner Join) kedua database
    merged_df = pd.merge(df_db1, df_db2, on="country", how="inner")
    return merged_df


df = load_and_merge_data()

# --- FILTER SIDEBAR ---
st.sidebar.header("⚙️ Filter Dashboard")
selected_year = st.sidebar.selectbox(
    "Pilih Tahun:", sorted(df["year"].unique(), reverse=True)
)
selected_continent = st.sidebar.selectbox(
    "Pilih Benua:", ["Semua Benua"] + list(df["continent"].unique())
)

filtered_df = df[df["year"] == selected_year]
if selected_continent != "Semua Benua":
    filtered_df = filtered_df[filtered_df["continent"] == selected_continent]

# --- KPI METRICS ---
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Negara", f"{filtered_df['country'].nunique()} Negara")
c2.metric("Rata-rata Harapan Hidup", f"{filtered_df['lifeExp'].mean():.1f} Thn")
c3.metric("Rata-rata PDB/Kapita", f"${filtered_df['gdpPercap'].mean():,.2f}")
c4.metric("Total Populasi", f"{filtered_df['pop'].sum() / 1_000_000:,.1f} Juta")

st.markdown("---")

# --- VISUALISASI ---
col_left, col_right = st.columns([1.2, 1])

with col_left:
    st.subheader(f"🗺️ Peta Sebaran PDB & Populasi ({selected_year})")
    fig_map = px.choropleth(
        filtered_df,
        locations="CODE",
        color="gdpPercap",
        hover_name="country",
        hover_data=["lifeExp", "pop", "macro_gdp_billions"],
        color_continuous_scale="Plasma",
    )
    fig_map.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig_map, use_container_width=True)

with col_right:
    st.subheader("📊 Korelasi PDB/Kapita vs Harapan Hidup")
    fig_scatter = px.scatter(
        filtered_df,
        x="gdpPercap",
        y="lifeExp",
        size="pop",
        color="continent",
        hover_name="country",
        log_x=True,
        size_max=45,
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

st.subheader("🏆 Top 10 Negara Berdasarkan GDP Makro (Miliar USD)")
top10 = filtered_df.sort_values(by="macro_gdp_billions", ascending=False).head(
    10
)
fig_bar = px.bar(
    top10,
    x="country",
    y="macro_gdp_billions",
    color="continent",
    text_auto=".2s",
)
st.plotly_chart(fig_bar, use_container_width=True)

with st.expander("🔍 Lihat Tabel Data Gabungan (2 Database)"):
    st.dataframe(filtered_df, use_container_width=True)