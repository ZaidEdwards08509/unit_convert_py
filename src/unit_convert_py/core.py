"""Unit conversion across distance, weight, and temperature scales.

Design choice: single dispatch function instead of per-domain objects. The use
site reads as ``convert(value, "m", "ft")`` which keeps the caller's intent
visible without importing three different converter classes. The cost is a
flat if/elif chain in one function, which is acceptable for a library covering
exactly three domains.

Floats are returned for every conversion. The measurement scales here are real
valued (metres-to-feet is not an integer relationship), so a caller comparing
results must use a tolerance. Tests use ``abs(actual - expected) < 1e-9`` rather
than ``==``.
"""


class UnitError(ValueError):
    """Raised when a unit string is not recognised in the requested domain."""


# Distance in metres. A unit appears here iff there is a documented factor to
# metres, so the lookup is total over the listed keys.
_DISTANCE_TO_METRES = {
    "m": 1.0,
    "metre": 1.0,
    "metres": 1.0,
    "meter": 1.0,
    "meters": 1.0,
    "km": 1000.0,
    "kilometre": 1000.0,
    "kilometres": 1000.0,
    "kilometer": 1000.0,
    "kilometers": 1000.0,
    "cm": 0.01,
    "centimetre": 0.01,
    "centimetres": 0.01,
    "centimeter": 0.01,
    "centimeters": 0.01,
    "mm": 0.001,
    "millimetre": 0.001,
    "millimetres": 0.001,
    "millimeter": 0.001,
    "millimeters": 0.001,
    "mi": 1609.344,
    "mile": 1609.344,
    "miles": 1609.344,
    "yd": 0.9144,
    "yard": 0.9144,
    "yards": 0.9144,
    "ft": 0.3048,
    "foot": 0.3048,
    "feet": 0.3048,
    "in": 0.0254,
    "inch": 0.0254,
    "inches": 0.0254,
}

# Weight in grams. Same rationale as distance.
_WEIGHT_TO_GRAMS = {
    "g": 1.0,
    "gram": 1.0,
    "grams": 1.0,
    "kg": 1000.0,
    "kilogram": 1000.0,
    "kilograms": 1000.0,
    "mg": 0.001,
    "milligram": 0.001,
    "milligrams": 0.001,
    "lb": 453.59237,
    "lbs": 453.59237,
    "pound": 453.59237,
    "pounds": 453.59237,
    "oz": 28.349523125,
    "ounce": 28.349523125,
    "ounces": 28.349523125,
    "t": 1_000_000.0,
    "tonne": 1_000_000.0,
    "tonnes": 1_000_000.0,
    "metric_ton": 1_000_000.0,
    "metric_tons": 1_000_000.0,
}


def _convert_distance(value, from_unit, to_unit):
    if from_unit not in _DISTANCE_TO_METRES:
        raise UnitError(f"unknown distance unit: {from_unit!r}")
    if to_unit not in _DISTANCE_TO_METRES:
        raise UnitError(f"unknown distance unit: {to_unit!r}")
    return value * _DISTANCE_TO_METRES[from_unit] / _DISTANCE_TO_METRES[to_unit]


def _convert_weight(value, from_unit, to_unit):
    if from_unit not in _WEIGHT_TO_GRAMS:
        raise UnitError(f"unknown weight unit: {from_unit!r}")
    if to_unit not in _WEIGHT_TO_GRAMS:
        raise UnitError(f"unknown weight unit: {to_unit!r}")
    return value * _WEIGHT_TO_GRAMS[from_unit] / _WEIGHT_TO_GRAMS[to_unit]


def _celsius_to_kelvin(c):
    return c + 273.15


def _kelvin_to_celsius(k):
    return k - 273.15


def _fahrenheit_to_celsius(f):
    return (f - 32.0) * 5.0 / 9.0


def _celsius_to_fahrenheit(c):
    return c * 9.0 / 5.0 + 32.0


# Aliases grouped by canonical symbol. The value is the canonical symbol, so
# lookup is two-stage: alias -> canonical -> formula branch. This keeps the
# conversion logic reading in terms of three well-known symbols rather than a
# dozen spellings.
_TEMPERATURE_ALIASES = {
    "c": "C", "celsius": "C", "degc": "C", "degcelsius": "C",
    "f": "F", "fahrenheit": "F", "degf": "F", "degfahrenheit": "F",
    "k": "K", "kelvin": "K", "degk": "K", "degkelvin": "K",
}


def _resolve_temperature(unit):
    if unit in _TEMPERATURE_ALIASES:
        return _TEMPERATURE_ALIASES[unit]
    if unit in ("C", "F", "K"):
        return unit
    raise UnitError(f"unknown temperature unit: {unit!r}")


def _convert_temperature(value, from_unit, to_unit):
    src = _resolve_temperature(from_unit)
    dst = _resolve_temperature(to_unit)
    if src == dst:
        return float(value)
    # Convert source to Celsius, then Celsius to target. Routing through Celsius
    # means each scale appears in exactly one conversion pair, so the offsets
    # are written once rather than once per pair.
    if src == "C":
        celsius = value
    elif src == "F":
        celsius = _fahrenheit_to_celsius(value)
    else:  # src == "K"
        celsius = _kelvin_to_celsius(value)
    if dst == "C":
        return float(celsius)
    if dst == "F":
        return _celsius_to_fahrenheit(celsius)
    return _celsius_to_kelvin(celsius)


_DOMAINS = {
    "distance": _convert_distance,
    "weight": _convert_weight,
    "temperature": _convert_temperature,
}


def _domain_of(unit):
    if unit in _DISTANCE_TO_METRES:
        return "distance"
    if unit in _WEIGHT_TO_GRAMS:
        return "weight"
    if unit in _TEMPERATURE_ALIASES or unit in ("C", "F", "K"):
        return "temperature"
    return None


def convert(value, from_unit, to_unit):
    """Convert ``value`` from ``from_unit`` to ``to_unit``.

    The domain (distance, weight, temperature) is inferred from the units
    themselves, so the caller does not name it. This means a typo can produce a
    ``UnitError`` naming the unit rather than the domain — the error message
    includes the offending unit string so the call site is identifiable.

    Returns a ``float``.

    Raises ``UnitError`` (a ``ValueError`` subclass) when either unit is unknown
    or when the two units belong to different domains.
    """
    if value is None:
        raise UnitError("value must be a number, got None")
    src_domain = _domain_of(from_unit)
    dst_domain = _domain_of(to_unit)
    if src_domain is None:
        raise UnitError(f"unknown unit: {from_unit!r}")
    if dst_domain is None:
        raise UnitError(f"unknown unit: {to_unit!r}")
    if src_domain != dst_domain:
        raise UnitError(
            f"cannot convert {from_unit!r} ({src_domain}) to {to_unit!r} ({dst_domain})"
        )
    return _DOMAINS[src_domain](float(value), from_unit, to_unit)


class KnownScales:
    """Read-only snapshot of the units the library recognises.

    Provided so callers can validate or enumerate units before calling
    ``convert``, without depending on the module's internal dictionaries.
    """

    distance = tuple(sorted(set(_DISTANCE_TO_METRES)))
    weight = tuple(sorted(set(_WEIGHT_TO_GRAMS)))
    temperature = tuple(sorted(set(_TEMPERATURE_ALIASES) | {"C", "F", "K"}))
