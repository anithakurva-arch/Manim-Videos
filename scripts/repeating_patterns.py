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
GREEN_OK    = "#2E8B57"
RED_COL     = "#D62828"
AMBER_COL   = "#F4A726"
GREEN_COL   = "#2E8B57"

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
Slow down on variables and key terms. Emphasize: cycle length, remainder, position.
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
            shift_needed = mt + min_gap - nb
            new_mob.shift(UP * shift_needed)
            print(f"WARNING: '{name}' overlapped. Shifted UP {shift_needed:.2f}")
        elif nb >= mt and (nb - mt) < min_gap:
            shift_needed = min_gap - (nb - mt)
            new_mob.shift(UP * shift_needed)
            print(f"WARNING: '{name}' too close. Shifted UP {shift_needed:.2f}")
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


# ── SHAPE HELPERS ──────────────────────────────────────────────────────────────

def make_traffic_circle(color, radius=0.38):
    """Filled circle with white stroke for traffic light element."""
    c = Circle(radius=radius,
               fill_color=color, fill_opacity=1.0,
               stroke_color=WHITE, stroke_width=2.5)
    return c


def make_shape_element(shape_name, size=0.55, color=PURPLE):
    """
    Returns a Manim mobject for 'circle', 'square', or 'triangle'.
    shape_name: 'circle' | 'square' | 'triangle'
    """
    if shape_name == "circle":
        return Circle(radius=size * 0.5,
                      fill_color=color, fill_opacity=0.85,
                      stroke_color=color, stroke_width=2.5)
    elif shape_name == "square":
        return Square(side_length=size,
                      fill_color=color, fill_opacity=0.85,
                      stroke_color=color, stroke_width=2.5)
    elif shape_name == "triangle":
        return Triangle(fill_color=color, fill_opacity=0.85,
                        stroke_color=color,
                        stroke_width=2.5).scale(size * 0.6)
    else:
        return Square(side_length=size,
                      fill_color=color, fill_opacity=0.85,
                      stroke_color=color, stroke_width=2.5)


def make_pattern_row(shape_names, colors=None,
                     size=0.55, buff=0.3, default_color=PURPLE):
    """
    Build a VGroup row of shapes with index labels below each.
    shape_names: list of 'circle'|'square'|'triangle'
    colors: optional list of colors per shape (same length)
    Returns VGroup of (shape, label) pairs.
    """
    if colors is None:
        colors = [default_color] * len(shape_names)
    items = VGroup()
    for i, (sn, col) in enumerate(zip(shape_names, colors)):
        sh = make_shape_element(sn, size=size, color=col)
        lbl = Text(str(i + 1), font="Poppins",
                   font_size=18, color=PALE_PURPLE)
        lbl.next_to(sh, DOWN, buff=0.12)
        pair = VGroup(sh, lbl)
        items.add(pair)
    items.arrange(RIGHT, buff=buff)
    return items


# ── MAIN SCENE ────────────────────────────────────────────────────────────────

class RepeatingPatternsScene(VoiceoverScene):

    def construct(self):
        self._setup_tts()
        self.show_title()
        self.show_concept_hook()
        self.show_concept_cycle_length()
        self.show_concept_remainder_rule()
        self.show_concept_worked_example()
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

    # ── CONCEPT 1: TRAFFIC LIGHT HOOK ────────────────────────────────────────

    def show_concept_hook(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        # Build traffic light circles
        c_red   = make_traffic_circle(RED_COL)
        c_amber = make_traffic_circle(AMBER_COL)
        c_green = make_traffic_circle(GREEN_COL)

        c_red.move_to(LEFT * 2.5 + UP * 0.5)
        c_amber.move_to(ORIGIN  + UP * 0.5)
        c_green.move_to(RIGHT * 2.5 + UP * 0.5)

        # Labels under each circle
        lbl_r = Text("Red",   font="Poppins", font_size=20, color=RED_COL)
        lbl_a = Text("Amber", font="Poppins", font_size=20, color=AMBER_COL)
        lbl_g = Text("Green", font="Poppins", font_size=20, color=GREEN_COL)
        lbl_r.next_to(c_red,   DOWN, buff=0.15)
        lbl_a.next_to(c_amber, DOWN, buff=0.15)
        lbl_g.next_to(c_green, DOWN, buff=0.15)

        with self.voiceover(
            text=(
                '<bookmark mark="bk_traffic"/>Think about traffic lights —'
                ' they cycle through red, amber, and green, then repeat. '
                '<bookmark mark="bk_forty"/>If someone asks what colour is'
                ' showing at the fortieth change,'
                ' you would not count all forty. '
                '<bookmark mark="bk_clever"/>You would spot the repeating'
                ' cycle, and use it cleverly.'
            )
        ) as tracker:

            # Pattern A: circles appear one by one
            self.wait_until_bookmark("bk_traffic")
            self.play(FadeIn(c_red), FadeIn(lbl_r), run_time=0.6)
            active_mobs.extend([c_red, lbl_r])
            self.wait(0.2)
            self.play(FadeIn(c_amber), FadeIn(lbl_a), run_time=0.6)
            active_mobs.extend([c_amber, lbl_a])
            self.wait(0.2)
            self.play(FadeIn(c_green), FadeIn(lbl_g), run_time=0.6)
            active_mobs.extend([c_green, lbl_g])

            # Curved loop arrow from green back toward red
            loop_arrow = CurvedArrow(
                c_green.get_top() + UP * 0.05,
                c_red.get_top()   + UP * 0.05,
                angle=-PI / 2.5,
                color=PALE_PURPLE, stroke_width=2.5,
                tip_length=0.18
            )
            check_safe_margins(loop_arrow, "loop_arrow")
            self.play(FadeIn(loop_arrow), run_time=0.6)
            active_mobs.append(loop_arrow)

            # "40th?" label
            self.wait_until_bookmark("bk_forty")
            forty_lbl = Text(
                "40th?", font="Poppins",
                font_size=32, color=ORANGE_HL
            )
            forty_lbl.move_to(UP * 2.0)
            check_safe_margins(forty_lbl, "forty_lbl")
            self.play(FadeIn(forty_lbl), run_time=0.5)
            active_mobs.append(forty_lbl)

            # Bridge card
            self.wait_until_bookmark("bk_clever")
            bridge = make_concept_card(
                "Spot the cycle — use it cleverly",
                position=DOWN * 2.2,
                font_size=24
            )
            check_safe_margins(bridge, "bridge")
            self.play(FadeIn(bridge), run_time=0.7)
            active_mobs.append(bridge)

        self.wait(0.4)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── CONCEPT 2: CYCLE LENGTH ───────────────────────────────────────────────

    def show_concept_cycle_length(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        # Two full cycles of R A G R A G as coloured circles
        cycle_colors  = [RED_COL, AMBER_COL, GREEN_COL,
                         RED_COL, AMBER_COL, GREEN_COL]
        cycle_circles = VGroup()
        for col in cycle_colors:
            c = make_traffic_circle(col, radius=0.30)
            cycle_circles.add(c)
        cycle_circles.arrange(RIGHT, buff=0.22)
        cycle_circles.move_to(UP * 0.5)
        check_safe_margins(cycle_circles, "cycle_circles")

        # Index labels 1–6 below each circle
        idx_labels = VGroup()
        for i, c in enumerate(cycle_circles):
            lbl = Text(str(i + 1), font="Poppins",
                       font_size=18, color=PALE_PURPLE)
            lbl.next_to(c, DOWN, buff=0.1)
            idx_labels.add(lbl)

        with self.voiceover(
            text=(
                '<bookmark mark="bk_repeating"/>A repeating pattern cycles'
                ' through a fixed set of elements before starting again. '
                '<bookmark mark="bk_cycle_length"/>The number of elements'
                ' in one complete cycle is called the cycle length. '
                '<bookmark mark="bk_three"/>For the traffic light,'
                ' the cycle length is three.'
            )
        ) as tracker:

            # Show two full cycles
            self.wait_until_bookmark("bk_repeating")
            self.play(
                FadeIn(cycle_circles),
                FadeIn(idx_labels),
                run_time=0.8
            )
            active_mobs.extend([cycle_circles, idx_labels])

            # Pattern D: brace under first 3 circles
            self.wait_until_bookmark("bk_cycle_length")
            first3 = VGroup(*[cycle_circles[i] for i in range(3)])
            brace = Brace(first3, DOWN, color=PURPLE, buff=0.35)
            brace_lbl = Text(
                "cycle length", font="Poppins",
                font_size=22, color=PURPLE
            )
            brace_lbl.next_to(brace, DOWN, buff=0.12)
            check_safe_margins(brace,     "brace")
            check_safe_margins(brace_lbl, "brace_lbl")
            self.play(FadeIn(brace), FadeIn(brace_lbl), run_time=0.7)
            active_mobs.extend([brace, brace_lbl])

            # Highlight "3"
            self.wait_until_bookmark("bk_three")
            three_lbl = Text(
                "3", font="Poppins",
                font_size=44, color=ORANGE_HL
            )
            three_lbl.next_to(brace, DOWN, buff=0.08)
            three_lbl.shift(RIGHT * 1.8)
            check_safe_margins(three_lbl, "three_lbl")
            self.play(FadeIn(three_lbl), run_time=0.5)
            active_mobs.append(three_lbl)

        self.wait(0.4)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── CONCEPT 3: THE REMAINDER RULE ────────────────────────────────────────

    def show_concept_remainder_rule(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        # Small cycle annotation row (R A G) for reference
        annot_colors = [RED_COL, AMBER_COL, GREEN_COL]
        annot_circles = VGroup()
        pos_labels    = VGroup()
        for idx, col in enumerate(annot_colors):
            c = make_traffic_circle(col, radius=0.28)
            annot_circles.add(c)
            pl = Text(str(idx + 1), font="Poppins",
                      font_size=18, color=PALE_PURPLE)
            pos_labels.add(pl)
        annot_circles.arrange(RIGHT, buff=0.25)
        annot_circles.move_to(DOWN * 0.5)
        for i, c in enumerate(annot_circles):
            pos_labels[i].next_to(c, DOWN, buff=0.1)
        check_safe_margins(annot_circles, "annot_circles")

        with self.voiceover(
            text=(
                '<bookmark mark="bk_divide"/>To find which element appears'
                ' at position n, we divide n by the cycle length,'
                ' and look at the remainder. '
                '<bookmark mark="bk_remainder_tells"/>The remainder tells us'
                ' exactly where we are within the current cycle. '
                '<bookmark mark="bk_rem_one"/>A remainder of one points to'
                ' the first element, a remainder of two to the second,'
                ' and so on. '
                '<bookmark mark="bk_rem_zero"/>If the remainder is zero,'
                ' we have landed exactly on the last element of the cycle.'
            )
        ) as tracker:

            # Pattern F: build division rule expression part by part
            self.wait_until_bookmark("bk_divide")
            r_n    = math_obj(r"n",             font_size=36)
            r_div  = math_obj(r"\div",          font_size=36)
            r_cl   = math_obj(r"\text{cycle length}", font_size=32)
            r_arr  = math_obj(r"\rightarrow",   font_size=32,
                              color=PALE_PURPLE)
            r_rem  = math_obj(r"\text{remainder}", font_size=32,
                              color=ORANGE_HL)
            rule_row = VGroup(
                r_n, r_div, r_cl, r_arr, r_rem
            ).arrange(RIGHT, buff=0.2)
            rule_row.move_to(UP * 1.5)
            check_safe_margins(rule_row, "rule_row")

            # Reveal part by part
            self.play(FadeIn(r_n), run_time=0.4)
            self.play(FadeIn(r_div), FadeIn(r_cl), run_time=0.5)
            self.play(FadeIn(r_arr), FadeIn(r_rem), run_time=0.5)
            active_mobs.append(rule_row)

            # Pattern B: arrow from "remainder" down to cycle row
            self.wait_until_bookmark("bk_remainder_tells")
            self.play(
                FadeIn(annot_circles),
                FadeIn(pos_labels),
                run_time=0.7
            )
            active_mobs.extend([annot_circles, pos_labels])

            rule_arrow = Arrow(
                r_rem.get_bottom() + DOWN * 0.05,
                annot_circles.get_top() + UP * 0.05,
                color=ORANGE_HL, stroke_width=2.5,
                tip_length=0.18, buff=0
            )
            check_safe_margins(rule_arrow, "rule_arrow")
            self.play(FadeIn(rule_arrow), run_time=0.5)
            active_mobs.append(rule_arrow)

            # Pattern D: highlight each circle at its remainder
            self.wait_until_bookmark("bk_rem_one")
            # Remainder 1 → RED (index 0)
            self.play(
                annot_circles[0].animate.set_stroke(
                    color=ORANGE_HL, width=4.0
                ),
                run_time=0.5
            )
            rem1_lbl = Text(
                "rem 1", font="Poppins",
                font_size=20, color=ORANGE_HL
            )
            rem1_lbl.next_to(annot_circles[0], UP, buff=0.18)
            check_safe_margins(rem1_lbl, "rem1_lbl")
            self.play(FadeIn(rem1_lbl), run_time=0.4)
            active_mobs.append(rem1_lbl)
            self.wait(0.2)

            # Remainder 2 → AMBER (index 1)
            self.play(
                annot_circles[1].animate.set_stroke(
                    color=ORANGE_HL, width=4.0
                ),
                run_time=0.5
            )
            rem2_lbl = Text(
                "rem 2", font="Poppins",
                font_size=20, color=ORANGE_HL
            )
            rem2_lbl.next_to(annot_circles[1], UP, buff=0.18)
            check_safe_margins(rem2_lbl, "rem2_lbl")
            self.play(FadeIn(rem2_lbl), run_time=0.4)
            active_mobs.append(rem2_lbl)

            # Pattern C: zero remainder contrast — two mini panels
            self.wait_until_bookmark("bk_rem_zero")

            # LEFT: nonzero remainder → normal position
            nz_bg = RoundedRectangle(
                corner_radius=0.15, width=2.8, height=1.2,
                fill_color=WHITE, fill_opacity=0.85,
                stroke_color=PALE_PURPLE, stroke_width=1.5
            )
            nz_bg.move_to(LEFT * 2.8 + DOWN * 2.0)
            nz_txt = Text(
                "rem = 1 or 2\n→ 1st or 2nd element",
                font="Poppins", font_size=18, color=PURPLE
            )
            nz_txt.move_to(nz_bg.get_center())
            nz_panel = VGroup(nz_bg, nz_txt)
            check_safe_margins(nz_panel, "nz_panel")

            # RIGHT: zero remainder → last element
            z_bg = RoundedRectangle(
                corner_radius=0.15, width=2.8, height=1.2,
                fill_color=WHITE, fill_opacity=0.85,
                stroke_color=ORANGE_HL, stroke_width=2.0
            )
            z_bg.move_to(RIGHT * 2.0 + DOWN * 2.0)
            z_txt = Text(
                "rem = 0\n→ last element (3rd)",
                font="Poppins", font_size=18, color=ORANGE_HL,
                
            )
            z_txt.move_to(z_bg.get_center())
            z_panel = VGroup(z_bg, z_txt)
            check_safe_margins(z_panel, "z_panel")

            self.play(FadeIn(nz_panel), run_time=0.6)
            active_mobs.append(nz_panel)
            self.play(FadeIn(z_panel), run_time=0.6)
            active_mobs.append(z_panel)

        self.wait(0.5)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── CONCEPT 4: WORKED EXAMPLE (POSITION 40) ──────────────────────────────

    def show_concept_worked_example(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        # Traffic light row (R A G) RIGHT zone
        tl_r = make_traffic_circle(RED_COL,   radius=0.30)
        tl_a = make_traffic_circle(AMBER_COL, radius=0.30)
        tl_g = make_traffic_circle(GREEN_COL, radius=0.30)
        tl_row = VGroup(tl_r, tl_a, tl_g).arrange(RIGHT, buff=0.22)
        tl_row.move_to(RIGHT * 3.2 + UP * 0.8)
        check_safe_margins(tl_row, "tl_row")

        # Position labels under each
        tl_lbl_r = Text("1", font="Poppins", font_size=18, color=PALE_PURPLE)
        tl_lbl_a = Text("2", font="Poppins", font_size=18, color=PALE_PURPLE)
        tl_lbl_g = Text("3", font="Poppins", font_size=18, color=PALE_PURPLE)
        tl_lbl_r.next_to(tl_r, DOWN, buff=0.1)
        tl_lbl_a.next_to(tl_a, DOWN, buff=0.1)
        tl_lbl_g.next_to(tl_g, DOWN, buff=0.1)
        tl_labels = VGroup(tl_lbl_r, tl_lbl_a, tl_lbl_g)

        self.play(FadeIn(tl_row), FadeIn(tl_labels), run_time=0.7)
        active_mobs.extend([tl_row, tl_labels])

        # StepManager: 4 steps, font_size=28, buff=0.35
        # height ≈ 4×(0.44+0.35) = 3.16 ✓
        anchor = UP * 2.0 + LEFT * 3.5

        with self.voiceover(
            text=(
                '<bookmark mark="bk_pos40"/>For the traffic light —'
                ' position forty. '
                '<bookmark mark="bk_div40"/>Divide forty by three. '
                '<bookmark mark="bk_result40"/>Forty divided by three'
                ' gives thirteen, with a remainder of one. '
                '<bookmark mark="bk_rem1_red"/>Remainder one means we are'
                ' at the first element — red. '
                '<bookmark mark="bk_answer40"/>The fortieth position shows red.'
            )
        ) as tracker:

            mgr = StepManager(
                self, start_anchor=anchor,
                font_size=28, buff=0.35
            )

            # Step 1: Position 40
            self.wait_until_bookmark("bk_pos40")
            s1 = math_obj(r"\text{Position: } 40", font_size=28)
            mgr.add_step(s1)
            active_mobs.append(s1)

            # Step 2: 40 ÷ 3
            self.wait_until_bookmark("bk_div40")
            s2 = math_obj(r"40 \div 3", font_size=28)
            mgr.add_step(s2)
            active_mobs.append(s2)

            # Step 3: = 13 remainder 1
            self.wait_until_bookmark("bk_result40")
            s3 = math_obj(
                r"= 13 \text{ remainder } 1",
                font_size=28
            )
            mgr.add_step(s3)
            active_mobs.append(s3)

            # Step 4: remainder 1 → RED — pulse the red circle
            self.wait_until_bookmark("bk_rem1_red")
            self.play(
                tl_r.animate.set_stroke(color=ORANGE_HL, width=4.5),
                run_time=0.5
            )
            s4 = math_obj(
                r"\text{rem } 1 \rightarrow \text{RED}",
                font_size=28, color=ORANGE_HL
            )
            mgr.add_step(s4)
            active_mobs.append(s4)

            # Conclusion echo
            self.wait_until_bookmark("bk_answer40")
            conclusion = math_obj(
                r"\text{Position 40} = \text{Red}",
                font_size=32, color=ORANGE_HL
            )
            # Placed below the step stack, centered LEFT zone
            conclusion.next_to(s4, DOWN, buff=0.5)
            check_safe_margins(conclusion, "conclusion")
            self.play(FadeIn(conclusion), run_time=0.7)
            active_mobs.append(conclusion)

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
                '<bookmark mark="bk_question"/>A pattern repeats —'
                ' circle, square, triangle — then repeats. '
                '<bookmark mark="bk_q29"/>What shape appears at'
                ' position twenty-nine?'
            )
        ) as tracker:

            self.wait_until_bookmark("bk_question")

            q_text = Text(
                "What shape appears at position 29?",
                font="Poppins", font_size=28, color=PURPLE
            )
            q_text.move_to(UP * 2.5)
            check_safe_margins(q_text, "q_text")
            self.play(FadeIn(q_text), run_time=0.6)
            active_mobs.append(q_text)

            # Two full cycles of circle, square, triangle
            shape_seq = ["circle", "square", "triangle",
                         "circle", "square", "triangle"]
            shape_colors_q = [PURPLE] * 6
            q_row = make_pattern_row(
                shape_seq, colors=shape_colors_q,
                size=0.55, buff=0.28
            )
            q_row.move_to(ORIGIN)
            check_safe_margins(q_row, "q_row")

            self.wait_until_bookmark("bk_q29")
            self.play(FadeIn(q_row), run_time=0.8)
            active_mobs.append(q_row)

            # "29th?" label below
            pos29_lbl = Text(
                "29th?", font="Poppins",
                font_size=30, color=ORANGE_HL
            )
            pos29_lbl.next_to(q_row, DOWN, buff=0.35)
            check_safe_margins(pos29_lbl, "pos29_lbl")
            self.play(FadeIn(pos29_lbl), run_time=0.5)
            active_mobs.append(pos29_lbl)

        self._q_row      = q_row
        self._pos29_lbl  = pos29_lbl
        self._q_text     = q_text
        self._q_badge    = badge
        self._active_q   = list(active_mobs)

    # ── SOLUTION ──────────────────────────────────────────────────────────────

    def show_solution(self):
        # STACK HEIGHT PRE-COMPUTATION:
        # 4 steps, font_size=28, buff=0.3 → 4×(0.44+0.3)=2.96 ✓
        # LIMITS[(28,0.3)] = 4 ✓

        active_mobs = list(self._active_q)

        # Swap badge
        sol_badge = create_heading_badge("Solution")
        self.play(
            FadeOut(self._q_badge),
            FadeIn(sol_badge),
            run_time=0.5
        )
        active_mobs[0] = sol_badge

        # Shift shape row and pos label to right zone
        self.play(
            self._q_row.animate.move_to(RIGHT * 3.0 + UP * 0.3),
            self._pos29_lbl.animate.move_to(RIGHT * 3.0 + DOWN * 0.8),
            self._q_text.animate.move_to(UP * 2.8),
            run_time=1.0
        )

        anchor = UP * 2.0 + LEFT * 3.5

        with self.voiceover(
            text=(
                '<bookmark mark="bk_s1"/>Cycle length is three. '
                '<bookmark mark="bk_s2"/>Divide twenty-nine by three —'
                ' nine groups of three, with a remainder of two. '
                '<bookmark mark="bk_s3"/>Remainder two corresponds to the'
                ' second element — square. '
                '<bookmark mark="bk_s4"/>The shape at position twenty-nine'
                ' is a square.'
            )
        ) as tracker:

            mgr = StepManager(
                self, start_anchor=anchor,
                font_size=28, buff=0.3
            )

            # Step 1: cycle length = 3
            self.wait_until_bookmark("bk_s1")
            s1 = math_obj(
                r"\text{Cycle length} = 3",
                font_size=28
            )
            mgr.add_step(s1)
            active_mobs.append(s1)

            # Step 2: 29 ÷ 3 = 9 remainder 2
            self.wait_until_bookmark("bk_s2")
            s2 = math_obj(
                r"29 \div 3 = 9 \text{ remainder } 2",
                font_size=28
            )
            mgr.add_step(s2)
            active_mobs.append(s2)

            # Step 3: remainder 2 → 2nd element → square
            # Highlight 2nd shape (square, index 1) in the right-zone row
            self.wait_until_bookmark("bk_s3")
            # q_row[1] is the 2nd pair (square at position 2 in cycle)
            # Each pair: VGroup(shape, label)
            self.play(
                self._q_row[1][0].animate.set_color(ORANGE_HL),
                run_time=0.5
            )
            s3 = math_obj(
                r"\text{rem } 2 \rightarrow \text{2nd} \rightarrow"
                r"\text{Square}",
                font_size=28, color=ORANGE_HL
            )
            mgr.add_step(s3)
            active_mobs.append(s3)

            # Step 4: final answer
            self.wait_until_bookmark("bk_s4")
            s4 = math_obj(
                r"\text{Position 29} = \text{Square}",
                font_size=28, color=ORANGE_HL
            )
            mgr.add_step(s4)
            active_mobs.append(s4)

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
            "A repeating pattern cycles through a fixed set"
            " of elements before starting again.",
            "The remainder tells us exactly where we are"
            " within the current cycle.",
            "If the remainder is zero, we have landed exactly"
            " on the last element of the cycle.",
        ]
        positions = [UP * 1.5, ORIGIN, DOWN * 1.5]

        with self.voiceover(
            text=(
                '<bookmark mark="bk_sum1"/>A repeating pattern cycles through'
                ' a fixed set of elements before starting again. '
                '<bookmark mark="bk_sum2"/>The remainder tells us exactly'
                ' where we are within the current cycle. '
                '<bookmark mark="bk_sum3"/>If the remainder is zero, we have'
                ' landed exactly on the last element of the cycle.'
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