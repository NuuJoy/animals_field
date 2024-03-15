

from __future__ import annotations

import json

from playground.elements import BaseTile, BaseLiving


class Field2D():
    def __init__(self) -> None:
        self.handler: dict[tuple[int, int], BaseTile] = {}

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, Field2D):
            return self.serialize() == __value.serialize()
        else:
            return False

    def _get_adjacent_tiles(self, d1: int, d2: int):
        return [
            self.handler[key]
            for key in [
                (d1 - 1, d2),
                (d1 + 1, d2),
                (d1, d2 - 1),
                (d1, d2 + 1)
            ]
            if key in self.handler
        ]

    def add_tile(self, posx: int, posy: int, tile: BaseTile):
        key = (posx, posy)
        if key in self.handler:
            raise KeyError('Adding duplicate key (position has been used)')
        else:
            self.handler[key] = tile
            for adjacent_tile in self._get_adjacent_tiles(posx, posy):
                tile.add_connections(adjacent_tile)

    def remove_tile(self, posx: int, posy: int):
        key = (posx, posy)
        if key not in self.handler:
            raise KeyError('Missing handler key (tile position not found)')
        tile = self.handler[key]
        for con in tile.connections:
            tile.remove_connections(con)
        del self.handler[key]

    def get_substances(self) -> list[BaseLiving]:
        return [
            sub
            for tile in self.handler.values()
            for sub in tile.substances
        ]

    def get_map_properties(self):
        return {
            f'{d1},{d2}': tile.get_properties()
            for (d1, d2), tile in self.handler.items()
        }

    def serialize(self) -> str:
        return json.dumps(self.get_map_properties(), indent=4)

    def visualize(self):
        # get boundary
        x_values, y_values = [values for values in zip(*self.handler)]
        x_shift = min(x_values)
        y_shift = min(y_values)
        x_max = max(x_values) - x_shift
        y_max = max(y_values) - y_shift
        # create 2-D array of empty field
        listmap = [
            [' ' for _ in range(x_max + 1)]
            for _ in range(y_max + 1)
        ]
        # mark tile with middle-dot
        for d1, d2 in self.handler:
            listmap[d2 - y_shift][d1 - x_shift] = u'\xb7'
        return '\n'.join([''.join(row) for row in listmap][::-1])
