from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


BASE_DIR = Path(__file__).parent
MAIN_DATA = BASE_DIR / "ai_data.csv"
GDP_DATA = BASE_DIR / "dataset" / "gdp_per_capita.csv"
INTERNET_DATA = BASE_DIR / "dataset" / "internet_usage.csv"
AI_PUBLICATIONS_DATA = BASE_DIR / "dataset" / "ai_publications_owid.csv"
AI_PATENTS_DATA = BASE_DIR / "dataset" / "ai_patents_per_million_owid.csv"
AI_INVESTMENT_DATA = BASE_DIR / "dataset" / "ai_private_investment_owid.csv"

AI_METRICS = {
    "Overall AI Score": "ai_overall_score",
    "Talent": "ai_talent",
    "Infrastructure": "ai_infrastructure",
    "Operating Environment": "ai_operating_environment",
    "Research": "ai_research",
    "Development": "ai_development",
    "Government Strategy": "ai_government_strategy",
    "Commercial": "ai_commercial",
}

AI_DIMENSIONS = {label: col for label, col in AI_METRICS.items() if col != "ai_overall_score"}

MAP_PROJECTIONS = {
    "Interactive Globe": "orthographic",
    "Flat World Map": "natural earth",
    "Mercator Zoom Map": "mercator",
}

QUADRANT_COLORS = {
    "Higher GDP - Higher AI": "#1D9E75",
    "Lower GDP - Higher AI": "#378ADD",
    "Higher GDP - Lower AI": "#EF9F27",
    "Lower GDP - Lower AI": "#D4537E",
}

PREDICTOR_FEATURES = [
    "hdi",
    "internet_usage_pct",
    "gdp_per_capita",
    "ai_talent",
    "ai_infrastructure",
    "ai_operating_environment",
    "ai_research",
    "ai_development",
    "ai_government_strategy",
    "ai_commercial",
]

TREND_SOURCES = {
    "AI Publications": {
        "path": AI_PUBLICATIONS_DATA,
        "value_col": "ai_publications",
        "label": "AI scholarly publications",
        "source_note": "OWID/CSET, annual scholarly publications related to AI.",
        "format": "count",
    },
    "AI Patents per Million": {
        "path": AI_PATENTS_DATA,
        "value_col": "ai_patents_per_million",
        "label": "AI patent applications per million people",
        "source_note": "OWID/CSET, AI-related patent applications per million people.",
        "format": "decimal",
    },
    "Private AI Investment": {
        "path": AI_INVESTMENT_DATA,
        "value_col": "ai_private_investment",
        "label": "Private AI investment, constant 2021 US$",
        "source_note": "OWID/CSET, estimated funding raised by privately held AI companies.",
        "format": "money",
    },
    "GDP per Capita": {
        "value_col": "gdp_per_capita",
        "label": "GDP per capita",
        "source_note": "World Bank WDI, supporting economic context.",
        "format": "money",
    },
    "Internet Usage": {
        "value_col": "internet_usage_pct",
        "label": "Internet usage (%)",
        "source_note": "World Bank WDI, supporting digital access context.",
        "format": "percent",
    },
}

PLOTLY_TEMPLATE = "plotly_white"

COUNTRY_ISO3 = {
    "Algeria": "DZA",
    "Argentina": "ARG",
    "Armenia": "ARM",
    "Australia": "AUS",
    "Austria": "AUT",
    "Azerbaijan": "AZE",
    "Bahrain": "BHR",
    "Bangladesh": "BGD",
    "Belgium": "BEL",
    "Benin": "BEN",
    "Brazil": "BRA",
    "Bulgaria": "BGR",
    "Canada": "CAN",
    "Chile": "CHL",
    "China": "CHN",
    "Colombia": "COL",
    "Croatia": "HRV",
    "Czech Republic": "CZE",
    "Denmark": "DNK",
    "Egypt": "EGY",
    "Estonia": "EST",
    "Ethiopia": "ETH",
    "Finland": "FIN",
    "France": "FRA",
    "Germany": "DEU",
    "Ghana": "GHA",
    "Greece": "GRC",
    "Hungary": "HUN",
    "Iceland": "ISL",
    "India": "IND",
    "Indonesia": "IDN",
    "Iran": "IRN",
    "Iraq": "IRQ",
    "Ireland": "IRL",
    "Israel": "ISR",
    "Italy": "ITA",
    "Japan": "JPN",
    "Jordan": "JOR",
    "Kenya": "KEN",
    "Latvia": "LVA",
    "Lithuania": "LTU",
    "Luxembourg": "LUX",
    "Malaysia": "MYS",
    "Malta": "MLT",
    "Mauritius": "MUS",
    "Mexico": "MEX",
    "Morocco": "MAR",
    "New Zealand": "NZL",
    "Nigeria": "NGA",
    "Norway": "NOR",
    "Oman": "OMN",
    "Pakistan": "PAK",
    "Peru": "PER",
    "Philippines": "PHL",
    "Poland": "POL",
    "Portugal": "PRT",
    "Qatar": "QAT",
    "Romania": "ROU",
    "Russia": "RUS",
    "Rwanda": "RWA",
    "Saudi Arabia": "SAU",
    "Serbia": "SRB",
    "Singapore": "SGP",
    "Slovakia": "SVK",
    "Slovenia": "SVN",
    "South Africa": "ZAF",
    "South Korea": "KOR",
    "Spain": "ESP",
    "Sri Lanka": "LKA",
    "Sweden": "SWE",
    "Switzerland": "CHE",
    "Thailand": "THA",
    "Tunisia": "TUN",
    "Turkey": "TUR",
    "Ukraine": "UKR",
    "United Arab Emirates": "ARE",
    "United Kingdom": "GBR",
    "United States": "USA",
    "Uruguay": "URY",
    "Vietnam": "VNM",
}


st.set_page_config(
    page_title="Global AI Readiness Dashboard",
    layout="wide",
)

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1.6rem;
            padding-bottom: 2rem;
        }
        div[data-testid="stMetric"] {
            border: 1px solid #e4e7ec;
            border-radius: 8px;
            min-height: 112px;
            padding: 14px 16px;
            background: var(--secondary-background-color);
            box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        div[data-testid="stMetricLabel"] {
            font-size: 0.82rem;
            color: var(--text-color); 
            opacity: 0.65;
            line-height: 1.25;
        }
    
        div[data-testid="stMetricValue"] {
            font-size: 1.45rem;
            line-height: 1.2;
            color: var(--text-color); 
        
        }
        div[data-testid="stMetricDelta"] {
            line-height: 1.25;
        }
        div[data-testid="stAlert"] {
            min-height: 108px;
            border-radius: 8px;
            display: flex;
            align-items: center;
        }
        div[data-testid="stAlert"] > div {
            width: 100%;
        }
        .profile-card {
            min-height: 150px;
            border: 1px solid #e4e7ec;
            border-radius: 8px;
            padding: 14px 16px;
            background: var(--secondary-background-color);
            box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            gap: 10px;
        }
        .profile-card-title {
            color: var(--text-color);
            font-size: 0.92rem;
            font-weight: 700;
            line-height: 1.25;
            margin-bottom: 2px;
        }
        .profile-card-score {
            color: var(--text-color);
            font-size: 1.55rem;
            font-weight: 700;
            line-height: 1.1;
        }
        .profile-card-rank {
            color: var(--text-color); 
            font-size: 0.78rem;
            line-height: 1.25;
        }
        .profile-card-detail {
            color: var(--text-color); 
            font-size: 0.78rem;
            line-height: 1.35;
            margin-top: 2px;
        }
        .insight-card {
            min-height: 148px;
            border-radius: 8px;
            padding: 16px 18px;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        .insight-card-label {
            font-size: 0.90rem;
            font-weight: 800;
            text-transform: uppercase;
            margin-bottom: 4px;
            opacity: 0.75;
        }
        .insight-card-title {
            font-size: 1.35rem;
            font-weight: 600;
            margin-bottom: 6px;
            line-height: 1.25;
        }
        .insight-card-body {
            font-size: 0.82rem;
            line-height: 1.55;
            opacity: 0.9;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_ai_data() -> pd.DataFrame:
    df = pd.read_csv(MAIN_DATA)
    df["iso_alpha"] = df["country"].map(COUNTRY_ISO3)
    numeric_cols = [
        "ai_overall_score",
        "ai_talent",
        "ai_infrastructure",
        "ai_operating_environment",
        "ai_research",
        "ai_development",
        "ai_government_strategy",
        "ai_commercial",
        "hdi",
        "expected_years_of_schooling",
        "mean_years_of_schooling",
        "internet_usage_pct",
        "gdp_per_capita",
        "rank_ai_overall",
        "rank_hdi",
        "rank_internet",
        "rank_gdp_per_capita",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["is_top10_ai"] = df["is_top10_ai"].astype(str).str.lower().eq("true")
    df["ai_group"] = df["is_top10_ai"].map({True: "Top 10 AI", False: "Other Countries"})
    df["internet_usage_size"] = df["internet_usage_pct"].fillna(df["internet_usage_pct"].median())
    df["internet_usage_size"] = df["internet_usage_size"].fillna(50).clip(lower=1)
    df["gdp_display"] = df["gdp_per_capita"].map(lambda x: f"${x:,.0f}" if pd.notna(x) else "-")
    df["hdi_level"] = pd.cut(
        df["hdi"],
        bins=[0, 0.55, 0.70, 0.80, 1.0],
        labels=["Low", "Medium", "High", "Very High"],
        include_lowest=True,
    )
    df["internet_level"] = pd.cut(
        df["internet_usage_pct"],
        bins=[0, 50, 75, 90, 100],
        labels=["<50%", "50-75%", "75-90%", ">90%"],
        include_lowest=True,
    )
    df["foundation_score"] = (
        df["hdi"].fillna(df["hdi"].median()) * 100 * 0.45
        + df["internet_usage_pct"].fillna(df["internet_usage_pct"].median()) * 0.35
        + (df["gdp_per_capita"].fillna(df["gdp_per_capita"].median()).rank(pct=True) * 100) * 0.20
    )
    df["readiness_gap"] = df["ai_overall_score"] - df["foundation_score"]

    if "region" not in df.columns:
        REGION_MAP = {
            # East Asia & Pacific
            "Australia": "East Asia & Pacific",
            "China": "East Asia & Pacific",
            "Hong Kong": "East Asia & Pacific",
            "Indonesia": "East Asia & Pacific",
            "Japan": "East Asia & Pacific",
            "Malaysia": "East Asia & Pacific",
            "Myanmar": "East Asia & Pacific",
            "New Zealand": "East Asia & Pacific",
            "Philippines": "East Asia & Pacific",
            "Singapore": "East Asia & Pacific",
            "South Korea": "East Asia & Pacific",
            "Taiwan": "East Asia & Pacific",
            "Thailand": "East Asia & Pacific",
            "Vietnam": "East Asia & Pacific",
            "Cambodia": "East Asia & Pacific",
            "Mongolia": "East Asia & Pacific",
            "Papua New Guinea": "East Asia & Pacific",
            "Sri Lanka": "East Asia & Pacific",
            # South Asia
            "Bangladesh": "South Asia",
            "India": "South Asia",
            "Nepal": "South Asia",
            "Pakistan": "South Asia",
            # Europe & Central Asia
            "Austria": "Europe & Central Asia",
            "Belgium": "Europe & Central Asia",
            "Czech Republic": "Europe & Central Asia",
            "Denmark": "Europe & Central Asia",
            "Estonia": "Europe & Central Asia",
            "Finland": "Europe & Central Asia",
            "France": "Europe & Central Asia",
            "Germany": "Europe & Central Asia",
            "Greece": "Europe & Central Asia",
            "Hungary": "Europe & Central Asia",
            "Iceland": "Europe & Central Asia",
            "Ireland": "Europe & Central Asia",
            "Italy": "Europe & Central Asia",
            "Kazakhstan": "Europe & Central Asia",
            "Lithuania": "Europe & Central Asia",
            "Luxembourg": "Europe & Central Asia",
            "Netherlands": "Europe & Central Asia",
            "Norway": "Europe & Central Asia",
            "Poland": "Europe & Central Asia",
            "Portugal": "Europe & Central Asia",
            "Romania": "Europe & Central Asia",
            "Russia": "Europe & Central Asia",
            "Slovenia": "Europe & Central Asia",
            "Spain": "Europe & Central Asia",
            "Sweden": "Europe & Central Asia",
            "Switzerland": "Europe & Central Asia",
            "Turkey": "Europe & Central Asia",
            "Ukraine": "Europe & Central Asia",
            "United Kingdom": "Europe & Central Asia",
            # Middle East & North Africa
            "Algeria": "Middle East & North Africa",
            "Bahrain": "Middle East & North Africa",
            "Egypt": "Middle East & North Africa",
            "Iran": "Middle East & North Africa",
            "Iraq": "Middle East & North Africa",
            "Israel": "Middle East & North Africa",
            "Jordan": "Middle East & North Africa",
            "Kuwait": "Middle East & North Africa",
            "Lebanon": "Middle East & North Africa",
            "Morocco": "Middle East & North Africa",
            "Oman": "Middle East & North Africa",
            "Qatar": "Middle East & North Africa",
            "Saudi Arabia": "Middle East & North Africa",
            "Tunisia": "Middle East & North Africa",
            "United Arab Emirates": "Middle East & North Africa",
            # North America
            "Canada": "North America",
            "Mexico": "North America",
            "United States": "North America",
            # Latin America & Caribbean
            "Argentina": "Latin America & Caribbean",
            "Bolivia": "Latin America & Caribbean",
            "Brazil": "Latin America & Caribbean",
            "Chile": "Latin America & Caribbean",
            "Colombia": "Latin America & Caribbean",
            "Costa Rica": "Latin America & Caribbean",
            "Ecuador": "Latin America & Caribbean",
            "Guatemala": "Latin America & Caribbean",
            "Panama": "Latin America & Caribbean",
            "Peru": "Latin America & Caribbean",
            "Uruguay": "Latin America & Caribbean",
            "Venezuela": "Latin America & Caribbean",
            # Sub-Saharan Africa
            "Angola": "Sub-Saharan Africa",
            "Benin": "Sub-Saharan Africa",
            "Botswana": "Sub-Saharan Africa",
            "Cameroon": "Sub-Saharan Africa",
            "Cote d'Ivoire": "Sub-Saharan Africa",
            "Ethiopia": "Sub-Saharan Africa",
            "Ghana": "Sub-Saharan Africa",
            "Kenya": "Sub-Saharan Africa",
            "Mauritius": "Sub-Saharan Africa",
            "Mozambique": "Sub-Saharan Africa",
            "Nigeria": "Sub-Saharan Africa",
            "Rwanda": "Sub-Saharan Africa",
            "Senegal": "Sub-Saharan Africa",
            "South Africa": "Sub-Saharan Africa",
            "Tanzania": "Sub-Saharan Africa",
            "Uganda": "Sub-Saharan Africa",
            "Zambia": "Sub-Saharan Africa",
            "Zimbabwe": "Sub-Saharan Africa",
        }
        df["region"] = df["country"].map(REGION_MAP).fillna("Other")
 
    return df


@st.cache_data
def load_world_bank_timeseries(path: Path, value_name: str) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=["country", "year", value_name])

    wide = pd.read_csv(path, skiprows=4)
    year_cols = [col for col in wide.columns if str(col).isdigit()]
    long = wide.melt(
        id_vars=["Country Name", "Country Code"],
        value_vars=year_cols,
        var_name="year",
        value_name=value_name,
    )
    long = long.rename(columns={"Country Name": "country", "Country Code": "country_code"})
    long["year"] = pd.to_numeric(long["year"], errors="coerce")
    long[value_name] = pd.to_numeric(long[value_name], errors="coerce")
    return long.dropna(subset=["year", value_name])


@st.cache_data
def load_owid_timeseries(path: Path, value_name: str) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=["country", "country_code", "year", value_name])

    raw = pd.read_csv(path)
    value_candidates = [col for col in raw.columns if col not in {"Entity", "Code", "Year"}]
    if not value_candidates:
        return pd.DataFrame(columns=["country", "country_code", "year", value_name])

    value_source = value_candidates[0]
    data = raw.rename(
        columns={
            "Entity": "country",
            "Code": "country_code",
            "Year": "year",
            value_source: value_name,
        }
    )
    data["year"] = pd.to_numeric(data["year"], errors="coerce")
    data[value_name] = pd.to_numeric(data[value_name], errors="coerce")
    data = data.dropna(subset=["country", "year", value_name])
    return data[["country", "country_code", "year", value_name]]


def format_number(value: float, suffix: str = "") -> str:
    if pd.isna(value):
        return "-"
    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.1f}M{suffix}"
    if abs(value) >= 1_000:
        return f"{value / 1_000:.1f}K{suffix}"
    return f"{value:.1f}{suffix}"


def format_trend_value(value: float, value_format: str) -> str:
    if pd.isna(value):
        return "-"
    if value_format == "money":
        return f"${format_number(value)}"
    if value_format == "percent":
        return f"{value:.1f}%"
    if value_format == "decimal":
        return f"{value:.3f}"
    return format_number(value)


def add_growth_metrics(data: pd.DataFrame, value_col: str) -> pd.DataFrame:
    if data.empty:
        return data

    rows = []
    for country, group in data.sort_values("year").groupby("country"):
        latest = group.iloc[-1]
        baseline_pool = group[group["year"] <= latest["year"] - 5]
        baseline = baseline_pool.iloc[-1] if not baseline_pool.empty else group.iloc[0]
        baseline_value = float(baseline[value_col])
        latest_value = float(latest[value_col])
        abs_growth = latest_value - baseline_value
        pct_growth = np.nan
        if baseline_value > 0:
            pct_growth = abs_growth / baseline_value * 100
        rows.append(
            {
                "country": country,
                "latest_year": int(latest["year"]),
                "latest_value": latest_value,
                "baseline_year": int(baseline["year"]),
                "baseline_value": baseline_value,
                "absolute_growth": abs_growth,
                "pct_growth": pct_growth,
            }
        )
    return pd.DataFrame(rows)


def latest_values_for_countries(data: pd.DataFrame, value_col: str, countries: list[str]) -> pd.DataFrame:
    if data.empty:
        return pd.DataFrame(columns=["country", "latest_year", value_col])

    latest = (
        data[data["country"].isin(countries)]
        .dropna(subset=[value_col])
        .sort_values("year")
        .groupby("country", as_index=False)
        .tail(1)
    )
    return latest.rename(columns={"year": "latest_year"})[["country", "latest_year", value_col]]


def metric_hover_data(selected_metric: str) -> dict[str, str | bool]:
    hover_data = {
        selected_metric: ":.2f",
        "ai_overall_score": ":.2f",
        "hdi": ":.3f",
        "internet_usage_pct": ":.2f",
        "gdp_per_capita": ":,.0f",
    }
    return dict(hover_data)


def country_strengths(row: pd.Series) -> tuple[str, str]:
    values = row[list(AI_DIMENSIONS.values())].astype(float)
    strongest_col = values.idxmax()
    weakest_col = values.idxmin()
    label_by_col = {col: label for label, col in AI_DIMENSIONS.items()}
    return label_by_col[strongest_col], label_by_col[weakest_col]


def build_insights(data: pd.DataFrame, selected_metric_label: str, selected_metric: str) -> list[str]:
    top_ai = data.nlargest(1, "ai_overall_score").iloc[0]
    top_metric = data.nlargest(1, selected_metric).iloc[0]
    high_foundation_low_ai = data[
        (data["foundation_score"] >= data["foundation_score"].quantile(0.75))
        & (data["ai_overall_score"] <= data["ai_overall_score"].median())
    ].sort_values("foundation_score", ascending=False)
    overperformer = data.nlargest(1, "readiness_gap").iloc[0]

    insights = [
        f"{top_ai['country']} leads the AI overall score with a value of {top_ai['ai_overall_score']:.1f}.",
        f"{top_metric['country']} is strongest on {selected_metric_label}, with a score of {top_metric[selected_metric]:.1f}.",
        f"{overperformer['country']} appears to overperform relative to its HDI, internet access, and GDP foundation.",
    ]
    if not high_foundation_low_ai.empty:
        candidate = high_foundation_low_ai.iloc[0]
        insights.append(
            f"{candidate['country']} has a relatively strong digital foundation, but its AI score is still below the dataset median."
        )
    return insights




def compute_dimension_regressions(data: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for label, col in AI_DIMENSIONS.items():
        if col not in data.columns:
            continue

        reg_data = data[[col, "ai_overall_score"]].dropna()
        if len(reg_data) < 3:
            continue

        x = reg_data[col].astype(float).to_numpy()
        y = reg_data["ai_overall_score"].astype(float).to_numpy()

        x_design = np.vstack([np.ones(len(x)), x]).T
        intercept, slope = np.linalg.lstsq(x_design, y, rcond=None)[0]
        y_pred = intercept + slope * x

        ss_res = float(np.sum((y - y_pred) ** 2))
        ss_tot = float(np.sum((y - y.mean()) ** 2))
        r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else np.nan

        rows.append(
            {
                "dimension": label,
                "coefficient": float(slope),
                "r_squared": float(r_squared),
            }
        )

    reg_df = pd.DataFrame(rows).dropna(subset=["r_squared"])
    return reg_df.sort_values("r_squared", ascending=False)


def render_dimension_pillar_cards() -> None:
    st.caption(
        "The Overall AI Score uses 122 indicators grouped into 3 pillars and 7 sub-pillars."
    )

    pillars = [
        ("Implementation", "Talent · Infrastructure · Operating Environment"),
        ("Innovation", "Research · Development"),
        ("Investment", "Government Strategy · Commercial"),
    ]

    for pillar, subpillars in pillars:
        st.markdown(
            f"""
            <div style="
                border:1px solid #e4e7ec;
                border-radius:8px;
                padding:8px 10px;
                margin-bottom:6px;
                background:#ffffff;
                line-height:1.2;
            ">
                <div style="
                    font-size:0.80rem;
                    font-weight:600;
                    color:#101828;
                    margin-bottom:2px;
                ">
                    {pillar}
                </div>
                <div style="
                    font-size:0.78rem;
                    color:#475467;
                ">
                    {subpillars}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


@st.cache_data
def train_regression_model(data: pd.DataFrame, feature_cols: list[str], target_col: str = "ai_overall_score") -> tuple[float, dict[str, float], float, pd.DataFrame]:
    model_data = data.dropna(subset=feature_cols + [target_col]).copy()
    if model_data.empty:
        return 0.0, {feature: 0.0 for feature in feature_cols}, float("nan"), model_data

    X = model_data[feature_cols].astype(float).to_numpy()
    y = model_data[target_col].astype(float).to_numpy()
    X_design = np.hstack([np.ones((X.shape[0], 1)), X])
    coefficients, *_ = np.linalg.lstsq(X_design, y, rcond=None)
    intercept = float(coefficients[0])
    weights = {feature: float(coefficients[i + 1]) for i, feature in enumerate(feature_cols)}
    predictions = X_design.dot(coefficients)
    ss_res = np.sum((y - predictions) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    model_data["predicted_ai_overall_score"] = predictions
    return intercept, weights, float(r2), model_data

@st.cache_data
def compute_radial_layout(
    n_nodes: int,
    ref_local_idx: int,
    similarities_to_ref: np.ndarray,
) -> np.ndarray:
    """Radial layout: ref at center, peers on rings scaled by similarity.
    Higher similarity means closer to center. Peers are evenly spaced by angle."""
    pos = np.zeros((n_nodes, 2))
    peer_indices = [i for i in range(n_nodes) if i != ref_local_idx]
    n_peers = len(peer_indices)
    if n_peers == 0:
        return pos
 
    # Sort by similarity descending so the most similar start at angle=0
    peer_by_sim = sorted(peer_indices, key=lambda i: similarities_to_ref[i], reverse=True)
 
    sims = similarities_to_ref[peer_by_sim]
    s_min, s_max = sims.min(), sims.max()
    s_range = s_max - s_min if s_max > s_min else 1.0
 
    for rank, i in enumerate(peer_by_sim):
        angle = 2 * np.pi * rank / n_peers
        # Most similar maps to radius 1.2, least similar maps to radius 3.5.
        norm = (similarities_to_ref[i] - s_min) / s_range   # 0 = least, 1 = most similar
        radius = 3.5 - norm * 2.3
        pos[i] = [radius * np.cos(angle), radius * np.sin(angle)]
 
    pos[ref_local_idx] = [0.0, 0.0]
    return pos

df = load_ai_data()
gdp_ts = load_world_bank_timeseries(GDP_DATA, "gdp_per_capita")
internet_ts = load_world_bank_timeseries(INTERNET_DATA, "internet_usage_pct")
ai_publications_ts = load_owid_timeseries(AI_PUBLICATIONS_DATA, "ai_publications")
ai_patents_ts = load_owid_timeseries(AI_PATENTS_DATA, "ai_patents_per_million")
ai_investment_ts = load_owid_timeseries(AI_INVESTMENT_DATA, "ai_private_investment")
country_options = sorted(df["country"].dropna().unique())

default_compare = [
    country for country in ["Indonesia", "Singapore", "China", "United States"] if country in country_options
]
if not default_compare:
    default_compare = country_options[:4]

with st.sidebar:
    st.header("Dashboard Controls")
    selected_metric_label = st.selectbox("AI indicator", list(AI_METRICS.keys()))
    selected_metric = AI_METRICS[selected_metric_label]

    map_mode = st.radio("Map mode", list(MAP_PROJECTIONS.keys()), horizontal=False)

    min_score, max_score = st.slider(
        "AI overall score range",
        min_value=0,
        max_value=100,
        value=(0, 100),
        step=1,
    )

    selected_groups = st.multiselect(
        "Country group",
        options=sorted(df["ai_group"].dropna().unique()),
        default=sorted(df["ai_group"].dropna().unique()),
    )

    selected_countries = st.multiselect(
        "Comparison countries",
        options=country_options,
        default=default_compare,
    )

    top_n = st.slider("Ranking size", min_value=5, max_value=25, value=10, step=1)

filtered = df[
    df["ai_overall_score"].between(min_score, max_score)
    & df["ai_group"].isin(selected_groups)
].copy()

if filtered.empty:
    st.warning("No data matches the current filters.")
    st.stop()

top_country = filtered.sort_values("ai_overall_score", ascending=False).iloc[0]
average_ai = filtered["ai_overall_score"].mean()
average_hdi = filtered["hdi"].mean()
average_internet = filtered["internet_usage_pct"].mean()
median_gdp = filtered["gdp_per_capita"].median()
dimension_regressions = compute_dimension_regressions(filtered)
strongest_predictor = (
    dimension_regressions.iloc[0]["dimension"] if not dimension_regressions.empty else "-"
)

st.title("Global AI Readiness Dashboard")
st.caption(
    "An interactive dashboard for exploring global AI readiness through AI index scores, "
    "human development, internet access, and economic conditions."
)

kpi_cols = st.columns(6)
kpi_cols[0].metric("Countries", f"{len(filtered)}")
kpi_cols[1].metric("Leader", top_country["country"], f"{top_country['ai_overall_score']:.1f}")
kpi_cols[2].metric("Average AI Score", f"{average_ai:.1f}")
kpi_cols[3].metric("Average HDI", f"{average_hdi:.3f}")
kpi_cols[4].metric("Median GDP/capita", format_number(median_gdp))
kpi_cols[5].metric("Strongest Factor", strongest_predictor)

tabs = st.tabs(["Overview", "Quadrant", "Compare", "Trends", "Simulator", "Data"])

with tabs[0]:
    dimension_col, regression_col = st.columns([0.9, 1.4])

    with dimension_col:
        render_dimension_pillar_cards()

    with regression_col:
        if dimension_regressions.empty:
            st.info("Not enough data to calculate regression strength.")
        else:
            reg_plot = dimension_regressions.sort_values("r_squared", ascending=True)
            regression_fig = px.bar(
                reg_plot,
                x="r_squared",
                y="dimension",
                orientation="h",
                text="r_squared",
                color="r_squared",
                color_continuous_scale="Viridis",
                title=None,
                hover_data={
                    "dimension": False,
                    "r_squared": ":.3f",
                    "coefficient": ":.3f",
                },
                template=PLOTLY_TEMPLATE,
            )
            regression_fig.update_traces(texttemplate="%{text:.3f}", textposition="outside")
            regression_fig.update_layout(
                height=260,
                yaxis_title="",
                xaxis_title="R²",
                xaxis=dict(range=[0, max(1, float(dimension_regressions["r_squared"].max()) + 0.08)]),
                margin=dict(l=0, r=25, t=8, b=0),
                coloraxis_showscale=False,
            )
            st.plotly_chart(regression_fig, width="stretch")

    # st.markdown("---")

    map_fig = px.choropleth(
        filtered,
        locations="iso_alpha",
        color=selected_metric,
        hover_name="country",
        hover_data=metric_hover_data(selected_metric),
        color_continuous_scale="Viridis",
        projection=MAP_PROJECTIONS[map_mode],
        title=f"{map_mode}: {selected_metric_label}",
        template=PLOTLY_TEMPLATE,
    )
    map_fig.update_geos(
        showcountries=True,
        showcoastlines=True,
        showland=True,
        landcolor="#f8fafc",
        oceancolor="#e6f0f7",
        showocean=True,
    )
    map_fig.update_layout(
        margin=dict(l=0, r=0, t=55, b=0),
        height=570,
        coloraxis_colorbar_title=selected_metric_label,
    )

    left, right = st.columns([1.35, 1])
    with left:
        st.plotly_chart(map_fig, width="stretch")

    with right:
        base_ranking = filtered.nlargest(top_n, selected_metric).copy()
        selected_for_pin = filtered[filtered["country"].isin(selected_countries)].copy()
        ranking = pd.concat([base_ranking, selected_for_pin], ignore_index=True)
        ranking = ranking.drop_duplicates(subset="country").sort_values(selected_metric)

        ranking["ranking_label"] = ranking.apply(
            lambda row: f"#{int(row['rank_ai_overall'])} {row['country']}"
            if pd.notna(row.get("rank_ai_overall"))
            else row["country"],
            axis=1,
        )

        bar_fig = px.bar(
            ranking,
            x=selected_metric,
            y="ranking_label",
            orientation="h",
            color=selected_metric,
            color_continuous_scale="Viridis",
            title=f"Top {top_n} Countries + Comparison Countries by {selected_metric_label}",
            hover_name="country",
            hover_data={
                selected_metric: ":.2f",
                "ai_overall_score": ":.2f",
                "rank_ai_overall": ":.0f",
                "hdi": ":.3f",
                "internet_usage_pct": ":.2f",
                "ranking_label": False,
            },
            template=PLOTLY_TEMPLATE,
        )
        bar_fig.update_layout(
            height=570,
            yaxis_title="",
            xaxis_title=selected_metric_label,
            margin=dict(l=0, r=0, t=55, b=0),
            coloraxis_showscale=False,
        )
        st.plotly_chart(bar_fig, width="stretch")

    heatmap_source = filtered.nlargest(top_n, "ai_overall_score").copy()
    selected_heat = filtered[filtered["country"].isin(selected_countries)].copy()
    heatmap_source = pd.concat([heatmap_source, selected_heat], ignore_index=True)
    heatmap_source = (
        heatmap_source.drop_duplicates(subset="country")
        .sort_values("ai_overall_score", ascending=False)
        .set_index("country")
    )

    heatmap_fig = px.imshow(
        heatmap_source[list(AI_DIMENSIONS.values())],
        labels=dict(x="AI Dimension", y="Country", color="Score"),
        x=list(AI_DIMENSIONS.keys()),
        y=heatmap_source.index,
        color_continuous_scale="Magma",
        aspect="auto",
        title=f"AI Dimension Heatmap for Top {top_n} Countries + Comparison Countries",
        template=PLOTLY_TEMPLATE,
    )

    selected_heatmap_countries = [
        country for country in selected_countries if country in list(heatmap_source.index)
    ]
    for country in selected_heatmap_countries:
        y_idx = list(heatmap_source.index).index(country)
        heatmap_fig.add_shape(
            type="rect",
            xref="x",
            yref="y",
            x0=-0.5,
            x1=len(AI_DIMENSIONS) - 0.5,
            y0=y_idx - 0.5,
            y1=y_idx + 0.5,
            line=dict(color="#ef4444", width=3),
            fillcolor="rgba(0,0,0,0)",
        )

    heatmap_fig.update_layout(height=500, margin=dict(l=0, r=0, t=55, b=0))
    st.plotly_chart(heatmap_fig, width="stretch")

with tabs[1]:
 
    has_region = "region" in filtered.columns and filtered["region"].notna().any()
    if has_region:
        all_regions = sorted(filtered["region"].dropna().unique())
        selected_region = st.selectbox(
            "Filter by region",
            options=["All regions"] + all_regions,
            index=0,
            key="explore_region_filter",
        )
        explore_data = (
            filtered[filtered["region"] == selected_region].copy()
            if selected_region != "All regions"
            else filtered.copy()
        )
    else:
        explore_data = filtered.copy()
 
    if explore_data.empty:
        st.info("No countries match the current region filter.")
        st.stop()
 
    quadrant_data = explore_data.dropna(subset=["gdp_per_capita", "ai_overall_score"]).copy()
    quadrant_data = quadrant_data[quadrant_data["gdp_per_capita"] > 0]
    gdp_med = quadrant_data["gdp_per_capita"].median()
    ai_med = quadrant_data["ai_overall_score"].median()
 
    quadrant_data["quadrant"] = "Lower GDP - Lower AI"
    quadrant_data.loc[
        (quadrant_data["gdp_per_capita"] >= gdp_med) & (quadrant_data["ai_overall_score"] >= ai_med),
        "quadrant",
    ] = "Higher GDP - Higher AI"
    quadrant_data.loc[
        (quadrant_data["gdp_per_capita"] < gdp_med) & (quadrant_data["ai_overall_score"] >= ai_med),
        "quadrant",
    ] = "Lower GDP - Higher AI"
    quadrant_data.loc[
        (quadrant_data["gdp_per_capita"] >= gdp_med) & (quadrant_data["ai_overall_score"] < ai_med),
        "quadrant",
    ] = "Higher GDP - Lower AI"
 
    sim_feature_cols = list(AI_DIMENSIONS.values()) + ["hdi", "internet_usage_pct"]
    sim_data = explore_data.copy().reset_index(drop=True)
 
    feat_df = sim_data[sim_feature_cols].copy()
    feat_df["gdp_log"] = np.log1p(
        sim_data["gdp_per_capita"].fillna(sim_data["gdp_per_capita"].median())
    )
    all_feats = sim_feature_cols + ["gdp_log"]
    feat_df = feat_df[all_feats].copy()
    feat_df = feat_df.fillna(feat_df.median())   # median-impute; never drops a country
 
    col_min = feat_df.min()
    col_max = feat_df.max()
    col_range = (col_max - col_min).replace(0, 1)
    norm_vals = ((feat_df - col_min) / col_range).to_numpy()
 
    countries_arr = sim_data["country"].tolist()
    n_c = len(countries_arr)
 
    diffs = norm_vals[:, np.newaxis, :] - norm_vals[np.newaxis, :, :]   # (n, n, feats)
    dist_mat_full = np.sqrt((diffs ** 2).sum(axis=2))                    # (n, n)
    max_d = dist_mat_full.max() + 1e-8
    sim_mat = 1.0 - dist_mat_full / max_d                                # (n, n)
 
    top_left, top_right = st.columns([3, 2])
 
    with top_left:
        st.markdown("#### Country Classification")
        quadrant_fig = px.scatter(
            quadrant_data,
            x="gdp_per_capita",
            y="ai_overall_score",
            size="internet_usage_size",
            color="quadrant",
            color_discrete_map=QUADRANT_COLORS,
            hover_name="country",
            hover_data={
                "gdp_per_capita": ":,.0f",
                "ai_overall_score": ":.2f",
                "internet_usage_pct": ":.2f",
                "hdi": ":.3f",
                "internet_usage_size": False,
            },
            log_x=True,
            size_max=18,
            template=PLOTLY_TEMPLATE,
        )
        quadrant_fig.add_hline(y=ai_med, line_dash="dash", line_color="#667085", line_width=1)
        quadrant_fig.add_vline(x=gdp_med, line_dash="dash", line_color="#667085", line_width=1)
        quadrant_fig.update_layout(
            height=460,
            xaxis_title="GDP per Capita (log scale)",
            yaxis_title="AI Overall Score",
            legend_title="",
            legend=dict(
                orientation="h",
                yanchor="top", y=-0.36,
                xanchor="center", x=0.5,
                font=dict(size=11, color="#344054"),
                bgcolor="rgba(255,255,255,0.9)",
                bordercolor="#E4E7EC",
                borderwidth=1,
                itemsizing="constant",
                itemwidth=40,
            ),
            margin=dict(l=0, r=0, t=30, b=10),
        )
        st.plotly_chart(quadrant_fig, width="stretch")
 
    with top_right:
        ref_options = sorted(explore_data["country"].dropna().unique())
        default_ref = ref_options.index("Indonesia") if "Indonesia" in ref_options else 0
        ref_country = st.selectbox(
            "Find countries most similar to:",
            ref_options,
            index=default_ref,
            key="force_ref_country",
        )
 
        ref_idx_global = countries_arr.index(ref_country) if ref_country in countries_arr else 0
 
        ref_sims = sim_mat[ref_idx_global].copy()
        ref_sims[ref_idx_global] = -1.0
        top_k = min(14, n_c - 1)
        top_sim_idx = np.argsort(ref_sims)[::-1][:top_k]
        display_set = sorted(set(list(top_sim_idx) + [ref_idx_global]))
        display_countries = [countries_arr[i] for i in display_set]
        n_disp = len(display_countries)
        local_ref = next(
            l for l, g in enumerate(display_set) if g == ref_idx_global
        )
 
        sub_sim = sim_mat[np.ix_(display_set, display_set)]

        off_diag = sub_sim[np.triu_indices(n_disp, k=1)]
        EDGE_THRESHOLD = float(np.percentile(off_diag, 70)) if len(off_diag) > 0 else 0.5
        edge_tuples = tuple(
            (i, j, float(sub_sim[i, j]))
            for i in range(n_disp)
            for j in range(i + 1, n_disp)
            if sub_sim[i, j] >= EDGE_THRESHOLD
        )
 
        pos = compute_radial_layout(
            n_disp,
            local_ref,
            np.array([float(sub_sim[i, local_ref]) for i in range(n_disp)]),
        )
 
        country_to_quad = dict(zip(quadrant_data["country"], quadrant_data["quadrant"]))
 
        peer_x, peer_y, peer_text, peer_color, peer_size = [], [], [], [], []
        peer_hover, peer_customdata = [], []
 
        ref_x, ref_y = 0.0, 0.0
 
        for i, c in enumerate(display_countries):
            is_ref = (c == ref_country)
            quad = country_to_quad.get(c, "Lower GDP - Lower AI")
            node_color = QUADRANT_COLORS.get(quad, "#888780")
            row_s = sim_data[sim_data["country"] == c]
            ai_score = float(row_s.iloc[0]["ai_overall_score"]) if (not row_s.empty and pd.notna(row_s.iloc[0]["ai_overall_score"])) else 10.0
            g_idx = countries_arr.index(c) if c in countries_arr else 0
            sim_val = float(sim_mat[g_idx, ref_idx_global])
 
            if is_ref:
                ref_x, ref_y = float(pos[i, 0]), float(pos[i, 1])
            else:
                peer_x.append(float(pos[i, 0]))
                peer_y.append(float(pos[i, 1]))
                peer_text.append(c)
                peer_color.append(node_color)
                peer_size.append(max(8.0, 8.0 + ai_score / 8.0))
                peer_hover.append(
                    f"{c} | AI: {ai_score:.1f} | Sim: {sim_val:.2f} | {quad}"
                )
 
        force_fig = go.Figure()
 
        if edge_tuples:
            ew_vals = np.array([ew for _, _, ew in edge_tuples])
            ew_min, ew_max = ew_vals.min(), ew_vals.max()
            ew_range = ew_max - ew_min if ew_max > ew_min else 1.0
 
            buckets = {
                "strong":  {"x": [], "y": [], "width": 3.5, "color": "rgba(29,158,117,0.75)"},
                "medium":  {"x": [], "y": [], "width": 1.8, "color": "rgba(29,158,117,0.38)"},
                "weak":    {"x": [], "y": [], "width": 0.8, "color": "rgba(150,150,150,0.20)"},
            }
            for ei, ej, ew in edge_tuples:
                norm = (ew - ew_min) / ew_range   # 0 = weakest, 1 = strongest
                bucket = "strong" if norm >= 0.67 else ("medium" if norm >= 0.33 else "weak")
                buckets[bucket]["x"] += [pos[ei, 0], pos[ej, 0], None]
                buckets[bucket]["y"] += [pos[ei, 1], pos[ej, 1], None]
 
            label_map = {
                "strong": "Strong link",
                "medium": "Medium link",
                "weak":   "Weak link",
            }
            for bname, b in buckets.items():
                if b["x"]:
                    force_fig.add_trace(go.Scatter(
                        x=b["x"], y=b["y"],
                        mode="lines",
                        line=dict(width=b["width"], color=b["color"]),
                        name=label_map[bname],
                        hoverinfo="none",
                        showlegend=True,
                        legendgroup="edges",
                    ))
 
        if peer_x:
            force_fig.add_trace(go.Scatter(
                x=peer_x, y=peer_y,
                mode="markers+text",
                marker=dict(
                    size=peer_size,
                    color=peer_color,
                    line=dict(width=1, color="#ffffff"),
                    opacity=0.9,
                ),
                text=peer_text,
                textposition="top center",
                textfont=dict(size=8),
                customdata=peer_hover,
                hovertemplate="%{customdata}<extra></extra>",
                showlegend=False,
            ))
 
        force_fig.add_trace(go.Scatter(
            x=[ref_x], y=[ref_y],
            mode="markers+text",
            marker=dict(
                size=26,
                color="#2C2C2A",
                line=dict(width=3, color=QUADRANT_COLORS.get(
                    country_to_quad.get(ref_country, "Lower GDP - Lower AI"), "#888780"
                )),
            ),
            text=[ref_country],
            textposition="top center",
            textfont=dict(size=11, color="#2C2C2A"),
            hovertemplate=f"<b>{ref_country}</b> (reference)<extra></extra>",
            showlegend=False,
        ))
 
        force_fig.update_layout(
            height=460,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, showline=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, showline=False),
            legend=dict(
                orientation="h", yanchor="top", y=-0.04,
                xanchor="left", x=0, font=dict(size=11),
            ),
            margin=dict(l=0, r=0, t=45, b=10),
            template=PLOTLY_TEMPLATE,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(force_fig, width="stretch")
 
    # Bottom row.
    gap_df = explore_data.dropna(subset=["readiness_gap", "foundation_score", "ai_overall_score"]).copy()
    gap_df = gap_df.sort_values("readiness_gap", ascending=False).reset_index(drop=True)
    n_gap = len(gap_df)
    half = max(1, n_gap // 2)
 
    over  = gap_df.head(min(10, half)).sort_values("readiness_gap")        
    under = gap_df.tail(min(10, half)).head(10).sort_values("readiness_gap", 
                                                            ascending=False)
 
    n_over  = len(over)
    n_under = len(under)

    over_height  = max(220, 48 + n_over  * 36)
    under_height = max(220, 48 + n_under * 36)
 
    bot_left, bot_right = st.columns(2)
 
    with bot_left:
        over_fig = go.Figure()
        for _, row in over.iterrows():
            over_fig.add_trace(go.Scatter(
                x=[row["foundation_score"], row["ai_overall_score"]],
                y=[row["country"], row["country"]],
                mode="lines",
                line=dict(color="#9FE1CB", width=2.5),
                showlegend=False,
                hoverinfo="none",
            ))
        
        st.markdown(
            "<h6 style='text-align: center;'>Overperformer Countries</h6>",
            unsafe_allow_html=True
        )
        over_fig.add_trace(go.Scatter(
            x=over["foundation_score"],
            y=over["country"],
            mode="markers",
            name="Foundation (HDI + internet + GDP)",
            marker=dict(color="#B4B2A9", size=11, symbol="circle"),
            hovertemplate="<b>%{y}</b><br>Foundation score: %{x:.1f}<extra></extra>",
        ))
        over_fig.add_trace(go.Scatter(
            x=over["ai_overall_score"],
            y=over["country"],
            mode="markers",
            name="AI score",
            marker=dict(color="#1D9E75", size=11, symbol="circle"),
            hovertemplate="<b>%{y}</b><br>AI score: %{x:.1f}<extra></extra>",
        ))
        over_fig.update_layout(
            height=over_height,
            xaxis_title="Score (0–100)",
            yaxis_title="",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            margin=dict(l=0, r=0, t=0, b=0),
            template=PLOTLY_TEMPLATE,
        )
        st.plotly_chart(over_fig, use_container_width=True)
 
    with bot_right:
        under_fig = go.Figure()
        for _, row in under.iterrows():
            under_fig.add_trace(go.Scatter(
                x=[row["ai_overall_score"], row["foundation_score"]],
                y=[row["country"], row["country"]],
                mode="lines",
                line=dict(color="#F09595", width=2.5),
                showlegend=False,
                hoverinfo="none",
            ))
        under_fig.add_trace(go.Scatter(
            x=under["ai_overall_score"],
            y=under["country"],
            mode="markers",
            name="AI score",
            marker=dict(color="#E24B4A", size=11, symbol="circle"),
            hovertemplate="<b>%{y}</b><br>AI score: %{x:.1f}<extra></extra>",
        ))
        under_fig.add_trace(go.Scatter(
            x=under["foundation_score"],
            y=under["country"],
            mode="markers",
            name="Foundation (HDI + internet + GDP)",
            marker=dict(color="#378ADD", size=11, symbol="circle"),
            hovertemplate="<b>%{y}</b><br>Foundation score: %{x:.1f}<extra></extra>",
        ))
        st.markdown(
            "<h6 style='text-align: center;'>Untapped Potential</h6>",
            unsafe_allow_html=True
        )
        under_fig.update_layout(
            height=under_height,
            xaxis_title="Score (0–100)",
            yaxis_title="",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            margin=dict(l=0, r=0, t=0, b=0),
            template=PLOTLY_TEMPLATE,
        )
        st.plotly_chart(under_fig, use_container_width=True)
 
        over = explore_data.nlargest(10, "readiness_gap").sort_values("readiness_gap")
 
    
 
    # Insight cards below the charts.
    top_over = explore_data.nlargest(1, "readiness_gap").iloc[0]
    top_under = explore_data.nsmallest(1, "readiness_gap").iloc[0]
 
    most_sim_name, most_sim_score = "-", 0.0
    if ref_country in countries_arr:
        sims_copy = sim_mat[ref_idx_global].copy()
        sims_copy[ref_idx_global] = -1.0
        best_i = int(np.argmax(sims_copy))
        most_sim_name = countries_arr[best_i]
        most_sim_score = float(sims_copy[best_i])
 
    cards = [
        (
            "#E1F5EE", "#085041",
            "Overperformer",
            top_over["country"],
            f"AI score of <b>{top_over['ai_overall_score']:.1f}</b> sits "
            f"<b>{top_over['readiness_gap']:.1f} pts above</b> what its HDI, internet access, "
            "and GDP would predict, the biggest positive gap in this filter.",
        ),
        (
            "#FBE7E6", "#7C0E0C",
            "Untapped potential",
            top_under["country"],
            f"Development foundation score of <b>{top_under['foundation_score']:.1f}</b> "
            f"but AI score of only <b>{top_under['ai_overall_score']:.1f}</b>. "
            f"A <b>{abs(top_under['readiness_gap']):.1f} pt gap</b> likely driven by "
            "policy, investment, or talent bottlenecks.",
        ),
        (
            "#C2E6FF", "#0D2134",
            f"Closest peer to {ref_country}",
            most_sim_name,
            f"Similarity score: <b>{most_sim_score:.2f}</b> across all AI dimensions, "
            f"the most comparable country to {ref_country} in the dataset.",
        ),
    ]
 
    st.markdown("<div style='margin-top:8px'></div>", unsafe_allow_html=True)
    card_cols = st.columns(3)
    for col, (bg, tc, label, title, body) in zip(card_cols, cards):
        col.markdown(
            f"""<div class="insight-card" style="background:{bg};color:{tc};">
                <div class="insight-card-title" style="color:{tc};">
                    {title}</div>
                <div class="insight-card-label" style="color:{tc};">
                    the {label}</div>
                <div class="insight-card-body" style="color:{tc};">
                    {body}</div>
            </div>""",
            unsafe_allow_html=True,
        )
        
with tabs[2]:
    compare_countries = [country for country in selected_countries if country in country_options]
    if not compare_countries:
        compare_countries = filtered.nlargest(4, "ai_overall_score")["country"].tolist()

    compare_df = df[df["country"].isin(compare_countries)].copy()
    st.subheader("Country Comparison")

    radar_fig = go.Figure()
    for _, row in compare_df.iterrows():
        radar_values = row[list(AI_DIMENSIONS.values())].fillna(0).astype(float).tolist()
        radar_fig.add_trace(
            go.Scatterpolar(
                r=radar_values + [radar_values[0]],
                theta=list(AI_DIMENSIONS.keys()) + [list(AI_DIMENSIONS.keys())[0]],
                fill="toself",
                name=row["country"],
                opacity=0.72,
            )
        )
    radar_fig.update_layout(
        title="AI Dimension Radar Comparison",
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        height=560,
        margin=dict(l=30, r=30, t=70, b=30),
        template=PLOTLY_TEMPLATE,
    )

    compare_bar_source = compare_df.melt(
        id_vars="country",
        value_vars=["ai_overall_score", "hdi", "internet_usage_pct"],
        var_name="metric",
        value_name="value",
    )
    compare_bar_source["metric"] = compare_bar_source["metric"].replace(
        {
            "ai_overall_score": "AI Score",
            "hdi": "HDI",
            "internet_usage_pct": "Internet Usage",
        }
    )
    compare_bar_source.loc[compare_bar_source["metric"] == "HDI", "value"] *= 100
    compare_bar_fig = px.bar(
        compare_bar_source,
        x="country",
        y="value",
        color="metric",
        barmode="group",
        title="AI Score, HDI x100, and Internet Usage",
        template=PLOTLY_TEMPLATE,
    )
    compare_bar_fig.update_layout(height=560, xaxis_title="", yaxis_title="Score")

    radar_col, compare_bar_col = st.columns([1, 1])
    with radar_col:
        st.plotly_chart(radar_fig, width="stretch")
    with compare_bar_col:
        st.plotly_chart(compare_bar_fig, width="stretch")

    compare_df = compare_df.sort_values("rank_ai_overall")
    visible_profiles = compare_df.head(4)
    profile_cards = st.columns(len(visible_profiles))

    for idx, (_, row) in enumerate(visible_profiles.iterrows()):
        strongest, weakest = country_strengths(row)
        with profile_cards[idx]:
            st.markdown(
                f"""
                <div class="profile-card">
                    <div>
                        <div class="profile-card-title">{row["country"]}</div>
                        <div class="profile-card-score">{row["ai_overall_score"]:.1f}</div>
                        <div class="profile-card-rank">AI rank {row["rank_ai_overall"]:.0f}</div>
                    </div>
                    <div>
                        <div class="profile-card-detail"><b>Strongest:</b> {strongest}</div>
                        <div class="profile-card-detail"><b>Weakest:</b> {weakest}</div>
                        <div class="profile-card-detail"><b>GDP/capita:</b> {row["gdp_display"]}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    if len(compare_df) > 4:
        with st.expander(
            f"Show {len(compare_df)-4} more countries"
        ):
            remaining_profiles = compare_df.iloc[4:]
            cards_per_row = 4
            for start_idx in range(0, len(remaining_profiles), cards_per_row):
                cols = st.columns(cards_per_row)
                row_data = remaining_profiles.iloc[
                    start_idx:start_idx + cards_per_row
                ]
                for col, (_, row) in zip(cols, row_data.iterrows()):
                    strongest, weakest = country_strengths(row)
                    with col:
                        st.markdown(
                            f"""
                            <div class="profile-card">
                                <div>
                                    <div class="profile-card-title">{row["country"]}</div>
                                    <div class="profile-card-score">{row["ai_overall_score"]:.1f}</div>
                                    <div class="profile-card-rank">
                                        AI rank {row["rank_ai_overall"]:.0f}
                                    </div>
                                </div>
                                <div>
                                    <div class="profile-card-detail">
                                        <b>Strongest:</b> {strongest}
                                    </div>
                                    <div class="profile-card-detail">
                                        <b>Weakest:</b> {weakest}
                                    </div>
                                    <div class="profile-card-detail">
                                        <b>GDP/capita:</b> {row["gdp_display"]}
                                    </div>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

with tabs[3]:
    trend_countries = [country for country in selected_countries if country in country_options]
    if not trend_countries:
        trend_countries = filtered.nlargest(5, "ai_overall_score")["country"].tolist()

    st.subheader("AI Growth Explorer")
    st.caption(
        "GDP and internet usage represent foundations; publications, patents, and private investment represent AI output."
    )

    trend_metric = st.radio(
        "Trend metric",
        options=list(TREND_SOURCES.keys()),
        horizontal=True,
    )

    trend_meta = TREND_SOURCES[trend_metric]
    y_col = trend_meta["value_col"]
    y_title = trend_meta["label"]
    value_format = trend_meta["format"]

    if trend_metric == "GDP per Capita":
        trend_df = gdp_ts[gdp_ts["country"].isin(trend_countries)].copy()
    elif trend_metric == "Internet Usage":
        trend_df = internet_ts[internet_ts["country"].isin(trend_countries)].copy()
    elif trend_metric == "AI Publications":
        trend_df = ai_publications_ts[ai_publications_ts["country"].isin(trend_countries)].copy()
    elif trend_metric == "AI Patents per Million":
        trend_df = ai_patents_ts[ai_patents_ts["country"].isin(trend_countries)].copy()
    else:
        trend_df = ai_investment_ts[ai_investment_ts["country"].isin(trend_countries)].copy()

    trend_df = trend_df[trend_df["year"] >= 2000]
    if trend_df.empty:
        st.warning(
            "No data is available for the selected countries and metric. "
            "Try selecting larger countries such as United States, China, India, United Kingdom, Germany, or Indonesia."
        )
    else:
        latest_metrics = add_growth_metrics(trend_df, y_col)
        latest_metrics = latest_metrics.merge(
            df[["country", "ai_overall_score", "ai_research", "ai_development", "ai_commercial", "gdp_per_capita", "internet_usage_pct"]],
            on="country",
            how="left",
        )

        leader = latest_metrics.nlargest(1, "latest_value").iloc[0]
        growth_pool = latest_metrics.dropna(subset=["absolute_growth"])
        growth_leader = growth_pool.nlargest(1, "absolute_growth").iloc[0]
        selected_total = latest_metrics["latest_value"].sum()
        avg_growth = latest_metrics["absolute_growth"].mean()

        trend_kpis = st.columns(4)
        trend_kpis[0].metric("Latest leader", leader["country"], format_trend_value(leader["latest_value"], value_format))
        trend_kpis[1].metric("Fastest 5Y gain", growth_leader["country"], format_trend_value(growth_leader["absolute_growth"], value_format))
        trend_kpis[2].metric("Selected total", format_trend_value(selected_total, value_format))
        trend_kpis[3].metric("Average gain", format_trend_value(avg_growth, value_format))

        line_fig = px.line(
            trend_df,
            x="year",
            y=y_col,
            color="country",
            markers=True,
            title=f"{y_title} over time",
            template=PLOTLY_TEMPLATE,
        )
        line_fig.update_layout(
            height=520,
            xaxis_title="Year",
            yaxis_title=y_title,
            legend_title="Country",
            margin=dict(l=0, r=0, t=55, b=0),
        )
        st.plotly_chart(line_fig, width="stretch")

        latest_left, latest_right = st.columns([1, 1])
        with latest_left:
            latest_fig = px.bar(
                latest_metrics.sort_values("latest_value", ascending=True),
                x="latest_value",
                y="country",
                orientation="h",
                title=f"Latest {y_title}",
                color="latest_value",
                color_continuous_scale="Viridis",
                hover_data={
                    "latest_year": True,
                    "baseline_year": True,
                    "absolute_growth": ":,.2f",
                    "ai_overall_score": ":.2f",
                },
                template=PLOTLY_TEMPLATE,
            )
            latest_fig.update_layout(height=460, yaxis_title="", xaxis_title=y_title, coloraxis_showscale=False)
            st.plotly_chart(latest_fig, width="stretch")

        with latest_right:
            growth_fig = px.bar(
                latest_metrics.sort_values("absolute_growth", ascending=True),
                x="absolute_growth",
                y="country",
                orientation="h",
                title="Baseline-to-latest growth",
                color="absolute_growth",
                color_continuous_scale="Tealgrn",
                hover_data={
                    "baseline_year": True,
                    "latest_year": True,
                    "baseline_value": ":,.2f",
                    "latest_value": ":,.2f",
                },
                template=PLOTLY_TEMPLATE,
            )
            growth_fig.update_layout(height=460, yaxis_title="", xaxis_title=f"Growth in {y_title}", coloraxis_showscale=False)
            st.plotly_chart(growth_fig, width="stretch")

        ai_link_metric = "ai_research"
        ai_link_label = "AI Research Score"
        if trend_metric == "AI Patents per Million":
            ai_link_metric = "ai_development"
            ai_link_label = "AI Development Score"
        elif trend_metric == "Private AI Investment":
            ai_link_metric = "ai_commercial"
            ai_link_label = "AI Commercial Score"
        elif trend_metric in {"GDP per Capita", "Internet Usage"}:
            ai_link_metric = "ai_overall_score"
            ai_link_label = "AI Overall Score"

        scatter_source = latest_metrics.dropna(subset=["latest_value", ai_link_metric]).copy()
        if not scatter_source.empty:
            scatter_fig = px.scatter(
                scatter_source,
                x="latest_value",
                y=ai_link_metric,
                size="ai_overall_score",
                color="country",
                hover_name="country",
                hover_data={
                    "latest_year": True,
                    "latest_value": ":,.2f",
                    "absolute_growth": ":,.2f",
                    "ai_overall_score": ":.2f",
                    "gdp_per_capita": ":,.0f",
                    "internet_usage_pct": ":.2f",
                },
                title=f"Latest {y_title} vs {ai_link_label}",
                template=PLOTLY_TEMPLATE,
            )
            scatter_fig.update_layout(
                height=500,
                xaxis_title=y_title,
                yaxis_title=ai_link_label,
                legend_title="Country",
                margin=dict(l=0, r=0, t=55, b=0),
            )
            st.plotly_chart(scatter_fig, width="stretch")

        st.markdown("#### Foundation vs AI Output")
        st.caption("Compare a foundation metric against an AI output metric for the selected countries.")

        relation_left, relation_right = st.columns([1, 1])
        foundation_choice = relation_left.selectbox(
            "Foundation to compare",
            ["GDP per Capita - Economic Foundation", "Internet Usage - Digital Access"],
        )
        output_choice = relation_right.selectbox(
            "AI output to compare",
            [
                "AI Publications - Research Output",
                "AI Patents per Million - Innovation Output",
                "Private AI Investment - Commercial Momentum",
            ],
        )

        if foundation_choice.startswith("GDP"):
            foundation_data = latest_values_for_countries(gdp_ts[gdp_ts["year"] >= 2000], "gdp_per_capita", trend_countries)
            foundation_col = "gdp_per_capita"
            foundation_label = "GDP per Capita"
            foundation_format = "money"
        else:
            foundation_data = latest_values_for_countries(internet_ts[internet_ts["year"] >= 2000], "internet_usage_pct", trend_countries)
            foundation_col = "internet_usage_pct"
            foundation_label = "Internet Usage (%)"
            foundation_format = "percent"

        if output_choice.startswith("AI Publications"):
            output_data = latest_values_for_countries(ai_publications_ts[ai_publications_ts["year"] >= 2000], "ai_publications", trend_countries)
            output_col = "ai_publications"
            output_label = "AI Publications"
            output_format = "count"
        elif output_choice.startswith("AI Patents"):
            output_data = latest_values_for_countries(ai_patents_ts[ai_patents_ts["year"] >= 2000], "ai_patents_per_million", trend_countries)
            output_col = "ai_patents_per_million"
            output_label = "AI Patents per Million"
            output_format = "decimal"
        else:
            output_data = latest_values_for_countries(ai_investment_ts[ai_investment_ts["year"] >= 2000], "ai_private_investment", trend_countries)
            output_col = "ai_private_investment"
            output_label = "Private AI Investment"
            output_format = "money"

        relation_data = foundation_data.merge(output_data, on="country", how="inner", suffixes=("_foundation", "_output"))
        relation_data = relation_data.merge(
            df[["country", "ai_overall_score", "region"]],
            on="country",
            how="left",
        )

        if relation_data.empty:
            st.warning("No overlapping data is available for this country and metric combination.")
        else:
            median_foundation = relation_data[foundation_col].median()
            median_output = relation_data[output_col].median()
            relation_data["exploratory_zone"] = "Lower foundation / lower AI output"
            relation_data.loc[
                (relation_data[foundation_col] >= median_foundation) & (relation_data[output_col] >= median_output),
                "exploratory_zone",
            ] = "Higher foundation / higher AI output"
            relation_data.loc[
                (relation_data[foundation_col] >= median_foundation) & (relation_data[output_col] < median_output),
                "exploratory_zone",
            ] = "Higher foundation / lower AI output"
            relation_data.loc[
                (relation_data[foundation_col] < median_foundation) & (relation_data[output_col] >= median_output),
                "exploratory_zone",
            ] = "Lower foundation / higher AI output"

            relation_fig = px.scatter(
                relation_data,
                x=foundation_col,
                y=output_col,
                size="ai_overall_score",
                color="exploratory_zone",
                hover_name="country",
                hover_data={
                    "region": True,
                    "ai_overall_score": ":.2f",
                    foundation_col: ":,.2f",
                    output_col: ":,.2f",
                    "latest_year_foundation": True,
                    "latest_year_output": True,
                },
                title=f"Does {foundation_label} appear aligned with {output_label}?",
                template=PLOTLY_TEMPLATE,
            )
            relation_fig.add_vline(x=median_foundation, line_dash="dash", line_color="#667085")
            relation_fig.add_hline(y=median_output, line_dash="dash", line_color="#667085")
            relation_fig.update_layout(
                height=540,
                xaxis_title=foundation_label,
                yaxis_title=output_label,
                legend_title="Exploratory zone",
                margin=dict(l=0, r=0, t=55, b=0),
            )
            st.plotly_chart(relation_fig, width="stretch")

            higher_foundation_lower_output = relation_data[
                (relation_data[foundation_col] >= median_foundation) & (relation_data[output_col] < median_output)
            ].sort_values(foundation_col, ascending=False)
            lower_foundation_higher_output = relation_data[
                (relation_data[foundation_col] < median_foundation) & (relation_data[output_col] >= median_output)
            ].sort_values(output_col, ascending=False)

            read_cols = st.columns(2)
            if not higher_foundation_lower_output.empty:
                candidate = higher_foundation_lower_output.iloc[0]
                read_cols[0].warning(
                    f"{candidate['country']} is worth exploring further: "
                    f"{foundation_label} is relatively high ({format_trend_value(candidate[foundation_col], foundation_format)}), "
                    f"but {output_label} is still relatively lower ({format_trend_value(candidate[output_col], output_format)})."
                )
            if not lower_foundation_higher_output.empty:
                candidate = lower_foundation_higher_output.iloc[0]
                read_cols[1].success(
                    f"{candidate['country']} appears to overperform on AI output: "
                    f"{output_label} is relatively high ({format_trend_value(candidate[output_col], output_format)}) "
                    f"even though {foundation_label} is not as high as the comparison group."
                )

        st.info(
            f"Source: {trend_meta['source_note']} "
        )

with tabs[4]:
    st.subheader("AI Prediction Simulator")
    st.write(
        "Choose the features included in the model, then adjust their values to see how the predicted AI score changes. "
        "A larger positive coefficient means that increasing the feature is associated with a higher AI score in this filtered data."
    )

    predict_country = st.selectbox(
        "Country to simulate",
        country_options,
        index=country_options.index("Indonesia") if "Indonesia" in country_options else 0,
    )

    selected_predictors = st.multiselect(
        "Choose predictor features",
        options=PREDICTOR_FEATURES,
        default=["hdi", "internet_usage_pct", "gdp_per_capita"],
        format_func=lambda x: x.replace("_", " ").title(),
    )

    if not selected_predictors:
        st.warning("Select at least one predictor feature.")
    else:
        intercept, weights, r2, model_data = train_regression_model(filtered, selected_predictors)
        st.markdown(f"**Linear regression model**  \nR-squared: {r2:.3f}")

        coef_df = pd.DataFrame(
            {
                "feature": ["intercept"] + selected_predictors,
                "coefficient": [intercept] + [weights[feature] for feature in selected_predictors],
            }
        )
        coef_df["feature"] = coef_df["feature"].str.replace("_", " ").str.title()
        st.dataframe(coef_df, hide_index=True, width="stretch")

        coef_rank = sorted(weights.items(), key=lambda x: x[1], reverse=True)
        if coef_rank:
            top_positive = [f"{feature.replace('_', ' ').title()} ({value:.3f})" for feature, value in coef_rank if value > 0][:3]
            top_negative = [f"{feature.replace('_', ' ').title()} ({value:.3f})" for feature, value in coef_rank if value < 0][:2]

            recommendation_lines = []
            if top_positive:
                recommendation_lines.append(
                    f"Features most associated with higher AI score: {', '.join(top_positive)}."
                )
            if top_negative:
                recommendation_lines.append(
                    f"Features associated with lower AI score when increased: {', '.join(top_negative)}."
                )
            if recommendation_lines:
                st.markdown("**Feature notes:**")
                for line in recommendation_lines:
                    st.markdown(f"- {line}")

        country_row = df[df["country"] == predict_country].iloc[0]
        feature_settings = {}

        slider_col_left, slider_col_right = st.columns(2)
        for idx, feature in enumerate(selected_predictors):
            col = slider_col_left if idx % 2 == 0 else slider_col_right
            feature_min = float(df[feature].min())
            feature_max = float(df[feature].max())
            default_value = float(country_row[feature]) if pd.notna(country_row[feature]) else float((feature_min + feature_max) / 2)
            step = float(max((feature_max - feature_min) / 100, 0.1))
            feature_settings[feature] = col.slider(
                feature.replace("_", " ").title(),
                min_value=feature_min,
                max_value=feature_max,
                value=default_value,
                step=step,
            )

        feature_vector = np.array([feature_settings[feature] for feature in selected_predictors], dtype=float)
        predicted_score = intercept + feature_vector.dot(np.array([weights[feature] for feature in selected_predictors], dtype=float))
        actual_score = float(country_row["ai_overall_score"]) if pd.notna(country_row["ai_overall_score"]) else float("nan")

        delta_text = None
        if pd.notna(actual_score):
            delta_text = f"{predicted_score - actual_score:+.1f}"

        st.metric("Predicted AI Score", f"{predicted_score:.1f}", delta=delta_text)
        if pd.notna(actual_score):
            st.caption(f"Actual AI Score for {predict_country}: {actual_score:.1f}")

        if not model_data.empty:
            scatter_fig = px.scatter(
                model_data,
                x="ai_overall_score",
                y="predicted_ai_overall_score",
                hover_name="country",
                title="Actual vs Predicted AI Score",
                labels={
                    "ai_overall_score": "Actual AI Score",
                    "predicted_ai_overall_score": "Predicted AI Score",
                },
                template=PLOTLY_TEMPLATE,
            )
            min_val = min(model_data["ai_overall_score"].min(), model_data["predicted_ai_overall_score"].min())
            max_val = max(model_data["ai_overall_score"].max(), model_data["predicted_ai_overall_score"].max())
            scatter_fig.add_shape(
                type="line",
                x0=min_val,
                y0=min_val,
                x1=max_val,
                y1=max_val,
                line=dict(dash="dash", color="#667085"),
            )
            scatter_fig.update_layout(height=520, margin=dict(l=0, r=0, t=55, b=0))
            st.plotly_chart(scatter_fig, width="stretch")

with tabs[5]:
    display_cols = [
        "country",
        "ai_overall_score",
        selected_metric,
        "hdi",
        "internet_usage_pct",
        "gdp_per_capita",
        "foundation_score",
        "readiness_gap",
        "rank_ai_overall",
    ]
    display_cols = list(dict.fromkeys(display_cols))
    table_data = filtered[display_cols].sort_values("ai_overall_score", ascending=False)
    st.dataframe(table_data, width="stretch", hide_index=True)

    csv_data = table_data.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download filtered data as CSV",
        data=csv_data,
        file_name="filtered_ai_readiness_data.csv",
        mime="text/csv",
    )
