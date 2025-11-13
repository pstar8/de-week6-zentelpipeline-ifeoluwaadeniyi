import pandas as pd
import os

def load_tables(data_path):
    """
    Loads all CSV files from the data folder and returns them as a dictionary.
    """
    service_data = pd.read_csv(os.path.join(data_path, 'service_data.csv'))

    employee = pd.read_csv(os.path.join(data_path, 'employee.csv'))

    channel = pd.read_csv(os.path.join(data_path, 'channel_type.csv'))

    service_type = pd.read_csv(os.path.join(data_path, 'service_type.csv'))

    fault_type = pd.read_csv(os.path.join(data_path, 'fault_type.csv'))

    location = pd.read_csv(os.path.join(data_path, 'location.csv'))

    tables = {
        'service_data': service_data,
        'employee': employee,
        'channel': channel,
        'service_type': service_type,
        'fault_type': fault_type,
        'location': location
    }
    
    return tables

def clean_tickets(df):
    """
    Cleans the service_data DataFrame
    """
    # Make a copy so we don't change the original
    df_clean = df.copy()

    time_columns = [
        'Ticket Open Time',
        'Ticket Resp Time', 
        'Issue Res Time',
        'Ticket Close Time'
    ]
    
    for col in time_columns:
        df_clean[col] = pd.to_datetime(df_clean[col], format="%Y/%m/%d %H:%M:%S", errors='coerce')

    df_clean['Operator'] = df_clean['Operator'].fillna('UNKNOWN')
    
    df_clean['Fault Type'] = df_clean['Fault Type'].fillna('Not Specified')

    "Clean texts with space"

    text_columns = ['Customer Name', 'Operator', 'Fault Type']
    
    for col in text_columns:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].str.strip()
    
    return df_clean

def enrich_tickets(tickets_df, employee_df, channel_df, location_df, 
                   service_type_df, fault_type_df):
    """
    Enriches tickets with information from lookup tables
    """
    enriched = tickets_df.copy()

    # Remove duplicates from lookup tables to prevent duplicate rows
    employee_df = employee_df.drop_duplicates(subset=['Employee_name'], keep='first')
    channel_df = channel_df.drop_duplicates(subset=['Channel Key'], keep='first')
    location_df = location_df.drop_duplicates(subset=['State Key'], keep='first')
    service_type_df = service_type_df.drop_duplicates(subset=['Service Code'], keep='first')
    fault_type_df = fault_type_df.drop_duplicates(subset=['Fault'], keep='first')

    # Channel info
    enriched = pd.merge(
        enriched,
        channel_df,
        left_on='Report Channel',    
        right_on='Channel Key',     
        how='left'                    # Keeps all tickets
    )

    # Location info
    enriched = pd.merge(
        enriched,
        location_df,
        on='State Key',
        how='left'
    )

    #Employee info
    enriched = pd.merge(
        enriched,
        employee_df,
        left_on='Operator',         
        right_on='Employee_name',  
        how='left'
    )
    
    # Extract service code from Report ID 
    enriched['Service_Code_Extracted'] = enriched['Report ID'].str.split('-').str[-1]

    # Service type info
    enriched = pd.merge(
        enriched,
        service_type_df,
        left_on='Service_Code_Extracted',
        right_on='Service Code',
        how='left'
    )

    # Fault type info
    enriched = pd.merge(
        enriched,
        fault_type_df,
        left_on='Fault Type',
        right_on='Fault',
        how='left'
    )
    return enriched

def compute_sla_metrics(df):
    """
    Calculates SLA metrics for each ticket
    """
    df_sla = df.copy()

    # Calculate response time in seconds
    df_sla['response_seconds'] = (
        df_sla['Ticket Resp Time'] - df_sla['Ticket Open Time']
    ).dt.total_seconds()
    
    # Calculate resolution time in minutes
    df_sla['resolution_minutes'] = (
        df_sla['Issue Res Time'] - df_sla['Ticket Resp Time']
    ).dt.total_seconds() / 60

    """Check if response met SLA"""
    df_sla['response_sla_pass'] = df_sla['response_seconds'] <= 10
    df_sla['resolution_sla_pass'] = df_sla['resolution_minutes'] <= 180

    # Categorize resolution performance
    def categorize_resolution(minutes):
        if minutes < 30:
            return 'Excellent'
        elif minutes < 60:
            return 'Good'
        elif minutes <= 180:
            return 'Fair'
        else:
            return 'Critical'
    
    df_sla['resolution_category'] = df_sla['resolution_minutes'].apply(categorize_resolution)
    return df_sla