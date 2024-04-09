

from __future__ import annotations
from random import choice, sample, randint

from old_playground.fields import Field2D
from old_playground.elements import Ground, Water
from old_playground.elements import BaseLiving, GroundPlant, WaterPlant


class IsleGround(Ground):
    symbol: str = ':'

    def is_support(self, cls: type[BaseLiving]):
        if issubclass(cls, IsleGroundPlant):
            return not any([
                isinstance(subs, IsleGroundPlant)
                for subs in self.substances
            ])
        elif issubclass(cls, IsleGroundAnimal):
            return not any([
                isinstance(subs, IsleGroundAnimal)
                for subs in self.substances
            ])
        else:
            return False


class IsleWater(Water):
    symbol: str = '.'


IsleTileCls = type[IsleGround | IsleWater]


class IsleGroundPlant(GroundPlant):
    @property
    def symbol(self) -> str:
        return '?'

    def reproduce(self, target_tile: Ground):
        if self.energy < 9:
            raise ValueError('Not enough energy')
        return super().reproduce(target_tile)


class IsleWaterPlant(WaterPlant):
    @property
    def symbol(self) -> str:
        return '?'

    def reproduce(self):
        if self.energy < 9:
            raise ValueError('Not enough energy')
        return super().reproduce()


IslePlantCls = type[IsleGroundPlant | IsleWaterPlant]


class IsleGroundAnimal(BaseLiving):
    pass


IsleAnimalCls = type[IsleGroundAnimal]


class Turnip(IsleGroundPlant):
    def standby(self):
        self.energy += randint(1, 2)
        self.health += randint(0, 1)

    @property
    def symbol(self) -> str:
        if self.health <= 3:
            return 'v'
        elif self. health <= 6:
            return 't'
        else:
            return 'T'


class Potato(IsleGroundPlant):
    def standby(self):
        self.energy += randint(0, self.health)
        self.health += randint(0, 2)

    @property
    def symbol(self) -> str:
        if self.health <= 3:
            return 'o'
        elif self. health <= 6:
            return 'p'
        else:
            return 'P'


class WaterLily(IsleWaterPlant):
    @property
    def symbol(self) -> str:
        if self. health <= 6:
            return 'l'
        else:
            return 'L'


class RandomIsland(Field2D):
    def __init__(self, blueprint: str | None = None) -> None:
        super().__init__(blueprint)

    def clear_all(self):
        self._handler = {}

    def generate_island(self,
                        width: int = 30,
                        height: int = 30,
                        init_island_num: int = 3,
                        ground_tile_num: int = 200):

        available_keys = tuple(
            (posx, posy)
            for posx in range(int(-width/2), int(width/2))
            for posy in range(int(-height/2), int(height/2))
            if (posx, posy) not in self.tiles
        )

        for posx, posy in sample(available_keys, init_island_num):
            self.add_tile(posx, posy, IsleGround())

        while len(self.tiles) < ground_tile_num:
            d1, d2 = choice(tuple(self.tiles.keys()))
            adjacent_tiles = [
                key
                for key in [
                    (d1 - 1, d2),
                    (d1 + 1, d2),
                    (d1, d2 - 1),
                    (d1, d2 + 1)
                ]
                if (key not in self.tiles) and (key in available_keys)
            ]
            if adjacent_tiles:
                posx, posy = choice(adjacent_tiles)
                self.add_tile(posx, posy, IsleGround())

        for posx, posy in available_keys:
            if (posx, posy) not in self.tiles:
                self.add_tile(posx, posy, IsleWater())

    def spawn(self, posx: int | None, posy: int | None, cls: IslePlantCls):
        available_tiles = tuple(
            (d1, d2)
            for (d1, d2), tile in self.tiles.items()
            if tile.is_support(cls) and (
                (d1 == posx) or (posx is None)) and (
                (d2 == posy) or (posy is None))
        )
        if available_tiles:
            posx, posy = choice(available_tiles)
            self.get_tile(posx, posy).add_substances(cls())
        else:
            raise ValueError('Not found available tile')

    def visualize(self):
        # get boundary
        if not self.tiles:
            return ''

        x_values, y_values = [values for values in zip(*self.tiles)]
        x_shift = min(x_values)
        y_shift = min(y_values)
        x_max = max(x_values) - x_shift
        y_max = max(y_values) - y_shift
        # create 2-D array of empty field
        listmap = [
            [' ' for _ in range(x_max + 1)]
            for _ in range(y_max + 1)
        ]

        # mark tile type
        for (d1, d2), tile in self.tiles.items():
            if isinstance(tile, (IsleGround, IsleWater)):
                if not tile.substances:
                    listmap[d2 - y_shift][d1 - x_shift] = tile.symbol
                else:
                    subs = tile.substances[0]
                    if isinstance(subs, (IsleGroundPlant, IsleWaterPlant)):
                        listmap[d2 - y_shift][d1 - x_shift] = subs.symbol
                    else:
                        listmap[d2 - y_shift][d1 - x_shift] = '?'
            else:
                listmap[d2 - y_shift][d1 - x_shift] = '?'
        return '\n'.join([''.join(row) for row in listmap][::-1])
