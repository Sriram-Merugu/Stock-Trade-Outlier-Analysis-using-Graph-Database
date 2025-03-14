from neo4j import GraphDatabase
# Import your custom data processing functions.
from data_loader import load_and_clean_data, detect_outliers
from analysis import compute_guideline_deviation

# ---------------------------
# Neo4j Connection Setup (Local Database)
# ---------------------------
# Update the URI and AUTH as per your local Neo4j configuration.
URI = "bolt://localhost:7687"
AUTH = ("neo4j", "password")  # Replace 'password' with your actual Neo4j password.
driver = GraphDatabase.driver(URI, auth=AUTH)

# ---------------------------
# Load and Preprocess CSV Data
# ---------------------------
csv_file = "assets/EURUSD.csv"
# Use data_loader functions to load, clean, and augment the data.
data = load_and_clean_data(csv_file)
data = detect_outliers(data)
data = compute_guideline_deviation(data)


# ---------------------------
# 1. Create Trade Nodes in Neo4j
# ---------------------------
def create_trade_node(tx, trade):
    query = """
    CREATE (t:Trade {
        trade_id: $trade_id,
        timestamp: $timestamp,
        open: $open,
        high: $high,
        low: $low,
        close: $close,
        volume: $volume,
        is_outlier: $is_outlier,
        deviates_guideline: $deviates_guideline
    })
    """
    tx.run(query, **trade)


with driver.session() as session:
    for idx, row in data.iterrows():
        # Use the 'Gmt time' column as the unique identifier (ISO format)
        trade_timestamp = row["Gmt time"]
        trade_id = trade_timestamp.isoformat()
        trade = {
            "trade_id": trade_id,
            "timestamp": trade_timestamp.isoformat(),
            "open": float(row["Open"]),
            "high": float(row["High"]),
            "low": float(row["Low"]),
            "close": float(row["Close"]),
            "volume": float(row["Volume"]),
            "is_outlier": bool(row["is_outlier"]),
            "deviates_guideline": bool(row["deviates_guideline"])
        }
        session.execute_write(create_trade_node, trade)

print("Trade nodes created successfully.")


# ---------------------------
# 2. Create Consecutive Relationships
# ---------------------------
def create_consecutive_relationship(tx, trade_id1, trade_id2):
    query = """
    MATCH (a:Trade {trade_id: $trade_id1}), (b:Trade {trade_id: $trade_id2})
    CREATE (a)-[:NEXT]->(b)
    """
    tx.run(query, trade_id1=trade_id1, trade_id2=trade_id2)


# Create a list of trade_ids in chronological order (sorted by "Gmt time")
trade_ids = [row["Gmt time"].isoformat() for _, row in data.sort_values(by="Gmt time").iterrows()]

with driver.session() as session:
    for i in range(len(trade_ids) - 1):
        session.execute_write(create_consecutive_relationship, trade_ids[i], trade_ids[i + 1])

print("Consecutive relationships created successfully.")

# ---------------------------
# 3. Create SIMILAR Relationships Based on Price Similarity
# ---------------------------
SIMILAR_THRESHOLD = 0.0005  # Adjust threshold as needed


def create_similar_relationship(tx, trade_id1, trade_id2, similarity):
    """
    Create a SIMILAR relationship between two trades with a similarity attribute.
    """
    query = """
    MATCH (a:Trade {trade_id: $trade_id1}), (b:Trade {trade_id: $trade_id2})
    CREATE (a)-[:SIMILAR {similarity: $similarity}]->(b)
    """
    tx.run(query, trade_id1=trade_id1, trade_id2=trade_id2, similarity=similarity)


trade_list = []
for idx, row in data.iterrows():
    trade_timestamp = row["Gmt time"]
    trade_id = trade_timestamp.isoformat()
    trade_list.append((trade_id, float(row["Open"])))

with driver.session() as session:
    for i in range(len(trade_list)):
        for j in range(i + 1, len(trade_list)):
            price_diff = abs(trade_list[i][1] - trade_list[j][1])
            if price_diff < SIMILAR_THRESHOLD:
                similarity = 1.0 / (price_diff + 1e-6)  # Add epsilon to avoid division by zero
                session.execute_write(create_similar_relationship, trade_list[i][0], trade_list[j][0], similarity)

print("Similar relationships have been created based on open price similarity.")

# Close the driver connection when done.
driver.close()
