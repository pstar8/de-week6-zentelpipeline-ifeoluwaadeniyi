import sys
import pytest
import pandas as pd
from pipeline.etl import manager_operator_performance


def test_operator_ranking_by_resolution_pass_rate():
    """
    Test that operators are correctly ranked by resolution pass rate
    Higher pass rate = better rank (rank 1 is best)
    """
    sample_data = pd.DataFrame({
        'Report ID': ['T1', 'T2', 'T3', 'T4', 'T5', 'T6'],
        'Operator': ['Alice', 'Alice', 'Bob', 'Bob', 'Charlie', 'Charlie'],
        'Manager': ['Victor', 'Victor', 'Kerry', 'Kerry', 'Victor', 'Victor'],
        'response_seconds': [5, 6, 15, 20, 8, 9],
        'resolution_minutes': [30, 40, 150, 200, 50, 55],
        'response_sla_pass': [True, True, False, False, True, True],
        'resolution_sla_pass': [True, True, True, False, True, True]
    })
    
    result = manager_operator_performance(sample_data)
    
    # Expected pass rates:
    # Alice: 2/2 = 100%
    # Charlie: 2/2 = 100%
    # Bob: 1/2 = 50%
    
    # Check that result contains both keys
    assert 'operators' in result
    assert 'managers' in result
    
    # Get operators DataFrame
    operators = result['operators']
    
    # Check that we have 3 operators
    assert len(operators) == 3
    
    # Check that best performers (100%) are ranked 1 and 2
    top_two = operators[operators['rank'].isin([1, 2])]
    assert set(top_two['Operator']) == {'Alice', 'Charlie'}
    assert all(top_two['resolution_pass_rate'] == 100.0)
    
    # Check that worst performer (50%) is ranked 3
    worst = operators[operators['rank'] == 3]
    assert worst['Operator'].iloc[0] == 'Bob'
    assert worst['resolution_pass_rate'].iloc[0] == 50.0


def test_escalation_count_by_operator():
    """
    Test that escalations (tickets > 180 min) are correctly counted per operator
    """
    sample_data = pd.DataFrame({
        'Report ID': ['T1', 'T2', 'T3', 'T4'],
        'Operator': ['Alice', 'Alice', 'Bob', 'Bob'],
        'Manager': ['Victor', 'Victor', 'Kerry', 'Kerry'],
        'response_seconds': [5, 6, 15, 20],
        'resolution_minutes': [30, 200, 150, 250],  # Alice has 1 escalation, Bob has 1
        'response_sla_pass': [True, True, False, False],
        'resolution_sla_pass': [True, False, True, False]
    })
    
    result = manager_operator_performance(sample_data)
    operators = result['operators']
    
    # Alice should have 1 escalation (200 minutes)
    alice_row = operators[operators['Operator'] == 'Alice']
    assert alice_row['escalations'].iloc[0] == 1
    
    # Bob should have 1 escalation (250 minutes)
    bob_row = operators[operators['Operator'] == 'Bob']
    assert bob_row['escalations'].iloc[0] == 1


def test_manager_ranking_aggregation():
    """
    Test that manager performance aggregates their team's tickets correctly
    """
    sample_data = pd.DataFrame({
        'Report ID': ['T1', 'T2', 'T3', 'T4'],
        'Operator': ['Alice', 'Bob', 'Charlie', 'David'],
        'Manager': ['Victor', 'Victor', 'Kerry', 'Kerry'],
        'response_seconds': [5, 6, 15, 20],
        'resolution_minutes': [30, 40, 150, 200],
        'response_sla_pass': [True, True, False, False],
        'resolution_sla_pass': [True, True, True, False]
    })
    
    result = manager_operator_performance(sample_data)
    managers = result['managers']
    
    # Expected:
    # Victor: 2 tickets, 2/2 = 100% resolution pass rate
    # Kerry: 2 tickets, 1/2 = 50% resolution pass rate
    
    # Check Victor's stats
    victor_row = managers[managers['Manager'] == 'Victor']
    assert victor_row['total_tickets'].iloc[0] == 2
    assert victor_row['resolution_pass_rate'].iloc[0] == 100.0
    assert victor_row['rank'].iloc[0] == 1  # Best manager
    
    # Check Kerry's stats
    kerry_row = managers[managers['Manager'] == 'Kerry']
    assert kerry_row['total_tickets'].iloc[0] == 2
    assert kerry_row['resolution_pass_rate'].iloc[0] == 50.0
    assert kerry_row['rank'].iloc[0] == 2  # Second best


def test_returns_correct_structure():
    """
    Test that function returns dictionary with correct keys and DataFrame types
    """
    sample_data = pd.DataFrame({
        'Report ID': ['T1'],
        'Operator': ['Alice'],
        'Manager': ['Victor'],
        'response_seconds': [5],
        'resolution_minutes': [30],
        'response_sla_pass': [True],
        'resolution_sla_pass': [True]
    })
    
    result = manager_operator_performance(sample_data)
    
    assert isinstance(result, dict)    
    assert 'operators' in result
    assert 'managers' in result    
    assert isinstance(result['operators'], pd.DataFrame)
    assert isinstance(result['managers'], pd.DataFrame)
    
    # Check required columns exist in operators DataFrame
    required_op_cols = ['Operator', 'total_tickets', 'avg_response_seconds', 
                        'avg_resolution_minutes', 'resolution_pass_rate', 
                        'escalations', 'rank']
    for col in required_op_cols:
        assert col in result['operators'].columns
    
    # Check required columns exist in managers DataFrame
    required_mgr_cols = ['Manager', 'total_tickets', 'resolution_pass_rate', 
                         'escalations', 'rank']
    for col in required_mgr_cols:
        assert col in result['managers'].columns

