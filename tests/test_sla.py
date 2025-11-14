import sys
from pathlib import Path
import pytest
import pandas as pd
from pipeline.etl import compute_sla_metrics


def test_sla_with_boundaries():
    """
    Test SLA calculations with boundary conditions:
    """
    sample_data = pd.DataFrame({
        'Report ID': ['TEST-001'],
        'Ticket Open Time': [pd.Timestamp('2020-12-31 17:00:00')],
        'Ticket Resp Time': [pd.Timestamp('2020-12-31 17:00:05')],  # 5 seconds
        'Issue Res Time': [pd.Timestamp('2020-12-31 18:00:05')],     # 60 minutes
        'Ticket Close Time': [pd.Timestamp('2020-12-31 18:10:00')]
    })
    
    result = compute_sla_metrics(sample_data)
    
    # Check response SLA (5 seconds <= 10)
    assert result['response_sla_pass'].iloc[0] == True, "Response SLA should pass at 5 seconds"
    
    # Check resolution SLA (60 minutes <= 180)
    assert result['resolution_sla_pass'].iloc[0] == True, "Resolution SLA should pass at 60 minutes"
    
    # Check resolution category (60 minutes = 'Good')
    assert result['resolution_category'].iloc[0] == 'Good', "60 minutes should be 'Good' category"
    
    # Verify actual calculated values
    assert result['response_seconds'].iloc[0] == 5.0
    assert result['resolution_minutes'].iloc[0] == 60.0


def test_escalation_at_181_minutes():
    """
    Test that a ticket with resolution_minutes = 181 is flagged as escalation
    (exceeds 180-minute SLA threshold)
    """
    sample_data = pd.DataFrame({
        'Report ID': ['TEST-ESCALATION'],
        'Ticket Open Time': [pd.Timestamp('2020-12-31 17:00:00')],
        'Ticket Resp Time': [pd.Timestamp('2020-12-31 17:00:05')],
        'Issue Res Time': [pd.Timestamp('2020-12-31 20:01:05')],  # 181 minutes
        'Ticket Close Time': [pd.Timestamp('2020-12-31 20:10:00')]
    })
    
    result = compute_sla_metrics(sample_data)
    
    # Check that resolution minutes is 181
    assert result['resolution_minutes'].iloc[0] == 181.0, "Should calculate 181 minutes"
    
    # Check that resolution SLA FAILS (181 > 180)
    assert result['resolution_sla_pass'].iloc[0] == False, "Should fail SLA at 181 minutes"
    
    # Check that it's categorized as Critical (> 180)
    assert result['resolution_category'].iloc[0] == 'Critical', "Should be 'Critical' category"
    
    is_escalation = result['resolution_minutes'].iloc[0] > 180
    assert is_escalation == True, "Ticket should be flagged as escalation"

def test_all_resolution_categories():
    """
    Test that all resolution categories work correctly
    """
    sample_data = pd.DataFrame({
        'Report ID': ['T1', 'T2', 'T3', 'T4'],
        'Ticket Open Time': [pd.Timestamp('2020-12-31 17:00:00')] * 4,
        'Ticket Resp Time': [pd.Timestamp('2020-12-31 17:00:05')] * 4,
        'Issue Res Time': [
            pd.Timestamp('2020-12-31 17:20:05'),  # 20 min - Excellent
            pd.Timestamp('2020-12-31 17:45:05'),  # 45 min - Good
            pd.Timestamp('2020-12-31 19:00:05'),  # 120 min - Fair
            pd.Timestamp('2020-12-31 21:00:05')   # 240 min - Critical
        ],
        'Ticket Close Time': [pd.Timestamp('2020-12-31 21:00:00')] * 4
    })
    
    result = compute_sla_metrics(sample_data)
    
    assert result['resolution_category'].iloc[0] == 'Excellent'
    assert result['resolution_category'].iloc[1] == 'Good'
    assert result['resolution_category'].iloc[2] == 'Fair'
    assert result['resolution_category'].iloc[3] == 'Critical'