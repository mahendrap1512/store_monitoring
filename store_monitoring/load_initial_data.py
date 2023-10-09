import pandas as pd
import pathlib
from main.models import StoreStatus, BusinessHours, Timezones

BASE_DIR: pathlib.Path = pathlib.Path(__file__).resolve().parent.parent
DATA_DIR = f"{BASE_DIR}/initial_data"
CHUNK_SIZE = 1000


def load_store_status():
    store_status = pd.read_csv(f"{DATA_DIR}/store_status.csv", chunksize=CHUNK_SIZE)
    for chunk in store_status:
        chunk["timestamp_utc"] = pd.to_datetime(
            chunk["timestamp_utc"], format="mixed", utc=True
        )
        data = chunk.to_dict(orient="records")
        StoreStatus.objects.bulk_create(StoreStatus(**d) for d in data)


def load_business_hours():
    business_hours = pd.read_csv(f"{DATA_DIR}/business_hours.csv", chunksize=CHUNK_SIZE)
    for chunk in business_hours:
        data = chunk.to_dict(orient="records")
        BusinessHours.objects.bulk_create(BusinessHours(**d) for d in data)


def load_store_timezones():
    timezones = pd.read_csv(f"{DATA_DIR}/store_timezone.csv", chunksize=CHUNK_SIZE)
    for chunk in timezones:
        data = chunk.to_dict(orient="records")
        Timezones.objects.bulk_create(Timezones(**d) for d in data)
