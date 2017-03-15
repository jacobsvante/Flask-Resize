import pytest

from flask_resize import exc
from flask_resize.utils import parse_dimensions, parse_rgb


def test_parse_dimensions():
    def image_dimensions_generator():
        yield 1
        yield 2

    assert parse_dimensions('100x'), (100, None)
    assert parse_dimensions('3x4'), (3, 4)
    assert parse_dimensions('x2000'), (None, 2000)
    assert parse_dimensions((666, None)), (666, None)
    assert parse_dimensions([None, 777]), (None, 777)
    assert parse_dimensions([123, 456]), (123, 456)
    assert parse_dimensions(image_dimensions_generator()), (1, 2)

    invalid_values = ['100px200px', '1x2x3', [1, 2, 3]]
    missing_values = ['', [0, 0], [None, None], [1]]

    for invalid in invalid_values + missing_values:
        with pytest.raises(exc.InvalidDimensionsError):
            parse_dimensions(invalid)

    for missing_value in missing_values:
        with pytest.raises(exc.MissingDimensionsError):
            parse_dimensions(invalid)


def test_parse_rgb():
    assert parse_rgb((0, 0, 0)) == '#000000'
    assert parse_rgb((20, 50, 200)) == '#1432c8'
    assert parse_rgb('000') == '#000000'
    assert parse_rgb('f0c') == '#ff00cc'
    assert parse_rgb('1432c8') == '#1432c8'
    assert parse_rgb('#feccde') == '#feccde'
    assert parse_rgb('#fcd') == '#ffccdd'

    assert parse_rgb((0, 0, 0), include_number_sign=False) == '000000'
    assert parse_rgb('#1432c8', include_number_sign=False) == '1432c8'
    assert parse_rgb('feccde', include_number_sign=False) == 'feccde'
    assert parse_rgb('fcd', include_number_sign=False) == 'ffccdd'
