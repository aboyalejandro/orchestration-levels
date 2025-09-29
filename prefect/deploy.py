"""
Prefect deployment script for the Piwik ETL flow
"""
from datetime import datetime
from etl_flow import piwik_etl_flow

if __name__ == "__main__":
    # Deploy the flow with scheduling
    piwik_etl_flow.serve(
        name="piwik-etl-deployment",
        cron="0 2 * * *",  # Run daily at 2 AM
        parameters={
            "start_date": datetime(2021, 1, 1),
            "end_date": datetime(2021, 1, 31)
        }
    )