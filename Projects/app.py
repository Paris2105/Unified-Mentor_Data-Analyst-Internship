
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(
    page_title="France Top 50 Analysis",
    page_icon="🎵",
    layout="wide"
)

@st.cache_data
def load_data():
    df = pd.read_csv("cleaned_france_top50.csv")
    df["date"] = pd.to_datetime(df["date"])
    return df

df = load_data()

st.title("🎵 France Top 50 Playlist Analysis")
st.markdown(
    "### Audience Sensitivity, Content Compliance & Format Preference Analysis"
)
st.write(
    "Analysis of explicit content, release format, album structure and song duration "
    "in daily France Top 50 snapshots."
)

st.sidebar.header("Filters")

min_date = df["date"].min().date()
max_date = df["date"].max().date()

date_range = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if isinstance(date_range, tuple):
    if len(date_range) == 2:
        start_date = pd.Timestamp(date_range[0])
        end_date = pd.Timestamp(date_range[1])
        filtered_df = df[
            (df["date"] >= start_date) &
            (df["date"] <= end_date)
        ].copy()
    else:
        selected_date = pd.Timestamp(date_range[0])
        filtered_df = df[df["date"] == selected_date].copy()
else:
    selected_date = pd.Timestamp(date_range)
    filtered_df = df[df["date"] == selected_date].copy()

rank_tier = st.sidebar.selectbox(
    "Rank Tier",
    ["Top 10", "Top 25", "Top 50"]
)

if rank_tier == "Top 10":
    filtered_df = filtered_df[filtered_df["position"] <= 10]
elif rank_tier == "Top 25":
    filtered_df = filtered_df[filtered_df["position"] <= 25]

explicit_filter = st.sidebar.selectbox(
    "Explicit Content",
    ["All", "Explicit", "Clean"]
)

if explicit_filter == "Explicit":
    filtered_df = filtered_df[filtered_df["is_explicit"] == True]
elif explicit_filter == "Clean":
    filtered_df = filtered_df[filtered_df["is_explicit"] == False]

album_filter = st.sidebar.multiselect(
    "Album Type",
    ["album", "single", "compilation"],
    default=["album", "single"]
)

if album_filter:
    filtered_df = filtered_df[
        filtered_df["album_type"].isin(album_filter)
    ]

if len(filtered_df) > 0:
    explicit_share = filtered_df["is_explicit"].mean() * 100
    avg_duration = filtered_df["duration_min"].mean()
    avg_popularity = filtered_df["popularity"].mean()
    avg_rank = filtered_df["position"].mean()

    rank_score = 100 * (51 - filtered_df["position"]) / 50
    acceptance_score = (
        0.5 * rank_score + 0.5 * filtered_df["popularity"]
    ).mean()
else:
    explicit_share = 0
    avg_duration = 0
    avg_popularity = 0
    avg_rank = 0
    acceptance_score = 0

st.subheader("Key Performance Indicators")

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("Explicit Share", f"{explicit_share:.1f}%")
c2.metric("Avg Duration", f"{avg_duration:.2f} min")
c3.metric("Avg Popularity", f"{avg_popularity:.1f}")
c4.metric("Avg Chart Position", f"{avg_rank:.1f}")
c5.metric("Acceptance Score", f"{acceptance_score:.1f}")

st.divider()

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "Overview",
        "Explicit Content",
        "Release Format",
        "Album Structure",
        "Song Duration"
    ]
)

with tab1:
    st.header("Overall Overview")

    col1, col2 = st.columns(2)

    with col1:
        data = (
            filtered_df["is_explicit"]
            .map({True: "Explicit", False: "Clean"})
            .value_counts()
            .reset_index()
        )
        data.columns = ["Content", "Count"]

        fig = px.pie(
            data,
            names="Content",
            values="Count",
            title="Explicit vs Clean Content"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        data = (
            filtered_df["album_type"]
            .value_counts()
            .reset_index()
        )
        data.columns = ["Album Type", "Count"]

        fig = px.bar(
            data,
            x="Album Type",
            y="Count",
            title="Release Format Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)

    summary = pd.DataFrame({
        "Metric": [
            "Tracks",
            "Explicit Share",
            "Average Popularity",
            "Average Duration",
            "Average Chart Position"
        ],
        "Value": [
            len(filtered_df),
            f"{explicit_share:.2f}%",
            f"{avg_popularity:.2f}",
            f"{avg_duration:.2f} min",
            f"{avg_rank:.2f}"
        ]
    })

    st.subheader("Filtered Summary")
    st.dataframe(summary, use_container_width=True, hide_index=True)

with tab2:
    st.header("Explicit Content Analysis")

    exp = (
        filtered_df
        .groupby("is_explicit")
        .agg(
            avg_rank=("position", "mean"),
            avg_popularity=("popularity", "mean"),
            track_count=("song", "count")
        )
        .reset_index()
    )

    exp["Content"] = exp["is_explicit"].map(
        {True: "Explicit", False: "Clean"}
    )

    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(
            exp,
            x="Content",
            y="avg_popularity",
            title="Average Popularity: Explicit vs Clean",
            text_auto=".1f"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.bar(
            exp,
            x="Content",
            y="avg_rank",
            title="Average Chart Position",
            text_auto=".1f"
        )
        fig.update_yaxes(autorange="reversed")
        st.plotly_chart(fig, use_container_width=True)

    groups = []

    for name, condition in [
        ("1-10", filtered_df["position"] <= 10),
        ("11-25", filtered_df["position"].between(11, 25)),
        ("26-50", filtered_df["position"].between(26, 50))
    ]:
        temp = filtered_df[condition]
        if len(temp) > 0:
            groups.append({
                "Rank Group": name,
                "Explicit Share": temp["is_explicit"].mean() * 100
            })

    groups_df = pd.DataFrame(groups)

    fig = px.bar(
        groups_df,
        x="Rank Group",
        y="Explicit Share",
        title="Explicit Content Share by Rank Group",
        text_auto=".1f"
    )
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.header("Release Format Analysis")

    format_df = filtered_df[
        filtered_df["album_type"].isin(["single", "album"])
    ].copy()

    if len(format_df) > 0:
        summary = (
            format_df
            .groupby("album_type")
            .agg(
                average_popularity=("popularity", "mean"),
                average_rank=("position", "mean"),
                track_count=("song", "count")
            )
            .reset_index()
        )

        col1, col2 = st.columns(2)

        with col1:
            fig = px.bar(
                summary,
                x="album_type",
                y="average_popularity",
                title="Popularity by Release Format",
                text_auto=".1f"
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.bar(
                summary,
                x="album_type",
                y="average_rank",
                title="Average Rank by Release Format",
                text_auto=".1f"
            )
            fig.update_yaxes(autorange="reversed")
            st.plotly_chart(fig, use_container_width=True)

        fig = px.box(
            format_df,
            x="album_type",
            y="popularity",
            title="Popularity Distribution by Release Format"
        )
        st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.header("Album Structure Analysis")

    fig = px.histogram(
        filtered_df,
        x="total_tracks",
        nbins=30,
        title="Album Size Distribution"
    )
    st.plotly_chart(fig, use_container_width=True)

    album_scatter = filtered_df[
        filtered_df["album_type"] == "album"
    ].copy()

    if len(album_scatter) > 0:
        fig = px.scatter(
            album_scatter,
            x="total_tracks",
            y="popularity",
            hover_data=["song", "artist", "position"],
            title="Album Size vs Popularity"
        )
        st.plotly_chart(fig, use_container_width=True)

        album_scatter["album_size_bucket"] = pd.cut(
            album_scatter["total_tracks"],
            bins=[0, 10, 15, 20, np.inf],
            labels=[
                "Small (1-10)",
                "Medium (11-15)",
                "Large (16-20)",
                "Very Large (21+)"
            ]
        )

        album_summary = (
            album_scatter
            .groupby("album_size_bucket", observed=True)
            .agg(
                average_popularity=("popularity", "mean"),
                average_rank=("position", "mean"),
                track_count=("song", "count")
            )
            .reset_index()
        )

        st.dataframe(
            album_summary,
            use_container_width=True,
            hide_index=True
        )

with tab5:
    st.header("Song Duration Analysis")

    duration_valid = filtered_df[
        filtered_df["duration_min"].notna()
    ].copy()

    fig = px.histogram(
        duration_valid,
        x="duration_min",
        nbins=30,
        title="Song Duration Distribution"
    )
    st.plotly_chart(fig, use_container_width=True)

    duration_valid["duration_bucket"] = pd.cut(
        duration_valid["duration_min"],
        bins=[-np.inf, 2, 3, 4, np.inf],
        labels=["<2 min", "2-3 min", "3-4 min", ">4 min"]
    )

    duration_summary = (
        duration_valid
        .groupby("duration_bucket", observed=True)
        .agg(
            average_popularity=("popularity", "mean"),
            average_rank=("position", "mean"),
            track_count=("song", "count")
        )
        .reset_index()
    )

    fig = px.bar(
        duration_summary,
        x="duration_bucket",
        y="average_popularity",
        title="Popularity by Duration Bucket",
        text_auto=".1f"
    )
    st.plotly_chart(fig, use_container_width=True)

    fig = px.scatter(
        duration_valid,
        x="duration_min",
        y="position",
        hover_data=["song", "artist", "popularity"],
        title="Duration vs Chart Position"
    )
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, use_container_width=True)

st.divider()
st.caption(
    "France Top 50 Content Analysis | Atlantic Recording Corporation"
)
