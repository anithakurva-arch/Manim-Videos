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


# ── MATCHSTICK DRAWING HELPERS ───────────────────────────────────

def make_triangle_row(n, side=0.9, origin=ORIGIN, new_color=ORANGE_HL):
    """
    Build n triangles sharing sides in a row.
    Returns VGroup of all stick Line objects.
    All sticks PURPLE except the last triangle's 2 new sticks in new_color.
    """
    sticks = VGroup()
    tip_y  = origin[1] + side * (3 ** 0.5) / 2

    for i in range(n):
        x_left  = origin[0] + i * side
        x_right = x_left + side
        base_l  = np.array([x_left,  origin[1], 0])
        base_r  = np.array([x_right, origin[1], 0])
        apex    = np.array([(x_left + x_right) / 2, tip_y, 0])

        is_new = (i == n - 1) and (n > 1)
        col    = new_color if is_new else PURPLE

        # left leg and right leg always drawn; base only for first triangle
        if i == 0:
            base = Line(base_l, base_r, color=PURPLE, stroke_width=3.5)
            sticks.add(base)
        left_leg  = Line(base_l, apex,  color=col, stroke_width=3.5)
        right_leg = Line(base_r, apex,  color=col, stroke_width=3.5)
        sticks.add(left_leg, right_leg)

    sticks.move_to(origin)
    return sticks


def make_square_row(n, side=0.85, origin=ORIGIN, new_color=ORANGE_HL):
    """
    Build n squares sharing sides in a row.
    Returns VGroup of all stick Line objects.
    Last square's 3 new sticks in new_color.
    """
    sticks = VGroup()
    for i in range(n):
        x0 = origin[0] + i * side
        x1 = x0 + side
        y0 = origin[1]
        y1 = y0 + side

        bl = np.array([x0, y0, 0])
        br = np.array([x1, y0, 0])
        tr = np.array([x1, y1, 0])
        tl = np.array([x0, y1, 0])

        is_new = (i == n - 1) and (n > 1)
        col    = new_color if is_new else PURPLE

        if i == 0:
            sticks.add(Line(bl, br, color=PURPLE, stroke_width=3.5))
            sticks.add(Line(bl, tl, color=PURPLE, stroke_width=3.5))
            sticks.add(Line(tl, tr, color=PURPLE, stroke_width=3.5))
            sticks.add(Line(br, tr, color=PURPLE, stroke_width=3.5))
        else:
            # shared left side already drawn; add top, right, bottom
            sticks.add(Line(tl, tr, color=col, stroke_width=3.5))
            sticks.add(Line(br, tr, color=col, stroke_width=3.5))
            sticks.add(Line(bl, br, color=col, stroke_width=3.5))

    sticks.move_to(origin)
    return sticks


# ─────────────────────── SCENE ──────────────────────────────────

class MatchstickPatternScene(VoiceoverScene):

    def construct(self):
        self._setup_tts()
        self.show_title()
        self.show_pattern_observation()
        self.show_generalisation()
        self.show_simplification()
        self.show_instant_terms()
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
            text='<bookmark mark="bk_title"/>Generalising Patterns with Letter-Numbers.'
        ) as tracker:
            self.wait_until_bookmark("bk_title")
            topic = Text(
                "Generalising Patterns\nwith Letter-Numbers",
                font="Poppins", font_size=46,
                color=WHITE
            )
            topic.move_to(ORIGIN)
            self.play(FadeIn(topic), run_time=0.8)
            active_mobs.append(topic)

        self.wait(0.4)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── PATTERN OBSERVATION ─────────────────────────────────────

    def show_pattern_observation(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        with self.voiceover(
            text=(
                '<bookmark mark="bk_look"/>Look at this matchstick pattern. '
                '<bookmark mark="bk_one"/>One triangle uses three sticks. '
                '<bookmark mark="bk_two"/>Two triangles placed side by side use five sticks. '
                '<bookmark mark="bk_three"/>Three triangles use seven sticks. '
                '<bookmark mark="bk_notice"/>Notice how the count grows with each step. '
                'But how do we describe this for any number of triangles, '
                'without drawing or counting each time?'
            )
        ) as tracker:

            self.wait_until_bookmark("bk_look")

            look_card = make_concept_card(
                "Matchstick pattern: triangles in a row.",
                position=UP * 2.3,
                font_size=26,
            )
            check_safe_margins(look_card, "look_card")
            self.play(FadeIn(look_card), run_time=0.6)
            active_mobs.append(look_card)

            # n=1: 3 sticks
            self.wait_until_bookmark("bk_one")
            tri1 = make_triangle_row(1, side=0.9, new_color=ORANGE_HL)
            tri1.move_to(LEFT * 4.5 + DOWN * 0.2)
            check_safe_margins(tri1, "tri1")
            lbl1 = VGroup(
                math_obj(r"n=1:", font_size=24, color=PURPLE),
                math_obj(r"3", font_size=24, color=ORANGE_HL),
                Text("sticks", font="Poppins",
                     font_size=22, color=PURPLE),
            ).arrange(RIGHT, buff=0.12)
            lbl1.next_to(tri1, DOWN, buff=0.3)
            check_safe_margins(lbl1, "lbl1")
            self.play(Create(tri1), run_time=0.9)
            self.play(FadeIn(lbl1), run_time=0.5)
            active_mobs.extend([tri1, lbl1])

            # n=2: 5 sticks
            self.wait_until_bookmark("bk_two")
            tri2 = make_triangle_row(2, side=0.9, new_color=ORANGE_HL)
            tri2.move_to(ORIGIN + DOWN * 0.2)
            check_safe_margins(tri2, "tri2")
            lbl2 = VGroup(
                math_obj(r"n=2:", font_size=24, color=PURPLE),
                math_obj(r"5", font_size=24, color=ORANGE_HL),
                Text("sticks", font="Poppins",
                     font_size=22, color=PURPLE),
            ).arrange(RIGHT, buff=0.12)
            lbl2.next_to(tri2, DOWN, buff=0.3)
            check_safe_margins(lbl2, "lbl2")
            self.play(Create(tri2), run_time=0.9)
            self.play(FadeIn(lbl2), run_time=0.5)
            active_mobs.extend([tri2, lbl2])

            # n=3: 7 sticks
            self.wait_until_bookmark("bk_three")
            tri3 = make_triangle_row(3, side=0.9, new_color=ORANGE_HL)
            tri3.move_to(RIGHT * 4.5 + DOWN * 0.2)
            check_safe_margins(tri3, "tri3")
            lbl3 = VGroup(
                math_obj(r"n=3:", font_size=24, color=PURPLE),
                math_obj(r"7", font_size=24, color=ORANGE_HL),
                Text("sticks", font="Poppins",
                     font_size=22, color=PURPLE),
            ).arrange(RIGHT, buff=0.12)
            lbl3.next_to(tri3, DOWN, buff=0.3)
            check_safe_margins(lbl3, "lbl3")
            self.play(Create(tri3), run_time=0.9)
            self.play(FadeIn(lbl3), run_time=0.5)
            active_mobs.extend([tri3, lbl3])

            self.wait_until_bookmark("bk_notice")
            notice_card = make_concept_card(
                "The count grows by 2 at each step. Can we write a rule?",
                position=DOWN * 2.3,
                font_size=24,
            )
            check_safe_margins(notice_card, "notice_card")
            check_y_gap(notice_card, active_mobs, name="notice_card")
            self.play(FadeIn(notice_card), run_time=0.6)
            active_mobs.append(notice_card)

        self.wait(0.4)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── GENERALISATION ──────────────────────────────────────────

    def show_generalisation(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        with self.voiceover(
            text=(
                '<bookmark mark="bk_let_n"/>We let n stand for the step number '
                '— the number of triangles. '
                '<bookmark mark="bk_first"/>The first triangle needs three sticks. '
                '<bookmark mark="bk_shared"/>Every triangle after that shares one side '
                'with the previous one, — so it only needs two new sticks. '
                '<bookmark mark="bk_reason"/>That shared side is always there — '
                'it is the mathematical reason the rule holds at every step.'
            )
        ) as tracker:

            self.wait_until_bookmark("bk_let_n")

            n_def = VGroup(
                Text("Let", font="Poppins", font_size=30, color=PURPLE),
                math_obj(r"n", font_size=36, color=ORANGE_HL),
                Text("= number of triangles", font="Poppins",
                     font_size=30, color=PURPLE),
            ).arrange(RIGHT, buff=0.2)
            n_def.move_to(UP * 2.1)
            check_safe_margins(n_def, "n_def")
            self.play(FadeIn(n_def), run_time=0.7)
            active_mobs.append(n_def)

            # Show n=1 triangle with stick count
            self.wait_until_bookmark("bk_first")

            tri_base = make_triangle_row(1, side=1.1, new_color=PURPLE)
            tri_base.move_to(LEFT * 3.5 + UP * 0.5)
            check_safe_margins(tri_base, "tri_base")
            self.play(Create(tri_base), run_time=0.8)
            active_mobs.append(tri_base)

            base_lbl = VGroup(
                math_obj(r"3", font_size=30, color=PURPLE),
                Text("sticks", font="Poppins", font_size=24, color=PURPLE),
            ).arrange(RIGHT, buff=0.12)
            base_lbl.next_to(tri_base, DOWN, buff=0.3)
            check_safe_margins(base_lbl, "base_lbl")
            self.play(FadeIn(base_lbl), run_time=0.5)
            active_mobs.append(base_lbl)

            # Show 2nd triangle with 2 new sticks highlighted
            self.wait_until_bookmark("bk_shared")

            tri_two = make_triangle_row(2, side=1.1, new_color=ORANGE_HL)
            tri_two.move_to(RIGHT * 2.0 + UP * 0.5)
            check_safe_margins(tri_two, "tri_two")
            self.play(Create(tri_two), run_time=0.9)
            active_mobs.append(tri_two)

            new_lbl = VGroup(
                math_obj(r"+2", font_size=30, color=ORANGE_HL),
                Text("new sticks", font="Poppins",
                     font_size=24, color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.12)
            new_lbl.next_to(tri_two, DOWN, buff=0.3)
            check_safe_margins(new_lbl, "new_lbl")
            self.play(FadeIn(new_lbl), run_time=0.5)
            active_mobs.append(new_lbl)

            self.wait_until_bookmark("bk_reason")
            reason_card = make_concept_card(
                "Shared side is the reason the rule holds at every step.",
                position=DOWN * 2.1,
                font_size=24,
            )
            check_safe_margins(reason_card, "reason_card")
            check_y_gap(reason_card, active_mobs, name="reason_card")
            self.play(FadeIn(reason_card), run_time=0.6)
            active_mobs.append(reason_card)

        self.wait(0.4)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── SIMPLIFICATION ──────────────────────────────────────────

    def show_simplification(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        with self.voiceover(
            text=(
                '<bookmark mark="bk_raw"/>So the total number of sticks for n triangles '
                'is three plus two times the quantity n minus one. '
                '<bookmark mark="bk_expand"/>Simplifying — three plus two n minus two, '
                '<bookmark mark="bk_result"/>gives us two n plus one.'
            )
        ) as tracker:

            self.wait_until_bookmark("bk_raw")

            # Pattern F: raw formula as split MathTex
            t_3     = math_obj(r"3", font_size=42)
            t_plus  = math_obj(r"+", font_size=42)
            t_2     = math_obj(r"2", font_size=42, color=ORANGE_HL)
            t_open  = math_obj(r"(", font_size=42)
            t_n     = math_obj(r"n", font_size=42, color=ORANGE_HL)
            t_minus = math_obj(r"-", font_size=42)
            t_1     = math_obj(r"1", font_size=42)
            t_close = math_obj(r")", font_size=42)

            raw_row = VGroup(
                t_3, t_plus, t_2, t_open, t_n, t_minus, t_1, t_close
            ).arrange(RIGHT, buff=0.12)
            raw_row.move_to(UP * 1.5)
            check_safe_margins(raw_row, "raw_row")
            self.play(FadeIn(raw_row), run_time=0.8)
            active_mobs.append(raw_row)

            # Highlight the 2(n-1) part
            self.play(
                t_2.animate.set_color(ORANGE_HL),
                t_n.animate.set_color(ORANGE_HL),
                run_time=0.5
            )

            self.wait_until_bookmark("bk_expand")

            expand_row = VGroup(
                math_obj(r"=", font_size=40),
                math_obj(r"3", font_size=40),
                math_obj(r"+", font_size=40),
                math_obj(r"2n", font_size=40, color=ORANGE_HL),
                math_obj(r"-", font_size=40),
                math_obj(r"2", font_size=40),
            ).arrange(RIGHT, buff=0.12)
            expand_row.next_to(raw_row, DOWN, buff=0.45)
            check_safe_margins(expand_row, "expand_row")
            check_y_gap(expand_row, active_mobs, name="expand_row")
            self.play(FadeIn(expand_row), run_time=0.7)
            active_mobs.append(expand_row)

            self.wait_until_bookmark("bk_result")

            result_row = VGroup(
                math_obj(r"=", font_size=46),
                math_obj(r"2n", font_size=46, color=ORANGE_HL),
                math_obj(r"+", font_size=46, color=ORANGE_HL),
                math_obj(r"1", font_size=46, color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.14)
            result_row.next_to(expand_row, DOWN, buff=0.45)
            check_safe_margins(result_row, "result_row")
            check_y_gap(result_row, active_mobs, name="result_row")
            self.play(FadeIn(result_row), run_time=0.8)
            active_mobs.append(result_row)

            rule_box = SurroundingRectangle(
                result_row, color=ORANGE_HL,
                corner_radius=0.15,
                stroke_width=2.5,
                buff=0.18
            )
            self.play(Create(rule_box), run_time=0.6)
            active_mobs.append(rule_box)

        self.wait(0.5)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── INSTANT TERMS ───────────────────────────────────────────

    def show_instant_terms(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        with self.voiceover(
            text=(
                '<bookmark mark="bk_instant"/>Once we have the general rule, '
                'we can find any term instantly. '
                '<bookmark mark="bk_ten"/>For step ten — two times ten plus one, '
                'equals twenty-one sticks. '
                '<bookmark mark="bk_fifty"/>For step fifty — two times fifty plus one, '
                'equals one hundred and one sticks.'
            )
        ) as tracker:

            self.wait_until_bookmark("bk_instant")

            rule_display = VGroup(
                Text("General rule:", font="Poppins",
                     font_size=26, color=PURPLE),
                math_obj(r"2n + 1", font_size=42, color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.3)
            rule_display.move_to(UP * 2.0)
            check_safe_margins(rule_display, "rule_display")
            self.play(FadeIn(rule_display), run_time=0.7)
            active_mobs.append(rule_display)

            # n = 10
            self.wait_until_bookmark("bk_ten")

            n10_lbl = math_obj(r"n = 10:", font_size=32,
                               color=ORANGE_HL)
            n10_calc = VGroup(
                math_obj(r"2(10)", font_size=32),
                math_obj(r"+", font_size=32),
                math_obj(r"1", font_size=32),
                math_obj(r"=", font_size=32),
                math_obj(r"21", font_size=32, color=ORANGE_HL),
                Text("sticks", font="Poppins", font_size=26,
                     color=PURPLE),
            ).arrange(RIGHT, buff=0.14)
            n10_block = VGroup(n10_lbl, n10_calc).arrange(
                RIGHT, buff=0.3)
            n10_block.move_to(UP * 0.6)
            check_safe_margins(n10_block, "n10_block")
            check_y_gap(n10_block, active_mobs, name="n10_block")
            self.play(FadeIn(n10_block), run_time=0.7)
            active_mobs.append(n10_block)

            # n = 50
            self.wait_until_bookmark("bk_fifty")

            n50_lbl = math_obj(r"n = 50:", font_size=32,
                               color=ORANGE_HL)
            n50_calc = VGroup(
                math_obj(r"2(50)", font_size=32),
                math_obj(r"+", font_size=32),
                math_obj(r"1", font_size=32),
                math_obj(r"=", font_size=32),
                math_obj(r"101", font_size=32, color=ORANGE_HL),
                Text("sticks", font="Poppins", font_size=26,
                     color=PURPLE),
            ).arrange(RIGHT, buff=0.14)
            n50_block = VGroup(n50_lbl, n50_calc).arrange(
                RIGHT, buff=0.3)
            n50_block.move_to(DOWN * 0.6)
            check_safe_margins(n50_block, "n50_block")
            check_y_gap(n50_block, active_mobs, name="n50_block")
            self.play(FadeIn(n50_block), run_time=0.7)
            active_mobs.append(n50_block)

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
                '<bookmark mark="bk_q"/>In a similar pattern, — squares are built in a row, '
                'and each new square shares one side with the previous one. '
                'One square needs four sticks. '
                '<bookmark mark="bk_q2"/>Write the general rule for n squares, '
                'and find the number of sticks for step twelve.'
            )
        ) as tracker:

            self.wait_until_bookmark("bk_q")

            # Show square pattern n=1 and n=2
            sq1 = make_square_row(1, side=0.85, new_color=PURPLE)
            sq1.move_to(LEFT * 4.0 + UP * 0.4)
            check_safe_margins(sq1, "sq1")
            sq1_lbl = VGroup(
                math_obj(r"n=1:", font_size=24, color=PURPLE),
                math_obj(r"4", font_size=24, color=ORANGE_HL),
                Text("sticks", font="Poppins",
                     font_size=22, color=PURPLE),
            ).arrange(RIGHT, buff=0.1)
            sq1_lbl.next_to(sq1, DOWN, buff=0.25)
            check_safe_margins(sq1_lbl, "sq1_lbl")
            self.play(Create(sq1), run_time=0.8)
            self.play(FadeIn(sq1_lbl), run_time=0.4)
            active_mobs.extend([sq1, sq1_lbl])

            sq2 = make_square_row(2, side=0.85, new_color=ORANGE_HL)
            sq2.move_to(ORIGIN + UP * 0.4)
            check_safe_margins(sq2, "sq2")
            sq2_lbl = VGroup(
                math_obj(r"n=2:", font_size=24, color=PURPLE),
                math_obj(r"7", font_size=24, color=ORANGE_HL),
                Text("sticks", font="Poppins",
                     font_size=22, color=PURPLE),
            ).arrange(RIGHT, buff=0.1)
            sq2_lbl.next_to(sq2, DOWN, buff=0.25)
            check_safe_margins(sq2_lbl, "sq2_lbl")
            self.play(Create(sq2), run_time=0.8)
            self.play(FadeIn(sq2_lbl), run_time=0.4)
            active_mobs.extend([sq2, sq2_lbl])

            sq3 = make_square_row(3, side=0.85, new_color=ORANGE_HL)
            sq3.move_to(RIGHT * 4.2 + UP * 0.4)
            check_safe_margins(sq3, "sq3")
            sq3_lbl = VGroup(
                math_obj(r"n=3:", font_size=24, color=PURPLE),
                math_obj(r"10", font_size=24, color=ORANGE_HL),
                Text("sticks", font="Poppins",
                     font_size=22, color=PURPLE),
            ).arrange(RIGHT, buff=0.1)
            sq3_lbl.next_to(sq3, DOWN, buff=0.25)
            check_safe_margins(sq3_lbl, "sq3_lbl")
            self.play(Create(sq3), run_time=0.8)
            self.play(FadeIn(sq3_lbl), run_time=0.4)
            active_mobs.extend([sq3, sq3_lbl])

            self.wait_until_bookmark("bk_q2")
            task_card = make_concept_card(
                "Write the general rule for n squares. Find sticks at step 12.",
                position=DOWN * 2.2,
                font_size=24,
            )
            check_safe_margins(task_card, "task_card")
            check_y_gap(task_card, active_mobs, name="task_card")
            self.play(FadeIn(task_card), run_time=0.6)
            active_mobs.append(task_card)

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
                '<bookmark mark="bk_s1"/>Each new square after the first adds three sticks. '
                '<bookmark mark="bk_s2"/>General rule — three n plus one. '
                '<bookmark mark="bk_s3"/>Check — three times one plus one equals four. Correct. '
                '<bookmark mark="bk_s4"/>For step twelve — three times twelve plus one, '
                'equals thirty-seven sticks.'
            )
        ) as tracker:

            mgr = StepManager(
                self,
                start_anchor=UP * 1.6 + LEFT * 0.5,
                font_size=28,
                buff=0.38
            )

            # Step 1: reasoning
            self.wait_until_bookmark("bk_s1")
            s1 = VGroup(
                Text("Each new square after the first:",
                     font="Poppins", font_size=26, color=PURPLE),
                math_obj(r"+3", font_size=30, color=ORANGE_HL),
                Text("sticks", font="Poppins", font_size=26, color=PURPLE),
            ).arrange(RIGHT, buff=0.18)
            mgr.add_step(s1)
            active_mobs.append(s1)

            # Step 2: general rule
            self.wait_until_bookmark("bk_s2")
            s2 = VGroup(
                Text("General rule:", font="Poppins",
                     font_size=26, color=PURPLE),
                math_obj(r"3n + 1", font_size=34, color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.22)
            mgr.add_step(s2)
            active_mobs.append(s2)

            rule_box = SurroundingRectangle(
                s2, color=ORANGE_HL,
                corner_radius=0.15,
                stroke_width=2.0,
                buff=0.12
            )
            self.play(Create(rule_box), run_time=0.5)
            active_mobs.append(rule_box)

            # Step 3: check n=1
            self.wait_until_bookmark("bk_s3")
            s3 = VGroup(
                Text("Check", font="Poppins",
                     font_size=26, color=PURPLE),
                math_obj(r"n=1:", font_size=28),
                math_obj(r"3(1)+1", font_size=28),
                math_obj(r"=", font_size=28),
                math_obj(r"4", font_size=28, color=ORANGE_HL),
                MathTex(r"\checkmark",
                        tex_template=TexFontTemplates.gnu_freesans_tx,
                        font_size=32, color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.16)
            mgr.add_step(s3)
            active_mobs.append(s3)

            # Step 4: n=12
            self.wait_until_bookmark("bk_s4")
            s4 = VGroup(
                math_obj(r"n=12:", font_size=28, color=ORANGE_HL),
                math_obj(r"3(12)+1", font_size=28),
                math_obj(r"=", font_size=28),
                math_obj(r"37", font_size=32, color=ORANGE_HL),
                Text("sticks", font="Poppins", font_size=26,
                     color=PURPLE),
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
            "Observe how the pattern grows at each step before writing the rule.",
            "Express the rule using a letter-number for the position.",
            "The rule holds because the same reasoning applies at every step.",
        ]
        positions = [UP * 1.5, ORIGIN, DOWN * 1.5]

        with self.voiceover(
            text=(
                '<bookmark mark="bk_sum1"/>Observe how the pattern grows at each step, '
                'before writing the rule. '
                '<bookmark mark="bk_sum2"/>Express the rule using a letter-number '
                'for the position. '
                '<bookmark mark="bk_sum3"/>The rule holds because the same reasoning '
                'applies at every step.'
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