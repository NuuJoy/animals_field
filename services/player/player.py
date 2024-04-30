

import redis
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
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
app.mount("/static", StaticFiles(directory='static'), name="static")


@app.get('/', response_class=HTMLResponse)
def home():
    return '''<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>RenderField</title>
    </head>
    <body>
        <canvas id="mapcanvas"></canvas>
        <script src="static/js/field_render.js"></script>
    </body>
    </html>'''


@app.get('/jsonmap')
def jsonmap():
    blueprint = rds.get('shared_field')
    if blueprint:
        field = Base2DSquareField()
        field.load(blueprint)
        x_s = [int(x) for (x, _) in field.tiles_dict]
        y_s = [int(y) for (_, y) in field.tiles_dict]

        fieldmap: list[list[int | str]] = []
        for x in range(min(x_s), max(x_s)+1):
            cols: list[int | str] = []
            for y in range(max(y_s), min(y_s)-1, -1):
                pos = (x, y)
                if pos in field.tiles_dict:
                    if field.tiles_dict[pos].substances:
                        sub = field.tiles_dict[(x, y)].substances[0]
                        if sub.age <= 10:
                            cols.append('v')
                        elif sub.age <= 20:
                            cols.append('w')
                        elif sub.age <= 30:
                            cols.append('V')
                        else:
                            cols.append('W')
                    else:
                        cols.append(1)
                else:
                    cols.append(0)
            fieldmap.append(cols)
        return {'fieldmap': fieldmap}
    else:
        return None
