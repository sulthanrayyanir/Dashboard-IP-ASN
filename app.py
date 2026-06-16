import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from io import BytesIO

st.set_page_config(
    page_title="Dashboard IP ASN Kemenkes",
    page_icon="📊",
    layout="wide"
)

# =====================
# SESSION STATE
# =====================

if "selected_pegawai" not in st.session_state:
    st.session_state.selected_pegawai = None

if "selected_jabatan" not in st.session_state:
    st.session_state.selected_jabatan = None

if "target_ip" not in st.session_state:
    st.session_state.target_ip = 84.0

st.sidebar.header("Target Institusi")

st.session_state.target_ip = st.sidebar.number_input(
    "Target IP Institusi",
    min_value=0.0,
    max_value=100.0,
    value=float(st.session_state.target_ip),
    step=0.1
)

TARGET_IP = st.session_state.target_ip

MAX_KUALIFIKASI = 25
MAX_KOMPETENSI = 40
MAX_KINERJA = 30
MAX_DISIPLIN = 5

st.title("📊 Dashboard Analisis IP ASN Kemenkes")

uploaded_file = st.file_uploader(
    "Upload File PIP ASN",
    type=["xlsx"]
)

if uploaded_file is not None:

    df = pd.read_excel(
        uploaded_file,
        header=6
    )

    df = df.dropna(
        subset=["Nama"]
    )

    df["Kualifikasi"] = pd.to_numeric(df["Kualifikasi"])
    df["Kompetensi"] = pd.to_numeric(df["Kompetensi"])
    df["Kinerja"] = pd.to_numeric(df["Kinerja"])
    df["Disiplin"] = pd.to_numeric(df["Disiplin"])
    df["Total"] = pd.to_numeric(df["Total"])

    # =========================
    # POTENSI
    # =========================

    df["Potensi Kualifikasi"] = (
        MAX_KUALIFIKASI - df["Kualifikasi"]
    )

    df["Potensi Kompetensi"] = (
        MAX_KOMPETENSI - df["Kompetensi"]
    )

    df["Potensi Kinerja"] = (
        MAX_KINERJA - df["Kinerja"]
    )

    df["Potensi Disiplin"] = (
        MAX_DISIPLIN - df["Disiplin"]
    )

    df["Potensi Total"] = (
        df["Potensi Kualifikasi"]
        + df["Potensi Kompetensi"]
        + df["Potensi Kinerja"]
        + df["Potensi Disiplin"]
    )

    df["IP Potensial"] = (
        df["Total"]
        + df["Potensi Total"]
    ).clip(upper=100)

    df["Gap Target"] = (
        TARGET_IP - df["Total"]
    )

    df["Priority Score"] = (
        df["Gap Target"].clip(lower=0)
        + df["Potensi Total"]
    )

    # =========================
    # KPI
    # =========================

    ip_inst = round(
        df["Total"].mean(),
        2
    )

    prediksi_maks = round(
        df["IP Potensial"].mean(),
        2
    )

    gap = round(
        TARGET_IP - ip_inst,
        2
    )

    prioritas = len(
        df[df["Total"] < TARGET_IP]
    )

    capaian = round(
    ip_inst / TARGET_IP * 100,
    2
    )

    col1,col2,col3,col4 = st.columns(4)

    col1.metric(
        "IP Institusi",
        ip_inst
    )

    col2.metric(
        "Target",
        TARGET_IP
    )

    col3.metric(
        "Gap",
        gap
    )

    col4.metric(
        "Jumlah Pegawai",
        len(df)
    )

    col5,col6,col7,col8 = st.columns(4)

    col5.metric(
        "Pegawai Prioritas",
        prioritas
    )

    col6.metric(
        "Prediksi Maksimum",
        prediksi_maks
    )

    col7.metric(
        "Capaian Target",
        f"{capaian}%"
    )

    col8.metric(
        "Potensi Kenaikan",
        round(prediksi_maks-ip_inst,2)
    )

    st.divider()

    # =========================
    # FILTER
    # =========================

    st.sidebar.header("Filter")

    jabatan = st.sidebar.multiselect(
        "Jabatan",
        sorted(df["Nama Jabatan"].unique())
    )

    satker = st.sidebar.multiselect(
        "Satuan Kerja",
        sorted(df["Satuan Kerja"].unique())
    )

    if jabatan:
        df = df[
            df["Nama Jabatan"].isin(jabatan)
        ]

    if satker:
        df = df[
            df["Satuan Kerja"].isin(satker)
        ]

    if df.empty:

        st.warning(
            "Tidak ada data yang sesuai dengan filter."
        )

        st.stop()

    if (
        st.session_state.selected_jabatan is not None
        and
        st.session_state.selected_jabatan not in df["Nama Jabatan"].values
    ):

        st.session_state.selected_jabatan = None

    if (
        st.session_state.selected_pegawai is not None
        and
        st.session_state.selected_pegawai not in df["Nama"].values
    ):

        st.session_state.selected_pegawai = None

    prioritas_df = (
        df[df["Total"] < TARGET_IP]
        .sort_values(
            "Priority Score",
            ascending=False
        )
        .copy()
    )

    # =========================
    # DISTRIBUSI IP
    # =========================

    st.subheader(
        "Distribusi Nilai IP ASN"
    )

    fig = px.histogram(
        df,
        x="Total",
        nbins=20
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        key="distribusi_ip_chart"
    )

    # =========================
    # ANALISIS PEGAWAI
    # =========================

    st.header(
        "Analisis Individu"
    )

    pegawai_options = df

    if st.session_state.selected_jabatan:

        pegawai_options = pegawai_options[
            pegawai_options["Nama Jabatan"]
            ==
            st.session_state.selected_jabatan
        ]

    pegawai_list = pegawai_options["Nama"].tolist()

    default_idx = 0

    if (
        st.session_state.selected_pegawai is not None
        and
        st.session_state.selected_pegawai in pegawai_list
    ):
        default_idx = pegawai_list.index(
            st.session_state.selected_pegawai
        )

    pegawai = st.selectbox(
        "Pilih Pegawai",
        pegawai_list,
        index=default_idx
    )

    st.session_state.selected_pegawai = pegawai

    p = df[
        df["Nama"] == pegawai
    ].iloc[0]

    a,b,c,d,e = st.columns(5)

    a.metric(
        "Kualifikasi",
        round(p["Kualifikasi"],2)
    )

    b.metric(
        "Kompetensi",
        round(p["Kompetensi"],2)
    )

    c.metric(
        "Kinerja",
        round(p["Kinerja"],2)
    )

    d.metric(
        "Disiplin",
        round(p["Disiplin"],2)
    )

    e.metric(
        "Total",
        round(p["Total"],2)
    )

    potensi = pd.DataFrame({
        "Komponen":[
            "Kualifikasi",
            "Kompetensi",
            "Kinerja",
            "Disiplin"
        ],
        "Saat Ini":[
            p["Kualifikasi"],
            p["Kompetensi"],
            p["Kinerja"],
            p["Disiplin"]
        ],
        "Maksimum":[25,40,30,5]
    })

    potensi["Potensi"] = (
        potensi["Maksimum"]
        - potensi["Saat Ini"]
    )

    potensi["Persentase Potensi"] = (
    potensi["Potensi"] /
    potensi["Maksimum"] * 100
    )

    def warna_potensi(val):

        if val >= 60:
            return "background-color:#ff4d4d;color:black"

        elif val >= 30:
            return "background-color:#ffb84d;color:black"

        elif val >= 10:
            return "background-color:#ffff99;color:black"

        return "background-color:#b7ffb7;color:black"
    
    potensi["Persentase Potensi"] = (
    potensi["Potensi"]
    /
    potensi["Maksimum"]
    * 100
    )   

    potensi = potensi.sort_values(
        "Potensi",
        ascending=False
    )

    st.dataframe(
        potensi,
        column_config={
            "Persentase Potensi":
            st.column_config.ProgressColumn(
                "Persentase Potensi",
                min_value=0,
                max_value=100,
                format="%.1f%%"
            )
        },
        use_container_width=True
    )

    # =========================
    # PRIORITAS PEGAWAI
    # =========================

    if st.session_state.selected_jabatan:

        st.info(
            f"Filter Jabatan Aktif : {st.session_state.selected_jabatan}"
        )

        if st.button(
            "Reset Filter Jabatan"
        ):
            st.session_state.selected_jabatan = None
            st.rerun()

    st.header(
        "Pegawai Prioritas"
    )

    filtered_prioritas = prioritas_df

    if st.session_state.selected_jabatan:

        filtered_prioritas = filtered_prioritas[
            filtered_prioritas["Nama Jabatan"]
            ==
            st.session_state.selected_jabatan
        ]

    st.write(
        "Klik baris pegawai untuk membuka Analisis Individu"
    )

    event = st.dataframe(
        filtered_prioritas[
            [
                "Nama",
                "Nama Jabatan",
                "Total",
                "Gap Target",
                "Priority Score"
            ]
        ],
        use_container_width=True,
        on_select="rerun",
        selection_mode="single-row"
    )

    if len(event.selection.rows):

        selected_row = event.selection.rows[0]

        selected_pegawai = filtered_prioritas.iloc[selected_row]["Nama"]

        if st.session_state.selected_pegawai != selected_pegawai:

            st.session_state.selected_pegawai = selected_pegawai

            st.rerun()

    # =========================
    # ANALISIS JABATAN
    # =========================

    st.header(
        "Analisis Jabatan"
    )

    jabatan_df = (
        df.groupby(
            "Nama Jabatan"
        )
        .agg(
            Jumlah=("Nama","count"),
            Rata_IP=("Total","mean"),
            Dibawah_Target=("Total",
            lambda x:(x<TARGET_IP).sum()),
            Potensi=("Potensi Total","sum")
        )
        .reset_index()
    )

    jabatan_df["Dampak Institusi"] = (
        jabatan_df["Potensi"]
        /
        len(df)
    )

    filtered_jabatan_df = jabatan_df

    if st.session_state.selected_jabatan:

        filtered_jabatan_df = filtered_jabatan_df[
            filtered_jabatan_df["Nama Jabatan"]
            ==
            st.session_state.selected_jabatan
        ]

    st.write(
        "Klik baris jabatan untuk memfilter Pegawai Prioritas"
    )

    event_jabatan = st.dataframe(
        filtered_jabatan_df,
        use_container_width=True,
        on_select="rerun",
        selection_mode="single-row"
    )

    if len(event_jabatan.selection.rows):

        selected_row = event_jabatan.selection.rows[0]

        selected_jabatan = filtered_jabatan_df.iloc[selected_row]["Nama Jabatan"]

        if st.session_state.selected_jabatan != selected_jabatan:

            st.session_state.selected_jabatan = selected_jabatan

            st.rerun()

    fig2 = px.bar(
        filtered_jabatan_df,
        x="Nama Jabatan",
        y="Dampak Institusi"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True,
        key="dampak_institusi_chart"
    )

    # =========================
    # HEATMAP
    # =========================

    st.header(
        "Heatmap Prioritas Jabatan"
    )

    def kategori(x):

        if x >= 1:
            return "🔴 Sangat Tinggi"

        elif x >= 0.5:
            return "🟠 Tinggi"

        elif x >= 0.2:
            return "🟡 Sedang"

        return "🟢 Rendah"

    jabatan_df["Prioritas"] = (
        jabatan_df["Dampak Institusi"]
        .apply(kategori)
    )

    filtered_jabatan_df = jabatan_df

    if st.session_state.selected_jabatan:

        filtered_jabatan_df = filtered_jabatan_df[
            filtered_jabatan_df["Nama Jabatan"]
            ==
            st.session_state.selected_jabatan
        ]

    st.write(
        "Klik baris jabatan untuk memfilter Pegawai Prioritas"
    )

    event_heatmap = st.dataframe(
        filtered_jabatan_df[
            [
                "Nama Jabatan",
                "Jumlah",
                "Rata_IP",
                "Prioritas"
            ]
        ],
        use_container_width=True,
        on_select="rerun",
        selection_mode="single-row"
    )

    if len(event_heatmap.selection.rows):

        selected_row = event_heatmap.selection.rows[0]

        selected_jabatan = filtered_jabatan_df.iloc[selected_row]["Nama Jabatan"]

        if st.session_state.selected_jabatan != selected_jabatan:

            st.session_state.selected_jabatan = selected_jabatan

            st.rerun()

    # =========================
    # OPTIMIZER TARGET 84
    # =========================

    st.header(
        "Target Achievement Optimizer"
    )

    st.info(
    f"Target Optimizer mengikuti Target Institusi : {TARGET_IP}"
    )

    kandidat = (
        df[df["Total"] < TARGET_IP]
        .sort_values(
            "Potensi Total",
            ascending=False
        )
        .copy()
    )

    if st.session_state.selected_jabatan:

        kandidat = kandidat[
            kandidat["Nama Jabatan"]
            ==
            st.session_state.selected_jabatan
        ]

    simulasi = df["Total"].copy()

    current_mean = simulasi.mean()

    selected = []

    for _, row in kandidat.iterrows():

        if current_mean >= TARGET_IP:
            break

        idx = row.name

        simulasi.loc[idx] = min(
            100,
            row["IP Potensial"]
        )

        current_mean = simulasi.mean()

        selected.append(row)

    hasil = pd.DataFrame(selected)

    st.metric(
        "Prediksi IP Institusi",
        round(current_mean,2)
    )

    if current_mean >= TARGET_IP:
        st.success(
            f"Target {TARGET_IP} dapat dicapai"
        )
    else:
        st.warning(
            f"Target {TARGET_IP} belum dapat dicapai meskipun seluruh kandidat ditingkatkan"
        )

    if not hasil.empty:

        st.dataframe(
            hasil[
                [
                    "Nama",
                    "Nama Jabatan",
                    "Total",
                    "IP Potensial"
                ]
            ],
            use_container_width=True
        )

    # =========================
    # EXPORT
    # =========================

    st.header(
        "Export Data"
    )

    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="xlsxwriter"
    ) as writer:

        prioritas_df.to_excel(
            writer,
            sheet_name="Prioritas Pegawai",
            index=False
        )

        jabatan_df.to_excel(
            writer,
            sheet_name="Prioritas Jabatan",
            index=False
        )

    st.download_button(
        label="Download Hasil Analisis",
        data=output.getvalue(),
        file_name="hasil_analisis_ip_asn.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:

    st.info(
        "Upload file PIP ASN terlebih dahulu."
    )
