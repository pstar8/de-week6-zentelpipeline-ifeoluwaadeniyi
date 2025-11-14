import pandas as pd
import json
from pathlib import Path
from pipeline.etl import (
    load_tables,
    clean_tickets,
    enrich_tickets,
    compute_sla_metrics,
    manager_operator_performance
)


def run_pipeline(data_path='data/'):
    """
    Runs the complete ETL pipeline
    """
  
    tables = load_tables(data_path)
    print(f"Loaded {len(tables['service_data'])} tickets")
    
    cleaned = clean_tickets(tables['service_data'])
    print(f"Cleaned {len(cleaned)} tickets")
    
    enriched = enrich_tickets(
        cleaned,
        tables['employee'],
        tables['channel'],
        tables['location'],
        tables['service_type'],
        tables['fault_type']
    )
    print(f"Enriched with {len(enriched.columns)} total columns")
    
    with_sla = compute_sla_metrics(enriched)
    print(f"✓ SLA metrics calculated")
    
    performance = manager_operator_performance(with_sla)
    print(f"✓ Ranked {len(performance['operators'])} operators")
    print(f"✓ Ranked {len(performance['managers'])} managers")

    return with_sla, performance


def calculate_weekly_kpis(df):
    """
    Calculates key performance indicators by week
    """
    df['week'] = df['Ticket Open Time'].dt.isocalendar().week
    df['year'] = df['Ticket Open Time'].dt.isocalendar().year
    df['year_week'] = df['year'].astype(str) + '-W' + df['week'].astype(str).str.zfill(2)
    
    weekly_stats = df.groupby('year_week').agg({
        'Report ID': 'count',
        'response_seconds': 'mean',
        'resolution_minutes': 'mean',
        'response_sla_pass': ['sum', 'mean'],
        'resolution_sla_pass': ['sum', 'mean']
    }).reset_index()
    
    weekly_stats.columns = [
        'year_week',
        'total_tickets',
        'avg_response_seconds',
        'avg_resolution_minutes',
        'response_pass_count',
        'response_pass_rate',
        'resolution_pass_count',
        'resolution_pass_rate'
    ]
    
    # Convert to percentages
    weekly_stats['response_pass_rate'] = weekly_stats['response_pass_rate'] * 100
    weekly_stats['resolution_pass_rate'] = weekly_stats['resolution_pass_rate'] * 100
    weekly_stats['avg_response_seconds'] = weekly_stats['avg_response_seconds'].round(2)
    weekly_stats['avg_resolution_minutes'] = weekly_stats['avg_resolution_minutes'].round(2)
    weekly_stats['response_pass_rate'] = weekly_stats['response_pass_rate'].round(2)
    weekly_stats['resolution_pass_rate'] = weekly_stats['resolution_pass_rate'].round(2)
    
    # Sort
    weekly_stats = weekly_stats.sort_values('year_week')
    
    return weekly_stats


def extract_escalations(df):
    """
    Extracts tickets that exceeded resolution SLA
    """
    escalations = df[df['resolution_minutes'] > 180].copy()
    
    escalation_report = escalations[[
        'Report ID',
        'Ticket Open Time',
        'Ticket Resp Time',
        'Issue Res Time',
        'Operator',
        'Manager',
        'Channel',
        'State',
        'Service Name',
        'Fault Type',
        'response_seconds',
        'resolution_minutes',
        'resolution_category'
    ]].copy()
    
    escalation_report = escalation_report.sort_values('resolution_minutes', ascending=False)
    escalation_report = escalation_report.reset_index(drop=True)
    
    return escalation_report


def save_reports(weekly_kpis, performance, escalations, output_path='reports/'):
    """
    Saves all reports to files
    """
    output_dir = Path(output_path)
    output_dir.mkdir(parents=True, exist_ok=True)
   
    weekly_path = output_dir / 'weekly_kpis.csv'
    weekly_kpis.to_csv(weekly_path, index=False)
    print(f"\n✓ Saved: {weekly_path}")
    print(f"  Rows: {len(weekly_kpis)}")
    
    performance_json = {
        'operators': performance['operators'].to_dict(orient='records'),
        'managers': performance['managers'].to_dict(orient='records'),
        'summary': {
            'total_operators': len(performance['operators']),
            'total_managers': len(performance['managers']),
            'best_operator': performance['operators'].iloc[0]['Operator'],
            'best_manager': performance['managers'].iloc[0]['Manager']
        }
    }
    
    json_path = output_dir / 'manager_operator_report.json'
    with open(json_path, 'w') as f:
        json.dump(performance_json, f, indent=2)
    print(f"\n✓ Saved: {json_path}")
    print(f"  Operators: {len(performance['operators'])}")
    print(f"  Managers: {len(performance['managers'])}")
    
    escalation_path = output_dir / 'escalations.csv'
    escalations.to_csv(escalation_path, index=False)
    print(f"\n✓ Saved: {escalation_path}")
    print(f"  Escalated tickets: {len(escalations)}")

def generate_reports(data_path='data/', output_path='reports/'):
    """
    Complete workflow: runs pipeline and generates all reports
    """
    data, performance = run_pipeline(data_path)
    weekly_kpis = calculate_weekly_kpis(data)
    escalations = extract_escalations(data)
    
    save_reports(weekly_kpis, performance, escalations, output_path)
    
    return {
        'data': data,
        'performance': performance,
        'weekly_kpis': weekly_kpis,
        'escalations': escalations
    }