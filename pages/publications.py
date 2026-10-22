import streamlit as st
import plotly.express as px
import pandas as pd

from utils.publications_utils import (
    calculate_concentration_change,
    calculate_active_countries,
    calculate_global_publications,
    calculate_top5_share,
    load_data,
    get_treemap_data,
    get_concentration_overtime_data,
    get_publication_trend_data,
    get_fastest_growing_countries
)

# =====================================
# Load Data
# =====================================

df = load_data()

# =====================================
# Dashboard Header
# =====================================

st.markdown(
    "### Is AI Development Becoming Concentrated in Fewer Countries?"
)

st.markdown(
    "# Is AI research output becoming concentrated in a small number of countries?"
)

st.write(
    "This dashboard explores how AI publication activity is distributed "
    "across countries and whether a growing share of global research output "
    "is being produced by a small group of leading nations."
)

# =====================================
# Year Range Filter
# =====================================

min_year = int(df["year"].min())
max_year = int(df["year"].max())

start_year, end_year = st.slider(
    "Select Year Range",
    min_value=min_year,
    max_value=max_year,
    value=(max_year - 5, max_year)
)

# =====================================
# KPI Calculations
# =====================================

global_publications = calculate_global_publications(
    df,
    start_year,
    end_year
)

active_countries = calculate_active_countries(
    df,
    start_year,
    end_year
)

top5_share = calculate_top5_share(
    df,
    start_year,
    end_year
)

concentration_change = calculate_concentration_change(
    df,
    start_year,
    end_year
)

# =====================================
# KPI Row
# =====================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Global AI Publications",
        f"{global_publications:,.0f}"
    )

with col2:
    st.metric(
        "Active Countries",
        active_countries
    )

with col3:
    st.metric(
        "Top 5 Share",
        f"{top5_share:.1f}%"
    )

with col4:
    st.metric(
        "Concentration Change",
        f"{concentration_change:+.1f} pp"
    )

st.success(
    f"Despite contributions from {active_countries} countries, "
    f"the five largest publishing countries account for "
    f"{top5_share:.1f}% of global AI publications during the "
    f"selected period."
)

st.caption(
    "Limitation: AI publications are identified using machine-learning models "
    "applied to articles with English titles or abstracts. Research published "
    "only in other languages may be underrepresented, and coverage of some "
    "Chinese journals is incomplete. Multi-country publications are counted "
    "once for each country represented through author affiliations."
)

# =====================================
# Section 1
# =====================================

st.markdown(
    f"## Current Concentration ({end_year})"
)

st.caption(
    "Distribution of global AI publications across countries in the latest year of the selected period."
)

treemap_df = get_treemap_data(
    df,
    end_year
)

fig = px.treemap(
    treemap_df,
    path=["country"],
    values="publications",
    color="rank_group",
    color_discrete_map={
        "Top 1": "#780000",
        "Top 2": "#A4133C",
        "Top 3": "#C1121F",
        "Top 4": "#E5383B",
        "Top 5": "#FF758F",
        "Other Countries": "#669BBC"
    },
    custom_data=[
        "share",
        "publications"
    ]
)

fig.update_traces(
    hovertemplate=
    "<b>%{label}</b><br>"
    "Publications: %{customdata[1]:,.0f}<br>"
    "Share of Global Publications: %{customdata[0]:.2f}%"
    "<extra></extra>"
)

fig.update_layout(
    margin=dict(
        t=10,
        l=0,
        r=0,
        b=0
    ),
    legend_title="Country Group"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

top_country = (
    treemap_df
    .sort_values(
        "publications",
        ascending=False
    )
    .iloc[0]
)

st.success(
    f"{top_country['country']} accounted for "
    f"{top_country['share']:.2f}% of global AI publications in "
    f"{end_year}, making it the largest contributor."
)

# =====================================
# Section 2
# =====================================

st.markdown(
    "## Concentration Over Time"
)

st.caption(
    f"Share of global AI publications among the five largest publishing countries in {end_year}."
)

area_df = get_concentration_overtime_data(
    df,
    start_year,
    end_year
)

# Top 5 countries from end year
top5 = (
    treemap_df[
        treemap_df["rank_group"] != "Other Countries"
    ]
    .sort_values(
        "publications",
        ascending=False
    )["country"]
    .tolist()
)

# Build colour map dynamically
country_colors = {}

palette = [
    "#780000",  # Top 1
    "#A4133C",  # Top 2
    "#C1121F",  # Top 3
    "#E5383B",  # Top 4
    "#FF758F"   # Top 5
]

for country, colour in zip(
    top5,
    palette
):
    country_colors[country] = colour

country_colors["Others"] = "#1D3557"

fig = px.area(
    area_df,
    x="year",
    y="share",
    color="group",
    labels={
        "year": "Year",
        "share": "Share of Global Publications (%)",
        "group": "Country"
    },
    color_discrete_map=country_colors
)

fig.update_traces(
    opacity=0.95,
    hovertemplate=
    "<b>%{fullData.name}</b><br>"
    "Year: %{x}<br>"
    "Share: %{y:.2f}%"
    "<extra></extra>"
)

fig.update_layout(
    hovermode="x unified",

    plot_bgcolor="white",
    paper_bgcolor="white",

    xaxis_title="Year",

    yaxis_title=
    "Share of Global Publications (%)",

    legend_title="Country",

    margin=dict(
        t=20,
        l=0,
        r=0,
        b=0
    )
)

st.plotly_chart(
    fig,
    use_container_width=True
)

latest_year = area_df[
    area_df["year"] == end_year
]

others_share = latest_year[
    latest_year["group"] == "Others"
]["share"].iloc[0]

top5_share = 100 - others_share

st.success(
    f"In {end_year}, the five largest publishing countries accounted for "
    f"{top5_share:.2f}% of global AI publications, while all remaining "
    f"countries collectively contributed {others_share:.2f}%."
)


# =====================================
# Section 3
# =====================================

st.markdown(
    "## Publication Trends"
)

st.caption(
    f"Annual AI publication output of the five largest publishing countries in {end_year}."
)

# Prepare data
# Prepare publication trend data
def get_publication_trend_data(
    df,
    start_year,
    end_year
):
    end_df = df[
        df["year"] == end_year
    ]

    top5 = (
        end_df
        .sort_values(
            "publications",
            ascending=False
        )
        .head(5)["country"]
        .tolist()
    )

    filtered = df[
        (df["year"] >= start_year)
        & (df["year"] <= end_year)
    ].copy()

    filtered = filtered[
        filtered["country"].isin(top5)
    ]

    return filtered

trend_df = get_publication_trend_data(
    df,
    start_year,
    end_year
)

# Get Top 5 countries from end year
top5 = (
    treemap_df[
        treemap_df["rank_group"] != "Other Countries"
    ]
    .sort_values(
        "publications",
        ascending=False
    )["country"]
    .tolist()
)

# Country selection
selected_countries = st.multiselect(
    "Select Countries",
    options=top5,
    default=top5
)

trend_df = trend_df[
    trend_df["country"].isin(
        selected_countries
    )
]

# Consistent colour palette
country_colors = {}

palette = [
    "#780000",  # Top 1
    "#A4133C",  # Top 2
    "#C1121F",  # Top 3
    "#E5383B",  # Top 4
    "#FF758F"   # Top 5
]

for country, colour in zip(
    top5,
    palette
):
    country_colors[country] = colour

# Create chart
fig = px.line(
    trend_df,
    x="year",
    y="publications",
    color="country",
    color_discrete_map=country_colors,
    markers=True,
    labels={
        "year": "Year",
        "publications": "AI Publications",
        "country": "Country"
    }
)

# Line styling
fig.update_traces(
    line=dict(width=3),
    marker=dict(size=8),
    hovertemplate=
    "<b>%{fullData.name}</b><br>"
    "Year: %{x}<br>"
    "Publications: %{y:,.0f}"
    "<extra></extra>"
)

# Layout
fig.update_layout(
    hovermode="x unified",

    plot_bgcolor="white",
    paper_bgcolor="white",

    xaxis_title="Year",

    yaxis_title="AI Publications",

    legend_title="Country",

    margin=dict(
        t=20,
        l=0,
        r=0,
        b=0
    )
)

# Display chart
st.plotly_chart(
    fig,
    use_container_width=True
)

# Insight
latest = (
    trend_df[
        trend_df["year"] == end_year
    ]
    .sort_values(
        "publications",
        ascending=False
    )
)

leader = latest.iloc[0]

st.success(
    f"{leader['country']} led AI publication output in "
    f"{end_year} with {leader['publications']:,.0f} publications."
)

# =====================================
# Section 4
# =====================================

st.markdown(
    "## Fastest Growing AI Research Countries"
)

st.caption(
    f"Countries ranked by a Growth + Scale Score between "
    f"{start_year} and {end_year}. The score balances publication growth "
    f"with current research scale to avoid overemphasising countries with "
    f"very small publication bases."
)

# Prepare data
growth_df = get_fastest_growing_countries(
    df,
    start_year,
    end_year
)

# Create chart
fig = px.bar(
    growth_df,
    x="growth_scale_score",
    y="country",
    orientation="h",
    color="growth_rate",
    color_continuous_scale=[
        "#F5F5F5",
        "#669BBC",
        "#1D3557",
        "#FF758F",
        "#C1121F"
    ],
    labels={
        "growth_scale_score":
        "Growth + Scale Score",
        "country":
        "Country"
    }
)

# Bar labels and hover
fig.update_traces(
    text=growth_df["growth_rate"].apply(
        lambda x: f"{x:.0f}%"
    ),
    textposition="outside",
    hovertemplate=
    "<b>%{y}</b><br>"
    "Growth Rate: %{text}<br>"
    "Growth + Scale Score: %{x:.2f}"
    "<extra></extra>"
)

# Layout
fig.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white",
    coloraxis_showscale=False,
    xaxis_title="Growth + Scale Score",
    yaxis_title="",
    margin=dict(
        t=20,
        l=0,
        r=0,
        b=0
    )
)

# Display chart
st.plotly_chart(
    fig,
    use_container_width=True
)

# Insight
leader = growth_df.iloc[0]

st.success(
    f"{leader['country']} ranked highest based on the Growth + Scale Score, "
    f"combining a publication growth rate of "
    f"{leader['growth_rate']:.1f}% with a meaningful level of AI research output "
    f"by {end_year}. This suggests the country is emerging as a significant AI "
    f"research hub beyond today's leading publishing nations."
)
