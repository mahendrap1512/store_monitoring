from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.decorators import action
from main.models import StoreStatus, BusinessHours, Timezones
import pandas as pd


class StoreReportViewSet(viewsets.ViewSet):
    def _get_utc_business_hours_df(self, store_id: int)-> pd.DataFrame:
        business_hours_data = BusinessHours.objects.filter(store_id=store_id).values(
            "store_id", "day", "start_time_local", "end_time_local"
        )
        business_hours_df = pd.DataFrame(business_hours_data)
        if business_hours_df.empty:
            business_hours_df = pd.DataFrame(
                {
                    "store_id": [store_id],
                    "day": [day for day in range(7)],
                    "start_time_local": ["00:00:00"],
                    "end_time_local": ["23:59:59"],
                }
            )

        store_timezone_data = Timezones.objects.filter(store_id=store_id).values(
            "store_id", "timezone_str"
        )
        store_timezone_df = pd.DataFrame(store_timezone_data)

        utc_business_hours_df = business_hours_df.merge(
            store_timezone_df, how="left", on=["store_id"]
        )

        # utc_business_hours_df["start_time"] = (
        #     pd.to_time(utc_business_hours_df["start_time_local"])
        #     .dt.tz_localize("timezone_str")
        #     .dt.tz_convert("UTC")
        # )
        # utc_business_hours_df["end_time"] = (
        #     pd.to_datetime(utc_business_hours_df["end_time_local"])
        #     .dt.tz_localize("timezone_str")
        #     .dt.tz_convert("UTC")
        # )
        return utc_business_hours_df

    @action(methods=['get'], url_path='trigger-report', detail=False)
    def trigger_report(self, request):
        # store_id, uptime_last_hour(in minutes), uptime_last_day(in hours), update_last_week(in hours), downtime_last_hour(in minutes), downtime_last_day(in hours), downtime_last_week(in hours)
        store_id = int(request.query_params["store_id"])
        utc_business_hours_df = self._get_utc_business_hours_df(store_id)
        store_status_data = StoreStatus.objects.filter(
            store_id=store_id,
            timestamp_utc__gt=pd.Timestamp.utcnow() - pd.Timedelta(days=7),
        ).values("store_id", "status", "timestamp_utc")
        store_status_df = pd.DataFrame(store_status_data)
        if store_status_df.empty:
            store_status_df = pd.DataFrame(columns=["store_id", "status", "timestamp_utc", "day"])
        else:
            store_status_df["day"] = store_status_df["timestamp_utc"].dt.day

        store_status_df = store_status_df.merge(utc_business_hours_df, how="left", on=["store_id", "day"])

        # Last hour report
        last_hour_range = pd.date_range(end=pd.Timestamp.now(), periods=60, freq='T')
        df_last_hour = store_status_df[store_status_df['timestamp_utc'].dt.floor('H').isin(last_hour_range)]
        df_last_hour = df_last_hour.set_index('timestamp_utc').resample('1T').asfreq().interpolate(method='time')
        uptime_last_hour = df_last_hour[df_last_hour['status'] == 'active'].shape[0]

        # Last day report
        last_day_range = pd.date_range(end=pd.Timestamp.now(), periods=24, freq='H')
        df_last_day = store_status_df[store_status_df['timestamp_utc'].dt.floor('H').isin(last_day_range)]
        df_last_day = df_last_day.set_index('timestamp_utc').resample('1H').asfreq().interpolate(method='time')
        uptime_last_day = df_last_day[df_last_day['status'] == 'active'].shape[0]


        # Last week report
        last_week_range = pd.date_range(end=pd.Timestamp.now(), periods=24*7, freq='H')
        df_last_week = store_status_df[store_status_df['timestamp_utc'].dt.floor('H').isin(last_week_range)]
        df_last_week = df_last_week.set_index('timestamp_utc').resample('1H').asfreq().interpolate(method='time')
        uptime_last_week = df_last_week[df_last_week['status'] == 'active'].shape[0]


        # Create the report dataframe
        report_df = pd.DataFrame({
            'store_id': [store_id],
            'uptime_last_hour': [uptime_last_hour],
            'uptime_last_day': [uptime_last_day],
            'update_last_week': [uptime_last_week],
            'downtime_last_hour': [60-uptime_last_hour],
            'downtime_last_day': [24 - uptime_last_day],
            'downtime_last_week': [24*7 - uptime_last_week],
        })

        # Print the report dataframe
        print(report_df)
