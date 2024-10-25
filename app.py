import pandas as pd
import streamlit as st
import plotly.express as px
from PIL import Image

st.set_page_config(
    page_title="Haryana Legislative Assembly 2024 Results - In-Depth Analysis",
    layout="wide",
)
st.header("Haryana Legislative Assembly Elections 2024 Results")
st.subheader("Interactive Data Exploration")

try:
    excel_file = "Election.xlsx"
    sheet_name = "DATA"

    df = pd.read_excel(excel_file, sheet_name=sheet_name, usecols="A:E,G:H", header=0)
    df_party = (
        df.groupby("Leading_Party").agg(Seats_Won=("Seats", "sum")).reset_index()
    )  # Pre-aggregate for faster party performance calculations
except FileNotFoundError:
    st.error("Error: 'Election.xlsx' file not found or inaccessible.")
    st.stop()

# Data cleaning
df_party.dropna(inplace=True)
with st.sidebar:
    st.title("Filter & Analyze Results")

    # Constituency multiselect using checkbox
    Constituency_options = df["Constituency"].unique().tolist()
    Constituency_selected = st.multiselect("Constituency", Constituency_options)

    # Leading party multiselect using checkbox
    Party_options = df["Leading_Party"].unique().tolist()
    Party_selected = st.multiselect(
        "Leading Party", Party_options, default=Party_options
    )

    # Margin slider for filtering
    margin = df["Margin"].unique().tolist()
    margin_selection = st.slider(
        "Margin:", min(margin), max(margin), value=(min(margin), max(margin))
    )

# Dynamic filtering based on user selections
mask = (
    (df["Constituency"].isin(Constituency_selected) if Constituency_selected else True)
    & (df["Leading_Party"].isin(Party_selected) if Party_selected else True)
    & df["Margin"].between(*margin_selection)
)

df_filtered = df[mask]

df = pd.read_excel(excel_file, sheet_name=sheet_name, usecols="A:E", header=0)

df_party = pd.read_excel(excel_file, sheet_name=sheet_name, usecols="G:H", header=0)
st.dataframe(df)
df_party.dropna(inplace=True)
col1, col2 = st.columns(2)
pie_chart = px.pie(
    df_party, title="Seat Sharing % Of Parties", values="Seats", names="Party_Name"
)

col1.plotly_chart(pie_chart)

col2.dataframe(df_party)

if st.checkbox("Analyze Party Performance by Constituency"):
    constituency_selection = st.selectbox(
        "Select Constituency", df_filtered["Constituency"].unique()
    )
    constituency_df = df_filtered[df_filtered["Constituency"] == constituency_selection]
    constituency_chart = px.bar(
        constituency_df,
        x="Leading_Party",
        y="Margin",
        title="Margin by Party in " + constituency_selection,
        color="Leading_Party",
        color_discrete_sequence=["#F63366", "#3366CC", "#99FF99"],
        template="plotly_white",
        labels={"Leading_Party": "Party", "Margin": "Margin (Votes)"},
    )
    st.plotly_chart(constituency_chart)


# 2. Margin Distribution:
margin_dist_chart = px.histogram(
    df_filtered,
    x="Margin",
    title="Margin Distribution",
    color="Leading_Party",
    color_discrete_sequence=["#F63366", "#3366CC", "#99FF99"],
)
st.plotly_chart(margin_dist_chart)


# Trend Analysis (if applicable):

colw1, colw2 = st.columns([1, 3])
# Bar chart with clearer title, informative labels, and color styling
df_grouped = (
    df_filtered.groupby(by=["Leading_Party"])["Constituency"].count().reset_index()
)
df_groupe = df_filtered["Constituency"]
colw1.dataframe(df_groupe, width=250)
bar_chart = px.bar(
    df_grouped,
    x="Leading_Party",
    y="Constituency",
    title="Constituency Count by Leading Party",
    color="Leading_Party",
    color_discrete_sequence=["#F63366", "#3366CC", "#99FF99"],
    width=900,
    template="plotly_white",
    labels={"Leading_Party": "Party", "Constituency": "Constituency Count"},
)
colw2.width = 9000
colw2.plotly_chart(bar_chart)
# Top/Bottom Performing Constituencies:
# Display results
top_n = st.number_input(
    "Number of Top/Bottom Performing Constituencies",
    min_value=1,
    max_value=df_filtered.shape[0],
)
winning_df = df_filtered.sort_values(by="Margin", ascending=False).head(top_n)
losing_df = df_filtered.sort_values(by="Margin", ascending=True).head(top_n)
winning_df_subset = winning_df.iloc[:, :5]
losing_df_subset = losing_df.iloc[:, :5]


st.header("Top Performing Constituencies:")

st.dataframe(
    winning_df_subset.style.apply(
        lambda x: [
            "background-color: lightgreen" if x[0] == "Leading_Party" else "" for _ in x
        ],
        axis=1,
    ),
    use_container_width=True,
)
st.header("Bottom Performing Constituencies:")
st.dataframe(
    losing_df_subset.style.apply(
        lambda x: [
            "background-color: lightcoral" if x[0] == "Leading_Party" else "" for _ in x
        ],
        axis=1,
    ),
    use_container_width=True,
)
Constituency = df["Constituency"].unique().tolist()
Party = df["Leading_Party"].unique().tolist()
margin = df["Margin"].unique().tolist()


# Party Comparison:

Party_selection = st.multiselect("Party:", Party, default=Party)
mask = df["Leading_Party"].isin(Party_selection)
number_of_result = df[mask].shape[0]
st.markdown(f"*Available Results: {number_of_result}*")


df_grouped = df[mask].groupby(by=["Leading_Party"])["Constituency"].count()


bar_chart = px.bar(
    df_grouped,
    color_discrete_sequence=["#F63366"] * len(df_grouped),
    template="plotly_white",
)
st.plotly_chart(bar_chart)
# new
# User input for chart type
chart_type = st.selectbox("Select Chart Type", ["Line Chart", "Bar Chart"])

# User input for x and y axes (flexible)
x_axis = st.selectbox("Select X-axis Variable", df_filtered.columns)
y_axis = st.selectbox("Select Y-axis Variable", df_filtered.columns)

if chart_type == "Line Chart":
    line_chart = px.line(
        df_filtered, x=x_axis, y=y_axis, title=f"{y_axis} vs. {x_axis}"
    )
    st.plotly_chart(line_chart)
else:
    bar_chart = px.bar(
        df_filtered,
        x=x_axis,
        y=y_axis,
        title=f"{y_axis} by {x_axis}",
        color="Leading_Party",
        color_discrete_sequence=["#F63366", "#3366CC", "#99FF99"],
    )
    st.plotly_chart(bar_chart)

    # boxplot
box_plot = px.box(
    df_filtered, x="Leading_Party", y="Margin", title="Margin Distribution by Party"
)
st.plotly_chart(box_plot)
if "Seats" in df_filtered.columns:
    pie_chart = px.pie(
        df_filtered.groupby("Leading_Party")["Seats"].sum(),
        names=df_filtered["Leading_Party"].unique(),
        title="Seats Won by Party Filtered",
    )
    st.plotly_chart(pie_chart)

import numpy as np
x = df_filtered["Margin"]
y = df_filtered["Margin"]

m, b = np.polyfit(x, y, 1)  # Linear regression

# Create the scatter plot with regression line
scatter_chart = px.scatter(
    df_filtered,
    x="Margin",
    y="Round",
    title="Margin vs. Rounds Polled",
    color="Leading_Party",
    color_discrete_sequence=["#F63366", "#3366CC", "#99FF99"],
)
st.plotly_chart(scatter_chart)


#about us
st.subheader("Developing Team")
co1, co2,co3 = st.columns(3)

image = Image.open("himanshuarora.png")
co1.image(
    image,
    caption="Himanshu Arora - Team Leader",
    width=100,
    use_column_width=True

)
image = Image.open("krish.png")
co2.image(
    image,
    caption="Krish Verma",
    width=100,
    use_column_width=True
)
image = Image.open("sahil.png")
co3.image(
    image,
    caption="Sahil",
    width=100,
    use_column_width=True
)

