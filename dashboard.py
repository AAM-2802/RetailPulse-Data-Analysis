# Import necessary libraries
import pandas as pd
import plotly.express as px
import streamlit as st

# Load the dataset
sales_data = pd.read_csv("sales_data_with_weather.csv")
sales_data["Order_Date"] = pd.to_datetime(sales_data["Order_Date"])

# Streamlit App
st.set_page_config(page_title="Retail Dashboard", layout="wide")

# Title
st.title("Retail Dashboard")

# Sidebar Filters
st.sidebar.header("Filters")
store_filter = st.sidebar.multiselect(
    "Select Store(s):", 
    options=sales_data["City"].unique(), 
    default=sales_data["City"].unique()
)
category_filter = st.sidebar.multiselect(
    "Select Product Category(s):", 
    options=sales_data["Category"].unique(), 
    default=sales_data["Category"].unique()
)
region_filter = st.sidebar.multiselect(
    "Select Region(s):", 
    options=sales_data["Region"].unique(), 
    default=sales_data["Region"].unique()
)

# Filter the data
filtered_data = sales_data[
    (sales_data["City"].isin(store_filter)) &
    (sales_data["Category"].isin(category_filter)) &
    (sales_data["Region"].isin(region_filter))
]

# Key Metrics
st.header("Key Metrics")
total_sales = filtered_data["Total_Sales"].sum()
average_spend = filtered_data["Avg_Spend"].mean()
top_product = (
    filtered_data.groupby("Product_ID")["Total_Sales"].sum().idxmax()
    if not filtered_data.empty else "N/A"
)
top_region = (
    filtered_data.groupby("Region")["Total_Sales"].sum().idxmax()
    if not filtered_data.empty else "N/A"
)
st.markdown(f"**Total Sales:** ₹{total_sales:,.2f}")
st.markdown(f"**Average Spend per Customer:** ₹{average_spend:,.2f}")
st.markdown(f"**Top Product:** {top_product}")
st.markdown(f"**Top Region:** {top_region}")

# Sales Trends
st.header("Sales Trends")
sales_trends = filtered_data.groupby(
    filtered_data["Order_Date"].dt.to_period("M")
)["Total_Sales"].sum().reset_index()
sales_trends["Order_Date"] = sales_trends["Order_Date"].astype(str)
fig_sales_trends = px.line(
    sales_trends, 
    x="Order_Date", 
    y="Total_Sales", 
    title="Monthly Sales Trends", 
    labels={"Order_Date": "Month", "Total_Sales": "Sales"}
)
st.plotly_chart(fig_sales_trends)

# Customer Insights
st.header("Customer Insights")
customer_segments = filtered_data["Segment"].value_counts().reset_index()
customer_segments.columns = ["Segment", "Count"]
fig_segments = px.bar(
    customer_segments, 
    x="Segment", 
    y="Count", 
    title="Customer Segment Distribution",
    labels={"Segment": "Customer Segment", "Count": "Count"}
)
st.plotly_chart(fig_segments)

# Store Performance
st.header("Store Performance")
geo_sales = filtered_data.groupby("Region")["Total_Sales"].sum().reset_index()
fig_geo_sales = px.choropleth(
    geo_sales,
    locations="Region",
    locationmode="USA-states",  # Update as per your dataset
    color="Total_Sales",
    title="Region-Wise Sales Performance",
    labels={"Total_Sales": "Sales"}
)
st.plotly_chart(fig_geo_sales)

# Top 10 High-Performing Stores
st.subheader("Top 10 High-Performing Stores")
top_stores = filtered_data.groupby("City")["Total_Sales"].sum().sort_values(ascending=False).head(10).reset_index()
fig_top_stores = px.bar(
    top_stores,
    x="City",
    y="Total_Sales",
    title="Top 10 Stores by Sales",
    labels={"City": "Store", "Total_Sales": "Sales"}
)
st.plotly_chart(fig_top_stores)

# External Factors: Correlation between Weather and Sales
st.header("Impact of External Factors")

# Check for external factor columns and debug missing data
if "Temperature" in filtered_data.columns and "Rainfall" in filtered_data.columns and "Holiday_Flag" in filtered_data.columns:
    st.markdown("### External Factor Data Available")
    
    # Debug filtered data
    st.dataframe(filtered_data[["Temperature", "Rainfall", "Holiday_Flag", "Total_Sales"]].head())

    # Correlation matrix
    external_factors = filtered_data[["Total_Sales", "Holiday_Flag", "Temperature", "Rainfall"]].corr()
    fig_corr = px.imshow(
        external_factors,
        text_auto=True,
        title="Correlation between Sales and External Factors"
    )
    st.plotly_chart(fig_corr)

    # Descriptive analysis
    avg_temp = filtered_data["Temperature"].mean()
    avg_rainfall = filtered_data["Rainfall"].mean()
    holiday_sales = filtered_data[filtered_data["Holiday_Flag"] == 1]["Total_Sales"].mean()
    non_holiday_sales = filtered_data[filtered_data["Holiday_Flag"] == 0]["Total_Sales"].mean()

    st.subheader("Insights from External Factors")
    st.markdown(f"**Average Temperature:** {avg_temp:.2f}°C")
    st.markdown(f"**Average Rainfall:** {avg_rainfall:.2f} mm")
    st.markdown(f"**Average Sales on Holidays:** ₹{holiday_sales:,.2f}")
    st.markdown(f"**Average Sales on Non-Holidays:** ₹{non_holiday_sales:,.2f}")

    # Highlight key insights
    st.markdown("### Observations:")
    if holiday_sales > non_holiday_sales:
        st.markdown("- Sales are higher on holidays compared to regular days.")
    else:
        st.markdown("- Sales are relatively stable or lower on holidays compared to regular days.")

    if avg_temp > 25:
        st.markdown("- Higher temperatures correlate with increased sales of seasonal products.")
    else:
        st.markdown("- Cooler temperatures might indicate lower sales activity in certain regions.")

    if avg_rainfall > 50:
        st.markdown("- Rainy weather could negatively impact store visits and sales.")
    else:
        st.markdown("- Minimal rainfall seems to have a neutral or positive impact on sales.")
else:
    st.markdown("No external factor data is available for the current selection.")
    st.markdown("Ensure your dataset contains `Temperature`, `Rainfall`, and `Holiday_Flag` columns.")