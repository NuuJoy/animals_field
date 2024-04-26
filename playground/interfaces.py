

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
        raise NotImplementedError

    @property
    @abstractmethod
    def substances(self) -> list[LivingInterface]:
        raise NotImplementedError

    @abstractmethod
    def add_connection(self, other: TileInterface) -> None:
        raise NotImplementedError

    @abstractmethod
    def remove_connection(self, other: TileInterface) -> None:
        raise NotImplementedError

    @abstractmethod
    def add_substances(self, living: LivingInterface) -> None:
        raise NotImplementedError

    @abstractmethod
    def remove_substances(self, living: LivingInterface) -> None:
        raise NotImplementedError

    @abstractmethod
    def is_support(self, living: LivingInterface) -> bool:
        raise NotImplementedError

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
    def age(self) -> int:
        raise NotImplementedError

    @age.setter
    @abstractmethod
    def age(self, value: int) -> None:
        raise NotImplementedError

    @property
    @abstractmethod
    def health(self) -> int:
        raise NotImplementedError

    @health.setter
    @abstractmethod
    def health(self, value: int) -> None:
        raise NotImplementedError

    @property
    @abstractmethod
    def energy(self) -> int:
        raise NotImplementedError

    @energy.setter
    @abstractmethod
    def energy(self, value: int) -> None:
        raise NotImplementedError

    @property
    @abstractmethod
    def tile(self) -> TileInterface | None:
        raise NotImplementedError

    @tile.setter
    @abstractmethod
    def tile(self, newtile: TileInterface | None) -> None:
        raise NotImplementedError

    def get_properties(self) -> dict[str, Any]:
        propdict = super().get_properties()
        propdict.update({
            'tile': self.tile.identifier if self.tile is not None else None,
            'age': self.age,
            'health': self.health,
            'energy': self.energy
        })
        return propdict


class FieldInterface(Entity):
    @abstractmethod
    def serialize(self) -> str:
        raise NotImplementedError

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, FieldInterface):
            return self.serialize() == __value.serialize()
        else:
            return False

    @property
    @abstractmethod
    def tiles(self) -> tuple[TileInterface, ...]:
        raise NotImplementedError

    @property
    @abstractmethod
    def tiles_dict(self) -> dict[tuple[int | float, ...], TileInterface]:
        raise NotImplementedError

    @abstractmethod
    def add_tile(self,
                 tile: TileInterface,
                 position: tuple[int | float, ...]) -> None:
        raise NotImplementedError

    def connect_tile(self,
                     tile: TileInterface,
                     others: tuple[TileInterface, ...]) -> None:
        for other in others:
            tile.add_connection(other)
