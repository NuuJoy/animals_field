

from random import random, choice

import redis

from playground.bases import BaseLiving, Base2DSquareField


LOCK_KEY = 'shared_lock'
FIELD_KEY = 'shared_field'


if __name__ == '__main__':

    rds = redis.Redis(
        host='redis',
        port=6379,
        charset="utf-8",
        decode_responses=True
    )

    p = rds.pubsub()
    p.subscribe('baseliving-channel')

    for i, message in enumerate(p.listen()):

        if message['type'] == 'message':
            iden = message['data']

            with rds.lock(LOCK_KEY):
                field = Base2DSquareField()
                blueprint = rds.get(FIELD_KEY)
                if blueprint:
                    field.load(blueprint)

                    process_done = False
                    for tile in field.tiles:
                        for living in tile.substances:
                            if living.identifier == iden:
                                process_done = True

                                living.age += 1
                                if random() < (living.age * 0.001):
                                    living.tile = None
                                elif living.energy < 9:
                                    living.energy += round(random())
                                else:
                                    support_tiles = [
                                        conntile
                                        for conntile in tile.connections
                                        if conntile.is_support(living)
                                    ]
                                    if support_tiles:
                                        target = choice(support_tiles)
                                        living.energy = 0
                                        target.add_substances(BaseLiving())
                                break
                        if process_done:
                            break

                    rds.set(FIELD_KEY, field.serialize())
