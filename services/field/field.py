

from time import sleep
from random import random

import redis

from playground.bases import BaseTile, BaseLiving, Base2DSquareField


LOCK_KEY = 'shared_lock'
FIELD_KEY = 'shared_field'
LIVING_CHANNELS = {
    'BaseLiving': 'baseliving-channel'
}


MAP = [
    [0, 0, 1, 1, 0, 0, 0, 0, 1, 0],
    [0, 1, 1, 1, 1, 0, 1, 1, 0, 0],
    [0, 1, 0, 0, 1, 1, 1, 1, 0, 0],
    [0, 1, 0, 0, 0, 1, 1, 1, 1, 1],
    [0, 0, 0, 1, 1, 1, 1, 1, 1, 0],
    [0, 0, 0, 1, 0, 1, 1, 1, 1, 0],
    [0, 0, 1, 1, 0, 0, 0, 1, 1, 1],
    [1, 1, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 0, 0, 0, 1, 1, 1],
    [0, 1, 0, 1, 1, 0, 0, 0, 0, 0]
]


if __name__ == '__main__':

    rds = redis.Redis(
        host='redis',
        port=6379,
        charset="utf-8",
        decode_responses=True
    )
    rds.flushall()

    field = Base2DSquareField()
    for y, row in enumerate(MAP[::-1]):
        for x, island in enumerate(row):
            if island:
                tile = BaseTile()
                if random() < 0.1:
                    tile.add_substances(BaseLiving())
                field.add_tile(tile, (x, y))

    with rds.lock(LOCK_KEY):
        rds.set(FIELD_KEY, field.serialize())

    sleep(1.0)
    while True:
        blueprint = rds.get(FIELD_KEY)
        if blueprint:
            field = Base2DSquareField()
            field.load(blueprint)

            for tile in field.tiles:
                for living in tile.substances:
                    ch = LIVING_CHANNELS[living.__class__.__name__]
                    rds.publish(ch, living.identifier)

        sleep(1.0)
