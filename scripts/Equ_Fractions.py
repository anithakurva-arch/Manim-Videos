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
                      font_size=24, max_chars=52):
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
        corner_radius=0.2,
        width=min(txt.width + 0.8, 10.2),
        height=txt.height + 0.4,
        fill_color=WHITE, fill_opacity=0.85,
        stroke_color=PALE_PURPLE, stroke_width=1.5)
    bg.move_to(position)
    txt.move_to(bg.get_center())
    return VGroup(bg, txt)


def make_bullet_point(text_str, position=ORIGIN,
                      font_size=25, max_chars=50):
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


def check_y_gap(new_mob, existing_mobs, min_gap=0.32, name="new_mob"):
    for mob in existing_mobs:
        if isinstance(mob, VGroup) and len(mob) == 0:
            continue
        nb = new_mob.get_bottom()[1]
        nt = new_mob.get_top()[1]
        mb = mob.get_bottom()[1]
        mt = mob.get_top()[1]
        if nb < mt and nt > mb:
            shift = mt + min_gap - nb
            new_mob.shift(UP * shift)
            print(f"WARNING: '{name}' overlapped. Shifted UP {shift:.2f}")
        elif nb >= mt and (nb - mt) < min_gap:
            shift = min_gap - (nb - mt)
            new_mob.shift(UP * shift)
            print(f"WARNING: '{name}' too close. Shifted UP {shift:.2f}")
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

class EquivalentExpressionsScene(VoiceoverScene):

    def construct(self):
        self._setup_tts()
        self.show_title()
        self.show_hook()
        self.show_equivalence_definition()
        self.show_simplification_proof()
        self.show_substitution_check()
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
            text='<bookmark mark="bk_title"/>Pick Patterns and Reveal Relationships.'
        ) as tracker:
            self.wait_until_bookmark("bk_title")
            topic = Text(
                "Pick Patterns and\nReveal Relationships",
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
                '<bookmark mark="bk_two_students"/>Imagine two students both study the '
                'same matchstick pattern and come up with different formulas. '
                '<bookmark mark="bk_formula_a"/>One writes three plus two times the '
                'quantity y minus one. '
                '<bookmark mark="bk_formula_b"/>The other writes two y plus one. '
                '<bookmark mark="bk_both_right"/>They each feel confident their formula '
                'is correct. And it turns out both are right — because the two expressions '
                'are equivalent. '
                'The same pattern can be described in multiple valid ways, '
                'and confirming equivalence is part of mathematical precision.'
            )
        ) as tracker:

            self.wait_until_bookmark("bk_two_students")

            intro_card = make_concept_card(
                "Two students — same pattern — different formulas.",
                position=UP * 2.0,
                font_size=26,
            )
            check_safe_margins(intro_card, "intro_card")
            self.play(FadeIn(intro_card), run_time=0.6)
            active_mobs.append(intro_card)

            # Student A formula — LEFT
            self.wait_until_bookmark("bk_formula_a")

            lbl_a = Text("Student A:", font="Poppins",
                         font_size=24, color=PURPLE)
            expr_a = VGroup(
                math_obj(r"3", font_size=36),
                math_obj(r"+", font_size=36),
                math_obj(r"2", font_size=36),
                math_obj(r"(y-1)", font_size=36),
            ).arrange(RIGHT, buff=0.10)
            col_a = VGroup(lbl_a, expr_a).arrange(DOWN, buff=0.2)
            col_a.move_to(LEFT * 3.0 + UP * 0.5)
            check_safe_margins(col_a, "col_a")
            check_y_gap(col_a, active_mobs, name="col_a")
            self.play(FadeIn(col_a), run_time=0.7)
            active_mobs.append(col_a)

            # Student B formula — RIGHT
            self.wait_until_bookmark("bk_formula_b")

            lbl_b = Text("Student B:", font="Poppins",
                         font_size=24, color=PURPLE)
            expr_b = VGroup(
                math_obj(r"2y", font_size=36),
                math_obj(r"+", font_size=36),
                math_obj(r"1", font_size=36),
            ).arrange(RIGHT, buff=0.10)
            col_b = VGroup(lbl_b, expr_b).arrange(DOWN, buff=0.2)
            col_b.move_to(RIGHT * 3.0 + UP * 0.5)
            check_safe_margins(col_b, "col_b")
            check_y_gap(col_b, active_mobs, name="col_b")
            self.play(FadeIn(col_b), run_time=0.7)
            active_mobs.append(col_b)

            # Question mark between them
            qmark = Text("=  ?", font="Poppins",
                         font_size=32, color=PALE_PURPLE)
            qmark.move_to(UP * 0.5)
            check_safe_margins(qmark, "qmark")
            self.play(FadeIn(qmark), run_time=0.4)
            active_mobs.append(qmark)

            self.wait_until_bookmark("bk_both_right")

            both_card = make_concept_card(
                "Both are right — the expressions are equivalent.",
                position=DOWN * 1.6,
                font_size=24,
            )
            check_safe_margins(both_card, "both_card")
            check_y_gap(both_card, active_mobs, name="both_card")
            self.play(FadeIn(both_card), run_time=0.6)
            active_mobs.append(both_card)

        self.wait(0.4)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── EQUIVALENCE DEFINITION ───────────────────────────────────

    def show_equivalence_definition(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        with self.voiceover(
            text=(
                '<bookmark mark="bk_def"/>Two algebraic expressions are equivalent '
                'when they always give the same output for every value of the letter-number. '
                '<bookmark mark="bk_how"/>The most reliable way to confirm this is to '
                'simplify both expressions fully and compare their simplified forms. '
                '<bookmark mark="bk_identical"/>If they are identical, — the expressions '
                'are equivalent — and this holds for all values, not just the ones we tested.'
            )
        ) as tracker:

            self.wait_until_bookmark("bk_def")

            def_card = make_concept_card(
                "Equivalent: always the same output for every value of the letter-number.",
                position=UP * 1.8,
                font_size=25,
            )
            check_safe_margins(def_card, "def_card")
            self.play(FadeIn(def_card), run_time=0.7)
            active_mobs.append(def_card)

            self.wait_until_bookmark("bk_how")

            how_card = make_concept_card(
                "Simplify both expressions fully, then compare their forms.",
                position=UP * 0.4,
                font_size=25,
            )
            check_safe_margins(how_card, "how_card")
            check_y_gap(how_card, active_mobs, name="how_card")
            self.play(FadeIn(how_card), run_time=0.7)
            active_mobs.append(how_card)

            self.wait_until_bookmark("bk_identical")

            # Pattern B: identical → equivalent arrow
            id_lbl = Text("Identical simplified forms",
                          font="Poppins", font_size=24, color=PURPLE)
            id_lbl.move_to(LEFT * 2.8 + DOWN * 1.0)
            check_safe_margins(id_lbl, "id_lbl")
            check_y_gap(id_lbl, active_mobs, name="id_lbl")

            eq_lbl = VGroup(
                MathTex(r"\Rightarrow",
                        tex_template=TexFontTemplates.gnu_freesans_tx,
                        font_size=36, color=ORANGE_HL),
                Text("Equivalent for ALL values",
                     font="Poppins", font_size=24,
                     color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.2)
            eq_lbl.move_to(RIGHT * 1.5 + DOWN * 1.0)
            check_safe_margins(eq_lbl, "eq_lbl")

            id_arrow = Arrow(
                start=id_lbl.get_right() + RIGHT * 0.05,
                end=eq_lbl.get_left() + LEFT * 0.05,
                color=ORANGE_HL, stroke_width=2.5,
                tip_length=0.2, buff=0.05
            )
            self.play(
                FadeIn(id_lbl), Create(id_arrow), FadeIn(eq_lbl),
                run_time=0.8
            )
            active_mobs.extend([id_lbl, id_arrow, eq_lbl])

        self.wait(0.4)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── SIMPLIFICATION PROOF ─────────────────────────────────────

    def show_simplification_proof(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        with self.voiceover(
            text=(
                '<bookmark mark="bk_take"/>Take three plus two times the quantity '
                'y minus one. '
                '<bookmark mark="bk_distribute"/>Distribute — three plus two y minus two. '
                '<bookmark mark="bk_simplify"/>Simplify — two y plus one. '
                '<bookmark mark="bk_match"/>This matches the second formula exactly. '
                'They are the same expression.'
            )
        ) as tracker:

            self.wait_until_bookmark("bk_take")

            # Show Formula A on left panel
            fa_hdr = Text("Formula A:", font="Poppins",
                          font_size=24, color=PURPLE)
            fa_hdr.move_to(LEFT * 3.5 + UP * 2.1)
            check_safe_margins(fa_hdr, "fa_hdr")
            self.play(FadeIn(fa_hdr), run_time=0.4)
            active_mobs.append(fa_hdr)

            # Pattern F: 3 + 2(y-1)
            t_3     = math_obj(r"3", font_size=40)
            t_pl    = math_obj(r"+", font_size=40)
            t_2     = math_obj(r"2", font_size=40, color=ORANGE_HL)
            t_open  = math_obj(r"(", font_size=40)
            t_y     = math_obj(r"y", font_size=40, color=ORANGE_HL)
            t_mi    = math_obj(r"-", font_size=40)
            t_1     = math_obj(r"1", font_size=40)
            t_close = math_obj(r")", font_size=40)

            fa_expr = VGroup(
                t_3, t_pl, t_2, t_open, t_y, t_mi, t_1, t_close
            ).arrange(RIGHT, buff=0.10)
            fa_expr.move_to(LEFT * 3.5 + UP * 1.3)
            check_safe_margins(fa_expr, "fa_expr")
            self.play(FadeIn(fa_expr), run_time=0.7)
            active_mobs.append(fa_expr)

            # Formula B on right panel
            fb_hdr = Text("Formula B:", font="Poppins",
                          font_size=24, color=PURPLE)
            fb_hdr.move_to(RIGHT * 3.5 + UP * 2.1)
            check_safe_margins(fb_hdr, "fb_hdr")
            self.play(FadeIn(fb_hdr), run_time=0.4)
            active_mobs.append(fb_hdr)

            fb_expr = VGroup(
                math_obj(r"2y", font_size=40, color=PURPLE),
                math_obj(r"+", font_size=40),
                math_obj(r"1", font_size=40, color=PURPLE),
            ).arrange(RIGHT, buff=0.12)
            fb_expr.move_to(RIGHT * 3.5 + UP * 1.3)
            check_safe_margins(fb_expr, "fb_expr")
            self.play(FadeIn(fb_expr), run_time=0.7)
            active_mobs.append(fb_expr)

            # Vertical divider
            div = Line(UP * 2.3, DOWN * 1.5,
                       color=PALE_PURPLE, stroke_width=1.2)
            self.play(Create(div), run_time=0.3)
            active_mobs.append(div)

            # Distribute step
            self.wait_until_bookmark("bk_distribute")

            # Arrows from t_2 to t_y and t_1
            arr_y = Arrow(
                start=t_2.get_bottom() + DOWN * 0.05,
                end=t_y.get_bottom() + DOWN * 0.32,
                color=ORANGE_HL, stroke_width=2.0,
                tip_length=0.16, buff=0.05
            )
            arr_1 = Arrow(
                start=t_2.get_bottom() + DOWN * 0.05,
                end=t_1.get_bottom() + DOWN * 0.32,
                color=ORANGE_HL, stroke_width=2.0,
                tip_length=0.16, buff=0.05
            )
            self.play(Create(arr_y), Create(arr_1), run_time=0.6)
            active_mobs.extend([arr_y, arr_1])

            dist_row = VGroup(
                math_obj(r"=", font_size=36),
                math_obj(r"3", font_size=36),
                math_obj(r"+", font_size=36),
                math_obj(r"2y", font_size=36, color=ORANGE_HL),
                math_obj(r"-", font_size=36),
                math_obj(r"2", font_size=36, color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.12)
            dist_row.move_to(LEFT * 3.5 + UP * 0.1)
            check_safe_margins(dist_row, "dist_row")
            check_y_gap(dist_row, active_mobs, name="dist_row")
            self.play(FadeIn(dist_row), run_time=0.7)
            active_mobs.append(dist_row)

            # Simplify step
            self.wait_until_bookmark("bk_simplify")

            simp_row = VGroup(
                math_obj(r"=", font_size=40),
                math_obj(r"2y", font_size=40, color=ORANGE_HL),
                math_obj(r"+", font_size=40, color=ORANGE_HL),
                math_obj(r"1", font_size=40, color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.12)
            simp_row.move_to(LEFT * 3.5 + DOWN * 0.85)
            check_safe_margins(simp_row, "simp_row")
            check_y_gap(simp_row, active_mobs, name="simp_row")
            self.play(FadeIn(simp_row), run_time=0.7)
            active_mobs.append(simp_row)

            # Match arrow across divider
            self.wait_until_bookmark("bk_match")

            match_arrow = Arrow(
                start=simp_row.get_right() + RIGHT * 0.1,
                end=fb_expr.get_left() + LEFT * 0.1,
                color=ORANGE_HL, stroke_width=2.5,
                tip_length=0.2, buff=0.05
            )
            match_lbl = MathTex(
                r"\checkmark",
                tex_template=TexFontTemplates.gnu_freesans_tx,
                font_size=44, color=ORANGE_HL
            )
            match_lbl.next_to(match_arrow, UP, buff=0.1)
            check_safe_margins(match_lbl, "match_lbl")
            self.play(Create(match_arrow), FadeIn(match_lbl),
                      run_time=0.7)
            active_mobs.extend([match_arrow, match_lbl])

            same_card = make_concept_card(
                "Same expression — they are equivalent.",
                position=DOWN * 2.1,
                font_size=24,
            )
            check_safe_margins(same_card, "same_card")
            check_y_gap(same_card, active_mobs, name="same_card")
            self.play(FadeIn(same_card), run_time=0.6)
            active_mobs.append(same_card)

        self.wait(0.4)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── SUBSTITUTION CHECK ───────────────────────────────────────

    def show_substitution_check(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        with self.voiceover(
            text=(
                '<bookmark mark="bk_sub"/>Substitution can offer a quick check — '
                'if both expressions give the same result for a specific value — '
                '<bookmark mark="bk_only"/>but only simplification gives certainty '
                'for all values.'
            )
        ) as tracker:

            self.wait_until_bookmark("bk_sub")

            sub_hdr = Text("Quick check with y = 3:",
                           font="Poppins", font_size=26,
                           color=PURPLE)
            sub_hdr.move_to(UP * 1.8)
            check_safe_margins(sub_hdr, "sub_hdr")
            self.play(FadeIn(sub_hdr), run_time=0.5)
            active_mobs.append(sub_hdr)

            # Formula A with y=3
            fa_check = VGroup(
                Text("A:", font="Poppins", font_size=24, color=PURPLE),
                math_obj(r"3 + 2(3-1)", font_size=32),
                math_obj(r"=", font_size=32),
                math_obj(r"3 + 4", font_size=32),
                math_obj(r"=", font_size=32),
                math_obj(r"7", font_size=32, color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.14)
            fa_check.move_to(UP * 0.8)
            check_safe_margins(fa_check, "fa_check")
            check_y_gap(fa_check, active_mobs, name="fa_check")
            self.play(FadeIn(fa_check), run_time=0.7)
            active_mobs.append(fa_check)

            # Formula B with y=3
            fb_check = VGroup(
                Text("B:", font="Poppins", font_size=24, color=PURPLE),
                math_obj(r"2(3) + 1", font_size=32),
                math_obj(r"=", font_size=32),
                math_obj(r"6 + 1", font_size=32),
                math_obj(r"=", font_size=32),
                math_obj(r"7", font_size=32, color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.14)
            fb_check.move_to(DOWN * 0.2)
            check_safe_margins(fb_check, "fb_check")
            check_y_gap(fb_check, active_mobs, name="fb_check")
            self.play(FadeIn(fb_check), run_time=0.7)
            active_mobs.append(fb_check)

            chk = MathTex(r"\checkmark",
                          tex_template=TexFontTemplates.gnu_freesans_tx,
                          font_size=38, color=ORANGE_HL)
            chk.move_to(DOWN * 0.2 + RIGHT * 4.0)
            check_safe_margins(chk, "chk")
            self.play(FadeIn(chk), run_time=0.4)
            active_mobs.append(chk)

            self.wait_until_bookmark("bk_only")

            only_card = make_concept_card(
                "Substitution: quick check only. Simplification: certainty for all values.",
                position=DOWN * 1.7,
                font_size=23,
            )
            check_safe_margins(only_card, "only_card")
            check_y_gap(only_card, active_mobs, name="only_card")
            self.play(FadeIn(only_card), run_time=0.6)
            active_mobs.append(only_card)

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
                '<bookmark mark="bk_q"/>Two students describe a pattern. '
                'One writes three times the quantity two n plus three. '
                '<bookmark mark="bk_q2"/>The other writes six n plus nine. '
                'Show whether these expressions are equivalent.'
            )
        ) as tracker:

            self.wait_until_bookmark("bk_q")

            q_lbl = Text("Are these equivalent?",
                         font="Poppins", font_size=28,
                         color=PURPLE)
            q_lbl.move_to(UP * 2.1)
            check_safe_margins(q_lbl, "q_lbl")
            self.play(FadeIn(q_lbl), run_time=0.5)
            active_mobs.append(q_lbl)

            # Student A: 3(2n+3)
            sa_lbl = Text("Student A:", font="Poppins",
                          font_size=24, color=PURPLE)
            sa_expr = VGroup(
                math_obj(r"3", font_size=40),
                math_obj(r"(", font_size=40),
                math_obj(r"2n", font_size=40, color=ORANGE_HL),
                math_obj(r"+", font_size=40),
                math_obj(r"3", font_size=40, color=ORANGE_HL),
                math_obj(r")", font_size=40),
            ).arrange(RIGHT, buff=0.10)
            col_a = VGroup(sa_lbl, sa_expr).arrange(DOWN, buff=0.2)
            col_a.move_to(LEFT * 3.0 + UP * 0.8)
            check_safe_margins(col_a, "col_a")
            check_y_gap(col_a, active_mobs, name="col_a")
            self.play(FadeIn(col_a), run_time=0.7)
            active_mobs.append(col_a)

            self.wait_until_bookmark("bk_q2")

            # Student B: 6n+9
            sb_lbl = Text("Student B:", font="Poppins",
                          font_size=24, color=PURPLE)
            sb_expr = VGroup(
                math_obj(r"6n", font_size=40, color=PURPLE),
                math_obj(r"+", font_size=40),
                math_obj(r"9", font_size=40, color=PURPLE),
            ).arrange(RIGHT, buff=0.12)
            col_b = VGroup(sb_lbl, sb_expr).arrange(DOWN, buff=0.2)
            col_b.move_to(RIGHT * 3.0 + UP * 0.8)
            check_safe_margins(col_b, "col_b")
            check_y_gap(col_b, active_mobs, name="col_b")
            self.play(FadeIn(col_b), run_time=0.7)
            active_mobs.append(col_b)

            qmark = Text("= ?", font="Poppins",
                         font_size=32, color=PALE_PURPLE)
            qmark.move_to(UP * 0.8)
            check_safe_margins(qmark, "qmark")
            self.play(FadeIn(qmark), run_time=0.4)
            active_mobs.append(qmark)

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
                '<bookmark mark="bk_s1"/>Expand the first — three times two n gives '
                'six n. Three times three gives nine. '
                '<bookmark mark="bk_s2"/>Expanded form — six n plus nine. '
                '<bookmark mark="bk_s3"/>Both expressions simplify to six n plus nine. '
                '<bookmark mark="bk_s4"/>They are equivalent.'
            )
        ) as tracker:

            mgr = StepManager(
                self,
                start_anchor=UP * 1.9 + LEFT * 0.5,
                font_size=28,
                buff=0.42
            )

            # Step 1: show distribution
            self.wait_until_bookmark("bk_s1")
            s1 = VGroup(
                math_obj(r"3(2n+3)", font_size=30),
                math_obj(r"=", font_size=30),
                math_obj(r"3 \cdot 2n", font_size=30, color=ORANGE_HL),
                math_obj(r"+", font_size=30),
                math_obj(r"3 \cdot 3", font_size=30, color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.14)
            mgr.add_step(s1)
            active_mobs.append(s1)

            # Step 2: expanded
            self.wait_until_bookmark("bk_s2")
            s2 = VGroup(
                math_obj(r"=", font_size=32),
                math_obj(r"6n", font_size=32, color=ORANGE_HL),
                math_obj(r"+", font_size=32),
                math_obj(r"9", font_size=32, color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.14)
            mgr.add_step(s2)
            active_mobs.append(s2)

            # Step 3: both equal 6n+9
            self.wait_until_bookmark("bk_s3")
            s3_a = VGroup(
                Text("A:", font="Poppins", font_size=24, color=PURPLE),
                math_obj(r"6n + 9", font_size=30, color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.2)

            s3_b = VGroup(
                Text("B:", font="Poppins", font_size=24, color=PURPLE),
                math_obj(r"6n + 9", font_size=30, color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.2)

            s3 = VGroup(s3_a, s3_b).arrange(RIGHT, buff=1.0)
            mgr.add_step(s3)
            active_mobs.append(s3)

            eq_chk = MathTex(r"\checkmark",
                             tex_template=TexFontTemplates.gnu_freesans_tx,
                             font_size=38, color=ORANGE_HL)
            eq_chk.next_to(s3, RIGHT, buff=0.3)
            check_safe_margins(eq_chk, "eq_chk")
            self.play(FadeIn(eq_chk), run_time=0.4)
            active_mobs.append(eq_chk)

            # Step 4: conclusion
            self.wait_until_bookmark("bk_s4")

            concl_bg = RoundedRectangle(
                corner_radius=0.18, width=7.0, height=0.72,
                fill_color=WHITE, fill_opacity=0.9,
                stroke_color=ORANGE_HL, stroke_width=2.5
            )

            last_step_bot = s3.get_bottom()[1]
            concl_bg.move_to(
                UP * (last_step_bot - 0.65)
            )
            concl_txt = VGroup(
                Text("The expressions are equivalent.",
                     font="Poppins", font_size=24, color=PURPLE),
                MathTex(r"\checkmark",
                        tex_template=TexFontTemplates.gnu_freesans_tx,
                        font_size=32, color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.3)
            concl_txt.move_to(concl_bg.get_center())
            concl_card = VGroup(concl_bg, concl_txt)
            check_safe_margins(concl_card, "concl_card")
            check_y_gap(concl_card, active_mobs, name="concl_card")
            self.play(FadeIn(concl_card), run_time=0.7)
            active_mobs.append(concl_card)

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
            "Two expressions are equivalent if they simplify to the same form.",
            "Distribute and collect like terms to fully simplify each expression.",
            "Equivalence proven through simplification holds for all values of n.",
        ]
        positions = [UP * 1.5, ORIGIN, DOWN * 1.5]

        with self.voiceover(
            text=(
                '<bookmark mark="bk_sum1"/>Two expressions are equivalent if they '
                'simplify to the same form. '
                '<bookmark mark="bk_sum2"/>Distribute and collect like terms to fully '
                'simplify each expression. '
                '<bookmark mark="bk_sum3"/>Equivalence proven through simplification '
                'holds for all values of n.'
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