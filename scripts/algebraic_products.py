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

# ── HELPERS ───────────────────────────────────────────────────────────────────

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
                lines.append(cur); cur = w
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


def make_legend(entries, position=DR, buff=0.4):
    rows = []
    for var_tex, def_str in entries:
        v = MathTex(var_tex, tex_template=TexFontTemplates.gnu_freesans_tx,
                    font_size=20, color=ORANGE_HL)
        d = Text(def_str, font="Poppins", font_size=20, color=PURPLE)
        rows.append(VGroup(v, d).arrange(RIGHT, buff=0.1))
    content = VGroup(*rows).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
    bg = RoundedRectangle(
        corner_radius=0.15, width=content.width + 0.4,
        height=content.height + 0.3,
        fill_color=WHITE, fill_opacity=0.85,
        stroke_color=PALE_PURPLE, stroke_width=1.0)
    bg.move_to(content)
    g = VGroup(bg, content)
    if position is not None:
        g.to_corner(position, buff=buff)
    return g


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
            print(f"WARNING: '{name}' overlapped. "
                  f"Shifted UP by {shift_needed:.2f}")
        elif (new_bottom >= mob_top and
              (new_bottom - mob_top) < min_gap):
            shift_needed = min_gap - (new_bottom - mob_top)
            new_mob.shift(UP * shift_needed)
            print(f"WARNING: '{name}' too close. "
                  f"Shifted UP by {shift_needed:.2f}")
    return new_mob


def resolve_overlaps(new_mob, active_mobs, name="new"):
    for mob in active_mobs:
        if isinstance(mob, VGroup) and len(mob) == 0:
            continue
        from manim import VGroup as VG
        nl = new_mob.get_left()[0]
        nr = new_mob.get_right()[0]
        nb = new_mob.get_bottom()[1]
        nt = new_mob.get_top()[1]
        ml = mob.get_left()[0]
        mr = mob.get_right()[0]
        mb = mob.get_bottom()[1]
        mt = mob.get_top()[1]
        margin = 0.15
        if (nl - margin < mr and nr + margin > ml and
                nb - margin < mt and nt + margin > mb):
            shift_y = mb - nt - 0.2
            new_mob.shift(DOWN * abs(shift_y))
            if new_mob.get_bottom()[1] < SAFE_B:
                new_mob.shift(UP * abs(shift_y))
                shift_x = mr - nl + 0.3
                new_mob.shift(RIGHT * shift_x)
            print(f"OVERLAP FIX: {name} repositioned")
    clamp_to_safe_area(new_mob)
    return new_mob


class StepManager:
    LIMITS = {(32, 0.4): 3, (28, 0.3): 4, (24, 0.25): 5, (20, 0.2): 6}

    def __init__(self, scene, start_anchor=None,
                 font_size=28, buff=0.3):
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
            self.scene.play(
                *[FadeOut(s) for s in self.steps], run_time=rt)
            self.steps.clear()


# ── MAIN SCENE ────────────────────────────────────────────────────────────────

class AlgebraicProductsScene(VoiceoverScene):

    def construct(self):
        self._setup_tts()
        self.show_title()
        self.show_concept_omit()
        self.show_concept_coeff_var()
        self.show_concept_coeff_first()
        self.show_concept_special_cases()
        self.show_concept_two_letters()
        self.show_question()
        self.show_solution()
        self.show_summary()

    # ── TTS ───────────────────────────────────────────────────────────────────

    def _setup_tts(self):
        self.set_speech_service(
            OpenAIService(
                voice="shimmer",
                model="gpt-4o-mini-tts",
                instructions=TTS_INSTRUCTIONS,
            )
        )

    # ── TITLE ─────────────────────────────────────────────────────────────────

    def show_title(self):
        active_mobs = []
        self.camera.background_color = PURPLE

        with self.voiceover(
            text='<bookmark mark="bk_title"/>Expressions Using Letter Numbers.'
        ) as tracker:
            self.wait_until_bookmark("bk_title")
            topic = Text(
                "Expressions Using Letter Numbers",
                font="Poppins", font_size=48,
                color=WHITE
            )
            topic.move_to(ORIGIN)
            check_safe_margins(topic, "topic_title")
            self.play(FadeIn(topic), run_time=0.8)
            active_mobs.append(topic)

        self.wait(0.4)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── CONCEPT 1: OMITTING THE MULTIPLICATION SYMBOL ────────────────────────

    def show_concept_omit(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        # ── Build arithmetic row: 3 × 5 (Pattern A — show arithmetic form)
        a_3   = math_obj(r"3",      font_size=44)
        a_x   = math_obj(r"\times", font_size=44)
        a_5   = math_obj(r"5",      font_size=44)
        arith_row = VGroup(a_3, a_x, a_5).arrange(RIGHT, buff=0.18)
        arith_row.move_to(UP * 1.2)
        check_safe_margins(arith_row, "arith_row")

        # ── Build algebra row: 3 × n (will lose the ×)
        b_3   = math_obj(r"3",      font_size=44)
        b_x   = math_obj(r"\times", font_size=44)
        b_n   = math_obj(r"n",      font_size=44)
        alg_row = VGroup(b_3, b_x, b_n).arrange(RIGHT, buff=0.18)
        alg_row.move_to(ORIGIN)
        check_safe_margins(alg_row, "alg_row")

        with self.voiceover(
            text=(
                '<bookmark mark="bk_arithmetic"/>In arithmetic, we write'
                ' three times five, with the multiplication symbol clearly'
                ' between them. '
                'But in algebra, once a letter-number is involved,'
                ' we use a much cleaner convention. '
                '<bookmark mark="bk_leave_out"/>We simply leave out the'
                ' multiplication symbol altogether. '
                '<bookmark mark="bk_three_n"/>Three times n, is written'
                ' as three n. '
                '<bookmark mark="bk_standard"/>This is the standard way'
                ' algebraic products are written.'
            )
        ) as tracker:

            # Show arithmetic form
            self.wait_until_bookmark("bk_arithmetic")
            self.play(FadeIn(arith_row), run_time=0.7)
            active_mobs.append(arith_row)

            # Show algebra form with × still present
            self.play(FadeIn(alg_row), run_time=0.7)
            active_mobs.append(alg_row)

            # Leave out the × symbol — ReplacementTransform × out
            self.wait_until_bookmark("bk_leave_out")

            # b_3 and b_n close together after × leaves
            b_3_target = math_obj(r"3", font_size=44)
            b_n_target = math_obj(r"n", font_size=44)
            # Position the result "3n" centered where alg_row was
            result_3n = VGroup(b_3_target, b_n_target).arrange(
                RIGHT, buff=0.06
            )
            result_3n.move_to(alg_row.get_center())
            check_safe_margins(result_3n, "result_3n")

            self.play(
                FadeOut(b_x),
                ReplacementTransform(b_3, b_3_target),
                ReplacementTransform(b_n, b_n_target),
                run_time=0.9
            )
            # Remove alg_row from active_mobs (children now gone/replaced)
            active_mobs.remove(alg_row)
            active_mobs.append(result_3n)

            # Highlight result
            self.wait_until_bookmark("bk_three_n")
            self.play(
                result_3n.animate.set_color(ORANGE_HL),
                run_time=0.5
            )
            self.wait(0.4)
            self.play(
                result_3n.animate.set_color(PURPLE),
                run_time=0.3
            )

            # Echo card
            self.wait_until_bookmark("bk_standard")
            echo = make_concept_card(
                "Standard algebraic product form",
                position=DOWN * 2.0,
                font_size=24
            )
            check_safe_margins(echo, "echo_card")
            self.play(FadeIn(echo), run_time=0.7)
            active_mobs.append(echo)

        self.wait(0.4)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── CONCEPT 2: COEFFICIENT AND VARIABLE ───────────────────────────────────

    def show_concept_coeff_var(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        # Build "7x" as two separate addressable objects (Pattern D + F)
        t_7  = math_obj(r"7",  font_size=52)
        t_x  = math_obj(r"x",  font_size=52)
        term = VGroup(t_7, t_x).arrange(RIGHT, buff=0.06)
        term.move_to(UP * 0.8)
        check_safe_margins(term, "term_7x")

        with self.voiceover(
            text=(
                '<bookmark mark="bk_next_to"/>When we write a number directly'
                ' next to a letter-number, with no symbol between them,'
                ' it means they are multiplied. '
                '<bookmark mark="bk_coefficient"/>The number in front is'
                ' called the coefficient. '
                '<bookmark mark="bk_variable"/>The letter-number is called'
                ' the variable. '
                '<bookmark mark="bk_seven_x"/>So in the term seven x, —'
                ' seven is the coefficient, and x is the variable. '
                '<bookmark mark="bk_means_seven"/>It means seven times x.'
            )
        ) as tracker:

            # Show the term
            self.wait_until_bookmark("bk_next_to")
            self.play(FadeIn(term), run_time=0.7)
            active_mobs.append(term)

            # Pattern D: arrow from 7 → "coefficient"
            self.wait_until_bookmark("bk_coefficient")
            self.play(t_7.animate.set_color(ORANGE_HL), run_time=0.4)

            coeff_arrow = Arrow(
                t_7.get_top() + UP * 0.05,
                t_7.get_top() + UP * 0.9 + LEFT * 0.8,
                color=ORANGE_HL, stroke_width=2.5,
                tip_length=0.18, buff=0
            )
            coeff_label = Text(
                "coefficient", font="Poppins",
                font_size=22, color=ORANGE_HL
            )
            coeff_label.next_to(coeff_arrow.get_end(), UP, buff=0.1)
            check_safe_margins(coeff_arrow, "coeff_arrow")
            check_safe_margins(coeff_label, "coeff_label")
            self.play(FadeIn(coeff_arrow), FadeIn(coeff_label), run_time=0.6)
            active_mobs.append(coeff_arrow)
            active_mobs.append(coeff_label)

            # Pattern D: arrow from x → "variable"
            self.wait_until_bookmark("bk_variable")
            self.play(t_x.animate.set_color(ORANGE_HL), run_time=0.4)

            var_arrow = Arrow(
                t_x.get_top() + UP * 0.05,
                t_x.get_top() + UP * 0.9 + RIGHT * 0.8,
                color=ORANGE_HL, stroke_width=2.5,
                tip_length=0.18, buff=0
            )
            var_label = Text(
                "variable", font="Poppins",
                font_size=22, color=ORANGE_HL
            )
            var_label.next_to(var_arrow.get_end(), UP, buff=0.1)
            check_safe_margins(var_arrow, "var_arrow")
            check_safe_margins(var_label, "var_label")
            self.play(FadeIn(var_arrow), FadeIn(var_label), run_time=0.6)
            active_mobs.append(var_arrow)
            active_mobs.append(var_label)

            # Highlight both in sequence
            self.wait_until_bookmark("bk_seven_x")
            self.play(
                t_7.animate.set_color(ORANGE_HL),
                run_time=0.4
            )
            self.wait(0.3)
            self.play(
                t_7.animate.set_color(PURPLE),
                t_x.animate.set_color(ORANGE_HL),
                run_time=0.4
            )
            self.wait(0.3)
            self.play(t_x.animate.set_color(PURPLE), run_time=0.3)

            # Pattern B: Arrow → expanded form "= 7 × x"
            self.wait_until_bookmark("bk_means_seven")
            expand_arrow = Arrow(
                term.get_right() + RIGHT * 0.1,
                term.get_right() + RIGHT * 1.2,
                color=PURPLE, stroke_width=2.5,
                tip_length=0.18, buff=0
            )
            expanded = math_obj(r"= 7 \times x", font_size=36)
            expanded.next_to(expand_arrow.get_end(), RIGHT, buff=0.15)
            check_safe_margins(expand_arrow, "expand_arrow")
            check_safe_margins(expanded, "expanded")
            self.play(
                FadeIn(expand_arrow), FadeIn(expanded), run_time=0.7
            )
            active_mobs.append(expand_arrow)
            active_mobs.append(expanded)

        self.wait(0.5)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── CONCEPT 3: COEFFICIENT COMES FIRST ───────────────────────────────────

    def show_concept_coeff_first(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        with self.voiceover(
            text=(
                '<bookmark mark="bk_coeff_first"/>The coefficient always'
                ' comes first. '
                '<bookmark mark="bk_five_y"/>We write five y, — not y five.'
            )
        ) as tracker:

            # Rule card
            self.wait_until_bookmark("bk_coeff_first")
            rule_card = make_concept_card(
                "Coefficient always comes first",
                position=UP * 1.5,
                font_size=26
            )
            check_safe_margins(rule_card, "rule_card")
            self.play(FadeIn(rule_card), run_time=0.7)
            active_mobs.append(rule_card)

            # Pattern C: CORRECT "5y" vs WRONG "y5"
            self.wait_until_bookmark("bk_five_y")

            # CORRECT side
            c_label = Text(
                "Correct", font="Poppins", font_size=22,
                color=WHITE
            )
            c_bg = RoundedRectangle(
                corner_radius=0.15,
                width=c_label.width + 0.5,
                height=c_label.height + 0.25,
                fill_color="#2E8B57", fill_opacity=0.9,
                stroke_width=0
            )
            c_bg.move_to(LEFT * 2.8 + UP * 0.1)
            c_label.move_to(c_bg.get_center())
            c_badge = VGroup(c_bg, c_label)

            c_expr_5 = math_obj(r"5", font_size=48, color="#2E8B57")
            c_expr_y = math_obj(r"y", font_size=48, color="#2E8B57")
            c_expr = VGroup(c_expr_5, c_expr_y).arrange(RIGHT, buff=0.06)
            c_expr.next_to(c_bg, DOWN, buff=0.25)

            correct_group = VGroup(c_badge, c_expr)
            check_safe_margins(correct_group, "correct_group")

            # WRONG side
            w_label = Text(
                "Wrong", font="Poppins", font_size=22,
                color=WHITE
            )
            w_bg = RoundedRectangle(
                corner_radius=0.15,
                width=w_label.width + 0.5,
                height=w_label.height + 0.25,
                fill_color=RED, fill_opacity=0.85,
                stroke_width=0
            )
            w_bg.move_to(RIGHT * 2.2 + UP * 0.1)
            w_label.move_to(w_bg.get_center())
            w_badge_grp = VGroup(w_bg, w_label)

            w_expr_y = math_obj(r"y", font_size=48, color=RED)
            w_expr_5 = math_obj(r"5", font_size=48, color=RED)
            w_expr = VGroup(w_expr_y, w_expr_5).arrange(RIGHT, buff=0.06)
            w_expr.next_to(w_bg, DOWN, buff=0.25)

            # Cross mark over wrong expression
            cross = MathTex(r"\times", font_size=60, color=RED)
            cross.move_to(w_expr.get_center())

            wrong_group = VGroup(w_badge_grp, w_expr, cross)
            check_safe_margins(wrong_group, "wrong_group")

            self.play(FadeIn(correct_group), run_time=0.7)
            active_mobs.append(correct_group)
            self.play(FadeIn(wrong_group), run_time=0.7)
            active_mobs.append(wrong_group)

        self.wait(0.5)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── CONCEPT 4: SPECIAL CASES (1 and −1) ──────────────────────────────────

    def show_concept_special_cases(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        # Case 1: 1 × x → x
        c1_one  = math_obj(r"1",      font_size=48)
        c1_mul  = math_obj(r"\times", font_size=48)
        c1_x    = math_obj(r"x",      font_size=48)
        case1_row = VGroup(c1_one, c1_mul, c1_x).arrange(RIGHT, buff=0.18)
        case1_row.move_to(UP * 0.8)
        check_safe_margins(case1_row, "case1_row")

        # Case 2: −1 × x → −x
        c2_neg  = math_obj(r"-1",     font_size=48)
        c2_mul  = math_obj(r"\times", font_size=48)
        c2_x    = math_obj(r"x",      font_size=48)
        case2_row = VGroup(c2_neg, c2_mul, c2_x).arrange(RIGHT, buff=0.18)
        case2_row.move_to(DOWN * 0.5)
        check_safe_margins(case2_row, "case2_row")

        with self.voiceover(
            text=(
                '<bookmark mark="bk_one_coeff"/>By convention, when the'
                ' coefficient is one, we do not write it — so x, means'
                ' one times x. '
                '<bookmark mark="bk_neg_one"/>And negative one times x,'
                ' is written simply as negative x.'
            )
        ) as tracker:

            # Show case 1
            self.wait_until_bookmark("bk_one_coeff")
            self.play(FadeIn(case1_row), run_time=0.7)
            active_mobs.append(case1_row)

            self.wait(0.3)
            # Highlight 1 and × to show they disappear
            self.play(
                c1_one.animate.set_color(ORANGE_HL),
                c1_mul.animate.set_color(ORANGE_HL),
                run_time=0.4
            )
            self.wait(0.3)

            # ReplacementTransform: 1 × x → x  (in-place)
            result_x = math_obj(r"x", font_size=48, color=ORANGE_HL)
            result_x.move_to(case1_row.get_center())

            self.play(
                FadeOut(c1_one),
                FadeOut(c1_mul),
                ReplacementTransform(c1_x, result_x),
                run_time=0.8
            )
            active_mobs.remove(case1_row)
            active_mobs.append(result_x)
            self.wait(0.3)
            self.play(result_x.animate.set_color(PURPLE), run_time=0.3)

            # Show case 2
            self.wait_until_bookmark("bk_neg_one")
            self.play(FadeIn(case2_row), run_time=0.7)
            active_mobs.append(case2_row)

            self.wait(0.3)
            # Highlight −1 and ×
            self.play(
                c2_neg.animate.set_color(ORANGE_HL),
                c2_mul.animate.set_color(ORANGE_HL),
                run_time=0.4
            )
            self.wait(0.3)

            # ReplacementTransform: −1 × x → −x  (in-place)
            result_neg_x = math_obj(r"-x", font_size=48, color=ORANGE_HL)
            result_neg_x.move_to(case2_row.get_center())

            self.play(
                FadeOut(c2_neg),
                FadeOut(c2_mul),
                ReplacementTransform(c2_x, result_neg_x),
                run_time=0.8
            )
            active_mobs.remove(case2_row)
            active_mobs.append(result_neg_x)
            self.wait(0.3)
            self.play(result_neg_x.animate.set_color(PURPLE), run_time=0.3)

        self.wait(0.5)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── CONCEPT 5: PRODUCTS OF TWO LETTER-NUMBERS ────────────────────────────

    def show_concept_two_letters(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        # Build a × b row
        ab_a   = math_obj(r"a",      font_size=52)
        ab_mul = math_obj(r"\times", font_size=52)
        ab_b   = math_obj(r"b",      font_size=52)
        ab_row = VGroup(ab_a, ab_mul, ab_b).arrange(RIGHT, buff=0.18)
        ab_row.move_to(ORIGIN)
        check_safe_margins(ab_row, "ab_row")

        with self.voiceover(
            text=(
                '<bookmark mark="bk_two_letters"/>This also applies to'
                ' products of two letter-numbers. '
                '<bookmark mark="bk_ab"/>When we write a b, it means'
                ' a times b. '
                '<bookmark mark="bk_no_symbol"/>No multiplication symbol'
                ' is needed.'
            )
        ) as tracker:

            # Extension card
            self.wait_until_bookmark("bk_two_letters")
            ext_card = make_concept_card(
                "Also applies to two letter-numbers",
                position=UP * 1.8,
                font_size=24
            )
            check_safe_margins(ext_card, "ext_card")
            self.play(FadeIn(ext_card), run_time=0.7)
            active_mobs.append(ext_card)

            # Show a × b
            self.wait_until_bookmark("bk_ab")
            self.play(FadeIn(ab_row), run_time=0.7)
            active_mobs.append(ab_row)

            # Remove × → ab
            self.wait_until_bookmark("bk_no_symbol")
            self.play(
                ab_mul.animate.set_color(ORANGE_HL),
                run_time=0.4
            )
            self.wait(0.3)

            ab_a_t = math_obj(r"a", font_size=52)
            ab_b_t = math_obj(r"b", font_size=52)
            result_ab = VGroup(ab_a_t, ab_b_t).arrange(RIGHT, buff=0.04)
            result_ab.move_to(ab_row.get_center())
            result_ab.set_color(ORANGE_HL)
            check_safe_margins(result_ab, "result_ab")

            self.play(
                FadeOut(ab_mul),
                ReplacementTransform(ab_a, ab_a_t),
                ReplacementTransform(ab_b, ab_b_t),
                run_time=0.8
            )
            active_mobs.remove(ab_row)
            active_mobs.append(result_ab)
            self.wait(0.3)
            self.play(result_ab.animate.set_color(PURPLE), run_time=0.3)

        self.wait(0.5)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── QUESTION ──────────────────────────────────────────────────────────────

    def show_question(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Question")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        with self.voiceover(
            text=(
                '<bookmark mark="bk_question"/>Rewrite the following using'
                ' standard algebraic notation — four times m, one times p,'
                ' negative one times q, and a times b.'
            )
        ) as tracker:

            self.wait_until_bookmark("bk_question")

            q_text = Text(
                "Rewrite using standard algebraic notation:",
                font="Poppins", font_size=26, color=PURPLE
            )
            q_text.move_to(UP * 2.8)
            check_safe_margins(q_text, "q_text")
            self.play(FadeIn(q_text), run_time=0.6)
            active_mobs.append(q_text)

            # Four items as a vertical list of MathTex (split for safety)
            item1 = math_obj(r"4 \times m",    font_size=36)
            item2 = math_obj(r"1 \times p",    font_size=36)
            item3 = math_obj(r"-1 \times q",   font_size=36)
            item4 = math_obj(r"a \times b",    font_size=36)

            q_list = VGroup(item1, item2, item3, item4).arrange(
                DOWN, aligned_edge=LEFT, buff=0.35
            )
            q_list.move_to(ORIGIN)
            check_safe_margins(q_list, "q_list")

            self.play(FadeIn(q_list), run_time=0.8)
            active_mobs.append(q_list)

        self._q_list        = q_list
        self._q_text        = q_text
        self._q_badge       = badge
        self._active_from_q = list(active_mobs)

    # ── SOLUTION ──────────────────────────────────────────────────────────────

    def show_solution(self):
        # Stack height: 4 steps, font_size=28, buff=0.3
        # height ≈ 4 × (0.44 + 0.3) = 2.96 units ✓
        # LIMITS[(28,0.3)] = 4 ✓

        active_mobs = list(self._active_from_q)

        # Swap badge
        sol_badge = create_heading_badge("Solution")
        self.play(
            FadeOut(self._q_badge),
            FadeIn(sol_badge),
            run_time=0.5
        )
        active_mobs[0] = sol_badge

        # Shift question list to right zone
        self.play(
            self._q_list.animate.move_to(RIGHT * 3.2 + UP * 0.5),
            self._q_text.animate.move_to(UP * 2.8),
            run_time=1.0
        )

        with self.voiceover(
            text=(
                '<bookmark mark="bk_s1"/>Four times m, is written as four m. '
                '<bookmark mark="bk_s2"/>One times p, is written simply as p. '
                '<bookmark mark="bk_s3"/>Negative one times q, is written'
                ' as negative q. '
                '<bookmark mark="bk_s4"/>a times b, is written as a b.'
            )
        ) as tracker:

            mgr = StepManager(
                self,
                start_anchor=UP * 2.0 + LEFT * 3.5,
                font_size=28, buff=0.3
            )

            # ── Step 1: 4m ────────────────────────────────────────────────
            self.wait_until_bookmark("bk_s1")
            # Highlight item1 on question list
            self.play(
                self._q_list[0].animate.set_color(ORANGE_HL),
                run_time=0.4
            )
            s1 = math_obj(
                r"4 \times m \;\rightarrow\; 4m",
                font_size=28
            )
            mgr.add_step(s1)
            active_mobs.append(s1)
            self.play(
                self._q_list[0].animate.set_color(PURPLE),
                run_time=0.3
            )

            # ── Step 2: p ─────────────────────────────────────────────────
            self.wait_until_bookmark("bk_s2")
            self.play(
                self._q_list[1].animate.set_color(ORANGE_HL),
                run_time=0.4
            )
            s2 = math_obj(
                r"1 \times p \;\rightarrow\; p",
                font_size=28
            )
            mgr.add_step(s2)
            active_mobs.append(s2)
            self.play(
                self._q_list[1].animate.set_color(PURPLE),
                run_time=0.3
            )

            # ── Step 3: −q ───────────────────────────────────────────────
            self.wait_until_bookmark("bk_s3")
            self.play(
                self._q_list[2].animate.set_color(ORANGE_HL),
                run_time=0.4
            )
            s3 = math_obj(
                r"-1 \times q \;\rightarrow\; -q",
                font_size=28
            )
            mgr.add_step(s3)
            active_mobs.append(s3)
            self.play(
                self._q_list[2].animate.set_color(PURPLE),
                run_time=0.3
            )

            # ── Step 4: ab ────────────────────────────────────────────────
            self.wait_until_bookmark("bk_s4")
            self.play(
                self._q_list[3].animate.set_color(ORANGE_HL),
                run_time=0.4
            )
            s4 = math_obj(
                r"a \times b \;\rightarrow\; ab",
                font_size=28, color=ORANGE_HL
            )
            mgr.add_step(s4)
            active_mobs.append(s4)
            self.play(
                self._q_list[3].animate.set_color(PURPLE),
                run_time=0.3
            )

        self.wait(0.8)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── SUMMARY ───────────────────────────────────────────────────────────────

    def show_summary(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Summary")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        summary_points = [
            "In algebra, the multiplication symbol is omitted"
            " between a number and a variable.",
            "The coefficient comes first, followed by the variable.",
            "A coefficient of one is not written; negative one is"
            " shown only as a negative sign.",
        ]
        positions = [UP * 1.5, ORIGIN, DOWN * 1.5]

        with self.voiceover(
            text=(
                '<bookmark mark="bk_sum1"/>In algebra, the multiplication'
                ' symbol is omitted between a number and a variable. '
                '<bookmark mark="bk_sum2"/>The coefficient comes first,'
                ' followed by the variable. '
                '<bookmark mark="bk_sum3"/>A coefficient of one is not'
                ' written, — negative one is shown only as a negative sign.'
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