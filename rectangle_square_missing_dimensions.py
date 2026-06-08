import os
import urllib.request
import atexit
import manimpango
from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.openai import OpenAIService

LAVENDER_BG = "#E7E5F3"
PURPLE = "#7464CE"
ORANGE_HL = "#FF9302"
PALE_PURPLE = "#9495D7"
WHITE = "#FFFFFF"


def _setup_poppins():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    fonts_dir = os.path.join(base_dir, ".fonts")
    os.makedirs(fonts_dir, exist_ok=True)
    base_url = "https://raw.githubusercontent.com/google/fonts/main/ofl/poppins/"
    fonts = {
        "Poppins-Regular.ttf": base_url + "Poppins-Regular.ttf",
        "Poppins-Bold.ttf": base_url + "Poppins-Bold.ttf",
        "Poppins-Italic.ttf": base_url + "Poppins-Italic.ttf",
        "Poppins-SemiBold.ttf": base_url + "Poppins-SemiBold.ttf",
    }
    for fname, url in fonts.items():
        path = os.path.join(fonts_dir, fname)
        if not os.path.exists(path):
            try:
                print(f"Downloading {fname}")
                urllib.request.urlretrieve(url, path)
            except Exception as e:
                print(f"Could not download {fname}: {e}")
                continue
        try:
            manimpango.register_font(path)
        except Exception:
            pass
    print("Poppins setup complete.")


_setup_poppins()

import manim_voiceover.tracker as _vt

_orig_time_until_bookmark = _vt.VoiceoverTracker.time_until_bookmark
_FAILED_BOOKMARKS = []


def _safe_time_until_bookmark(self, mark, buff=0.0, limit=None):
    try:
        return _orig_time_until_bookmark(self, mark, buff, limit)
    except Exception:
        scene_text = getattr(self, "data", {}).get("input_text", "unknown")[:80]
        _FAILED_BOOKMARKS.append((mark, scene_text))
        print(f"WARNING  Bookmark '{mark}' NOT FOUND in: {scene_text}...")
        return 0.0


_vt.VoiceoverTracker.time_until_bookmark = _safe_time_until_bookmark


def _report():
    if _FAILED_BOOKMARKS:
        print("\n" + "=" * 60)
        print(f"FAILED BOOKMARKS SUMMARY ({len(_FAILED_BOOKMARKS)} total):")
        print("=" * 60)
        for mark, text in _FAILED_BOOKMARKS:
            print(f"FAILED: {mark} -> {text}")
        print("=" * 60)


atexit.register(_report)


def _make_cosec_template():
    base = TexFontTemplates.gnu_freesans_tx
    t = TexTemplate(
        tex_compiler=base.tex_compiler,
        output_format=base.output_format,
        preamble=base.preamble,
        placeholder_text=base.placeholder_text,
    )
    t.add_to_preamble(r"\DeclareMathOperator{\cosec}{cosec}")
    return t


COSEC_TEMPLATE = _make_cosec_template()


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


def safe_text(text, font_size=26, color=PURPLE, weight=NORMAL):
    return Text(text, font="Poppins", font_size=font_size, color=color, weight=weight)


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


def create_dimension(start, end, label_str, direction=DOWN):
    arrow = DoubleArrow(
        start=start,
        end=end,
        color=PURPLE,
        stroke_width=2,
        tip_length=0.2,
        buff=0,
    )
    label = Text(label_str, font="Poppins", font_size=22, color=PURPLE)
    label.next_to(arrow, direction, buff=0.15)
    return VGroup(arrow, label)


def create_unknown(position):
    return Text(
        "?",
        font="Poppins",
        font_size=36,
        color=ORANGE_HL,
        weight=BOLD,
    ).move_to(position)


def justified_block(lines, font_size=22, color=PURPLE, width=11.8, line_buff=0.15):
    rendered = VGroup()
    for line in lines:
        rendered.add(safe_text(line, font_size=font_size, color=color))
    rendered.arrange(DOWN, aligned_edge=LEFT, buff=line_buff)
    if rendered.width > width:
        rendered.scale_to_fit_width(width)
    return rendered


class PerimeterAreaMissingDimensions(VoiceoverScene):
    def construct(self):
        self.camera.background_color = LAVENDER_BG

        TTS_INSTRUCTIONS = """
Voice & Personality:
You are a warm, patient, and encouraging mathematics teacher speaking
to a middle-school student. Your tone is friendly, calm, and confident
- never rushed, never robotic. The voice profile is shimmer.

Pacing:
Speak at a MODERATE-TO-SLOW pace. Honor commas, dashes, and ellipses.

Variables and Math Terms:
When pronouncing single-letter variables, slow down and articulate clearly.

Formulas:
Slow down further on equations. Pause between each component.

Numbers and Units:
Pronounce numbers clearly.

Do NOT:
- Do not race through sentences.
- Do not improvise or paraphrase.
"""

        self.set_speech_service(
            OpenAIService(
                voice="shimmer",
                model="gpt-4o-mini-tts",
                transcription_model="medium",
                instructions=TTS_INSTRUCTIONS,
            ),
            create_subcaption=False,
        )

        with self.voiceover(
            text='<bookmark mark="bk_1a"/>Hello students! Imagine you are '
            '<bookmark mark="bk_1b"/>arranging chairs around a rectangular classroom table. '
            'You know the <bookmark mark="bk_1c"/>total number of chairs that fit around it, '
            'and you know <bookmark mark="bk_1d"/>how many fit along one side. '
            'Could you figure out <bookmark mark="bk_1e"/>how many fit along the other side without counting again?'
        ):
            self.wait_until_bookmark("bk_1a")
            self.camera.background_color = PURPLE
            title = safe_text("Perimeter and Area", font_size=64, color=WHITE, weight=BOLD)
            subtitle = safe_text("Missing Dimensions", font_size=34, color=WHITE)
            subtitle.next_to(title, DOWN, buff=0.3)
            title_group = VGroup(title, subtitle).move_to(ORIGIN)
            self.play(FadeIn(title_group), run_time=0.8)

            self.wait_until_bookmark("bk_1b")
            self.play(FadeOut(title_group), run_time=0.8)
            self.camera.background_color = LAVENDER_BG

            table = RoundedRectangle(
                corner_radius=0.12,
                width=4.6,
                height=2.1,
                color=PURPLE,
                stroke_width=2.5,
                fill_opacity=0.08,
            ).move_to(ORIGIN)
            self.play(Create(table), run_time=1.0)

            chairs = VGroup()
            for x in [-1.6, -0.8, 0, 0.8, 1.6]:
                chairs.add(Square(0.22, color=PURPLE, fill_color=WHITE, fill_opacity=1).move_to([x, 1.35, 0]))
                chairs.add(Square(0.22, color=PURPLE, fill_color=WHITE, fill_opacity=1).move_to([x, -1.35, 0]))
            for y in [-0.55, 0, 0.55]:
                chairs.add(Square(0.22, color=PURPLE, fill_color=WHITE, fill_opacity=1).move_to([-2.65, y, 0]))
                chairs.add(Square(0.22, color=PURPLE, fill_color=WHITE, fill_opacity=1).move_to([2.65, y, 0]))
            self.play(FadeIn(chairs), run_time=0.8)

            self.wait_until_bookmark("bk_1c")
            perimeter_path = SurroundingRectangle(table, color=ORANGE_HL, buff=0.18, stroke_width=4)
            total_label = safe_text("Total around", font_size=28, color=ORANGE_HL, weight=BOLD).to_edge(UP, buff=0.8)
            self.play(Create(perimeter_path), FadeIn(total_label), run_time=1.0)

            self.wait_until_bookmark("bk_1d")
            one_side = Line(table.get_corner(DL), table.get_corner(DR), color=ORANGE_HL, stroke_width=7)
            side_label = safe_text("One side", font_size=26, color=ORANGE_HL, weight=BOLD)
            side_label.next_to(one_side, DOWN, buff=0.35)
            self.play(Create(one_side), FadeIn(side_label), run_time=0.7)

            self.wait_until_bookmark("bk_1e")
            missing = create_unknown(table.get_right() + RIGHT * 0.7)
            self.play(FadeIn(missing), Indicate(missing, color=ORANGE_HL), run_time=0.7)
            self.play(FadeOut(VGroup(table, chairs, perimeter_path, total_label, one_side, side_label, missing)), run_time=0.9)

        with self.voiceover(
            text='<bookmark mark="bk_2a"/>The perimeter is the total length around a shape. '
            'For a <bookmark mark="bk_2b"/>rectangle, the perimeter equals, two times, the sum of '
            '<bookmark mark="bk_2c"/>length and width. For a <bookmark mark="bk_2d"/>square, '
            'the perimeter equals, four times, the length of one <bookmark mark="bk_2e"/>side. '
            'So if we know the <bookmark mark="bk_2f"/>perimeter and one dimension, we can rearrange the formula, '
            'and find the <bookmark mark="bk_2g"/>missing one. '
            'This means perimeter is not just for measuring - it is also a tool to '
            '<bookmark mark="bk_2h"/>work backwards.'
        ):
            badge = create_heading_badge("Concept")

            self.wait_until_bookmark("bk_2a")
            shape = Polygon(
                LEFT * 1.5 + DOWN,
                RIGHT * 1.5 + DOWN,
                RIGHT * 1.2 + UP,
                LEFT * 1.1 + UP,
                color=PURPLE,
                stroke_width=2.5,
            )
            perimeter = SurroundingRectangle(shape, color=ORANGE_HL, buff=0.12, stroke_width=4)
            per_text = safe_text("Perimeter", font_size=36, color=PURPLE, weight=BOLD).to_edge(UP, buff=0.9)
            self.play(FadeIn(badge), Create(shape), run_time=0.8)
            self.play(Create(perimeter), FadeIn(per_text), run_time=0.8)

            self.wait_until_bookmark("bk_2b")
            self.play(FadeOut(VGroup(shape, perimeter, per_text)), run_time=0.8)
            rect = Rectangle(width=4.1, height=2.0, color=PURPLE, stroke_width=2.5).move_to(RIGHT * 1.1)
            rect_label = safe_text("Rectangle", font_size=30, color=PURPLE, weight=BOLD).next_to(rect, UP, buff=0.3)
            p2 = math_obj(r"P = 2", font_size=40).to_edge(LEFT, buff=1.0).shift(UP * 0.6)
            self.play(Create(rect), FadeIn(rect_label), FadeIn(p2), run_time=1.0)
            top_side = Line(rect.get_corner(UL), rect.get_corner(UR), color=ORANGE_HL, stroke_width=7)
            bottom_side = Line(rect.get_corner(DL), rect.get_corner(DR), color=ORANGE_HL, stroke_width=7)
            self.play(Create(top_side), Create(bottom_side), run_time=0.6)

            self.wait_until_bookmark("bk_2c")
            formula_rect = math_obj(r"P = 2(l + w)", font_size=40).move_to(p2)
            len_lab = safe_text("length", font_size=22, color=ORANGE_HL).next_to(rect, DOWN, buff=0.25)
            wid_lab = safe_text("width", font_size=22, color=ORANGE_HL).next_to(rect, RIGHT, buff=0.25)
            self.play(ReplacementTransform(p2, formula_rect), FadeIn(len_lab), FadeIn(wid_lab), run_time=0.9)
            self.play(FadeOut(VGroup(top_side, bottom_side, len_lab, wid_lab)), run_time=0.6)

            self.wait_until_bookmark("bk_2d")
            self.play(FadeOut(VGroup(rect, rect_label, formula_rect)), run_time=0.8)
            square = Square(side_length=2.3, color=PURPLE, stroke_width=2.5).move_to(RIGHT * 1.0)
            sq_label = safe_text("Square", font_size=30, color=PURPLE, weight=BOLD).next_to(square, UP, buff=0.3)
            p4 = math_obj(r"P = 4", font_size=40).to_edge(LEFT, buff=1.0).shift(UP * 0.5)
            self.play(Create(square), FadeIn(sq_label), FadeIn(p4), run_time=1.0)

            sides = VGroup(
                Line(square.get_corner(UL), square.get_corner(UR), color=ORANGE_HL, stroke_width=7),
                Line(square.get_corner(UR), square.get_corner(DR), color=ORANGE_HL, stroke_width=7),
                Line(square.get_corner(DR), square.get_corner(DL), color=ORANGE_HL, stroke_width=7),
                Line(square.get_corner(DL), square.get_corner(UL), color=ORANGE_HL, stroke_width=7),
            )
            self.play(Create(sides), run_time=0.7)

            self.wait_until_bookmark("bk_2e")
            formula_sq = math_obj(r"P = 4s", font_size=40).move_to(p4)
            side_lab = safe_text("side", font_size=22, color=ORANGE_HL).next_to(square, DOWN, buff=0.25)
            self.play(ReplacementTransform(p4, formula_sq), FadeIn(side_lab), run_time=0.8)

            self.wait_until_bookmark("bk_2f")
            known = safe_text("Known", font_size=30, color=ORANGE_HL, weight=BOLD).to_edge(LEFT, buff=1.0).shift(DOWN * 0.5)
            rearrange = safe_text("Rearrange", font_size=30, color=PURPLE, weight=BOLD).next_to(known, DOWN, buff=0.35)
            self.play(FadeIn(known), FadeIn(rearrange), run_time=0.8)

            self.wait_until_bookmark("bk_2g")
            unknown = create_unknown(square.get_center())
            self.play(FadeIn(unknown), Indicate(unknown, color=ORANGE_HL), run_time=0.7)

            self.wait_until_bookmark("bk_2h")
            back = CurvedArrow(RIGHT * 2.6 + DOWN * 1.6, LEFT * 1.3 + DOWN * 1.6, color=ORANGE_HL, stroke_width=4)
            back_label = safe_text("Work backwards", font_size=30, color=ORANGE_HL, weight=BOLD).next_to(back, DOWN, buff=0.25)
            self.play(Create(back), FadeIn(back_label), run_time=0.8)
            self.play(FadeOut(VGroup(badge, square, sq_label, formula_sq, sides, side_lab, known, rearrange, unknown, back, back_label)), run_time=0.9)

        with self.voiceover(
            text='<bookmark mark="bk_3a"/>Now, why does this work? A rectangle has '
            '<bookmark mark="bk_3b"/>two equal lengths and two equal widths. '
            'So once we know the <bookmark mark="bk_3c"/>perimeter and one of them, '
            'simple algebra gives us the <bookmark mark="bk_3d"/>other. '
            'A square has <bookmark mark="bk_3e"/>four equal sides, so its side is simply the perimeter divided by '
            '<bookmark mark="bk_3f"/>four.'
        ):
            badge = create_heading_badge("Why")

            self.wait_until_bookmark("bk_3a")
            r = Rectangle(width=4, height=2, color=PURPLE, stroke_width=2.5).shift(LEFT * 1.2)
            s = Square(side_length=2, color=PURPLE, stroke_width=2.5).shift(RIGHT * 3)
            why = safe_text("Why?", font_size=42, color=PURPLE, weight=BOLD).to_edge(UP, buff=0.9)
            self.play(FadeIn(badge), FadeIn(why), Create(r), Create(s), run_time=1.0)

            self.wait_until_bookmark("bk_3b")
            len_pair = VGroup(
                Line(r.get_corner(UL), r.get_corner(UR), color=ORANGE_HL, stroke_width=7),
                Line(r.get_corner(DL), r.get_corner(DR), color=ORANGE_HL, stroke_width=7),
            )
            wid_pair = VGroup(
                Line(r.get_corner(UL), r.get_corner(DL), color=ORANGE_HL, stroke_width=7),
                Line(r.get_corner(UR), r.get_corner(DR), color=ORANGE_HL, stroke_width=7),
            )
            eq_len = safe_text("Equal lengths", font_size=26, color=ORANGE_HL, weight=BOLD).next_to(r, DOWN, buff=0.35)
            self.play(Create(len_pair), FadeIn(eq_len), run_time=0.8)
            self.play(FadeOut(eq_len), Create(wid_pair), run_time=0.7)

            self.wait_until_bookmark("bk_3c")
            known_p = safe_text("Perimeter known", font_size=28, color=PURPLE, weight=BOLD).to_edge(LEFT, buff=0.8).shift(UP * 1.3)
            known_d = safe_text("One dimension known", font_size=26, color=ORANGE_HL, weight=BOLD).next_to(known_p, DOWN, buff=0.3)
            self.play(FadeIn(known_p), FadeIn(known_d), run_time=0.8)

            self.wait_until_bookmark("bk_3d")
            other = safe_text("Other dimension", font_size=26, color=ORANGE_HL, weight=BOLD).next_to(known_d, DOWN, buff=0.3)
            self.play(FadeIn(other), run_time=0.6)

            self.wait_until_bookmark("bk_3e")
            square_sides = VGroup(
                Line(s.get_corner(UL), s.get_corner(UR), color=ORANGE_HL, stroke_width=7),
                Line(s.get_corner(UR), s.get_corner(DR), color=ORANGE_HL, stroke_width=7),
                Line(s.get_corner(DR), s.get_corner(DL), color=ORANGE_HL, stroke_width=7),
                Line(s.get_corner(DL), s.get_corner(UL), color=ORANGE_HL, stroke_width=7),
            )
            four = safe_text("Four equal sides", font_size=26, color=ORANGE_HL, weight=BOLD).next_to(s, DOWN, buff=0.35)
            self.play(Create(square_sides), FadeIn(four), run_time=0.8)

            self.wait_until_bookmark("bk_3f")
            div = math_obj(r"s = \dfrac{P}{4}", font_size=42).to_edge(DOWN, buff=0.7)
            self.play(FadeIn(div), run_time=0.7)
            self.play(FadeOut(VGroup(badge, why, r, s, len_pair, wid_pair, known_p, known_d, other, square_sides, four, div)), run_time=0.9)

        with self.voiceover(
            text='<bookmark mark="bk_4a"/>Question: Part one: The perimeter of a '
            '<bookmark mark="bk_4b"/>rectangular notebook is thirty four centimetres. '
            'Its length is <bookmark mark="bk_4c"/>eleven centimetres. '
            'Find its width, and check whether <bookmark mark="bk_4d"/>two such notebooks would fit along a twenty four centimetre shelf. '
            'Part two: A <bookmark mark="bk_4e"/>square tile has a perimeter of forty eight centimetres. '
            'Find the length of one <bookmark mark="bk_4f"/>side.'
        ):
            badge = create_heading_badge("Question")

            self.wait_until_bookmark("bk_4a")
            q1 = justified_block(
                [
                    "Part 1: The perimeter of a rectangular notebook is 34 centimetres.",
                    "Its length is 11 centimetres.",
                    "Find its width and check whether two such notebooks would fit along a",
                    "24-centimetre shelf.",
                ],
                font_size=21,
                width=12.2,
            ).to_edge(UP, buff=0.9)
            self.play(FadeIn(badge), FadeIn(q1), run_time=0.8)

            self.wait_until_bookmark("bk_4b")
            notebook = Rectangle(width=4.4, height=2.2, color=PURPLE, stroke_width=2.5).move_to(DOWN * 0.5)
            per34 = safe_text("P = 34 centimetres", font_size=24, color=PURPLE, weight=BOLD).next_to(notebook, UP, buff=0.25)
            self.play(Create(notebook), FadeIn(per34), run_time=1.0)

            self.wait_until_bookmark("bk_4c")
            len_dim = create_dimension(
                notebook.get_corner(DL) + DOWN * 0.35,
                notebook.get_corner(DR) + DOWN * 0.35,
                "11 centimetres",
                DOWN,
            )
            self.play(Create(len_dim[0]), FadeIn(len_dim[1]), run_time=0.8)
            self.play(len_dim[0].animate.set_color(ORANGE_HL), len_dim[1].animate.set_color(ORANGE_HL), run_time=0.5)
            self.play(len_dim[0].animate.set_color(PURPLE), len_dim[1].animate.set_color(PURPLE), run_time=0.5)

            self.wait_until_bookmark("bk_4d")
            width_unknown = create_unknown(notebook.get_right() + RIGHT * 0.45)
            shelf = Line(LEFT * 4.5 + DOWN * 3.0, RIGHT * 4.5 + DOWN * 3.0, color=PURPLE, stroke_width=5)
            shelf_dim = create_dimension(
                LEFT * 4.5 + DOWN * 3.35,
                RIGHT * 4.5 + DOWN * 3.35,
                "24-centimetre shelf",
                DOWN,
            )
            copies = VGroup(
                Rectangle(width=1.2, height=0.65, color=PURPLE, stroke_width=2.5).move_to(LEFT * 0.8 + DOWN * 2.55),
                Rectangle(width=1.2, height=0.65, color=PURPLE, stroke_width=2.5).move_to(RIGHT * 0.8 + DOWN * 2.55),
            )
            self.play(FadeIn(width_unknown), run_time=0.6)
            self.play(FadeIn(copies), Create(shelf), Create(shelf_dim[0]), FadeIn(shelf_dim[1]), run_time=0.8)

            self.wait_until_bookmark("bk_4e")
            self.play(FadeOut(VGroup(q1, notebook, per34, len_dim, width_unknown, shelf, shelf_dim, copies)), run_time=0.8)
            q2 = justified_block(
                [
                    "Part 2: A square tile has a perimeter of 48 centimetres.",
                    "Find the length of one side.",
                ],
                font_size=23,
                width=11.8,
            ).to_edge(UP, buff=1.0)
            tile = Square(side_length=2.4, color=PURPLE, stroke_width=2.5).move_to(DOWN * 0.4)
            per48 = safe_text("P = 48 centimetres", font_size=24, color=PURPLE, weight=BOLD).next_to(tile, UP, buff=0.3)
            self.play(FadeIn(q2), Create(tile), FadeIn(per48), run_time=1.0)

            self.wait_until_bookmark("bk_4f")
            tile_unknown = create_unknown(tile.get_bottom() + DOWN * 0.35)
            self.play(FadeIn(tile_unknown), Indicate(tile_unknown, color=ORANGE_HL), run_time=0.7)
            self.play(FadeOut(VGroup(badge, q2, tile, per48, tile_unknown)), run_time=0.8)

        with self.voiceover(
            text='<bookmark mark="bk_5a"/>Solution: For the notebook: Two times the '
            '<bookmark mark="bk_5b"/>sum of length and width equals the perimeter. '
            'Two times <bookmark mark="bk_5c"/>eleven plus width equals thirty four. '
            'Eleven plus <bookmark mark="bk_5d"/>width equals seventeen. '
            'So width equals - <bookmark mark="bk_5e"/>six centimetres. '
            'Two notebooks placed side by side would need <bookmark mark="bk_5f"/>twelve centimetres, which fits well on the shelf. '
            'For the <bookmark mark="bk_5g"/>tile: The perimeter equals four times the side. '
            'Four times the <bookmark mark="bk_5h"/>side equals forty eight. '
            'So the side equals - <bookmark mark="bk_5i"/>twelve centimetres. '
            'This is the same idea builders use when calculating <bookmark mark="bk_5j"/>tile sizes for a floor.'
        ):
            badge = create_heading_badge("Solution")

            self.wait_until_bookmark("bk_5a")
            notebook = Rectangle(width=3.0, height=1.5, color=PURPLE, stroke_width=2.5).shift(RIGHT * 3.6 + UP * 0.7)
            n_len = create_dimension(
                notebook.get_corner(DL) + DOWN * 0.25,
                notebook.get_corner(DR) + DOWN * 0.25,
                "11 centimetres",
                DOWN,
            )
            n_unknown = create_unknown(notebook.get_right() + RIGHT * 0.35)
            note_head = safe_text("For the notebook", font_size=28, color=PURPLE, weight=BOLD).to_edge(LEFT, buff=0.8).shift(UP * 2.0)
            self.play(FadeIn(badge), Create(notebook), Create(n_len[0]), FadeIn(n_len[1]), FadeIn(n_unknown), FadeIn(note_head), run_time=1.0)

            self.wait_until_bookmark("bk_5b")
            eq1 = math_obj(r"2(l + w) = P", font_size=36).next_to(note_head, DOWN, buff=0.5).align_to(note_head, LEFT)
            self.play(FadeIn(eq1), run_time=0.7)

            self.wait_until_bookmark("bk_5c")
            self.play(eq1.animate.set_opacity(0.4), run_time=0.5)
            eq2 = math_obj(r"2(11 + w) = 34", font_size=36).next_to(eq1, DOWN, buff=0.4).align_to(eq1, LEFT)
            self.play(FadeIn(eq2), run_time=0.8)

            self.wait_until_bookmark("bk_5d")
            self.play(eq2.animate.set_opacity(0.4), run_time=0.5)
            eq3 = math_obj(r"11 + w = 17", font_size=36).next_to(eq2, DOWN, buff=0.4).align_to(eq2, LEFT)
            self.play(FadeIn(eq3), run_time=0.8)

            self.wait_until_bookmark("bk_5e")
            self.play(eq3.animate.set_opacity(0.4), run_time=0.5)
            width_value = safe_text("6", font_size=30, color=ORANGE_HL, weight=BOLD).move_to(n_unknown)
            ans_w_math = math_obj(r"w = 6", color=ORANGE_HL, font_size=40)
            ans_w_text = safe_text("centimetres", font_size=28, color=ORANGE_HL, weight=BOLD)
            ans_w = VGroup(ans_w_math, ans_w_text).arrange(RIGHT, buff=0.15)
            ans_w.next_to(eq3, DOWN, buff=0.45).align_to(eq3, LEFT)
            self.play(ReplacementTransform(n_unknown, width_value), FadeIn(ans_w), run_time=0.9)

            self.wait_until_bookmark("bk_5f")
            self.play(FadeOut(VGroup(note_head, eq1, eq2, eq3, ans_w, notebook, n_len, width_value)), run_time=0.8)
            shelf = Line(LEFT * 4.5 + DOWN * 1.3, RIGHT * 4.5 + DOWN * 1.3, color=PURPLE, stroke_width=5)
            shelf_dim = create_dimension(
                LEFT * 4.5 + DOWN * 1.65,
                RIGHT * 4.5 + DOWN * 1.65,
                "24-centimetre shelf",
                DOWN,
            )
            book_a = Rectangle(width=1.4, height=0.75, color=PURPLE, stroke_width=2.5).move_to(LEFT * 0.8 + DOWN * 0.8)
            book_b = Rectangle(width=1.4, height=0.75, color=PURPLE, stroke_width=2.5).move_to(RIGHT * 0.8 + DOWN * 0.8)
            need12 = safe_text("12 centimetres", font_size=32, color=ORANGE_HL, weight=BOLD).next_to(VGroup(book_a, book_b), UP, buff=0.35)
            self.play(Create(shelf), Create(shelf_dim[0]), FadeIn(shelf_dim[1]), FadeIn(book_a), FadeIn(book_b), FadeIn(need12), run_time=1.0)
            self.play(Indicate(shelf_dim[1], color=ORANGE_HL), run_time=0.7)

            self.wait_until_bookmark("bk_5g")
            self.play(FadeOut(VGroup(shelf, shelf_dim, book_a, book_b, need12)), run_time=0.8)
            tile_head = safe_text("For the tile", font_size=28, color=PURPLE, weight=BOLD).to_edge(LEFT, buff=0.8).shift(UP * 2.0)
            tile = Square(side_length=2.2, color=PURPLE, stroke_width=2.5).shift(RIGHT * 3.5 + UP * 0.3)
            tile_q = create_unknown(tile.get_bottom() + DOWN * 0.35)
            eqt1 = math_obj(r"P = 4s", font_size=38).next_to(tile_head, DOWN, buff=0.5).align_to(tile_head, LEFT)
            self.play(FadeIn(tile_head), Create(tile), FadeIn(tile_q), FadeIn(eqt1), run_time=1.0)

            self.wait_until_bookmark("bk_5h")
            self.play(eqt1.animate.set_opacity(0.4), run_time=0.5)
            eqt2 = math_obj(r"4s = 48", font_size=38).next_to(eqt1, DOWN, buff=0.4).align_to(eqt1, LEFT)
            self.play(FadeIn(eqt2), Circumscribe(tile, color=ORANGE_HL), run_time=0.9)

            self.wait_until_bookmark("bk_5i")
            self.play(eqt2.animate.set_opacity(0.4), run_time=0.5)
            side_value = safe_text("12", font_size=30, color=ORANGE_HL, weight=BOLD).move_to(tile_q)
            ans_s_math = math_obj(r"s = 12", color=ORANGE_HL, font_size=40)
            ans_s_text = safe_text("centimetres", font_size=28, color=ORANGE_HL, weight=BOLD)
            ans_s = VGroup(ans_s_math, ans_s_text).arrange(RIGHT, buff=0.15)
            ans_s.next_to(eqt2, DOWN, buff=0.45).align_to(eqt2, LEFT)
            self.play(ReplacementTransform(tile_q, side_value), FadeIn(ans_s), run_time=0.9)

            self.wait_until_bookmark("bk_5j")
            self.play(FadeOut(VGroup(tile_head, eqt1, eqt2, ans_s, tile, side_value)), run_time=0.8)
            floor = VGroup()
            for i in range(4):
                for j in range(3):
                    floor.add(
                        Square(
                            0.65,
                            color=PURPLE,
                            stroke_width=2,
                            fill_color=WHITE,
                            fill_opacity=0.5,
                        ).move_to([i * 0.7 - 1.05, j * 0.7 - 0.7, 0])
                    )
            tile_sizes = safe_text("Tile sizes", font_size=34, color=ORANGE_HL, weight=BOLD).next_to(floor, UP, buff=0.35)
            self.play(FadeIn(floor), FadeIn(tile_sizes), run_time=0.9)
            self.play(Indicate(floor[5], color=ORANGE_HL), run_time=0.7)
            self.play(FadeOut(VGroup(badge, floor, tile_sizes)), run_time=0.9)

        with self.voiceover(
            text='<bookmark mark="bk_6a"/>Summary. Perimeter formulas can be rearranged to find '
            '<bookmark mark="bk_6b"/>missing dimensions. Rectangle: perimeter is two times the '
            '<bookmark mark="bk_6c"/>sum of length and width. Square: side is the perimeter divided by '
            '<bookmark mark="bk_6d"/>four.'
        ):
            badge = create_heading_badge("Summary")

            self.wait_until_bookmark("bk_6a")
            self.play(FadeIn(badge), run_time=0.6)

            self.wait_until_bookmark("bk_6b")
            line1 = safe_text(
                "Perimeter formulas can be rearranged to find missing dimensions.",
                font_size=27,
                color=PURPLE,
            ).to_edge(UP, buff=1.4)
            self.play(FadeIn(line1), run_time=0.7)

            self.wait_until_bookmark("bk_6c")
            rect_word = safe_text("Rectangle:", font_size=28, color=PURPLE, weight=BOLD)
            rect_formula = math_obj(r"P = 2(l + w)", font_size=34)
            line2 = VGroup(rect_word, rect_formula).arrange(RIGHT, buff=0.25)
            line2.next_to(line1, DOWN, buff=0.55).align_to(line1, LEFT)
            self.play(FadeIn(line2), run_time=0.7)

            self.wait_until_bookmark("bk_6d")
            sq_word = safe_text("Square:", font_size=28, color=PURPLE, weight=BOLD)
            sq_formula = math_obj(r"s = \dfrac{P}{4}", font_size=34)
            line3 = VGroup(sq_word, sq_formula).arrange(RIGHT, buff=0.25)
            line3.next_to(line2, DOWN, buff=0.55).align_to(line2, LEFT)
            self.play(FadeIn(line3), run_time=0.7)

            self.wait(0.6)
            self.play(FadeOut(VGroup(badge, line1, line2, line3)), run_time=0.9)