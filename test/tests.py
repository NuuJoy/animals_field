

import unittest


from playground.bases import BaseTile, BaseLiving, Base2DSquareField


class BaseTileTests(unittest.TestCase):

    def test_add_remove_connection(self):
        tile1 = BaseTile()
        tile2 = BaseTile()
        tile1.add_connection(tile2)
        self.assertEqual(tile1.connections, [tile2])
        self.assertEqual(tile2.connections, [tile1])
        tile2.remove_connection(tile1)
        self.assertEqual(tile1.connections, [])
        self.assertEqual(tile2.connections, [])

    def test_add_remove_substance(self):
        tile = BaseTile()
        live1 = BaseLiving()
        live2 = BaseLiving()
        self.assertEqual(tile.is_support(live1), True)
        self.assertEqual(tile.is_support(live2), True)
        tile.add_substances(live1)
        self.assertEqual(tile.substances, [live1])
        self.assertEqual(tile.is_support(live1), False)
        self.assertEqual(tile.is_support(live2), False)
        tile.remove_substances(live1)
        self.assertEqual(tile.is_support(live1), True)
        self.assertEqual(tile.is_support(live2), True)

    def test_get_properties(self):
        tile1 = BaseTile()
        tile2 = BaseTile()
        live = BaseLiving()
        tile1.add_connection(tile2)
        tile1.add_substances(live)
        self.assertEqual(
            tile1.get_properties(),
            {
                'classname': tile1.__class__.__name__,
                'identifier': tile1.identifier,
                'connections': [tile2.identifier],
                'substances': [live.get_properties()]
            }
        )


class BaseLivingTests(unittest.TestCase):

    def test_attributes(self):
        live = BaseLiving()
        tile = BaseTile()
        self.assertIsNone(live.tile)
        self.assertEqual(tile.substances, [])
        live.tile = tile
        self.assertEqual(live.tile, tile)
        self.assertEqual(tile.substances, [live])
        live.tile = None
        self.assertIsNone(live.tile)
        self.assertEqual(tile.substances, [])
        tile.add_substances(live)
        self.assertEqual(live.tile, tile)
        self.assertEqual(tile.substances, [live])
        tile.remove_substances(live)
        self.assertIsNone(live.tile)
        self.assertEqual(tile.substances, [])


class Base2DSquareFieldTest(unittest.TestCase):

    def test_tiles_connectivity(self):
        field = Base2DSquareField()
        tile1 = BaseTile()
        tile2 = BaseTile()
        tile3 = BaseTile()
        tile4 = BaseTile()
        tile5 = BaseTile()
        field.add_tile(tile1, (0, 0))
        field.add_tile(tile2, (-1, 0))
        field.add_tile(tile3, (0, -1))
        field.add_tile(tile4, (1, 1))
        field.add_tile(tile5, (2, 1))
        self.assertEqual(tile1.connections, [tile2, tile3, tile4])
        self.assertEqual(tile2.connections, [tile1, tile3])
        self.assertEqual(tile3.connections, [tile1, tile2])
        self.assertEqual(tile4.connections, [tile1, tile5])
        self.assertEqual(tile5.connections, [tile4])

    def test_serialize(self):
        field = Base2DSquareField()
        tile1 = BaseTile()
        tile2 = BaseTile()
        live = BaseLiving()
        field.add_tile(tile1, (0, 0))
        field.add_tile(tile2, (1, 0))
        tile1.add_substances(live)
        self.assertEqual(tile1.connections, [tile2])
        self.assertEqual(tile2.connections, [tile1])
        self.assertEqual(tile1.substances, [live])
        self.assertEqual(
            field.serialize(),
            '{\n'
            '    "0,0": {\n'
            f'        "classname": "{tile1.__class__.__name__}",\n'
            f'        "identifier": "{tile1.identifier}",\n'
            '        "connections": [\n'
            f'            "{tile2.identifier}"\n'
            '        ],\n'
            '        "substances": [\n'
            '            {\n'
            '                "classname": "BaseLiving",\n'
            f'                "identifier": "{live.identifier}",\n'
            f'                "tile": "{tile1.identifier}",\n'
            f'                "energy": {live.energy},\n'
            f'                "health": {live.health}\n'
            '            }\n'
            '        ]\n'
            '    },\n'
            '    "1,0": {\n'
            f'        "classname": "{tile2.__class__.__name__}",\n'
            f'        "identifier": "{tile2.identifier}",\n'
            '        "connections": [\n'
            f'            "{tile1.identifier}"\n'
            '        ],\n'
            '        "substances": []\n'
            '    }\n'
            '}'
        )

    def test_load(self):
        field = Base2DSquareField()
        field.load(
            '{\n'
            '    "0,0": {\n'
            '        "classname": "BaseTile",\n'
            '        "identifier": "usertile1iden",\n'
            '        "connections": [\n'
            '            "usertile2iden"\n'
            '        ],\n'
            '        "substances": [\n'
            '            {\n'
            '                "classname": "BaseLiving",\n'
            '                "identifier": "userlive1iden",\n'
            '                "tile": "usertile1iden",\n'
            '                "energy": 0,\n'
            '                "health": 1\n'
            '            }\n'
            '        ]\n'
            '    },\n'
            '    "1,0": {\n'
            '        "classname": "BaseTile",\n'
            '        "identifier": "usertile2iden",\n'
            '        "connections": [\n'
            '            "usertile1iden"\n'
            '        ],\n'
            '        "substances": []\n'
            '    }\n'
            '}'
        )

        self.assertEqual(
            field.tiles[0].connections[0].identifier,
            'usertile2iden'
        )
        self.assertEqual(
            field.tiles[0].substances[0].identifier,
            'userlive1iden'
        )
        self.assertEqual(
            field.tiles[1].connections[0].identifier,
            'usertile1iden'
        )


if __name__ == '__main__':
    print(f'''\n{'[Start Tests]----------':->90}''')
    unittest.main(verbosity=2)
