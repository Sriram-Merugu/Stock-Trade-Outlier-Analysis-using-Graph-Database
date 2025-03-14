import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
import plotly.express as px
import networkx as nx


def plot_boxplot(data):
    """
    Boxplot of daily returns to visualize outliers.

    Parameters:
        data (DataFrame): Processed trade data containing the 'Return' column.

    Returns:
        fig (Figure): Matplotlib figure object for the boxplot.
    """
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.boxplot(y=data['Return'], ax=ax, showfliers=True)
    ax.set_title("Boxplot of Daily Returns with Outliers")
    ax.set_ylabel("Daily Return")
    plt.tight_layout()
    return fig


def plot_guideline_scatter(data):
    """
    Scatter plot of Volume vs Daily Return with guideline boundaries.

    Trades deviating from the guidelines are colored red; others are blue.
    The guideline boundaries are defined as:
      - Volume: [25th percentile, 75th percentile]
      - Daily Return: [mean - 2*std, mean + 2*std]

    Parameters:
        data (DataFrame): Processed trade data with 'Volume', 'Return', and 'deviates_guideline' columns.

    Returns:
        fig (Figure): Matplotlib figure object for the scatter plot.
    """
    # Calculate guideline boundaries
    volume_min = data['Volume'].quantile(0.25)
    volume_max = data['Volume'].quantile(0.75)
    mean_return = data['Return'].mean()
    std_return = data['Return'].std()
    return_min = mean_return - 2 * std_return
    return_max = mean_return + 2 * std_return

    # Create scatter plot
    fig, ax = plt.subplots(figsize=(10, 6))
    # Color mapping: red if trade deviates from guideline, blue otherwise.
    colors = data['deviates_guideline'].map({True: 'red', False: 'blue'})
    ax.scatter(data['Return'], data['Volume'], c=colors, alpha=0.6)

    # Set axis labels and title
    ax.set_xlabel('Daily Return')
    ax.set_ylabel('Volume')
    ax.set_title('Trade Volume vs Daily Return\nRed = Deviation from Guidelines')

    # Draw guideline boundaries
    ax.axhline(y=volume_min, color='green', linestyle='--', label='Volume Lower Bound')
    ax.axhline(y=volume_max, color='green', linestyle='--', label='Volume Upper Bound')
    ax.axvline(x=return_min, color='orange', linestyle='--', label='Return Lower Bound')
    ax.axvline(x=return_max, color='orange', linestyle='--', label='Return Upper Bound')

    ax.legend()
    return fig


def view_graph(path, title):
    """
    Load an image from a file and create an interactive Plotly figure.

    This is useful for displaying pre-generated network graph snapshots.

    Parameters:
        path (str): The file path of the image.
        title (str): The title to display on the Plotly figure.

    Returns:
        fig (Figure): Interactive Plotly figure with zoom/pan enabled.
    """
    img = Image.open(path)
    fig = px.imshow(img, title=title)
    fig.update_xaxes(showticklabels=False)
    fig.update_yaxes(showticklabels=False)
    # Set a large initial size
    fig.update_layout(width=1200, height=800)
    return fig


class Chart:
    """
    Encapsulates multiple trade visualization charts.

    Attributes:
        df (DataFrame): A subset (first 100 rows) of the processed trade data.
        G (DiGraph): A NetworkX directed graph built from the trade data.
    """

    def __init__(self, data):
        # Use only the first 100 rows for visualization
        self.df = data[:100]
        self.G = nx.DiGraph()

        # Create graph nodes using the "Gmt time" as a unique identifier in ISO format.
        for index, row in self.df.iterrows():
            trade_timestamp = row["Gmt time"]
            trade_id = trade_timestamp.isoformat()
            self.G.add_node(trade_id,
                            timestamp=trade_timestamp,
                            open=float(row["Open"]),
                            high=float(row["High"]),
                            low=float(row["Low"]),
                            close=float(row["Close"]),
                            volume=float(row["Volume"]),
                            is_outlier=row["is_outlier"],
                            deviates_guideline=row["deviates_guideline"])

        # Create consecutive "NEXT" relationships by sorting trades by "Gmt time"
        df_sorted = self.df.sort_values(by="Gmt time")
        trade_ids = [row["Gmt time"].isoformat() for _, row in df_sorted.iterrows()]
        for i in range(len(trade_ids) - 1):
            self.G.add_edge(trade_ids[i], trade_ids[i + 1])

    def line_chart(self):
        """
        Plotly line chart of trade volume over time.

        Returns:
            fig (Figure): Plotly figure of the line chart.
        """
        fig = px.line(self.df, x="Gmt time", y="Volume",
                      title="Trade Volume Over Time",
                      labels={"Gmt time": "Time", "Volume": "Volume"})
        return fig

    def betweeness_centrality(self):
        """
        histogram of betweenness centrality for the trade graph nodes.

        Returns:
            fig (Figure): Matplotlib figure of the histogram.
        """
        centrality = nx.betweenness_centrality(self.G)
        centrality_values = list(centrality.values())
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.hist(centrality_values, bins=30, color="purple", alpha=0.7)
        ax.set_title("Betweenness Centrality Distribution of Trade Nodes")
        ax.set_xlabel("Betweenness Centrality")
        ax.set_ylabel("Frequency")
        return fig

    def scatter_plot(self):
        """
        Plotly scatter plot of close price over time,
        highlighting outlier trades in red.

        Returns:
            fig (Figure): Plotly figure of the scatter plot.
        """
        fig = px.scatter(
            self.df,
            x="Gmt time",
            y="Close",
            color="is_outlier",
            title="Close Price Over Time (Outliers Highlighted)",
            labels={"Gmt time": "Time", "Close": "Close Price", "is_outlier": "Is Outlier"},
            color_discrete_map={True: "red", False: "blue"}
        )
        return fig

    def bar_chart(self):
        """
        Plotly bar chart summarizing the trade status counts.

        Returns:
            fig (Figure): Plotly figure of the bar chart.
        """
        status_counts = {
            "Outlier": self.df["is_outlier"].sum(),
            "Guideline Deviation": self.df["deviates_guideline"].sum(),
            "Normal": len(self.df) - self.df["is_outlier"].sum() - self.df["deviates_guideline"].sum()
        }
        status_df = pd.DataFrame({
            "Status": list(status_counts.keys()),
            "Count": list(status_counts.values())
        })
        fig = px.bar(
            status_df,
            x="Status",
            y="Count",
            title="Trade Status Counts",
            labels={"Count": "Number of Trades"},
            color="Status",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        return fig
