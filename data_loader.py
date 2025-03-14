# data_loader.py
import pandas as pd

def load_and_clean_data(csv_file):
    """
    Load CSV data, convert the date column, remove duplicates and zero volume entries.
    """
    data = pd.read_csv(csv_file)
    # Convert 'Gmt time' column to datetime
    data['Gmt time'] = pd.to_datetime(data['Gmt time'], format='%d.%m.%Y %H:%M:%S.%f', dayfirst=True)
    # data.set_index('Gmt time', inplace=True)

    # Remove duplicate rows
    data = data.drop_duplicates()
    # Convert numeric columns to float
    numeric_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
    for col in numeric_cols:
        data[col] = pd.to_numeric(data[col], errors='coerce')
    # Remove rows with zero volume
    data = data[data['Volume'] != 0]
    return data

def detect_outliers(data, threshold=3):
    """
    Compute daily returns, Z-scores, and flag outliers.
    """
    data['Return'] = data['Close'].pct_change()
    data.dropna(subset=['Return'], inplace=True)
    mean_return = data['Return'].mean()
    std_return = data['Return'].std()
    data['z_score'] = (data['Return'] - mean_return) / std_return
    data['is_outlier'] = data['z_score'].abs() > threshold
    return data
