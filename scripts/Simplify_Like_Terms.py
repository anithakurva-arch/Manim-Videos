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

class SimplifyLikeTermsScene(VoiceoverScene):

    def construct(self):
        self._setup_tts()
        self.show_title()
        self.show_hook()
        self.show_simplified_form()
        self.show_like_unlike_terms()
        self.show_combining_rule()
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

    # ── HOOK ────────────────────────────────────────────────────

    def show_hook(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        with self.voiceover(
            text=(
                '<bookmark mark="bk_desk"/>Suppose you have three pencils, two rulers, '
                'and four more pencils on your desk. '
                '<bookmark mark="bk_say"/>You would naturally say you have seven pencils '
                'and two rulers — '
                'you would not keep them as a long, messy list. '
                '<bookmark mark="bk_algebra"/>Algebraic expressions work exactly the same way. '
                'We group what belongs together, — and leave the rest as it is.'
            )
        ) as tracker:

            self.wait_until_bookmark("bk_desk")

            # Pattern A: show messy list → grouped
            messy_lbl = Text("On your desk:", font="Poppins",
                             font_size=24, color=PURPLE)

            # Pencil icons via coloured dots + labels
            p1 = VGroup(
                *[Circle(radius=0.18, color=ORANGE_HL,
                         fill_color=ORANGE_HL, fill_opacity=1)
                  for _ in range(3)]
            ).arrange(RIGHT, buff=0.12)
            p1_lbl = Text("3 pencils", font="Poppins",
                          font_size=22, color=PURPLE)
            g1 = VGroup(p1, p1_lbl).arrange(DOWN, buff=0.1)

            r1 = VGroup(
                *[Rectangle(width=0.28, height=0.18,
                            color=PALE_PURPLE,
                            fill_color=PALE_PURPLE, fill_opacity=1)
                  for _ in range(2)]
            ).arrange(RIGHT, buff=0.12)
            r1_lbl = Text("2 rulers", font="Poppins",
                          font_size=22, color=PURPLE)
            g2 = VGroup(r1, r1_lbl).arrange(DOWN, buff=0.1)

            p2 = VGroup(
                *[Circle(radius=0.18, color=ORANGE_HL,
                         fill_color=ORANGE_HL, fill_opacity=1)
                  for _ in range(4)]
            ).arrange(RIGHT, buff=0.12)
            p2_lbl = Text("4 more pencils", font="Poppins",
                          font_size=22, color=PURPLE)
            g3 = VGroup(p2, p2_lbl).arrange(DOWN, buff=0.1)

            desk_row = VGroup(g1, g2, g3).arrange(
                RIGHT, buff=0.5)
            desk_block = VGroup(messy_lbl, desk_row).arrange(
                DOWN, buff=0.25)
            desk_block.move_to(UP * 1.1)
            check_safe_margins(desk_block, "desk_block")
            self.play(FadeIn(desk_block), run_time=0.9)
            active_mobs.append(desk_block)

            self.wait_until_bookmark("bk_say")

            # Arrow → simplified grouping
            simp_arrow = Arrow(
                start=desk_block.get_bottom() + DOWN * 0.05,
                end=desk_block.get_bottom() + DOWN * 0.8,
                color=ORANGE_HL, stroke_width=2.5,
                tip_length=0.2, buff=0.05
            )
            simp_row = VGroup(
                Text("7 pencils", font="Poppins",
                     font_size=26, color=ORANGE_HL),
                Text("+", font="Poppins",
                     font_size=26, color=PURPLE),
                Text("2 rulers", font="Poppins",
                     font_size=26, color=PURPLE),
            ).arrange(RIGHT, buff=0.2)
            simp_row.next_to(simp_arrow, DOWN, buff=0.15)
            check_safe_margins(simp_row, "simp_row")
            self.play(Create(simp_arrow), FadeIn(simp_row), run_time=0.7)
            active_mobs.extend([simp_arrow, simp_row])

            self.wait_until_bookmark("bk_algebra")
            algebra_card = make_concept_card(
                "Algebraic expressions: group what belongs together.",
                position=DOWN * 2.4,
                font_size=24,
            )
            check_safe_margins(algebra_card, "algebra_card")
            check_y_gap(algebra_card, active_mobs, name="algebra_card")
            self.play(FadeIn(algebra_card), run_time=0.6)
            active_mobs.append(algebra_card)

        self.wait(0.4)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── SIMPLIFIED FORM ─────────────────────────────────────────

    def show_simplified_form(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        with self.voiceover(
            text=(
                '<bookmark mark="bk_simp"/>An algebraic expression is in its simplified form '
                'when all like terms have been combined, '
                'and no further grouping is possible.'
            )
        ) as tracker:

            self.wait_until_bookmark("bk_simp")

            # Show unsimplified vs simplified side by side — Pattern C
            lbl_before = Text("Before:", font="Poppins",
                              font_size=24, color=PALE_PURPLE)
            expr_before = VGroup(
                math_obj(r"3x", font_size=38),
                math_obj(r"+", font_size=38),
                math_obj(r"5x", font_size=38),
                math_obj(r"+", font_size=38),
                math_obj(r"2y", font_size=38),
            ).arrange(RIGHT, buff=0.12)
            col_before = VGroup(lbl_before, expr_before).arrange(
                DOWN, buff=0.2)
            col_before.move_to(LEFT * 3.0 + UP * 0.5)
            check_safe_margins(col_before, "col_before")
            self.play(FadeIn(col_before), run_time=0.7)
            active_mobs.append(col_before)

            mid_arrow = Arrow(
                start=col_before.get_right() + RIGHT * 0.1,
                end=col_before.get_right() + RIGHT * 1.5,
                color=ORANGE_HL, stroke_width=2.5,
                tip_length=0.2, buff=0.05
            )
            self.play(Create(mid_arrow), run_time=0.4)
            active_mobs.append(mid_arrow)

            lbl_after = Text("Simplified:", font="Poppins",
                             font_size=24, color=ORANGE_HL)
            expr_after = VGroup(
                math_obj(r"8x", font_size=38, color=ORANGE_HL),
                math_obj(r"+", font_size=38),
                math_obj(r"2y", font_size=38),
            ).arrange(RIGHT, buff=0.12)
            col_after = VGroup(lbl_after, expr_after).arrange(
                DOWN, buff=0.2)
            col_after.move_to(RIGHT * 3.2 + UP * 0.5)
            check_safe_margins(col_after, "col_after")
            self.play(FadeIn(col_after), run_time=0.7)
            active_mobs.append(col_after)

            def_card = make_concept_card(
                "Simplified form: all like terms combined, no further grouping possible.",
                position=DOWN * 1.8,
                font_size=24,
            )
            check_safe_margins(def_card, "def_card")
            check_y_gap(def_card, active_mobs, name="def_card")
            self.play(FadeIn(def_card), run_time=0.6)
            active_mobs.append(def_card)

        self.wait(0.4)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── LIKE VS UNLIKE TERMS ────────────────────────────────────

    def show_like_unlike_terms(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        with self.voiceover(
            text=(
                '<bookmark mark="bk_like"/>Like terms are terms that involve the same '
                'letter-number. '
                'So three x and five x are like terms — both involve x. '
                '<bookmark mark="bk_unlike"/>But three x and five y are unlike terms — '
                'they involve different letter-numbers, — just as pencils and rulers '
                'cannot be merged into a single count.'
            )
        ) as tracker:

            self.wait_until_bookmark("bk_like")

            # Pattern C: like terms LEFT, unlike terms RIGHT

            # LEFT: like terms — 3x and 5x
            like_hdr = Text("Like Terms", font="Poppins",
                            font_size=26, color=ORANGE_HL)

            t_3x = math_obj(r"3x", font_size=44, color=ORANGE_HL)
            t_and = Text("and", font="Poppins",
                         font_size=28, color=PURPLE)
            t_5x = math_obj(r"5x", font_size=44, color=ORANGE_HL)
            like_expr = VGroup(t_3x, t_and, t_5x).arrange(
                RIGHT, buff=0.2)

            like_note = Text(
                "Both involve x",
                font="Poppins", font_size=22, color=PALE_PURPLE
            )

            # Brace under both terms
            like_brace = Brace(like_expr, DOWN, color=ORANGE_HL)
            like_brace_lbl = Text(
                "same letter", font="Poppins",
                font_size=20, color=ORANGE_HL
            )
            like_brace_lbl.next_to(like_brace, DOWN, buff=0.12)

            like_col = VGroup(
                like_hdr, like_expr, like_brace,
                like_brace_lbl
            ).arrange(DOWN, buff=0.18)
            like_col.move_to(LEFT * 3.2 + UP * 0.4)
            check_safe_margins(like_col, "like_col")
            self.play(FadeIn(like_col), run_time=0.8)
            active_mobs.append(like_col)

            self.wait_until_bookmark("bk_unlike")

            # RIGHT: unlike terms — 3x and 5y
            unlike_hdr = Text("Unlike Terms", font="Poppins",
                              font_size=26, color=PALE_PURPLE)

            t_3x2 = math_obj(r"3x", font_size=44, color=ORANGE_HL)
            t_and2 = Text("and", font="Poppins",
                          font_size=28, color=PURPLE)
            t_5y = math_obj(r"5y", font_size=44, color=PALE_PURPLE)
            unlike_expr = VGroup(t_3x2, t_and2, t_5y).arrange(
                RIGHT, buff=0.2)

            unlike_brace = Brace(unlike_expr, DOWN, color=PALE_PURPLE)
            unlike_brace_lbl = Text(
                "different letters", font="Poppins",
                font_size=20, color=PALE_PURPLE
            )
            unlike_brace_lbl.next_to(unlike_brace, DOWN, buff=0.12)

            unlike_col = VGroup(
                unlike_hdr, unlike_expr, unlike_brace,
                unlike_brace_lbl
            ).arrange(DOWN, buff=0.18)
            unlike_col.move_to(RIGHT * 3.2 + UP * 0.4)
            check_safe_margins(unlike_col, "unlike_col")
            self.play(FadeIn(unlike_col), run_time=0.8)
            active_mobs.append(unlike_col)

            # Divider
            div = Line(UP * 2.2, DOWN * 1.5,
                       color=PALE_PURPLE, stroke_width=1.5)
            self.play(Create(div), run_time=0.3)
            active_mobs.append(div)

        self.wait(0.4)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── COMBINING RULE ──────────────────────────────────────────

    def show_combining_rule(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        with self.voiceover(
            text=(
                '<bookmark mark="bk_coeff"/>To simplify, we add or subtract the '
                'coefficients — the numbers in front — of like terms only. '
                '<bookmark mark="bk_like_ex"/>Three x plus five x becomes eight x. '
                '<bookmark mark="bk_unlike_ex"/>But three x plus five y stays as '
                'three x plus five y. '
                'Unlike terms cannot be combined further.'
            )
        ) as tracker:

            self.wait_until_bookmark("bk_coeff")

            coeff_card = make_concept_card(
                "Combine like terms by adding or subtracting their coefficients.",
                position=UP * 2.0,
                font_size=26,
            )
            check_safe_margins(coeff_card, "coeff_card")
            self.play(FadeIn(coeff_card), run_time=0.6)
            active_mobs.append(coeff_card)

            # Pattern F: 3x + 5x = 8x — highlight coefficients
            self.wait_until_bookmark("bk_like_ex")

            t_3   = math_obj(r"3", font_size=44, color=ORANGE_HL)
            t_x1  = math_obj(r"x", font_size=44)
            t_pl  = math_obj(r"+", font_size=44)
            t_5   = math_obj(r"5", font_size=44, color=ORANGE_HL)
            t_x2  = math_obj(r"x", font_size=44)
            t_eq  = math_obj(r"=", font_size=44)
            t_8   = math_obj(r"8", font_size=44, color=ORANGE_HL)
            t_x3  = math_obj(r"x", font_size=44, color=ORANGE_HL)

            like_row = VGroup(
                t_3, t_x1, t_pl, t_5, t_x2, t_eq, t_8, t_x3
            ).arrange(RIGHT, buff=0.12)
            like_row.move_to(UP * 0.7)
            check_safe_margins(like_row, "like_row")
            self.play(FadeIn(like_row), run_time=0.8)
            active_mobs.append(like_row)

            # Brace under 3 and 5 — coefficients
            coeff_grp = VGroup(t_3, t_5)
            coeff_brace = Brace(coeff_grp, DOWN, color=ORANGE_HL)
            coeff_lbl = Text("coefficients", font="Poppins",
                             font_size=20, color=ORANGE_HL)
            coeff_lbl.next_to(coeff_brace, DOWN, buff=0.1)
            check_safe_margins(coeff_lbl, "coeff_lbl")
            self.play(Create(coeff_brace), FadeIn(coeff_lbl),
                      run_time=0.6)
            active_mobs.extend([coeff_brace, coeff_lbl])

            # Unlike terms: cannot combine — Pattern C
            self.wait_until_bookmark("bk_unlike_ex")

            unlike_row = VGroup(
                math_obj(r"3x", font_size=40, color=ORANGE_HL),
                math_obj(r"+", font_size=40),
                math_obj(r"5y", font_size=40, color=PALE_PURPLE),
                math_obj(r"\rightarrow", font_size=36),
                Text("stays as", font="Poppins",
                     font_size=24, color=PURPLE),
                math_obj(r"3x + 5y", font_size=40),
            ).arrange(RIGHT, buff=0.18)

            # Replace \rightarrow arrow with actual Arrow obj
            t_3xb  = math_obj(r"3x", font_size=40, color=ORANGE_HL)
            t_plb  = math_obj(r"+", font_size=40)
            t_5yb  = math_obj(r"5y", font_size=40, color=PALE_PURPLE)
            stays  = Text("stays as", font="Poppins",
                          font_size=24, color=PURPLE)
            t_res  = math_obj(r"3x + 5y", font_size=40)
            stay_arrow = Arrow(
                start=ORIGIN, end=RIGHT * 0.7,
                color=PURPLE, stroke_width=2.0,
                tip_length=0.18, buff=0.0
            )
            unlike_final = VGroup(
                t_3xb, t_plb, t_5yb,
                stay_arrow, stays, t_res
            ).arrange(RIGHT, buff=0.18)
            unlike_final.move_to(DOWN * 0.8)
            check_safe_margins(unlike_final, "unlike_final")
            check_y_gap(unlike_final, active_mobs, name="unlike_final")
            self.play(FadeIn(unlike_final), run_time=0.8)
            active_mobs.append(unlike_final)

            cannot_lbl = Text(
                "Unlike terms cannot be combined further.",
                font="Poppins", font_size=24, color=PALE_PURPLE
            )
            cannot_lbl.next_to(unlike_final, DOWN, buff=0.35)
            check_safe_margins(cannot_lbl, "cannot_lbl")
            check_y_gap(cannot_lbl, active_mobs, name="cannot_lbl")
            self.play(FadeIn(cannot_lbl), run_time=0.5)
            active_mobs.append(cannot_lbl)

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
                '<bookmark mark="bk_q"/>Simplify the expression '
                'six a plus four b minus two a plus nine b minus three.'
            )
        ) as tracker:

            self.wait_until_bookmark("bk_q")

            q_lbl = Text(
                "Simplify:", font="Poppins",
                font_size=28, color=PURPLE
            )
            q_lbl.move_to(UP * 2.2)
            check_safe_margins(q_lbl, "q_lbl")
            self.play(FadeIn(q_lbl), run_time=0.5)
            active_mobs.append(q_lbl)

            # Pattern F: split every term
            q_6a    = math_obj(r"6a", font_size=40)
            q_pl1   = math_obj(r"+", font_size=40)
            q_4b    = math_obj(r"4b", font_size=40)
            q_mi1   = math_obj(r"-", font_size=40)
            q_2a    = math_obj(r"2a", font_size=40)
            q_pl2   = math_obj(r"+", font_size=40)
            q_9b    = math_obj(r"9b", font_size=40)
            q_mi2   = math_obj(r"-", font_size=40)
            q_3     = math_obj(r"3", font_size=40)

            q_expr = VGroup(
                q_6a, q_pl1, q_4b, q_mi1, q_2a,
                q_pl2, q_9b, q_mi2, q_3
            ).arrange(RIGHT, buff=0.10)
            q_expr.move_to(UP * 0.8)
            check_safe_margins(q_expr, "q_expr")
            self.play(FadeIn(q_expr), run_time=0.9)
            active_mobs.append(q_expr)

            # Colour-code like terms to hint grouping
            self.play(
                q_6a.animate.set_color(ORANGE_HL),
                q_2a.animate.set_color(ORANGE_HL),
                run_time=0.5
            )
            self.play(
                q_4b.animate.set_color(PURPLE),
                q_9b.animate.set_color(PURPLE),
                run_time=0.4
            )

            hint_a = Text("a terms", font="Poppins",
                          font_size=20, color=ORANGE_HL)
            hint_b = Text("b terms", font="Poppins",
                          font_size=20, color=PURPLE)
            hint_c = Text("number term", font="Poppins",
                          font_size=20, color=PALE_PURPLE)

            hint_a.next_to(q_6a, DOWN, buff=0.45)
            hint_b.next_to(q_4b, DOWN, buff=0.45)
            hint_c.next_to(q_3, DOWN, buff=0.45)
            check_safe_margins(hint_a, "hint_a")
            check_safe_margins(hint_b, "hint_b")
            check_safe_margins(hint_c, "hint_c")
            self.play(
                FadeIn(hint_a), FadeIn(hint_b), FadeIn(hint_c),
                run_time=0.6
            )
            active_mobs.extend([hint_a, hint_b, hint_c])

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
                '<bookmark mark="bk_s1"/>Group the a terms — '
                'six a minus two a equals four a. '
                '<bookmark mark="bk_s2"/>Group the b terms — '
                'four b plus nine b equals thirteen b. '
                '<bookmark mark="bk_s3"/>The number term stays — minus three. '
                '<bookmark mark="bk_s4"/>The simplified expression is '
                'four a plus thirteen b minus three. '
                '<bookmark mark="bk_s5"/>Notice that three kinds of terms appeared here. '
                'Two pairs of like terms were combined, — and the number term stayed '
                'separate — because it is unlike both the a terms and the b terms.'
            )
        ) as tracker:

            mgr = StepManager(
                self,
                start_anchor=UP * 1.8 + LEFT * 0.5,
                font_size=28,
                buff=0.38
            )

            # Step 1: a terms
            self.wait_until_bookmark("bk_s1")
            s1 = VGroup(
                math_obj(r"6a", font_size=30, color=ORANGE_HL),
                math_obj(r"-", font_size=30),
                math_obj(r"2a", font_size=30, color=ORANGE_HL),
                math_obj(r"=", font_size=30),
                math_obj(r"4a", font_size=30, color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.14)
            mgr.add_step(s1)
            active_mobs.append(s1)

            # Step 2: b terms
            self.wait_until_bookmark("bk_s2")
            s2 = VGroup(
                math_obj(r"4b", font_size=30, color=PURPLE),
                math_obj(r"+", font_size=30),
                math_obj(r"9b", font_size=30, color=PURPLE),
                math_obj(r"=", font_size=30),
                math_obj(r"13b", font_size=30, color=PURPLE),
            ).arrange(RIGHT, buff=0.14)
            mgr.add_step(s2)
            active_mobs.append(s2)

            # Step 3: constant stays
            self.wait_until_bookmark("bk_s3")
            s3 = VGroup(
                math_obj(r"-3", font_size=30, color=PALE_PURPLE),
                Text("stays as is", font="Poppins",
                     font_size=24, color=PALE_PURPLE),
            ).arrange(RIGHT, buff=0.2)
            mgr.add_step(s3)
            active_mobs.append(s3)

            # Step 4: final simplified expression
            self.wait_until_bookmark("bk_s4")
            s4 = VGroup(
                math_obj(r"=", font_size=34),
                math_obj(r"4a", font_size=34, color=ORANGE_HL),
                math_obj(r"+", font_size=34),
                math_obj(r"13b", font_size=34, color=PURPLE),
                math_obj(r"-", font_size=34),
                math_obj(r"3", font_size=34, color=PALE_PURPLE),
            ).arrange(RIGHT, buff=0.14)
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

            # Notice card
            self.wait_until_bookmark("bk_s5")
            notice_card = make_concept_card(
                "Two pairs of like terms combined. Number term stayed separate.",
                position=DOWN * 2.5,
                font_size=22,
            )
            check_safe_margins(notice_card, "notice_card")
            check_y_gap(notice_card, active_mobs, name="notice_card")
            self.play(FadeIn(notice_card), run_time=0.6)
            active_mobs.append(notice_card)

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
            "Like terms share the same letter-number part and can be combined.",
            "Unlike terms have different letter-number parts and cannot be combined.",
            "Simplified form means all like terms have been collected into single terms.",
        ]
        positions = [UP * 1.5, ORIGIN, DOWN * 1.5]

        with self.voiceover(
            text=(
                '<bookmark mark="bk_sum1"/>Like terms share the same letter-number part, '
                'and can be combined. '
                '<bookmark mark="bk_sum2"/>Unlike terms have different letter-number parts, '
                'and cannot be combined. '
                '<bookmark mark="bk_sum3"/>Simplified form means all like terms have been '
                'collected into single terms.'
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