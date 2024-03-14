

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
    def __init__(self, idenstr: str | None = None) -> None:
        super().__init__(idenstr)
        self._connections: list[EmptySpace] = []
        self._substances: list[BaseLiving] = []

    @property
    def connections(self):
        return self._connections

    @property
    def substances(self):
        return self._substances

    def add_connections(self, obj: EmptySpace):
        if obj not in self._connections:
            self._connections.append(obj)

    def remove_connections(self, obj: EmptySpace):
        if obj in self._connections:
            self._connections.remove(obj)

    def add_substances(self, obj: BaseLiving):
        if obj not in self._substances:
            self._substances.append(obj)

    def remove_substances(self, obj: BaseLiving):
        if obj in self._substances:
            self._substances.remove(obj)

    def is_support(self, cls: type[BaseLiving]) -> bool:
        return True

    def get_properties(self) -> dict[str, Any]:
        propdict = super().get_properties()
        propdict.update({
            'connections': [con.identifier for con in self.connections],
            'substances': [sub.get_properties() for sub in self.substances]
        })
        return propdict


class BaseTile(EmptySpace):
    def add_connections(self, obj: EmptySpace, twoway: bool = True):
        super().add_connections(obj)
        if twoway and isinstance(obj, BaseTile):
            obj.add_connections(self, twoway=False)

    def remove_connections(self, obj: EmptySpace, twoway: bool = True):
        super().remove_connections(obj)
        if twoway and isinstance(obj, BaseTile):
            obj.remove_connections(self, twoway=False)

    def add_substances(self, obj: BaseLiving):
        super().add_substances(obj)
        obj.tile = self

    def remove_substances(self, obj: BaseLiving):
        super().remove_substances(obj)
        obj.tile = None

    def is_support(self, cls: type[BaseLiving]):
        # not allow duplicate type within substance
        return not any([isinstance(subs, cls) for subs in self.substances])


class Ground(BaseTile):
    def is_support(self, cls: type[BaseLiving]):
        return super().is_support(cls) and issubclass(cls, GroundPlant)


class Water(BaseTile):
    def is_support(self, cls: type[BaseLiving]):
        return super().is_support(cls) and issubclass(cls, WaterPlant)


class BaseLiving(Entity):
    energy: int = 0
    health: int = 0
    protect: int = 0

    def __init__(self,
                 idenstr: str | None = None,
                 tile: BaseTile | None = None) -> None:
        super().__init__(idenstr)
        self.tile = tile
        if self.tile is not None:
            self.tile.add_substances(self)

    def __setattr__(self, __name: str, __value: Any) -> None:
        if __name in ('energy', 'health', 'protect'):
            __value = max(min(__value, 9), 0)
        super().__setattr__(__name, __value)

    def get_properties(self) -> dict[str, Any]:
        propdict = super().get_properties()
        propdict.update({
            'tile': self.tile.identifier if self.tile is not None else None,
            'energy': self.energy,
            'health': self.health,
            'protect': self.protect
        })
        return propdict


class GroundPlant(BaseLiving):
    def __init__(self,
                 idenstr: str | None = None,
                 tile: BaseTile | None = None) -> None:
        super().__init__(idenstr, tile)
        self.health = 1

    def standby(self):
        self.energy += 2
        self.health += 1

    def reproduce(self, target_tile: Ground):
        if self.tile is None:
            raise ValueError('Self-tile not found')
        if (
            target_tile in self.tile.connections
            and target_tile.is_support(self.__class__)
        ):
            self.energy = 0
            target_tile.add_substances(self.__class__())
        else:
            raise ValueError('Can\'t reproduce on selected tile')


class WaterPlant(BaseLiving):
    def __init__(self,
                 idenstr: str | None = None,
                 tile: BaseTile | None = None) -> None:
        super().__init__(idenstr, tile)
        self.health = 1

    def standby(self):
        self.energy += 1
        self.health += 1

    def _get_support_tiles(self) -> list[BaseTile]:
        if self.tile is not None:
            return [
                con
                for con in self.tile.connections
                if (
                    isinstance(con, BaseTile)
                    and con.is_support(self.__class__)
                )
            ]
        else:
            raise ValueError('Self-tile not found')

    def float(self):
        # randomly move to support adjacent tile
        if self.tile and (support_tiles := self._get_support_tiles()):
            target = choice(support_tiles)
            self.tile.remove_substances(self)
            target.add_substances(self)
            self.health += 1
        else:
            raise ValueError('No connected support tile')

    def reproduce(self):
        # randomly reproduce to support adjacent tile
        if self.tile and (support_tiles := self._get_support_tiles()):
            target = choice(support_tiles)
            target.add_substances(self.__class__())
            self.energy = 0
        else:
            raise ValueError('No connected support tile')
