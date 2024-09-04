import redis
import datetime

class ValkeyLog:
    def __init__(self, host="localhost", port=6379, db=0):
        """
        Initialize the Valkey connection, similar to Redis.
        """
        self.host = host
        self.port = port
        self.db = db
        self.r = redis.Redis(host=self.host, port=self.port, db=self.db)

    def log(self, sensor_d, sensor_a):
        """
        Log sensor data with a timestamp in Valkey.
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = {
            'timestamp': timestamp,
            'sensor_a': sensor_a,
            'sensor_d': sensor_d
        }

        # Increment a counter to ensure unique keys for each log entry
        key = self.r.incr("data_counter")

        # Store the data as a hash in Valkey
        self.r.hset(f"data_{key}", mapping=data)

        print(f"Logged data at key: data_{key}")

