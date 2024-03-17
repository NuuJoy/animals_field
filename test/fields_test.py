

import unittest

from playground.elements import BaseTile, BaseLiving
from playground.fields import Field2D


class ElementsTests(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)

    def test_00_Field2D(self):
        field = Field2D()
        self.assertEqual(field.handler, {})
        field.add_tile(0, 1, BaseTile())
        field.add_tile(-1, 0, tile1 := BaseTile())
        self.assertRaises(KeyError, lambda: field.add_tile(-1, 0, BaseTile()))
        field.add_tile(0, 0, tile2 := BaseTile())
        field.add_tile(0, -1, tile3 := BaseTile())
        field.add_tile(1, 1, tile4 := BaseTile())
        field.remove_tile(0, 1)
        self.assertRaises(KeyError, lambda: field.remove_tile(9, 9))
        # test tile connections
        self.assertIn(tile1, tile2.connections)
        self.assertNotIn(tile1, tile3.connections)
        self.assertNotIn(tile1, tile4.connections)
        self.assertIn(tile2, tile1.connections)
        self.assertIn(tile2, tile3.connections)
        self.assertNotIn(tile2, tile4.connections)
        self.assertNotIn(tile3, tile1.connections)
        self.assertIn(tile3, tile2.connections)
        self.assertNotIn(tile3, tile4.connections)
        self.assertNotIn(tile4, tile1.connections)
        self.assertNotIn(tile4, tile2.connections)
        self.assertNotIn(tile4, tile3.connections)
        # test substance adding
        tile1.add_substances(BaseLiving())
        tile4.add_substances(BaseLiving())
        self.assertEqual(len(field.get_substances()), 2)
        self.assertIn(tile1.substances[0], field.get_substances())
        self.assertIn(tile4.substances[0], field.get_substances())
        # test output
        self.assertEqual(len(field.get_map_properties()), 4)
        self.assertIn('-1,0', field.get_map_properties())
        self.assertIn('0,0', field.get_map_properties())
        self.assertIn('0,-1', field.get_map_properties())
        self.assertIn('1,1', field.get_map_properties())
        self.assertIsInstance(field.serialize(), str)
        self.assertEqual(field.visualize(), '  ·\n·· \n · ')

    def test_01_FieldClone(self):
        prototype = Field2D()
        prototype.add_tile(-1, 0, tile1 := BaseTile())
        prototype.add_tile(0, 0, tile2 := BaseTile())
        prototype.add_tile(0, -1, BaseTile())
        prototype.add_tile(1, 1, BaseTile())
        tile1.add_substances(BaseLiving())
        tile2.add_substances(BaseLiving())
        blueprint = prototype.serialize()
        clone = Field2D(blueprint=blueprint)
        self.assertEqual(prototype, clone)
        prototype.remove_tile(0, 0)
        self.assertNotEqual(prototype, clone)


if __name__ == '__main__':
    print(f'''\n{'[Start Tests]----------':->90}''')
    unittest.main(verbosity=2)
