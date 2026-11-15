"""Every value and passage against the copy it was read from, and the sheet and the knife against
furniture-design's rules.

The copies are copyrighted and live in the private repo xag/furniture, checked out beside this one (or at
$FURNITURE_REPO), under sources/multiwall-polycarbonate/, each original beside its text. Without them these
tests fail, saying where they looked, and never skip.
"""

import hashlib
import os
import re
from pathlib import Path

from quern import Quern, run_rules
from quern.provenance import Quantity
from quern.tree import Node

from furniture_design.knowledge import knowledge as general, merge
from furniture_design.package import PACKAGE
from multiwall_sheets import documents, knowledge

ROOT = Path(__file__).resolve().parents[1]
CAPTURES = Path(os.environ.get("FURNITURE_REPO", ROOT.parent / "furniture")) / "sources" / "multiwall-polycarbonate"


def _text(doc: dict) -> str:
    original = CAPTURES / doc["file"]
    assert original.exists(), (f"the private copy {original} is missing: clone xag/furniture beside this repo or "
                               "set FURNITURE_REPO")
    assert hashlib.sha256(original.read_bytes()).hexdigest() == doc["sha256"], doc["id"]
    return re.sub(r"\s+", " ", original.with_suffix(".txt").read_text(encoding="utf-8"))


def _numbers(printed: str) -> list[float]:
    return [float(n.replace(",", ".")) for n in re.findall(r"\d+(?:[.,]\d+)?", printed)]


def test_every_value_and_passage_is_in_the_document_fetched():
    for doc in documents().values():
        text = _text(doc)
        for clause in doc["clauses"]:
            for name, v in clause["params"].items():
                assert v["printed"] in text, (doc["id"], clause["id"], name, v["printed"])
                assert v["value"] in _numbers(v["printed"]), (doc["id"], clause["id"], name)
            for w in clause.get("words", []):
                assert w in text, (doc["id"], clause["id"], w)
            assert clause["params"] or clause.get("words"), (doc["id"], clause["id"])


def _by_id(branch: str) -> dict[str, Node]:
    return {n.id: n for b in knowledge() if b.id == branch for n in b.children}


def test_the_sheet_reads_its_values_from_its_makers_manual():
    sheet = _by_id("materials")["lexan-thermoclear-lt2uv62rs13-opal"]
    p = sheet.params
    assert p["mass_per_area"].value == 1.3 and p["rib_pitch"].value == 6.3
    assert abs(p["density"].value - 1300 / 6) < 1e-9
    assert abs(p["thermal_expansion"].value - 0.07) < 1e-12 and p["thermal_expansion"].unit == "mm/(m.K)"
    assert p["expansion_allowance"].value == 3
    for q in p.values():
        assert q.grounded and q.derived_from


def test_the_knife_says_the_same_in_both_languages_and_cuts_what_the_maker_allows():
    k = _by_id("tools")["knife-on-multiwall-sheet"]
    fr, en = (k.payload["say"][lang]["method"] for lang in ("fr", "en"))
    assert len(fr) == len(en) == 6
    assert k.params["kerf"].value == 0 and k.params["max_cut_depth"].value == 10


def _tree(thickness: float) -> Quern:
    tree = Quern(vocabulary=PACKAGE.vocabulary, rules=PACKAGE.rules, solvers=PACKAGE.solvers)
    leaf = Node(id="leaf", kind="part",
                links={"uses": ["materials/lexan-thermoclear-lt2uv62rs13-opal"],
                       "sawn_with": ["tools/knife-on-multiwall-sheet"]},
                params={"thickness": Quantity(value=thickness, unit="mm", provenance="design-target")},
                payload={"shape": {"op": "box", "size": [thickness, 800, 2000]}})
    tree.root.children = merge(general(), knowledge()) + [
        Node(id="pieces", kind="", children=[Node(id="doors", kind="piece", children=[leaf])])]
    return tree


def _verdict(tree: Quern, rule: str) -> str:
    return next(r.verdict for r in run_rules(tree, "pieces/doors") if r.rule == rule and r.node == "pieces/doors/leaf")


def test_a_leaf_cut_with_the_knife_states_its_cut_and_no_thicker_sheet_than_the_maker_allows():
    assert _verdict(_tree(6), "a-part-is-sawn-with-a-saw-that-states-its-cut") == "holds"
    assert _verdict(_tree(6), "a-part-is-no-thicker-than-its-saw-cuts") == "holds"
    assert _verdict(_tree(16), "a-part-is-no-thicker-than-its-saw-cuts") == "broken"


def test_the_sheet_knife_and_sources_break_none_of_furniture_designs_rules():
    tree = Quern(vocabulary=PACKAGE.vocabulary, rules=PACKAGE.rules, solvers=PACKAGE.solvers)
    tree.root.children = merge(general(), knowledge())
    ours = {f"{b.id}/{n.id}" for b in knowledge() for n in b.children}
    broken = [r for r in run_rules(tree, "") if not r.ok and any(r.node == p or r.node.startswith(p + "/") for p in ours)]
    assert not broken, broken


def test_every_link_lands_on_a_clause_and_every_source_says_its_authority():
    clauses = {f"sources/{s.id}/{c.id}" for s in knowledge()[0].children for c in s.children}
    for s in knowledge()[0].children:
        assert s.payload["authority"] == "maker", s.id
    for b in knowledge()[1:]:
        for n in b.children:
            for p in n.links["per"]:
                assert p in clauses, (n.id, p)
            for q in n.params.values():
                for d in q.derived_from:
                    assert d in clauses or d.rsplit("/", 1)[0] in clauses, (n.id, d)
