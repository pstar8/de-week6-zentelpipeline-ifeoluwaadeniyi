"""
Visualization module - creates charts for the business insights
"""
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path


def create_visualizations(data, performance, output_path='reports/'):
    """
    Creates all visualization charts for the analysis
    
    Parameters:
    data (DataFrame): Full enriched dataset
    performance (dict): Performance rankings
    output_path (str): Where to save charts
    """
    output_dir = Path(output_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "="*70)
    print("CREATING VISUALIZATIONS")
    print("="*70)
    
    # Set style for cleaner charts
    plt.style.use('default')
    
    # ===== 1. OVERALL SLA PERFORMANCE =====
    print("\n📊 Chart 1: Overall SLA Performance...")
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Calculate metrics
    response_pass_rate = (data['response_sla_pass'].sum() / len(data)) * 100
    resolution_pass_rate = (data['resolution_sla_pass'].sum() / len(data)) * 100
    
    categories = ['Response SLA\n(≤10 sec)', 'Resolution SLA\n(≤180 min)']
    pass_rates = [response_pass_rate, resolution_pass_rate]
    targets = [90, 80]  # Target lines
    
    bars = ax.bar(categories, pass_rates, color=['#ff6b6b', '#f9ca24'], edgecolor='black', linewidth=1.2)
    
    # Add target lines
    ax.axhline(y=90, color='green', linestyle='--', linewidth=2, label='Response Target (90%)')
    ax.axhline(y=80, color='blue', linestyle='--', linewidth=2, label='Resolution Target (80%)')
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%',
                ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    ax.set_ylabel('Pass Rate (%)', fontsize=12, fontweight='bold')
    ax.set_title('Zentel SLA Performance vs Targets', fontsize=14, fontweight='bold', pad=20)
    ax.set_ylim(0, 100)
    ax.legend(fontsize=10)
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'chart1_overall_sla.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"   ✓ Saved: {output_dir / 'chart1_overall_sla.png'}")
    
    # ===== 2. RESPONSE TIME BY CHANNEL =====
    print("\n📊 Chart 2: Response Time by Channel...")
    
    channel_stats = data.groupby('Channel')['response_seconds'].mean().sort_values(ascending=False)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    bars = ax.barh(channel_stats.index, channel_stats.values, color='#e74c3c', edgecolor='black', linewidth=1.2)
    
    # Add target line
    ax.axvline(x=10, color='green', linestyle='--', linewidth=2, label='Target (10 sec)')
    
    # Add value labels
    for i, (idx, value) in enumerate(channel_stats.items()):
        ax.text(value + 5, i, f'{value:.1f}s', va='center', fontsize=10, fontweight='bold')
    
    ax.set_xlabel('Average Response Time (seconds)', fontsize=12, fontweight='bold')
    ax.set_title('Response Time by Communication Channel', fontsize=14, fontweight='bold', pad=20)
    ax.legend(fontsize=10)
    ax.grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'chart2_response_by_channel.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"   ✓ Saved: {output_dir / 'chart2_response_by_channel.png'}")
    
    # ===== 3. RESPONSE TIME BY ZONE =====
    print("\n📊 Chart 3: Response Time by Geographic Zone...")
    
    zone_stats = data.groupby('Zone Desc')['response_seconds'].mean().sort_values(ascending=False)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    bars = ax.barh(zone_stats.index, zone_stats.values, color='#3498db', edgecolor='black', linewidth=1.2)
    
    # Add target line
    ax.axvline(x=10, color='green', linestyle='--', linewidth=2, label='Target (10 sec)')
    
    # Add value labels
    for i, (idx, value) in enumerate(zone_stats.items()):
        ax.text(value + 5, i, f'{value:.1f}s', va='center', fontsize=10, fontweight='bold')
    
    ax.set_xlabel('Average Response Time (seconds)', fontsize=12, fontweight='bold')
    ax.set_title('Response Time by Geographic Zone', fontsize=14, fontweight='bold', pad=20)
    ax.legend(fontsize=10)
    ax.grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'chart3_response_by_zone.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"   ✓ Saved: {output_dir / 'chart3_response_by_zone.png'}")
    
    # ===== 4. RESPONSE TIME BY FAULT TYPE =====
    print("\n📊 Chart 4: Response Time by Fault Type...")
    
    fault_stats = data.groupby('Fault Type')['response_seconds'].mean().sort_values(ascending=False)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    bars = ax.barh(fault_stats.index, fault_stats.values, color='#9b59b6', edgecolor='black', linewidth=1.2)
    
    # Add target line
    ax.axvline(x=10, color='green', linestyle='--', linewidth=2, label='Target (10 sec)')
    
    # Add value labels
    for i, (idx, value) in enumerate(fault_stats.items()):
        ax.text(value + 5, i, f'{value:.1f}s', va='center', fontsize=10, fontweight='bold')
    
    ax.set_xlabel('Average Response Time (seconds)', fontsize=12, fontweight='bold')
    ax.set_title('Response Time by Fault Type (KEY FACTOR)', fontsize=14, fontweight='bold', pad=20)
    ax.legend(fontsize=10)
    ax.grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'chart4_response_by_fault.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"   ✓ Saved: {output_dir / 'chart4_response_by_fault.png'}")
    
    # ===== 5. TOP 10 OPERATORS =====
    print("\n📊 Chart 5: Top 10 Operator Performance...")
    
    top_10_ops = performance['operators'].head(10)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    bars = ax.barh(range(len(top_10_ops)), top_10_ops['resolution_pass_rate'].values, 
                   color='#2ecc71', edgecolor='black', linewidth=1.2)
    
    # Add target line
    ax.axvline(x=70, color='orange', linestyle='--', linewidth=2, label='Target (70%)')
    
    # Set y-axis labels
    ax.set_yticks(range(len(top_10_ops)))
    ax.set_yticklabels(top_10_ops['Operator'].values)
    
    # Add value labels
    for i, value in enumerate(top_10_ops['resolution_pass_rate'].values):
        ax.text(value + 1, i, f'{value:.1f}%', va='center', fontsize=9, fontweight='bold')
    
    ax.set_xlabel('Resolution SLA Pass Rate (%)', fontsize=12, fontweight='bold')
    ax.set_title('Top 10 Operator Performance', fontsize=14, fontweight='bold', pad=20)
    ax.set_xlim(0, 100)
    ax.legend(fontsize=10)
    ax.grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'chart5_top_operators.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"   ✓ Saved: {output_dir / 'chart5_top_operators.png'}")
    
    # ===== 6. BOTTOM 10 OPERATORS =====
    print("\n📊 Chart 6: Bottom 10 Operator Performance...")
    
    bottom_10_ops = performance['operators'].tail(10)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    bars = ax.barh(range(len(bottom_10_ops)), bottom_10_ops['resolution_pass_rate'].values, 
                   color='#e74c3c', edgecolor='black', linewidth=1.2)
    
    # Add target line
    ax.axvline(x=70, color='orange', linestyle='--', linewidth=2, label='Target (70%)')
    
    # Set y-axis labels
    ax.set_yticks(range(len(bottom_10_ops)))
    ax.set_yticklabels(bottom_10_ops['Operator'].values)
    
    # Add value labels
    for i, value in enumerate(bottom_10_ops['resolution_pass_rate'].values):
        ax.text(value + 1, i, f'{value:.1f}%', va='center', fontsize=9, fontweight='bold')
    
    ax.set_xlabel('Resolution SLA Pass Rate (%)', fontsize=12, fontweight='bold')
    ax.set_title('Bottom 10 Operators (Need Support)', fontsize=14, fontweight='bold', pad=20)
    ax.set_xlim(0, 100)
    ax.legend(fontsize=10)
    ax.grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'chart6_bottom_operators.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"   ✓ Saved: {output_dir / 'chart6_bottom_operators.png'}")
    
    # ===== 7. RESOLUTION CATEGORY DISTRIBUTION =====
    print("\n📊 Chart 7: Resolution Quality Distribution...")
    
    category_counts = data['resolution_category'].value_counts()
    category_order = ['Excellent', 'Good', 'Fair', 'Critical']
    category_counts = category_counts.reindex(category_order)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    colors = ['#2ecc71', '#f39c12', '#3498db', '#e74c3c']
    bars = ax.bar(category_counts.index, category_counts.values, 
                  color=colors, edgecolor='black', linewidth=1.2)
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        percentage = (height / len(data)) * 100
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}\n({percentage:.1f}%)',
                ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    ax.set_ylabel('Number of Tickets', fontsize=12, fontweight='bold')
    ax.set_title('Resolution Quality Distribution', fontsize=14, fontweight='bold', pad=20)
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'chart7_resolution_quality.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"   ✓ Saved: {output_dir / 'chart7_resolution_quality.png'}")
    
    print("\n" + "="*70)
    print("✅ ALL VISUALIZATIONS CREATED")
    print("="*70)
    print(f"\nCharts saved to: {output_dir}/")
    print("\nGenerated Charts:")
    print("  1. chart1_overall_sla.png - Overall SLA performance")
    print("  2. chart2_response_by_channel.png - Response time by channel")
    print("  3. chart3_response_by_zone.png - Response time by zone")
    print("  4. chart4_response_by_fault.png - Response time by fault type")
    print("  5. chart5_top_operators.png - Top 10 operators")
    print("  6. chart6_bottom_operators.png - Bottom 10 operators")
    print("  7. chart7_resolution_quality.png - Quality distribution")