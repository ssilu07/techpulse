"""
TechSeconds / TechPulse Google Analytics 4 (GA4) Automated Reporter
Connects via Google Analytics Data API (v1beta) to fetch real-time and historical analytics.
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Optional

# Ensure UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent

# Credential search locations
KEY_FILES = [
    BASE_DIR / "ga_service_account.json",
    BASE_DIR / "service_account.json",
    BASE_DIR / "credentials.json",
]


def find_credentials_file() -> Optional[Path]:
    """Finds service account JSON key file or environment variable."""
    env_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if env_path and Path(env_path).exists():
        return Path(env_path)
    for kf in KEY_FILES:
        if kf.exists():
            return kf
    return None


def get_client():
    """Initializes and returns BetaAnalyticsDataClient."""
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    key_file = find_credentials_file()
    if key_file:
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(key_file.resolve())
        return BetaAnalyticsDataClient()
    
    # Try default credentials
    return BetaAnalyticsDataClient()


def run_realtime_report(property_id: str):
    """Fetches real-time visitors in the last 30 minutes."""
    from google.analytics.data_v1beta.types import (
        RunRealtimeReportRequest,
        Metric,
        Dimension,
    )

    client = get_client()
    request = RunRealtimeReportRequest(
        property=f"properties/{property_id}",
        dimensions=[
            Dimension(name="country"),
            Dimension(name="unifiedScreenName"),
        ],
        metrics=[Metric(name="activeUsers")],
    )

    response = client.run_realtime_report(request)
    print("\n" + "=" * 50)
    print("⚡ TECHSECONDS - REALTIME AUDIENCE (LAST 30 MINS)")
    print("=" * 50)

    total_active = 0
    for row in response.rows:
        users = int(row.metric_values[0].value)
        total_active += users
        country = row.dimension_values[0].value
        page = row.dimension_values[1].value
        print(f" • [{country}] {page} -> {users} active user(s)")

    if not response.rows:
        print("ℹ️ Currently 0 active users in the last 30 minutes.")
    else:
        print(f"\n🔥 Total Active Users (Last 30 mins): {total_active}")
    print("=" * 50 + "\n")


def run_period_report(property_id: str, days: int = 7, is_yesterday: bool = False):
    """Fetches high-level performance over the last N days or yesterday."""
    from google.analytics.data_v1beta.types import (
        RunReportRequest,
        DateRange,
        Metric,
        Dimension,
        OrderBy,
    )

    client = get_client()
    if is_yesterday:
        start_date = "yesterday"
        end_date = "yesterday"
        title_period = "YESTERDAY"
    elif days > 1:
        start_date = f"{days}daysAgo"
        end_date = "today"
        title_period = f"LAST {days} DAYS"
    else:
        start_date = "today"
        end_date = "today"
        title_period = "TODAY"

    # 1. Overview metrics
    overview_req = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        metrics=[
            Metric(name="activeUsers"),
            Metric(name="newUsers"),
            Metric(name="sessions"),
            Metric(name="screenPageViews"),
            Metric(name="engagedSessions"),
            Metric(name="engagementRate"),
            Metric(name="userEngagementDuration"),
        ],
    )
    overview_res = client.run_report(overview_req)

    print("\n" + "=" * 60)
    print(f"📊 TECHSECONDS - PERFORMANCE REPORT ({title_period})")
    print("=" * 60)

    if overview_res.rows:
        vals = overview_res.rows[0].metric_values
        active_users = vals[0].value
        new_users = vals[1].value
        sessions = vals[2].value
        page_views = vals[3].value
        engaged_sessions = vals[4].value
        eng_rate = float(vals[5].value) * 100
        avg_duration = (
            float(vals[6].value) / int(active_users) if int(active_users) > 0 else 0
        )

        print(f"👤 Total Active Users:     {active_users}")
        print(f"✨ New Users:              {new_users}")
        print(f"🔄 Sessions:               {sessions}")
        print(f"👁️ Page Views:             {page_views}")
        print(f"🎯 Engaged Sessions:       {engaged_sessions} ({eng_rate:.1f}% Engagement Rate)")
        print(f"⏱️ Avg Engagement Time:    {avg_duration:.1f} seconds / user")
    else:
        print("ℹ️ No data recorded for this time period.")

    # 2. Top Countries
    country_req = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimensions=[Dimension(name="country")],
        metrics=[Metric(name="activeUsers"), Metric(name="engagedSessions")],
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="activeUsers"), desc=True)],
        limit=5,
    )
    country_res = client.run_report(country_req)

    print("\n🌍 TOP COUNTRIES:")
    print("-" * 60)
    for row in country_res.rows:
        country = row.dimension_values[0].value
        users = row.metric_values[0].value
        engaged = row.metric_values[1].value
        print(f" • {country:20} -> {users:>3} users ({engaged} engaged)")

    # 3. Top Pages / Stories
    pages_req = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimensions=[Dimension(name="pageTitle")],
        metrics=[Metric(name="screenPageViews"), Metric(name="activeUsers")],
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="screenPageViews"), desc=True)],
        limit=8,
    )
    pages_res = client.run_report(pages_req)

    print("\n📄 TOP PAGES & STORIES:")
    print("-" * 60)
    for row in pages_res.rows:
        title = row.dimension_values[0].value[:45]
        views = row.metric_values[0].value
        users = row.metric_values[1].value
        print(f" • {title:45} -> {views:>3} views ({users} users)")

    # 4. Traffic Channels / Sources
    channels_req = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimensions=[Dimension(name="sessionPrimaryChannelGroup")],
        metrics=[Metric(name="sessions"), Metric(name="engagedSessions")],
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="sessions"), desc=True)],
        limit=5,
    )
    channels_res = client.run_report(channels_req)

    print("\n🚦 TRAFFIC CHANNELS:")
    print("-" * 60)
    for row in channels_res.rows:
        channel = row.dimension_values[0].value
        sessions = row.metric_values[0].value
        engaged = row.metric_values[1].value
        print(f" • {channel:20} -> {sessions:>3} sessions ({engaged} engaged)")

    print("=" * 60 + "\n")


def print_setup_instructions():
    """Prints clear setup guide if credentials or property ID are missing."""
    print("""
========================================================================
⚠️  GOOGLE ANALYTICS 4 DATA API SETUP INSTRUCTIONS
========================================================================
1. GOOGLE CLOUD CONSOLE:
   - Go to: https://console.cloud.google.com/
   - Create a project (or pick an existing one).
   - Search for 'Google Analytics Data API' and click ENABLE.
   - Go to 'APIs & Services' > 'Credentials' > 'Create Credentials' > 'Service Account'.
   - Name it (e.g. 'ga-reader') and click 'Done'.
   - Click on the created service account > 'Keys' tab > 'Add Key' > 'Create new key' > JSON.
   - Download the file and save it in this project folder as:
     ga_service_account.json

2. GOOGLE ANALYTICS ACCESS:
   - Open Google Analytics (https://analytics.google.com/).
   - Click the Gear icon ⚙️ (Admin) at bottom-left.
   - In Property column, click 'Property Access Management'.
   - Click the '+' button > 'Add users'.
   - Paste the service account email (ends with @...gserviceaccount.com).
   - Set role to 'Viewer' and click 'Add'.

3. FIND YOUR NUMERIC PROPERTY ID:
   - In GA4 Admin ⚙️, under Property column, click 'Property details'.
   - Look at the top right for 'PROPERTY ID' (numeric e.g., 423456789).
   - Pass it with --property-id <ID> or set GA4_PROPERTY_ID in your environment.
========================================================================
""")


def main():
    parser = argparse.ArgumentParser(description="TechSeconds GA4 Analytics Reporter")
    parser.add_argument(
        "--property-id",
        default=os.environ.get("GA4_PROPERTY_ID", "558519433"),
        help="Numeric GA4 Property ID (found in Admin > Property details)",
    )
    parser.add_argument("--realtime", action="store_true", help="Fetch real-time active users (last 30 mins)")
    parser.add_argument("--yesterday", action="store_true", help="Fetch report specifically for yesterday")
    parser.add_argument("--days", type=int, default=7, help="Number of past days to report (default: 7)")
    parser.add_argument("--setup", action="store_true", help="Show setup instructions")

    args = parser.parse_args()

    if args.setup or not find_credentials_file() or not args.property_id:
        if not find_credentials_file() or not args.property_id:
            print_setup_instructions()
            if not find_credentials_file():
                print("❌ Missing: 'ga_service_account.json' key file not found in project directory.")
            if not args.property_id:
                print("❌ Missing: Numeric GA4 Property ID not provided.")
                print("   Run: python analytics_reporter.py --property-id <NUMERIC_ID>")
            sys.exit(1)

    try:
        if args.realtime:
            run_realtime_report(args.property_id)
        else:
            run_period_report(args.property_id, days=args.days, is_yesterday=args.yesterday)
    except Exception as e:
        print(f"\n❌ API Error: {e}")
        print("Please check that the Service Account has been added as a Viewer in GA4 Property Access Management.")
        sys.exit(1)


if __name__ == "__main__":
    main()
