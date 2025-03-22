from influxdb import InfluxDBClient
from flask import current_app

class InfluxDBConnector:
    def __init__(self, host='localhost', port=8086, username='', password='', database=''):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database
        self.client = None

    def connect(self):
        try:
            self.client = InfluxDBClient(
                host=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                database=self.database
            )
            current_app.logger.info(f"Connected to InfluxDB at {self.host}:{self.port}")
        except Exception as e:
            current_app.logger.error(f"Failed to connect to InfluxDB: {e}")
            raise

    def query_data(self, query):
        if not self.client:
            current_app.logger.error("InfluxDB client is not connected.")
        try:
            result = self.client.query(query)
            return result
        except Exception as e:
            current_app.logger.error(f"Failed to query data from InfluxDB: {e}")
            raise

    def close(self):
        if self.client:
            self.client.close()
            current_app.logger.info("InfluxDB connection closed.")