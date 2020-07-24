from influxdb import InfluxDBClient
import prog_files.vars as CN
import random
import time

if __name__ == "__main__":
    variables = {}
    for a in "asdfghjkl":
        variables[a] = float(random.randint(0, 20))
    client = InfluxDBClient(CN.DB_ADDRESS, database=CN.DB_NAME)

    while True:
        ms = {
            "measurement": CN.MEASURE_NAME,
            "fields": variables
        }
        client.write_points([ms])
        time.sleep(1)
        for a in variables:
            variables[a] += (-1 + 2*random.randint(0, 1))*random.random()
