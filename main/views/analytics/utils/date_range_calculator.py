from datetime import datetime, timedelta
import pandas as pd


def calculate_date_range(start_date=None, end_date=None):
    if not start_date and not end_date:
        current_date = datetime.now().date()
        start_date = current_date - timedelta(days=current_date.weekday())
        end_date = start_date + timedelta(days=6)
    elif start_date and not end_date:
        start_date = pd.to_datetime(start_date).date()
        end_date = start_date + timedelta(days=6)
    elif not start_date and end_date:
        end_date = pd.to_datetime(end_date).date()
        start_date = end_date - timedelta(days=end_date.weekday())
    return start_date, end_date