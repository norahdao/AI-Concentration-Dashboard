import pandas as pd
import numpy as np

# Load and clean publication data
def load_data():
    df = pd.read_csv("data/publications.csv")

    df = df.rename(
        columns={
            "entity": "country",
            "code": "code",
            "year": "year",
            "num_articles__field_all": "publications",
        }
    )

    # Keep only rows with country codes
    df = df[df["code"].notna()]

    # Remove OWID aggregate regions
    df = df[~df["code"].str.startswith("OWID", na=False)]

    return df

# Calculate total global publications
def calculate_global_publications(
    df,
    start_year,
    end_year
):
    filtered = df[
        (df["year"] >= start_year)
        & (df["year"] <= end_year)
    ]

    return int(filtered["publications"].sum())


# Calculate active countries
def calculate_active_countries(
    df,
    start_year,
    end_year
):
    filtered = df[
        (df["year"] >= start_year)
        & (df["year"] <= end_year)
    ]

    active = filtered.loc[
        filtered["publications"] > 0,
        "country"
    ].nunique()

    return int(active)


# Calculate Top 5 countries' share of global publications
def calculate_top5_share(
    df,
    start_year,
    end_year
):
    filtered = df[
        (df["year"] >= start_year)
        & (df["year"] <= end_year)
    ]

    # Total global publications
    total_publications = filtered["publications"].sum()

    # Publications by country
    country_totals = (
        filtered
        .groupby("country")["publications"]
        .sum()
        .sort_values(ascending=False)
    )

    # Top 5 countries
    top5_publications = country_totals.head(5).sum()

    # Share of global publications
    top5_share = (
        top5_publications
        / total_publications
    ) * 100

    return round(top5_share, 1)


# Calculate change in Top 5 share between the first and last year
def calculate_concentration_change(
    df,
    start_year,
    end_year
):
    # First year data
    start_df = df[
        df["year"] == start_year
    ]

    start_total = start_df["publications"].sum()

    start_top5 = (
        start_df
        .groupby("country")["publications"]
        .sum()
        .sort_values(ascending=False)
        .head(5)
        .sum()
    )

    start_share = (
        start_top5
        / start_total
    ) * 100


    # Last year data
    end_df = df[
        df["year"] == end_year
    ]

    end_total = end_df["publications"].sum()

    end_top5 = (
        end_df
        .groupby("country")["publications"]
        .sum()
        .sort_values(ascending=False)
        .head(5)
        .sum()
    )

    end_share = (
        end_top5
        / end_total
    ) * 100


    # Difference in percentage points
    concentration_change = (
        end_share
        - start_share
    )

    return round(concentration_change, 1)

# Prepare treemap data
def get_treemap_data(
    df,
    end_year
):
    year_df = df[
        df["year"] == end_year
    ].copy()

    year_df = year_df[
        year_df["publications"] > 0
    ]

    # Get Top 5 countries
    top5 = (
        year_df
        .sort_values(
            "publications",
            ascending=False
        )
        .head(5)["country"]
        .tolist()
    )

    # Rank groups for colouring
    year_df["rank_group"] = "Other Countries"

    if len(top5) >= 1:
        year_df.loc[
            year_df["country"] == top5[0],
            "rank_group"
        ] = "Top 1"

    if len(top5) >= 2:
        year_df.loc[
            year_df["country"] == top5[1],
            "rank_group"
        ] = "Top 2"

    if len(top5) >= 3:
        year_df.loc[
            year_df["country"] == top5[2],
            "rank_group"
        ] = "Top 3"

    if len(top5) >= 4:
        year_df.loc[
            year_df["country"] == top5[3],
            "rank_group"
        ] = "Top 4"

    if len(top5) >= 5:
        year_df.loc[
            year_df["country"] == top5[4],
            "rank_group"
        ] = "Top 5"

    total_publications = (
        year_df["publications"].sum()
    )

    year_df["share"] = (
        year_df["publications"]
        / total_publications
        * 100
    )

    return year_df


# Prepare data for concentration over time chart
def get_concentration_overtime_data(
    df,
    start_year,
    end_year
):
    # Get Top 5 countries from end_year
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

    # Filter selected period
    filtered = df[
        (df["year"] >= start_year)
        & (df["year"] <= end_year)
    ].copy()

    # Group non-top5 countries into Others
    filtered["group"] = filtered["country"]

    filtered.loc[
        ~filtered["country"].isin(top5),
        "group"
    ] = "Others"

    # Aggregate publications
    grouped = (
        filtered
        .groupby(
            ["year", "group"],
            as_index=False
        )["publications"]
        .sum()
    )

    # Calculate yearly total publications
    yearly_total = (
        grouped
        .groupby("year")["publications"]
        .transform("sum")
    )

    # Convert to percentage share
    grouped["share"] = (
        grouped["publications"]
        / yearly_total
        * 100
    )

    return grouped

# Prepare publication trend data
def get_publication_trend_data(
    df,
    start_year,
    end_year
):
    # Get top 5 countries from end_year
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

    # Filter selected period
    filtered = df[
        (df["year"] >= start_year)
        & (df["year"] <= end_year)
    ].copy()

    # Keep only top 5 countries
    filtered = filtered[
        filtered["country"].isin(top5)
    ]

    return filtered


# Find fastest growing AI research countries
def get_fastest_growing_countries(
    df,
    start_year,
    end_year,
    top_n=5
):
    import numpy as np

    # Top 5 publishing countries in end year
    end_df = df[
        df["year"] == end_year
    ]

    current_top5 = (
        end_df
        .sort_values(
            "publications",
            ascending=False
        )
        .head(5)["country"]
        .tolist()
    )

    rows = []

    countries = df["country"].unique()

    for country in countries:

        # Exclude current leaders
        if country in current_top5:
            continue

        country_df = df[
            df["country"] == country
        ]

        start_value = (
            country_df[
                country_df["year"] == start_year
            ]["publications"]
            .sum()
        )

        end_value = (
            country_df[
                country_df["year"] == end_year
            ]["publications"]
            .sum()
        )

        # Avoid divide by zero
        if start_value <= 0:
            continue

        # Publication growth (%)
        growth_rate = (
            (end_value - start_value)
            / start_value
            * 100
        )

        # Growth + Scale Score
        growth_scale_score = (
            growth_rate
            * np.log10(end_value + 1)
        )

        rows.append(
            {
                "country": country,
                "start_publications": start_value,
                "end_publications": end_value,
                "growth_rate": growth_rate,
                "growth_scale_score": growth_scale_score
            }
        )

    growth_df = pd.DataFrame(rows)

    growth_df = (
        growth_df
        .sort_values(
            "growth_scale_score",
            ascending=False
        )
        .head(top_n)
    )

    return growth_df