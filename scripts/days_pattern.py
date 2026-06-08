import os
import urllib.request
import manimpango
from dotenv import load_dotenv
from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.openai import OpenAIService

load_dotenv()

LAVENDER_BG  = "#E7E5F3"
PURPLE       = "#7464CE"
ORANGE_HL    = "#FF9302"
PALE_PURPLE  = "#9495D7"
GREEN_OK     = "#2E8B57"

# Colour palette for the question sequence
COL_YELLOW   = "#F5C518"
COL_BLUE     = "#4A90D9"
COL_GREEN    = "#2E8B57"
COL_RED      = "#D62828"

# Day-of-week display colour
DAY_FILL     = "#D6D0F0"


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
Slow down on key terms: cycle length, remainder, position.
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
        mt = mob.get_top()[1]
        mb = mob.get_bottom()[1]
        if nb < mt and nt > mb:
            shift_needed = mt + min_gap - nb
            new_mob.shift(UP * shift_needed)
            print(f"WARNING: '{name}' overlapped. "
                  f"Shifted UP {shift_needed:.2f}")
        elif nb >= mt and (nb - mt) < min_gap:
            shift_needed = min_gap - (nb - mt)
            new_mob.shift(UP * shift_needed)
            print(f"WARNING: '{name}' too close. "
                  f"Shifted UP {shift_needed:.2f}")
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


# ── DAY BOX HELPER ────────────────────────────────────────────────────────────

def make_day_box(day_abbr, box_w=0.78, box_h=0.55, font_size=18):
    """Single labelled box for a day of the week."""
    bg = Rectangle(
        width=box_w, height=box_h,
        fill_color=DAY_FILL, fill_opacity=1.0,
        stroke_color=PURPLE, stroke_width=2.0
    )
    lbl = Text(day_abbr, font="Poppins",
               font_size=font_size, color=PURPLE)
    lbl.move_to(bg.get_center())
    return VGroup(bg, lbl)


def make_day_row(font_size=18):
    """Full 7-day row arranged RIGHT."""
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    boxes = [make_day_box(d, font_size=font_size) for d in days]
    row = VGroup(*boxes).arrange(RIGHT, buff=0.06)
    if row.width > 9.0:
        row.scale(9.0 / row.width)
    return row, boxes


# ── COLOUR BOX HELPER ─────────────────────────────────────────────────────────

def make_colour_box(fill_col, label_str, box_w=0.85, box_h=0.65,
                    font_size=16):
    """Filled coloured box with text label."""
    bg = Rectangle(
        width=box_w, height=box_h,
        fill_color=fill_col, fill_opacity=0.85,
        stroke_color=PURPLE, stroke_width=2.0
    )
    lbl = Text(label_str, font="Poppins",
               font_size=font_size, color=WHITE)
    lbl.move_to(bg.get_center())
    return VGroup(bg, lbl)


def make_colour_row(n_cycles=2, font_size=16):
    """
    Two complete cycles of yellow/blue/green/red.
    Returns (VGroup of 8 pairs, list of individual VGroup pairs).
    """
    seq = [
        (COL_YELLOW, "Yellow"),
        (COL_BLUE,   "Blue"),
        (COL_GREEN,  "Green"),
        (COL_RED,    "Red"),
    ]
    boxes = []
    for _ in range(n_cycles):
        for col, lbl in seq:
            boxes.append(make_colour_box(col, lbl, font_size=font_size))
    row = VGroup(*boxes).arrange(RIGHT, buff=0.06)
    if row.width > 9.5:
        row.scale(9.5 / row.width)
    return row, boxes


# ── MAIN SCENE ────────────────────────────────────────────────────────────────

class RepeatingPatternsDaysScene(VoiceoverScene):

    def construct(self):
        self._setup_tts()
        self.show_title()
        self.show_concept_hook()
        self.show_concept_rule()
        self.show_concept_worked()
        self.show_concept_zero_rem()
        self.show_concept_realworld()
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

    # ── CONCEPT 1: DAYS OF THE WEEK HOOK ─────────────────────────────────────

    def show_concept_hook(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        # Build day row (hidden initially — revealed box by box)
        day_row, day_boxes = make_day_row(font_size=18)
        day_row.move_to(UP * 0.6)
        check_safe_margins(day_row, "day_row")

        with self.voiceover(
            text=(
                '<bookmark mark="bk_days"/>Think about days of the week. '
                'Monday, Tuesday, Wednesday, Thursday,'
                ' Friday, Saturday, Sunday — then back to Monday. '
                '<bookmark mark="bk_thirty"/>If today is Monday and you want'
                ' to know what day it will be in thirty days,'
                ' you would not count day by day all the way to thirty. '
                '<bookmark mark="bk_cycle"/>You would use the cycle. '
                '<bookmark mark="bk_tool"/>And the mathematical tool for this,'
                ' is the remainder.'
            )
        ) as tracker:

            # Pattern A: intro card then boxes one by one
            self.wait_until_bookmark("bk_days")
            intro_card = make_concept_card(
                "Think about days of the week",
                position=UP * 2.0, font_size=24
            )
            check_safe_margins(intro_card, "intro_card")
            self.play(FadeIn(intro_card), run_time=0.6)
            active_mobs.append(intro_card)

            # Reveal day boxes one by one
            for i, box in enumerate(day_boxes):
                self.play(FadeIn(box), run_time=0.25)
                if i == 0:
                    active_mobs.append(day_row)
            # (day_row is parent — all boxes are children; track parent only)

            # Curved loop arrow from Sun back toward Mon
            loop_arrow = CurvedArrow(
                day_boxes[6].get_top() + UP * 0.05,
                day_boxes[0].get_top() + UP * 0.05,
                angle=-PI / 2.2,
                color=PALE_PURPLE, stroke_width=2.5,
                tip_length=0.18
            )
            check_safe_margins(loop_arrow, "loop_arrow")
            self.play(FadeIn(loop_arrow), run_time=0.5)
            active_mobs.append(loop_arrow)

            # "30th?" label
            self.wait_until_bookmark("bk_thirty")
            thirty_lbl = Text(
                "30th?", font="Poppins",
                font_size=30, color=ORANGE_HL
            )
            thirty_lbl.move_to(UP * 2.0)
            # Remove intro_card first to avoid overlap at UP*2.0
            self.play(FadeOut(intro_card), run_time=0.4)
            active_mobs.remove(intro_card)
            check_safe_margins(thirty_lbl, "thirty_lbl")
            self.play(FadeIn(thirty_lbl), run_time=0.5)
            active_mobs.append(thirty_lbl)

            # Pulse loop arrow ORANGE_HL
            self.wait_until_bookmark("bk_cycle")
            self.play(
                loop_arrow.animate.set_color(ORANGE_HL),
                run_time=0.5
            )
            self.wait(0.3)
            self.play(
                loop_arrow.animate.set_color(PALE_PURPLE),
                run_time=0.3
            )

            # Tool card
            self.wait_until_bookmark("bk_tool")
            tool_card = make_concept_card(
                "Mathematical tool: the remainder",
                position=DOWN * 2.0, font_size=24
            )
            check_safe_margins(tool_card, "tool_card")
            self.play(FadeIn(tool_card), run_time=0.7)
            active_mobs.append(tool_card)

        self.wait(0.4)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── CONCEPT 2: THE REMAINDER RULE ────────────────────────────────────────

    def show_concept_rule(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        # Pattern F: build division rule expression part by part
        r_pos  = math_obj(r"\text{position}",    font_size=32)
        r_div  = math_obj(r"\div",               font_size=32)
        r_cl   = math_obj(r"\text{cycle length}", font_size=32)
        r_arr  = math_obj(r"\rightarrow",         font_size=28,
                          color=PALE_PURPLE)
        r_rem  = math_obj(r"\text{remainder}",    font_size=32,
                          color=ORANGE_HL)
        rule_row = VGroup(
            r_pos, r_div, r_cl, r_arr, r_rem
        ).arrange(RIGHT, buff=0.18)
        rule_row.move_to(UP * 1.2)
        check_safe_margins(rule_row, "rule_row")

        # Mini 3-box cycle row for Pattern B demonstration
        mini_boxes = VGroup()
        for i in range(1, 4):
            bg = Rectangle(
                width=0.7, height=0.5,
                fill_color=DAY_FILL, fill_opacity=1.0,
                stroke_color=PURPLE, stroke_width=1.8
            )
            lbl = Text(str(i), font="Poppins",
                       font_size=20, color=PURPLE)
            lbl.move_to(bg.get_center())
            mini_boxes.add(VGroup(bg, lbl))
        mini_boxes.arrange(RIGHT, buff=0.1)
        mini_boxes.move_to(DOWN * 0.5)
        check_safe_margins(mini_boxes, "mini_boxes")

        with self.voiceover(
            text=(
                '<bookmark mark="bk_rule"/>When a pattern repeats with a'
                ' fixed cycle length — the number of elements in one complete'
                ' cycle — we use division with remainders,'
                ' to find any position quickly. '
                '<bookmark mark="bk_remainder_tells"/>The remainder after'
                ' dividing the position number by the cycle length,'
                ' tells us exactly where we land within the cycle.'
            )
        ) as tracker:

            # Reveal rule expression part by part
            self.wait_until_bookmark("bk_rule")
            self.play(FadeIn(r_pos), run_time=0.4)
            self.play(FadeIn(r_div), FadeIn(r_cl), run_time=0.5)
            self.play(FadeIn(r_arr), FadeIn(r_rem), run_time=0.5)
            active_mobs.append(rule_row)

            # Pattern B: mini cycle row + arrow from remainder to it
            self.wait_until_bookmark("bk_remainder_tells")
            self.play(FadeIn(mini_boxes), run_time=0.6)
            active_mobs.append(mini_boxes)

            rule_arrow = Arrow(
                r_rem.get_bottom() + DOWN * 0.05,
                mini_boxes.get_top() + UP * 0.05,
                color=ORANGE_HL, stroke_width=2.5,
                tip_length=0.18, buff=0
            )
            check_safe_margins(rule_arrow, "rule_arrow")
            self.play(FadeIn(rule_arrow), run_time=0.5)
            active_mobs.append(rule_arrow)

            # Highlight middle box (pos 2) to show remainder-2 landing
            self.play(
                mini_boxes[1][0].animate.set_fill(
                    color=ORANGE_HL, opacity=0.85
                ),
                run_time=0.5
            )
            self.wait(0.4)
            self.play(
                mini_boxes[1][0].animate.set_fill(
                    color=DAY_FILL, opacity=1.0
                ),
                run_time=0.3
            )

        self.wait(0.4)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── CONCEPT 3: WORKED EXAMPLE (DAYS) ─────────────────────────────────────

    def show_concept_worked(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        # Day row in RIGHT zone
        day_row, day_boxes = make_day_row(font_size=16)
        day_row.move_to(RIGHT * 3.0 + UP * 1.2)
        check_safe_margins(day_row, "day_row_right")

        # Index labels 1–7 below each box
        idx_labels = VGroup()
        for i, box in enumerate(day_boxes):
            lbl = Text(str(i + 1), font="Poppins",
                       font_size=14, color=PALE_PURPLE)
            lbl.next_to(box, DOWN, buff=0.08)
            idx_labels.add(lbl)

        self.play(FadeIn(day_row), FadeIn(idx_labels), run_time=0.7)
        active_mobs.extend([day_row, idx_labels])

        # Brace under all 7 boxes
        brace7 = Brace(day_row, DOWN, color=PURPLE, buff=0.28)
        brace_lbl7 = Text(
            "7", font="Poppins",
            font_size=28, color=ORANGE_HL
        )
        brace_lbl7.next_to(brace7, DOWN, buff=0.08)
        check_safe_margins(brace7,     "brace7")
        check_safe_margins(brace_lbl7, "brace_lbl7")

        anchor = UP * 2.0 + LEFT * 3.5

        with self.voiceover(
            text=(
                '<bookmark mark="bk_seven"/>For the days of the week,'
                ' the cycle length is seven. '
                '<bookmark mark="bk_pos30"/>Counting from Monday as position'
                ' one, position thirty means we divide thirty by seven. '
                '<bookmark mark="bk_four_rem2"/>Seven goes into thirty four'
                ' times, with a remainder of two. '
                '<bookmark mark="bk_tuesday"/>Remainder two points to the'
                ' second element of the cycle — Tuesday. '
                '<bookmark mark="bk_so_tuesday"/>So thirty days from Monday'
                ' is a Tuesday.'
            )
        ) as tracker:

            # Show brace + label 7
            self.wait_until_bookmark("bk_seven")
            self.play(FadeIn(brace7), FadeIn(brace_lbl7), run_time=0.6)
            active_mobs.extend([brace7, brace_lbl7])

            mgr = StepManager(
                self, start_anchor=anchor,
                font_size=28, buff=0.32
            )

            # Step 1: 30 ÷ 7
            self.wait_until_bookmark("bk_pos30")
            s1 = math_obj(r"30 \div 7", font_size=28)
            mgr.add_step(s1)
            active_mobs.append(s1)

            # Step 2: = 4 remainder 2
            self.wait_until_bookmark("bk_four_rem2")
            s2 = math_obj(
                r"= 4 \text{ remainder } 2",
                font_size=28
            )
            mgr.add_step(s2)
            active_mobs.append(s2)

            # Step 3: rem 2 → Tue; highlight Tue box
            self.wait_until_bookmark("bk_tuesday")
            self.play(
                day_boxes[1][0].animate.set_fill(
                    color=ORANGE_HL, opacity=0.9
                ),
                run_time=0.5
            )
            s3 = math_obj(
                r"\text{rem } 2 \rightarrow \text{Tuesday}",
                font_size=28, color=ORANGE_HL
            )
            mgr.add_step(s3)
            active_mobs.append(s3)

            # Conclusion echo
            self.wait_until_bookmark("bk_so_tuesday")
            conclusion = math_obj(
                r"\text{Day 30} = \text{Tuesday}",
                font_size=30, color=ORANGE_HL
            )
            conclusion.next_to(s3, DOWN, buff=0.45)
            check_safe_margins(conclusion, "conclusion")
            self.play(FadeIn(conclusion), run_time=0.7)
            active_mobs.append(conclusion)

        self.wait(0.5)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── CONCEPT 4: ZERO REMAINDER ─────────────────────────────────────────────

    def show_concept_zero_rem(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        with self.voiceover(
            text=(
                '<bookmark mark="bk_zero"/>If the remainder is zero,'
                ' we are at the last element of the cycle. '
                '<bookmark mark="bk_never_ignore"/>A remainder of zero'
                ' is a meaningful answer — never ignore it.'
            )
        ) as tracker:

            # Pattern C: two side-by-side contrast panels
            self.wait_until_bookmark("bk_zero")

            # LEFT panel — nonzero remainder
            nz_bg = RoundedRectangle(
                corner_radius=0.18, width=3.2, height=1.6,
                fill_color=WHITE, fill_opacity=0.88,
                stroke_color=PALE_PURPLE, stroke_width=1.8
            )
            nz_bg.move_to(LEFT * 2.8 + UP * 0.1)
            nz_title = Text(
                "rem = 2", font="Poppins",
                font_size=22, color=PURPLE
            )
            nz_title.move_to(nz_bg.get_center() + UP * 0.28)
            nz_desc = Text(
                "2nd element",
                font="Poppins", font_size=20, color=PURPLE
            )
            nz_desc.move_to(nz_bg.get_center() + DOWN * 0.22)
            nz_panel = VGroup(nz_bg, nz_title, nz_desc)
            check_safe_margins(nz_panel, "nz_panel")

            # RIGHT panel — zero remainder (ORANGE_HL border)
            z_bg = RoundedRectangle(
                corner_radius=0.18, width=3.2, height=1.6,
                fill_color=WHITE, fill_opacity=0.88,
                stroke_color=ORANGE_HL, stroke_width=2.5
            )
            z_bg.move_to(RIGHT * 1.8 + UP * 0.1)
            z_title = Text(
                "rem = 0", font="Poppins",
                font_size=22, color=ORANGE_HL
            )
            z_title.move_to(z_bg.get_center() + UP * 0.28)
            z_desc = Text(
                "LAST element",
                font="Poppins", font_size=20,
                color=ORANGE_HL
            )
            z_desc.move_to(z_bg.get_center() + DOWN * 0.22)
            z_panel = VGroup(z_bg, z_title, z_desc)
            check_safe_margins(z_panel, "z_panel")

            self.play(FadeIn(nz_panel), run_time=0.7)
            active_mobs.append(nz_panel)
            self.play(FadeIn(z_panel), run_time=0.7)
            active_mobs.append(z_panel)

            # "Never ignore it!" warning below right panel
            self.wait_until_bookmark("bk_never_ignore")
            self.play(
                z_bg.animate.set_stroke(color=ORANGE_HL, width=4.0),
                run_time=0.4
            )
            never_lbl = Text(
                "Never ignore it!",
                font="Poppins", font_size=22,
                color=ORANGE_HL
            )
            never_lbl.next_to(z_panel, DOWN, buff=0.28)
            check_safe_margins(never_lbl, "never_lbl")
            self.play(FadeIn(never_lbl), run_time=0.5)
            active_mobs.append(never_lbl)

        self.wait(0.5)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── CONCEPT 5: REAL-WORLD APPLICATION ────────────────────────────────────

    def show_concept_realworld(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        with self.voiceover(
            text=(
                '<bookmark mark="bk_realworld"/>This same idea is used when'
                ' timetables or duty rosters cycle through a fixed rotation.'
            )
        ) as tracker:

            self.wait_until_bookmark("bk_realworld")
            applic_card = make_concept_card(
                "Used in timetables and duty rosters"
                " that cycle through a fixed rotation.",
                position=ORIGIN, font_size=26
            )
            check_safe_margins(applic_card, "applic_card")
            self.play(FadeIn(applic_card), run_time=0.7)
            active_mobs.append(applic_card)

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
                '<bookmark mark="bk_question"/>A sequence of colours repeats'
                ' — yellow, blue, green, red — then repeats. '
                '<bookmark mark="bk_q54"/>What colour appears at'
                ' position fifty-four?'
            )
        ) as tracker:

            self.wait_until_bookmark("bk_question")

            q_text = Text(
                "What colour appears at position 54?",
                font="Poppins", font_size=26, color=PURPLE
            )
            q_text.move_to(UP * 2.5)
            check_safe_margins(q_text, "q_text")
            self.play(FadeIn(q_text), run_time=0.6)
            active_mobs.append(q_text)

            # Two full cycles of 4 colours = 8 boxes
            self.wait_until_bookmark("bk_q54")
            colour_row, colour_boxes = make_colour_row(
                n_cycles=2, font_size=15
            )
            colour_row.move_to(ORIGIN)
            check_safe_margins(colour_row, "colour_row")
            self.play(FadeIn(colour_row), run_time=0.8)
            active_mobs.append(colour_row)

            # "54th?" label below
            pos54_lbl = Text(
                "54th?", font="Poppins",
                font_size=28, color=ORANGE_HL
            )
            pos54_lbl.next_to(colour_row, DOWN, buff=0.35)
            check_safe_margins(pos54_lbl, "pos54_lbl")
            self.play(FadeIn(pos54_lbl), run_time=0.5)
            active_mobs.append(pos54_lbl)

        # Store refs for solution
        self._colour_row    = colour_row
        self._colour_boxes  = colour_boxes
        self._pos54_lbl     = pos54_lbl
        self._q_text        = q_text
        self._q_badge       = badge
        self._active_q      = list(active_mobs)

    # ── SOLUTION ──────────────────────────────────────────────────────────────

    def show_solution(self):
        # Stack height: 4 steps × (0.44+0.3) = 2.96 ✓
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

        # Shift colour row and label to right zone
        self.play(
            self._colour_row.animate.move_to(RIGHT * 3.0 + UP * 0.5),
            self._pos54_lbl.animate.move_to(RIGHT * 3.0 + DOWN * 0.8),
            self._q_text.animate.move_to(UP * 2.8),
            run_time=1.0
        )

        anchor = UP * 2.0 + LEFT * 3.5

        with self.voiceover(
            text=(
                '<bookmark mark="bk_s1"/>Cycle length is four. '
                '<bookmark mark="bk_s2"/>Divide fifty-four by four —'
                ' thirteen groups of four, with a remainder of two. '
                '<bookmark mark="bk_s3"/>Remainder two corresponds to the'
                ' second element — blue. '
                '<bookmark mark="bk_s4"/>The colour at position fifty-four'
                ' is blue.'
            )
        ) as tracker:

            mgr = StepManager(
                self, start_anchor=anchor,
                font_size=28, buff=0.3
            )

            # Step 1: cycle length = 4
            self.wait_until_bookmark("bk_s1")
            s1 = math_obj(r"\text{Cycle length} = 4", font_size=28)
            mgr.add_step(s1)
            active_mobs.append(s1)

            # Step 2: 54 ÷ 4 = 13 remainder 2
            self.wait_until_bookmark("bk_s2")
            s2 = math_obj(
                r"54 \div 4 = 13 \text{ remainder } 2",
                font_size=28
            )
            mgr.add_step(s2)
            active_mobs.append(s2)

            # Step 3: remainder 2 → Blue (2nd box in first cycle)
            self.wait_until_bookmark("bk_s3")
            # colour_boxes index 1 = Blue (first cycle, 2nd element)
            self.play(
                self._colour_boxes[1][0].animate.set_stroke(
                    color=ORANGE_HL, width=4.5
                ),
                run_time=0.5
            )
            s3 = math_obj(
                r"\text{rem } 2 \rightarrow \text{2nd} \rightarrow"
                r"\text{Blue}",
                font_size=28, color=ORANGE_HL
            )
            mgr.add_step(s3)
            active_mobs.append(s3)

            # Step 4: final answer
            self.wait_until_bookmark("bk_s4")
            s4 = math_obj(
                r"\text{Position 54} = \text{Blue}",
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
            "Divide the position number by the cycle length"
            " to find the remainder.",
            "The remainder identifies the element's position"
            " within the cycle.",
            "A remainder of zero means the element is"
            " the last in the cycle.",
        ]
        positions = [UP * 1.5, ORIGIN, DOWN * 1.5]

        with self.voiceover(
            text=(
                '<bookmark mark="bk_sum1"/>Divide the position number by'
                ' the cycle length to find the remainder. '
                '<bookmark mark="bk_sum2"/>The remainder identifies the'
                ' element\'s position within the cycle. '
                '<bookmark mark="bk_sum3"/>A remainder of zero means the'
                ' element is the last in the cycle.'
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