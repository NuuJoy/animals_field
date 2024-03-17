

from __future__ import annotations

import json

from playground import elements
from playground.elements import BaseTile, BaseLiving


class Field2D():
    def __init__(self, blueprint: str | None = None) -> None:
        self._handler: dict[tuple[int, int], BaseTile] = {}
        if blueprint is not None:
            # creat all tile and substance from blueprint data
            mapprop = json.loads(blueprint)
            for key, tileprop in mapprop.items():
                posx, posy = (int(val) for val in key.split(','))
                basetile_cls = getattr(elements, tileprop['classname'])
                tile = basetile_cls(idenstr=tileprop['identifier'])

                for liveprop in tileprop['substances']:
                    baselive_cls = getattr(elements, liveprop['classname'])
                    live = baselive_cls(
                        idenstr=liveprop['identifier'],
                        tile=tile
                    )
                    for attrname, attrval in liveprop.items():
                        if attrname not in (
                            'classname',
                            'identifier',
                            'substances',
                            'connections',
                            'tile'
                        ):
                            setattr(live, attrname, attrval)
                self.add_tile(posx, posy, tile)

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, Field2D):
            return self.serialize() == __value.serialize()
        else:
            return False

    def _get_adjacent_tiles(self, d1: int, d2: int):
        return [
            self._handler[key]
            for key in [
                (d1 - 1, d2),
                (d1 + 1, d2),
                (d1, d2 - 1),
                (d1, d2 + 1)
            ]
            if key in self._handler
        ]

    def add_tile(self, posx: int, posy: int, tile: BaseTile):
        key = (posx, posy)
        if key in self._handler:
            raise KeyError('Adding duplicate key (position has been used)')
        else:
            self._handler[key] = tile
            for adjacent_tile in self._get_adjacent_tiles(posx, posy):
                tile.add_connections(adjacent_tile)

    def remove_tile(self, posx: int, posy: int):
        key = (posx, posy)
        if key not in self._handler:
            raise KeyError('Missing handler key (tile position not found)')
        tile = self._handler[key]
        for con in tile.connections:
            tile.remove_connections(con)
        del self._handler[key]

    @property
    def tiles(self):
        return self._handler

    def get_tile(self, *args: str | int):
        if len(args) == 1:
            for tile in self.tiles.values():
                if tile.identifier == args[0]:
                    return tile
            else:
                raise ValueError(f'Not found tile with identifier: {args[0]}')
        elif len(args) == 2:
            if args in self.tiles:
                return self.tiles[args]
            else:
                raise ValueError(f'Not found tile with key position: {args}')
        else:
            raise ValueError(
                'Expect type "identifier: str" or "position: int, int"')

    @property
    def substances(self) -> list[BaseLiving]:
        return [
            sub
            for tile in self._handler.values()
            for sub in tile.substances
        ]

    def get_substance(self, identifier: str):
        for sub in self.substances:
            if sub.identifier == identifier:
                return sub

    def get_map_properties(self):
        return {
            key: tile.get_properties()
            for key, tile in self._handler.items()
        }

    def serialize(self) -> str:
        return json.dumps({
            f'{d1},{d2}': tileprop
            for (d1, d2), tileprop in self.get_map_properties().items()
        }, indent=4)

    def visualize(self):
        # get boundary
        if not self._handler:
            return

        x_values, y_values = [values for values in zip(*self._handler)]
        x_shift = min(x_values)
        y_shift = min(y_values)
        x_max = max(x_values) - x_shift
        y_max = max(y_values) - y_shift
        # create 2-D array of empty field
        listmap = [
            [' ' for _ in range(x_max + 1)]
            for _ in range(y_max + 1)
        ]
        # mark tile with middle-dot, substance with cross
        for (d1, d2), tile in self._handler.items():
            if not tile.substances:
                listmap[d2 - y_shift][d1 - x_shift] = u'\xb7'
            else:
                listmap[d2 - y_shift][d1 - x_shift] = 'x'
        return '\n'.join([''.join(row) for row in listmap][::-1])
