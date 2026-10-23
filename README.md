# unit_convert_py

Switch measurements across distance, weight, and temperature scales with a single function.

```python
from unit_convert_py import convert

convert(1.0, "m", "ft")           # 3.2808398950131
convert(100.0, "kg", "lb")         # 220.46226218487757
convert(0.0, "celsius", "fahrenheit")  # 32.0
```

The library exists because small projects keep re-implementing the same three conversions and getting the temperature offsets wrong. Everything routes through one ``convert(value, from_unit, to_unit)`` call; the domain is inferred from the units, so the caller never names it.

All results are floats. The scales here are real-valued, so compare with a tolerance rather than ``==``.

The awkward edge: unit strings are case-insensitive for distance and weight but case-sensitive for temperature, because ``m`` means metres and ``M`` is not a unit. Use ``"C"``, ``"F"``, ``"K"`` or the spelled-out forms ``celsius``, ``fahrenheit``, ``kelvin`` to avoid ambiguity.

Cross-domain conversion (e.g. kilograms to metres) raises ``UnitError``, a subclass of ``ValueError``.
