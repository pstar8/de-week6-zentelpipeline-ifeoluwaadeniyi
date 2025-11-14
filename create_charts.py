from pipeline.analysis import generate_reports
from pipeline.viz import create_visualizations

# Run pipeline to get data
print("Running pipeline to generate data...")
results = generate_reports(
    data_path='data/',
    output_path='reports/'
)

# Create all visualizations
create_visualizations(
    data=results['data'],
    performance=results['performance'],
    output_path='reports/'
)

print("\n✅ COMPLETE!")