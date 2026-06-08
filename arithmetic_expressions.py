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
RED_HL      = "#E05252"
GREEN_HL    = "#52A852"


def _setup_poppins():
    base_dir  = os.path.dirname(os.path.abspath(__file__))
    fonts_dir = os.path.join(base_dir, ".fonts")
    os.makedirs(fonts_dir, exist_ok=True)
    base_url = (
        "https://raw.githubusercontent.com/google/fonts"
        "/main/ofl/poppins/"
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
Slow down on term identification and evaluation steps.
Emphasize 'evaluate first', 'order of operations', and final answers.
Read the script EXACTLY. No filler. No improvisation.
"""


# ── helpers ────────────────────────────────────────────────────────────────

def create_heading_badge(text_str):
    t = Text(text_str, font="Poppins", font_size=28,
             color=WHITE, weight=BOLD)
    bg = RoundedRectangle(
        corner_radius=0.2, width=t.width + 0.6,
        height=t.height + 0.3,
        fill_color=PURPLE, fill_opacity=1, stroke_width=0)
    bg.move_to(t)
    return VGroup(bg, t).to_corner(UL, buff=0.3)


def math_obj(tex_str, color=PURPLE, font_size=36):
    return MathTex(
        tex_str,
        tex_template=TexFontTemplates.gnu_freesans_tx,
        color=color, font_size=font_size
    )


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
    txt = Text(text_str, font="Poppins",
               font_size=font_size, color=PURPLE)
    bg = RoundedRectangle(
        corner_radius=0.2,
        width=min(txt.width + 0.8, 10.5),
        height=txt.height + 0.4,
        fill_color=WHITE, fill_opacity=0.85,
        stroke_color=PALE_PURPLE, stroke_width=1.5)
    bg.move_to(position)
    txt.move_to(bg.get_center())
    return VGroup(bg, txt)


def make_legend(entries, position=DR, buff=0.4):
    rows = []
    for var_tex, def_str in entries:
        v = MathTex(var_tex,
                    tex_template=TexFontTemplates.gnu_freesans_tx,
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


SAFE_L, SAFE_R = -6.11,  6.11
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
        nb = new_mob.get_bottom()[1]
        nt = new_mob.get_top()[1]
        mb = mob.get_bottom()[1]
        mt = mob.get_top()[1]
        if nb < mt and nt > mb:
            shift = mt + min_gap - nb
            new_mob.shift(UP * shift)
            print(f"WARNING: '{name}' overlapped. Shifted {shift:.2f}")
        elif nb >= mt and (nb - mt) < min_gap:
            shift = min_gap - (nb - mt)
            new_mob.shift(UP * shift)
            print(f"WARNING: '{name}' too close. Shifted {shift:.2f}")
    return new_mob


def has_overlap(a, b, margin=0.15):
    return (a.get_left()[0]  - margin < b.get_right()[0] and
            a.get_right()[0] + margin > b.get_left()[0]  and
            a.get_bottom()[1]- margin < b.get_top()[1]   and
            a.get_top()[1]   + margin > b.get_bottom()[1])


def resolve_overlaps(new_mob, active_mobs, name="new"):
    for mob in active_mobs:
        if isinstance(mob, VGroup) and len(mob) == 0:
            continue
        if has_overlap(new_mob, mob):
            sy = mob.get_bottom()[1] - new_mob.get_top()[1] - 0.2
            new_mob.shift(DOWN * abs(sy))
            if new_mob.get_bottom()[1] < SAFE_B:
                new_mob.shift(UP * abs(sy))
                sx = mob.get_right()[0] - new_mob.get_left()[0] + 0.3
                new_mob.shift(RIGHT * sx)
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
        # ✅ FIXED: use explicit None check — never use `or` on numpy arrays
        self.anchor = (
            start_anchor if start_anchor is not None
            else (UP * 2.0 + LEFT * 3.5)
        )

    def add_step(self, mob, run_time=0.7):
        if len(self.steps) >= self.max:
            print(f"WARNING: StepManager limit ({self.max}).")
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


# ── shelf helper ───────────────────────────────────────────────────────────

def make_shelf(width=3.5, height=0.28, color=PURPLE):
    """A horizontal shelf bar."""
    bar = Rectangle(
        width=width, height=height,
        fill_color=color, fill_opacity=0.85,
        stroke_width=0
    )
    # Small brackets on left and right ends
    left_br  = Line(UP * 0.35, DOWN * 0.05,
                    color=color, stroke_width=2.5)
    right_br = Line(UP * 0.35, DOWN * 0.05,
                    color=color, stroke_width=2.5)
    left_br.next_to(bar, LEFT, buff=0, aligned_edge=DOWN)
    right_br.next_to(bar, RIGHT, buff=0, aligned_edge=DOWN)
    return VGroup(bar, left_br, right_br)


# ── Main Scene ─────────────────────────────────────────────────────────────

class ArithmeticExpressionsScene(VoiceoverScene):

    def construct(self):
        self._setup_tts()
        self.show_title()
        self.show_concept_a()
        self.show_concept_b()
        self.show_concept_c()
        self.show_concept_d()
        self.show_question()
        self.show_solution()
        self.show_summary()

    def _setup_tts(self):
        self.set_speech_service(
            OpenAIService(
                voice="shimmer",
                model="gpt-4o-mini-tts",
                instructions=TTS_INSTRUCTIONS,
            )
        )

    # ── TITLE ──────────────────────────────────────────────────────────────

    def show_title(self):
        active_mobs = []
        self.camera.background_color = PURPLE

        with self.voiceover(
            text='<bookmark mark="bk_title"/>Hello students!'
        ) as tracker:
            self.wait_until_bookmark("bk_title")
            topic = Text(
                "Revisiting Arithmetic\nExpressions",
                font="Poppins", font_size=52,
                color=WHITE, weight=BOLD
            )
            topic.move_to(ORIGIN)
            self.play(FadeIn(topic), run_time=0.8)
            active_mobs.append(topic)

        self.wait(0.4)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── CONCEPT A — Shelf Anchor ───────────────────────────────────────────

    def show_concept_a(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        # Shelf geometry
        SHELF_W  = 3.5
        S1_POS   = LEFT * 2.0 + UP * 1.5
        S2_POS   = LEFT * 2.0 + UP * 0.2
        S3_POS   = LEFT * 2.0 + DOWN * 1.1

        badge = create_heading_badge("Concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        with self.voiceover(
            text=(
                '<bookmark mark="bk_shelves"/>Suppose you want to find '
                'the total number of items on three shelves. '
                '<bookmark mark="bk_shelf1"/>The first shelf has eight items. '
                '<bookmark mark="bk_shelf2"/>The second has two boxes '
                'with five items each. '
                '<bookmark mark="bk_shelf3"/>The third shelf has three items. '
                'Before you can find the total, — '
                '<bookmark mark="bk_evaluate_shelf"/>you need to work out '
                'how many items are on the second shelf. '
                'You cannot just count boxes — '
                '<bookmark mark="bk_must_eval"/>you must evaluate the '
                'box contents first. '
                '<bookmark mark="bk_same_way"/>Expressions in arithmetic '
                'work exactly the same way.'
            )
        ) as tracker:

            # ── Draw three shelves ──
            self.wait_until_bookmark("bk_shelves")

            shelf1 = make_shelf(SHELF_W)
            shelf2 = make_shelf(SHELF_W)
            shelf3 = make_shelf(SHELF_W)
            shelf1.move_to(S1_POS)
            shelf2.move_to(S2_POS)
            shelf3.move_to(S3_POS)

            s_lbl1 = Text("Shelf 1", font="Poppins",
                          font_size=20, color=PURPLE)
            s_lbl2 = Text("Shelf 2", font="Poppins",
                          font_size=20, color=PURPLE)
            s_lbl3 = Text("Shelf 3", font="Poppins",
                          font_size=20, color=PURPLE)
            s_lbl1.next_to(shelf1, LEFT, buff=0.2)
            s_lbl2.next_to(shelf2, LEFT, buff=0.2)
            s_lbl3.next_to(shelf3, LEFT, buff=0.2)

            shelves = VGroup(shelf1, shelf2, shelf3)
            shelf_lbls = VGroup(s_lbl1, s_lbl2, s_lbl3)
            check_safe_margins(shelves, "shelves")
            check_safe_margins(shelf_lbls, "shelf_lbls")
            self.play(
                Create(shelf1), Create(shelf2), Create(shelf3),
                run_time=0.9
            )
            self.play(FadeIn(shelf_lbls), run_time=0.5)
            active_mobs += [shelves, shelf_lbls]

            # ── Shelf 1: "8 items" ──
            self.wait_until_bookmark("bk_shelf1")

            item1 = Text("8 items", font="Poppins",
                         font_size=26, color=PURPLE)
            item1.next_to(shelf1, RIGHT, buff=0.35)
            check_safe_margins(item1, "item1")
            self.play(FadeIn(item1), run_time=0.5)
            active_mobs.append(item1)

            # ── Shelf 2: "2 × 5 items" ──
            self.wait_until_bookmark("bk_shelf2")

            item2 = math_obj(r"2 \times 5 \text{ items}",
                             font_size=26, color=PURPLE)
            item2.next_to(shelf2, RIGHT, buff=0.35)
            check_safe_margins(item2, "item2")
            self.play(FadeIn(item2), run_time=0.5)
            active_mobs.append(item2)

            # ── Shelf 3: "3 items" ──
            self.wait_until_bookmark("bk_shelf3")

            item3 = Text("3 items", font="Poppins",
                         font_size=26, color=PURPLE)
            item3.next_to(shelf3, RIGHT, buff=0.35)
            check_safe_margins(item3, "item3")
            self.play(FadeIn(item3), run_time=0.5)
            active_mobs.append(item3)

            # ── Highlight shelf 2 (need to evaluate) ──
            self.wait_until_bookmark("bk_evaluate_shelf")

            self.play(
                item2.animate.set_color(ORANGE_HL),
                shelf2[0].animate.set_fill(ORANGE_HL, opacity=0.3),
                run_time=0.6
            )

            # ── Evaluate: "= 10" appears next to item2 ──
            self.wait_until_bookmark("bk_must_eval")

            eval_result = math_obj(r"= 10", font_size=26,
                                   color=ORANGE_HL)
            eval_result.next_to(item2, RIGHT, buff=0.25)
            check_safe_margins(eval_result, "eval_result")
            self.play(FadeIn(eval_result), run_time=0.6)
            active_mobs.append(eval_result)

            # Revert shelf2 color
            self.play(
                item2.animate.set_color(PURPLE),
                shelf2[0].animate.set_fill(PURPLE, opacity=0.85),
                run_time=0.4
            )

            # Total row
            total_row = math_obj(
                r"8 + 10 + 3 = 21",
                font_size=28, color=PURPLE
            )
            total_row.move_to(DOWN * 2.3)
            check_safe_margins(total_row, "total_row")
            self.play(FadeIn(total_row), run_time=0.6)
            active_mobs.append(total_row)

            # ── Bridge card ──
            self.wait_until_bookmark("bk_same_way")

            # Fade out shelves, show bridge card
            self.play(
                FadeOut(shelves), FadeOut(shelf_lbls),
                FadeOut(item1), FadeOut(item2),
                FadeOut(item3), FadeOut(eval_result),
                FadeOut(total_row),
                run_time=0.6
            )
            for m in [shelves, shelf_lbls, item1, item2,
                      item3, eval_result, total_row]:
                if m in active_mobs:
                    active_mobs.remove(m)

            bridge_card = make_concept_card(
                "Expressions in arithmetic work the same way:\n"
                "evaluate each term before combining.",
                position=UP * 0.5, font_size=24
            )
            check_safe_margins(bridge_card, "bridge_card")
            self.play(FadeIn(bridge_card), run_time=0.8)
            active_mobs.append(bridge_card)

        self.wait(0.4)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── CONCEPT B — Identifying Terms ─────────────────────────────────────

    def show_concept_b(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        with self.voiceover(
            text=(
                'An expression is made up of individual terms '
                '<bookmark mark="bk_terms_def"/>separated by addition '
                'or subtraction. '
                'The first skill is '
                '<bookmark mark="bk_identify"/>identifying each term clearly. '
                'In the expression twenty-three minus ten times two, — '
                '<bookmark mark="bk_terms_show"/>the terms are twenty-three '
                'and ten times two. '
                '<bookmark mark="bk_sep"/>Each is separated by a '
                'subtraction sign.'
            )
        ) as tracker:

            # ── Definition card + expression ──
            self.wait_until_bookmark("bk_terms_def")

            def_card = make_concept_card(
                "Terms are separated by + or \u2212",
                position=UP * 2.0, font_size=24
            )
            check_safe_margins(def_card, "def_card")
            self.play(FadeIn(def_card), run_time=0.7)
            active_mobs.append(def_card)

            # Expression: "23 - 10 × 2"
            # Build as separate MathTex parts for selective highlighting
            expr_full = math_obj(
                r"23 - 10 \times 2",
                font_size=44, color=PURPLE
            )
            expr_full.set_stroke(width=2.0)
            expr_full.move_to(UP * 0.8)
            check_safe_margins(expr_full, "expr_full")
            self.play(FadeIn(expr_full), run_time=0.7)
            active_mobs.append(expr_full)

            # ── Underline term 1 "23" ──
            self.wait_until_bookmark("bk_identify")

            # Approximate bounding box for "23" — leftmost part
            ul1 = Underline(expr_full, color=ORANGE_HL, buff=0.08)
            # We use a manual line for just the "23" portion
            t1_left  = expr_full.get_left()[0]
            t1_right = expr_full.get_left()[0] + expr_full.width * 0.28
            t1_y     = expr_full.get_bottom()[1] - 0.1
            underline1 = Line(
                [t1_left,  t1_y, 0],
                [t1_right, t1_y, 0],
                color=ORANGE_HL, stroke_width=3
            )
            lbl_t1 = Text("term 1", font="Poppins",
                          font_size=18, color=ORANGE_HL)
            lbl_t1.next_to(underline1, DOWN, buff=0.12)
            check_safe_margins(underline1, "underline1")
            check_safe_margins(lbl_t1, "lbl_t1")
            self.play(Create(underline1), FadeIn(lbl_t1), run_time=0.6)
            active_mobs += [underline1, lbl_t1]

            # ── Underline term 2 "10 × 2" ──
            self.wait_until_bookmark("bk_terms_show")

            t2_left  = expr_full.get_left()[0] + expr_full.width * 0.42
            t2_right = expr_full.get_right()[0]
            underline2 = Line(
                [t2_left,  t1_y, 0],
                [t2_right, t1_y, 0],
                color=ORANGE_HL, stroke_width=3
            )
            lbl_t2 = Text("term 2", font="Poppins",
                          font_size=18, color=ORANGE_HL)
            lbl_t2.next_to(underline2, DOWN, buff=0.12)
            check_safe_margins(underline2, "underline2")
            check_safe_margins(lbl_t2, "lbl_t2")
            self.play(Create(underline2), FadeIn(lbl_t2), run_time=0.6)
            active_mobs += [underline2, lbl_t2]

            # ── Minus sign pulse ──
            self.wait_until_bookmark("bk_sep")

            sep_note = Text("subtraction separates", font="Poppins",
                            font_size=20, color=PURPLE)
            sep_note.move_to(DOWN * 1.6)
            check_safe_margins(sep_note, "sep_note")
            self.play(FadeIn(sep_note), run_time=0.5)
            active_mobs.append(sep_note)

        self.wait(0.4)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── CONCEPT C — Evaluating Non-Numerical Terms ────────────────────────

    def show_concept_c(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        with self.voiceover(
            text=(
                'The second skill is evaluating non-numerical terms — '
                '<bookmark mark="bk_nonnumerical"/>those that involve '
                'a product — before combining. '
                '<bookmark mark="bk_ten_two"/>Ten times two is a term, '
                'and its value is twenty. '
                'Once evaluated, '
                '<bookmark mark="bk_becomes"/>the expression becomes '
                'twenty-three minus twenty, which equals three.'
            )
        ) as tracker:

            # ── Show "23 − 10 × 2" again ──
            self.wait_until_bookmark("bk_nonnumerical")

            expr_c = math_obj(
                r"23 - 10 \times 2",
                font_size=44, color=PURPLE
            )
            expr_c.set_stroke(width=2.0)
            expr_c.move_to(UP * 1.2)
            check_safe_margins(expr_c, "expr_c")
            self.play(FadeIn(expr_c), run_time=0.7)
            active_mobs.append(expr_c)

            # Highlight "10 × 2" portion ORANGE_HL via overlay
            prod_hi = math_obj(r"10 \times 2",
                               font_size=44, color=ORANGE_HL)
            prod_hi.set_stroke(width=2.0)
            # Position over the right portion of expr_c
            prod_hi.move_to(
                expr_c.get_right() + LEFT * prod_hi.width / 2
            )
            prod_hi.shift(LEFT * 0.1)
            check_safe_margins(prod_hi, "prod_hi")
            self.play(FadeIn(prod_hi), run_time=0.5)
            active_mobs.append(prod_hi)

            nonnumerical_lbl = Text(
                "non-numerical term (product)",
                font="Poppins", font_size=20, color=ORANGE_HL
            )
            nonnumerical_lbl.next_to(prod_hi, DOWN, buff=0.3)
            check_safe_margins(nonnumerical_lbl, "nonnumerical_lbl")
            self.play(FadeIn(nonnumerical_lbl), run_time=0.5)
            active_mobs.append(nonnumerical_lbl)

            # ── Evaluate 10×2 = 20 ──
            self.wait_until_bookmark("bk_ten_two")

            self.play(
                FadeOut(prod_hi),
                FadeOut(nonnumerical_lbl),
                run_time=0.4
            )
            active_mobs.remove(prod_hi)
            active_mobs.remove(nonnumerical_lbl)

            # StepManager for this mini-evaluation
            mgr_c = StepManager(
                self,
                start_anchor=UP * 0.2 + LEFT * 1.0,
                font_size=30, buff=0.35
            )

            eval_step = math_obj(
                r"10 \times 2 = 20",
                font_size=30, color=ORANGE_HL
            )
            mgr_c.add_step(eval_step)
            active_mobs.append(eval_step)

            # ── Expression becomes 23 − 20 = 3 ──
            self.wait_until_bookmark("bk_becomes")

            expr_c2 = math_obj(
                r"23 - 20",
                font_size=40, color=PURPLE
            )
            expr_c2.set_stroke(width=2.0)
            expr_c2.next_to(eval_step, DOWN, buff=0.4)
            check_safe_margins(expr_c2, "expr_c2")
            self.play(
                *[s.animate.set_opacity(0.4) for s in mgr_c.steps],
                FadeIn(expr_c2), run_time=0.7
            )
            active_mobs.append(expr_c2)

            result_c = math_obj(r"= 3", font_size=40, color=ORANGE_HL)
            result_c.next_to(expr_c2, RIGHT, buff=0.35)
            check_safe_margins(result_c, "result_c")
            self.play(FadeIn(result_c), run_time=0.6)
            active_mobs.append(result_c)

        self.wait(0.4)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── CONCEPT D — Rule (Pattern C contrast + order card) ────────────────

    def show_concept_d(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        with self.voiceover(
            text=(
                'We must never combine terms '
                '<bookmark mark="bk_never"/>before fully evaluating each one. '
                'If a term contains a multiplication, — '
                '<bookmark mark="bk_mult_first"/>evaluate that first. '
                '<bookmark mark="bk_order_ops"/>This is directly connected '
                'to the order of operations.'
            )
        ) as tracker:

            # ── Pattern C: Wrong vs Correct ──
            self.wait_until_bookmark("bk_never")

            # WRONG column: combine first
            w_title = Text("WRONG", font="Poppins",
                           font_size=22, color=RED_HL, weight=BOLD)
            w_expr  = math_obj(r"23 - 10 \times 2",
                               font_size=26, color=PURPLE)
            w_expr.set_stroke(width=2.0)
            w_wrong = math_obj(r"= 13 \times 2 = 26",
                               font_size=24, color=RED_HL)
            w_wrong.set_stroke(width=2.0)
            w_cross = Text("X", font="Poppins",
                           font_size=34, color=RED_HL, weight=BOLD)
            wrong_col = VGroup(
                w_title, w_expr, w_wrong, w_cross
            ).arrange(DOWN, buff=0.28)
            wrong_col.move_to(LEFT * 2.8 + UP * 0.3)
            check_safe_margins(wrong_col, "wrong_col")

            # CORRECT column: evaluate first
            c_title  = Text("CORRECT", font="Poppins",
                            font_size=22, color=GREEN_HL, weight=BOLD)
            c_expr   = math_obj(r"23 - 10 \times 2",
                                font_size=26, color=PURPLE)
            c_expr.set_stroke(width=2.0)
            c_right  = math_obj(r"= 23 - 20 = 3",
                                font_size=24, color=GREEN_HL)
            c_right.set_stroke(width=2.0)
            c_check  = math_obj(r"\checkmark", font_size=34,
                                color=GREEN_HL)
            correct_col = VGroup(
                c_title, c_expr, c_right, c_check
            ).arrange(DOWN, buff=0.28)
            correct_col.move_to(RIGHT * 2.5 + UP * 0.3)
            check_safe_margins(correct_col, "correct_col")

            self.play(
                FadeIn(wrong_col), FadeIn(correct_col),
                run_time=0.9
            )
            active_mobs += [wrong_col, correct_col]

            # ── Evaluate first rule annotation ──
            self.wait_until_bookmark("bk_mult_first")

            eval_note = Text(
                "Evaluate multiplication first!",
                font="Poppins", font_size=22,
                color=ORANGE_HL, weight=BOLD
            )
            eval_note.move_to(DOWN * 1.5)
            check_safe_margins(eval_note, "eval_note")
            self.play(FadeIn(eval_note), run_time=0.6)
            active_mobs.append(eval_note)

            # ── Order of operations card ──
            self.wait_until_bookmark("bk_order_ops")

            order_card = make_concept_card(
                "Order of operations:\n"
                "Multiply before adding or subtracting.",
                position=DOWN * 2.3, font_size=22
            )
            check_safe_margins(order_card, "order_card")
            self.play(FadeIn(order_card), run_time=0.7)
            active_mobs.append(order_card)

        self.wait(0.4)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── QUESTION ──────────────────────────────────────────────────────────

    def show_question(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Question")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        with self.voiceover(
            text=(
                '<bookmark mark="bk_q"/>Evaluate the expression '
                'five plus four times three minus two times six.'
            )
        ) as tracker:

            self.wait_until_bookmark("bk_q")

            q_text = Text(
                "Evaluate:",
                font="Poppins", font_size=26, color=PURPLE
            )
            q_text.move_to(UP * 2.5)
            check_safe_margins(q_text, "q_text")
            self.play(FadeIn(q_text), run_time=0.5)
            active_mobs.append(q_text)

            q_expr = math_obj(
                r"5 + 4 \times 3 - 2 \times 6",
                font_size=42, color=PURPLE
            )
            q_expr.set_stroke(width=2.0)
            q_expr.move_to(ORIGIN)
            check_safe_margins(q_expr, "q_expr")
            self.play(FadeIn(q_expr), run_time=0.8)
            active_mobs.append(q_expr)

        self._q_expr = q_expr
        self._q_text = q_text
        self._active_from_q = active_mobs[:]

    # ── SOLUTION ──────────────────────────────────────────────────────────

    def show_solution(self):
        active_mobs = list(self._active_from_q)
        q_expr      = self._q_expr

        # Fade out "Evaluate:" label
        self.play(FadeOut(self._q_text), run_time=0.5)
        if self._q_text in active_mobs:
            active_mobs.remove(self._q_text)

        # Shift expression RIGHT
        self.play(
            q_expr.animate.move_to(RIGHT * 3.0 + UP * 0.3),
            run_time=1.0
        )

        # Swap badge
        old_badge = active_mobs[0]
        new_badge = create_heading_badge("Solution")
        self.play(FadeOut(old_badge), FadeIn(new_badge), run_time=0.5)
        active_mobs[0] = new_badge

        # Stack height:
        # 4 steps × (28px≈0.5u + 0.3u) = 3.2u from UP*2.0 → y≈−1.2 ✅

        with self.voiceover(
            text=(
                '<bookmark mark="bk_s1"/>Identify the terms, — five, — '
                'four times three, — and two times six. '
                '<bookmark mark="bk_s2"/>Evaluate, — four times three '
                'equals twelve. — Two times six equals twelve. '
                '<bookmark mark="bk_s3"/>Expression becomes five plus '
                'twelve minus twelve. '
                '<bookmark mark="bk_s4"/>Final answer is five.'
            )
        ) as tracker:

            mgr = StepManager(
                self,
                start_anchor=UP * 2.0 + LEFT * 3.5,
                font_size=28, buff=0.3
            )

            # step 1 — identify terms
            self.wait_until_bookmark("bk_s1")
            s1 = math_obj(
                r"\text{Terms: } 5, \;\; 4 \times 3, \;\; 2 \times 6",
                font_size=26, color=PURPLE
            )
            mgr.add_step(s1)
            active_mobs.append(s1)

            # step 2 — evaluate products
            self.wait_until_bookmark("bk_s2")
            s2 = math_obj(
                r"4 \times 3 = 12, \quad 2 \times 6 = 12",
                font_size=26, color=ORANGE_HL
            )
            s2.set_stroke(width=2.0)
            mgr.add_step(s2)
            active_mobs.append(s2)

            # step 3 — substitute evaluated terms
            self.wait_until_bookmark("bk_s3")
            s3 = math_obj(
                r"5 + 12 - 12",
                font_size=28, color=PURPLE
            )
            s3.set_stroke(width=2.0)
            mgr.add_step(s3)
            active_mobs.append(s3)

            # step 4 — final answer
            self.wait_until_bookmark("bk_s4")
            s4 = math_obj(
                r"= 5",
                font_size=34, color=ORANGE_HL
            )
            mgr.add_step(s4)
            active_mobs.append(s4)

        self.wait(0.6)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── SUMMARY ───────────────────────────────────────────────────────────

    def show_summary(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Summary")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        summary_texts = [
            "Identify each term in the expression\nbefore calculating.",
            "Evaluate non-numerical terms —\nthose involving products — first.",
            "Only combine terms after every individual\nterm has been fully evaluated.",
        ]
        positions = [UP * 1.5, ORIGIN, DOWN * 1.5]

        with self.voiceover(
            text=(
                '<bookmark mark="bk_sum1"/>Identify each term in the '
                'expression before calculating. '
                '<bookmark mark="bk_sum2"/>Evaluate non-numerical terms — '
                'those involving products — first. '
                '<bookmark mark="bk_sum3"/>Only combine terms after every '
                'individual term has been fully evaluated.'
            )
        ) as tracker:

            for i, (txt, pos) in enumerate(zip(summary_texts, positions)):
                self.wait_until_bookmark(f"bk_sum{i + 1}")
                card = make_concept_card(txt, position=pos, font_size=22)
                check_safe_margins(card, f"summary_card_{i + 1}")
                self.play(FadeIn(card), run_time=0.7)
                active_mobs.append(card)

        self.wait(0.6)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()