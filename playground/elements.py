

from __future__ import annotations
from typing import Any

import uuid
from random import choice


class Entity():
    def __init__(self, idenstr: str | None = None) -> None:
        if idenstr is None:
            idenstr = uuid.uuid1().hex
        self._identifier = idenstr

    @property
    def identifier(self):
        return self._identifier

    def get_properties(self) -> dict[str, Any]:
        return {
            'classname': self.__class__.__name__,
            'identifier': self._identifier,
        }


class EmptySpace(Entity):
    _connections: list[EmptySpace] = []
    _substances: list[BaseLiving] = []

    @property
    def connections(self):
        return self._connections

    @property
    def substances(self):
        return self._substances

    def add_connections(self, obj: EmptySpace):
        self._connections.append(obj)

    def remove_connections(self, obj: EmptySpace):
        self._connections.remove(obj)

    def add_substances(self, obj: BaseLiving):
        self._substances.append(obj)

    def remove_substances(self, obj: BaseLiving):
        self._substances.remove(obj)

    def is_support(self, cls: type[BaseLiving]) -> bool:
        return True

    def get_properties(self) -> dict[str, Any]:
        propdict = super().get_properties()
        propdict.update({
            'connections': [conn.identifier for conn in self.connections],
            'substances': [subs.identifier for subs in self.substances]
        })
        return propdict


class BaseTile(EmptySpace):
    def add_substances(self, obj: BaseLiving):
        super().add_substances(obj)
        obj.tile = self

    def is_support(self, cls: type[BaseLiving]):
        return not any([isinstance(subs, cls) for subs in self.substances])


class Ground(BaseTile):
    def is_support(self, cls: type[BaseLiving]):
        return super().is_support(cls) and issubclass(cls, GroundPlant)


class Water(BaseTile):
    def is_support(self, cls: type[BaseLiving]):
        return super().is_support(cls) and issubclass(cls, WaterPlant)


class BaseLiving(Entity):
    tile: BaseTile
    energy: int = 0
    health: int = 0
    protect: int = 0

    def __setattr__(self, __name: str, __value: Any) -> None:
        if __name in ('energy', 'health', 'protect'):
            __value = max(min(__value, 9), 0)
        super().__setattr__(__name, __value)

    def get_properties(self) -> dict[str, Any]:
        propdict = super().get_properties()
        propdict.update({
            'tile': self.tile.identifier,
            'energy': self.energy,
            'health': self.health,
            'protect': self.protect
        })
        return propdict


class GroundPlant(BaseLiving):
    def __init__(self) -> None:
        self.health = 1

    def standby(self):
        self.energy += 2
        self.health += 1

    def reproduce(self, target_tile: Ground):
        if (
            target_tile in self.tile.connections
        ) and (
            not target_tile.is_support(self.__class__)
        ):
            target_tile.add_substances(self.__class__())
        else:
            raise ValueError('Can\'t reproduce on selected tile')


class WaterPlant(BaseLiving):
    def __init__(self) -> None:
        self.health = 1

    def standby(self):
        self.energy += 1
        self.health += 1

    def float(self):
        support_tiles = [
            conn
            for conn in self.tile.connections
            if conn.is_support(self.__class__)
        ]
        if support_tiles:
            target = choice(support_tiles)
            self.tile.remove_substances(self)
            target.add_substances(self)
        else:
            raise ValueError('No connected support tile')

    def reproduce(self, target_tile: Water):
        if (
            target_tile in self.tile.connections
        ) and (
            not target_tile.is_support(self.__class__)
        ):
            target_tile.add_substances(self.__class__())
        else:
            raise ValueError('Can\'t reproduce on selected tile')
