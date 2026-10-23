import math
import unittest

from unit_convert_py import convert, UnitError, KnownScales


def approx(a, b, tol=1e-9):
    return abs(a - b) < tol


class TestDistance(unittest.TestCase):
    def test_metres_to_feet(self):
        self.assertTrue(approx(convert(1.0, "m", "ft"), 3.2808398950131))

    def test_roundtrip_kilometres_miles(self):
        self.assertTrue(approx(convert(convert(10.0, "km", "mi"), "mi", "km"), 10.0))

    def test_centimetres_to_inches(self):
        self.assertTrue(approx(convert(2.54, "cm", "in"), 1.0))

    def test_alias_word_form(self):
        self.assertTrue(approx(convert(1000.0, "metres", "kilometre"), 1.0))


class TestWeight(unittest.TestCase):
    def test_kg_to_lb(self):
        self.assertTrue(approx(convert(1.0, "kg", "lb"), 2.2046226218487757))

    def test_oz_to_grams(self):
        self.assertTrue(approx(convert(1.0, "oz", "g"), 28.349523125))

    def test_tonne_to_milligrams(self):
        self.assertTrue(approx(convert(1.0, "t", "mg"), 1_000_000_000.0))


class TestTemperature(unittest.TestCase):
    def test_celsius_to_fahrenheit(self):
        self.assertTrue(approx(convert(0.0, "celsius", "fahrenheit"), 32.0))
        self.assertTrue(approx(convert(100.0, "C", "F"), 212.0))

    def test_fahrenheit_to_kelvin(self):
        self.assertTrue(approx(convert(32.0, "f", "k"), 273.15))

    def test_kelvin_to_celsius(self):
        self.assertTrue(approx(convert(300.0, "K", "C"), 26.85))

    def test_same_unit_returns_float(self):
        result = convert(42, "C", "C")
        self.assertIsInstance(result, float)
        self.assertTrue(approx(result, 42.0))

    def test_negative_celsius_to_fahrenheit(self):
        self.assertTrue(approx(convert(-40.0, "celsius", "fahrenheit"), -40.0))


class TestErrors(unittest.TestCase):
    def test_unknown_unit(self):
        with self.assertRaises(UnitError):
            convert(1.0, "lightyear", "m")

    def test_cross_domain_rejected(self):
        with self.assertRaises(UnitError):
            convert(1.0, "kg", "m")

    def test_none_value_rejected(self):
        with self.assertRaises(UnitError):
            convert(None, "m", "ft")

    def test_unit_error_is_value_error(self):
        self.assertTrue(issubclass(UnitError, ValueError))


class TestKnownScales(unittest.TestCase):
    def test_distance_contains_metre(self):
        self.assertIn("m", KnownScales.distance)

    def test_weight_contains_gram(self):
        self.assertIn("g", KnownScales.weight)

    def test_temperature_contains_kelvin(self):
        self.assertIn("K", KnownScales.temperature)


if __name__ == "__main__":
    unittest.main()
