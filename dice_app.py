# -*- coding: utf-8 -*-
"""
dice_app.py
-----------
Streamlit application for the DICE model.
Run with:  streamlit run dice_app.py
"""

import numpy as np
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from cpydicemodel import cdicemodel

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DICE Model Explorer",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Styles ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-title {font-size:2rem; font-weight:700; color:#1a3a5c; margin-bottom:0;}
    .subtitle   {font-size:1rem; color:#555; margin-bottom:1.5rem;}
    .metric-box {background:#f0f4f8; border-radius:8px; padding:12px 16px; text-align:center;}
    .metric-val {font-size:1.6rem; font-weight:700; color:#1a3a5c;}
    .metric-lbl {font-size:0.78rem; color:#666; margin-top:2px;}
    .section-hdr{font-size:1rem; font-weight:600; color:#1a3a5c;
                 border-bottom:2px solid #d0dce8; padding-bottom:4px; margin-top:1rem;}
    [data-testid="stSidebar"] {background:#f7f9fc;}
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<p class="main-title">🌍 DICE Model Explorer</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle">Dynamic Integrated Climate-Economy model · Nordhaus (2017) · '
    'Adjust the parameters in the sidebar and press <b>Run</b>.</p>',
    unsafe_allow_html=True,
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Scenario parameters")

    # Time horizon
    st.markdown('<p class="section-hdr">Time horizon</p>', unsafe_allow_html=True)
    col_y1, col_y2 = st.columns(2)
    with col_y1:
        initial_year = st.number_input("Initial year", 2020, 2050, 2023, step=1)
    with col_y2:
        end_year = st.number_input("Final year", 2050, 2200, 2100, step=5)

    # Emissions
    st.markdown('<p class="section-hdr">Initial emissions (GtCO₂)</p>', unsafe_allow_html=True)
    industrial_em = st.slider("Industrial emissions", 20.0, 60.0, 37.0, 0.5)
    land_em       = st.slider("Land-use emissions",    0.5, 10.0,  3.3, 0.1)
    em_intensity  = st.slider("Emission intensity",   0.05, 0.80, 0.27, 0.01,
                               help="GtCO₂ per trillion USD of output")

    # Economy
    st.markdown('<p class="section-hdr">Economy</p>', unsafe_allow_html=True)
    population  = st.slider("Initial population (billions)", 5.0, 10.0, 7.8, 0.1)
    capital     = st.slider("Initial capital (trillion USD 2010)", 100.0, 600.0, 318.8, 5.0)
    tfp         = st.slider("Initial TFP", 2.0, 12.0, 5.276, 0.1,
                             help="Total Factor Productivity")
    saving_rate = st.slider("Saving rate", 0.10, 0.40, 0.20, 0.01)

    # Climate policy
    st.markdown('<p class="section-hdr">Abatement policy</p>', unsafe_allow_html=True)
    abatement_0 = st.slider("Initial abatement rate (μ₀)", 0.0, 0.10, 0.001, 0.001,
                             format="%.3f")
    abatement_g = st.slider("Annual μ growth", 0.00, 1.00, 0.25, 0.01,
                             help="How fast the abatement rate grows each year")

    run_btn = st.button("▶  Run model", type="primary", use_container_width=True)

# ── Model execution ───────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def run_model(iy, ey, ie, le, ei, pop, cap, tfp_, ar0, arg, sr):
    m = cdicemodel(
        initial_year=iy,
        end_year=ey,
        industrial_emissions_initial_value=ie,
        land_emissions_initial_value=le,
        emission_intensity_initial_value=ei,
        population_initial_value=pop,
        capital_initial_value=cap,
        tfp_initial_value=tfp_,
        abatement_rate_initial_value=ar0,
        abatement_rate_growth=arg,
        saving_rate=sr,
    )
    m.run()
    return m.df_output.copy(), m.df_carbon_concentration.copy(), m.df_temperature.copy()


if "results" not in st.session_state or run_btn:
    with st.spinner("Running DICE model…"):
        df, df_cc, df_t = run_model(
            initial_year, end_year,
            industrial_em, land_em, em_intensity,
            population, capital, tfp,
            abatement_0, abatement_g, saving_rate,
        )
    st.session_state["results"] = (df, df_cc, df_t)

df, df_cc, df_t = st.session_state["results"]

# ── KPIs ──────────────────────────────────────────────────────────────────────
yr_end = df.index[-1]

def fmt(val, dec=2):
    return f"{val:.{dec}f}" if pd.notna(val) else "—"

kpis = [
    ("🌡️ Final T_AT (°C)",          fmt(df.loc[yr_end, "T_AT"]),                    "Atmospheric temp. above pre-industrial"),
    ("💨 Final emissions",           fmt(df.loc[yr_end, "total_emissions"]) + " GtCO₂", "Final year total"),
    ("📈 Final net output (Q)",      fmt(df.loc[yr_end, "Q"]) + " T$",                "Net production (trillion USD 2010)"),
    ("🔧 Final abatement rate (μ)",  fmt(df.loc[yr_end, "mu"], 3),                    "Fraction of emissions abated"),
    ("🌲 Final atmospheric carbon",  fmt(df_cc.loc[yr_end, "CC_AT"]) + " GtC",        "Atmospheric carbon concentration"),
    ("⚖️ Cumulative utility",        fmt(df.loc[yr_end, "U"], 0),                     "Discounted social welfare"),
]

cols = st.columns(len(kpis))
for col, (lbl, val, tip) in zip(cols, kpis):
    with col:
        st.markdown(
            f'<div class="metric-box" title="{tip}">'
            f'<div class="metric-val">{val}</div>'
            f'<div class="metric-lbl">{lbl}</div></div>',
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)

# ── Charts ────────────────────────────────────────────────────────────────────
PALETTE = {
    "blue":   "#2a6496",
    "green":  "#2e7d5e",
    "red":    "#c0392b",
    "orange": "#d68910",
    "purple": "#6c3483",
    "gray":   "#555",
    "teal":   "#117a8b",
}

def base_fig(title, yaxis_title, xaxis_title="Year"):
    fig = go.Figure()
    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color="#1a3a5c")),
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=10, r=10, t=40, b=30),
        legend=dict(orientation="h", y=-0.2),
        font=dict(family="sans-serif", size=12),
        hovermode="x unified",
    )
    fig.update_xaxes(showgrid=True, gridcolor="#eee", zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="#eee", zeroline=False)
    return fig

idx = df.index.tolist()

tab1, tab2, tab3 = st.tabs(["🌡️ Climate", "💰 Economy", "💨 Emissions"])

with tab1:
    c1, c2 = st.columns(2)

    with c1:
        fig = base_fig("Atmospheric temperature (T_AT)", "°C above pre-industrial")
        fig.add_trace(go.Scatter(x=idx, y=df["T_AT"], mode="lines",
                                 name="T_AT", line=dict(color=PALETTE["red"], width=2.5)))
        fig.add_hrect(y0=1.5, y1=2.0, fillcolor="orange", opacity=0.08,
                      annotation_text="Paris Agreement range 1.5–2°C",
                      annotation_position="top left")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig = base_fig("Carbon concentration", "GtC")
        for col, color, name in zip(
            ["CC_AT", "CC_UP", "CC_LO"],
            [PALETTE["blue"], PALETTE["teal"], PALETTE["gray"]],
            ["Atmosphere", "Upper ocean", "Deep ocean"],
        ):
            fig.add_trace(go.Scatter(x=idx, y=df_cc[col], mode="lines",
                                     name=name, line=dict(color=color, width=2)))
        st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        fig = base_fig("Ocean temperature (T_LO)", "°C")
        fig.add_trace(go.Scatter(x=idx, y=df_t["T_LO"], mode="lines",
                                 name="T_LO", line=dict(color=PALETTE["teal"], width=2.5)))
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        pi_1, pi_2 = 0.001, 2.67e-3
        damage_pct = (pi_1 * df["T_AT"] + pi_2 * df["T_AT"] ** 2) * 100
        fig = base_fig("Climate damage cost (% of gross output)", "% GDP")
        fig.add_trace(go.Scatter(x=idx, y=damage_pct, mode="lines",
                                 name="Damage", line=dict(color=PALETTE["orange"], width=2.5),
                                 fill="tozeroy", fillcolor="rgba(214,137,16,0.08)"))
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    c1, c2 = st.columns(2)

    with c1:
        fig = base_fig("Gross output (Y) and net output (Q)", "Trillion USD 2010")
        fig.add_trace(go.Scatter(x=idx, y=df["Y"], mode="lines", name="Y (gross)",
                                 line=dict(color=PALETTE["blue"], width=2, dash="dot")))
        fig.add_trace(go.Scatter(x=idx, y=df["Q"], mode="lines", name="Q (net)",
                                 line=dict(color=PALETTE["green"], width=2.5)))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig = base_fig("Capital (K) and Investment (I)", "Trillion USD 2010")
        fig.add_trace(go.Scatter(x=idx, y=df["K"], mode="lines", name="K",
                                 line=dict(color=PALETTE["blue"], width=2.5)))
        fig.add_trace(go.Scatter(x=idx, y=df["I"], mode="lines", name="I",
                                 line=dict(color=PALETTE["purple"], width=2),
                                 yaxis="y2"))
        fig.update_layout(
            yaxis2=dict(title="Investment (T$)", overlaying="y", side="right", showgrid=False),
        )
        st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        fig = base_fig("Population (L) and TFP (A)", "Billions / index")
        fig.add_trace(go.Scatter(x=idx, y=df["L"], mode="lines", name="Population (L)",
                                 line=dict(color=PALETTE["green"], width=2.5)))
        fig.add_trace(go.Scatter(x=idx, y=df["A"], mode="lines", name="TFP (A)",
                                 line=dict(color=PALETTE["orange"], width=2), yaxis="y2"))
        fig.update_layout(yaxis2=dict(title="TFP", overlaying="y", side="right", showgrid=False))
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        fig = base_fig("Cumulative social utility (U)", "Welfare")
        fig.add_trace(go.Scatter(x=idx, y=df["U"], mode="lines", name="U",
                                 line=dict(color=PALETTE["purple"], width=2.5),
                                 fill="tozeroy", fillcolor="rgba(108,52,131,0.07)"))
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    c1, c2 = st.columns(2)

    with c1:
        fig = base_fig("Total, industrial and land-use emissions", "GtCO₂")
        for col, color, name in zip(
            ["total_emissions", "industrial_emissions", "land_emissions"],
            [PALETTE["gray"], PALETTE["blue"], PALETTE["green"]],
            ["Total", "Industrial", "Land-use"],
        ):
            fig.add_trace(go.Scatter(x=idx, y=df[col], mode="lines",
                                     name=name, line=dict(color=color, width=2)))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig = base_fig("Abatement rate (μ) and emission intensity", "Fraction / index")
        fig.add_trace(go.Scatter(x=idx, y=df["mu"], mode="lines", name="μ (abatement)",
                                 line=dict(color=PALETTE["red"], width=2.5)))
        fig.add_trace(go.Scatter(x=idx, y=df["emission_intensity"], mode="lines",
                                 name="Emission intensity",
                                 line=dict(color=PALETTE["teal"], width=2), yaxis="y2"))
        fig.update_layout(yaxis2=dict(title="Intensity", overlaying="y", side="right", showgrid=False))
        st.plotly_chart(fig, use_container_width=True)

# ── Data table ────────────────────────────────────────────────────────────────
with st.expander("📋 View full results table"):
    show_cols = ["Y", "Q", "K", "I", "L", "A",
                 "T_AT", "total_emissions", "industrial_emissions",
                 "land_emissions", "mu", "emission_intensity", "U"]
    st.dataframe(
        df[show_cols].round(4),
        use_container_width=True,
        height=300,
    )
    csv = df[show_cols].to_csv().encode("utf-8")
    st.download_button("⬇ Download CSV", csv, "dice_results.csv", "text/csv")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption(
    "Based on the DICE model by William Nordhaus (Nobel Prize in Economics, 2018). "
    "Python implementation — calibration parameters are defined in dice_config.py."
)
