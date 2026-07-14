import streamlit as st
import pandas as pd
import io
import plotly.express as px

st.set_page_config(
    page_title="Dashboard Genre Film Netflix",
    page_icon="🎬",
    layout="wide"
)

st.markdown("""
<style>

.block-container{

    padding-top:2rem;
    padding-left:2rem;
    padding-right:2rem;
    background:#f4f8fc;

}

h1,h2,h3{

    color:#143d7a;
    font-weight:bold;

}

div[data-testid="metric-container"]{

    background:white;

    border-radius:18px;

    padding:20px;

    box-shadow:0px 6px 20px rgba(0,0,0,.08);

    border-left:6px solid #2563eb;

}

div[data-testid="stDataFrame"]{

    background:white;

    border-radius:20px;

}

</style>

""",unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_excel("Book1.xlsx")

    df.columns = df.columns.str.strip()

    df["genre"] = df["genre"].astype(str).str.strip()

    df["rating(imdb)"] = pd.to_numeric(df["rating(imdb)"], errors="coerce")
    df["Ditonton sebanyak"] = pd.to_numeric(
        df["Ditonton sebanyak"], errors="coerce"
    )

    return df

genre_color = {
    "Action": "#2563EB",
    "Animation": "#F59E0B",
    "Comedy": "#10B981",
    "Drama": "#EF4444",
    "Documentary": "#8B5CF6",
    "Adventure": "#06B6D4",
    "Thriller": "#F97316",
    "Horror": "#111827",
    "Crime": "#EC4899"
}
df = load_data()

with st.spinner("Memuat Dashboard..."):
    df = load_data()

st.sidebar.title("Filter Data")

tahun = st.sidebar.multiselect(
    "Pilih Tahun",
    sorted(df["Tahun"].unique()),
    default=sorted(df["Tahun"].unique())
)
genre = st.sidebar.multiselect(
    "Pilih Genre",
    sorted(df["genre"].unique()),
    default=sorted(df["genre"].unique())
)
df = df[
    (df["Tahun"].isin(tahun)) &
    (df["genre"].isin(genre))
]
st.success(
    f"""
Menampilkan **{len(df)} film**
dengan **{df['genre'].nunique()} genre**
untuk tahun **{', '.join(map(str,tahun))}**
"""
)
tahun_text = ", ".join(map(str, tahun))

st.title(f"🎬 Dashboard Genre Film Netflix ({tahun_text})")

st.caption(
    "Periode 2023–2025 | Berdasarkan Hours Viewed dan IMDb Rating"
)
st.info(f"""
### 📌 Informasi Dataset

- Total Film : **{total_film}**
- Total Genre : **{total_genre}**
- Tahun : **{tahun_text}**
- IMDb Rata-rata : **{avg_rating}**

""")
total_film = len(df)
total_genre = df["genre"].nunique()
avg_rating = round(df["rating(imdb)"].mean(),2)
total_hours = df["Ditonton sebanyak"].sum()
c1,c2,c3,c4 = st.columns(4)
c1.metric(
    "Total Film",
    f"{total_film}"
)
c2.metric(
    "Jumlah Genre",
    f"{total_genre}"
)
c3.metric(
    "Rata-rata IMDb",
    avg_rating
)
c4.metric(
    "Hours Viewed",
    f"{total_hours:,.0f}"
)
st.markdown("---")
col1, col2 = st.columns(2)
genre_count = (
    df.groupby("genre")
      .size()
      .reset_index(name="Jumlah Film")
      .sort_values("Jumlah Film", ascending=False)
)
fig_bar = px.bar(
    genre_count,
    x="genre",
    y="Jumlah Film",
    text="Jumlah Film",
    color="genre",
    color_discrete_map=genre_color,
    title=f"Distribusi Genre Film Netflix ({min(tahun)}–{max(tahun)})"
)
fig_bar.update_layout(
    showlegend=False,
    xaxis_title="Genre",
    yaxis_title="Jumlah Film",
    title_x=0.5
)
with col1:

    st.container(border=True)

    st.plotly_chart(
        fig_bar,
        use_container_width=True
    )

fig_pie = px.pie(

    genre_count,

    names="genre",

    values="Jumlah Film",

    color="genre",

    color_discrete_map=genre_color,

    title=f"Proporsi Genre Film Netflix ({min(tahun)}–{max(tahun)})"

)
fig_pie.update_traces(

hovertemplate=

"%{label}<br>%{percent}"

)
fig_pie.update_traces(

    textposition="inside",

    textinfo="percent+value"

)

fig_pie.update_layout(
    title_x=0.5
)

with col2:

    st.container(border=True)

    st.plotly_chart(
        fig_pie,
        use_container_width=True
    )
st.markdown("---")

trend = (
    df.groupby("Tahun")
      .size()
      .reset_index(name="Jumlah Film")
)

fig_line = px.line(

    trend,

    x="Tahun",

    y="Jumlah Film",

    markers=True,

    title="Tren Genre Film Netflix"

)

fig_line.update_traces(

    line_width=4,

    marker_size=10

)
fig_line.update_layout(
    title_x=0.5
)

st.plotly_chart(fig_line, use_container_width=True)

st.markdown("---")

total_film = len(df)
total_genre = df["genre"].nunique()
avg_rating = round(df["rating(imdb)"].mean(), 2)
total_hours = df["Ditonton sebanyak"].sum()

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.info("🎬 Total Film")
    st.metric("", total_film)

with c2:
    st.success("🎭 Total Genre")
    st.metric("", total_genre)

with c3:
    st.warning("⭐ Rata-rata IMDb")
    st.metric("", avg_rating)

with c4:
    st.error("👁 Hours Viewed")
    st.metric("", f"{total_hours:,.0f}")

csv = df.to_csv(index=False).encode("utf-8")

st.download_button(

    label="📥 Download Dataset Hasil Filter",

    data=csv,

    file_name="dataset_filter.csv",

    mime="text/csv"

)
buffer = io.BytesIO()

with pd.ExcelWriter(buffer) as writer:

    df.to_excel(
        writer,
        index=False
    )

st.download_button(

    label="📥 Download Excel",

    data=buffer.getvalue(),

    file_name="NetflixDashboard.xlsx",

    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

)
fig_bar.update_layout(

    height=430,

    template="plotly_white"

)

fig_pie.update_layout(

    height=430,

    template="plotly_white"

)

fig_line.update_layout(

    height=430,

    template="plotly_white"

)
fig_bar.update_traces(

    hovertemplate=

    "<b>%{x}</b><br>Jumlah Film : %{y}"

)
fig_line.update_traces(

hovertemplate=

"Tahun %{x}<br>%{y} Film"

)
