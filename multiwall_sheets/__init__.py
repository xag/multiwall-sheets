"""Multiwall polycarbonate sheets as data on furniture-design's kinds (source, clause, material, tool): each
sheet's properties as its maker prints them, and how the sheet makers say to cut it by hand. Unofficial: neither
the makers wrote nor endorsed it.

A sheet is one `material` under materials/, its params derived from its maker's clauses:

- density (kg/m3): its mass per area over its thickness, so a part made of it weighs what the sheet does;
- mass_per_area (kg/m2), rib_pitch (mm): as printed;
- thermal_expansion (mm/(m.K)): the resin's coefficient of linear thermal expansion;
- expansion_allowance (mm/m): the room its maker says to leave for it, per metre, and over which temperature
  difference (payload).

Its bending values are not stated (measured_along "unstated"): a multiwall sheet is not the clear wood or
panel furniture-design's bending checks hold, so no part of it is judged for sag.

The way the makers say to cut a multiwall sheet by hand is a `tool`, knife-on-multiwall-sheet, saying in French
and English how it is used, every sentence resting on clauses; its kerf is 0, the cut being scored and broken
along the line, which takes no material out, and its max_cut_depth the thickest sheet the maker of the sheet
read here allows a knife on.

Every document is copyrighted, so a clause carries its locator, its values and a few of the words it rests on,
and no quote; the copies are kept private and tests/test_values.py checks every value and word against them.

    from furniture_design.knowledge import knowledge as general, merge
    from multiwall_sheets import knowledge as sheets
    tree.root.children = merge(general(), sheets()) + [pieces]
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from quern.provenance import Quantity
from quern.tree import Node
from furniture_design.knowledge import with_authority

HERE = Path(__file__).parent
SOURCES = "sources"
MATERIALS = "materials"
TOOLS = "tools"


@lru_cache(maxsize=1)
def documents() -> dict[str, dict]:
    return {d["id"]: d for d in json.loads((HERE / "documents.json").read_text(encoding="utf-8"))["documents"]}


def _value(ref: str) -> dict:
    doc, clause, param = ref.split("/")
    return next(c for c in documents()[doc]["clauses"] if c["id"] == clause)["params"][param]


def _derived(ref: str, unit: str | None = None, scale: float = 1.0, how: str = "") -> Quantity:
    v = _value(ref)
    return Quantity(value=float(v["value"]) * scale, unit=unit or v["unit"], provenance="derived", grounded=True,
                    derived_from=[f"{SOURCES}/{ref}"], note=f"as printed: {v['printed']}{how}")


def sources() -> list[Node]:
    """One source per document, one clause per table row or passage read, its values as printed."""
    out = []
    for d in documents().values():
        clauses = [Node(id=c["id"], kind="clause",
                        payload={"locator": c["locator"],
                                 **({"rows": {k: v["printed"] for k, v in c["params"].items()}} if c["params"] else {})},
                        params={k: Quantity(value=float(v["value"]), unit=v["unit"], provenance="published",
                                            grounded=True, source=c["locator"], note=f"printed: {v['printed']}")
                                for k, v in c["params"].items()})
                   for c in d["clauses"]]
        out.append(Node(id=d["id"], kind="source", name=f"{d['publisher']}: {d['title']}",
                        payload={"publisher": d["publisher"], "url": d["url"], "fetched": d["fetched"],
                                 "sha256": d["sha256"], "licence": "copyrighted",
                                 "capture": "private copy, identified by its sha256"},
                        children=clauses))
    return out


LT = "polyvantis-thermoclear-manual"


def lexan_thermoclear_6() -> Node:
    """LEXAN THERMOCLEAR LT2UV62RS13 in opal white: 6 mm, two walls, rectangular cells."""
    sel = f"{LT}/product-selector"
    mass, thick = _value(f"{sel}/mass_per_area"), _value(f"{sel}/thickness")
    density = Quantity(value=float(mass["value"]) / float(thick["value"]) * 1000, unit="kg/m3", provenance="derived",
                       grounded=True, derived_from=[f"{SOURCES}/{sel}/mass_per_area", f"{SOURCES}/{sel}/thickness"],
                       note=f"{mass['value']} kg/m2 over {thick['value']} mm: the sheet's mass spread through its "
                            "thickness, cells included")
    return Node(
        id="lexan-thermoclear-lt2uv62rs13-opal", kind="material",
        name="LEXAN THERMOCLEAR LT2UV62RS13, opal white, 6 mm twin-wall polycarbonate",
        params={"density": density,
                "mass_per_area": _derived(f"{sel}/mass_per_area"),
                "rib_pitch": _derived(f"{sel}/rib_pitch"),
                "thermal_expansion": _derived(f"{LT}/resin-properties/thermal_expansion_coefficient", "mm/(m.K)", 0.01,
                                              ": 7.00 x 10^-5 per °C is 0.07 mm per metre per kelvin"),
                "expansion_allowance": _derived(f"{LT}/thermal-expansion/expansion_allowance")},
        payload={"form": "multiwall polycarbonate sheet, two walls, rectangular cells",
                 "label": "Lexan Thermoclear 6 mm opal", "maker": "Polyvantis (F&S B.V.)",
                 "product_code": "LT2UV62RS13", "colour_code": "WH7A092X", "thickness_mm": 6,
                 "measured_along": "unstated", "ribs_run_along": "length",
                 "expansion_over": "3 mm per metre for a temperature difference of 50 °C, as printed",
                 "say": {"fr": {"name": "Plaque alvéolaire Lexan Thermoclear 6 mm opale"},
                         "en": {"name": "Lexan Thermoclear 6 mm opal multiwall sheet"}}},
        links={"per": [f"{SOURCES}/{sel}", f"{SOURCES}/{LT}/resin-properties", f"{SOURCES}/{LT}/thermal-expansion",
                       f"{SOURCES}/{LT}/dos"]})


def knife() -> Node:
    """How a multiwall sheet is cut by hand with a knife, as the sheet makers say it."""
    S = SOURCES
    faq, ex, tips = f"{S}/exolon-faq-multiwall/cutting", f"{S}/exolon-multi-uv-manual/cutting", \
        f"{S}/exolon-multi-uv-manual/ribs"
    saw, edge = f"{S}/{LT}/sawing", f"{S}/{LT}/edge-sealing"
    return Node(
        id="knife-on-multiwall-sheet", kind="tool", name="Utility knife on a multiwall sheet",
        params={"kerf": Quantity(value=0.0, unit="mm", provenance="derived", grounded=True,
                                 derived_from=[faq], note="scored, then broken along the line: no material taken out"),
                "max_cut_depth": _derived(f"{LT}/sawing/knife_max_thickness")},
        payload={"maker": "any", "saw_kind": "knife",
                 "does": "cuts a multiwall sheet straight across, scored along a rule then broken",
                 "say": {
                     "fr": {"name": "Cutter (plaque alvéolaire)", "method": [
                         "Laisser le film de protection et tracer le trait dessus au crayon, le long d'une règle.",
                         "Placer le trait au plus près d'une nervure, pour que le bord tombe sur une alvéole fermée.",
                         "Avec un cutter bien affûté, à lame courte et rigide, guidé contre la règle, inciser le "
                         "trait plusieurs fois jusqu'à une profondeur suffisante, sans aller trop profond.",
                         "Casser la plaque le long du trait en appuyant avec précaution.",
                         "Souffler la poussière et les copeaux hors des alvéoles à l'air comprimé sec.",
                         "Laisser un bord lisse et arrondi, sans entaille."]},
                     "en": {"name": "Utility knife (multiwall sheet)", "method": [
                         "Leave the protective film on and mark the line on it in pencil, along a rule.",
                         "Put the line as close to a rib as you can, so the edge falls on a closed cell.",
                         "With a sharp utility knife, its blade short and rigid, guided against the rule, score the "
                         "line several times to a sufficient depth, without scoring too deep.",
                         "Break the sheet along the line, pressing carefully.",
                         "Blow the dust and chips out of the cells with dry compressed air.",
                         "Leave the edge smooth and rounded, with no notch."]}}},
        links={"per": [faq, tips, saw, ex, edge]})


# Who stands behind each source (furniture-design's AUTHORITIES).
AUTHORITY = {d: "maker" for d in ("polyvantis-thermoclear-manual", "exolon-faq-multiwall", "exolon-multi-uv-manual")}


def _say(id_: str, name: str, text: str, *about: str) -> Node:
    return Node(id=id_, kind="guidance", name=name, payload={"text": " ".join(text.split())},
                links={"about": list(about)} if about else {})


def guidance() -> Node:
    """What whoever designs with this package is told before reading its nodes (furniture-design's kind
    guidance): a reader gives it to its assistant and writes none of its own."""
    return Node(id="guidance", kind="", children=[
        _say("multiwall-sheets", "A multiwall polycarbonate sheet", """
            A multiwall polycarbonate sheet is a material of this package
            (materials/lexan-thermoclear-lt2uv62rs13-opal: its ribs run along its length and are set vertical).
            A part cut out of one with a knife links sawn_with tools/knife-on-multiwall-sheet, the sheet
            makers' way of scoring and breaking it, which takes no cut out and says up to which thickness. No
            sheet maker allows an angle grinder on multiwall sheet: do not cut one with it.""",
            "materials/lexan-thermoclear-lt2uv62rs13-opal", "tools/knife-on-multiwall-sheet"),
    ])


def knowledge() -> list[Node]:
    """The branches to merge beside furniture-design's: the sources, the sheets and the knife."""
    return [Node(id=SOURCES, kind="", children=with_authority(sources(), AUTHORITY)),
            Node(id=MATERIALS, kind="", children=[lexan_thermoclear_6()]),
            Node(id=TOOLS, kind="", children=[knife()]), guidance()]
