"""The decisions multiwall-sheets is bound by, as a ledger. Read it with `uv run quern brief .`, never whole.

Vocabulary: ledger@0.8.0 and grounding@1.2.0, pinned in quern.lock.
"""

from __future__ import annotations

import os
from pathlib import Path

import quern.grounding  # noqa: F401
from quern import Node, Quern
from quern.library import consume

OWNER = ("Les portes sont en element de toiture alvéolée. [...] Il faudrait sourcer toutes les infos nécessaires et "
         "les intégrer aux packages. Pour la coupe et le montage. / Two new public repos (Recommended) / A cutter "
         "(Recommended)")


def _alt(id_: str, name: str, why: str) -> Node:
    return Node(id=id_, kind="alternative", name=name, payload={"why": why})


def entries() -> list[Node]:
    return [
        Node(
            id="multiwall-sheets-are-one-package", kind="decision",
            name="Multiwall polycarbonate sheets of every maker are one package, multiwall-sheets, which requires "
                 "furniture-design and adds each sheet as a material under materials/ and the way the sheet makers "
                 "say to cut one by hand as a tool under tools/, with the makers' documents as sources; it names no "
                 "shop and no piece",
            payload={"decided_on": "2026-11-15", "the_owner": OWNER,
                     "why": "furniture-design names no maker (its ledger: makers-products-are-in-packages-outside-"
                            "furniture-design), and its ledger's a-name-says-unofficial-only-when-it-names-a-maker-"
                            "or-shop names a package of one kind of product after the product. A multiwall sheet is "
                            "neither a wood panel nor a shop's range."},
            children=[
                _alt("in-wood-panels", "Put the sheets in wood-panels",
                     "A polycarbonate sheet is not a wood panel; the package's name would stop saying what it holds."),
                _alt("a-package-per-maker", "One unofficial package per sheet maker (Polyvantis, Exolon, ...)",
                     "Each would hold a sheet or two and the same way of cutting them."),
            ],
        ),
        Node(
            id="a-multiwall-sheets-density-is-its-mass-per-area-over-its-thickness", kind="decision",
            name="A multiwall sheet's density is its printed mass per area over its printed thickness (LT2UV62RS13: "
                 "1.30 kg/m2 over 6 mm, 217 kg/m3), so furniture-design's mass, which is a part's volume times its "
                 "material's density, weighs a part of it as much as the sheet weighs",
            links={"rests_on": ["multiwall-sheets-are-one-package"]},
            payload={"decided_on": "2026-11-15", "the_owner": OWNER,
                     "why": "The mass calculation reads density; a multiwall sheet is mostly air, and its maker "
                            "prints its mass per area, not a density."},
            children=[
                _alt("the-resins-density", "Use the resin's density (1.20 g/cm3, the maker's Table 2)",
                     "That is solid polycarbonate: a 6 mm leaf would weigh 7.2 kg/m2 instead of 1.3."),
                _alt("no-density", "State no density", "The piece's mass would then be refused for every part of it."),
            ],
        ),
        Node(
            id="a-knife-cut-takes-no-material", kind="decision",
            name="Cutting a multiwall sheet with a knife is a tool, knife-on-multiwall-sheet, whose kerf is 0: the "
                 "sheet makers' method scores the line and breaks the sheet along it (Exolon's FAQ), which takes "
                 "no material out; its max_cut_depth is the thickest sheet the sheet's maker allows a knife on "
                 "(Polyvantis: up to 10 mm)",
            links={"rests_on": ["multiwall-sheets-are-one-package"]},
            payload={"decided_on": "2026-11-15", "the_owner": OWNER,
                     "why": "furniture-design's rule a-part-is-sawn-with-a-saw-that-states-its-cut refuses a cutting "
                            "tool that states no cut, and the owner cuts the sheets with a cutter: no maker allows "
                            "an angle grinder on multiwall sheet, and Polyvantis allows a sharp knife up to 10 mm."},
            children=[
                _alt("no-kerf", "State no kerf for a knife",
                     "Every leaf cut with it would be refused, though its cut takes nothing out."),
                _alt("a-knifes-blade-thickness", "Count the blade's thickness",
                     "A scored and broken line leaves both sides whole: the blade does not cut through."),
            ],
        ),
        Node(
            id="a-multiwall-sheet-states-no-bending-values", kind="decision",
            name="A multiwall sheet states no bending values (measured_along unstated), so furniture-design judges "
                 "no part of it for sag or bending stress: its maker prints the resin's modulus, measured on solid "
                 "samples, and EN 16153 stiffnesses (Bx, By) whose direction and meaning no public source states",
            links={"rests_on": ["multiwall-sheets-are-one-package"]},
            payload={"decided_on": "2026-11-15", "the_owner": OWNER,
                     "why": "furniture-design's ledger: a-material-says-which-way-its-values-were-measured and "
                            "an-equation-is-applied-only-where-its-source-says-it-holds."},
            children=[
                _alt("the-resins-modulus", "Use the resin's tensile modulus (2300 MPa) on the sheet's thickness",
                     "A twin-wall section is two thin skins on ribs, not a solid board of 6 mm."),
                _alt("bx-as-ei", "Read Bx = 14 Nm2/m as the sheet's bending stiffness along the ribs",
                     "No public source says which of x and y runs along the ribs, and EN 16153's own definition "
                     "is in a copyrighted standard not read here."),
            ],
        ),
    ]


def build() -> Quern:
    root = Path(__file__).resolve().parents[1]
    lib, refs = consume(root, os.environ.get("QUERN_REGISTRY", root.parent / "quern-registry"))
    quern = Quern(packages=list(refs))
    quern = lib.effective(quern)
    quern.root.children = entries()
    return quern
