import asyncio
import random
from influxdb import InfluxDBClient
from aiohttp import web
from asyncio_mqtt import Client
from prog_files.vars import DB_NAME, DB_ADDRESS, MEASURE_NAME, MQTT_ADDR


variables = {}
app = web.Application()
db = InfluxDBClient(DB_ADDRESS, database=DB_NAME)
mqtt_cli = Client(MQTT_ADDR)
mqtt_init_procedure_done = False
writing = False
writingdb = False


async def start_imulator_loop():
    while writing:
        time_sleep = 1
        for name in variables:
            if variables[name][1]:
                variables[name][0] = float(random.randint(0, 20))
                if variables[name][2] > time_sleep:
                    time_sleep = variables[name][1]
        for name in variables:
            if variables[name][1]:
                variables[name][2] -= time_sleep
                if variables[name][2] <= 0:
                    variables[name][2] = variables[name][3]
        await asyncio.sleep(time_sleep)


async def start_imulate(request):
    global writing
    if not writing:
        writing = True
        asyncio.get_event_loop().create_task(start_imulator_loop())
        return True
    return False


async def stop_emulate(request):
    global writing
    if writing:
        writing = False
        return True
    return False


async def add_variable(request):
    post = await request.post()
    nm = post.get('var_name', None)
    val = post.get('value', None)
    sleep_time = post.get('sleep_time', None)
    variables[nm] = [float(val), True, float(sleep_time), float(sleep_time)]
    return True


async def del_variable(request):
    post = await request.post()
    if variables.get(post['var_name'], None) is None:
        return False
    variables.pop(post['var_name'])
    return True


async def writer_loop(sleep_time):
    while writingdb:
        fields = {}
        for name in variables:
            if variables[name][0] is not None:
                fields[name] = variables[name][0]
        if fields:
            db.write_points([{
                "measurement": MEASURE_NAME,
                "fields": fields
            }])
        await asyncio.sleep(sleep_time)


async def start_write(request):
    global writingdb
    post = await request.post()
    if post.get('sleep_time', None) is None or writingdb:
        return False
    writingdb = True
    asyncio.get_event_loop().create_task(writer_loop(float(post['sleep_time'])))
    return True


async def stop_write(request):
    global writingdb
    if writingdb:
        writingdb = False
        return True
    return False


async def get_info(request):
    return variables


async def mqtt_coroutine():
    while True:
        async with mqtt_cli.unfiltered_messages() as messages:
            async for message in messages:
                var_name = message.topic.split("/")[-1]
                if var_name not in variables:
                    continue
                try:
                    variables[var_name][0] = float(message.payload.decode())
                except Exception:
                    pass


async def mqtt_add(request):
    global  mqtt_init_procedure_done
    post = await request.post()
    nm = post.get('var_name', None)
    tp = post.get('topic', None)
    if tp is None or nm is None:
        return False
    if not mqtt_init_procedure_done:
        mqtt_init_procedure_done = True
        await mqtt_cli.connect()
        asyncio.get_event_loop().create_task(mqtt_coroutine())
    variables[nm] = [None, False, 0, 0]
    await mqtt_cli.subscribe(tp + '/' + nm)
    return True


req_list = {
    'start_im': start_imulate,
    'stop_im': stop_emulate,
    'start_write': start_write,
    'stop_write': stop_write,
    'add': add_variable,
    'del': del_variable,
    'info': get_info,
    'mqtt': mqtt_add
}


async def main_route_function(request):
    post = await request.post()
    if post.get("req", None) is None:
        return web.json_response({"status": "error", "desc": "no param req"})
    f = req_list.get(post['req'], None)
    if f is None:
        return web.json_response({"status": "error", "desc": "this req not supported"})
    rk = await f(request)
    return web.json_response({"status": "DONE", "desc": rk})


app.add_routes([
    web.post('/api', main_route_function)
])

if __name__ == '__main__':
    web.run_app(app, port=2155)
