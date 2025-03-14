import streamlit as st
import pandas as pd

# Import custom functions from your modules.
from data_loader import load_and_clean_data, detect_outliers
from analysis import compute_guideline_deviation
from visualization import plot_boxplot, plot_guideline_scatter, view_graph, Chart

# ====================================================
# Sidebar: Navigation
# ====================================================
st.sidebar.title("Navigation")
section = st.sidebar.radio("Choose Section",
                           options=["Dataset Overview", "Outlier Analysis", "Network Graphs",
                                    "Additional Visualizations"])

# ====================================================
# Main Title
# ====================================================
st.title("Stock Trade Outlier Analysis Dashboard")
st.markdown("---")  # Horizontal rule for separation

# ====================================================
# Section 1: Dataset Overview
# ====================================================
if section == "Dataset Overview":
    st.header("Dataset Details (Raw Data)")
    # Load raw data from CSV file
    csv_file = "assets/EURUSD.csv"
    data = pd.read_csv(csv_file)

    # Display basic dataset details
    st.markdown(f"**Total Rows:** {data.shape[0]}")
    st.markdown(f"**Total Columns:** {data.shape[1]}")
    st.markdown("**Column Names:**")
    st.write(data.columns.tolist())
    st.markdown("**Statistical Summary:**")
    st.write(data.describe())

    st.subheader("Data Sample (Before Data Cleaning)")
    st.write(data.head())

    st.markdown("---")
    st.header("Processed Data Sample")
    # Process the data using the helper functions
    processed_data = load_and_clean_data(csv_file)
    processed_data = detect_outliers(processed_data)
    processed_data = compute_guideline_deviation(processed_data)
    st.subheader("Data Sample (After Data Cleaning and Analysis)")
    st.write(processed_data.head(20).tail(5))

# ====================================================
# Section 2: Outlier Analysis
# ====================================================
elif section == "Outlier Analysis":
    st.header("Outlier Detection & Guideline Analysis")
    csv_file = "assets/EURUSD.csv"
    # Process the data
    processed_data = load_and_clean_data(csv_file)
    processed_data = detect_outliers(processed_data)
    processed_data = compute_guideline_deviation(processed_data)

    # Display total outlier count
    total_outliers = processed_data['is_outlier'].sum()
    st.write(f"**Total Outliers:** {total_outliers}")

    # Visual 1: Boxplot of Daily Returns for Outlier Detection
    st.subheader("Boxplot of Daily Returns")
    fig_box = plot_boxplot(processed_data)
    st.pyplot(fig_box)

    st.markdown("---")
    # Visual 2: Scatter Plot for Guideline Comparison (Volume vs Daily Return)
    st.subheader("Trade Volume vs Daily Return")
    fig_scatter = plot_guideline_scatter(processed_data)
    st.pyplot(fig_scatter)

# ====================================================
# Section 3: Network Graphs
# ====================================================
elif section == "Network Graphs":
    st.header("Trade Network Graph Snapshots")

    # Display static snapshots of the Neo4j network graphs (saved as images)
    st.subheader("Graph: 100 Nodes & 156 Relationships")
    st.plotly_chart(view_graph("assets/graph.png", "FX Trade Graph Displaying 100 nodes, 156 relationships"),
                    use_container_width=True)

    st.subheader("Graph: Outlier Nodes Only")
    st.plotly_chart(view_graph("assets/graph2.png", "FX Trade Graph Displaying only outlier nodes"),
                    use_container_width=True)

# ====================================================
# Section 4: Additional Visualizations
# ====================================================
elif section == "Additional Visualizations":
    st.header("Additional Trade Visualizations")
    csv_file = "assets/EURUSD.csv"
    # Process the data for visualizations
    processed_data = load_and_clean_data(csv_file)
    processed_data = detect_outliers(processed_data)
    processed_data = compute_guideline_deviation(processed_data)

    # Create a Chart object that encapsulates multiple visualization functions
    chart_obj = Chart(processed_data)

    st.subheader("Line Chart: Trade Volume Over Time")
    st.plotly_chart(chart_obj.line_chart(), use_container_width=True)

    st.subheader("Scatter Plot: Close Price Over Time")
    st.plotly_chart(chart_obj.scatter_plot(), use_container_width=True)

    st.subheader("Histogram: Betweenness Centrality")
    st.pyplot(chart_obj.betweeness_centrality())

    st.subheader("Bar Chart: Trade Status Counts")
    st.plotly_chart(chart_obj.bar_chart(), use_container_width=True)

# ====================================================
# Summary Report (Displayed at the bottom)
# ====================================================
st.markdown("---")
st.header("Summary Report")
csv_file = "assets/EURUSD.csv"
processed_data = load_and_clean_data(csv_file)
processed_data = detect_outliers(processed_data)
processed_data = compute_guideline_deviation(processed_data)
total_trades = len(processed_data)
total_outliers = processed_data['is_outlier'].sum()
total_guideline_deviations = processed_data['deviates_guideline'].sum()
total_normal = total_trades - total_outliers - total_guideline_deviations

report = f"""
**Trade Graph Summary Report**

- **Total Trades:** {total_trades}
- **Outlier Trades:** {total_outliers}
- **Trades Deviating from Guidelines:** {total_guideline_deviations}
- **Normal Trades:** {total_normal}

**Key Insights:**
- The boxplot shows the distribution of daily returns and highlights outliers.
- The scatter plot reveals deviations in trade volume vs daily return.
- Network graphs provide a visual overview of trade relationships and outlier nodes.
- Additional charts offer deeper insights into trade trends.
"""
st.markdown(report)
