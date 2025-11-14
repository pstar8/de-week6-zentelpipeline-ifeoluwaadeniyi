from pipeline.analysis import generate_reports

if __name__ == '__main__':
    results = generate_reports(
        data_path='data/',
        output_path='reports/'
    )
    
    print("\nGenerated files:")
    print("  - reports/weekly_kpis.csv")
    print("  - reports/manager_operator_report.json")
    print("  - reports/escalations.csv")