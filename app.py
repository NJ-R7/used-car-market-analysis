import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Used Car Analysis", layout="wide")

df = pd.read_csv("cardekho_dataset.csv")
df = df.drop(columns=["Unnamed: 0"], errors="ignore")

st.title("🚗 Used Car Market Analysis Dashboard")

st.sidebar.header("Filters")

brand = st.sidebar.selectbox("Select Brand", ["All"] + sorted(df["brand"].unique().tolist()))

fuel = st.sidebar.multiselect("Fuel Type", sorted(df["fuel_type"].unique()), default=sorted(df["fuel_type"].unique()))

transmission = st.sidebar.selectbox("Transmission", ["All"] + sorted(df["transmission_type"].unique()))

seller = st.sidebar.multiselect("Seller Type", sorted(df["seller_type"].unique()), default=sorted(df["seller_type"].unique()))

age = st.sidebar.slider("Vehicle Age", int(df["vehicle_age"].min()), int(df["vehicle_age"].max()), (int(df["vehicle_age"].min()), int(df["vehicle_age"].max())))

price = st.sidebar.slider("Selling Price", int(df["selling_price"].min()), int(df["selling_price"].max()), (int(df["selling_price"].min()), int(df["selling_price"].max())))

filtered = df[
    (df["fuel_type"].isin(fuel)) &
    (df["seller_type"].isin(seller)) &
    (df["vehicle_age"].between(age[0], age[1])) &
    (df["selling_price"].between(price[0], price[1]))
]

if brand != "All":
    filtered = filtered[filtered["brand"] == brand]

if transmission != "All":
    filtered = filtered[filtered["transmission_type"] == transmission]

if filtered.empty:
    st.warning("No cars found. Change the filters.")
    st.stop()

with st.container():
    st.subheader("Key Performance Indicators")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Cars", len(filtered))
    c2.metric("Average Price", f"₹{filtered['selling_price'].mean():,.0f}")
    c3.metric("Average Mileage", f"{filtered['mileage'].mean():.2f} km/l")
    c4.metric("Average Age", f"{filtered['vehicle_age'].mean():.1f} years")

tab1, tab2, tab3 = st.tabs(["Overview", "Visualizations", "Dataset"])

with tab1:
    st.subheader("Category-wise Analysis")

    col1, col2 = st.columns(2)

    with col1:
        brand_count = filtered.groupby("brand").size().reset_index(name="Cars")
        fig1 = px.bar(brand_count, x="brand", y="Cars", title="Cars by Brand")
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        fuel_count = filtered.groupby("fuel_type").size().reset_index(name="Cars")
        fig2 = px.pie(fuel_count, names="fuel_type", values="Cars", title="Fuel Type Distribution")
        st.plotly_chart(fig2, use_container_width=True)

    with st.expander("Numerical Summary"):
        st.dataframe(filtered.describe(), use_container_width=True)

    st.subheader("Data Aggregation")
    st.write("Total Kilometres Driven:", f"{filtered['km_driven'].sum():,}")
    st.write("Maximum Selling Price:", f"₹{filtered['selling_price'].max():,}")
    st.write("Minimum Selling Price:", f"₹{filtered['selling_price'].min():,}")

with tab2:
    st.subheader("Data Visualizations")

    col1, col2 = st.columns(2)

    with col1:
        brand_price = filtered.groupby("brand", as_index=False)["selling_price"].mean()
        fig3 = px.bar(brand_price, x="brand", y="selling_price", title="Average Price by Brand",
                      labels={"selling_price": "Average Price (₹)"})
        st.plotly_chart(fig3, use_container_width=True)

    with col2:
        age_price = filtered.groupby("vehicle_age", as_index=False)["selling_price"].mean()
        fig4 = px.line(age_price, x="vehicle_age", y="selling_price", markers=True,
                       title="Vehicle Age vs Average Price",
                       labels={"vehicle_age": "Vehicle Age", "selling_price": "Average Price (₹)"})
        st.plotly_chart(fig4, use_container_width=True)

    fig5 = px.scatter(filtered, x="km_driven", y="selling_price", color="fuel_type",
                      title="Kilometres Driven vs Selling Price",
                      labels={"km_driven": "Kilometres Driven", "selling_price": "Selling Price (₹)"})
    st.plotly_chart(fig5, use_container_width=True)

with tab3:
    st.subheader("Dataset Explorer")
    st.write("Total Records:", len(filtered))
    st.dataframe(filtered, use_container_width=True)

    st.download_button(
        "Download Filtered Dataset",
        filtered.to_csv(index=False),
        "filtered_cars.csv",
        "text/csv"
    )

st.subheader("Insights")

c1, c2, c3 = st.columns(3)

c1.info(f"Most common brand: {filtered['brand'].mode()[0]}")
c2.info(f"Most common fuel: {filtered['fuel_type'].mode()[0]}")
c3.info(f"Most common transmission: {filtered['transmission_type'].mode()[0]}")