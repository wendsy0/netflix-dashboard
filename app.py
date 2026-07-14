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
.block-container {
    padding-top: 2rem;
    padding-left: 2rem;
    padding-right: 2rem;
    background: #f4f8fc;
}
h1, h2, h3 {
    color: #143d7a;
    font-weight: bold;
}
div[data-testid="metric-container"] {
    background: white;
    border-radius: 18px;
    padding: 20px;
    box-shadow: 0px 6px 20px rgba(0,0,0,.08);
    border-left: 6px solid #2563eb;
}
div[data-testid="stDataFrame"] {
    background: white;
    border-radius: 20px;
}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    df = pd.read_excel("Book1.xlsx")
    df.columns = df.columns.str.strip()
    df["genre"] = df["genre"].astype(str).str.strip()
    df["rating(imdb)"] = pd.to_numeric(
        df["rating(imdb)"].astype(str).str.replace("/10", "").str.strip(),
        errors="coerce"
    )
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

df_raw = load_data()

# ── SIDEBAR FILTERS ──────────────────────────────────────────
st.sidebar.title("Filter Data")

semua_tahun = sorted(df_raw["Tahun"].dropna().unique())
tahun_dipilih = st.sidebar.multiselect(
    "Pilih Tahun",
    semua_tahun,
    default=semua_tahun
)

semua_genre = sorted(df_raw["genre"].dropna().unique())
genre_dipilih = st.sidebar.multiselect(
    "Pilih Genre",
    semua_genre,
    default=semua_genre
)

# ── FILTER DATA ───────────────────────────────────────────────
df = df_raw[
    (df_raw["Tahun"].isin(tahun_dipilih)) &
    (df_raw["genre"].isin(genre_dipilih))
].copy()

# ── HITUNG METRIK ────────────────────────────────────────────
total_film   = len(df)
total_genre  = df["genre"].nunique()
avg_rating   = round(df["rating(imdb)"].mean(), 2) if total_film > 0 else 0
total_hours  = df["Ditonton sebanyak"].sum()

# ── JUDUL DINAMIS ────────────────────────────────────────────
if tahun_dipilih:
    tahun_min = min(tahun_dipilih)
    tahun_max = max(tahun_dipilih)
    if tahun_min == tahun_max:
        tahun_label = str(tahun_min)
    else:
        tahun_label = f"{tahun_min}–{tahun_max}"
else:
    tahun_label = "Semua Tahun"

st.title(f"🎬 Dashboard Genre Film Netflix ({tahun_label})")
st.caption("Berdasarkan Hours Viewed dan IMDb Rating | Data: Netflix Tudum & IMDb")

# ── STATUS BAR ───────────────────────────────────────────────
if total_film > 0:
    tahun_text = ", ".join(map(str, sorted(tahun_dipilih)))
    st.success(
        f"Menampilkan **{total_film} film** dengan "
        f"**{total_genre} genre** untuk tahun **{tahun_text}**"
    )
else:
    st.warning("Tidak ada data untuk filter yang dipilih.")

# ── INFO DATASET ─────────────────────────────────────────────
with st.expander("📌 Informasi Dataset", expanded=False):
    st.markdown(f"""
| Keterangan | Nilai |
|---|---|
| Total Film | **{total_film}** |
| Total Genre | **{total_genre}** |
| Tahun | **{tahun_label}** |
| IMDb Rata-rata | **{avg_rating}** |
""")

# ── METRIK CARDS ─────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("🎬 Total Film",      f"{total_film:,}")
c2.metric("🎭 Jumlah Genre",    f"{total_genre}")
c3.metric("⭐ Rata-rata IMDb",  f"{avg_rating}")
c4.metric("👁 Hours Viewed",    f"{total_hours:,.0f}")

st.markdown("---")

if total_film == 0:
    st.info("Tidak ada data yang sesuai filter. Silakan ubah filter di sidebar.")
    st.stop()

# ── BARIS 1: BAR CHART + PIE CHART ───────────────────────────
col1, col2 = st.columns(2)

genre_count = (
    df.groupby("genre")
      .size()
      .reset_index(name="Total Konten")
      .sort_values("Total Konten", ascending=False)
)

fig_bar = px.bar(
    genre_count,
    x="genre",
    y="Total Konten",
    text="Total Konten",
    color="genre",
    color_discrete_map=genre_color,
    title=f"Distribusi Genre Film Netflix ({tahun_label})"
)
fig_bar.update_layout(
    showlegend=False,
    xaxis_title="Genre",
    yaxis_title="Jumlah Film",
    title_x=0.5,
    height=430,
    template="plotly_white"
)
fig_bar.update_traces(
    hovertemplate="<b>%{x}</b><br>Jumlah Film: %{y}"
)

with col1:
    st.plotly_chart(fig_bar, use_container_width=True)

fig_pie = px.pie(
    genre_count,
    names="genre",
    values="Total Konten",
    color="genre",
    color_discrete_map=genre_color,
    title=f"Proporsi Genre Film Netflix ({tahun_label})"
)
fig_pie.update_traces(
    textposition="inside",
    textinfo="percent+value",
    hovertemplate="%{label}<br>%{percent}"
)
fig_pie.update_layout(
    title_x=0.5,
    height=430,
    template="plotly_white"
)

with col2:
    st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")

# ── BARIS 2: LINE CHART TREN ─────────────────────────────────
trend = (
    df.groupby(["Tahun", "genre"])
      .size()
      .reset_index(name="Jumlah Film")
)

fig_line = px.line(
    trend,
    x="Tahun",
    y="Jumlah Film",
    color="genre",
    color_discrete_map=genre_color,
    markers=True,
    title=f"Tren Genre Film Netflix ({tahun_label})"
)
fig_line.update_traces(
    line_width=3,
    marker_size=8,
    hovertemplate="Tahun %{x}<br>%{y} Film"
)
fig_line.update_layout(
    title_x=0.5,
    height=430,
    template="plotly_white",
    xaxis=dict(tickmode="linear", dtick=1),
    xaxis_title="Tahun",
    yaxis_title="Jumlah Film"
)

st.plotly_chart(fig_line, use_container_width=True)

st.markdown("---")

# ── BARIS 3: TOP 5 PER GENRE ─────────────────────────────────
st.subheader(f"🏆 Top 5 Film per Genre ({tahun_label})")

genre_list = sorted(df["genre"].unique())
tab_list   = st.tabs(genre_list)

for tab, g in zip(tab_list, genre_list):
    with tab:
        top5 = (
            df[df["genre"] == g]
            .sort_values("Ditonton sebanyak", ascending=False)
            .head(5)[["judul", "genre", "Tahun", "rating(imdb)", "Ditonton sebanyak"]]
            .rename(columns={
                "judul": "Judul",
                "genre": "Genre",
                "Tahun": "Tahun",
                "rating(imdb)": "IMDb Rating",
                "Ditonton sebanyak": "Hours Viewed"
            })
            .reset_index(drop=True)
        )
        top5.index = top5.index + 1
        top5["Hours Viewed"] = top5["Hours Viewed"].apply(
            lambda x: f"{x:,.0f}" if pd.notna(x) else "-"
        )
        st.dataframe(top5, use_container_width=True)

st.markdown("---")

# ── DOWNLOAD SECTION ─────────────────────────────────────────
st.subheader("📥 Download Data")

col_dl1, col_dl2 = st.columns(2)

csv = df.to_csv(index=False).encode("utf-8")
with col_dl1:
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name=f"netflix_genre_{tahun_label}.csv",
        mime="text/csv"
    )

buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
    df.to_excel(writer, index=False)

with col_dl2:
    st.download_button(
        label="📥 Download Excel",
        data=buffer.getvalue(),
        file_name=f"netflix_genre_{tahun_label}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )