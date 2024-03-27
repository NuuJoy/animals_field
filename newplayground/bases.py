

from __future__ import annotations
from typing import Any

from newplayground.interfaces import TileInterface, LivingInterface


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

    def add_connections(self, other: TileInterface):
        if other not in self.connections:
            self.connections.append(other)
            self.connections.sort(key=lambda con: con.identifier)
            if self not in other.connections:
                other.add_connections(self)

    def remove_connections(self, other: TileInterface):
        if other in self.connections:
            self.connections.remove(other)
            if self in other.connections:
                other.remove_connections(self)

    def add_substances(self, living: LivingInterface):
        if living not in self.substances and self.is_support(living):
            self.substances.append(living)
            self.substances.sort(key=lambda sub: sub.identifier)
            if living.tile is not self:
                living.tile = self

    def remove_substances(self, living: LivingInterface):
        if living in self.substances:
            self.substances.remove(living)
        living.tile = None

    def is_support(self, living: LivingInterface) -> bool:
        # not allow duplicate type within substance
        return isinstance(living, self._support_living_classes) and not any([
            isinstance(subs, type(living))
            for subs in self.substances
        ])

    def get_properties(self) -> dict[str, Any]:
        propdict = super().get_properties()
        propdict.update({
            'connections': [con.identifier for con in self.connections],
            'substances': [sub.get_properties() for sub in self.substances]
        })
        return propdict


class BaseLiving(LivingInterface):

    def __init__(self,
                 idenstr: str | None = None,
                 tile: BaseTile | None = None) -> None:
        super().__init__(idenstr)
        self._tile = tile
        if self.tile is not None:
            self.tile.add_substances(self)

    @property
    def tile(self) -> TileInterface | None:
        return self._tile

    @tile.setter
    def tile(self, tile: TileInterface | None) -> TileInterface | None:
        if self.tile is not tile:
            self._tile = tile
        return self._tile
