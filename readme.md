
# Stock Trade Outlier Analysis

This project performs outlier detection and network graph analysis on FX trade data. The application leverages Python libraries such as Pandas, Matplotlib, Seaborn, Plotly, and NetworkX to process historical FX trade data from a CSV file. In addition, the project integrates with Neo4j to create a graph representation of trades and similar relationships. An interactive dashboard is built using Streamlit to visualize the data, analysis, and network graphs.

## Project Structure

```
Stock_Trade_Outlier_Analysis/
├── app.py                 # Streamlit dashboard for interactive analysis and visualizations.
├── assets/
│   ├── EURUSD.csv         # Historical FX trade data.
│   ├── graph.png          # Pre-generated network graph snapshot (100 nodes, 156 relationships).
│   └── graph2.png         # Pre-generated network graph snapshot (outlier nodes only).
├── data_loader.py         # Module to load and clean the CSV data.
├── analysis.py            # Module to perform outlier detection and guideline deviation analysis.
├── visualization.py       # Module with functions and Chart class for visualizations.
└── create_graph.py        # Script to create nodes, consecutive and similar relationships in Neo4j.
```

## Installation

1. **Clone the Repository:**

   ```bash
   git clone <repository-url>
   cd Stock_Trade_Outlier_Analysis
   ```

2. **Install Dependencies:**

   Ensure you have Python installed, then run:

   ```bash
   pip install -r requirements.txt
   ```

   *The `requirements.txt` should include:*

   ```
   streamlit
   pandas
   matplotlib
   seaborn
   plotly
   networkx
   neo4j
   ```

## Usage

### 1. Running the Streamlit Dashboard

The Streamlit app provides an interactive interface to explore the FX trade data, view outlier analysis, and visualize network graphs.

Run the dashboard with:

```bash
streamlit run app.py
```

The dashboard includes:
- **Dataset Overview:** Displaying raw and processed data details.
- **Outlier Analysis:** Visualizations such as a boxplot of daily returns and a scatter plot comparing trade volume versus daily return.
- **Network Graphs:** Static snapshots of network graphs (pre-generated from Neo4j).
- **Additional Visualizations:** Charts (line, scatter, histogram, bar) summarizing trade trends and graph metrics.

### 2. Creating the Graph in Neo4j

To build a graph in your local Neo4j database (nodes, consecutive "NEXT" relationships, and "SIMILAR" relationships based on price similarity), run:

```bash
python create_graph.py
```

*Note:* Make sure to update the Neo4j connection parameters (URI and password) in `create_graph.py` according to your local configuration.

## Data Processing Overview

- **Data Loader (`data_loader.py`):**  
  Loads the CSV file, converts the "Gmt time" column to datetime, removes duplicates, and drops rows with zero volume.

- **Outlier Detection:**  
  Daily returns are computed from the "Close" prices. Z-scores are calculated, and trades with an absolute Z-score above a threshold (default is 3) are flagged as outliers.

- **Guideline Deviation Analysis (`analysis.py`):**  
  Trades are flagged as deviating from guidelines if their volume or daily return falls outside expected ranges (defined by percentiles and standard deviations).

## Visualizations

Visualizations are implemented in `visualization.py` and include:
- **Boxplot:** For daily returns to detect outliers.
- **Scatter Plot:** Comparing trade volume vs daily return, with deviations highlighted.
- **Interactive Graph Snapshots:** Displayed using Plotly (`view_graph`) to present pre-generated network graph images.
- **Chart Class:** Encapsulates multiple visualizations (line chart, scatter plot, histogram, bar chart) based on a subset of the data and network metrics.

## Acknowledgements

This project demonstrates a complete workflow for FX trade outlier analysis and network graph visualization, integrating data processing, machine learning techniques, and interactive dashboards with Streamlit and Neo4j.

---
