import pytest
import pandas as pd
from pipeline.etl import clean_tickets, enrich_tickets

def test_datetime_conversion():
    """Test that date strings are converted to datetime objects"""
    sample_data = pd.DataFrame({
        'Report ID': ['TEST-001', 'TEST-002'],
        'Ticket Open Time': ['2020/12/31 17:07:04', '2020/12/30 14:23:11'],
        'Ticket Resp Time': ['2020/12/31 17:10:20', '2020/12/30 14:23:15'],
        'Issue Res Time': ['2020/12/31 20:44:42', '2020/12/30 15:30:00'],
        'Ticket Close Time': ['2020/12/31 21:10:20', '2020/12/30 16:00:00'],
        'Operator': ['Tunde', 'Bola'],
        'Fault Type': ['Bad Network', 'Line damage']
    })
    
    cleaned = clean_tickets(sample_data)
    
    # Check datetime types
    assert cleaned['Ticket Open Time'].dtype == 'datetime64[ns]'
    assert cleaned['Ticket Resp Time'].dtype == 'datetime64[ns]'
    assert cleaned['Issue Res Time'].dtype == 'datetime64[ns]'
    assert cleaned['Ticket Close Time'].dtype == 'datetime64[ns]'
    assert cleaned['Ticket Open Time'].notna().all()
    assert cleaned['Ticket Resp Time'].notna().all()


def test_missing_operator_filled():
    """Test that missing Operator names are filled with 'UNKNOWN'"""
    sample_data = pd.DataFrame({
        'Report ID': ['TEST-001', 'TEST-002'],
        'Ticket Open Time': ['2020/12/31 17:07:04', '2020/12/30 14:23:11'],
        'Ticket Resp Time': ['2020/12/31 17:10:20', '2020/12/30 14:23:15'],
        'Issue Res Time': ['2020/12/31 20:44:42', '2020/12/30 15:30:00'],
        'Ticket Close Time': ['2020/12/31 21:10:20', '2020/12/30 16:00:00'],
        'Operator': ['Tunde', None],
        'Fault Type': ['Bad Network', 'Line damage']
    })
    
    cleaned = clean_tickets(sample_data)
    
    assert cleaned['Operator'].iloc[1] == 'UNKNOWN'
    assert cleaned['Operator'].notna().all()


def test_missing_fault_type_filled():
    """Test that missing Fault Type is filled with 'Not Specified'"""
    sample_data = pd.DataFrame({
        'Report ID': ['TEST-001', 'TEST-002'],
        'Ticket Open Time': ['2020/12/31 17:07:04', '2020/12/30 14:23:11'],
        'Ticket Resp Time': ['2020/12/31 17:10:20', '2020/12/30 14:23:15'],
        'Issue Res Time': ['2020/12/31 20:44:42', '2020/12/30 15:30:00'],
        'Ticket Close Time': ['2020/12/31 21:10:20', '2020/12/30 16:00:00'],
        'Operator': ['Tunde', 'Bola'],
        'Fault Type': [None, 'Line damage']
    })
    
    cleaned = clean_tickets(sample_data)
    
    assert cleaned['Fault Type'].iloc[0] == 'Not Specified'
    assert cleaned['Fault Type'].notna().all()


def test_text_stripping():
    """Test that extra spaces are removed from text columns"""
    sample_data = pd.DataFrame({
        'Report ID': ['TEST-001'],
        'Ticket Open Time': ['2020/12/31 17:07:04'],
        'Ticket Resp Time': ['2020/12/31 17:10:20'],
        'Issue Res Time': ['2020/12/31 20:44:42'],
        'Ticket Close Time': ['2020/12/31 21:10:20'],
        'Operator': ['  Tunde  '],
        'Customer Name': ['Access  '],
        'Fault Type': ['Bad Network']
    })
    
    cleaned = clean_tickets(sample_data)
    
    assert cleaned['Operator'].iloc[0] == 'Tunde'
    assert cleaned['Customer Name'].iloc[0] == 'Access'


def test_no_duplicate_rows_created():
    """Test that merges don't create duplicate rows"""
    tickets = pd.DataFrame({
        'Report ID': ['TEST-001'],
        'Report Channel': ['CH01'],
        'Ticket Open Time': [pd.Timestamp('2020-12-31 17:07:04')],
        'Ticket Resp Time': [pd.Timestamp('2020-12-31 17:10:20')],
        'Issue Res Time': [pd.Timestamp('2020-12-31 20:44:42')],
        'Ticket Close Time': [pd.Timestamp('2020-12-31 21:10:20')],
        'Operator': ['Tunde'],
        'State Key': ['NGS001'],
        'Fault Type': ['Bad Network']
    })
    
    channel = pd.DataFrame({
        'Channel Key': ['CH01', 'CH01'],  # DUPLICATE
        'Channel': ['Social Media', 'Social Media']
    })
    
    employees = pd.DataFrame({
        'Employee_name': ['Tunde'], 
        'Manager': ['Victor']
    })
    
    location = pd.DataFrame({
        'State Key': ['NGS001'], 
        'State': ['Anambra'], 
        'Zone': ['SS'], 
        'Zone Desc': ['South-South']
    })
    
    service_type = pd.DataFrame({
        'Service Code': ['WLESS'], 
        'Service Name': ['Wireless'], 
        'Service Key': [1]
    })
    
    fault_type = pd.DataFrame({
        'Fault': ['Bad Network'], 
        'Fault Key': [1]
    })
    
    enriched = enrich_tickets(tickets, employees, channel, location, service_type, fault_type)
    
    # Should still be only 1 row
    assert len(enriched) == 1

def test_channel_merge_preserves_all_tickets():
    """Test that left join keeps all tickets even if no match"""
    tickets = pd.DataFrame({
        'Report ID': ['TEST-001', 'TEST-002'],
        'Report Channel': ['CH01', 'CH99'],
        'Ticket Open Time': [pd.Timestamp('2020-12-31 17:07:04')] * 2,
        'Ticket Resp Time': [pd.Timestamp('2020-12-31 17:10:20')] * 2,
        'Issue Res Time': [pd.Timestamp('2020-12-31 20:44:42')] * 2,
        'Ticket Close Time': [pd.Timestamp('2020-12-31 21:10:20')] * 2,
        'Operator': ['Tunde', 'Bola'],
        'State Key': ['NGS001', 'NGS001'],
        'Fault Type': ['Bad Network', 'Line damage']
    })
    
    channel = pd.DataFrame({
        'Channel Key': ['CH01'],
        'Channel': ['Social Media']
    })
    
    employees = pd.DataFrame({
        'Employee_name': ['Tunde', 'Bola'], 
        'Manager': ['Victor', 'Victor']
    })
    
    location = pd.DataFrame({
        'State Key': ['NGS001'], 
        'State': ['Anambra'], 
        'Zone': ['SS'], 
        'Zone Desc': ['South-South']
    })
    
    service_type = pd.DataFrame({
        'Service Code': ['WLESS'], 
        'Service Name': ['Wireless'], 
        'Service Key': [1]
    })
    
    fault_type = pd.DataFrame({
        'Fault': ['Bad Network', 'Line damage'], 
        'Fault Key': [1, 2]
    })
    
    enriched = enrich_tickets(tickets, employees, channel, location, service_type, fault_type)
    
    assert len(enriched) == 2    
    assert enriched.iloc[0]['Channel'] == 'Social Media'
    assert pd.isna(enriched.iloc[1]['Channel'])