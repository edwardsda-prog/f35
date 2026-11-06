"""Unit tests for F-35 Executive Storytelling Slide Deck generation.

Verifies:
1. Output slide deck exists and is valid 16:9 widescreen presentation.
2. Contains exactly 12 slides (9 storytelling + 3 appendix).
3. 100% of slides contain populated speaker notes.
4. Live demo slides (4, 5, 6) include stage direction switch cues.
5. Appendix slides (10, 11, 12) contain architecture canvas placeholders.
"""

from pathlib import Path
import pytest
from pptx import Presentation
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.util import Inches

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DECK_PATH = PROJECT_ROOT / "docs" / "F35_Executive_Storytelling_Deck.pptx"
USE_CASES_DECK_PATH = PROJECT_ROOT / "docs" / "F35_Executive_Use_Cases_Deck.pptx"


@pytest.fixture(scope="module")
def presentation() -> Presentation:
    assert DECK_PATH.exists(), f"Deck missing at {DECK_PATH}"
    return Presentation(str(DECK_PATH))


def test_deck_files_exist():
    """Verify both canonical and synced decks exist."""
    assert DECK_PATH.exists(), "F35_Executive_Storytelling_Deck.pptx must exist"
    assert USE_CASES_DECK_PATH.exists(), "F35_Executive_Use_Cases_Deck.pptx must exist"
    assert DECK_PATH.stat().st_size > 50000, "Deck size must be substantial (>50KB)"
    assert USE_CASES_DECK_PATH.stat().st_size > 50000, "Synced deck size must be substantial (>50KB)"


def test_slide_count_is_twelve(presentation: Presentation):
    """Verify the deck has exactly 12 slides (9 core + 3 appendix)."""
    assert len(presentation.slides) == 12, f"Expected 12 slides, got {len(presentation.slides)}"


def test_widescreen_16_9_dimensions(presentation: Presentation):
    """Verify the deck uses 16:9 widescreen dimensions (13.333 x 7.500 inches)."""
    width_inches = presentation.slide_width / Inches(1)
    height_inches = presentation.slide_height / Inches(1)
    assert abs(width_inches - 13.333) < 0.05, f"Expected width ~13.333, got {width_inches}"
    assert abs(height_inches - 7.500) < 0.05, f"Expected height ~7.500, got {height_inches}"


def test_speaker_notes_100_percent_coverage(presentation: Presentation):
    """Verify 100% of slides have non-empty, detailed speaker notes."""
    for idx, slide in enumerate(presentation.slides, start=1):
        assert slide.has_notes_slide, f"Slide {idx} must have notes slide"
        notes_text = slide.notes_slide.notes_text_frame.text.strip()
        assert len(notes_text) >= 100, f"Slide {idx} speaker notes too brief ({len(notes_text)} chars)"


def test_live_demo_switch_markers(presentation: Presentation):
    """Verify Slides 4, 5, and 6 contain the exact live demo switch marker in speaker notes."""
    live_demo_slides = [4, 5, 6]
    expected_marker = "👉 SWITCH TO LIVE SCREEN NOW"

    for slide_num in live_demo_slides:
        slide = presentation.slides[slide_num - 1]
        notes = slide.notes_slide.notes_text_frame.text
        assert expected_marker in notes, f"Slide {slide_num} missing '{expected_marker}' in notes"


def test_appendix_architecture_canvases_exist(presentation: Presentation):
    """Verify Slides 10, 11, and 12 form the themed Appendix with architecture canvas placeholders."""
    # Slide 10: Appendix Divider
    slide_10 = presentation.slides[9]
    slide_10_text = " ".join(shape.text for shape in slide_10.shapes if shape.has_text_frame)
    assert "APPENDIX" in slide_10_text
    assert "Architecture & Technical Foundations" in slide_10_text

    # Slide 11: Architecture Diagram Canvas I
    slide_11 = presentation.slides[10]
    slide_11_text = " ".join(shape.text for shape in slide_11.shapes if shape.has_text_frame).upper()
    assert "SOLUTION ARCHITECTURE & MULTI-AGENT ORCHESTRATION" in slide_11_text
    assert "ARCHITECTURE DIAGRAM CANVAS" in slide_11_text
    dashed_shapes_11 = [
        s for s in slide_11.shapes
        if hasattr(s, "line") and s.line.dash_style == MSO_LINE_DASH_STYLE.DASH
    ]
    assert len(dashed_shapes_11) >= 1, "Slide 11 must contain a dashed canvas placeholder shape"

    # Slide 12: Architecture Diagram Canvas II
    slide_12 = presentation.slides[11]
    slide_12_text = " ".join(shape.text for shape in slide_12.shapes if shape.has_text_frame).upper()
    assert "DATA FLOW, CONTINUOUS REPLICATION & SEMANTIC GOVERNANCE" in slide_12_text
    assert "ARCHITECTURE DIAGRAM CANVAS" in slide_12_text
    dashed_shapes_12 = [
        s for s in slide_12.shapes
        if hasattr(s, "line") and s.line.dash_style == MSO_LINE_DASH_STYLE.DASH
    ]
    assert len(dashed_shapes_12) >= 1, "Slide 12 must contain a dashed canvas placeholder shape"


def test_brand_identity_and_assets(presentation: Presentation):
    """Verify title slide has imagery and Google branding."""
    title_slide = presentation.slides[0]
    # Check that shapes include pictures (Google logo, F35 hero photo)
    picture_count = sum(1 for shape in title_slide.shapes if shape.shape_type == 13)  # MSO_SHAPE_TYPE.PICTURE = 13
    assert picture_count >= 1, "Title slide must include visual picture assets"


def test_classification_agility(presentation: Presentation):
    """Verify zero occurrences of BigQuery or Gemini Enterprise, and required brand terms exist."""
    forbidden = ["bigquery", "gemini enterprise"]
    for deck_obj in [presentation, Presentation(str(USE_CASES_DECK_PATH))]:
        all_texts = []
        for idx, slide in enumerate(deck_obj.slides, start=1):
            for shape in slide.shapes:
                if shape.has_text_frame:
                    for paragraph in shape.text_frame.paragraphs:
                        text_lower = paragraph.text.lower()
                        for term in forbidden:
                            assert term not in text_lower, (
                                f"Slide {idx} contains forbidden term '{term}' in text: '{paragraph.text}'"
                            )
                    all_texts.append(shape.text_frame.text)

        full_deck_text = " ".join(all_texts)
        assert "Agents (F35 Support)" in full_deck_text, "Deck must contain 'Agents (F35 Support)'"
        assert "F35 Data Warehouse" in full_deck_text, "Deck must contain 'F35 Data Warehouse'"


def test_no_classification_markings(presentation: Presentation):
    """Verify complete removal of classification marks (e.g. OFFICIAL-SENSITIVE) across all slides and notes."""
    forbidden_terms = ["official-sensitive", "demo track"]
    for idx, slide in enumerate(presentation.slides, start=1):
        notes = slide.notes_slide.notes_text_frame.text if slide.has_notes_slide else ""
        for term in forbidden_terms:
            assert term not in notes.lower(), (
                f"Slide {idx} speaker notes contain classification term '{term}'"
            )

        for shape in slide.shapes:
            if shape.has_text_frame:
                shape_text_lower = shape.text_frame.text.lower()
                for term in forbidden_terms:
                    assert term not in shape_text_lower, (
                        f"Slide {idx} shape contains classification term '{term}' in '{shape.text_frame.text}'"
                    )


def test_no_latency_references(presentation: Presentation):
    """Verify complete removal of latency and SLA metrics across all slides and notes."""
    forbidden_terms = [
        "latency",
        "sla:",
        "response sla",
        "speed_sla",
        "< 1.5s",
        "< 790ms",
        "< 400ms",
        "< 350ms",
        "sub-450ms",
        "sub-second",
        "378 milliseconds",
        "1.2 seconds",
        "790 milliseconds",
    ]
    for idx, slide in enumerate(presentation.slides, start=1):
        notes = slide.notes_slide.notes_text_frame.text if slide.has_notes_slide else ""
        for term in forbidden_terms:
            assert term not in notes.lower(), (
                f"Slide {idx} speaker notes contain latency reference '{term}'"
            )

        for shape in slide.shapes:
            if shape.has_text_frame:
                shape_text_lower = shape.text_frame.text.lower()
                for term in forbidden_terms:
                    assert term not in shape_text_lower, (
                        f"Slide {idx} shape contains latency reference '{term}' in '{shape.text_frame.text}'"
                    )


def test_high_contrast_text_readability(presentation: Presentation):
    """Verify that white text is never rendered on white or uncolored background shapes."""
    from pptx.dml.color import RGBColor

    for idx, slide in enumerate(presentation.slides, start=1):
        for shape in slide.shapes:
            if shape.has_text_frame:
                for p in shape.text_frame.paragraphs:
                    for run in p.runs:
                        if run.font.color and run.font.color.rgb == RGBColor(255, 255, 255):
                            # White text is ONLY permitted inside pills/badges with dark solid fills
                            assert shape.fill.type == 1, (
                                f"Slide {idx} has white text '{run.text}' inside shape without solid fill"
                            )
                            fill_rgb = shape.fill.fore_color.rgb
                            # Fill must NOT be white or light grey
                            assert fill_rgb not in [RGBColor(255, 255, 255), RGBColor(248, 249, 250), RGBColor(232, 240, 254)], (
                                f"Slide {idx} has white text '{run.text}' on light background ({fill_rgb})"
                            )

