import os
import sys
import subprocess
import webbrowser

REQUIRED_PACKAGES = [
    'pandas', 'numpy', 'scikit-learn', 'plotly', 'dash', 'pyyaml', 'pytest'
]

def install_packages():
    import importlib
    for pkg in REQUIRED_PACKAGES:
        try:
            importlib.import_module(pkg.replace('-', '_'))
        except ImportError:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', pkg])

def initialize_data():
    import pandas as pd
    import numpy as np
    # Simulate security event data
    np.random.seed(42)
    data = pd.DataFrame({
        'timestamp': pd.date_range('2023-01-01', periods=1000, freq='H'),
        'src_ip': np.random.choice(['10.0.0.1', '10.0.0.2', '10.0.0.3'], 1000),
        'dst_ip': np.random.choice(['192.168.1.1', '192.168.1.2'], 1000),
        'event_type': np.random.choice(['login', 'file_access', 'malware_detected'], 1000),
        'bytes': np.random.randint(100, 10000, 1000)
    })
    os.makedirs('data', exist_ok=True)
    data.to_csv('data/security_events.csv', index=False)

def run_ml_pipeline():
    import pandas as pd
    from sklearn.ensemble import IsolationForest
    from sklearn.cluster import KMeans
    data = pd.read_csv('data/security_events.csv')
    features = data[['bytes']]
    # Anomaly detection
    iso = IsolationForest(contamination=0.05, random_state=42)
    data['anomaly'] = iso.fit_predict(features)
    # Clustering
    kmeans = KMeans(n_clusters=3, random_state=42)
    data['cluster'] = kmeans.fit_predict(features)
    data.to_csv('data/security_events_labeled.csv', index=False)

def launch_dashboard():
    # Launch the dashboard in a subprocess
    subprocess.Popen([sys.executable, 'dashboard.py'])
    webbrowser.open('http://127.0.0.1:8050/')

def main():
    print('Checking/installing dependencies...')
    install_packages()
    print('Initializing data...')
    initialize_data()
    print('Running ML pipeline...')
    run_ml_pipeline()
    print('Launching dashboard...')
    launch_dashboard()

if __name__ == '__main__':
    main()