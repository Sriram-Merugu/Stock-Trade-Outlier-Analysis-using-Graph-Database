# analysis.py
def compute_guideline_deviation(data):
    """
    Flag trades that deviate from expected guidelines.
    Expected volume range: [25th, 75th percentile].
    Expected return range: [mean - 2*std, mean + 2*std].
    """
    volume_min = data['Volume'].quantile(0.05)
    volume_max = data['Volume'].quantile(0.95)
    mean_return = data['Return'].mean()
    std_return = data['Return'].std()
    return_min = mean_return - 2 * std_return
    return_max = mean_return + 2 * std_return

    data['deviates_guideline'] = data.apply(
        lambda row: (row['Volume'] < volume_min or row['Volume'] > volume_max) or
                    (row['Return'] < return_min or row['Return'] > return_max),
        axis=1
    )
    return data
