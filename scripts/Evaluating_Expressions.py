import os
import urllib.request
import manimpango
from dotenv import load_dotenv
from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.openai import OpenAIService

load_dotenv()

LAVENDER_BG = "#E7E5F3"
PURPLE      = "#7464CE"
ORANGE_HL   = "#FF9302"
PALE_PURPLE = "#9495D7"


def _setup_poppins():
    base_dir  = os.path.dirname(os.path.abspath(__file__))
    fonts_dir = os.path.join(base_dir, ".fonts")
    os.makedirs(fonts_dir, exist_ok=True)
    base_url = (
        "https://raw.githubusercontent.com/google/fonts/main/ofl/poppins/"
    )
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
                urllib.request.urlretrieve(url, path)
            except Exception as e:
                print(f"Could not download {fname}: {e}")
                continue
        try:
            manimpango.register_font(path)
        except Exception:
            pass


_setup_poppins()

import manim_voiceover.tracker as _vt
_orig = _vt.VoiceoverTracker.time_until_bookmark
_FAILED = []


def _safe_tub(self, mark, buff=0.0, limit=None):
    try:
        return _orig(self, mark, buff, limit)
    except Exception:
        _FAILED.append(mark)
        print(f"WARNING: bookmark '{mark}' not found")
        return 0.0


_vt.VoiceoverTracker.time_until_bookmark = _safe_tub

import atexit


def _report():
    if _FAILED:
        print(f"\nFAILED BOOKMARKS: {_FAILED}")


atexit.register(_report)

TTS_INSTRUCTIONS = """
You are a warm, patient math teacher. Tone: friendly, calm, never rushed.
Pace: moderate-to-slow. Honor commas, dashes, ellipses as pacing marks.
Slow down on variables and formulas. Emphasize shape names and final answers.
Read the script EXACTLY. No filler. No improvisation.
"""


# ─────────────────────── HELPERS ────────────────────────────────

def create_heading_badge(text_str):
    t = Text(text_str, font="Poppins", font_size=28,
             color=WHITE)
    bg = RoundedRectangle(
        corner_radius=0.2, width=t.width + 0.6, height=t.height + 0.3,
        fill_color=PURPLE, fill_opacity=1, stroke_width=0)
    bg.move_to(t)
    return VGroup(bg, t).to_corner(UL, buff=0.3)


def math_obj(tex_str, color=PURPLE, font_size=36):
    return MathTex(tex_str,
                   tex_template=TexFontTemplates.gnu_freesans_tx,
                   color=color, font_size=font_size)


def make_concept_card(text_str, position=ORIGIN,
                      font_size=26, max_chars=55):
    if len(text_str) > max_chars:
        words = text_str.split()
        lines, cur = [], ""
        for w in words:
            if len(cur) + len(w) + 1 <= max_chars:
                cur += (" " if cur else "") + w
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        text_str = "\n".join(lines)
    txt = Text(text_str, font="Poppins", font_size=font_size,
               color=PURPLE)
    bg = RoundedRectangle(
        corner_radius=0.2, width=min(txt.width + 0.8, 10.5),
        height=txt.height + 0.4, fill_color=WHITE, fill_opacity=0.85,
        stroke_color=PALE_PURPLE, stroke_width=1.5)
    bg.move_to(position)
    txt.move_to(bg.get_center())
    return VGroup(bg, txt)


def make_bullet_point(text_str, position=ORIGIN,
                      font_size=26, max_chars=52):
    if len(text_str) > max_chars:
        words = text_str.split()
        lines, cur = [], ""
        for w in words:
            if len(cur) + len(w) + 1 <= max_chars:
                cur += (" " if cur else "") + w
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        text_str = "\n".join(lines)
    dot = Text("\u2022", font="Poppins",
               font_size=font_size + 4, color=ORANGE_HL)
    txt = Text(text_str, font="Poppins",
               font_size=font_size, color=PURPLE)
    row = VGroup(dot, txt).arrange(RIGHT, buff=0.25, aligned_edge=UP)
    row.move_to(position)
    return row


def clear_and_transition(scene, active_mobs, new_bg,
                         ft=0.8, buf=0.2, settle=0.1):
    if active_mobs:
        scene.play(*[FadeOut(m) for m in active_mobs], run_time=ft)
    scene.wait(buf)
    scene.camera.background_color = new_bg
    scene.wait(settle)


SAFE_L, SAFE_R = -6.11, 6.11
SAFE_T, SAFE_B =  3.25, -3.25


def check_safe_margins(mob, name="obj"):
    ok = True
    if mob.get_left()[0]   < SAFE_L: ok = False
    if mob.get_right()[0]  > SAFE_R: ok = False
    if mob.get_top()[1]    > SAFE_T: ok = False
    if mob.get_bottom()[1] < SAFE_B: ok = False
    if not ok:
        print(f"MARGIN WARNING: {name}")
        clamp_to_safe_area(mob)
    return ok


def clamp_to_safe_area(mob):
    sx, sy = 0, 0
    if   mob.get_left()[0]   < SAFE_L: sx = SAFE_L - mob.get_left()[0]
    elif mob.get_right()[0]  > SAFE_R: sx = SAFE_R - mob.get_right()[0]
    if   mob.get_bottom()[1] < SAFE_B: sy = SAFE_B - mob.get_bottom()[1]
    elif mob.get_top()[1]    > SAFE_T: sy = SAFE_T - mob.get_top()[1]
    if sx or sy:
        mob.shift(RIGHT * sx + UP * sy)
    return mob


def check_y_gap(new_mob, existing_mobs, min_gap=0.3, name="new_mob"):
    for mob in existing_mobs:
        if isinstance(mob, VGroup) and len(mob) == 0:
            continue
        new_bottom = new_mob.get_bottom()[1]
        new_top    = new_mob.get_top()[1]
        mob_bottom = mob.get_bottom()[1]
        mob_top    = mob.get_top()[1]
        if new_bottom < mob_top and new_top > mob_bottom:
            shift_needed = mob_top + min_gap - new_bottom
            new_mob.shift(UP * shift_needed)
            print(f"WARNING: '{name}' overlapped. Shifted UP {shift_needed:.2f}")
        elif (new_bottom >= mob_top and
              (new_bottom - mob_top) < min_gap):
            shift_needed = min_gap - (new_bottom - mob_top)
            new_mob.shift(UP * shift_needed)
            print(f"WARNING: '{name}' too close. Shifted UP {shift_needed:.2f}")
    return new_mob


class StepManager:
    LIMITS = {(32, 0.4): 3, (28, 0.3): 4, (24, 0.25): 5, (20, 0.2): 6}

    def __init__(self, scene, start_anchor=None, font_size=28, buff=0.3):
        self.scene  = scene
        self.steps  = []
        self.fs     = font_size
        self.buff   = buff
        self.max    = self.LIMITS.get((font_size, buff), 4)
        self.anchor = (
            start_anchor if start_anchor is not None
            else (UP * 2.0 + LEFT * 3.5)
        )

    def add_step(self, mob, run_time=0.7):
        if len(self.steps) >= self.max:
            print(f"WARNING: StepManager at safe limit ({self.max}).")
        if self.steps:
            mob.next_to(self.steps[-1], DOWN,
                        aligned_edge=LEFT, buff=self.buff)
            self.scene.play(
                *[s.animate.set_opacity(0.4) for s in self.steps],
                FadeIn(mob), run_time=run_time)
        else:
            mob.move_to(self.anchor)
            self.scene.play(FadeIn(mob), run_time=run_time)
        self.steps.append(mob)
        if mob.get_bottom()[1] < SAFE_B:
            print("WARNING: step below safe area")
        return mob

    def get_all(self):
        return VGroup(*self.steps)

    def fadeout_all(self, rt=0.8):
        if self.steps:
            self.scene.play(*[FadeOut(s) for s in self.steps],
                            run_time=rt)
            self.steps.clear()


# ─────────────────────── SCENE ──────────────────────────────────

class EvaluatingExpressionsScene(VoiceoverScene):

    def construct(self):
        self._setup_tts()
        self.show_title()
        self.show_hook()
        self.show_evaluation_steps()
        self.show_example_linear()
        self.show_example_bracket()
        self.show_rule_card()
        self.show_question()
        self.show_solution()
        self.show_summary()

    # ── TTS ─────────────────────────────────────────────────────

    def _setup_tts(self):
        self.set_speech_service(
            OpenAIService(
                voice="shimmer",
                model="gpt-4o-mini-tts",
                instructions=TTS_INSTRUCTIONS,
            )
        )

    # ── TITLE ───────────────────────────────────────────────────

    def show_title(self):
        active_mobs = []
        self.camera.background_color = PURPLE

        with self.voiceover(
            text='<bookmark mark="bk_title"/>Evaluating Expressions.'
        ) as tracker:
            self.wait_until_bookmark("bk_title")
            topic = Text(
                "Evaluating Expressions",
                font="Poppins", font_size=52,
                color=WHITE
            )
            topic.move_to(ORIGIN)
            self.play(FadeIn(topic), run_time=0.8)
            active_mobs.append(topic)

        self.wait(0.4)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── HOOK ────────────────────────────────────────────────────

    def show_hook(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        with self.voiceover(
            text=(
                '<bookmark mark="bk_hook"/>Imagine your teacher announces that every '
                'student\'s total score is calculated as five times the number of '
                'correct answers, plus three bonus marks. '
                'You scored eight correct answers. '
                '<bookmark mark="bk_replace"/>To find your total, — you simply replace '
                'the unknown with eight and calculate. '
                '<bookmark mark="bk_def"/>This process — replacing a letter-number with '
                'a specific value to find the result — is called evaluation.'
            )
        ) as tracker:

            self.wait_until_bookmark("bk_hook")

            # Show the formula with unknown
            formula_lbl = Text(
                "Score formula:", font="Poppins",
                font_size=26, color=PURPLE
            )
            formula_lbl.move_to(UP * 2.1)
            check_safe_margins(formula_lbl, "formula_lbl")
            self.play(FadeIn(formula_lbl), run_time=0.5)
            active_mobs.append(formula_lbl)

            # Pattern F: 5 × a + 3
            t_5    = math_obj(r"5", font_size=44)
            t_x    = math_obj(r"\times", font_size=44)
            t_a    = math_obj(r"a", font_size=44, color=ORANGE_HL)
            t_plus = math_obj(r"+", font_size=44)
            t_3    = math_obj(r"3", font_size=44)

            formula_row = VGroup(
                t_5, t_x, t_a, t_plus, t_3
            ).arrange(RIGHT, buff=0.14)
            formula_row.move_to(UP * 1.2)
            check_safe_margins(formula_row, "formula_row")
            self.play(FadeIn(formula_row), run_time=0.7)
            active_mobs.append(formula_row)

            # a = 8 label
            self.wait_until_bookmark("bk_replace")

            a_val = VGroup(
                math_obj(r"a", font_size=36, color=ORANGE_HL),
                math_obj(r"=", font_size=36),
                math_obj(r"8", font_size=36, color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.14)
            a_val.move_to(UP * 0.1)
            check_safe_margins(a_val, "a_val")
            check_y_gap(a_val, active_mobs, name="a_val")

            # Arrow from a in formula down to a=8
            sub_arrow = Arrow(
                start=t_a.get_bottom() + DOWN * 0.05,
                end=a_val.get_top() + UP * 0.05,
                color=ORANGE_HL, stroke_width=2.5,
                tip_length=0.2, buff=0.05
            )
            self.play(Create(sub_arrow), FadeIn(a_val), run_time=0.7)
            active_mobs.extend([sub_arrow, a_val])

            # Result
            result_row = VGroup(
                math_obj(r"5 \times 8", font_size=38),
                math_obj(r"+", font_size=38),
                math_obj(r"3", font_size=38),
                math_obj(r"=", font_size=38),
                math_obj(r"43", font_size=38, color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.14)
            result_row.move_to(DOWN * 0.9)
            check_safe_margins(result_row, "result_row")
            check_y_gap(result_row, active_mobs, name="result_row")
            self.play(FadeIn(result_row), run_time=0.7)
            active_mobs.append(result_row)

            self.wait_until_bookmark("bk_def")
            def_card = make_concept_card(
                "Evaluation: replacing a letter-number with a value to find the result.",
                position=DOWN * 2.2,
                font_size=24,
            )
            check_safe_margins(def_card, "def_card")
            check_y_gap(def_card, active_mobs, name="def_card")
            self.play(FadeIn(def_card), run_time=0.6)
            active_mobs.append(def_card)

        self.wait(0.4)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── EVALUATION STEPS ────────────────────────────────────────

    def show_evaluation_steps(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        with self.voiceover(
            text=(
                '<bookmark mark="bk_steps"/>To evaluate an expression, — write it clearly, '
                'replace every letter-number with its given value, '
                '<bookmark mark="bk_order"/>and then simplify using the correct order '
                'of operations — multiplication before addition, — and brackets first.'
            )
        ) as tracker:

            self.wait_until_bookmark("bk_steps")

            # Three steps displayed sequentially
            step_a_dot = Text("\u2460", font="Poppins",
                              font_size=30, color=ORANGE_HL)
            step_a_txt = Text(
                "Write the expression clearly.",
                font="Poppins", font_size=26, color=PURPLE
            )
            step_a = VGroup(step_a_dot, step_a_txt).arrange(
                RIGHT, buff=0.2)
            step_a.move_to(UP * 1.5)
            check_safe_margins(step_a, "step_a")
            self.play(FadeIn(step_a), run_time=0.6)
            active_mobs.append(step_a)

            step_b_dot = Text("\u2461", font="Poppins",
                              font_size=30, color=ORANGE_HL)
            step_b_txt = Text(
                "Replace every letter-number with its given value.",
                font="Poppins", font_size=26, color=PURPLE
            )
            step_b = VGroup(step_b_dot, step_b_txt).arrange(
                RIGHT, buff=0.2)
            step_b.move_to(UP * 0.5)
            check_safe_margins(step_b, "step_b")
            check_y_gap(step_b, active_mobs, name="step_b")
            self.play(FadeIn(step_b), run_time=0.6)
            active_mobs.append(step_b)

            self.wait_until_bookmark("bk_order")

            step_c_dot = Text("\u2462", font="Poppins",
                              font_size=30, color=ORANGE_HL)
            step_c_txt = Text(
                "Simplify: brackets first, then multiply, then add.",
                font="Poppins", font_size=26, color=PURPLE
            )
            step_c = VGroup(step_c_dot, step_c_txt).arrange(
                RIGHT, buff=0.2)
            step_c.move_to(DOWN * 0.6)
            check_safe_margins(step_c, "step_c")
            check_y_gap(step_c, active_mobs, name="step_c")
            self.play(FadeIn(step_c), run_time=0.6)
            active_mobs.append(step_c)

            order_card = make_concept_card(
                "Order: Brackets first. Then multiply. Then add or subtract.",
                position=DOWN * 2.0,
                font_size=24,
            )
            check_safe_margins(order_card, "order_card")
            check_y_gap(order_card, active_mobs, name="order_card")
            self.play(FadeIn(order_card), run_time=0.6)
            active_mobs.append(order_card)

        self.wait(0.4)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── EXAMPLE: LINEAR (3a + 7, a=5) ───────────────────────────

    def show_example_linear(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        with self.voiceover(
            text=(
                '<bookmark mark="bk_ex1"/>For example, — if the expression is three a '
                'plus seven, — and a equals five, — we replace a with five. '
                '<bookmark mark="bk_ex1_calc"/>Three times five plus seven, '
                'gives fifteen plus seven, '
                '<bookmark mark="bk_ex1_ans"/>which equals twenty-two.'
            )
        ) as tracker:

            self.wait_until_bookmark("bk_ex1")

            ex_lbl = Text(
                "Expression:", font="Poppins",
                font_size=26, color=PURPLE
            )
            ex_lbl.move_to(UP * 2.1)
            check_safe_margins(ex_lbl, "ex_lbl")
            self.play(FadeIn(ex_lbl), run_time=0.4)
            active_mobs.append(ex_lbl)

            # Pattern F: 3a + 7
            t_3a   = math_obj(r"3a", font_size=44)
            t_plus = math_obj(r"+", font_size=44)
            t_7    = math_obj(r"7", font_size=44)

            expr_row = VGroup(t_3a, t_plus, t_7).arrange(RIGHT, buff=0.16)
            expr_row.move_to(UP * 1.3)
            check_safe_margins(expr_row, "expr_row")
            self.play(FadeIn(expr_row), run_time=0.6)
            active_mobs.append(expr_row)

            # a = 5 annotation
            a5_lbl = VGroup(
                math_obj(r"a", font_size=32, color=ORANGE_HL),
                math_obj(r"=", font_size=32),
                math_obj(r"5", font_size=32, color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.12)
            a5_lbl.move_to(UP * 0.4)
            check_safe_margins(a5_lbl, "a5_lbl")
            check_y_gap(a5_lbl, active_mobs, name="a5_lbl")

            sub_arr = Arrow(
                start=t_3a.get_bottom() + DOWN * 0.05,
                end=a5_lbl.get_top() + UP * 0.05,
                color=ORANGE_HL, stroke_width=2.0,
                tip_length=0.18, buff=0.05
            )
            self.play(Create(sub_arr), FadeIn(a5_lbl), run_time=0.6)
            active_mobs.extend([sub_arr, a5_lbl])

            self.wait_until_bookmark("bk_ex1_calc")

            step1 = VGroup(
                math_obj(r"=", font_size=40),
                math_obj(r"3 \times 5", font_size=40, color=ORANGE_HL),
                math_obj(r"+", font_size=40),
                math_obj(r"7", font_size=40),
            ).arrange(RIGHT, buff=0.14)
            step1.move_to(DOWN * 0.5)
            check_safe_margins(step1, "step1")
            check_y_gap(step1, active_mobs, name="step1")
            self.play(FadeIn(step1), run_time=0.7)
            active_mobs.append(step1)

            step2 = VGroup(
                math_obj(r"=", font_size=40),
                math_obj(r"15", font_size=40, color=ORANGE_HL),
                math_obj(r"+", font_size=40),
                math_obj(r"7", font_size=40),
            ).arrange(RIGHT, buff=0.14)
            step2.next_to(step1, DOWN, buff=0.38)
            check_safe_margins(step2, "step2")
            check_y_gap(step2, active_mobs, name="step2")
            self.play(FadeIn(step2), run_time=0.7)
            active_mobs.append(step2)

            self.wait_until_bookmark("bk_ex1_ans")

            step3 = VGroup(
                math_obj(r"=", font_size=44),
                math_obj(r"22", font_size=44, color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.14)
            step3.next_to(step2, DOWN, buff=0.38)
            check_safe_margins(step3, "step3")
            check_y_gap(step3, active_mobs, name="step3")
            self.play(FadeIn(step3), run_time=0.7)
            active_mobs.append(step3)

            ans_box = SurroundingRectangle(
                step3, color=ORANGE_HL,
                corner_radius=0.15,
                stroke_width=2.5,
                buff=0.15
            )
            self.play(Create(ans_box), run_time=0.5)
            active_mobs.append(ans_box)

        self.wait(0.4)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── EXAMPLE: BRACKET (2(b+4), b=3) ──────────────────────────

    def show_example_bracket(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        with self.voiceover(
            text=(
                '<bookmark mark="bk_brack"/>Be careful with brackets. '
                'If the expression is two times the quantity b plus four, '
                '— and b equals three, — work inside the bracket first — '
                '<bookmark mark="bk_inside"/>three plus four equals seven. '
                '<bookmark mark="bk_then_mult"/>Then multiply — two times seven equals fourteen.'
            )
        ) as tracker:

            self.wait_until_bookmark("bk_brack")

            warn_card = make_concept_card(
                "Be careful with brackets — evaluate inside first!",
                position=UP * 2.1,
                font_size=26,
            )
            check_safe_margins(warn_card, "warn_card")
            self.play(FadeIn(warn_card), run_time=0.6)
            active_mobs.append(warn_card)

            # Pattern F: 2(b + 4), b=3
            t_2      = math_obj(r"2", font_size=44)
            t_open   = math_obj(r"(", font_size=44)
            t_b      = math_obj(r"b", font_size=44, color=ORANGE_HL)
            t_plus   = math_obj(r"+", font_size=44)
            t_4      = math_obj(r"4", font_size=44)
            t_close  = math_obj(r")", font_size=44)

            expr_row = VGroup(
                t_2, t_open, t_b, t_plus, t_4, t_close
            ).arrange(RIGHT, buff=0.12)
            expr_row.move_to(UP * 1.0)
            check_safe_margins(expr_row, "expr_row")
            self.play(FadeIn(expr_row), run_time=0.7)
            active_mobs.append(expr_row)

            b3_lbl = VGroup(
                math_obj(r"b", font_size=32, color=ORANGE_HL),
                math_obj(r"=", font_size=32),
                math_obj(r"3", font_size=32, color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.12)
            b3_lbl.move_to(UP * 0.05)
            check_safe_margins(b3_lbl, "b3_lbl")
            check_y_gap(b3_lbl, active_mobs, name="b3_lbl")

            b_arrow = Arrow(
                start=t_b.get_bottom() + DOWN * 0.05,
                end=b3_lbl.get_top() + UP * 0.05,
                color=ORANGE_HL, stroke_width=2.0,
                tip_length=0.18, buff=0.05
            )
            self.play(Create(b_arrow), FadeIn(b3_lbl), run_time=0.6)
            active_mobs.extend([b_arrow, b3_lbl])

            self.wait_until_bookmark("bk_inside")

            # Step: inside bracket first
            inside_step = VGroup(
                math_obj(r"=", font_size=40),
                math_obj(r"2", font_size=40),
                math_obj(r"(", font_size=40),
                math_obj(r"3", font_size=40, color=ORANGE_HL),
                math_obj(r"+", font_size=40),
                math_obj(r"4", font_size=40),
                math_obj(r")", font_size=40),
                math_obj(r"=", font_size=40),
                math_obj(r"2", font_size=40),
                math_obj(r"(", font_size=40),
                math_obj(r"7", font_size=40, color=ORANGE_HL),
                math_obj(r")", font_size=40),
            ).arrange(RIGHT, buff=0.10)
            inside_step.move_to(DOWN * 0.8)
            check_safe_margins(inside_step, "inside_step")
            check_y_gap(inside_step, active_mobs, name="inside_step")
            self.play(FadeIn(inside_step), run_time=0.8)
            active_mobs.append(inside_step)

            self.wait_until_bookmark("bk_then_mult")

            final_step = VGroup(
                math_obj(r"=", font_size=44),
                math_obj(r"14", font_size=44, color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.14)
            final_step.next_to(inside_step, DOWN, buff=0.4)
            check_safe_margins(final_step, "final_step")
            check_y_gap(final_step, active_mobs, name="final_step")
            self.play(FadeIn(final_step), run_time=0.7)
            active_mobs.append(final_step)

            ans_box = SurroundingRectangle(
                final_step, color=ORANGE_HL,
                corner_radius=0.15,
                stroke_width=2.5,
                buff=0.15
            )
            self.play(Create(ans_box), run_time=0.5)
            active_mobs.append(ans_box)

        self.wait(0.4)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── RULE CARD ───────────────────────────────────────────────

    def show_rule_card(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        with self.voiceover(
            text=(
                '<bookmark mark="bk_rule"/>The rule is always the same — '
                'substitute first, — then calculate step by step.'
            )
        ) as tracker:

            self.wait_until_bookmark("bk_rule")

            rule_bg = RoundedRectangle(
                corner_radius=0.25,
                width=9.0, height=1.6,
                fill_color=WHITE, fill_opacity=0.92,
                stroke_color=ORANGE_HL, stroke_width=3.0
            )
            rule_bg.move_to(ORIGIN)

            rule_txt = Text(
                "Substitute first — then calculate step by step.",
                font="Poppins", font_size=30, color=PURPLE
            )
            rule_txt.move_to(rule_bg.get_center())
            rule_card = VGroup(rule_bg, rule_txt)
            check_safe_margins(rule_card, "rule_card")
            self.play(FadeIn(rule_card), run_time=0.8)
            active_mobs.append(rule_card)

        self.wait(0.5)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── QUESTION ────────────────────────────────────────────────

    def show_question(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Question")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        with self.voiceover(
            text=(
                '<bookmark mark="bk_q"/>The expression for a student\'s score is '
                'four m minus five, — where m is the number of questions answered correctly. '
                '<bookmark mark="bk_q2"/>Find the score when m equals eight.'
            )
        ) as tracker:

            self.wait_until_bookmark("bk_q")

            q_lbl = Text(
                "Student's score expression:",
                font="Poppins", font_size=26, color=PURPLE
            )
            q_lbl.move_to(UP * 2.1)
            check_safe_margins(q_lbl, "q_lbl")
            self.play(FadeIn(q_lbl), run_time=0.5)
            active_mobs.append(q_lbl)

            # Pattern F: 4m - 5
            q_4m    = math_obj(r"4m", font_size=48)
            q_minus = math_obj(r"-", font_size=48)
            q_5     = math_obj(r"5", font_size=48)

            q_expr = VGroup(q_4m, q_minus, q_5).arrange(RIGHT, buff=0.16)
            q_expr.move_to(UP * 1.0)
            check_safe_margins(q_expr, "q_expr")
            self.play(FadeIn(q_expr), run_time=0.7)
            active_mobs.append(q_expr)

            where_lbl = Text(
                "where m = number of correct answers",
                font="Poppins", font_size=24, color=PALE_PURPLE
            )
            where_lbl.move_to(UP * 0.1)
            check_safe_margins(where_lbl, "where_lbl")
            check_y_gap(where_lbl, active_mobs, name="where_lbl")
            self.play(FadeIn(where_lbl), run_time=0.5)
            active_mobs.append(where_lbl)

            self.wait_until_bookmark("bk_q2")

            find_card = make_concept_card(
                "Find the score when m = 8.",
                position=DOWN * 1.0,
                font_size=28,
            )
            check_safe_margins(find_card, "find_card")
            check_y_gap(find_card, active_mobs, name="find_card")
            self.play(FadeIn(find_card), run_time=0.6)
            active_mobs.append(find_card)

        self.wait(0.4)
        self._q_active = active_mobs[:]
        self._q_badge  = badge

    # ── SOLUTION ────────────────────────────────────────────────

    def show_solution(self):
        active_mobs = self._q_active[:]

        old_badge = self._q_badge
        new_badge = create_heading_badge("Solution")
        self.play(FadeOut(old_badge), FadeIn(new_badge), run_time=0.5)
        if old_badge in active_mobs:
            active_mobs.remove(old_badge)
        active_mobs.append(new_badge)

        mobs_to_fade = [m for m in active_mobs if m is not new_badge]
        if mobs_to_fade:
            self.play(*[FadeOut(m) for m in mobs_to_fade], run_time=0.6)
        for m in mobs_to_fade:
            if m in active_mobs:
                active_mobs.remove(m)
        self.wait(0.2)

        with self.voiceover(
            text=(
                '<bookmark mark="bk_s1"/>Replace m with eight. '
                '<bookmark mark="bk_s2"/>Four times eight minus five. '
                '<bookmark mark="bk_s3"/>Thirty-two minus five. '
                '<bookmark mark="bk_s4"/>The score is twenty-seven. '
                '<bookmark mark="bk_s5"/>This same process is used by engineers and scientists '
                'when applying formulas to real measurements.'
            )
        ) as tracker:

            mgr = StepManager(
                self,
                start_anchor=UP * 1.8 + LEFT * 0.5,
                font_size=30,
                buff=0.40
            )

            # Step 1: substitute
            self.wait_until_bookmark("bk_s1")
            s1 = VGroup(
                math_obj(r"m", font_size=34, color=ORANGE_HL),
                math_obj(r"=", font_size=34),
                math_obj(r"8", font_size=34, color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.16)
            mgr.add_step(s1)
            active_mobs.append(s1)

            # Step 2: write substituted expression
            self.wait_until_bookmark("bk_s2")
            s2 = VGroup(
                math_obj(r"4 \times 8", font_size=34, color=ORANGE_HL),
                math_obj(r"-", font_size=34),
                math_obj(r"5", font_size=34),
            ).arrange(RIGHT, buff=0.16)
            mgr.add_step(s2)
            active_mobs.append(s2)

            # Step 3: multiply first
            self.wait_until_bookmark("bk_s3")
            s3 = VGroup(
                math_obj(r"=", font_size=34),
                math_obj(r"32", font_size=34, color=ORANGE_HL),
                math_obj(r"-", font_size=34),
                math_obj(r"5", font_size=34),
            ).arrange(RIGHT, buff=0.16)
            mgr.add_step(s3)
            active_mobs.append(s3)

            # Step 4: final answer
            self.wait_until_bookmark("bk_s4")
            s4 = VGroup(
                math_obj(r"=", font_size=38),
                math_obj(r"27", font_size=38, color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.16)
            mgr.add_step(s4)
            active_mobs.append(s4)

            ans_box = SurroundingRectangle(
                s4, color=ORANGE_HL,
                corner_radius=0.15,
                stroke_width=2.5,
                buff=0.15
            )
            self.play(Create(ans_box), run_time=0.6)
            active_mobs.append(ans_box)

            # Real-world connection
            self.wait_until_bookmark("bk_s5")
            real_card = make_concept_card(
                "Engineers and scientists use this same process with real measurements.",
                position=DOWN * 2.3,
                font_size=22,
            )
            check_safe_margins(real_card, "real_card")
            check_y_gap(real_card, active_mobs, name="real_card")
            self.play(FadeIn(real_card), run_time=0.6)
            active_mobs.append(real_card)

        self.wait(0.6)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── SUMMARY ─────────────────────────────────────────────────

    def show_summary(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Summary")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        summary_points = [
            "Evaluation means replacing each letter-number with its given value.",
            "Apply the correct order of operations after substituting.",
            "Substitute first — then calculate carefully, step by step.",
        ]
        positions = [UP * 1.5, ORIGIN, DOWN * 1.5]

        with self.voiceover(
            text=(
                '<bookmark mark="bk_sum1"/>Evaluation means replacing each letter-number '
                'with its given value. '
                '<bookmark mark="bk_sum2"/>Apply the correct order of operations '
                'after substituting. '
                '<bookmark mark="bk_sum3"/>Substitute first — then calculate carefully, '
                'step by step.'
            )
        ) as tracker:

            for i, (txt, pos) in enumerate(
                zip(summary_points, positions)
            ):
                self.wait_until_bookmark(f"bk_sum{i+1}")
                bullet = make_bullet_point(txt, position=pos)
                check_safe_margins(bullet, f"bullet_{i+1}")
                self.play(FadeIn(bullet), run_time=0.7)
                active_mobs.append(bullet)

        self.wait(0.6)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()