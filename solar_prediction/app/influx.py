import datetime
import json
from influxdb import InfluxDBClient
from flask import current_app



def get_influx_data(date_from: datetime.datetime = None, date_to: datetime.datetime = None):
    try:
        with open("/data/options.json") as f:
            ha_options= json.load(f)
    
        client = InfluxDBClient(
            host=ha_options["influx_host"], 
            port=ha_options["influx_port"],
            username=ha_options["influx_user"],
            password=ha_options["influx_password"],
            database=ha_options["influx_db"]
        )
        current_app.logger.info(f"Connected to InfluxDB at {ha_options['influx_host']}:{ha_options['influx_port']}")
        result = client.query(f"""SELECT max("value") AS "mean_value" FROM "homeassistant"."autogen"."kWh" WHERE {f"time > '{date_from.strftime('%Y-%m-%dT%H:%M:%SZ')}' AND" if date_from else ""} {f"time < '{date_to.strftime('%Y-%m-%dT%H:%M:%SZ')}' AND" if date_to else ""} "entity_id"='today_s_pv_generation' GROUP BY time(1d) FILL(0)""")
        client.close()
    except Exception as e:
        current_app.logger.error(f"Failed to connect to InfluxDB: {e}")
        raise
    return result