'use strict'

const playerImage = new Image()
// playerImage.onload = setInterval(main, 1000)
playerImage.src = 'image_tiles.gif'

const fragpx = 8
const zoomin = 1

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
        playerImage,
        ulcol*fragpx, 0, fragpx, fragpx,
        zoomin*(posx*2*fragpx),
        zoomin*(posy*2*fragpx),
        drawsize, drawsize
    )
    ctx.drawImage(
        playerImage,
        urcol*fragpx, 1*fragpx, fragpx, fragpx,
        zoomin*(fragpx*(2*posx + 1)),
        zoomin*(fragpx*(2*posy)),
        drawsize, drawsize
    )
    ctx.drawImage(
        playerImage,
        drcol*fragpx, 2*fragpx, fragpx, fragpx,
        zoomin*(fragpx*(2*posx + 1)),
        zoomin*(fragpx*(2*posy + 1)),
        drawsize, drawsize
    )
    ctx.drawImage(
        playerImage,
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

function get_tile(fieldmap, posx, posy) {
    let value
    try {
        value = fieldmap[posx][posy]
        if (value == undefined) {
            return 0
        } else {
            return value
        }
    } catch (error) {
        return 0
    }
}

function generate_randomfield(sizex, sizey, thres) {
    let fieldmap = []
    for (let posx = 0; posx < sizex; posx++) {
        let cols = []
        for (let posy = 0; posy < sizey; posy++) {
            if (Math.random() > thres) {
                cols.push(1)
            } else {
                cols.push(0)
            }
        }
        fieldmap.push(cols)
    }
    return fieldmap
}

function main() {

    let fieldmap = generate_randomfield(8, 8, 0.25)

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
        }
    }
}
