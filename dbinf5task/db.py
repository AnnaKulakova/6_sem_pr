import time
from datetime import datetime
from dateutil.relativedelta import relativedelta

from influxdb import InfluxDBClient
from prog_files import vars


if __name__ == "__main__":
    t = input("measure name>> ")
    variables = input("variable>> ")
    if variables == "":
        variables = "*"
    time_string = "%d:%m:%Y:%H:%M:%S"
    time_b = input("(begin_time)"+time_string + ">> ")
    struct_time = datetime.strptime(time_b, time_string)
    time_d_string = "%H:%M:%S"
    time_l = input("(time_mes)"+time_d_string + ">> ")
    td = time_l.split(":")
    struct_time_2 = struct_time + relativedelta(hours=int(td[0]), minutes=int(td[1]), seconds=int(td[2]))
    time_b_s = int((struct_time-datetime(1970,1,1)).total_seconds()) * 1000000000
    time_e_s = int((struct_time_2 - datetime(1970, 1, 1)).total_seconds()) * 1000000000
    q_s = 'SELECT ' + variables + " FROM " + t + ' WHERE "time" > ' + str(time_b_s) + ' AND "time" < ' + str(time_e_s)
    conn = InfluxDBClient(vars.DB_ADDRESS, database=vars.DB_NAME)
    a = time.time()
    pt = conn.query(q_s)
    a = time.time() - a
    print(list(pt.get_points()))
    print(a)
