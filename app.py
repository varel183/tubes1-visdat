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

AI_METRICS = {
    "Overall AI Score": "ai_overall_score",
    "Talent": "ai_talent",
    "Infrastructure": "ai_infrastructure",
    "Operating Environment": "ai_operating_environment",
    "Research": "ai_research",
    "Development": "ai_development",
    "Government Strategy": "ai_government_strategy",
    "Commercial": "ai_commercial",
    "Scale": "ai_scale",
    "Intensity": "ai_intensity",
}

AI_DIMENSIONS = {label: col for label, col in AI_METRICS.items() if col != "ai_overall_score"}

MAP_PROJECTIONS = {
    "Interactive Globe": "orthographic",
    "Flat World Map": "natural earth",
    "Mercator Zoom Map": "mercator",
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
    "ai_scale",
    "ai_intensity",
]

PLOTLY_TEMPLATE = "plotly_white"


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
            padding: 14px 16px;
            background: #ffffff;
            box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
        }
        div[data-testid="stMetricLabel"] p {
            font-size: 0.82rem;
            color: #475467;
        }
        div[data-testid="stMetricValue"] {
            font-size: 1.45rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_ai_data() -> pd.DataFrame:
    df = pd.read_csv(MAIN_DATA)
    numeric_cols = [
        "ai_overall_score",
        "ai_talent",
        "ai_infrastructure",
        "ai_operating_environment",
        "ai_research",
        "ai_development",
        "ai_government_strategy",
        "ai_commercial",
        "ai_scale",
        "ai_intensity",
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


def format_number(value: float, suffix: str = "") -> str:
    if pd.isna(value):
        return "-"
    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.1f}M{suffix}"
    if abs(value) >= 1_000:
        return f"{value / 1_000:.1f}K{suffix}"
    return f"{value:.1f}{suffix}"


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
        f"{top_ai['country']} memimpin AI overall score dengan nilai {top_ai['ai_overall_score']:.1f}.",
        f"{top_metric['country']} paling kuat pada indikator {selected_metric_label} dengan nilai {top_metric[selected_metric]:.1f}.",
        f"{overperformer['country']} terlihat paling overperform dibanding fondasi HDI, internet, dan GDP relatifnya.",
    ]
    if not high_foundation_low_ai.empty:
        candidate = high_foundation_low_ai.iloc[0]
        insights.append(
            f"{candidate['country']} punya fondasi digital relatif tinggi, tetapi AI score-nya masih di bawah median data."
        )
    return insights


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


df = load_ai_data()
gdp_ts = load_world_bank_timeseries(GDP_DATA, "gdp_per_capita")
internet_ts = load_world_bank_timeseries(INTERNET_DATA, "internet_usage_pct")
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
    st.warning("Tidak ada data yang sesuai dengan filter.")
    st.stop()

top_country = filtered.sort_values("ai_overall_score", ascending=False).iloc[0]
average_ai = filtered["ai_overall_score"].mean()
average_hdi = filtered["hdi"].mean()
average_internet = filtered["internet_usage_pct"].mean()
median_gdp = filtered["gdp_per_capita"].median()

st.title("Global AI Readiness Dashboard")
st.caption(
    "Dashboard interaktif untuk membaca kesiapan AI global melalui indeks AI, kualitas manusia, "
    "akses internet, dan kondisi ekonomi."
)

kpi_cols = st.columns(5)
kpi_cols[0].metric("Countries", f"{len(filtered)}")
kpi_cols[1].metric("Leader", top_country["country"], f"{top_country['ai_overall_score']:.1f}")
kpi_cols[2].metric("Average AI Score", f"{average_ai:.1f}")
kpi_cols[3].metric("Average HDI", f"{average_hdi:.3f}")
kpi_cols[4].metric("Median GDP/capita", format_number(median_gdp))

tabs = st.tabs(["Overview", "Quadrant", "Compare", "Trends", "Simulator", "Data"])

with tabs[0]:
    insight_cols = st.columns(4)
    for idx, insight in enumerate(build_insights(filtered, selected_metric_label, selected_metric)):
        insight_cols[idx].info(insight)

    map_fig = px.choropleth(
        filtered,
        locations="country",
        locationmode="country names",
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
        ranking = filtered.nlargest(top_n, selected_metric).sort_values(selected_metric)
        bar_fig = px.bar(
            ranking,
            x=selected_metric,
            y="country",
            orientation="h",
            color=selected_metric,
            color_continuous_scale="Viridis",
            title=f"Top {top_n} Countries by {selected_metric_label}",
            hover_data={
                selected_metric: ":.2f",
                "ai_overall_score": ":.2f",
                "hdi": ":.3f",
                "internet_usage_pct": ":.2f",
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

    heatmap_source = filtered.nlargest(top_n, "ai_overall_score").set_index("country")
    heatmap_fig = px.imshow(
        heatmap_source[list(AI_DIMENSIONS.values())],
        labels=dict(x="AI Dimension", y="Country", color="Score"),
        x=list(AI_DIMENSIONS.keys()),
        y=heatmap_source.index,
        color_continuous_scale="Magma",
        aspect="auto",
        title=f"AI Dimension Heatmap for Top {top_n} Countries",
        template=PLOTLY_TEMPLATE,
    )
    heatmap_fig.update_layout(height=460, margin=dict(l=0, r=0, t=55, b=0))
    st.plotly_chart(heatmap_fig, width="stretch")

with tabs[1]:
    quadrant_data = filtered.dropna(subset=["gdp_per_capita", "ai_overall_score"]).copy()
    quadrant_data = quadrant_data[quadrant_data["gdp_per_capita"] > 0]
    gdp_threshold = quadrant_data["gdp_per_capita"].median()
    ai_threshold = quadrant_data["ai_overall_score"].median()
    quadrant_data["quadrant"] = "Lower GDP - Lower AI"
    quadrant_data.loc[
        (quadrant_data["gdp_per_capita"] >= gdp_threshold)
        & (quadrant_data["ai_overall_score"] >= ai_threshold),
        "quadrant",
    ] = "Higher GDP - Higher AI"
    quadrant_data.loc[
        (quadrant_data["gdp_per_capita"] < gdp_threshold)
        & (quadrant_data["ai_overall_score"] >= ai_threshold),
        "quadrant",
    ] = "Lower GDP - Higher AI"
    quadrant_data.loc[
        (quadrant_data["gdp_per_capita"] >= gdp_threshold)
        & (quadrant_data["ai_overall_score"] < ai_threshold),
        "quadrant",
    ] = "Higher GDP - Lower AI"

    quadrant_fig = px.scatter(
        quadrant_data,
        x="gdp_per_capita",
        y="ai_overall_score",
        size="internet_usage_size",
        color="quadrant",
        hover_name="country",
        hover_data={
            "gdp_per_capita": ":,.0f",
            "ai_overall_score": ":.2f",
            "internet_usage_pct": ":.2f",
            "hdi": ":.3f",
            "internet_usage_size": False,
        },
        log_x=True,
        size_max=38,
        title="AI Readiness Quadrant: Economic Capacity vs AI Performance",
        template=PLOTLY_TEMPLATE,
    )
    quadrant_fig.add_hline(y=ai_threshold, line_dash="dash", line_color="#667085")
    quadrant_fig.add_vline(x=gdp_threshold, line_dash="dash", line_color="#667085")
    quadrant_fig.update_layout(
        height=620,
        xaxis_title="GDP per Capita (log scale)",
        yaxis_title="AI Overall Score",
        legend_title="Quadrant",
        margin=dict(l=0, r=0, t=55, b=0),
    )
    st.plotly_chart(quadrant_fig, width="stretch")

    gap_cols = st.columns(2)
    with gap_cols[0]:
        over = filtered.nlargest(10, "readiness_gap").sort_values("readiness_gap")
        over_fig = px.bar(
            over,
            x="readiness_gap",
            y="country",
            orientation="h",
            title="Overperformers: AI Score above Development Foundation",
            color="readiness_gap",
            color_continuous_scale="Tealgrn",
            template=PLOTLY_TEMPLATE,
        )
        over_fig.update_layout(height=420, yaxis_title="", xaxis_title="Readiness Gap")
        st.plotly_chart(over_fig, width="stretch")

    with gap_cols[1]:
        under = filtered.nsmallest(10, "readiness_gap").sort_values("readiness_gap", ascending=False)
        under_fig = px.bar(
            under,
            x="readiness_gap",
            y="country",
            orientation="h",
            title="Untapped Potential: Stronger Foundation than AI Score",
            color="readiness_gap",
            color_continuous_scale="RdBu",
            template=PLOTLY_TEMPLATE,
        )
        under_fig.update_layout(height=420, yaxis_title="", xaxis_title="Readiness Gap")
        st.plotly_chart(under_fig, width="stretch")

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

    profile_cards = st.columns(min(len(compare_df), 4))
    for idx, (_, row) in enumerate(compare_df.head(4).iterrows()):
        strongest, weakest = country_strengths(row)
        with profile_cards[idx]:
            st.metric(row["country"], f"{row['ai_overall_score']:.1f}", f"Rank {row['rank_ai_overall']:.0f}")
            st.caption(f"Strongest: {strongest}")
            st.caption(f"Weakest: {weakest}")
            st.caption(f"GDP/capita: {row['gdp_display']}")

with tabs[3]:
    trend_countries = [country for country in selected_countries if country in country_options]
    if not trend_countries:
        trend_countries = filtered.nlargest(5, "ai_overall_score")["country"].tolist()

    trend_metric = st.radio(
        "Trend metric",
        options=["GDP per Capita", "Internet Usage"],
        horizontal=True,
    )

    if trend_metric == "GDP per Capita":
        trend_df = gdp_ts[gdp_ts["country"].isin(trend_countries)].copy()
        y_col = "gdp_per_capita"
        y_title = "GDP per Capita"
    else:
        trend_df = internet_ts[internet_ts["country"].isin(trend_countries)].copy()
        y_col = "internet_usage_pct"
        y_title = "Internet Usage (%)"

    trend_df = trend_df[trend_df["year"] >= 2000]
    line_fig = px.line(
        trend_df,
        x="year",
        y=y_col,
        color="country",
        markers=True,
        title=f"{y_title} Trend since 2000",
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

    latest_trend = trend_df.sort_values("year").groupby("country", as_index=False).tail(1)
    if not latest_trend.empty:
        latest_fig = px.bar(
            latest_trend.sort_values(y_col, ascending=True),
            x=y_col,
            y="country",
            orientation="h",
            title=f"Latest Available {y_title}",
            color=y_col,
            color_continuous_scale="Viridis",
            template=PLOTLY_TEMPLATE,
        )
        latest_fig.update_layout(height=420, yaxis_title="", xaxis_title=y_title, coloraxis_showscale=False)
        st.plotly_chart(latest_fig, width="stretch")

with tabs[4]:
    st.subheader("AI Prediction Simulator")
    st.write(
        "Pilih fitur yang ingin dimasukkan ke model, lalu geser nilai fitur untuk melihat bagaimana prediksi AI score berubah. "
        "Semakin besar koefisien positif, semakin besar dampak kenaikan nilai fitur terhadap AI score."
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
        st.warning("Pilih minimal satu fitur prediksi.")
    else:
        intercept, weights, r2, model_data = train_regression_model(filtered, selected_predictors)
        st.markdown(f"**Linear regression model**  \nR²: {r2:.3f}")

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
                    f"Fitur paling berpengaruh naikkan AI score: {', '.join(top_positive)}."
                )
            if top_negative:
                recommendation_lines.append(
                    f"Fitur dengan dampak negatif jika naik: {', '.join(top_negative)}."
                )
            if recommendation_lines:
                st.markdown("**Rekomendasi fitur:**")
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
