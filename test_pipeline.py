import pandas as pd
import os

def test_data_exists():
    assert os.path.exists('data/security_events.csv'), 'Raw data file missing.'
    assert os.path.exists('data/security_events_labeled.csv'), 'Labeled data file missing.'

def test_anomaly_column():
    df = pd.read_csv('data/security_events_labeled.csv')
    assert 'anomaly' in df.columns, 'Anomaly column missing.'
    assert df['anomaly'].isin([-1, 1]).all(), 'Anomaly values should be -1 or 1.'

def test_cluster_column():
    df = pd.read_csv('data/security_events_labeled.csv')
    assert 'cluster' in df.columns, 'Cluster column missing.'
    assert df['cluster'].nunique() == 3, 'There should be 3 clusters.'

def run_all_tests():
    test_data_exists()
    test_anomaly_column()
    test_cluster_column()
    print('All tests passed!')

if __name__ == '__main__':
    run_all_tests()