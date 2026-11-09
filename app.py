import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------------------------
# PAGE CONFIGURATION
# -------------------------------------------------
st.set_page_config(
    page_title="Used Car Market Analysis",
    page_icon="🚗",
    layout="wide"
)

# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------
@st.cache_data
def load_data(file):
    data = pd.read_csv(file)

    # Remove unnecessary index column, if present
    data = data.loc[:, ~data.columns.str.contains(r"^Unnamed")]

    # Convert numerical columns safely
    numeric_columns = [
        "vehicle_age", "km_driven", "mileage",
        "engine", "max_power", "seats", "selling_price"
    ]

    for column in numeric_columns:
        if column in data.columns:
            data[column] = pd.to_numeric(data[column], errors="coerce")

    return data


st.title("🚗 Used Car Market Analysis Dashboard")
st.write(
    "An interactive dashboard to explore used-car prices, brands, "
    "fuel types, mileage and vehicle characteristics."
)

uploaded_file = st.sidebar.file_uploader(
    "Upload CarDekho CSV file",
    type=["csv"]
)

try:
    if uploaded_file is not None:
        df = load_data(uploaded_file)
    else:
        df = load_data("cardekho_dataset.csv")
except FileNotFoundError:
    st.error(
        "Dataset not found. Keep cardekho_dataset.csv in the same folder "
        "as app.py, or upload the CSV using the sidebar."
    )
    st.stop()
except Exception as error:
    st.error(f"Unable to read the dataset: {error}")
    st.stop()

required_columns = [
    "car_name", "brand", "model", "vehicle_age", "km_driven",
    "seller_type", "fuel_type", "transmission_type", "mileage",
    "engine", "max_power", "seats", "selling_price"
]

missing_columns = [column for column in required_columns if column not in df.columns]

if missing_columns:
    st.error(f"Dataset is missing these required columns: {missing_columns}")
    st.stop()

# Remove rows that have no useful values in important fields
df = df.dropna(subset=["brand", "selling_price"])

if df.empty:
    st.error("The dataset does not contain usable car records.")
    st.stop()

# -------------------------------------------------
# SIDEBAR FILTERS
# -------------------------------------------------
st.sidebar.header("🔎 Filter Cars")

brands = ["All"] + sorted(df["brand"].dropna().unique().tolist())
selected_brand = st.sidebar.selectbox("Select Brand", brands)

fuel_options = sorted(df["fuel_type"].dropna().unique().tolist())
selected_fuels = st.sidebar.multiselect(
    "Select Fuel Type",
    fuel_options,
    default=fuel_options
)

transmission_options = ["All"] + sorted(
    df["transmission_type"].dropna().unique().tolist()
)
selected_transmission = st.sidebar.selectbox(
    "Select Transmission",
    transmission_options
)

seller_options = sorted(df["seller_type"].dropna().unique().tolist())
selected_sellers = st.sidebar.multiselect(
    "Select Seller Type",
    seller_options,
    default=seller_options
)

min_age = int(df["vehicle_age"].min())
max_age = int(df["vehicle_age"].max())

age_range = st.sidebar.slider(
    "Vehicle Age (Years)",
    min_value=min_age,
    max_value=max_age,
    value=(min_age, max_age)
)

min_price = int(df["selling_price"].min())
max_price = int(df["selling_price"].max())

price_range = st.sidebar.slider(
    "Selling Price (₹)",
    min_value=min_price,
    max_value=max_price,
    value=(min_price, max_price),
    step=max(1, (max_price - min_price) // 100)
)

# -------------------------------------------------
# APPLY FILTERS
# -------------------------------------------------
filtered_df = df.copy()

if selected_brand != "All":
    filtered_df = filtered_df[filtered_df["brand"] == selected_brand]

filtered_df = filtered_df[
    filtered_df["fuel_type"].isin(selected_fuels)
]

if selected_transmission != "All":
    filtered_df = filtered_df[
        filtered_df["transmission_type"] == selected_transmission
    ]

filtered_df = filtered_df[
    filtered_df["seller_type"].isin(selected_sellers)
]

filtered_df = filtered_df[
    filtered_df["vehicle_age"].between(age_range[0], age_range[1])
]

filtered_df = filtered_df[
    filtered_df["selling_price"].between(price_range[0], price_range[1])
]

# -------------------------------------------------
# HANDLE EMPTY FILTER RESULT
# -------------------------------------------------
if filtered_df.empty:
    st.warning("No cars match the selected filters. Please change the filters.")
    st.stop()

# -------------------------------------------------
# KPI DASHBOARD
# -------------------------------------------------
st.subheader("📊 Key Performance Indicators")

total_cars = len(filtered_df)
average_age = filtered_df["vehicle_age"].mean()
average_km = filtered_df["km_driven"].mean()
average_price = filtered_df["selling_price"].mean()
average_mileage = filtered_df["mileage"].mean()
total_km = filtered_df["km_driven"].sum()

with st.container():
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Cars", f"{total_cars:,}")
    col2.metric("Average Vehicle Age", f"{average_age:.2f} years")
    col3.metric("Average KM Driven", f"{average_km:,.0f} km")
    col4.metric("Average Selling Price", f"₹{average_price:,.0f}")

col5, col6 = st.columns(2)
col5.metric("Average Mileage", f"{average_mileage:.2f} km/l")
col6.metric("Total KM Driven", f"{total_km:,.0f} km")

st.divider()

# -------------------------------------------------
# TABS
# -------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "Overview",
    "Brand Analysis",
    "Price Analysis",
    "Dataset Explorer"
])

# -------------------------------------------------
# TAB 1: OVERVIEW
# -------------------------------------------------
with tab1:
    st.header("Dataset Overview")

    left, right = st.columns(2)

    with left:
        st.subheader("Cars by Fuel Type")
        fuel_counts = (
            filtered_df.groupby("fuel_type")
            .size()
            .reset_index(name="Number of Cars")
        )

        fig_fuel = px.bar(
            fuel_counts,
            x="fuel_type",
            y="Number of Cars",
            title="Number of Cars by Fuel Type",
            labels={
                "fuel_type": "Fuel Type",
                "Number of Cars": "Number of Cars"
            },
            text="Number of Cars"
        )
        st.plotly_chart(fig_fuel, use_container_width=True)

    with right:
        st.subheader("Cars by Transmission")
        transmission_counts = (
            filtered_df.groupby("transmission_type")
            .size()
            .reset_index(name="Number of Cars")
        )

        fig_transmission = px.pie(
            transmission_counts,
            names="transmission_type",
            values="Number of Cars",
            title="Transmission Type Distribution"
        )
        st.plotly_chart(fig_transmission, use_container_width=True)

    with st.expander("View numerical summary"):
        st.write(filtered_df.select_dtypes(include="number").describe())

# -------------------------------------------------
# TAB 2: BRAND ANALYSIS
# -------------------------------------------------
with tab2:
    st.header("Brand Analysis")

    brand_summary = (
        filtered_df.groupby("brand")
        .agg(
            Number_of_Cars=("car_name", "count"),
            Average_Price=("selling_price", "mean"),
            Average_Mileage=("mileage", "mean")
        )
        .reset_index()
        .sort_values("Number_of_Cars", ascending=False)
    )

    fig_brand = px.bar(
        brand_summary,
        x="brand",
        y="Number_of_Cars",
        title="Number of Cars by Brand",
        labels={
            "brand": "Car Brand",
            "Number_of_Cars": "Number of Cars"
        },
        text="Number_of_Cars"
    )
    fig_brand.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_brand, use_container_width=True)

    st.subheader("Brand-wise Summary")
    st.dataframe(brand_summary, use_container_width=True)

# -------------------------------------------------
# TAB 3: PRICE ANALYSIS
# -------------------------------------------------
with tab3:
    st.header("Used Car Price Analysis")

    # Bar chart: average selling price by brand
    average_price_by_brand = (
        filtered_df.groupby("brand", as_index=False)["selling_price"]
        .mean()
        .sort_values("selling_price", ascending=False)
    )

    fig_price = px.bar(
        average_price_by_brand,
        x="brand",
        y="selling_price",
        title="Average Selling Price by Brand",
        labels={
            "brand": "Car Brand",
            "selling_price": "Average Selling Price (₹)"
        }
    )
    fig_price.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_price, use_container_width=True)

    # Line chart: average selling price by vehicle age
    age_price = (
        filtered_df.groupby("vehicle_age", as_index=False)["selling_price"]
        .mean()
        .sort_values("vehicle_age")
    )

    fig_line = px.line(
        age_price,
        x="vehicle_age",
        y="selling_price",
        markers=True,
        title="Average Selling Price by Vehicle Age",
        labels={
            "vehicle_age": "Vehicle Age (Years)",
            "selling_price": "Average Selling Price (₹)"
        }
    )
    st.plotly_chart(fig_line, use_container_width=True)

    # Scatter plot: kilometres driven versus selling price
    fig_scatter = px.scatter(
        filtered_df,
        x="km_driven",
        y="selling_price",
        color="fuel_type",
        hover_data=["car_name", "brand", "vehicle_age"],
        title="Kilometres Driven vs Selling Price",
        labels={
            "km_driven": "Kilometres Driven",
            "selling_price": "Selling Price (₹)",
            "fuel_type": "Fuel Type"
        }
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

# -------------------------------------------------
# TAB 4: DATASET EXPLORER
# -------------------------------------------------
with tab4:
    st.header("Explore Car Records")

    st.write(
        f"Showing **{len(filtered_df):,}** records after applying the filters."
    )

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )

    with st.expander("Dataset information"):
        info_df = pd.DataFrame({
            "Column": df.columns,
            "Data Type": df.dtypes.astype(str).values,
            "Missing Values": df.isnull().sum().values
        })
        st.dataframe(info_df, use_container_width=True, hide_index=True)

    csv_data = filtered_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Filtered Data as CSV",
        data=csv_data,
        file_name="filtered_cardekho_cars.csv",
        mime="text/csv"
    )

# -------------------------------------------------
# INSIGHTS
# -------------------------------------------------
st.divider()
st.subheader("💡 Quick Insights")

most_common_brand = filtered_df["brand"].mode().iloc[0]
most_common_fuel = filtered_df["fuel_type"].mode().iloc[0]
most_common_transmission = filtered_df["transmission_type"].mode().iloc[0]

insight1, insight2, insight3 = st.columns(3)

insight1.info(f"Most represented brand: **{most_common_brand}**")
insight2.info(f"Most common fuel type: **{most_common_fuel}**")
insight3.info(
    f"Most common transmission: **{most_common_transmission}**"
)

st.caption(
    "Used Car Market Analysis Dashboard | Built with Python, Pandas, "
    "Plotly and Streamlit"
)
