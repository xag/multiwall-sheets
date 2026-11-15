# multiwall-sheets

Multiwall (alveolar) polycarbonate sheets as data for [furniture-design](https://github.com/xag/furniture-design): each sheet's properties as its maker prints them, and how the sheet makers say to cut one by hand. **Unofficial**: the makers did not write or endorse it, and nothing here speaks for them.

## What is here

- `materials/lexan-thermoclear-lt2uv62rs13-opal`: Polyvantis's LEXAN THERMOCLEAR LT2UV62RS13 in opal white (WH7A092X), 6 mm, two walls, rectangular cells. `mass_per_area` 1.30 kg/m², `rib_pitch` 6.3 mm, `density` 217 kg/m³ (the mass per area over the thickness, so a part made of it weighs what the sheet weighs), `thermal_expansion` 0.07 mm per metre per kelvin (the resin's 7.00 × 10⁻⁵ per °C) and `expansion_allowance` 3 mm per metre, the room its maker says to leave for a temperature difference of 50 °C. It states no bending values: its maker prints the resin's modulus, measured on solid samples, and EN 16153 stiffnesses whose direction no public source states, so furniture-design judges no part of it for sag.
- `tools/knife-on-multiwall-sheet`: cutting a multiwall sheet with a utility knife, in French and English, every sentence resting on the makers' words: the line marked on the protective film along a rule, close to a rib; a sharp knife with a short rigid blade, guided, scoring the line several times without going too deep; the sheet broken along the line; the cells blown clean with dry compressed air; the edge left smooth and rounded. Its `kerf` is 0 (scored and broken, nothing is taken out) and its `max_cut_depth` 10 mm, the thickest sheet Polyvantis allows a knife on.

No maker read here allows an angle grinder or an abrasive disc on multiwall sheet: they name a knife, a fine-toothed circular saw, a jigsaw without pendulum action and a band saw.

No kinds and no rules of its own: a part made of a sheet links `uses` to it, and furniture-design's rules judge it.

## Sources

Polyvantis's LEXAN THERMOCLEAR technical, processing and installation guide (PV_TM_001, 12-24), Exolon's multi UV technical manual and its FAQ on multiwall sheets, fetched on 2026-11-15. They are copyrighted, so they are cited by locator, values and a few of the words each passage rests on, never quoted. The copies as fetched are kept in a private repo, and `tests/test_values.py` checks every value and word against them, by sha256: clone that repo beside this one, or set `FURNITURE_REPO`, or that test fails and says why.

## Using it

```python
from furniture_design.knowledge import knowledge as general, merge
from multiwall_sheets import knowledge as sheets

tree.root.children = merge(general(), sheets()) + [pieces]
```

## Design ledger

```sh
uv sync
uv run quern brief .
uv run quern check
```

There is no flight-recorder boundary: nothing here touches storage, the network, the clock or randomness at run time.

## Licence

- **The code** (`multiwall_sheets/*.py`, `tests/`, `ledger/`) is licensed under the [GNU Affero General Public License v3.0 or later](LICENSE), copyright 2026 Xavier Grehant.
- **The knowledge base**, the database `multiwall_sheets.knowledge()` returns (documents.json and every value on its nodes), is licensed under [Creative Commons Attribution-NonCommercial-NoDerivatives 4.0](LICENSE-DATA), database rights included, with one added permission: designing, building and selling furniture with it is allowed. An improvement is published here, through [CONTRIBUTING.md](CONTRIBUTING.md).
- The makers' values are cited from their documents, not licensed.

## Tests

`uv run pytest` runs the tests whose code, data or packages changed since they passed, last failures first then the fastest, under a time budget (testplan); `uv run pytest --all` runs them all, once a day. Both stop at the first failure.
