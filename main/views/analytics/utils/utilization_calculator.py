import pandas as pd


def calculate_utilization(df_sessions, df_facilities, start_date, end_date):
    # REMOVE DUPLICATES BASED ON SESSION DATE, START TIME, AND END TIME
    df_sessions = df_sessions.drop_duplicates(subset=['facility__object_id', 'session_date', 'start_time', 'end_time'])

    # CREATE DATETIME COLUMNS
    df_sessions.loc[:, 'start_datetime'] = pd.to_datetime(df_sessions['session_date'].astype(str) + ' ' + df_sessions['start_time'].astype(str))
    df_sessions.loc[:, 'end_datetime'] = pd.to_datetime(df_sessions['session_date'].astype(str) + ' ' + df_sessions['end_time'].astype(str))

    # SET SESSION DURATION BASED ON COURSE CATEGORY TYPE
    df_sessions.loc[:, 'duration'] = df_sessions['enrollment__course__course_category__category_type'].apply(
    lambda x: 2.0 if x == 'PDC' else (7.5 if x == 'TDC' else 0)
    )

    # AGGREGATE AND CALCULATE TOTAL HOURS ASSIGNED
    utilization = df_sessions.groupby('facility__object_id')['duration'].sum().reset_index()
    utilization.columns = ['facility_code', 'hoursAssigned']

    # MERGE WITH FACILITY DATA
    utilization = pd.merge(df_facilities, utilization, left_on='facility_code', right_on='facility_code', how='left')
    utilization['hoursAssigned'] = utilization['hoursAssigned'].fillna(0).infer_objects(copy=False)

    # CALCULATE TOTAL HOURS AVAILABLE
    total_days = (end_date - start_date).days + 1
    hours_available_per_facility = total_days * 8
    utilization['hoursAvailable'] = hours_available_per_facility

    # CALCULATE UTILIZATION RATE
    utilization['utilizationRate'] = (utilization['hoursAssigned'] / utilization['hoursAvailable'] * 100).round(2)

    # SORT FACILITYS BY UTILIZATION RATE
    utilization = utilization.sort_values(by='utilizationRate', ascending=True)

    # OVERALL UTILIZATION
    total_hours_assigned = utilization['hoursAssigned'].sum()
    total_hours_available = len(df_facilities) * hours_available_per_facility
    overall_utilization_rate = (total_hours_assigned / total_hours_available * 100).round(2)

    return utilization, overall_utilization_rate, total_hours_assigned, total_hours_available
