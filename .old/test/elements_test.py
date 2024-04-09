

import unittest

from playground.elements import Entity, EmptySpace, BaseTile, Ground, Water
from playground.elements import BaseLiving, GroundPlant, WaterPlant


class ElementsTests(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)

    def test_00_Entity(self):
        entity = Entity()
        self.assertIsInstance(entity.identifier, str)
        propdict = entity.get_properties()
        self.assertIsInstance(propdict, dict)
        self.assertIn('classname', propdict)
        self.assertEqual(propdict['classname'], Entity.__name__)
        self.assertIn('identifier', propdict)
        self.assertEqual(propdict['identifier'], entity.identifier)

    def test_01_EmptySpace(self):
        # add/remove connections test
        empty_space_1 = EmptySpace()
        self.assertEqual(empty_space_1.connections, [])
        self.assertEqual(empty_space_1.substances, [])
        empty_space_2 = EmptySpace()
        empty_space_1.add_connections(empty_space_2)
        self.assertEqual(empty_space_1.connections, [empty_space_2])
        empty_space_1.remove_connections(empty_space_2)
        self.assertEqual(empty_space_1.connections, [])
        # add/remove substances test
        live = BaseLiving()
        empty_space_1.add_substances(live)
        self.assertEqual(empty_space_1.substances, [live])
        empty_space_1.remove_substances(live)
        self.assertEqual(empty_space_1.substances, [])
        self.assertEqual(empty_space_1.is_support(BaseLiving), True)
        # get_properties test
        empty_space_1.add_connections(empty_space_2)
        empty_space_1.add_substances(live)
        propdict = empty_space_1.get_properties()
        self.assertIn('connections', propdict)
        self.assertIn(empty_space_2.identifier, propdict['connections'])
        self.assertIn('substances', propdict)
        self.assertIn(live.get_properties(), propdict['substances'])

    def test_02_BaseTile(self):
        # twoway add/remove connections test
        base_tile = BaseTile()
        adjacent_tile = BaseTile()
        base_tile.add_connections(adjacent_tile)
        self.assertEqual(base_tile.connections, [adjacent_tile])
        self.assertEqual(adjacent_tile.connections, [base_tile])
        adjacent_tile.remove_connections(base_tile)
        self.assertEqual(base_tile.connections, [])
        self.assertEqual(adjacent_tile.connections, [])
        base_tile = BaseTile()
        adjacent_tile = BaseTile()
        base_tile.add_connections(adjacent_tile, twoway=False)
        self.assertEqual(base_tile.connections, [adjacent_tile])
        self.assertEqual(adjacent_tile.connections, [])
        base_tile.remove_connections(adjacent_tile)
        self.assertEqual(base_tile.connections, [])
        # twoway add/remove substances test
        base_living = BaseLiving()
        base_tile.add_substances(base_living)
        self.assertEqual(base_tile.substances, [base_living])
        self.assertEqual(base_living.tile, base_tile)
        base_tile.remove_substances(base_living)
        self.assertEqual(base_tile.substances, [])
        self.assertEqual(base_living.tile, None)
        # is_support test
        ground_plant = GroundPlant()
        water_plant = WaterPlant()
        self.assertEqual(base_tile.is_support(GroundPlant), True)
        self.assertEqual(base_tile.is_support(WaterPlant), True)
        base_tile.add_substances(ground_plant)
        self.assertEqual(base_tile.is_support(GroundPlant), False)
        self.assertEqual(base_tile.is_support(WaterPlant), True)
        base_tile.add_substances(water_plant)
        self.assertEqual(base_tile.is_support(GroundPlant), False)
        self.assertEqual(base_tile.is_support(WaterPlant), False)

    def test_03_Ground(self):
        ground = Ground()
        self.assertEqual(ground.is_support(BaseLiving), False)
        self.assertEqual(ground.is_support(GroundPlant), True)
        self.assertEqual(ground.is_support(WaterPlant), False)

    def test_04_Water(self):
        water = Water()
        self.assertEqual(water.is_support(BaseLiving), False)
        self.assertEqual(water.is_support(GroundPlant), False)
        self.assertEqual(water.is_support(WaterPlant), True)

    def test_05_BaseLiving(self):
        base_living = BaseLiving()
        self.assertEqual(base_living.energy, 0)
        self.assertEqual(base_living.health, 0)
        self.assertEqual(base_living.protect, 0)
        self.assertIsInstance(base_living.tile, type(None))
        base_tile = BaseTile()
        base_living = BaseLiving(tile=base_tile)
        self.assertEqual(base_living.tile, base_tile)
        for value in range(-1, 11):
            base_living.energy = value
            base_living.health = value
            base_living.protect = value
            self.assertEqual(base_living.energy, min(max(value, 0), 9))
            self.assertEqual(base_living.health, min(max(value, 0), 9))
            self.assertEqual(base_living.protect, min(max(value, 0), 9))
        propdict = base_living.get_properties()
        self.assertIn('tile', propdict)
        self.assertEqual(propdict['tile'], base_tile.identifier)
        self.assertIn('energy', propdict)
        self.assertEqual(propdict['energy'], 9)
        self.assertIn('health', propdict)
        self.assertEqual(propdict['health'], 9)
        self.assertIn('protect', propdict)
        self.assertEqual(propdict['protect'], 9)

    def test_06_GroundPlant(self):
        current_tile = Ground()
        adjacent_tile = Ground()
        adjacent_water = Water()
        current_tile.add_connections(adjacent_tile)
        current_tile.add_connections(adjacent_water)
        ground_plant = GroundPlant(tile=current_tile)
        # init test
        self.assertEqual(ground_plant.health, 1)
        # standby test
        for i in range(12):
            self.assertEqual(ground_plant.health, min(1 + i, 9))
            self.assertEqual(ground_plant.energy, min(2 * i, 9))
            ground_plant.standby()
        self.assertEqual(ground_plant.health, 9)
        self.assertEqual(ground_plant.energy, 9)
        # reproduce test
        self.assertIsNotNone(ground_plant.tile)
        self.assertTrue(adjacent_tile in current_tile.connections)
        self.assertTrue(adjacent_tile.is_support(GroundPlant))
        ground_plant.reproduce(adjacent_tile)
        self.assertEqual(ground_plant.energy, 0)
        self.assertIsInstance(adjacent_tile.substances[0], GroundPlant)
        self.assertNotEqual(
            current_tile.substances[0], adjacent_tile.substances[0]
        )

    def test_07_WaterPlant(self):
        current_tile = Water()
        adjacent_tile = Water()
        adjacent_ground = Ground()
        current_tile.add_connections(adjacent_tile)
        current_tile.add_connections(adjacent_ground)
        water_plant = WaterPlant(tile=current_tile)
        # init test
        self.assertEqual(water_plant.health, 1)
        # standby test
        for i in range(12):
            self.assertEqual(water_plant.health, min(1 + i, 9))
            self.assertEqual(water_plant.energy, min(i, 9))
            water_plant.standby()
        self.assertEqual(water_plant.health, 9)
        self.assertEqual(water_plant.energy, 9)
        # float test
        water_plant.float()
        self.assertEqual(current_tile.substances, [])
        self.assertIsInstance(adjacent_tile.substances[0], WaterPlant)
        self.assertEqual(adjacent_ground.substances, [])
        current_tile, adjacent_tile = adjacent_tile, current_tile
        # reproduce test
        self.assertIsNotNone(water_plant.tile)
        self.assertTrue(adjacent_tile in current_tile.connections)
        self.assertTrue(adjacent_tile.is_support(WaterPlant))
        water_plant.reproduce()
        self.assertEqual(water_plant.energy, 0)
        self.assertIsInstance(adjacent_tile.substances[0], WaterPlant)
        self.assertNotEqual(
            current_tile.substances[0], adjacent_tile.substances[0]
        )


if __name__ == '__main__':
    print(f'''\n{'[Start Tests]----------':->90}''')
    unittest.main(verbosity=2)
