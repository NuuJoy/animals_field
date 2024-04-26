

import redis
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from playground.bases import Base2DSquareField


LOCK_KEY = 'shared_lock'
FIELD_KEY = 'shared_field'


app = FastAPI()
rds = redis.Redis(
    host='redis',
    port=6379,
    charset="utf-8",
    decode_responses=True
)


@app.get("/")
def home():
    return 'Hello, world!'


@app.get("/plaintext", response_class=HTMLResponse)
def plaintext():
    blueprint = rds.get('shared_field')
    if blueprint:
        field = Base2DSquareField()
        field.load(blueprint)

        x_s = [int(x) for (x, _) in field.tiles_dict]
        y_s = [int(y) for (_, y) in field.tiles_dict]

        output = '<p style="font-family:monospace"><pre>'
        for y in range(max(y_s), min(y_s)-1, -1):
            text = ''
            for x in range(min(x_s), max(x_s)+1):
                pos = (x, y)
                if pos in field.tiles_dict:
                    if field.tiles_dict[pos].substances:
                        sub = field.tiles_dict[(x, y)].substances[0]
                        if sub.age <= 10:
                            text += 'v'
                        elif sub.age <= 20:
                            text += 'w'
                        elif sub.age <= 30:
                            text += 'V'
                        else:
                            text += 'W'
                    else:
                        text += '.'
                else:
                    text += ' '
            output += text + '<br>'
        output += '</pre></p>'
        return output
    else:
        return None
