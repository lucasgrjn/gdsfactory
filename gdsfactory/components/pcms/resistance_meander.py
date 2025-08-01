from __future__ import annotations

import numpy as np

import gdsfactory as gf
from gdsfactory.component import Component
from gdsfactory.typings import LayerSpec, Size


@gf.cell_with_module_name
def resistance_meander(
    name: str = "net",
    pad_size: Size = (50.0, 50.0),
    num_squares: int = 1000,
    width: float = 1.0,
    res_layer: LayerSpec = "MTOP",
    pad_layer: LayerSpec = "MTOP",
) -> Component:
    """Return meander to test resistance.

    based on phidl.geometry

    Args:
        name: Name of the component.
        pad_size: Size of the two matched impedance pads (microns).
        num_squares: Number of squares comprising the resonator wire.
        width: The width of the squares (microns).
        res_layer: resistance layer.
        pad_layer: pad layer.
    """
    x = pad_size[0]
    z = pad_size[1]

    # Checking validity of input
    if x <= 0 or z <= 0:
        raise ValueError("Pad must have positive, real dimensions")
    elif width > z:
        raise ValueError("Width of cell cannot be greater than height of pad")
    elif num_squares <= 0:
        raise ValueError("Number of squares must be a positive real number")
    elif width <= 0:
        raise ValueError("Width of cell must be a positive real number")

    # Performing preliminary calculations
    num_rows = int(np.floor(z / (2 * width)))
    if num_rows % 2 == 0:
        num_rows -= 1
    num_columns = num_rows - 1
    squares_in_row = (num_squares - num_columns - 2) / num_rows

    # Compensating for weird edge cases
    if squares_in_row < 1:
        num_rows = round(num_rows / 2) - 2
        squares_in_row = 1
    if width * 2 > z:
        num_rows = 1
        squares_in_row = num_squares - 2

    length_row = squares_in_row * width

    # Creating row/column corner combination structure
    T = Component()
    Row = gf.c.rectangle(size=(length_row, width), layer=res_layer)
    Col = gf.c.rectangle(size=(width, width), layer=res_layer)

    T.add_ref(Row)
    col = T.add_ref(Col)
    col.move((length_row - width, -width))

    # Creating entire straight net
    N = Component(name=name)
    n = 1
    for i in range(num_rows):
        d = N.add_ref(T) if i != num_rows - 1 else N.add_ref(Row)
        if n % 2 == 0:
            d.dmirror_x(d.x)
        d.movey(-(n - 1) * T.ysize)
        n += 1
    ref = N.add_ref(Col)
    ref.movex(-width)

    end = N.add_ref(Col)
    end.movey(-(n - 2) * T.ysize)
    end.movex(length_row)

    # Creating pads
    P = Component()
    pad = gf.c.rectangle(size=(x, z), layer=pad_layer)
    pad1 = P.add_ref(pad)
    pad1.movex(-x - width)
    pad2 = P.add_ref(pad)
    pad2.movex(length_row + width)
    net = P.add_ref(N)
    net.ymin = pad1.ymin
    P.flatten()
    return P


if __name__ == "__main__":
    c = resistance_meander(num_squares=500)
    c.show()
