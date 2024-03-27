

from __future__ import annotations
from typing import Any
from abc import ABC, abstractmethod

import uuid


class Entity(ABC):
    def __init__(self, idenstr: str | None = None) -> None:
        if idenstr is None:
            idenstr = uuid.uuid1().hex
        self._identifier = idenstr

    @property
    def identifier(self) -> str:
        return self._identifier

    def get_properties(self) -> dict[str, Any]:
        return {
            'classname': self.__class__.__name__,
            'identifier': self._identifier,
        }


class TileInterface(Entity):
    @property
    @abstractmethod
    def connections(self) -> list[TileInterface]:
        pass

    @property
    @abstractmethod
    def substances(self) -> list[LivingInterface]:
        pass

    @abstractmethod
    def add_connections(self, other: TileInterface) -> None:
        pass

    @abstractmethod
    def remove_connections(self, other: TileInterface) -> None:
        pass

    @abstractmethod
    def add_substances(self, living: LivingInterface) -> None:
        pass

    @abstractmethod
    def remove_substances(self, living: LivingInterface) -> None:
        pass

    @abstractmethod
    def is_support(self, living: LivingInterface) -> bool:
        pass

    def get_properties(self):
        propdict = super().get_properties()
        propdict.update({
            'connections': [con.identifier for con in self.connections],
            'substances': [sub.get_properties() for sub in self.substances]
        })
        return propdict


class LivingInterface(Entity):
    @property
    @abstractmethod
    def energy(self) -> int:
        pass

    @property
    @abstractmethod
    def health(self) -> int:
        pass

    @property
    @abstractmethod
    def protect(self) -> int:
        pass

    @property
    @abstractmethod
    def tile(self) -> TileInterface | None:
        pass

    @tile.setter
    @abstractmethod
    def tile(self, tile: TileInterface | None) -> TileInterface | None:
        pass

    def get_properties(self) -> dict[str, Any]:
        propdict = super().get_properties()
        propdict.update({
            'tile': self.tile.identifier if self.tile is not None else None,
            'energy': self.energy,
            'health': self.health,
            'protect': self.protect
        })
        return propdict
