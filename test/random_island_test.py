

import unittest

from playground.random_island import RandomIsland, IsleGround, IsleWater
from playground.random_island import Turnip, Potato, WaterLily


class ElementsTests(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)

    def test_00_RandomIsland(self):
        island = RandomIsland()
        island.generate_island(4, 4, 1, 6)
        ground_tiles = tuple(
            tile
            for tile in island.tiles.values()
            if isinstance(tile, IsleGround)
        )
        water_tiles = tuple(
            tile
            for tile in island.tiles.values()
            if isinstance(tile, IsleWater)
        )
        self.assertEqual(len(ground_tiles), 6)
        self.assertEqual(len(water_tiles), 10)
        island.spawn(None, None, Turnip)
        island.spawn(None, None, Turnip)
        island.spawn(None, None, Potato)
        island.spawn(None, None, WaterLily)
        island.spawn(None, None, WaterLily)
        island.spawn(None, None, WaterLily)
        turnip_num = tuple(
            tile
            for tile in ground_tiles
            if tile.substances and isinstance(tile.substances[0], Turnip)
        )
        potato_num = tuple(
            tile
            for tile in ground_tiles
            if tile.substances and isinstance(tile.substances[0], Potato)
        )
        waterlily_num = tuple(
            tile
            for tile in water_tiles
            if tile.substances and isinstance(tile.substances[0], WaterLily)
        )
        self.assertEqual(len(turnip_num), 2)
        self.assertEqual(len(potato_num), 1)
        self.assertEqual(len(waterlily_num), 3)
        self.assertEqual(island.visualize().count('v'), 2)
        self.assertEqual(island.visualize().count('o'), 1)
        self.assertEqual(island.visualize().count('l'), 3)
        self.assertEqual(island.visualize().count(':'), 3)
        self.assertEqual(island.visualize().count('.'), 7)
        island.clear_all()
        self.assertEqual(island.tiles, {})


if __name__ == '__main__':
    print(f'''\n{'[Start Tests]----------':->90}''')
    unittest.main(verbosity=2)
