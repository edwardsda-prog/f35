#!/usr/bin/env python3
"""Independent Empirical Verification Harness for F-35 Executive Presentation Decks.

Author: Challenger 1 (Adversarial Critic & Specialist)
Tests:
- File size > 50KB for both docs/F35_Executive_Storytelling_Deck.pptx and docs/F35_Executive_Use_Cases_Deck.pptx
- Slide count == 12
- Dimensions == (13.333333 in, 7.500000 in)
- Speaker note length >= 100 characters on every single slide
- Verbatim stage cue "👉 SWITCH TO LIVE SCREEN NOW" on slides 4, 5, 6 notes
- Slide 10 has Appendix section divider title ("APPENDIX", "Architecture & Technical Foundations")
- Slides 11 and 12 have dashed border container shapes and "ARCHITECTURE DIAGRAM CANVAS" title
- Deep text scan: assert zero occurrences of "BigQuery" and "Gemini Enterprise" in any text frame or note
- Assert presence of "Agents (F35 Support)" and "F35 Data Warehouse"
"""

import sys
from pathlib import Path
from pptx import Presentation
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.util import Inches

PROJECT_ROOT = Path(__file__).resolve().parent.parent
STORYTELLING_DECK = PROJECT_ROOT / "docs" / "F35_Executive_Storytelling_Deck.pptx"
USE_CASES_DECK = PROJECT_ROOT / "docs" / "F35_Executive_Use_Cases_Deck.pptx"

TARGET_DECKS = [STORYTELLING_DECK, USE_CASES_DECK]

def extract_all_text_elements(slide):
    """Recursively extract all text from shapes, tables, and groups."""
    texts = []
    
    def _extract_shape(shape):
        if shape.has_text_frame:
            for p in shape.text_frame.paragraphs:
                texts.append((shape.name, p.text))
        if shape.has_table:
            for row in shape.table.rows:
                for cell in row.cells:
                    for p in cell.text_frame.paragraphs:
                        texts.append((f"{shape.name}_cell", p.text))
        if shape.shape_type == 6:  # MSO_SHAPE_TYPE.GROUP
            for sub_shape in shape.shapes:
                _extract_shape(sub_shape)

    for shape in slide.shapes:
        _extract_shape(shape)
        
    return texts

def verify_deck(deck_path: Path):
    print(f"\n=======================================================")
    print(f"VERIFYING DECK: {deck_path.name}")
    print(f"Path: {deck_path}")
    print(f"=======================================================")
    
    # 1. File existence and size
    assert deck_path.exists(), f"Deck file missing: {deck_path}"
    file_size = deck_path.stat().st_size
    print(f"[TEST 1] File Size: {file_size:,} bytes")
    assert file_size > 50000, f"File size {file_size} <= 50,000 bytes threshold"
    print("  -> PASS: File size > 50KB")

    prs = Presentation(str(deck_path))

    # 2. Slide count
    slide_count = len(prs.slides)
    print(f"[TEST 2] Slide Count: {slide_count}")
    assert slide_count == 12, f"Expected 12 slides, found {slide_count}"
    print("  -> PASS: Slide count == 12")

    # 3. Slide dimensions
    width_in = prs.slide_width / Inches(1)
    height_in = prs.slide_height / Inches(1)
    print(f"[TEST 3] Slide Dimensions: {width_in:.6f} in x {height_in:.6f} in (EMUs: {prs.slide_width} x {prs.slide_height})")
    assert abs(width_in - 13.333333) < 0.01, f"Expected width ~13.333333 in, got {width_in}"
    assert abs(height_in - 7.500000) < 0.01, f"Expected height ~7.500000 in, got {height_in}"
    print("  -> PASS: Widescreen 16:9 (13.333333 in x 7.500000 in)")

    # 4. Speaker notes
    print(f"[TEST 4] Speaker Notes Coverage & Length (>= 100 chars):")
    for idx, slide in enumerate(prs.slides, start=1):
        assert slide.has_notes_slide, f"Slide {idx} missing notes slide"
        notes_text = slide.notes_slide.notes_text_frame.text.strip()
        length = len(notes_text)
        print(f"  Slide {idx:2d}: {length:4d} characters | Sample: {notes_text[:60]!r}...")
        assert length >= 100, f"Slide {idx} note length {length} < 100 chars"
    print("  -> PASS: 100% of slides have notes >= 100 chars")

    # 5. Live stage cues on slides 4, 5, 6
    print(f"[TEST 5] Live Stage Cue ('👉 SWITCH TO LIVE SCREEN NOW') on Slides 4, 5, 6:")
    expected_cue = "👉 SWITCH TO LIVE SCREEN NOW"
    for s_idx in [4, 5, 6]:
        slide = prs.slides[s_idx - 1]
        note = slide.notes_slide.notes_text_frame.text
        assert expected_cue in note, f"Slide {s_idx} missing exact cue '{expected_cue}'"
        print(f"  Slide {s_idx:2d}: Found exact cue '{expected_cue}'")
    
    # Check other slides don't have the cue
    for s_idx in [1, 2, 3, 7, 8, 9, 10, 11, 12]:
        slide = prs.slides[s_idx - 1]
        note = slide.notes_slide.notes_text_frame.text
        if expected_cue in note:
            print(f"  [WARNING] Slide {s_idx} also contains the live cue.")
    print("  -> PASS: Slides 4, 5, 6 contain verbatim stage cue")

    # 6. Slide 10 Appendix section divider
    print(f"[TEST 6] Slide 10 Appendix Section Divider:")
    slide_10 = prs.slides[9]
    slide_10_texts = [txt for _, txt in extract_all_text_elements(slide_10)]
    slide_10_full = " ".join(slide_10_texts)
    print(f"  Slide 10 Text: {slide_10_full[:120]!r}...")
    assert "APPENDIX" in slide_10_full.upper(), "Slide 10 missing 'APPENDIX' in text"
    assert "Architecture & Technical Foundations" in slide_10_full, "Slide 10 missing 'Architecture & Technical Foundations'"
    print("  -> PASS: Slide 10 is Appendix section divider")

    # 7. Slides 11 & 12 Dashed Border Canvas Shapes & Canvas Title
    print(f"[TEST 7] Slides 11 & 12 Dashed Architecture Canvas & Titles:")
    for s_idx, title_keyword in [(11, "SOLUTION ARCHITECTURE & MULTI-AGENT ORCHESTRATION"), 
                                 (12, "DATA FLOW, CONTINUOUS REPLICATION & SEMANTIC GOVERNANCE")]:
        slide = prs.slides[s_idx - 1]
        texts = [txt for _, txt in extract_all_text_elements(slide)]
        full_text = " ".join(texts).upper()
        assert title_keyword in full_text, f"Slide {s_idx} missing section header '{title_keyword}'"
        assert "ARCHITECTURE DIAGRAM CANVAS" in full_text, f"Slide {s_idx} missing 'ARCHITECTURE DIAGRAM CANVAS'"
        
        dashed_shapes = [
            s for s in slide.shapes
            if hasattr(s, "line") and s.line.dash_style == MSO_LINE_DASH_STYLE.DASH
        ]
        print(f"  Slide {s_idx:2d}: Found {len(dashed_shapes)} dashed border shape(s). Title: {title_keyword[:40]}...")
        assert len(dashed_shapes) >= 1, f"Slide {s_idx} has no shapes with MSO_LINE_DASH_STYLE.DASH"
    print("  -> PASS: Slides 11 & 12 have dashed border container shapes and required canvas titles")

    # 8. Deep text scan: assert zero occurrences of "BigQuery" and "Gemini Enterprise" in text frames and notes
    print(f"[TEST 8] Deep Text Scan for Forbidden Terms ('BigQuery', 'Gemini Enterprise') in Shapes AND Notes:")
    forbidden_terms = ["bigquery", "gemini enterprise"]
    found_violations = []

    for idx, slide in enumerate(prs.slides, start=1):
        # Scan shapes
        shape_elements = extract_all_text_elements(slide)
        for shape_name, text in shape_elements:
            t_lower = text.lower()
            for term in forbidden_terms:
                if term in t_lower:
                    found_violations.append((idx, f"Shape '{shape_name}'", term, text))
        
        # Scan speaker notes
        if slide.has_notes_slide:
            notes_text = slide.notes_slide.notes_text_frame.text
            n_lower = notes_text.lower()
            for term in forbidden_terms:
                if term in n_lower:
                    found_violations.append((idx, "Speaker Notes", term, notes_text))

    if found_violations:
        print("  -> FAIL: Found forbidden terms:")
        for v in found_violations:
            print(f"     Slide {v[0]} [{v[1]}]: term '{v[2]}' in: {v[3][:100]!r}")
        assert False, f"Deep text scan failed: {len(found_violations)} forbidden term occurrences found"
    else:
        print("  -> PASS: Zero occurrences of 'BigQuery' or 'Gemini Enterprise' in all text frames and speaker notes")

    # 9. Assert presence of "Agents (F35 Support)" and "F35 Data Warehouse"
    print(f"[TEST 9] Assert Presence of Required Branding:")
    all_slide_texts = []
    for slide in prs.slides:
        all_slide_texts.extend(txt for _, txt in extract_all_text_elements(slide))
        if slide.has_notes_slide:
            all_slide_texts.append(slide.notes_slide.notes_text_frame.text)
    
    total_corpus = " ".join(all_slide_texts)
    assert "Agents (F35 Support)" in total_corpus, "Required brand 'Agents (F35 Support)' not found in deck"
    assert "F35 Data Warehouse" in total_corpus, "Required brand 'F35 Data Warehouse' not found in deck"
    print(f"  Count 'Agents (F35 Support)': {total_corpus.count('Agents (F35 Support)')}")
    print(f"  Count 'F35 Data Warehouse':   {total_corpus.count('F35 Data Warehouse')}")
    print("  -> PASS: Required branding verified present across the deck")

    return True

def main():
    print("=== STARTING CHALLENGER 1 INDEPENDENT EMPIRICAL VERIFICATION ===")
    all_passed = True
    for deck in TARGET_DECKS:
        try:
            verify_deck(deck)
        except AssertionError as e:
            print(f"\n[FAIL] Assertion failed on {deck.name}: {e}")
            all_passed = False
        except Exception as e:
            print(f"\n[ERROR] Unexpected error on {deck.name}: {e}")
            all_passed = False

    if not all_passed:
        print("\nOVERALL VERDICT: CHALLENGE_FAILED")
        sys.exit(1)
    else:
        print("\n=======================================================")
        print("OVERALL VERDICT: APPROVE (ALL EMPIRICAL TESTS PASSED)")
        print("=======================================================")
        sys.exit(0)

if __name__ == "__main__":
    main()
