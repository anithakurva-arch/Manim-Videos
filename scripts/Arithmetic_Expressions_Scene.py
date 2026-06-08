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

class ArithmeticExpressionsScene(VoiceoverScene):

    def construct(self):
        self._setup_tts()
        self.show_title()
        self.show_hook()
        self.show_terms_and_properties()
        self.show_distributive_property()
        self.show_brackets_concept()
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
            text='<bookmark mark="bk_title"/>Revisiting Arithmetic Expressions.'
        ) as tracker:
            self.wait_until_bookmark("bk_title")
            topic = Text(
                "Revisiting Arithmetic\nExpressions",
                font="Poppins", font_size=48,
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
                '<bookmark mark="bk_hook"/>Suppose you buy three notebooks at twelve rupees each, '
                'and then two more at the same price. '
                'You could calculate three times twelve, and two times twelve separately, '
                'then add them. '
                '<bookmark mark="bk_or"/>Or you could say five times twelve directly. '
                'Both give sixty. '
                '<bookmark mark="bk_point"/>This is exactly how arithmetic expressions work '
                '— they can always be rewritten without changing their value.'
            )
        ) as tracker:

            self.wait_until_bookmark("bk_hook")

            # Pattern C: two approaches side by side
            # Left: separate calculation
            lbl_left = Text("Separate:", font="Poppins",
                            font_size=24, color=PURPLE)
            calc_left = VGroup(
                math_obj(r"3 \times 12", font_size=34),
                math_obj(r"+", font_size=34),
                math_obj(r"2 \times 12", font_size=34),
                math_obj(r"=", font_size=34),
                math_obj(r"60", font_size=34, color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.12)
            col_left = VGroup(lbl_left, calc_left).arrange(DOWN, buff=0.2)
            col_left.move_to(LEFT * 3.0 + UP * 0.6)
            check_safe_margins(col_left, "col_left")
            self.play(FadeIn(col_left), run_time=0.8)
            active_mobs.append(col_left)

            self.wait_until_bookmark("bk_or")

            # Right: direct calculation
            lbl_right = Text("Direct:", font="Poppins",
                             font_size=24, color=PURPLE)
            calc_right = VGroup(
                math_obj(r"5 \times 12", font_size=34),
                math_obj(r"=", font_size=34),
                math_obj(r"60", font_size=34, color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.12)
            col_right = VGroup(lbl_right, calc_right).arrange(DOWN, buff=0.2)
            col_right.move_to(RIGHT * 3.0 + UP * 0.6)
            check_safe_margins(col_right, "col_right")
            self.play(FadeIn(col_right), run_time=0.8)
            active_mobs.append(col_right)

            # Equals sign between columns
            eq_sign = math_obj(r"=", font_size=40, color=ORANGE_HL)
            eq_sign.move_to(UP * 0.35)
            check_safe_margins(eq_sign, "eq_sign")
            self.play(FadeIn(eq_sign), run_time=0.4)
            active_mobs.append(eq_sign)

            self.wait_until_bookmark("bk_point")
            point_card = make_concept_card(
                "Expressions can always be rewritten without changing their value.",
                position=DOWN * 1.6,
                font_size=24,
            )
            check_safe_margins(point_card, "point_card")
            check_y_gap(point_card, active_mobs, name="point_card")
            self.play(FadeIn(point_card), run_time=0.7)
            active_mobs.append(point_card)

        self.wait(0.4)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── TERMS AND PROPERTIES ────────────────────────────────────

    def show_terms_and_properties(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        with self.voiceover(
            text=(
                '<bookmark mark="bk_terms"/>Every arithmetic expression is made up of '
                'individual terms, — separated by addition or subtraction. '
                '<bookmark mark="bk_swap"/>The swapping property lets us change the order '
                'of terms. '
                '<bookmark mark="bk_group"/>The grouping property lets us change how terms '
                'are bracketed. '
                '<bookmark mark="bk_neither"/>Neither changes the value.'
            )
        ) as tracker:

            # Terms concept — Pattern F: show expression split into terms
            self.wait_until_bookmark("bk_terms")

            t_a = math_obj(r"12", font_size=42)
            t_plus1 = math_obj(r"+", font_size=42)
            t_b = math_obj(r"7", font_size=42)
            t_plus2 = math_obj(r"+", font_size=42)
            t_c = math_obj(r"5", font_size=42)

            expr_row = VGroup(
                t_a, t_plus1, t_b, t_plus2, t_c
            ).arrange(RIGHT, buff=0.16)
            expr_row.move_to(UP * 1.8)
            check_safe_margins(expr_row, "expr_row")
            self.play(FadeIn(expr_row), run_time=0.7)
            active_mobs.append(expr_row)

            # Underline each term
            ul_a = Underline(t_a, color=ORANGE_HL, stroke_width=2.5)
            ul_b = Underline(t_b, color=ORANGE_HL, stroke_width=2.5)
            ul_c = Underline(t_c, color=ORANGE_HL, stroke_width=2.5)
            self.play(
                Create(ul_a), Create(ul_b), Create(ul_c),
                run_time=0.6
            )
            active_mobs.extend([ul_a, ul_b, ul_c])

            terms_label = Text("Terms", font="Poppins",
                               font_size=22, color=ORANGE_HL)
            terms_label.next_to(expr_row, DOWN, buff=0.35)
            check_safe_margins(terms_label, "terms_label")
            self.play(FadeIn(terms_label), run_time=0.4)
            active_mobs.append(terms_label)

            # Swapping property — Pattern A
            self.wait_until_bookmark("bk_swap")

            swap_lbl = Text("Swapping:", font="Poppins",
                            font_size=24, color=PURPLE)

            orig_row = VGroup(
                math_obj(r"12", font_size=34),
                math_obj(r"+", font_size=34),
                math_obj(r"7", font_size=34),
            ).arrange(RIGHT, buff=0.12)

            arr_swap = math_obj(r"\rightarrow", font_size=34)

            swap_row = VGroup(
                math_obj(r"7", font_size=34, color=ORANGE_HL),
                math_obj(r"+", font_size=34),
                math_obj(r"12", font_size=34, color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.12)

            # Use Arrow instead of \rightarrow
            swap_arrow = Arrow(
                start=ORIGIN, end=RIGHT * 0.6,
                color=PURPLE, stroke_width=2.0,
                tip_length=0.18, buff=0.0
            )

            swap_line = VGroup(
                orig_row, swap_arrow, swap_row
            ).arrange(RIGHT, buff=0.25)
            swap_block = VGroup(swap_lbl, swap_line).arrange(DOWN, buff=0.2)
            swap_block.move_to(LEFT * 2.5 + UP * 0.2)
            check_safe_margins(swap_block, "swap_block")
            check_y_gap(swap_block, active_mobs, name="swap_block")
            self.play(FadeIn(swap_block), run_time=0.7)
            active_mobs.append(swap_block)

            # Grouping property — Pattern A
            self.wait_until_bookmark("bk_group")

            grp_lbl = Text("Grouping:", font="Poppins",
                           font_size=24, color=PURPLE)

            grp_orig = VGroup(
                math_obj(r"(12+7)", font_size=34),
                math_obj(r"+", font_size=34),
                math_obj(r"5", font_size=34),
            ).arrange(RIGHT, buff=0.12)

            grp_arrow = Arrow(
                start=ORIGIN, end=RIGHT * 0.6,
                color=PURPLE, stroke_width=2.0,
                tip_length=0.18, buff=0.0
            )

            grp_new = VGroup(
                math_obj(r"12", font_size=34, color=ORANGE_HL),
                math_obj(r"+", font_size=34),
                math_obj(r"(7+5)", font_size=34, color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.12)

            grp_line = VGroup(
                grp_orig, grp_arrow, grp_new
            ).arrange(RIGHT, buff=0.25)
            grp_block = VGroup(grp_lbl, grp_line).arrange(DOWN, buff=0.2)
            grp_block.move_to(RIGHT * 2.0 + UP * 0.2)
            check_safe_margins(grp_block, "grp_block")
            check_y_gap(grp_block, active_mobs, name="grp_block")
            self.play(FadeIn(grp_block), run_time=0.7)
            active_mobs.append(grp_block)

            self.wait_until_bookmark("bk_neither")
            neither_card = make_concept_card(
                "Neither changes the value.",
                position=DOWN * 2.0,
                font_size=26,
            )
            check_safe_margins(neither_card, "neither_card")
            check_y_gap(neither_card, active_mobs, name="neither_card")
            self.play(FadeIn(neither_card), run_time=0.6)
            active_mobs.append(neither_card)

        self.wait(0.4)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── DISTRIBUTIVE PROPERTY ───────────────────────────────────

    def show_distributive_property(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        with self.voiceover(
            text=(
                '<bookmark mark="bk_dist_intro"/>The distributive property takes this further. '
                'Multiplying a number by a sum, — is the same as multiplying it by each part '
                'separately. '
                '<bookmark mark="bk_dist_ex"/>So four times the quantity seven plus three, '
                '— equals four times seven, plus four times three, '
                '<bookmark mark="bk_dist_calc"/>which equals twenty-eight plus twelve, '
                '<bookmark mark="bk_dist_ans"/>which equals forty.'
            )
        ) as tracker:

            self.wait_until_bookmark("bk_dist_intro")

            rule_card = make_concept_card(
                "Multiply a number by each part of the sum separately.",
                position=UP * 2.0,
                font_size=26,
            )
            check_safe_margins(rule_card, "rule_card")
            self.play(FadeIn(rule_card), run_time=0.7)
            active_mobs.append(rule_card)

            # Pattern F: 4 × (7 + 3) — split MathTex objects
            self.wait_until_bookmark("bk_dist_ex")

            t_4      = math_obj(r"4", font_size=44)
            t_times  = math_obj(r"\times", font_size=44)
            t_open   = math_obj(r"(", font_size=44)
            t_7      = math_obj(r"7", font_size=44)
            t_plus   = math_obj(r"+", font_size=44)
            t_3      = math_obj(r"3", font_size=44)
            t_close  = math_obj(r")", font_size=44)

            orig_expr = VGroup(
                t_4, t_times, t_open, t_7, t_plus, t_3, t_close
            ).arrange(RIGHT, buff=0.12)
            orig_expr.move_to(UP * 0.9)
            check_safe_margins(orig_expr, "orig_expr")
            self.play(FadeIn(orig_expr), run_time=0.7)
            active_mobs.append(orig_expr)

            # Pattern B: arrows from 4 to each inner term
            arr_to_7 = Arrow(
                start=t_4.get_bottom() + DOWN * 0.05,
                end=t_7.get_bottom() + DOWN * 0.35,
                color=ORANGE_HL, stroke_width=2.5,
                tip_length=0.18, buff=0.05
            )
            arr_to_3 = Arrow(
                start=t_4.get_bottom() + DOWN * 0.05,
                end=t_3.get_bottom() + DOWN * 0.35,
                color=ORANGE_HL, stroke_width=2.5,
                tip_length=0.18, buff=0.05
            )
            self.play(
                Create(arr_to_7), Create(arr_to_3),
                t_7.animate.set_color(ORANGE_HL),
                t_3.animate.set_color(ORANGE_HL),
                run_time=0.8
            )
            active_mobs.extend([arr_to_7, arr_to_3])

            # Expanded form
            expanded = VGroup(
                math_obj(r"=", font_size=40),
                math_obj(r"4 \times 7", font_size=40, color=ORANGE_HL),
                math_obj(r"+", font_size=40),
                math_obj(r"4 \times 3", font_size=40, color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.14)
            expanded.next_to(orig_expr, DOWN, buff=0.55)
            check_safe_margins(expanded, "expanded")
            check_y_gap(expanded, active_mobs, name="expanded")
            self.play(FadeIn(expanded), run_time=0.7)
            active_mobs.append(expanded)

            self.wait_until_bookmark("bk_dist_calc")
            calc_step = VGroup(
                math_obj(r"=", font_size=40),
                math_obj(r"28", font_size=40),
                math_obj(r"+", font_size=40),
                math_obj(r"12", font_size=40),
            ).arrange(RIGHT, buff=0.14)
            calc_step.next_to(expanded, DOWN, buff=0.4)
            check_safe_margins(calc_step, "calc_step")
            check_y_gap(calc_step, active_mobs, name="calc_step")
            self.play(FadeIn(calc_step), run_time=0.7)
            active_mobs.append(calc_step)

            self.wait_until_bookmark("bk_dist_ans")
            ans_step = VGroup(
                math_obj(r"=", font_size=44),
                math_obj(r"40", font_size=44, color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.14)
            ans_step.next_to(calc_step, DOWN, buff=0.4)
            check_safe_margins(ans_step, "ans_step")
            check_y_gap(ans_step, active_mobs, name="ans_step")
            self.play(FadeIn(ans_step), run_time=0.7)
            active_mobs.append(ans_step)

        self.wait(0.5)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── BRACKETS CONCEPT ────────────────────────────────────────

    def show_brackets_concept(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        with self.voiceover(
            text=(
                '<bookmark mark="bk_brack"/>Brackets indicate which part of the expression '
                'should be evaluated first. '
                '<bookmark mark="bk_careful"/>Using them carefully, — keeps our rewriting '
                'accurate and unambiguous.'
            )
        ) as tracker:

            self.wait_until_bookmark("bk_brack")

            # Pattern C: with vs without brackets
            lbl_without = Text("Without brackets:", font="Poppins",
                               font_size=24, color=PURPLE)
            expr_without = VGroup(
                math_obj(r"3", font_size=38),
                math_obj(r"+", font_size=38),
                math_obj(r"4", font_size=38),
                math_obj(r"\times", font_size=38),
                math_obj(r"2", font_size=38),
                math_obj(r"=", font_size=38),
                math_obj(r"11", font_size=38, color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.12)
            note_without = Text("(multiply first)", font="Poppins",
                                font_size=20, color=PALE_PURPLE)
            col_without = VGroup(
                lbl_without, expr_without, note_without
            ).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
            col_without.move_to(LEFT * 3.0 + UP * 0.5)
            check_safe_margins(col_without, "col_without")
            self.play(FadeIn(col_without), run_time=0.8)
            active_mobs.append(col_without)

            lbl_with = Text("With brackets:", font="Poppins",
                            font_size=24, color=PURPLE)
            expr_with = VGroup(
                math_obj(r"(3", font_size=38, color=ORANGE_HL),
                math_obj(r"+", font_size=38, color=ORANGE_HL),
                math_obj(r"4)", font_size=38, color=ORANGE_HL),
                math_obj(r"\times", font_size=38),
                math_obj(r"2", font_size=38),
                math_obj(r"=", font_size=38),
                math_obj(r"14", font_size=38, color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.12)
            note_with = Text("(add first)", font="Poppins",
                             font_size=20, color=PALE_PURPLE)
            col_with = VGroup(
                lbl_with, expr_with, note_with
            ).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
            col_with.move_to(RIGHT * 2.8 + UP * 0.5)
            check_safe_margins(col_with, "col_with")
            self.play(FadeIn(col_with), run_time=0.8)
            active_mobs.append(col_with)

            self.wait_until_bookmark("bk_careful")
            careful_card = make_concept_card(
                "Brackets keep our rewriting accurate and unambiguous.",
                position=DOWN * 1.9,
                font_size=24,
            )
            check_safe_margins(careful_card, "careful_card")
            check_y_gap(careful_card, active_mobs, name="careful_card")
            self.play(FadeIn(careful_card), run_time=0.7)
            active_mobs.append(careful_card)

        self.wait(0.4)
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
                '<bookmark mark="bk_q"/>Rewrite and simplify six times the quantity nine '
                'plus four, — using the distributive property. '
                'Then verify your answer.'
            )
        ) as tracker:

            self.wait_until_bookmark("bk_q")

            q_label = Text(
                "Rewrite and simplify using the distributive property:",
                font="Poppins", font_size=24, color=PURPLE
            )
            q_label.move_to(UP * 2.1)
            check_safe_margins(q_label, "q_label")
            self.play(FadeIn(q_label), run_time=0.6)
            active_mobs.append(q_label)

            q_expr = VGroup(
                math_obj(r"6", font_size=48),
                math_obj(r"\times", font_size=48),
                math_obj(r"(", font_size=48),
                math_obj(r"9", font_size=48),
                math_obj(r"+", font_size=48),
                math_obj(r"4", font_size=48),
                math_obj(r")", font_size=48),
            ).arrange(RIGHT, buff=0.12)
            q_expr.move_to(UP * 0.5)
            check_safe_margins(q_expr, "q_expr")
            self.play(FadeIn(q_expr), run_time=0.9)
            active_mobs.append(q_expr)

            verify_card = make_concept_card(
                "Then verify your answer.",
                position=DOWN * 1.2,
                font_size=24,
            )
            check_safe_margins(verify_card, "verify_card")
            check_y_gap(verify_card, active_mobs, name="verify_card")
            self.play(FadeIn(verify_card), run_time=0.6)
            active_mobs.append(verify_card)

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
                '<bookmark mark="bk_s1"/>Distribute — six times nine, plus six times four. '
                '<bookmark mark="bk_s2"/>Equals fifty-four plus twenty-four. '
                '<bookmark mark="bk_s3"/>Equals seventy-eight. '
                '<bookmark mark="bk_s4"/>Verify — six times thirteen equals seventy-eight. '
                'The result is verified.'
            )
        ) as tracker:

            mgr = StepManager(
                self,
                start_anchor=UP * 1.6 + LEFT * 0.5,
                font_size=28,
                buff=0.38
            )

            # Step 1: distribute
            self.wait_until_bookmark("bk_s1")
            s1 = VGroup(
                math_obj(r"6 \times 9", font_size=32, color=ORANGE_HL),
                math_obj(r"+", font_size=32),
                math_obj(r"6 \times 4", font_size=32, color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.14)
            mgr.add_step(s1)
            active_mobs.append(s1)

            # Step 2: compute each product
            self.wait_until_bookmark("bk_s2")
            s2 = VGroup(
                math_obj(r"=", font_size=32),
                math_obj(r"54", font_size=32),
                math_obj(r"+", font_size=32),
                math_obj(r"24", font_size=32),
            ).arrange(RIGHT, buff=0.14)
            mgr.add_step(s2)
            active_mobs.append(s2)

            # Step 3: final sum
            self.wait_until_bookmark("bk_s3")
            s3 = VGroup(
                math_obj(r"=", font_size=36),
                math_obj(r"78", font_size=36, color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.14)
            mgr.add_step(s3)
            active_mobs.append(s3)

            ans_box = SurroundingRectangle(
                s3, color=ORANGE_HL,
                corner_radius=0.15,
                stroke_width=2.5,
                buff=0.15
            )
            self.play(Create(ans_box), run_time=0.6)
            active_mobs.append(ans_box)

            # Step 4: verify
            self.wait_until_bookmark("bk_s4")
            mgr.fadeout_all(rt=0.6)
            for mob in [s1, s2, s3]:
                if mob in active_mobs:
                    active_mobs.remove(mob)
            if ans_box in active_mobs:
                active_mobs.remove(ans_box)
            self.play(FadeOut(ans_box), run_time=0.3)

            mgr2 = StepManager(
                self,
                start_anchor=UP * 1.0 + LEFT * 0.5,
                font_size=28,
                buff=0.38
            )

            verify_step = VGroup(
                math_obj(r"6 \times 13", font_size=32),
                math_obj(r"=", font_size=32),
                math_obj(r"78", font_size=32, color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.14)
            mgr2.add_step(verify_step)
            active_mobs.append(verify_step)

            verified_label = Text(
                "The result is verified.",
                font="Poppins", font_size=28, color=ORANGE_HL
            )
            verified_label.next_to(verify_step, DOWN, buff=0.5)
            check_safe_margins(verified_label, "verified_label")
            check_y_gap(verified_label, active_mobs, name="verified_label")

            chk = MathTex(r"\checkmark",
                          tex_template=TexFontTemplates.gnu_freesans_tx,
                          font_size=42, color=ORANGE_HL)
            chk.next_to(verified_label, RIGHT, buff=0.25)
            check_safe_margins(chk, "chk")

            self.play(FadeIn(verified_label), FadeIn(chk), run_time=0.7)
            active_mobs.extend([verified_label, chk])

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
            "Every expression is a sum of terms that can be reordered or regrouped freely.",
            "The distributive property: multiply across every term inside the brackets.",
            "Rewriting using these properties never changes the value of an expression.",
        ]
        positions = [UP * 1.5, ORIGIN, DOWN * 1.5]

        with self.voiceover(
            text=(
                '<bookmark mark="bk_sum1"/>Every expression is a sum of terms, '
                'that can be reordered or regrouped freely. '
                '<bookmark mark="bk_sum2"/>The distributive property — multiply across '
                'every term inside the brackets. '
                '<bookmark mark="bk_sum3"/>Rewriting using these properties, '
                'never changes the value of an expression.'
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