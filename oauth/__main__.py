import jwt
import web_mqtt.__main__ as wm

secret = "secrsecrsecr"

user = {
    "ann": "ann123"
}


async def get_tok(request):
    post = await request.post()
    username = post.get('username', None)
    password = post.get('password', None)
    if username is None or password is None:
        return False
    us = str(username)
    if us not in user:
        return False
    if str(password) != user[us]:
        return False
    return jwt.encode({"user": us}, secret, algorithm='HS256').decode()


async def check_tok(request):
    hd = request.headers
    t = hd.get('Authorization', "").split(" ")
    if len(t) != 2:
        return False
    if t[0] != 'Bearer':
        return False
    tok = str(t[1])
    try:
        tt = jwt.decode(tok, secret, algorithms=['HS256'])
        us = tt['user']
        if us in user:
            return True
    except Exception:
        return False


def ct_decor(f):
    async def decorator(request):
        t = await check_tok(request)
        if not t:
            return False
        return await f(request)
    return decorator


wm.req_list['mqtt'] = ct_decor(wm.mqtt_add)
wm.req_list['tok'] = get_tok


if __name__ == '__main__':
    wm.web.run_app(wm.app, port=2155)
