'use strict'


var images_toload = 2
var loaded_images = 0

const image_tiles = new Image()
const image_baselives = new Image()

image_tiles.onload = try_start_run
image_baselives.onload = try_start_run

image_tiles.src = 'static/img/image_tiles.gif'
image_baselives.src = 'static/img/image_baselives.gif'

function try_start_run() {
    loaded_images += 1
    if (loaded_images >= images_toload) {
        // main()
        setInterval(main, 500)
    }
}

const fragpx = 8
const zoomin = 2

const field_slice = {
    '111': 1,
    '011': 2,
    '101': 4,
    '110': 5,
    '000': 3,
    '100': 3,
    '010': 5,
    '001': 4
}

function get_fragment_cols(ul, u, ur, l, c, r, dl, d, dr) {
    if (c != 1) {
        return [0, 0, 0, 0]
    } else {
        return [
            field_slice[ul.toString() + u.toString() + l.toString()],
            field_slice[ur.toString() + r.toString() + u.toString()],
            field_slice[dr.toString() + d.toString() + r.toString()],
            field_slice[dl.toString() + l.toString() + d.toString()]
        ]
    }
}

function draw_tile(ctx, ulcol, urcol, drcol, dlcol, posx, posy) {
    let drawsize = zoomin * fragpx
    ctx.drawImage(
        image_tiles,
        ulcol*fragpx, 0, fragpx, fragpx,
        zoomin*(posx*2*fragpx),
        zoomin*(posy*2*fragpx),
        drawsize, drawsize
    )
    ctx.drawImage(
        image_tiles,
        urcol*fragpx, 1*fragpx, fragpx, fragpx,
        zoomin*(fragpx*(2*posx + 1)),
        zoomin*(fragpx*(2*posy)),
        drawsize, drawsize
    )
    ctx.drawImage(
        image_tiles,
        drcol*fragpx, 2*fragpx, fragpx, fragpx,
        zoomin*(fragpx*(2*posx + 1)),
        zoomin*(fragpx*(2*posy + 1)),
        drawsize, drawsize
    )
    ctx.drawImage(
        image_tiles,
        dlcol*fragpx, 3*fragpx, fragpx, fragpx,
        zoomin*(fragpx*(2*posx )),
        zoomin*(fragpx*(2*posy + 1)),
        drawsize, drawsize
    )
    ctx.lineWidth = 0.2 * zoomin
    ctx.strokeRect(
        zoomin*(posx*2*fragpx),
        zoomin*(posy*2*fragpx),
        2*drawsize,
        2*drawsize
    );
}

function draw_live(ctx, text, posx, posy) {
    let keymap = {'v': 0, 'w': 16, 'V': 32, 'W': 48}
    if (text in keymap) {
        ctx.drawImage(
            image_baselives,
            keymap[text], 0, 2*fragpx, 2*fragpx,
            zoomin*(posx*2*fragpx), zoomin*(posy*2*fragpx),
            zoomin*2*fragpx, zoomin*2*fragpx
        )
    }
}

function get_tile(fieldmap, posx, posy) {
    let value
    try {
        value = fieldmap[posx][posy]
        if (value == undefined) {
            return 0
        } else if (typeof value == 'string') {
            return 1
        } else {
            return value
        }
    } catch (error) {
        return 0
    }
}

// function generate_randomfield(sizex, sizey) {
//     let fieldmap = []
//     for (let posx = 0; posx < sizex; posx++) {
//         let cols = []
//         for (let posy = 0; posy < sizey; posy++) {
//             let randval = Math.random()
//             if (randval < 0.25) {
//                 cols.push(0)
//             } else if (randval < 0.80){
//                 cols.push(1)
//             } else if (randval < 0.85){
//                 cols.push('v')
//             } else if (randval < 0.90){
//                 cols.push('w')
//             } else if (randval < 0.95){
//                 cols.push('V')
//             } else {
//                 cols.push('W')
//             }
//         }
//         fieldmap.push(cols)
//     }
//     return fieldmap
// }

function query_json(suburl) {
    let xmlHttp = new XMLHttpRequest()
    xmlHttp.open('GET', window.location.origin + suburl, false)
    xmlHttp.send(null)
    return JSON.parse(xmlHttp.response)
}

function main() {
    // let fieldmap = generate_randomfield(8, 8)
    let fieldmap = query_json('/jsonmap')['fieldmap']

    const canvas = document.getElementById('mapcanvas')
    canvas.width = zoomin * 2* fragpx * fieldmap.length
    canvas.height = zoomin * 2 * fragpx * fieldmap[0].length

    const ctx = canvas.getContext('2d')
    ctx.imageSmoothingEnabled = false

    let ul, u, ur, l, c, r, dl, d, dr
    for (let posx = 0; posx < fieldmap.length; posx++) {
        for (let posy = 0; posy < fieldmap[0].length; posy++) {

            ul = get_tile(fieldmap, posx-1, posy-1)
            u = get_tile(fieldmap, posx, posy-1)
            ur = get_tile(fieldmap, posx+1, posy-1)
            l = get_tile(fieldmap, posx-1, posy)
            c = get_tile(fieldmap, posx, posy)
            r = get_tile(fieldmap, posx+1, posy)
            dl = get_tile(fieldmap, posx-1, posy+1)
            d = get_tile(fieldmap, posx, posy+1)
            dr = get_tile(fieldmap, posx+1, posy+1)

            let [ulcol, urcol, drcol, dlcol] = get_fragment_cols(ul, u, ur, l, c, r, dl, d, dr)
            draw_tile(ctx, ulcol, urcol, drcol, dlcol, posx, posy)
            draw_live(ctx, fieldmap[posx][posy], posx, posy)
        }
    }
}
