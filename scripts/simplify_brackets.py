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

FRACTIONS: When you see "X over Y", say exactly "X over Y".
Never say "X-Yths" or common names like "one half" or "three quarters".
Example: "three over four" NOT "three quarters".

Read the script EXACTLY. No filler. No improvisation.
"""


# ─────────────────────── HELPER FUNCTIONS ───────────────────────

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
SAFE_T, SAFE_B = 3.25, -3.25


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
            print(f"WARNING: '{name}' overlapped. Shifted UP by {shift_needed:.2f}")
        elif (new_bottom >= mob_top and
              (new_bottom - mob_top) < min_gap):
            shift_needed = min_gap - (new_bottom - mob_top)
            new_mob.shift(UP * shift_needed)
            print(f"WARNING: '{name}' too close. Shifted UP by {shift_needed:.2f}")
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

    def highlight_last(self):
        if self.steps:
            self.scene.play(
                self.steps[-1].animate.set_color(ORANGE_HL),
                run_time=0.5)

    def get_all(self):
        return VGroup(*self.steps)

    def fadeout_all(self, rt=0.8):
        if self.steps:
            self.scene.play(*[FadeOut(s) for s in self.steps],
                            run_time=rt)
            self.steps.clear()


# ─────────────────────────── MAIN SCENE ─────────────────────────

class SimplifyBracketsScene(VoiceoverScene):

    def construct(self):
        self._setup_tts()
        self.show_title()
        self.show_hook()
        self.show_positive_rule()
        self.show_negative_rule()
        self.show_caution()
        self.show_question()
        self.show_solution()
        self.show_summary()

    # ── TTS SETUP ──────────────────────────────────────────────

    def _setup_tts(self):
        self.set_speech_service(
            OpenAIService(
                voice="shimmer",
                model="gpt-4o-mini-tts",
                instructions=TTS_INSTRUCTIONS,
            )
        )

    # ── TITLE ──────────────────────────────────────────────────

    def show_title(self):
        active_mobs = []
        self.camera.background_color = PURPLE

        with self.voiceover(
            text='<bookmark mark="bk_title"/>Simplification of Algebraic Expressions.'
        ) as tracker:
            self.wait_until_bookmark("bk_title")
            topic = Text(
                "Simplification of\nAlgebraic Expressions",
                font="Poppins", font_size=48,
                color=WHITE
            )
            topic.move_to(ORIGIN)
            self.play(FadeIn(topic), run_time=0.8)
            active_mobs.append(topic)

        self.wait(0.4)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── HOOK / ANALOGY ─────────────────────────────────────────

    def show_hook(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        with self.voiceover(
            text=(
                '<bookmark mark="bk_bag"/>Suppose someone owes you a bag, '
                'containing three pens and two pencils. '
                'When they take back the whole bag, — you lose both the three pens, '
                'and the two pencils — not just one of them. '
                '<bookmark mark="bk_neg_intro"/>A negative sign before a bracket, '
                'in algebra, works exactly the same way. '
                'It applies to every single term, inside.'
            )
        ) as tracker:

            self.wait_until_bookmark("bk_bag")
            card1 = make_concept_card(
                "Someone takes back the whole bag — you lose EVERYTHING inside.",
                position=UP * 0.8,
                font_size=26,
            )
            check_safe_margins(card1, "card1")
            self.play(FadeIn(card1), run_time=0.7)
            active_mobs.append(card1)

            self.wait_until_bookmark("bk_neg_intro")
            card2 = make_concept_card(
                "A negative sign before a bracket applies to every single term inside.",
                position=DOWN * 0.7,
                font_size=26,
            )
            check_safe_margins(card2, "card2")
            check_y_gap(card2, active_mobs, name="card2")
            self.play(FadeIn(card2), run_time=0.7)
            active_mobs.append(card2)

        self.wait(0.4)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── POSITIVE SIGN RULE ─────────────────────────────────────

    def show_positive_rule(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        with self.voiceover(
            text=(
                '<bookmark mark="bk_pos_rule"/>When a positive sign appears before a bracket, '
                '— each term inside keeps its sign. '
                '<bookmark mark="bk_pos_ex"/>So five plus the quantity three x plus two, '
                '— becomes five plus three x plus two, '
                '<bookmark mark="bk_pos_simp"/>which simplifies to three x plus seven.'
            )
        ) as tracker:

            # Rule card
            self.wait_until_bookmark("bk_pos_rule")
            rule_card = make_concept_card(
                "Positive sign before bracket: every term keeps its sign.",
                position=UP * 2.0,
                font_size=26,
            )
            check_safe_margins(rule_card, "pos_rule_card")
            self.play(FadeIn(rule_card), run_time=0.7)
            active_mobs.append(rule_card)

            # Pattern F — build expression as separate MathTex objects
            self.wait_until_bookmark("bk_pos_ex")

            t_five  = math_obj(r"5", font_size=40)
            t_plus1 = math_obj(r"+", font_size=40)
            t_open  = math_obj(r"(", font_size=40)
            t_3x    = math_obj(r"3x", font_size=40)
            t_plus2 = math_obj(r"+", font_size=40)
            t_two   = math_obj(r"2", font_size=40)
            t_close = math_obj(r")", font_size=40)

            expr_row = VGroup(
                t_five, t_plus1, t_open, t_3x, t_plus2, t_two, t_close
            ).arrange(RIGHT, buff=0.12)
            expr_row.move_to(UP * 0.5)
            check_safe_margins(expr_row, "pos_expr_row")
            self.play(FadeIn(expr_row), run_time=0.8)
            active_mobs.append(expr_row)

            # Highlight inner terms — they keep their sign
            self.play(
                t_3x.animate.set_color(ORANGE_HL),
                t_two.animate.set_color(ORANGE_HL),
                run_time=0.5
            )
            self.wait(0.3)

            # Show expanded form below
            expanded = VGroup(
                math_obj(r"=", font_size=40),
                math_obj(r"5", font_size=40),
                math_obj(r"+", font_size=40),
                math_obj(r"3x", font_size=40, color=ORANGE_HL),
                math_obj(r"+", font_size=40),
                math_obj(r"2", font_size=40, color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.12)
            expanded.next_to(expr_row, DOWN, buff=0.45)
            check_safe_margins(expanded, "pos_expanded")
            self.play(FadeIn(expanded), run_time=0.7)
            active_mobs.append(expanded)

            # Revert colors
            self.play(
                t_3x.animate.set_color(PURPLE),
                t_two.animate.set_color(PURPLE),
                run_time=0.3
            )

            # Simplified result
            self.wait_until_bookmark("bk_pos_simp")
            result = VGroup(
                math_obj(r"=", font_size=40),
                math_obj(r"3x", font_size=40, color=ORANGE_HL),
                math_obj(r"+", font_size=40, color=ORANGE_HL),
                math_obj(r"7", font_size=40, color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.12)
            result.next_to(expanded, DOWN, buff=0.45)
            check_safe_margins(result, "pos_result")
            check_y_gap(result, active_mobs, name="pos_result")
            self.play(FadeIn(result), run_time=0.8)
            active_mobs.append(result)

        self.wait(0.5)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── NEGATIVE SIGN RULE ─────────────────────────────────────

    def show_negative_rule(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        with self.voiceover(
            text=(
                '<bookmark mark="bk_neg_rule"/>When a negative sign appears before a bracket, '
                '— every term inside the bracket flips its sign. '
                '<bookmark mark="bk_distrib"/>This happens because the negative sign distributes '
                'across every term inside, — just like the distributive property. '
                '<bookmark mark="bk_neg_ex"/>So five minus the quantity three x plus two, '
                '— becomes five minus three x minus two. '
                '<bookmark mark="bk_neg_simp"/>Simplifying gives three minus three x.'
            )
        ) as tracker:

            # Rule card
            self.wait_until_bookmark("bk_neg_rule")
            rule_card = make_concept_card(
                "Negative sign before bracket: every term flips its sign.",
                position=UP * 2.1,
                font_size=26,
            )
            check_safe_margins(rule_card, "neg_rule_card")
            self.play(FadeIn(rule_card), run_time=0.7)
            active_mobs.append(rule_card)

            # Pattern F — build 5 - (3x + 2)
            self.wait_until_bookmark("bk_distrib")

            t_five   = math_obj(r"5", font_size=40)
            t_minus  = math_obj(r"-", font_size=40, color=ORANGE_HL)
            t_open   = math_obj(r"(", font_size=40)
            t_3x     = math_obj(r"3x", font_size=40)
            t_plus   = math_obj(r"+", font_size=40)
            t_two    = math_obj(r"2", font_size=40)
            t_close  = math_obj(r")", font_size=40)

            expr_row = VGroup(
                t_five, t_minus, t_open, t_3x, t_plus, t_two, t_close
            ).arrange(RIGHT, buff=0.12)
            expr_row.move_to(UP * 0.7)
            check_safe_margins(expr_row, "neg_expr_row")
            self.play(FadeIn(expr_row), run_time=0.8)
            active_mobs.append(expr_row)

            # Pattern B — arrows from minus to each inner term
            arrow_to_3x = Arrow(
                start=t_minus.get_bottom() + DOWN * 0.05,
                end=t_3x.get_bottom() + DOWN * 0.3,
                color=ORANGE_HL, stroke_width=2.5,
                tip_length=0.18, buff=0.05
            )
            arrow_to_two = Arrow(
                start=t_minus.get_bottom() + DOWN * 0.05,
                end=t_two.get_bottom() + DOWN * 0.3,
                color=ORANGE_HL, stroke_width=2.5,
                tip_length=0.18, buff=0.05
            )
            self.play(
                Create(arrow_to_3x),
                Create(arrow_to_two),
                run_time=0.9
            )
            active_mobs.append(arrow_to_3x)
            active_mobs.append(arrow_to_two)

            # Terms flash to show flip
            self.play(
                t_3x.animate.set_color(ORANGE_HL),
                t_plus.animate.set_color(ORANGE_HL),
                t_two.animate.set_color(ORANGE_HL),
                run_time=0.5
            )
            self.wait(0.25)

            # Show expanded (sign-flipped) form
            self.wait_until_bookmark("bk_neg_ex")

            expanded = VGroup(
                math_obj(r"=", font_size=40),
                math_obj(r"5", font_size=40),
                math_obj(r"-", font_size=40, color=ORANGE_HL),
                math_obj(r"3x", font_size=40, color=ORANGE_HL),
                math_obj(r"-", font_size=40, color=ORANGE_HL),
                math_obj(r"2", font_size=40, color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.12)
            expanded.next_to(expr_row, DOWN, buff=0.55)
            check_safe_margins(expanded, "neg_expanded")
            check_y_gap(expanded, active_mobs, name="neg_expanded")
            self.play(FadeIn(expanded), run_time=0.8)
            active_mobs.append(expanded)

            # Revert original expression colors
            self.play(
                t_3x.animate.set_color(PURPLE),
                t_plus.animate.set_color(PURPLE),
                t_two.animate.set_color(PURPLE),
                run_time=0.3
            )

            # Simplified result
            self.wait_until_bookmark("bk_neg_simp")
            result = VGroup(
                math_obj(r"=", font_size=40),
                math_obj(r"3", font_size=40, color=ORANGE_HL),
                math_obj(r"-", font_size=40, color=ORANGE_HL),
                math_obj(r"3x", font_size=40, color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.12)
            result.next_to(expanded, DOWN, buff=0.45)
            check_safe_margins(result, "neg_result")
            check_y_gap(result, active_mobs, name="neg_result")
            self.play(FadeIn(result), run_time=0.8)
            active_mobs.append(result)

        self.wait(0.5)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── CAUTION ────────────────────────────────────────────────

    def show_caution(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        with self.voiceover(
            text=(
                '<bookmark mark="bk_caution"/>Take your time, and change every sign inside, '
                '— when there is a minus sign before the bracket. '
                '<bookmark mark="bk_errors"/>This is where errors most often appear.'
            )
        ) as tracker:

            self.wait_until_bookmark("bk_caution")

            # Caution card with orange border — using RoundedRectangle directly
            caution_text = Text(
                "Change EVERY sign inside\nwhen you see a minus before a bracket.",
                font="Poppins", font_size=28, color=PURPLE
            )
            caution_bg = RoundedRectangle(
                corner_radius=0.25,
                width=caution_text.width + 1.0,
                height=caution_text.height + 0.6,
                fill_color=WHITE, fill_opacity=0.9,
                stroke_color=ORANGE_HL, stroke_width=3.0
            )
            caution_bg.move_to(UP * 0.4)
            caution_text.move_to(caution_bg.get_center())
            caution_card = VGroup(caution_bg, caution_text)
            check_safe_margins(caution_card, "caution_card")
            self.play(FadeIn(caution_card), run_time=0.8)
            active_mobs.append(caution_card)

            # Errors label
            self.wait_until_bookmark("bk_errors")
            err_label = Text(
                "This is where errors most often appear.",
                font="Poppins", font_size=24, color=ORANGE_HL
            )
            err_label.next_to(caution_card, DOWN, buff=0.45)
            check_safe_margins(err_label, "err_label")
            check_y_gap(err_label, active_mobs, name="err_label")
            self.play(FadeIn(err_label), run_time=0.6)
            active_mobs.append(err_label)

        self.wait(0.5)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── QUESTION ───────────────────────────────────────────────

    def show_question(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Question")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        with self.voiceover(
            text=(
                '<bookmark mark="bk_q"/>Simplify eight plus the quantity four x plus three, '
                '— minus the quantity two x minus five.'
            )
        ) as tracker:

            self.wait_until_bookmark("bk_q")

            q_text = Text(
                "Simplify:", font="Poppins",
                font_size=28, color=PURPLE
            )
            q_text.move_to(UP * 2.3)
            check_safe_margins(q_text, "q_text")
            self.play(FadeIn(q_text), run_time=0.6)
            active_mobs.append(q_text)

            # Full question expression — Pattern F split
            q_eight   = math_obj(r"8", font_size=42)
            q_plus    = math_obj(r"+", font_size=42)
            q_open1   = math_obj(r"(", font_size=42)
            q_4x      = math_obj(r"4x", font_size=42)
            q_plus3   = math_obj(r"+", font_size=42)
            q_three   = math_obj(r"3", font_size=42)
            q_close1  = math_obj(r")", font_size=42)
            q_minus   = math_obj(r"-", font_size=42)
            q_open2   = math_obj(r"(", font_size=42)
            q_2x      = math_obj(r"2x", font_size=42)
            q_minus2  = math_obj(r"-", font_size=42)
            q_five    = math_obj(r"5", font_size=42)
            q_close2  = math_obj(r")", font_size=42)

            q_expr = VGroup(
                q_eight, q_plus, q_open1, q_4x, q_plus3,
                q_three, q_close1, q_minus, q_open2,
                q_2x, q_minus2, q_five, q_close2
            ).arrange(RIGHT, buff=0.10)
            q_expr.move_to(ORIGIN)
            check_safe_margins(q_expr, "q_expr")
            self.play(FadeIn(q_expr), run_time=0.9)
            active_mobs.append(q_expr)

            # Store for solution reference
            self._q_expr = q_expr

        self.wait(0.4)
        # Store badge for swap in solution
        self._question_badge = badge
        self._question_active = active_mobs[:]

    # ── SOLUTION ───────────────────────────────────────────────

    def show_solution(self):
        # Inherit question active mobs
        active_mobs = self._question_active[:]

        # Swap badge
        old_badge = self._question_badge
        new_badge = create_heading_badge("Solution")
        self.play(FadeOut(old_badge), FadeIn(new_badge), run_time=0.5)
        active_mobs.remove(old_badge)
        active_mobs.append(new_badge)

        # Move question expression to left side as reference
        q_expr = self._q_expr
        self.play(q_expr.animate.move_to(UP * 2.7), run_time=0.7)

        with self.voiceover(
            text=(
                '<bookmark mark="bk_s1"/>Open first bracket — eight plus four x plus three. '
                '<bookmark mark="bk_s2"/>Open second bracket with negative sign — '
                'minus two x plus five. '
                '<bookmark mark="bk_s3"/>Full expression — eight plus four x plus three, '
                'minus two x plus five. '
                '<bookmark mark="bk_s4"/>Collect like terms — four x minus two x, equals two x. '
                '<bookmark mark="bk_s5"/>Combine constants — eight plus three plus five, '
                'equals sixteen. '
                '<bookmark mark="bk_s6"/>Simplified expression is, two x plus sixteen.'
            )
        ) as tracker:

            # Phase 1 — Steps 1–3
            mgr = StepManager(
                self,
                start_anchor=UP * 1.5 + LEFT * 0.5,
                font_size=28,
                buff=0.35
            )

            # Step 1: open first bracket
            self.wait_until_bookmark("bk_s1")
            s1 = VGroup(
                math_obj(r"8", font_size=28),
                math_obj(r"+", font_size=28),
                math_obj(r"4x", font_size=28),
                math_obj(r"+", font_size=28),
                math_obj(r"3", font_size=28),
            ).arrange(RIGHT, buff=0.10)
            mgr.add_step(s1)
            active_mobs.append(s1)

            # Step 2: open second bracket (negative)
            self.wait_until_bookmark("bk_s2")
            s2 = VGroup(
                math_obj(r"-", font_size=28, color=ORANGE_HL),
                math_obj(r"2x", font_size=28, color=ORANGE_HL),
                math_obj(r"+", font_size=28, color=ORANGE_HL),
                math_obj(r"5", font_size=28, color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.10)
            mgr.add_step(s2)
            active_mobs.append(s2)

            # Step 3: full combined expression
            self.wait_until_bookmark("bk_s3")
            s3 = VGroup(
                math_obj(r"8", font_size=28),
                math_obj(r"+", font_size=28),
                math_obj(r"4x", font_size=28),
                math_obj(r"+", font_size=28),
                math_obj(r"3", font_size=28),
                math_obj(r"-", font_size=28),
                math_obj(r"2x", font_size=28),
                math_obj(r"+", font_size=28),
                math_obj(r"5", font_size=28),
            ).arrange(RIGHT, buff=0.10)
            mgr.add_step(s3)
            active_mobs.append(s3)

            # Fade out Phase 1, keep reference expr
            self.wait(0.3)
            mgr.fadeout_all(rt=0.7)
            for step in [s1, s2, s3]:
                if step in active_mobs:
                    active_mobs.remove(step)

            # Phase 2 — Steps 4–6
            mgr2 = StepManager(
                self,
                start_anchor=UP * 1.5 + LEFT * 0.5,
                font_size=28,
                buff=0.35
            )

            # Step 4: collect x terms
            self.wait_until_bookmark("bk_s4")
            s4 = VGroup(
                math_obj(r"4x", font_size=28, color=ORANGE_HL),
                math_obj(r"-", font_size=28),
                math_obj(r"2x", font_size=28, color=ORANGE_HL),
                math_obj(r"=", font_size=28),
                math_obj(r"2x", font_size=28, color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.10)
            mgr2.add_step(s4)
            active_mobs.append(s4)

            # Step 5: combine constants
            self.wait_until_bookmark("bk_s5")
            s5 = VGroup(
                math_obj(r"8", font_size=28, color=ORANGE_HL),
                math_obj(r"+", font_size=28),
                math_obj(r"3", font_size=28, color=ORANGE_HL),
                math_obj(r"+", font_size=28),
                math_obj(r"5", font_size=28, color=ORANGE_HL),
                math_obj(r"=", font_size=28),
                math_obj(r"16", font_size=28, color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.10)
            mgr2.add_step(s5)
            active_mobs.append(s5)

            # Step 6: final answer
            self.wait_until_bookmark("bk_s6")
            s6 = VGroup(
                math_obj(r"=", font_size=32),
                math_obj(r"2x", font_size=32, color=ORANGE_HL),
                math_obj(r"+", font_size=32, color=ORANGE_HL),
                math_obj(r"16", font_size=32, color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.12)
            mgr2.add_step(s6)
            active_mobs.append(s6)

            # Box the final answer
            self.wait(0.2)
            ans_box = SurroundingRectangle(
                s6, color=ORANGE_HL,
                corner_radius=0.15,
                stroke_width=2.5,
                buff=0.15
            )
            self.play(Create(ans_box), run_time=0.7)
            active_mobs.append(ans_box)

        self.wait(0.6)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── SUMMARY ────────────────────────────────────────────────

    def show_summary(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Summary")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        summary_points = [
            "A positive sign before a bracket keeps all signs inside unchanged.",
            "A negative sign before a bracket flips every sign inside.",
            "Always open all brackets before collecting like terms.",
        ]
        positions = [UP * 1.5, ORIGIN, DOWN * 1.5]

        with self.voiceover(
            text=(
                '<bookmark mark="bk_sum1"/>A positive sign before a bracket, '
                'keeps all signs inside unchanged. '
                '<bookmark mark="bk_sum2"/>A negative sign before a bracket, '
                'flips every sign inside. '
                '<bookmark mark="bk_sum3"/>Always open all brackets, '
                'before collecting like terms.'
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