from collections import namedtuple


GradientProperties = namedtuple('GradientProperties', ['ln', 'k', 'r', 'n', 'ds', 'de'])


def grading_by_ds_ccratio_count(ds, k, n):
    """
    Calculate grading properties.

    Args:
        ds: Start cell size
        k: Cell-to-cell expansion (or geometric growth ratio)
        n: Number of cells

    Returns:
        grading properties as a namedtuple.
            ln: Total length
            k: Cell-to-cell expansion (or geometric growth ratio)
            r: Total expansion ratio (=bias factor in Ansys Meshing)
            n: Number of cells
            ds: Start cell size
            de: End cell size
    """
    ln = sum(ds * k ** i for i in range(0, n))
    r = k ** (n - 1)
    de = r * ds
    return GradientProperties(ln, k, r, n, ds, de)


def grading_by_length_ds_ccratio(ln, ds, k):
    """
    Calculate grading properties.

    Args:
        ln: Total length
        ds: Start cell size
        k: Cell-to-cell expansion (or geometric growth ratio)

    Returns:
        grading properties as a namedtuple.
            ln: Total length
            k: Cell-to-cell expansion (or geometric growth ratio)
            r: Total expansion ratio (=bias factor in Ansys Meshing)
            n: Number of cells
            ds: Start cell size
            de: End cell size
    """
    n = 0
    tl = 0
    while tl < ln:
        tl += ds * k ** n
        n += 1
    n -= 1
    ln = sum(ds * k ** i for i in range(0, n))
    r = k ** (n - 1)
    de = r * ds
    return GradientProperties(ln, k, r, n, ds, de)


def grading_by_length_de_ccratio(ln, de, k, min_ds=1):
    """
    Calculate grading properties.

    Args:
        ln: Total length
        de: End cell size
        k: Cell-to-cell expansion (or geometric growth ratio)
        min_ds: Minimum size for start cell size.
    Returns:
        grading properties as a namedtuple.
            ln: Total length
            k: Cell-to-cell expansion (or geometric growth ratio)
            r: Total expansion ratio (=bias factor in Ansys Meshing)
            n: Number of cells
            ds: Start cell size
            de: End cell size
    """
    k_rev = 1.0 / k
    n = 0
    tl = 0
    ds = min_ds + 1.0  # initial value to start the calculation
    while tl < ln and ds > min_ds:
        tl += de * k_rev ** n
        r = k ** (n - 1)
        ds = de / r
        n += 1

    n -= 1
    r = k ** (n - 1)
    ds = de / r
    ln = sum(ds * k ** i for i in range(0, n))
    return GradientProperties(ln, k, r, n, ds, de)


def grading_by_length_ds_de(ln, ds, de):
    """
    Calculate grading properties.

    Args:
        ln: Total length
        ds: Start cell size
        de: End cell size

    Returns:
        grading properties as a namedtuple.
            ln: Total length
            k: Cell-to-cell expansion (or geometric growth ratio)
            r: Total expansion ratio (=bias factor in Ansys Meshing)
            n: Number of cells
            ds: Start cell size
            de: End cell size
    """
    r = de / ds
    # try to find the cell count to get to this point
    n = 2
    tl = 0
    while tl < ln:
        k = r ** (1.0 / (n - 1))
        tl = sum(ds * k ** i for i in range(0, n))
        n += 1

    n -= 2
    # re-calculate the last option with closest length
    k = r ** (1.0 / (n - 1))
    ln = sum(ds * k ** i for i in range(0, n))
    r = k ** (n - 1)
    de = r * ds

    return GradientProperties(ln, k, r, n, ds, de)


if __name__ == '__main__':
    # ds = 2
    # k = 1.2
    # ln = 1000
    # res = grading_by_length_ds_ccratio(ln, ds, k)
    # print(res)

    # de = 159
    # k = 1.2
    ds = 0.5
    de = 1
    ln = 8
    res = grading_by_length_ds_de(ln, ds, de)
    print(res)
    # ln = 14.12
    # de = 1
    # res = grading_by_length_de_ccratio(ln, de, 1.0 / 1.2, 0.01)
    # print(res)
