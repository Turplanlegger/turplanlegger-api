from datetime import datetime


def pytest_csv_register_columns(columns):
    columns['utc_timestamp'] = datetime.utcnow().isoformat()
