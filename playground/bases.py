

from __future__ import annotations
from typing import Any

import json

from playground.interfaces import TileInterface
from playground.interfaces import LivingInterface
from playground.interfaces import FieldInterface


class BaseTile(TileInterface):
    _support_living_classes: tuple[type] = (LivingInterface,)

    def __init__(self, idenstr: str | None = None) -> None:
        super().__init__(idenstr)
        self._connections: list[TileInterface] = []
        self._substances: list[LivingInterface] = []

    @property
    def connections(self) -> list[TileInterface]:
        return self._connections

    @property
    def substances(self) -> list[LivingInterface]:
        return self._substances

    def add_connection(self, other: TileInterface):
        if other not in self.connections:
            self.connections.append(other)
            self.connections.sort(key=lambda con: con.identifier)
            if self not in other.connections:
                other.add_connection(self)

    def remove_connection(self, other: TileInterface):
        if other in self.connections:
            self.connections.remove(other)
            if self in other.connections:
                other.remove_connection(self)

    def add_substances(self, living: LivingInterface):
        if living not in self.substances and self.is_support(living):
            self.substances.append(living)
            self.substances.sort(key=lambda sub: sub.identifier)
            if living.tile is not self:
                living.tile = self

    def remove_substances(self, living: LivingInterface):
        if living in self.substances:
            self.substances.remove(living)

    def is_support(self, living: LivingInterface) -> bool:
        # not allow duplicate type within substance
        return isinstance(living, self._support_living_classes) and not any([
            isinstance(subs, type(living))
            for subs in self.substances
        ])


class BaseLiving(LivingInterface):

    def __init__(self,
                 idenstr: str | None = None,
                 tile: BaseTile | None = None) -> None:
        super().__init__(idenstr)
        self._tile = tile
        if self.tile is not None:
            self.tile.add_substances(self)
        self._age = 0
        self._health = 1
        self._energy = 0

    @property
    def age(self) -> int:
        return self._age

    @age.setter
    def age(self, value: int):
        self._age = value

    @property
    def health(self) -> int:
        return self._health

    @health.setter
    def health(self, value: int):
        self._health = value

    @property
    def energy(self) -> int:
        return self._energy

    @energy.setter
    def energy(self, value: int):
        self._energy = value

    @property
    def tile(self) -> TileInterface | None:
        return self._tile

    @tile.setter
    def tile(self, newtile: TileInterface | None):
        oldtile = self.tile
        self._tile = newtile
        if newtile and (self not in newtile.substances):
            newtile.add_substances(self)
        if oldtile and (self in oldtile.substances):
            oldtile.remove_substances(self)


class Base2DSquareField(FieldInterface):
    def __init__(self):
        self._tiles: dict[tuple[int | float, ...], TileInterface] = {}
        self.border = 1.5

    def load(self, blueprint: str):
        mapprop = json.loads(blueprint)
        for key, tileprop in mapprop.items():
            position = tuple(int(val) for val in key.split(','))
            basetile_cls = globals()[tileprop['classname']]
            tile = basetile_cls(idenstr=tileprop['identifier'])

            for liveprop in tileprop['substances']:
                baselive_cls = globals()[liveprop['classname']]
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
            self.add_tile(tile, position)

    @property
    def tiles(self):
        return tuple(val for val in self._tiles.values())

    @property
    def tiles_dict(self):
        return self._tiles

    def add_tile(self,
                 tile: TileInterface,
                 position: tuple[int | float, ...]):
        position = tuple(int(pos) for pos in position)
        self._tiles[position] = tile
        self._tiles = {k: self._tiles[k] for k in sorted(self._tiles)}

        self.connect_tile(
            tile,
            tuple(
                other_tile
                for other_position, other_tile in self._tiles.items()
                if (
                    self._cal_distance(position, other_position) <= self.border
                ) and (
                    other_tile is not tile
                )
            )
        )

    def _cal_distance(self, pos1: tuple[Any, ...], pos2: tuple[Any, ...]):
        if len(pos1) != len(pos2):
            raise ValueError(
                f'position length not equal ({len(pos1)} and {len(pos2)})'
            )
        else:
            return sum(
                (val1 - val2)**2 for val1, val2 in zip(pos1, pos2)
            ) ** 0.5

    def _get_map_properties(self) -> dict[Any, Any]:
        return {
            key: tile.get_properties()
            for key, tile in self._tiles.items()
        }

    def serialize(self):
        return json.dumps({
            ','.join(str(val) for val in position): tileprop
            for position, tileprop in self._get_map_properties().items()
        }, indent=4)
