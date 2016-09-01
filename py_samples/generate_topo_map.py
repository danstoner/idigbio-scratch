TILE_SIZE = 512
zoom = 15

bbox = {
    "top_left": {
        "lat": 35.02830956921098,
        "lon": -85.49560546875
    },
    "bottom_right": {
        "lat": 34.814367059175304,
        "lon": -85.29716491699219
    }
}

import PIL.Image as Image
import requests
import math
s = requests.Session()

from cStringIO import StringIO as io_ify

def deg2num(lat_deg, lon_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
    return (xtile, ytile)

top_left_tile = deg2num(
    bbox["top_left"]["lat"],
    bbox["top_left"]["lon"],
    zoom
)

bottom_right_tile = deg2num(
    bbox["bottom_right"]["lat"],
    bbox["bottom_right"]["lon"],
    zoom
)

x_tiles = range(top_left_tile[0], bottom_right_tile[0]+1)
y_tiles = range(top_left_tile[1], bottom_right_tile[1]+1)

im = Image.new("RGB", (len(x_tiles) * TILE_SIZE, len(y_tiles) * TILE_SIZE))
x_tile_count = 0
for x in x_tiles:
    y_tile_count = 0
    for y in y_tiles:
        r = s.get(
            "https://api.mapbox.com/styles/v1/mapbox/outdoors-v9/tiles/{z}/{x}/{y}?access_token=pk.eyJ1IjoidGF0aWFuYSIsImEiOiJjaWs1bzRiZGQwMDdjcHRrc285bTdwcWU5In0.0EWPVHyjaE9jTzNvOiIO-w".format(
                z=zoom, x=x, y=y))
        r.raise_for_status()
        bim = Image.open(io_ify(r.content))
        im.paste(bim, (x_tile_count * TILE_SIZE, y_tile_count * TILE_SIZE))
        y_tile_count += 1
    x_tile_count += 1
im.save("{0}.png".format("map"), "PNG")
