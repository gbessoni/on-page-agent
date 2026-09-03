"""Tests for v2.0.0 research-pipeline additions:
measure_dom_depth, flag_deep_nesting, STRUCTURAL_DIRECTIVES.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from research import (
    measure_dom_depth,
    flag_deep_nesting,
    STRUCTURAL_DIRECTIVES,
)


# --- measure_dom_depth --------------------------------------------------------

def test_dom_depth_flat():
    html = "<section><h2>Title</h2><div>answer</div></section>"
    # section(1) > h2(2) closes, div(2) closes, section closes -> max 2
    assert measure_dom_depth(html) == 2


def test_dom_depth_deeply_nested():
    html = (
        "<div><div><div><div><div><span>buried</span></div>"
        "</div></div></div></div>"
    )
    # 5 divs + 1 span = depth 6
    assert measure_dom_depth(html) == 6


def test_dom_depth_void_tags_do_not_count():
    html = "<div><img src='x'><br><hr><p>text</p></div>"
    # div(1) > p(2); img/br/hr are void and don't increase depth
    assert measure_dom_depth(html) == 2


def test_dom_depth_self_closing_do_not_count():
    html = "<div><img src='x' /><input type='text' /></div>"
    assert measure_dom_depth(html) == 1


def test_dom_depth_empty_and_none():
    assert measure_dom_depth("") == 0
    assert measure_dom_depth(None) == 0


def test_dom_depth_unbalanced_closes_clamped():
    # More closing tags than opens must not go negative
    html = "</div></div><section>x</section>"
    assert measure_dom_depth(html) == 1


# --- flag_deep_nesting --------------------------------------------------------

def test_flag_deep_nesting_not_assessed_without_raw_html():
    # Neither current parser supplies raw_html -> not_assessed, no fabrication
    content_data = [
        {"headings": ["H2: x"], "word_count": 100},
        {"headings": ["H2: y"], "word_count": 200},
    ]
    organic = [{"url": "https://a.com"}, {"url": "https://b.com"}]
    out = flag_deep_nesting(content_data, organic, top_n=3, max_depth=3)
    assert out["status"].startswith("not_assessed")
    assert out["assessed_count"] == 0
    assert out["flagged"] == []
    assert out["target_max_depth"] == 3


def test_flag_deep_nesting_flags_when_raw_html_present():
    deep = "<div><div><div><div><div><p>x</p></div></div></div></div></div>"
    flat = "<section><h2>t</h2><div>a</div></section>"
    content_data = [
        {"raw_html": deep},   # depth 6 -> flagged
        {"raw_html": flat},   # depth 2 -> ok
    ]
    organic = [{"url": "https://deep.com"}, {"url": "https://flat.com"}]
    out = flag_deep_nesting(content_data, organic, top_n=3, max_depth=3)
    assert out["status"] == "assessed"
    assert out["assessed_count"] == 2
    assert len(out["flagged"]) == 1
    assert out["flagged"][0]["url"] == "https://deep.com"
    assert out["flagged"][0]["max_depth"] == 6


def test_flag_deep_nesting_respects_top_n():
    deep = "<div><div><div><div><p>x</p></div></div></div></div>"  # depth 5
    content_data = [
        {"raw_html": "<section>ok</section>"},
        {"raw_html": "<section>ok</section>"},
        {"raw_html": "<section>ok</section>"},
        {"raw_html": deep},  # 4th competitor -- beyond top_n=3
    ]
    organic = [{"url": f"https://s{i}.com"} for i in range(4)]
    out = flag_deep_nesting(content_data, organic, top_n=3, max_depth=3)
    # The deep 4th competitor must not be assessed
    assert out["assessed_count"] == 3
    assert out["flagged"] == []


def test_flag_deep_nesting_empty_inputs():
    out = flag_deep_nesting([], [], top_n=3, max_depth=3)
    assert out["status"].startswith("not_assessed")
    assert out["assessed_count"] == 0
    out2 = flag_deep_nesting(None, None, top_n=3, max_depth=3)
    assert out2["assessed_count"] == 0


# --- STRUCTURAL_DIRECTIVES ----------------------------------------------------

def test_structural_directives_shape():
    sd = STRUCTURAL_DIRECTIVES
    assert sd["anti_paragraph_rule"] is True
    assert sd["max_dom_nesting_depth"] == 3
    # The snippet container directive must forbid bare <p>
    assert "<p>" in sd["snippet_answer_container"]
    assert "NEVER" in sd["snippet_answer_container"]
    # Two-gate target names both gates
    assert "Gate 1" in sd["two_gate_target"]
    assert "Gate 2" in sd["two_gate_target"]
    # Subheading directive bans generic headings
    assert "Overview" in sd["subheading_entity_synergy"]
    # v2.1.0: anti-NLP-stuffing directive present and forbids the pattern
    assert "anti_nlp_stuffing" in sd
    assert "FORBIDDEN" in sd["anti_nlp_stuffing"]
    assert "de-indexation" in sd["anti_nlp_stuffing"]
    # v2.3.0: AI SEO correlation protocols
    assert sd["outbound_citations_min"] == 5
    assert "nofollow" in sd["outbound_citation_rule"]
    assert "Title" in sd["strict_phrase_placement"]
    assert "H2/H3/H4" in sd["strict_phrase_placement"]
    assert "verifiable fact" in sd["entity_fact_pairing"]
    assert "informational" in sd["intent_divergence"]
    assert "boilerplate" in sd["anti_boilerplate_linking"]


if __name__ == "__main__":
    test_dom_depth_flat()
    test_dom_depth_deeply_nested()
    test_dom_depth_void_tags_do_not_count()
    test_dom_depth_self_closing_do_not_count()
    test_dom_depth_empty_and_none()
    test_dom_depth_unbalanced_closes_clamped()
    test_flag_deep_nesting_not_assessed_without_raw_html()
    test_flag_deep_nesting_flags_when_raw_html_present()
    test_flag_deep_nesting_respects_top_n()
    test_flag_deep_nesting_empty_inputs()
    test_structural_directives_shape()
    print("All tests passed.")
