"""
Analysis module - orchestrates the ETL pipeline and generates reports
"""
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
    print(f"SLA metrics calculated")
    
    performance = manager_operator_performance(with_sla)
    print(f"✓ Ranked {len(performance['operators'])} operators")
    print(f"✓ Ranked {len(performance['managers'])} managers")
    
    return with_sla, performance