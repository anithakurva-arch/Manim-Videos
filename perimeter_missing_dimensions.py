import os
import urllib.request
import manimpango
from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.openai import OpenAIService

LAVENDER_BG = "#E7E5F3"
PURPLE      = "#7464CE"
ORANGE_HL   = "#FF9302"
PALE_PURPLE = "#9495D7"

# ============================================================
# POPPINS AUTO-DOWNLOAD & REGISTRATION
# ============================================================
def _setup_poppins():
    base_dir  = os.path.dirname(os.path.abspath(__file__))
    fonts_dir = os.path.join(base_dir, ".fonts")
    os.makedirs(fonts_dir, exist_ok=True)
    base_url = "https://raw.githubusercontent.com/google/fonts/main/ofl/poppins/"
    fonts = {
        "Poppins-Regular.ttf":  base_url + "Poppins-Regular.ttf",
        "Poppins-Bold.ttf":     base_url + "Poppins-Bold.ttf",
        "Poppins-Italic.ttf":   base_url + "Poppins-Italic.ttf",
        "Poppins-SemiBold.ttf": base_url + "Poppins-SemiBold.ttf",
    }
    for fname, url in fonts.items():
        path = os.path.join(fonts_dir, fname)
        if not os.path.exists(path):
            try:
                print(f"Downloading {fname}")
                urllib.request.urlretrieve(url, path)
            except Exception as e:
                print(f"   Could not download {fname}: {e}")
                continue
        try:
            manimpango.register_font(path)
        except Exception:
            pass
    print("Poppins setup complete.")

_setup_poppins()

# ============================================================
# BOOKMARK FAILURE TRACKER (DEBUG)
# ============================================================
import manim_voiceover.tracker as _vt
_orig_time_until_bookmark = _vt.VoiceoverTracker.time_until_bookmark
_FAILED_BOOKMARKS = []

def _safe_time_until_bookmark(self, mark, buff=0.0, limit=None):
    try:
        return _orig_time_until_bookmark(self, mark, buff, limit)
    except Exception:
        scene_text = getattr(self, 'data', {}).get('input_text', 'unknown')[:80]
        _FAILED_BOOKMARKS.append((mark, scene_text))
        print(f"WARNING  Bookmark '{mark}' NOT FOUND in: {scene_text}...")
        return 0.0

_vt.VoiceoverTracker.time_until_bookmark = _safe_time_until_bookmark

import atexit
def _report():
    if _FAILED_BOOKMARKS:
        print("\n" + "="*60)
        print(f"FAILED BOOKMARKS SUMMARY ({len(_FAILED_BOOKMARKS)} total):")
        print("="*60)
        for mark, text in _FAILED_BOOKMARKS:
            print(f"  FAILED: {mark}  ->  {text}")
        print("="*60)
atexit.register(_report)

TTS_INSTRUCTIONS = """
Voice & Personality:
You are a warm, patient, and encouraging mathematics teacher speaking
to a middle-school student. Your tone is friendly, calm, and confident
never rushed, never robotic. You sound like a human explainer in a
Khan Academy or 3Blue1Brown style video. The voice profile is shimmer
bright, warm, and slightly playful.

Pacing:
Speak at a MODERATE-TO-SLOW pace. Honor the commas, dashes, and
ellipses in the script they are deliberate pacing marks placed by
the director.

Variables and Math Terms:
When pronouncing single-letter variables like x, y, z, a, b, c, h, r,
or t, slow down noticeably and articulate each letter clearly with a
brief micro-pause before and after it.

Formulas:
Slow down further on equations. Pause between each component so the
student can match the spoken word to the symbol on screen.

Numbers and Units:
Pronounce numbers clearly. For units like centimeter square or
meter cube, say them with a confident, deliberate cadence.

Emphasis:
Naturally emphasize key terms: shape names, formulas, the final
answer, and any word that introduces a new concept.

Pauses:
Beat at commas, medium pause at dashes, dramatic pause at ellipses.
After stating a final answer, pause for a moment before continuing.

Mood:
Encouraging, curious, and warm. Avoid monotone. Add gentle warmth.

Do NOT:
- Do not race through sentences.
- Do not flatten your voice into monotone.
- Do not add filler words or commentary not in the script.
- Do not improvise or paraphrase, read the script exactly.
"""

# ============================================================
# COSEC TEMPLATE (version-safe clone of gnu_freesans_tx)
# ============================================================
def _make_cosec_template():
    base = TexFontTemplates.gnu_freesans_tx
    t = TexTemplate(
        tex_compiler     = base.tex_compiler,
        output_format    = base.output_format,
        preamble         = base.preamble,
        placeholder_text = base.placeholder_text,
    )
    t.add_to_preamble(r"\DeclareMathOperator{\cosec}{cosec}")
    return t

COSEC_TEMPLATE = _make_cosec_template()


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def create_heading_badge(text_str):
    t = Text(text_str, font="Poppins", font_size=28, color=WHITE, weight=BOLD)
    badge = RoundedRectangle(
        corner_radius=0.2,
        width=t.width + 0.6,
        height=t.height + 0.3,
        fill_color=PURPLE,
        fill_opacity=1,
        stroke_width=0,
    )
    badge.move_to(t)
    return VGroup(badge, t).to_corner(UL, buff=0.3)


def math_obj(tex_str, color=PURPLE, font_size=36):
    return MathTex(
        tex_str,
        tex_template=TexFontTemplates.gnu_freesans_tx,
        color=color,
        font_size=font_size,
    )


def math_obj_cosec(tex_str, color=PURPLE, font_size=36):
    return MathTex(
        tex_str,
        tex_template=COSEC_TEMPLATE,
        color=color,
        font_size=font_size,
    )


def fade_out_all(scene, *mobjects):
    """Utility: FadeOut all passed mobjects that are not None."""
    targets = [m for m in mobjects if m is not None]
    if targets:
        scene.play(*[FadeOut(m) for m in targets], run_time=0.8)


# ============================================================
# MAIN SCENE
# ============================================================

class PerimeterMissingDimensions(VoiceoverScene):

    def construct(self):
        self.set_speech_service(
            OpenAIService(
                voice="shimmer",
                model="gpt-4o-mini-tts",
                transcription_model="medium",
                instructions=TTS_INSTRUCTIONS,
            ),
            create_subcaption=False,
        )

        # ============================================================
        # SEGMENT 1 — HOOK
        # ============================================================
        with self.voiceover(
            text=(
                '<bookmark mark="bk_title"/>Hello students! '
                '<bookmark mark="bk_hook_chairs"/>Imagine you are arranging chairs around a rectangular classroom table. '
                'You know the total number of chairs that fit around it, — '
                'and you know how many fit along one side. '
                '<bookmark mark="bk_hook_q"/>Could you figure out how many fit along the other side, '
                'without counting again?'
            )
        ) as tracker:

            # 1a — Title slide
            self.wait_until_bookmark("bk_title")
            self.camera.background_color = PURPLE
            title_main = Text(
                "Perimeter and Area",
                font="Poppins", font_size=52, color=WHITE, weight=BOLD,
            ).move_to(UP * 0.4)
            title_sub = Text(
                "Finding Missing Dimensions",
                font="Poppins", font_size=32, color=WHITE,
            ).next_to(title_main, DOWN, buff=0.35)
            self.play(FadeIn(title_main), run_time=0.8)
            self.play(FadeIn(title_sub), run_time=0.7)
            self.wait(0.3)

            # 1b — Transition to hook
            self.wait_until_bookmark("bk_hook_chairs")
            self.play(FadeOut(title_main), FadeOut(title_sub), run_time=0.6)
            self.camera.background_color = LAVENDER_BG

            # Draw table rectangle
            table = Rectangle(
                width=4.0, height=2.2,
                color=PURPLE, stroke_width=2.5, fill_opacity=0,
            ).move_to(ORIGIN + DOWN * 0.2)

            # Chair squares along edges (small squares)
            chair_size = 0.28
            chairs = VGroup()
            n_long = 5
            n_short = 3
            for i in range(n_long):
                x = table.get_left()[0] + (i + 0.5) * (table.width / n_long)
                # top chairs
                c = Square(side_length=chair_size, color=PURPLE,
                           stroke_width=1.5, fill_opacity=0.08,
                           fill_color=PURPLE)
                c.move_to([x, table.get_top()[1] + chair_size * 0.6, 0])
                chairs.add(c)
                # bottom chairs
                c2 = Square(side_length=chair_size, color=PURPLE,
                            stroke_width=1.5, fill_opacity=0.08,
                            fill_color=PURPLE)
                c2.move_to([x, table.get_bottom()[1] - chair_size * 0.6, 0])
                chairs.add(c2)
            for j in range(n_short):
                y = table.get_bottom()[1] + (j + 0.5) * (table.height / n_short)
                # left chairs
                c3 = Square(side_length=chair_size, color=PURPLE,
                            stroke_width=1.5, fill_opacity=0.08,
                            fill_color=PURPLE)
                c3.move_to([table.get_left()[0] - chair_size * 0.6, y, 0])
                chairs.add(c3)
                # right chairs
                c4 = Square(side_length=chair_size, color=PURPLE,
                            stroke_width=1.5, fill_opacity=0.08,
                            fill_color=PURPLE)
                c4.move_to([table.get_right()[0] + chair_size * 0.6, y, 0])
                chairs.add(c4)

            hook_label = Text(
                "Rectangular classroom table",
                font="Poppins", font_size=22, color=PURPLE,
            ).next_to(table, DOWN, buff=0.5)

            self.play(Create(table), run_time=1.0)
            self.play(FadeIn(chairs), FadeIn(hook_label), run_time=0.8)

            # 1c — Question mark
            self.wait_until_bookmark("bk_hook_q")
            q_mark = Text(
                "?", font="Poppins", font_size=48,
                color=ORANGE_HL, weight=BOLD,
            ).move_to(table.get_center())
            self.play(FadeIn(q_mark), run_time=0.6)
            self.play(Indicate(q_mark, color=ORANGE_HL, scale_factor=1.3), run_time=0.6)

        # Clear Segment 1
        fade_out_all(self, table, chairs, hook_label, q_mark)

        # ============================================================
        # SEGMENT 2 — CONCEPT
        # ============================================================
        with self.voiceover(
            text=(
                '<bookmark mark="bk_concept_def"/>The perimeter — is the total length around a shape. '
                '<bookmark mark="bk_rect_formula"/>For a rectangle, the perimeter equals, '
                'two times the sum of length and width. '
                '<bookmark mark="bk_sq_formula"/>For a square, the perimeter equals, '
                'four times the length of one side. '
                '<bookmark mark="bk_rearrange"/>So if we know the perimeter, and one dimension, — '
                'we can rearrange the formula, and find the missing one. '
                '<bookmark mark="bk_tool"/>This means perimeter is not just for measuring — '
                'it is also a tool to work backwards.'
            )
        ) as tracker:

            badge_concept = create_heading_badge("Concept")
            self.play(FadeIn(badge_concept), run_time=0.6)

            # 2a — Definition
            self.wait_until_bookmark("bk_concept_def")
            def_p1 = Text("Perimeter", font="Poppins", font_size=30,
                          color=ORANGE_HL, weight=BOLD)
            def_p2 = Text("= total length around a shape",
                          font="Poppins", font_size=28, color=PURPLE)
            def_line = VGroup(def_p1, def_p2).arrange(RIGHT, buff=0.2)
            def_line.move_to(UP * 1.8)
            self.play(FadeIn(def_line), run_time=0.8)

            # 2b–2c — Rectangle formula
            self.wait_until_bookmark("bk_rect_formula")
            self.play(def_line.animate.set_opacity(0.35), run_time=0.4)
            rect_shape = Rectangle(
                width=3.2, height=1.6,
                color=PURPLE, stroke_width=2.5, fill_opacity=0,
            ).move_to(ORIGIN + UP * 0.4)
            rect_label_top = Text(
                "l", font="Poppins", font_size=22, color=PURPLE,
            ).next_to(rect_shape, UP, buff=0.15)
            rect_label_side = Text(
                "w", font="Poppins", font_size=22, color=PURPLE,
            ).next_to(rect_shape, RIGHT, buff=0.15)
            self.play(Create(rect_shape), run_time=1.0)
            self.play(FadeIn(rect_label_top), FadeIn(rect_label_side), run_time=0.6)

            rect_formula = math_obj(r"P = 2(l + w)", font_size=36)
            rect_formula.next_to(rect_shape, DOWN, buff=0.45)
            self.play(FadeIn(rect_formula), run_time=0.8)
            self.play(Indicate(rect_formula, color=ORANGE_HL, scale_factor=1.1),
                      run_time=0.6)

            # 2d–2e — Square formula
            self.wait_until_bookmark("bk_sq_formula")
            self.play(
                FadeOut(rect_shape), FadeOut(rect_label_top),
                FadeOut(rect_label_side), FadeOut(rect_formula),
                run_time=0.7,
            )
            sq_shape = Square(
                side_length=2.0,
                color=PURPLE, stroke_width=2.5, fill_opacity=0,
            ).move_to(ORIGIN + UP * 0.4)
            sq_label = Text(
                "s", font="Poppins", font_size=22, color=PURPLE,
            ).next_to(sq_shape, DOWN, buff=0.15)
            self.play(Create(sq_shape), run_time=1.0)
            self.play(FadeIn(sq_label), run_time=0.5)

            sq_formula = math_obj(r"P = 4s", font_size=36)
            sq_formula.next_to(sq_shape, DOWN, buff=0.5)
            self.play(FadeIn(sq_formula), run_time=0.8)
            self.play(Indicate(sq_formula, color=ORANGE_HL, scale_factor=1.1),
                      run_time=0.6)

            # 2f — Rearrange concept
            self.wait_until_bookmark("bk_rearrange")
            self.play(
                FadeOut(sq_shape), FadeOut(sq_label), FadeOut(sq_formula),
                run_time=0.7,
            )
            rearr_p1 = Text("P + one dimension", font="Poppins",
                            font_size=26, color=PURPLE)
            rearr_arr = math_obj(r"\rightarrow", font_size=26)
            rearr_p2 = Text("missing dimension", font="Poppins",
                            font_size=26, color=ORANGE_HL, weight=BOLD)
            rearr_line = VGroup(rearr_p1, rearr_arr, rearr_p2).arrange(RIGHT, buff=0.2)
            rearr_line.move_to(ORIGIN + UP * 0.3)
            self.play(FadeIn(rearr_line), run_time=0.8)

            # 2g — Tool to work backwards
            self.wait_until_bookmark("bk_tool")
            tool_text = Text(
                "Work backwards!",
                font="Poppins", font_size=30,
                color=ORANGE_HL, weight=BOLD,
            ).next_to(rearr_line, DOWN, buff=0.5)
            self.play(FadeIn(tool_text), run_time=0.7)
            self.play(Flash(tool_text, color=ORANGE_HL, flash_radius=1.2),
                      run_time=0.6)

        # Clear Segment 2
        fade_out_all(self, badge_concept, def_line, rearr_line, tool_text)

        # ============================================================
        # SEGMENT 3 — WHY IT WORKS
        # ============================================================
        with self.voiceover(
            text=(
                '<bookmark mark="bk_why"/>Now, why does this work? '
                '<bookmark mark="bk_two_lengths"/>A rectangle has two equal lengths, and two equal widths. '
                '<bookmark mark="bk_algebra"/>So once we know the perimeter, and one of them, — '
                'simple algebra gives us the other. '
                '<bookmark mark="bk_four_sides"/>A square has four equal sides, — '
                'so its side is simply, the perimeter divided by four.'
            )
        ) as tracker:

            badge_why = create_heading_badge("Why It Works")
            self.play(FadeIn(badge_why), run_time=0.6)

            # 3a — Question framing
            self.wait_until_bookmark("bk_why")
            why_q = Text(
                "Why does this work?",
                font="Poppins", font_size=30, color=PURPLE,
            ).move_to(UP * 2.2)
            self.play(FadeIn(why_q), run_time=0.7)

            # 3b — Rectangle two pairs
            self.wait_until_bookmark("bk_two_lengths")
            self.play(why_q.animate.set_opacity(0.35), run_time=0.4)

            why_rect = Rectangle(
                width=3.4, height=1.8,
                color=PURPLE, stroke_width=2.5, fill_opacity=0,
            ).move_to(ORIGIN + UP * 0.2)

            # Four side arrows + labels
            top_arr = DoubleArrow(
                start=why_rect.get_corner(UL) + LEFT * 0.05,
                end=why_rect.get_corner(UR) + RIGHT * 0.05,
                color=PURPLE, stroke_width=2, tip_length=0.18, buff=0,
            ).shift(UP * 0.32)
            top_lbl = Text("l", font="Poppins", font_size=22, color=PURPLE)
            top_lbl.next_to(top_arr, UP, buff=0.12)

            bot_arr = DoubleArrow(
                start=why_rect.get_corner(DL) + LEFT * 0.05,
                end=why_rect.get_corner(DR) + RIGHT * 0.05,
                color=PURPLE, stroke_width=2, tip_length=0.18, buff=0,
            ).shift(DOWN * 0.32)
            bot_lbl = Text("l", font="Poppins", font_size=22, color=PURPLE)
            bot_lbl.next_to(bot_arr, DOWN, buff=0.12)

            lft_arr = DoubleArrow(
                start=why_rect.get_corner(DL) + DOWN * 0.05,
                end=why_rect.get_corner(UL) + UP * 0.05,
                color=PURPLE, stroke_width=2, tip_length=0.18, buff=0,
            ).shift(LEFT * 0.32)
            lft_lbl = Text("w", font="Poppins", font_size=22, color=PURPLE)
            lft_lbl.next_to(lft_arr, LEFT, buff=0.12)

            rgt_arr = DoubleArrow(
                start=why_rect.get_corner(DR) + DOWN * 0.05,
                end=why_rect.get_corner(UR) + UP * 0.05,
                color=PURPLE, stroke_width=2, tip_length=0.18, buff=0,
            ).shift(RIGHT * 0.32)
            rgt_lbl = Text("w", font="Poppins", font_size=22, color=PURPLE)
            rgt_lbl.next_to(rgt_arr, RIGHT, buff=0.12)

            self.play(Create(why_rect), run_time=1.0)
            self.play(
                Create(top_arr), FadeIn(top_lbl),
                Create(bot_arr), FadeIn(bot_lbl),
                run_time=0.8,
            )
            self.play(
                Create(lft_arr), FadeIn(lft_lbl),
                Create(rgt_arr), FadeIn(rgt_lbl),
                run_time=0.8,
            )

            # 3c — Algebra note
            self.wait_until_bookmark("bk_algebra")
            self.play(
                top_arr.animate.set_color(ORANGE_HL),
                top_lbl.animate.set_color(ORANGE_HL),
                lft_arr.animate.set_color(ORANGE_HL),
                lft_lbl.animate.set_color(ORANGE_HL),
                run_time=0.5,
            )
            alg_note = Text(
                "Simple algebra gives the other dimension.",
                font="Poppins", font_size=24, color=PURPLE,
            ).next_to(why_rect, DOWN, buff=0.45)
            self.play(FadeIn(alg_note), run_time=0.7)
            self.play(
                top_arr.animate.set_color(PURPLE),
                top_lbl.animate.set_color(PURPLE),
                lft_arr.animate.set_color(PURPLE),
                lft_lbl.animate.set_color(PURPLE),
                run_time=0.4,
            )

            # 3d — Square: 4 equal sides
            self.wait_until_bookmark("bk_four_sides")
            self.play(
                FadeOut(why_rect),
                FadeOut(top_arr), FadeOut(top_lbl),
                FadeOut(bot_arr), FadeOut(bot_lbl),
                FadeOut(lft_arr), FadeOut(lft_lbl),
                FadeOut(rgt_arr), FadeOut(rgt_lbl),
                FadeOut(alg_note),
                run_time=0.7,
            )

            why_sq = Square(
                side_length=2.2,
                color=PURPLE, stroke_width=2.5, fill_opacity=0,
            ).move_to(ORIGIN + UP * 0.3)
            sq_s_labels = VGroup(
                Text("s", font="Poppins", font_size=22, color=PURPLE).next_to(why_sq, UP, buff=0.15),
                Text("s", font="Poppins", font_size=22, color=PURPLE).next_to(why_sq, DOWN, buff=0.15),
                Text("s", font="Poppins", font_size=22, color=PURPLE).next_to(why_sq, LEFT, buff=0.15),
                Text("s", font="Poppins", font_size=22, color=PURPLE).next_to(why_sq, RIGHT, buff=0.15),
            )
            self.play(Create(why_sq), run_time=1.0)
            self.play(FadeIn(sq_s_labels), run_time=0.6)

            sq_div = math_obj(r"s = \dfrac{P}{4}", font_size=36)
            sq_div.next_to(why_sq, DOWN, buff=0.5)
            self.play(FadeIn(sq_div), run_time=0.8)
            self.play(Indicate(sq_div, color=ORANGE_HL, scale_factor=1.12),
                      run_time=0.6)

        # Clear Segment 3
        fade_out_all(self, badge_why, why_q, why_sq, sq_s_labels, sq_div)

        # ============================================================
        # SEGMENT 4 — QUESTION
        # ============================================================
        with self.voiceover(
            text=(
                '<bookmark mark="bk_q1_start"/>Part one — the perimeter of a rectangular notebook, '
                'is thirty four centimetres. '
                '<bookmark mark="bk_q1_length"/>Its length is, eleven centimetres. '
                '<bookmark mark="bk_q1_find"/>Find its width, and check whether two such notebooks '
                'would fit along a twenty four centimetre shelf. '
                '<bookmark mark="bk_q2_start"/>Part two — a square tile has a perimeter of forty eight centimetres. '
                '<bookmark mark="bk_q2_find"/>Find the length of one side.'
            )
        ) as tracker:

            badge_q = create_heading_badge("Question")
            self.play(FadeIn(badge_q), run_time=0.6)

            # ── PART 1 ──────────────────────────────────────────────
            self.wait_until_bookmark("bk_q1_start")

            # Part 1 sub-label
            part1_label = Text(
                "Part 1", font="Poppins", font_size=26,
                color=PURPLE, weight=BOLD,
            ).move_to(UP * 2.6 + LEFT * 0.5)

            p1_perim_t = Text("P =", font="Poppins", font_size=26, color=PURPLE)
            p1_perim_v = math_obj(r"34 \text{ cm}", font_size=26, color=ORANGE_HL)
            p1_perim = VGroup(p1_perim_t, p1_perim_v).arrange(RIGHT, buff=0.15)
            p1_perim.next_to(part1_label, RIGHT, buff=0.4)

            self.play(FadeIn(part1_label), FadeIn(p1_perim), run_time=0.7)

            # Rectangle figure (right of center)
            q1_rect = Rectangle(
                width=3.2, height=1.7,
                color=PURPLE, stroke_width=2.5, fill_opacity=0,
            ).move_to(RIGHT * 2.2 + DOWN * 0.2)
            self.play(Create(q1_rect), run_time=1.0)

            # Length arrow + label (below)
            self.wait_until_bookmark("bk_q1_length")
            len_arrow = DoubleArrow(
                start=q1_rect.get_corner(DL) + DOWN * 0.32,
                end=q1_rect.get_corner(DR) + DOWN * 0.32,
                color=PURPLE, stroke_width=2, tip_length=0.2, buff=0,
            )
            len_label = Text("11 cm", font="Poppins", font_size=22, color=PURPLE)
            len_label.next_to(len_arrow, DOWN, buff=0.15)
            self.play(Create(len_arrow), FadeIn(len_label), run_time=0.8)

            # Width arrow + "?" (right side)
            self.wait_until_bookmark("bk_q1_find")
            wid_arrow = DoubleArrow(
                start=q1_rect.get_corner(DR) + RIGHT * 0.32,
                end=q1_rect.get_corner(UR) + RIGHT * 0.32,
                color=PURPLE, stroke_width=2, tip_length=0.2, buff=0,
            )
            wid_q = Text("?", font="Poppins", font_size=36,
                         color=ORANGE_HL, weight=BOLD)
            wid_q.next_to(wid_arrow, RIGHT, buff=0.2)
            self.play(Create(wid_arrow), FadeIn(wid_q), run_time=0.8)
            self.play(Indicate(wid_q, color=ORANGE_HL, scale_factor=1.3),
                      run_time=0.5)

            # Shelf line (below, left area)
            shelf_line = Line(
                start=LEFT * 3.6 + DOWN * 1.9,
                end=LEFT * 0.2 + DOWN * 1.9,
                color=PURPLE, stroke_width=3,
            )
            shelf_label_t = Text("24 cm shelf", font="Poppins",
                                 font_size=20, color=PURPLE)
            shelf_label_t.next_to(shelf_line, DOWN, buff=0.15)
            self.play(Create(shelf_line), FadeIn(shelf_label_t), run_time=0.8)

            # ── PART 2 ──────────────────────────────────────────────
            self.wait_until_bookmark("bk_q2_start")
            # FadeOut Part 1 visuals cleanly
            self.play(
                FadeOut(part1_label), FadeOut(p1_perim),
                FadeOut(q1_rect), FadeOut(len_arrow), FadeOut(len_label),
                FadeOut(wid_arrow), FadeOut(wid_q),
                FadeOut(shelf_line), FadeOut(shelf_label_t),
                run_time=0.8,
            )

            part2_label = Text(
                "Part 2", font="Poppins", font_size=26,
                color=PURPLE, weight=BOLD,
            ).move_to(UP * 2.6 + LEFT * 0.5)

            p2_perim_t = Text("P =", font="Poppins", font_size=26, color=PURPLE)
            p2_perim_v = math_obj(r"48 \text{ cm}", font_size=26, color=ORANGE_HL)
            p2_perim = VGroup(p2_perim_t, p2_perim_v).arrange(RIGHT, buff=0.15)
            p2_perim.next_to(part2_label, RIGHT, buff=0.4)

            self.play(FadeIn(part2_label), FadeIn(p2_perim), run_time=0.7)

            q2_sq = Square(
                side_length=2.4,
                color=PURPLE, stroke_width=2.5, fill_opacity=0,
            ).move_to(ORIGIN + DOWN * 0.2)
            self.play(Create(q2_sq), run_time=1.0)

            # Side arrow + "?"
            self.wait_until_bookmark("bk_q2_find")
            sq_side_arrow = DoubleArrow(
                start=q2_sq.get_corner(DR) + RIGHT * 0.32,
                end=q2_sq.get_corner(UR) + RIGHT * 0.32,
                color=PURPLE, stroke_width=2, tip_length=0.2, buff=0,
            )
            sq_side_q = Text("?", font="Poppins", font_size=36,
                             color=ORANGE_HL, weight=BOLD)
            sq_side_q.next_to(sq_side_arrow, RIGHT, buff=0.2)
            self.play(Create(sq_side_arrow), FadeIn(sq_side_q), run_time=0.8)
            self.play(Indicate(sq_side_q, color=ORANGE_HL, scale_factor=1.3),
                      run_time=0.5)

        # Store Part 2 figure for solution reuse (shift to right later)
        q2_fig_group = VGroup(q2_sq, sq_side_arrow, sq_side_q)

        # Clear Q badge and Part 2 labels (keep q2_fig_group for solution)
        self.play(
            FadeOut(badge_q),
            FadeOut(part2_label), FadeOut(p2_perim),
            run_time=0.7,
        )

        # ============================================================
        # SEGMENT 5 — SOLUTION
        # ============================================================
        with self.voiceover(
            text=(
                '<bookmark mark="bk_notebook_label"/>For the notebook... '
                '<bookmark mark="bk_sol_formula"/>Two times the sum of length and width, equals the perimeter. '
                '<bookmark mark="bk_sol_sub"/>Two times, eleven plus, width, equals thirty four. '
                '<bookmark mark="bk_sol_step2"/>Eleven plus, width, equals seventeen. '
                '<bookmark mark="bk_sol_width"/>So, width equals — six centimetres. '
                '<bookmark mark="bk_sol_shelf"/>Two notebooks placed side by side, would need twelve centimetres, — '
                'which fits well on the shelf. '
                '<bookmark mark="bk_tile_label"/>For the tile... '
                '<bookmark mark="bk_tile_formula"/>The perimeter equals, four times the side. '
                '<bookmark mark="bk_tile_sub"/>Four times the side, equals forty eight. '
                '<bookmark mark="bk_tile_side"/>So the side equals — twelve centimetres.'
            )
        ) as tracker:

            badge_sol = create_heading_badge("Solution")
            self.play(FadeIn(badge_sol), run_time=0.6)

            # ── NOTEBOOK SOLUTION ────────────────────────────────────

            self.wait_until_bookmark("bk_notebook_label")

            # Fade out Part 2 question figure — we're doing notebook first
            self.play(FadeOut(q2_fig_group), run_time=0.6)

            nb_label = Text(
                "For the notebook:",
                font="Poppins", font_size=26, color=PURPLE, weight=BOLD,
            ).move_to(UP * 2.6 + LEFT * 2.2)
            self.play(FadeIn(nb_label), run_time=0.6)

            # Rebuild notebook figure on RIGHT (persistent)
            nb_rect = Rectangle(
                width=2.6, height=1.4,
                color=PURPLE, stroke_width=2.5, fill_opacity=0,
            ).move_to(RIGHT * 3.2 + DOWN * 0.2)
            nb_len_arr = DoubleArrow(
                start=nb_rect.get_corner(DL) + DOWN * 0.28,
                end=nb_rect.get_corner(DR) + DOWN * 0.28,
                color=PURPLE, stroke_width=2, tip_length=0.18, buff=0,
            )
            nb_len_lbl = Text("11 cm", font="Poppins", font_size=20, color=PURPLE)
            nb_len_lbl.next_to(nb_len_arr, DOWN, buff=0.12)
            nb_wid_arr = DoubleArrow(
                start=nb_rect.get_corner(DR) + RIGHT * 0.28,
                end=nb_rect.get_corner(UR) + RIGHT * 0.28,
                color=PURPLE, stroke_width=2, tip_length=0.18, buff=0,
            )
            nb_wid_q = Text("?", font="Poppins", font_size=30,
                            color=ORANGE_HL, weight=BOLD)
            nb_wid_q.next_to(nb_wid_arr, RIGHT, buff=0.18)

            self.play(
                Create(nb_rect),
                Create(nb_len_arr), FadeIn(nb_len_lbl),
                Create(nb_wid_arr), FadeIn(nb_wid_q),
                run_time=1.0,
            )

            # Step 1 — base formula
            LEFT_COL = LEFT * 3.4
            STEP_Y_START = UP * 1.6
            STEP_BUFF = 0.72

            self.wait_until_bookmark("bk_sol_formula")
            n_s1 = math_obj(r"2(l + w) = P", font_size=30)
            n_s1.move_to(LEFT_COL + STEP_Y_START)
            n_s1.align_to(LEFT_COL, LEFT)
            self.play(FadeIn(n_s1), run_time=0.7)

            # Step 2 — substitute
            self.wait_until_bookmark("bk_sol_sub")
            self.play(n_s1.animate.set_opacity(0.35), run_time=0.4)
            n_s2 = math_obj(r"2(11 + w) = 34", font_size=30)
            n_s2.next_to(n_s1, DOWN, buff=STEP_BUFF)
            n_s2.align_to(n_s1, LEFT)
            self.play(FadeIn(n_s2), run_time=0.7)
            self.play(
                nb_rect.animate.set_color(ORANGE_HL),
                nb_len_lbl.animate.set_color(ORANGE_HL),
                run_time=0.4,
            )
            self.play(
                nb_rect.animate.set_color(PURPLE),
                nb_len_lbl.animate.set_color(PURPLE),
                run_time=0.4,
            )

            # Step 3 — simplify
            self.wait_until_bookmark("bk_sol_step2")
            self.play(n_s2.animate.set_opacity(0.35), run_time=0.4)
            n_s3 = math_obj(r"11 + w = 17", font_size=30)
            n_s3.next_to(n_s2, DOWN, buff=STEP_BUFF)
            n_s3.align_to(n_s1, LEFT)
            self.play(FadeIn(n_s3), run_time=0.7)

            # Step 4 — answer
            self.wait_until_bookmark("bk_sol_width")
            self.play(n_s3.animate.set_opacity(0.35), run_time=0.4)
            n_s4 = math_obj(r"w = 6 \text{ cm}", font_size=32,
                            color=ORANGE_HL)
            n_s4.next_to(n_s3, DOWN, buff=STEP_BUFF)
            n_s4.align_to(n_s1, LEFT)
            self.play(FadeIn(n_s4), run_time=0.7)
            self.play(Flash(n_s4, color=ORANGE_HL, flash_radius=1.0),
                      run_time=0.6)
            # Replace ? with 6 cm on figure
            nb_wid_ans = Text("6 cm", font="Poppins", font_size=24,
                              color=ORANGE_HL, weight=BOLD)
            nb_wid_ans.next_to(nb_wid_arr, RIGHT, buff=0.18)
            self.play(
                ReplacementTransform(nb_wid_q, nb_wid_ans),
                run_time=0.8,
            )
            self.wait(0.3)

            # Step 5 — shelf check
            self.wait_until_bookmark("bk_sol_shelf")
            self.play(n_s4.animate.set_opacity(0.35), run_time=0.4)

            shelf_check_t = Text("2 notebooks =", font="Poppins",
                                 font_size=24, color=PURPLE)
            shelf_check_v = math_obj(r"12 \text{ cm} < 24 \text{ cm}", font_size=26)
            shelf_tick = Text("Fits!", font="Poppins", font_size=26,
                              color=ORANGE_HL, weight=BOLD)
            shelf_row = VGroup(shelf_check_t, shelf_check_v, shelf_tick).arrange(
                RIGHT, buff=0.2
            )
            shelf_row.next_to(n_s4, DOWN, buff=0.5)
            shelf_row.align_to(n_s1, LEFT)
            self.play(FadeIn(shelf_row), run_time=0.8)
            self.play(Indicate(shelf_tick, color=ORANGE_HL, scale_factor=1.2),
                      run_time=0.5)

            # ── TILE SOLUTION ────────────────────────────────────────

            self.wait_until_bookmark("bk_tile_label")
            # Clear notebook solution cleanly
            self.play(
                FadeOut(nb_label),
                FadeOut(n_s1), FadeOut(n_s2), FadeOut(n_s3),
                FadeOut(n_s4), FadeOut(shelf_row),
                FadeOut(nb_rect), FadeOut(nb_len_arr), FadeOut(nb_len_lbl),
                FadeOut(nb_wid_arr), FadeOut(nb_wid_ans),
                run_time=0.8,
            )

            tile_label = Text(
                "For the tile:",
                font="Poppins", font_size=26, color=PURPLE, weight=BOLD,
            ).move_to(UP * 2.6 + LEFT * 2.2)
            self.play(FadeIn(tile_label), run_time=0.6)

            # Tile figure on RIGHT
            tile_sq = Square(
                side_length=2.2,
                color=PURPLE, stroke_width=2.5, fill_opacity=0,
            ).move_to(RIGHT * 3.2 + DOWN * 0.2)
            tile_side_arr = DoubleArrow(
                start=tile_sq.get_corner(DR) + RIGHT * 0.28,
                end=tile_sq.get_corner(UR) + RIGHT * 0.28,
                color=PURPLE, stroke_width=2, tip_length=0.18, buff=0,
            )
            tile_side_q = Text("?", font="Poppins", font_size=30,
                               color=ORANGE_HL, weight=BOLD)
            tile_side_q.next_to(tile_side_arr, RIGHT, buff=0.18)
            tile_p_lbl_t = Text("P =", font="Poppins", font_size=20, color=PURPLE)
            tile_p_lbl_v = math_obj(r"48 \text{ cm}", font_size=20, color=ORANGE_HL)
            tile_p_lbl = VGroup(tile_p_lbl_t, tile_p_lbl_v).arrange(RIGHT, buff=0.1)
            tile_p_lbl.next_to(tile_sq, UP, buff=0.2)

            self.play(
                Create(tile_sq),
                FadeIn(tile_p_lbl),
                Create(tile_side_arr), FadeIn(tile_side_q),
                run_time=1.0,
            )

            TILE_Y_START = UP * 1.6

            # Tile step 1
            self.wait_until_bookmark("bk_tile_formula")
            t_s1 = math_obj(r"P = 4s", font_size=30)
            t_s1.move_to(LEFT_COL + TILE_Y_START)
            t_s1.align_to(LEFT_COL, LEFT)
            self.play(FadeIn(t_s1), run_time=0.7)

            # Tile step 2
            self.wait_until_bookmark("bk_tile_sub")
            self.play(t_s1.animate.set_opacity(0.35), run_time=0.4)
            t_s2 = math_obj(r"4s = 48", font_size=30)
            t_s2.next_to(t_s1, DOWN, buff=STEP_BUFF)
            t_s2.align_to(t_s1, LEFT)
            self.play(FadeIn(t_s2), run_time=0.7)

            # Tile step 3 — answer
            self.wait_until_bookmark("bk_tile_side")
            self.play(t_s2.animate.set_opacity(0.35), run_time=0.4)
            t_s3 = math_obj(r"s = 12 \text{ cm}", font_size=32,
                            color=ORANGE_HL)
            t_s3.next_to(t_s2, DOWN, buff=STEP_BUFF)
            t_s3.align_to(t_s1, LEFT)
            self.play(FadeIn(t_s3), run_time=0.7)
            self.play(Flash(t_s3, color=ORANGE_HL, flash_radius=1.0),
                      run_time=0.6)
            # Replace ? with 12 cm on figure
            tile_side_ans = Text("12 cm", font="Poppins", font_size=24,
                                 color=ORANGE_HL, weight=BOLD)
            tile_side_ans.next_to(tile_side_arr, RIGHT, buff=0.18)
            self.play(
                ReplacementTransform(tile_side_q, tile_side_ans),
                run_time=0.8,
            )
            self.wait(0.6)

        # Clear Segment 5
        fade_out_all(
            self,
            badge_sol, tile_label,
            t_s1, t_s2, t_s3,
            tile_sq, tile_side_arr, tile_side_ans, tile_p_lbl,
        )

        # ============================================================
        # SEGMENT 6 — REAL-LIFE CONNECTION
        # ============================================================
        with self.voiceover(
            text=(
                '<bookmark mark="bk_reallife"/>This is the same idea builders use, '
                'when calculating tile sizes for a floor.'
            )
        ) as tracker:

            badge_rl = create_heading_badge("Real-Life Connection")
            self.play(FadeIn(badge_rl), run_time=0.6)

            self.wait_until_bookmark("bk_reallife")

            # Floor tile grid — 4×3 small squares
            tile_grid = VGroup()
            tile_w = 0.65
            for row in range(3):
                for col in range(4):
                    sq = Square(
                        side_length=tile_w,
                        color=PURPLE, stroke_width=1.5,
                        fill_opacity=0.08, fill_color=PURPLE,
                    ).move_to(
                        ORIGIN
                        + RIGHT * (col - 1.5) * tile_w
                        + DOWN * (row - 1.0) * tile_w
                    )
                    tile_grid.add(sq)

            tile_grid.move_to(ORIGIN + DOWN * 0.2)
            self.play(Create(tile_grid), run_time=1.2)

            rl_text = Text(
                "Builders use this to calculate tile sizes for floors.",
                font="Poppins", font_size=26, color=PURPLE,
            ).next_to(tile_grid, DOWN, buff=0.45)
            self.play(FadeIn(rl_text), run_time=0.7)

        fade_out_all(self, badge_rl, tile_grid, rl_text)

        # ============================================================
        # SEGMENT 7 — SUMMARY
        # ============================================================
        with self.voiceover(
            text=(
                '<bookmark mark="bk_sum1"/>Perimeter formulas can be rearranged, '
                'to find missing dimensions. '
                '<bookmark mark="bk_sum2"/>Rectangle — perimeter is, '
                'two times the sum of length and width. '
                '<bookmark mark="bk_sum3"/>Square — side is, '
                'the perimeter divided by four.'
            )
        ) as tracker:

            badge_sum = create_heading_badge("Summary")
            self.play(FadeIn(badge_sum), run_time=0.6)

            # Bullet 1
            self.wait_until_bookmark("bk_sum1")
            dot1 = Text("*", font="Poppins", font_size=28, color=PURPLE)
            bul1 = Text(
                "Perimeter formulas can be rearranged to find missing dimensions.",
                font="Poppins", font_size=24, color=PURPLE,
            )
            b1 = VGroup(dot1, bul1).arrange(RIGHT, buff=0.2)
            b1.move_to(UP * 1.2)
            self.play(FadeIn(b1), run_time=0.8)

            # Bullet 2
            self.wait_until_bookmark("bk_sum2")
            dot2 = Text("*", font="Poppins", font_size=28, color=PURPLE)
            bul2_t = Text(
                "Rectangle:", font="Poppins", font_size=24, color=PURPLE,
            )
            bul2_f = math_obj(r"P = 2(l + w)", font_size=28)
            bul2_line = VGroup(bul2_t, bul2_f).arrange(RIGHT, buff=0.2)
            b2 = VGroup(dot2, bul2_line).arrange(RIGHT, buff=0.2)
            b2.next_to(b1, DOWN, buff=0.5)
            self.play(FadeIn(b2), run_time=0.8)

            # Bullet 3
            self.wait_until_bookmark("bk_sum3")
            dot3 = Text("*", font="Poppins", font_size=28, color=PURPLE)
            bul3_t = Text(
                "Square:", font="Poppins", font_size=24, color=PURPLE,
            )
            bul3_f = math_obj(r"s = P \div 4", font_size=28)
            bul3_line = VGroup(bul3_t, bul3_f).arrange(RIGHT, buff=0.2)
            b3 = VGroup(dot3, bul3_line).arrange(RIGHT, buff=0.2)
            b3.next_to(b2, DOWN, buff=0.5)
            self.play(FadeIn(b3), run_time=0.8)
            self.wait(0.6)

        fade_out_all(self, badge_sum, b1, b2, b3)