import os
import urllib.request
import manimpango
from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.openai import OpenAIService

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
# BOOKMARK FAILURE TRACKING
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
        print(f"  Bookmark '{mark}' NOT FOUND in: {scene_text}...")
        return 0.0

_vt.VoiceoverTracker.time_until_bookmark = _safe_time_until_bookmark

import atexit
def _report():
    if _FAILED_BOOKMARKS:
        print("\n" + "="*60)
        print(f"FAILED BOOKMARKS SUMMARY ({len(_FAILED_BOOKMARKS)} total):")
        print("="*60)
        for mark, text in _FAILED_BOOKMARKS:
            print(f"   {mark}    {text}")
        print("="*60)
atexit.register(_report)

# ============================================================
# COSCHOOL COLOR PALETTE
# ============================================================
LAVENDER_BG = "#E7E5F3"
PURPLE      = "#7464CE"
ORANGE_HL   = "#FF9302"
PALE_PURPLE = "#9495D7"

TTS_INSTRUCTIONS = """
Voice & Personality:
You are a warm, patient, and encouraging math teacher speaking to a
middle-school student. Your tone is friendly, calm, and confident -
never rushed, never robotic. You sound like a human explainer in a
Khan Academy or 3Blue1Brown style video.

Pacing:
Speak at a MODERATE-TO-SLOW pace. Prioritize clarity over speed.
Every word must be clearly heard and mentally absorbed by the student.
Do NOT race through sentences. Allow the listener to follow along
with the visual on screen.

Variables and Math Terms:
When pronouncing single-letter variables like x, y, z, a, b, c, h, r,
or t, slow down noticeably and articulate each letter clearly with a
brief micro-pause before and after it. Treat each variable as an
important named character in the explanation.

Formulas:
When reading a formula or equation, slow your pace even further.
Pause briefly between each component of the formula so the student
can match the spoken word to the symbol on screen. For example, in
"one half times base times height," insert a small breath between
"one half," "times base," and "times height."

Numbers and Units:
Pronounce numbers clearly. For units like "centimeter square" or
"meter cube," say them with a confident, deliberate cadence - never
mumbled or rushed.

Emphasis:
Naturally emphasize key terms: the name of the shape, the formula
being introduced, the final answer, and any word that introduces a
new concept. Use gentle stress, not loudness.

Pauses:
Add a natural beat (short pause) at commas, and a slightly longer
pause at periods. After stating a final answer, pause for a moment
before continuing.

Mood:
Encouraging, curious, and warm. You want the student to succeed and
feel confident. Avoid monotone delivery. Add gentle warmth and a
teacher's natural curiosity to your voice.

Do NOT:
- Do not speak in a rushed, news-anchor tone.
- Do not flatten your voice into monotone.
- Do not add filler words, sounds, or commentary not in the script.
- Do not improvise or paraphrase - read the script exactly as written.
"""

def create_heading_badge(text_str):
    t = Text(text_str, font="Poppins", font_size=28,
             color=WHITE, weight=BOLD)
    badge = RoundedRectangle(
        corner_radius=0.2,
        width=t.width + 0.6, height=t.height + 0.3,
        fill_color=PURPLE, fill_opacity=1, stroke_width=0,
    )
    badge.move_to(t)
    return VGroup(badge, t).to_corner(UL, buff=0.3)

def create_unknown(position):
    return Text("?", font="Poppins", font_size=36,
                color=ORANGE_HL, weight=BOLD).move_to(position)


class PerimeterAndArea(VoiceoverScene):
    def construct(self):
        self.camera.background_color = LAVENDER_BG
        self.set_speech_service(
            OpenAIService(
                voice="nova",
                model="gpt-4o-mini-tts",
                transcription_model="medium",
                instructions=TTS_INSTRUCTIONS,
            ),
            create_subcaption=False,
        )

        # ====================================================
        # SCENE 1: TITLE SLIDE
        # ====================================================
        title_bg = Rectangle(
            width=config.frame_width, height=config.frame_height,
            fill_color=PURPLE, fill_opacity=1, stroke_width=0,
        )
        title = Text("Perimeter and Area", font="Poppins", font_size=72,
                     color=WHITE, weight=BOLD).move_to(ORIGIN)

        with self.voiceover(
            text='<bookmark mark="bk_title"/>Perimeter and Area.'
        ) as tracker:
            self.wait_until_bookmark("bk_title")
            self.play(FadeIn(title_bg), FadeIn(title), run_time=1.0)
        self.wait(0.5)
        self.play(FadeOut(title_bg), FadeOut(title), run_time=0.8)

        # ====================================================
        # SCENE 2: INTRO
        # ====================================================
        intro = Text("Hello students!", font="Poppins",
                     font_size=40, color=PURPLE).move_to(ORIGIN)

        with self.voiceover(
            text='<bookmark mark="bk_hello"/>Hello students!'
        ) as tracker:
            self.wait_until_bookmark("bk_hello")
            self.play(FadeIn(intro), run_time=0.8)
        self.wait(0.4)
        self.play(FadeOut(intro), run_time=0.6)

        # ====================================================
        # SCENE 3: INTRODUCTION (Garden fence)
        # ====================================================
        heading = create_heading_badge("Introduction")

        garden = Rectangle(width=5, height=2.8, color=PURPLE,
                           stroke_width=2.5, fill_opacity=0.1,
                           fill_color=PURPLE).move_to(ORIGIN)

        known_arrow = DoubleArrow(
            start=garden.get_corner(DL) + DOWN*0.3,
            end=garden.get_corner(DR) + DOWN*0.3,
            color=PURPLE, stroke_width=2, tip_length=0.2, buff=0,
        )
        known_label = Text("known", font="Poppins", font_size=22, color=PURPLE)
        known_label.next_to(known_arrow, DOWN, buff=0.15)

        unknown_arrow = DoubleArrow(
            start=garden.get_corner(UR) + RIGHT*0.3,
            end=garden.get_corner(DR) + RIGHT*0.3,
            color=PURPLE, stroke_width=2, tip_length=0.2, buff=0,
        )
        unknown_label = Text("?", font="Poppins", font_size=36,
                             color=ORANGE_HL, weight=BOLD)
        unknown_label.next_to(unknown_arrow, RIGHT, buff=0.15)

        with self.voiceover(
            text='<bookmark mark="bk_intro_head"/>Suppose you need to put '
                 '<bookmark mark="bk_garden"/>a fence around a rectangular garden. '
                 '<bookmark mark="bk_total"/>You know the total length of the fence '
                 '<bookmark mark="bk_oneside"/>and the length of one side. '
                 '<bookmark mark="bk_figure"/>How can you figure out the other side '
                 '<bookmark mark="bk_measuring"/>without measuring it?'
        ) as tracker:
            self.wait_until_bookmark("bk_intro_head")
            self.play(FadeIn(heading), run_time=0.6)

            self.wait_until_bookmark("bk_garden")
            self.play(Create(garden), run_time=1.2)

            self.wait_until_bookmark("bk_total")
            self.play(Create(known_arrow), FadeIn(known_label),
                      garden.animate.set_stroke(ORANGE_HL),
                      run_time=0.8)

            self.wait_until_bookmark("bk_oneside")
            self.play(
                garden.animate.set_stroke(PURPLE),
                Create(unknown_arrow), FadeIn(unknown_label),
                run_time=0.8,
            )

            self.wait_until_bookmark("bk_figure")
            self.play(Indicate(unknown_label, color=ORANGE_HL), run_time=0.6)

            self.wait_until_bookmark("bk_measuring")
            self.play(Flash(garden, color=ORANGE_HL), run_time=0.5)

        self.wait(0.3)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

        # ====================================================
        # SCENE 4: CONCEPT - Perimeter Definition + Formulas
        # ====================================================
        heading = create_heading_badge("Concept")

        rect_concept = Rectangle(width=4.5, height=2.5, color=PURPLE,
                                 stroke_width=2.5).move_to(RIGHT*3 + DOWN*0.5)

        rect_label = Text("Rectangle", font="Poppins", font_size=26,
                          color=PURPLE).to_edge(LEFT, buff=1.0).shift(UP*2)
        rect_formula = MathTex(r"P = 2 \times (l + w)",
                               color=PURPLE, font_size=36)
        rect_formula.next_to(rect_label, DOWN, buff=0.4).align_to(rect_label, LEFT)

        square_concept = Square(side_length=2.5, color=PURPLE,
                                stroke_width=2.5).move_to(RIGHT*3 + DOWN*0.5)

        sq_label = Text("Square", font="Poppins", font_size=26,
                        color=PURPLE).to_edge(LEFT, buff=1.0).shift(UP*2)
        sq_formula = MathTex(r"P = 4 \times s",
                             color=PURPLE, font_size=36)
        sq_formula.next_to(sq_label, DOWN, buff=0.4).align_to(sq_label, LEFT)

        tool_text = Text("Rearrange to find missing dimension",
                         font="Poppins", font_size=24, color=PURPLE)
        tool_text.to_edge(DOWN, buff=1.0)

        with self.voiceover(
            text='<bookmark mark="bk_concept_head"/>The perimeter is the total distance '
                 '<bookmark mark="bk_shape"/>around a shape. '
                 '<bookmark mark="bk_rect"/>For a rectangle, '
                 '<bookmark mark="bk_pformula"/>perimeter equals two times the sum of length and width, '
                 '<bookmark mark="bk_written"/>written as 2 times length plus width. '
                 '<bookmark mark="bk_square"/>For a square, '
                 '<bookmark mark="bk_sqformula"/>perimeter equals four times its side, '
                 '<bookmark mark="bk_sqwritten"/>written as 4 times side. '
                 '<bookmark mark="bk_given"/>So if we are given the perimeter and one dimension, '
                 '<bookmark mark="bk_rearrange"/>we can rearrange these formulas to find the missing dimension. '
                 '<bookmark mark="bk_backwards"/>This means perimeter is not just for measuring, '
                 '<bookmark mark="bk_tool"/>it is a tool to work backwards too.'
        ) as tracker:
            self.wait_until_bookmark("bk_concept_head")
            self.play(FadeIn(heading), run_time=0.6)

            self.wait_until_bookmark("bk_shape")
            self.play(Create(rect_concept), run_time=1.0)

            self.wait_until_bookmark("bk_rect")
            self.play(FadeIn(rect_label), run_time=0.6)

            self.wait_until_bookmark("bk_pformula")
            self.play(FadeIn(rect_formula),
                      Indicate(rect_concept, color=ORANGE_HL),
                      run_time=0.8)

            self.wait_until_bookmark("bk_written")
            self.play(Indicate(rect_formula, color=ORANGE_HL), run_time=0.6)

            self.wait_until_bookmark("bk_square")
            self.play(
                FadeOut(rect_concept),
                FadeOut(rect_label),
                FadeOut(rect_formula),
                Create(square_concept),
                run_time=1.0,
            )
            self.play(FadeIn(sq_label), run_time=0.5)

            self.wait_until_bookmark("bk_sqformula")
            self.play(FadeIn(sq_formula),
                      Indicate(square_concept, color=ORANGE_HL),
                      run_time=0.8)

            self.wait_until_bookmark("bk_sqwritten")
            self.play(Indicate(sq_formula, color=ORANGE_HL), run_time=0.6)

            self.wait_until_bookmark("bk_given")
            self.play(Indicate(sq_formula, color=ORANGE_HL), run_time=0.6)

            self.wait_until_bookmark("bk_rearrange")
            self.play(FadeIn(tool_text), run_time=0.7)

            self.wait_until_bookmark("bk_backwards")
            self.play(Indicate(tool_text, color=ORANGE_HL), run_time=0.6)

            self.wait_until_bookmark("bk_tool")
            self.play(Flash(tool_text, color=ORANGE_HL), run_time=0.5)

        self.wait(0.3)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

        # ====================================================
        # SCENE 5: REASONING
        # ====================================================
        heading = create_heading_badge("Reasoning")

        rect_r = Rectangle(width=4.5, height=2.5, color=PURPLE,
                           stroke_width=2.5).move_to(ORIGIN + UP*0.3)
        l_top = Text("l", font="Poppins", font_size=24, color=PURPLE)
        l_top.next_to(rect_r, UP, buff=0.15)
        l_bot = Text("l", font="Poppins", font_size=24, color=PURPLE)
        l_bot.next_to(rect_r, DOWN, buff=0.15)
        w_left = Text("w", font="Poppins", font_size=24, color=PURPLE)
        w_left.next_to(rect_r, LEFT, buff=0.15)
        w_right = Text("w", font="Poppins", font_size=24, color=PURPLE)
        w_right.next_to(rect_r, RIGHT, buff=0.15)

        algebra_hint = Text("Use simple algebra to find the missing one",
                            font="Poppins", font_size=22, color=PURPLE)
        algebra_hint.to_edge(DOWN, buff=1.0)

        sq_r = Square(side_length=2.5, color=PURPLE,
                      stroke_width=2.5).move_to(ORIGIN + UP*0.3)
        s_labels = VGroup(
            Text("s", font="Poppins", font_size=24, color=PURPLE).next_to(sq_r, UP, buff=0.15),
            Text("s", font="Poppins", font_size=24, color=PURPLE).next_to(sq_r, DOWN, buff=0.15),
            Text("s", font="Poppins", font_size=24, color=PURPLE).next_to(sq_r, LEFT, buff=0.15),
            Text("s", font="Poppins", font_size=24, color=PURPLE).next_to(sq_r, RIGHT, buff=0.15),
        )

        side_formula = MathTex(r"s = P \div 4", color=PURPLE, font_size=36)
        side_formula.to_edge(DOWN, buff=1.0)

        with self.voiceover(
            text='<bookmark mark="bk_why"/>Now, why does this work? '
                 '<bookmark mark="bk_rectangle"/>A rectangle has two equal lengths '
                 '<bookmark mark="bk_widths"/>and two equal widths, '
                 '<bookmark mark="bk_perimeter"/>so once we know the perimeter and one of them, '
                 '<bookmark mark="bk_algebra"/>the other can be found using simple algebra. '
                 '<bookmark mark="bk_squareall"/>For a square, all four sides are equal, '
                 '<bookmark mark="bk_divided"/>so the side is just the perimeter divided by four.'
        ) as tracker:
            self.wait_until_bookmark("bk_why")
            self.play(FadeIn(heading), run_time=0.6)

            self.wait_until_bookmark("bk_rectangle")
            self.play(Create(rect_r), FadeIn(l_top), FadeIn(l_bot), run_time=1.0)
            self.play(l_top.animate.set_color(ORANGE_HL),
                      l_bot.animate.set_color(ORANGE_HL), run_time=0.5)

            self.wait_until_bookmark("bk_widths")
            self.play(
                l_top.animate.set_color(PURPLE),
                l_bot.animate.set_color(PURPLE),
                FadeIn(w_left), FadeIn(w_right),
                run_time=0.7,
            )
            self.play(w_left.animate.set_color(ORANGE_HL),
                      w_right.animate.set_color(ORANGE_HL), run_time=0.5)

            self.wait_until_bookmark("bk_perimeter")
            self.play(
                w_left.animate.set_color(PURPLE),
                w_right.animate.set_color(PURPLE),
                Indicate(rect_r, color=ORANGE_HL),
                run_time=0.6,
            )

            self.wait_until_bookmark("bk_algebra")
            self.play(FadeIn(algebra_hint), run_time=0.7)

            self.wait_until_bookmark("bk_squareall")
            self.play(
                FadeOut(rect_r), FadeOut(l_top), FadeOut(l_bot),
                FadeOut(w_left), FadeOut(w_right),
                FadeOut(algebra_hint),
                Create(sq_r), FadeIn(s_labels),
                run_time=1.0,
            )
            self.play(s_labels.animate.set_color(ORANGE_HL), run_time=0.5)

            self.wait_until_bookmark("bk_divided")
            self.play(s_labels.animate.set_color(PURPLE),
                      FadeIn(side_formula), run_time=0.7)

        self.wait(0.4)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

        # ====================================================
        # SCENE 6: QUESTION
        # ====================================================
        heading = create_heading_badge("Question")

        # PART 1
        part1_label = Text("Part 1:", font="Poppins", font_size=28,
                           color=PURPLE, weight=BOLD).to_edge(UP, buff=1.0).to_edge(LEFT, buff=1.0)
        p1_text = Text("The perimeter of a rectangle is 28 cm. Length = 9 cm. Find width.",
                       font="Poppins", font_size=22, color=PURPLE)
        p1_text.next_to(part1_label, DOWN, buff=0.3).align_to(part1_label, LEFT)

        rect_q = Rectangle(width=4.0, height=2.0, color=PURPLE,
                           stroke_width=2.5).move_to(DOWN*0.8)
        len_arrow_q = DoubleArrow(
            start=rect_q.get_corner(DL) + DOWN*0.3,
            end=rect_q.get_corner(DR) + DOWN*0.3,
            color=PURPLE, stroke_width=2, tip_length=0.2, buff=0,
        )
        len_label_q = Text("9 cm", font="Poppins", font_size=22, color=PURPLE)
        len_label_q.next_to(len_arrow_q, DOWN, buff=0.15)

        wid_arrow_q = DoubleArrow(
            start=rect_q.get_corner(UR) + RIGHT*0.3,
            end=rect_q.get_corner(DR) + RIGHT*0.3,
            color=PURPLE, stroke_width=2, tip_length=0.2, buff=0,
        )
        wid_q = Text("?", font="Poppins", font_size=36,
                     color=ORANGE_HL, weight=BOLD)
        wid_q.next_to(wid_arrow_q, RIGHT, buff=0.15)

        with self.voiceover(
            text='<bookmark mark="bk_q_head"/>Part 1. '
                 '<bookmark mark="bk_p1"/>The perimeter of a rectangle is 28 centimetres. '
                 '<bookmark mark="bk_length9"/>Its length is 9 centimetres. '
                 '<bookmark mark="bk_findwidth"/>Find its width.'
        ) as tracker:
            self.wait_until_bookmark("bk_q_head")
            self.play(FadeIn(heading), FadeIn(part1_label), run_time=0.6)

            self.wait_until_bookmark("bk_p1")
            self.play(FadeIn(p1_text), Create(rect_q), run_time=1.0)

            self.wait_until_bookmark("bk_length9")
            self.play(Create(len_arrow_q), FadeIn(len_label_q), run_time=0.8)

            self.wait_until_bookmark("bk_findwidth")
            self.play(Create(wid_arrow_q), FadeIn(wid_q), run_time=0.7)

        self.wait(0.4)

        rect_q_group = VGroup(rect_q, len_arrow_q, len_label_q,
                              wid_arrow_q, wid_q)

        # PART 2
        part2_label = Text("Part 2:", font="Poppins", font_size=28,
                           color=PURPLE, weight=BOLD).to_edge(UP, buff=1.0).to_edge(LEFT, buff=1.0)
        p2_text = Text("The perimeter of a square is 36 cm. Find side.",
                       font="Poppins", font_size=22, color=PURPLE)
        p2_text.next_to(part2_label, DOWN, buff=0.3).align_to(part2_label, LEFT)

        sq_q = Square(side_length=2.2, color=PURPLE,
                      stroke_width=2.5).move_to(DOWN*0.8)
        side_arrow_q = DoubleArrow(
            start=sq_q.get_corner(DL) + DOWN*0.3,
            end=sq_q.get_corner(DR) + DOWN*0.3,
            color=PURPLE, stroke_width=2, tip_length=0.2, buff=0,
        )
        side_q = Text("?", font="Poppins", font_size=36,
                      color=ORANGE_HL, weight=BOLD)
        side_q.next_to(side_arrow_q, DOWN, buff=0.15)

        with self.voiceover(
            text='<bookmark mark="bk_p2_head"/>Part 2. '
                 '<bookmark mark="bk_p2"/>The perimeter of a square is 36 centimetres. '
                 '<bookmark mark="bk_findside"/>Find the length of its side.'
        ) as tracker:
            self.wait_until_bookmark("bk_p2_head")
            self.play(
                FadeOut(part1_label), FadeOut(p1_text),
                FadeOut(rect_q_group),
                FadeIn(part2_label),
                run_time=0.8,
            )

            self.wait_until_bookmark("bk_p2")
            self.play(FadeIn(p2_text), Create(sq_q), run_time=1.0)

            self.wait_until_bookmark("bk_findside")
            self.play(Create(side_arrow_q), FadeIn(side_q), run_time=0.8)

        self.wait(0.4)
        self.play(
            FadeOut(part2_label), FadeOut(p2_text),
            FadeOut(sq_q), FadeOut(side_arrow_q), FadeOut(side_q),
            FadeOut(heading),
            run_time=0.8,
        )

        # ====================================================
        # SCENE 7: SOLUTION
        # ====================================================
        heading = create_heading_badge("Solution")
        self.play(FadeIn(heading), run_time=0.5)

        # Rebuild figures persistently for solution
        rect_s = Rectangle(width=3.5, height=1.8, color=PURPLE,
                           stroke_width=2.5).move_to(RIGHT*3.5 + DOWN*0.3)
        len_arrow_s = DoubleArrow(
            start=rect_s.get_corner(DL) + DOWN*0.3,
            end=rect_s.get_corner(DR) + DOWN*0.3,
            color=PURPLE, stroke_width=2, tip_length=0.2, buff=0,
        )
        len_label_s = Text("9 cm", font="Poppins", font_size=22, color=PURPLE)
        len_label_s.next_to(len_arrow_s, DOWN, buff=0.15)
        wid_arrow_s = DoubleArrow(
            start=rect_s.get_corner(UR) + RIGHT*0.3,
            end=rect_s.get_corner(DR) + RIGHT*0.3,
            color=PURPLE, stroke_width=2, tip_length=0.2, buff=0,
        )
        wid_q_s = Text("?", font="Poppins", font_size=36,
                       color=ORANGE_HL, weight=BOLD)
        wid_q_s.next_to(wid_arrow_s, RIGHT, buff=0.15)

        rect_label_s = Text("Rectangle", font="Poppins", font_size=24,
                            color=PURPLE, weight=BOLD)
        rect_label_s.to_edge(LEFT, buff=0.8).shift(UP*2.5)

        formula1 = MathTex(r"P = 2 \times (l + w)", color=PURPLE, font_size=34)
        formula1.next_to(rect_label_s, DOWN, buff=0.4).align_to(rect_label_s, LEFT)

        step1 = MathTex(r"2 \times (9 + w) = 28", color=PURPLE, font_size=34)
        step1.next_to(formula1, DOWN, buff=0.4).align_to(formula1, LEFT)

        step2 = MathTex(r"9 + w = 14", color=PURPLE, font_size=34)
        step2.next_to(step1, DOWN, buff=0.4).align_to(step1, LEFT)

        ans1 = MathTex(r"w = 5 \, \text{cm}", color=ORANGE_HL, font_size=40)
        ans1.next_to(step2, DOWN, buff=0.4).align_to(step2, LEFT)

        with self.voiceover(
            text='<bookmark mark="bk_rectangle_sol"/>For the rectangle: '
                 '<bookmark mark="bk_perimeter_formula"/>We know perimeter equals 2 times length plus width. '
                 '<bookmark mark="bk_substitute"/>So, 2 times 9 plus width equals 28. '
                 '<bookmark mark="bk_dividing"/>Dividing both sides by 2, we get 9 plus width equals 14. '
                 '<bookmark mark="bk_width5"/>So, width equals 5 centimetres.'
        ) as tracker:
            self.wait_until_bookmark("bk_rectangle_sol")
            self.play(
                Create(rect_s),
                Create(len_arrow_s), FadeIn(len_label_s),
                Create(wid_arrow_s), FadeIn(wid_q_s),
                FadeIn(rect_label_s),
                run_time=1.2,
            )

            self.wait_until_bookmark("bk_perimeter_formula")
            self.play(FadeIn(formula1), run_time=0.8)

            self.wait_until_bookmark("bk_substitute")
            self.play(
                len_label_s.animate.set_color(ORANGE_HL),
                FadeIn(step1),
                run_time=0.8,
            )

            self.wait_until_bookmark("bk_dividing")
            self.play(
                len_label_s.animate.set_color(PURPLE),
                FadeIn(step2),
                formula1.animate.set_opacity(0.4),
                run_time=0.8,
            )

            self.wait_until_bookmark("bk_width5")
            self.play(
                step1.animate.set_opacity(0.4),
                step2.animate.set_opacity(0.4),
                FadeOut(wid_q_s),
                FadeIn(ans1),
                run_time=1.0,
            )

        self.wait(0.6)

        # Clear part 1 solution
        self.play(
            FadeOut(rect_s), FadeOut(len_arrow_s), FadeOut(len_label_s),
            FadeOut(wid_arrow_s),
            FadeOut(rect_label_s), FadeOut(formula1),
            FadeOut(step1), FadeOut(step2), FadeOut(ans1),
            run_time=0.8,
        )

        # SQUARE solution
        sq_s = Square(side_length=2.0, color=PURPLE,
                      stroke_width=2.5).move_to(RIGHT*3.5 + DOWN*0.3)
        side_arrow_s = DoubleArrow(
            start=sq_s.get_corner(DL) + DOWN*0.3,
            end=sq_s.get_corner(DR) + DOWN*0.3,
            color=PURPLE, stroke_width=2, tip_length=0.2, buff=0,
        )
        side_q_s = Text("?", font="Poppins", font_size=36,
                        color=ORANGE_HL, weight=BOLD)
        side_q_s.next_to(side_arrow_s, DOWN, buff=0.15)

        sq_label_s = Text("Square", font="Poppins", font_size=24,
                          color=PURPLE, weight=BOLD)
        sq_label_s.to_edge(LEFT, buff=0.8).shift(UP*2.5)

        formula2 = MathTex(r"P = 4 \times s", color=PURPLE, font_size=34)
        formula2.next_to(sq_label_s, DOWN, buff=0.4).align_to(sq_label_s, LEFT)

        step_sq1 = MathTex(r"4 \times s = 36", color=PURPLE, font_size=34)
        step_sq1.next_to(formula2, DOWN, buff=0.4).align_to(formula2, LEFT)

        ans2 = MathTex(r"s = 9 \, \text{cm}", color=ORANGE_HL, font_size=40)
        ans2.next_to(step_sq1, DOWN, buff=0.4).align_to(step_sq1, LEFT)

        with self.voiceover(
            text='<bookmark mark="bk_square_sol"/>For the square: '
                 '<bookmark mark="bk_square_formula"/>We know perimeter equals 4 times side. '
                 '<bookmark mark="bk_substitute_sq"/>So, 4 times side equals 36. '
                 '<bookmark mark="bk_dividing_sq"/>Dividing both sides by 4, side equals 9 centimetres.'
        ) as tracker:
            self.wait_until_bookmark("bk_square_sol")
            self.play(
                Create(sq_s),
                Create(side_arrow_s), FadeIn(side_q_s),
                FadeIn(sq_label_s),
                run_time=1.2,
            )

            self.wait_until_bookmark("bk_square_formula")
            self.play(FadeIn(formula2), run_time=0.8)

            self.wait_until_bookmark("bk_substitute_sq")
            self.play(FadeIn(step_sq1), run_time=0.8)

            self.wait_until_bookmark("bk_dividing_sq")
            self.play(
                formula2.animate.set_opacity(0.4),
                step_sq1.animate.set_opacity(0.4),
                FadeOut(side_q_s),
                FadeIn(ans2),
                run_time=1.0,
            )

        self.wait(0.6)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

        # ====================================================
        # SCENE 8: SUMMARY
        # ====================================================
        heading = create_heading_badge("Summary")

        b1 = Text("- Perimeter formulas can be rearranged to find missing dimensions.",
                  font="Poppins", font_size=24, color=PURPLE)
        b2 = Text("- Rectangle: P = 2 x (length + width).",
                  font="Poppins", font_size=24, color=PURPLE)
        b3 = Text("- Square: side = perimeter / 4.",
                  font="Poppins", font_size=24, color=PURPLE)

        bullets = VGroup(b1, b2, b3).arrange(DOWN, aligned_edge=LEFT, buff=0.5)
        bullets.move_to(ORIGIN)

        with self.voiceover(
            text='<bookmark mark="bk_summary_head"/>Summary. '
                 '<bookmark mark="bk_bullet1"/>Perimeter formulas can be rearranged to find missing dimensions. '
                 '<bookmark mark="bk_bullet2"/>Rectangle: use perimeter equals 2 times length plus width. '
                 '<bookmark mark="bk_bullet3"/>Square: side equals perimeter divided by 4.'
        ) as tracker:
            self.wait_until_bookmark("bk_summary_head")
            self.play(FadeIn(heading), run_time=0.6)

            self.wait_until_bookmark("bk_bullet1")
            self.play(FadeIn(b1), run_time=0.7)

            self.wait_until_bookmark("bk_bullet2")
            self.play(FadeIn(b2), run_time=0.7)

            self.wait_until_bookmark("bk_bullet3")
            self.play(FadeIn(b3), run_time=0.7)

        self.wait(0.8)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)