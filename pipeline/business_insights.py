import pandas as pd
import numpy as np

def analyze_overall_performance(data, weekly_kpis):
    total_tickets = len(data)
    
    response_pass_count = data['response_sla_pass'].sum()
    response_pass_rate = (response_pass_count / total_tickets) * 100
    avg_response_time = data['response_seconds'].mean()
    
    """ SLA metrics """
    resolution_pass_count = data['resolution_sla_pass'].sum()
    resolution_pass_rate = (resolution_pass_count / total_tickets) * 100
    avg_resolution_time = data['resolution_minutes'].mean()
    
    escalation_count = (data['resolution_minutes'] > 180).sum()
    escalation_rate = (escalation_count / total_tickets) * 100
    
    category_dist = data['resolution_category'].value_counts()
    category_pct = (category_dist / total_tickets * 100).round(2)
   
    print(f"Total Tickets Processed:        {total_tickets:,}")
    print(f"Time Period:                    {data['Ticket Open Time'].min().date()} to {data['Ticket Open Time'].max().date()}")
    print(f"Number of Weeks:                {len(weekly_kpis)}")
    
    print(f"Target:                         ≤ 10 seconds")
    print(f"Average Response Time:          {avg_response_time:.2f} seconds")
    print(f"Tickets Meeting Response SLA:   {response_pass_count:,} / {total_tickets:,}")
    print(f"Response SLA Pass Rate:         {response_pass_rate:.2f}%")
    
    # Status indicator
    if response_pass_rate >= 90:
        status = "✅ EXCELLENT"
    elif response_pass_rate >= 70:
        status = "⚠️  NEEDS IMPROVEMENT"
    else:
        status = "❌ CRITICAL"
    print(f"Status:                         {status}")
    
    print("\n🎯 RESOLUTION TIME PERFORMANCE")
    print("-" * 70)
    print(f"Target:                         ≤ 180 minutes (3 hours)")
    print(f"Average Resolution Time:        {avg_resolution_time:.2f} minutes ({avg_resolution_time/60:.2f} hours)")
    print(f"Tickets Meeting Resolution SLA: {resolution_pass_count:,} / {total_tickets:,}")
    print(f"Resolution SLA Pass Rate:       {resolution_pass_rate:.2f}%")
    
    # Status indicator
    if resolution_pass_rate >= 80:
        status = "✅ EXCELLENT"
    elif resolution_pass_rate >= 60:
        status = "⚠️  NEEDS IMPROVEMENT"
    else:
        status = "❌ CRITICAL"
    print(f"Status:                         {status}")
    
    print("\n🚨 ESCALATIONS")
    print("-" * 70)
    print(f"Total Escalations:              {escalation_count:,}")
    print(f"Escalation Rate:                {escalation_rate:.2f}%")
    print(f"Target Escalation Rate:         < 20%")
    
    if escalation_rate < 20:
        status = "✅ WITHIN TARGET"
    elif escalation_rate < 35:
        status = "⚠️  ABOVE TARGET"
    else:
        status = "❌ SIGNIFICANTLY ABOVE TARGET"
    print(f"Status:                         {status}")
    
    print("\n📈 RESOLUTION QUALITY BREAKDOWN")
    print("-" * 70)
    for category in ['Excellent', 'Good', 'Fair', 'Critical']:
        if category in category_dist.index:
            count = category_dist[category]
            pct = category_pct[category]
            print(f"{category:12s}: {count:6,} tickets ({pct:5.2f}%)")
    
    print("\n📅 WEEKLY TRENDS")
    print("-" * 70)
    print(f"Best Week (Response SLA):       Week {weekly_kpis.loc[weekly_kpis['response_pass_rate'].idxmax(), 'year_week']} - {weekly_kpis['response_pass_rate'].max():.2f}%")
    print(f"Worst Week (Response SLA):      Week {weekly_kpis.loc[weekly_kpis['response_pass_rate'].idxmin(), 'year_week']} - {weekly_kpis['response_pass_rate'].min():.2f}%")
    print(f"Best Week (Resolution SLA):     Week {weekly_kpis.loc[weekly_kpis['resolution_pass_rate'].idxmax(), 'year_week']} - {weekly_kpis['resolution_pass_rate'].max():.2f}%")
    print(f"Worst Week (Resolution SLA):    Week {weekly_kpis.loc[weekly_kpis['resolution_pass_rate'].idxmin(), 'year_week']} - {weekly_kpis['resolution_pass_rate'].min():.2f}%")
    
    # Calculate trend (is performance improving or declining?)
    if len(weekly_kpis) >= 4:
        # Compare first quarter vs last quarter of data
        first_quarter = weekly_kpis.head(len(weekly_kpis)//4)
        last_quarter = weekly_kpis.tail(len(weekly_kpis)//4)
        
        response_trend = last_quarter['response_pass_rate'].mean() - first_quarter['response_pass_rate'].mean()
        resolution_trend = last_quarter['resolution_pass_rate'].mean() - first_quarter['resolution_pass_rate'].mean()
        
        print(f"\nResponse SLA Trend:             {'+' if response_trend > 0 else ''}{response_trend:.2f}% {'📈' if response_trend > 0 else '📉'}")
        print(f"Resolution SLA Trend:           {'+' if resolution_trend > 0 else ''}{resolution_trend:.2f}% {'📈' if resolution_trend > 0 else '📉'}")
    
    print("\n" + "="*70)
    print("OVERALL BUSINESS HEALTH ASSESSMENT")
    print("="*70)
    
    # Calculate overall score
    score = 0
    max_score = 3
    
    if response_pass_rate >= 70:
        score += 1
    if resolution_pass_rate >= 60:
        score += 1
    if escalation_rate < 35:
        score += 1
    
    health_percentage = (score / max_score) * 100
    
    if health_percentage >= 80:
        health = "🟢 HEALTHY - Meeting most targets"
    elif health_percentage >= 50:
        health = "🟡 MODERATE - Significant room for improvement"
    else:
        health = "🔴 CRITICAL - Immediate action required"
    
    print(f"\nOverall Health Score:           {score}/{max_score} ({health_percentage:.0f}%)")
    print(f"Assessment:                     {health}")
    
    print("\n💡 KEY FINDINGS:")
    findings = []
    
    if response_pass_rate < 70:
        findings.append(f"   • Response time FAILS target: Only {response_pass_rate:.1f}% of tickets responded to within 10 seconds")
    
    if avg_response_time > 15:
        findings.append(f"   • Average response time ({avg_response_time:.1f}s) exceeds the 15-second average target")
    
    if resolution_pass_rate < 70:
        findings.append(f"   • Resolution time FAILS target: Only {resolution_pass_rate:.1f}% resolved within 3 hours")
    
    if escalation_rate > 30:
        findings.append(f"   • High escalation rate ({escalation_rate:.1f}%) indicates systemic issues")
    
    if category_dist.get('Critical', 0) > category_dist.get('Excellent', 0):
        findings.append(f"   • More 'Critical' resolutions than 'Excellent' - quality concerns")
    
    if not findings:
        findings.append("   • Performance is generally meeting targets")
    
    for finding in findings:
        print(finding)
    
    print("\n" + "="*70)
    
    # Return metrics for further analysis
    return {
        'total_tickets': total_tickets,
        'response_pass_rate': response_pass_rate,
        'resolution_pass_rate': resolution_pass_rate,
        'avg_response_time': avg_response_time,
        'avg_resolution_time': avg_resolution_time,
        'escalation_rate': escalation_rate,
        'health_score': health_percentage,
        'category_distribution': category_dist.to_dict()
    }


def analyze_response_delays(data):
    results = {}
    
    # ===== 1. CHANNEL ANALYSIS =====
    print("\n📱 FACTOR 1: COMMUNICATION CHANNEL")
    
    channel_stats = data.groupby('Channel').agg({
        'Report ID': 'count',
        'response_seconds': 'mean',
        'response_sla_pass': lambda x: (x.sum() / len(x) * 100)
    }).round(2)
    
    channel_stats.columns = ['Total Tickets', 'Avg Response (sec)', 'SLA Pass Rate (%)']
    channel_stats = channel_stats.sort_values('Avg Response (sec)', ascending=False)
    
    print(channel_stats)
    
    print("\n💡 INSIGHTS:")
    slowest_channel = channel_stats.index[0]
    fastest_channel = channel_stats.index[-1]
    slowest_time = channel_stats.iloc[0]['Avg Response (sec)']
    fastest_time = channel_stats.iloc[-1]['Avg Response (sec)']
    
    print(f"   • SLOWEST: {slowest_channel} ({slowest_time:.1f} seconds)")
    print(f"   • FASTEST: {fastest_channel} ({fastest_time:.1f} seconds)")
    print(f"   • Difference: {slowest_time - fastest_time:.1f} seconds")
    
    results['channel'] = channel_stats
    
    # ===== 2. GEOGRAPHIC ANALYSIS (STATE) =====
    print("\n\n🗺️  FACTOR 2: GEOGRAPHIC LOCATION (STATE)")
 
    state_stats = data.groupby('State').agg({
        'Report ID': 'count',
        'response_seconds': 'mean',
        'response_sla_pass': lambda x: (x.sum() / len(x) * 100)
    }).round(2)
    
    state_stats.columns = ['Total Tickets', 'Avg Response (sec)', 'SLA Pass Rate (%)']
    state_stats = state_stats.sort_values('Avg Response (sec)', ascending=False)
    
    print("\nTOP 5 SLOWEST STATES:")
    print(state_stats.head(5))
    
    print("\nTOP 5 FASTEST STATES:")
    print(state_stats.tail(5))
    
    print("\n💡 INSIGHTS:")
    slowest_state = state_stats.index[0]
    fastest_state = state_stats.index[-1]
    print(f"   • SLOWEST: {slowest_state} ({state_stats.iloc[0]['Avg Response (sec)']:.1f} seconds)")
    print(f"   • FASTEST: {fastest_state} ({state_stats.iloc[-1]['Avg Response (sec)']:.1f} seconds)")
    
    # ===== 3. SERVICE TYPE ANALYSIS =====
    print("\n\n🔧 FACTOR 3: SERVICE TYPE")
    
    service_stats = data.groupby('Service Name').agg({
        'Report ID': 'count',
        'response_seconds': 'mean',
        'response_sla_pass': lambda x: (x.sum() / len(x) * 100)
    }).round(2)
    
    service_stats.columns = ['Total Tickets', 'Avg Response (sec)', 'SLA Pass Rate (%)']
    service_stats = service_stats.sort_values('Avg Response (sec)', ascending=False)
    
    print(service_stats)
    
    print("\n💡 INSIGHTS:")
    slowest_service = service_stats.index[0]
    fastest_service = service_stats.index[-1]
    print(f"   • SLOWEST: {slowest_service} ({service_stats.iloc[0]['Avg Response (sec)']:.1f} seconds)")
    print(f"   • FASTEST: {fastest_service} ({service_stats.iloc[-1]['Avg Response (sec)']:.1f} seconds)")
    
    results['service'] = service_stats
    
    # ===== 4. FAULT TYPE ANALYSIS =====
    print("\n\n⚠️  FACTOR 4: FAULT TYPE")
    
    fault_stats = data.groupby('Fault Type').agg({
        'Report ID': 'count',
        'response_seconds': 'mean',
        'response_sla_pass': lambda x: (x.sum() / len(x) * 100)
    }).round(2)
    
    fault_stats.columns = ['Total Tickets', 'Avg Response (sec)', 'SLA Pass Rate (%)']
    fault_stats = fault_stats.sort_values('Avg Response (sec)', ascending=False)
    
    print(fault_stats)
    
    print("\n💡 INSIGHTS:")
    slowest_fault = fault_stats.index[0]
    fastest_fault = fault_stats.index[-1]
    print(f"   • SLOWEST: {slowest_fault} ({fault_stats.iloc[0]['Avg Response (sec)']:.1f} seconds)")
    print(f"   • FASTEST: {fastest_fault} ({fault_stats.iloc[-1]['Avg Response (sec)']:.1f} seconds)")
    
    results['fault'] = fault_stats