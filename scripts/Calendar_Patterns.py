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


# ── CALENDAR GRID HELPER ─────────────────────────────────────────

def make_calendar_grid(center_val=16, cell_w=0.82, cell_h=0.72,
                       highlight_center=True):
    """
    Draw a 3×3 section of a weekly calendar grid centered on center_val.
    Returns dict with VGroup 'grid' and individual cell refs.
    """
    rows, cols = 3, 3
    cells = {}
    group = VGroup()

    offsets = [(-7, -1), (-7, 0), (-7, 1),
               (0,  -1), (0,  0), (0,  1),
               (7,  -1), (7,  0), (7,  1)]

    for idx, (row_off, col_off) in enumerate(offsets):
        val  = center_val + row_off + col_off
        r    = idx // 3
        c    = idx  % 3
        x    = (c - 1) * cell_w
        y    = -(r - 1) * cell_h

        is_center = (row_off == 0 and col_off == 0)
        is_above  = (row_off == -7 and col_off == 0)
        is_below  = (row_off == 7  and col_off == 0)

        if is_center and highlight_center:
            fill_c   = ORANGE_HL
            fill_op  = 0.25
            stk_c    = ORANGE_HL
            txt_c    = ORANGE_HL
        elif is_above or is_below:
            fill_c   = PURPLE
            fill_op  = 0.10
            stk_c    = PURPLE
            txt_c    = PURPLE
        else:
            fill_c   = WHITE
            fill_op  = 0.0
            stk_c    = PALE_PURPLE
            txt_c    = PALE_PURPLE

        rect = RoundedRectangle(
            corner_radius=0.08,
            width=cell_w - 0.06,
            height=cell_h - 0.06,
            fill_color=fill_c,
            fill_opacity=fill_op,
            stroke_color=stk_c,
            stroke_width=1.8 if (is_center or is_above or is_below) else 1.0
        )
        rect.move_to(RIGHT * x + UP * y)

        num_txt = Text(str(val), font="Poppins",
                       font_size=22, color=txt_c)
        num_txt.move_to(rect.get_center())

        cell_grp = VGroup(rect, num_txt)
        group.add(cell_grp)

        if is_center: cells["center"] = cell_grp
        if is_above:  cells["above"]  = cell_grp
        if is_below:  cells["below"]  = cell_grp

    return {"grid": group, "cells": cells}


def make_calendar_lr(center_val=16, cell_w=0.82, cell_h=0.72):
    """
    Draw a 1×3 calendar row: left, center, right.
    """
    group = VGroup()
    cells = {}
    for idx, col_off in enumerate([-1, 0, 1]):
        val = center_val + col_off
        x   = (col_off) * cell_w

        is_center = (col_off == 0)
        is_side   = (col_off != 0)

        if is_center:
            fill_c  = ORANGE_HL
            fill_op = 0.25
            stk_c   = ORANGE_HL
            txt_c   = ORANGE_HL
        else:
            fill_c  = PURPLE
            fill_op = 0.10
            stk_c   = PURPLE
            txt_c   = PURPLE

        rect = RoundedRectangle(
            corner_radius=0.08,
            width=cell_w - 0.06, height=cell_h - 0.06,
            fill_color=fill_c, fill_opacity=fill_op,
            stroke_color=stk_c, stroke_width=1.8
        )
        rect.move_to(RIGHT * x)
        num_txt = Text(str(val), font="Poppins",
                       font_size=22, color=txt_c)
        num_txt.move_to(rect.get_center())
        cell_grp = VGroup(rect, num_txt)
        group.add(cell_grp)
        if col_off == 0:  cells["center"] = cell_grp
        if col_off == -1: cells["left"]   = cell_grp
        if col_off == 1:  cells["right"]  = cell_grp

    return {"grid": group, "cells": cells}


# ─────────────────────── SCENE ──────────────────────────────────

class CalendarPatternsScene(VoiceoverScene):

    def construct(self):
        self._setup_tts()
        self.show_title()
        self.show_hook()
        self.show_algebraic_positions()
        self.show_proof_above_below()
        self.show_power_statement()
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
                '<bookmark mark="bk_curious"/>Here is something curious — look at any '
                'number on a calendar. '
                'The numbers directly above and below it, — have a special relationship. '
                '<bookmark mark="bk_claim"/>The sum of those two numbers always equals '
                'twice the chosen number. '
                '<bookmark mark="bk_prove"/>But is this always true, for every single number? '
                'We cannot check every case. '
                'So instead, — we use letter-numbers to prove it for all cases at once.'
            )
        ) as tracker:

            self.wait_until_bookmark("bk_curious")

            # Show calendar grid centered on 16
            cal_data = make_calendar_grid(center_val=16)
            cal_grid = cal_data["grid"]
            cal_grid.scale(1.1)
            cal_grid.move_to(RIGHT * 3.2 + UP * 0.2)
            check_safe_margins(cal_grid, "cal_grid")
            self.play(FadeIn(cal_grid), run_time=0.9)
            active_mobs.append(cal_grid)

            # Arrow pointing to above cell
            above_cell = cal_data["cells"]["above"]
            below_cell = cal_data["cells"]["below"]
            center_cell = cal_data["cells"]["center"]

            arr_above = Arrow(
                start=above_cell.get_left() + LEFT * 0.05,
                end=above_cell.get_left() + LEFT * 0.7,
                color=ORANGE_HL, stroke_width=2.0,
                tip_length=0.16, buff=0.05
            )
            arr_below = Arrow(
                start=below_cell.get_left() + LEFT * 0.05,
                end=below_cell.get_left() + LEFT * 0.7,
                color=ORANGE_HL, stroke_width=2.0,
                tip_length=0.16, buff=0.05
            )
            self.play(Create(arr_above), Create(arr_below), run_time=0.6)
            active_mobs.extend([arr_above, arr_below])

            self.wait_until_bookmark("bk_claim")

            claim_card = make_concept_card(
                "Above + Below = 2 × chosen number",
                position=LEFT * 3.0 + UP * 1.0,
                font_size=26,
            )
            check_safe_margins(claim_card, "claim_card")
            self.play(FadeIn(claim_card), run_time=0.7)
            active_mobs.append(claim_card)

            # Numeric check: 9 + 23 = 32 = 2×16
            check_row = VGroup(
                math_obj(r"9", font_size=30, color=ORANGE_HL),
                math_obj(r"+", font_size=30),
                math_obj(r"23", font_size=30, color=ORANGE_HL),
                math_obj(r"=", font_size=30),
                math_obj(r"32", font_size=30, color=ORANGE_HL),
                math_obj(r"=", font_size=30),
                math_obj(r"2 \times 16", font_size=30),
            ).arrange(RIGHT, buff=0.10)
            check_row.move_to(LEFT * 3.0 + DOWN * 0.1)
            check_safe_margins(check_row, "check_row")
            check_y_gap(check_row, active_mobs, name="check_row")
            self.play(FadeIn(check_row), run_time=0.7)
            active_mobs.append(check_row)

            self.wait_until_bookmark("bk_prove")
            prove_card = make_concept_card(
                "Use letter-numbers to prove it for all cases at once.",
                position=LEFT * 3.0 + DOWN * 1.4,
                font_size=24,
            )
            check_safe_margins(prove_card, "prove_card")
            check_y_gap(prove_card, active_mobs, name="prove_card")
            self.play(FadeIn(prove_card), run_time=0.6)
            active_mobs.append(prove_card)

        self.wait(0.4)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── ALGEBRAIC POSITIONS ─────────────────────────────────────

    def show_algebraic_positions(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        with self.voiceover(
            text=(
                '<bookmark mark="bk_let_n"/>Let n represent any number on the calendar. '
                '<bookmark mark="bk_above"/>In a standard weekly calendar with seven days '
                'in each row, — moving up one row means the number is seven less. '
                'So the number directly above n is n minus seven. '
                '<bookmark mark="bk_below"/>The number directly below is n plus seven.'
            )
        ) as tracker:

            self.wait_until_bookmark("bk_let_n")

            # Algebraic calendar grid — center cell shows n
            # Build 3×3 grid with labels n-7, n, n+7
            cell_w, cell_h = 1.1, 0.85

            def make_alg_cell(label_tex, is_center=False, is_key=False):
                col = ORANGE_HL if is_center else (
                    PURPLE if is_key else PALE_PURPLE)
                fill_op = 0.20 if is_center else (
                    0.10 if is_key else 0.0)
                stk_w = 2.0 if (is_center or is_key) else 1.0
                rect = RoundedRectangle(
                    corner_radius=0.08,
                    width=cell_w - 0.08, height=cell_h - 0.08,
                    fill_color=col, fill_opacity=fill_op,
                    stroke_color=col if (is_center or is_key) else PALE_PURPLE,
                    stroke_width=stk_w
                )
                lbl = math_obj(label_tex, color=col, font_size=26)
                lbl.move_to(rect.get_center())
                return VGroup(rect, lbl)

            # Row labels for 3×3 grid positions
            grid_labels = [
                [r"n{-}8", r"n{-}7", r"n{-}6"],
                [r"n{-}1", r"n",      r"n{+}1"],
                [r"n{+}6", r"n{+}7", r"n{+}8"],
            ]
            key_positions = {(0, 1), (1, 1), (2, 1)}  # above, center, below

            grid_group = VGroup()
            cell_refs  = {}
            for r in range(3):
                for c in range(3):
                    is_ctr = (r == 1 and c == 1)
                    is_key = (r, c) in key_positions
                    cell = make_alg_cell(
                        grid_labels[r][c],
                        is_center=is_ctr,
                        is_key=is_key
                    )
                    cell.move_to(RIGHT * (c - 1) * cell_w
                                 + UP * (1 - r) * cell_h)
                    grid_group.add(cell)
                    cell_refs[(r, c)] = cell

            grid_group.move_to(RIGHT * 2.8 + UP * 0.1)
            check_safe_margins(grid_group, "grid_group")
            self.play(FadeIn(grid_group), run_time=0.9)
            active_mobs.append(grid_group)

            # n label annotation on left
            n_lbl = VGroup(
                Text("Any number:", font="Poppins",
                     font_size=24, color=PURPLE),
                math_obj(r"n", font_size=38, color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.2)
            n_lbl.move_to(LEFT * 3.5 + UP * 1.5)
            check_safe_margins(n_lbl, "n_lbl")
            self.play(FadeIn(n_lbl), run_time=0.6)
            active_mobs.append(n_lbl)

            self.wait_until_bookmark("bk_above")

            above_lbl = VGroup(
                Text("Above:", font="Poppins",
                     font_size=24, color=PURPLE),
                math_obj(r"n - 7", font_size=34, color=PURPLE),
            ).arrange(RIGHT, buff=0.2)
            above_lbl.move_to(LEFT * 3.5 + UP * 0.5)
            check_safe_margins(above_lbl, "above_lbl")
            check_y_gap(above_lbl, active_mobs, name="above_lbl")
            self.play(FadeIn(above_lbl), run_time=0.6)
            active_mobs.append(above_lbl)

            # Highlight above cell
            above_cell = cell_refs[(0, 1)]
            self.play(
                above_cell.animate.set_color(ORANGE_HL),
                run_time=0.4
            )

            self.wait_until_bookmark("bk_below")

            below_lbl = VGroup(
                Text("Below:", font="Poppins",
                     font_size=24, color=PURPLE),
                math_obj(r"n + 7", font_size=34, color=PURPLE),
            ).arrange(RIGHT, buff=0.2)
            below_lbl.move_to(LEFT * 3.5 + DOWN * 0.5)
            check_safe_margins(below_lbl, "below_lbl")
            check_y_gap(below_lbl, active_mobs, name="below_lbl")
            self.play(FadeIn(below_lbl), run_time=0.6)
            active_mobs.append(below_lbl)

            below_cell = cell_refs[(2, 1)]
            self.play(
                below_cell.animate.set_color(ORANGE_HL),
                run_time=0.4
            )

        self.wait(0.4)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── PROOF: ABOVE + BELOW ────────────────────────────────────

    def show_proof_above_below(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        with self.voiceover(
            text=(
                '<bookmark mark="bk_sum_setup"/>The sum of these two is — '
                'the quantity n minus seven, plus the quantity n plus seven. '
                '<bookmark mark="bk_expand"/>Opening the brackets — '
                'n minus seven plus n plus seven. '
                '<bookmark mark="bk_cancel"/>The minus seven and plus seven cancel. '
                '<bookmark mark="bk_result"/>The result is two n — '
                'exactly twice the chosen number.'
            )
        ) as tracker:

            self.wait_until_bookmark("bk_sum_setup")

            # Step: raw sum
            sum_lbl = Text("Sum:", font="Poppins",
                           font_size=26, color=PURPLE)
            sum_lbl.move_to(UP * 2.1 + LEFT * 4.5)
            check_safe_margins(sum_lbl, "sum_lbl")
            self.play(FadeIn(sum_lbl), run_time=0.4)
            active_mobs.append(sum_lbl)

            # Pattern F: (n-7) + (n+7)
            t_open1  = math_obj(r"(", font_size=42)
            t_n1     = math_obj(r"n", font_size=42)
            t_m7     = math_obj(r"-", font_size=42, color=ORANGE_HL)
            t_7a     = math_obj(r"7", font_size=42, color=ORANGE_HL)
            t_close1 = math_obj(r")", font_size=42)
            t_plus   = math_obj(r"+", font_size=42)
            t_open2  = math_obj(r"(", font_size=42)
            t_n2     = math_obj(r"n", font_size=42)
            t_p7     = math_obj(r"+", font_size=42, color=ORANGE_HL)
            t_7b     = math_obj(r"7", font_size=42, color=ORANGE_HL)
            t_close2 = math_obj(r")", font_size=42)

            raw_sum = VGroup(
                t_open1, t_n1, t_m7, t_7a, t_close1,
                t_plus,
                t_open2, t_n2, t_p7, t_7b, t_close2
            ).arrange(RIGHT, buff=0.10)
            raw_sum.move_to(UP * 1.3)
            check_safe_margins(raw_sum, "raw_sum")
            self.play(FadeIn(raw_sum), run_time=0.8)
            active_mobs.append(raw_sum)

            self.wait_until_bookmark("bk_expand")

            # Expanded form
            exp_row = VGroup(
                math_obj(r"=", font_size=40),
                math_obj(r"n", font_size=40),
                math_obj(r"-", font_size=40, color=ORANGE_HL),
                math_obj(r"7", font_size=40, color=ORANGE_HL),
                math_obj(r"+", font_size=40),
                math_obj(r"n", font_size=40),
                math_obj(r"+", font_size=40, color=ORANGE_HL),
                math_obj(r"7", font_size=40, color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.12)
            exp_row.next_to(raw_sum, DOWN, buff=0.45)
            check_safe_margins(exp_row, "exp_row")
            check_y_gap(exp_row, active_mobs, name="exp_row")
            self.play(FadeIn(exp_row), run_time=0.7)
            active_mobs.append(exp_row)

            self.wait_until_bookmark("bk_cancel")

            # Strike through the ±7 terms to show cancellation
            cancel_line1 = Line(
                exp_row[2].get_left() + LEFT * 0.05,
                exp_row[3].get_right() + RIGHT * 0.05,
                color=RED, stroke_width=2.5
            )
            cancel_line2 = Line(
                exp_row[6].get_left() + LEFT * 0.05,
                exp_row[7].get_right() + RIGHT * 0.05,
                color=RED, stroke_width=2.5
            )
            self.play(
                Create(cancel_line1), Create(cancel_line2),
                run_time=0.6
            )
            active_mobs.extend([cancel_line1, cancel_line2])

            cancel_card = make_concept_card(
                "-7 and +7 cancel each other out.",
                position=DOWN * 0.2,
                font_size=24,
            )
            check_safe_margins(cancel_card, "cancel_card")
            check_y_gap(cancel_card, active_mobs, name="cancel_card")
            self.play(FadeIn(cancel_card), run_time=0.5)
            active_mobs.append(cancel_card)

            self.wait_until_bookmark("bk_result")

            result_row = VGroup(
                math_obj(r"=", font_size=46),
                math_obj(r"2n", font_size=46, color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.14)
            result_row.next_to(cancel_card, DOWN, buff=0.45)
            check_safe_margins(result_row, "result_row")
            check_y_gap(result_row, active_mobs, name="result_row")
            self.play(FadeIn(result_row), run_time=0.8)
            active_mobs.append(result_row)

            ans_box = SurroundingRectangle(
                result_row, color=ORANGE_HL,
                corner_radius=0.15,
                stroke_width=2.5,
                buff=0.15
            )
            self.play(Create(ans_box), run_time=0.5)
            active_mobs.append(ans_box)

        self.wait(0.4)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── POWER STATEMENT ─────────────────────────────────────────

    def show_power_statement(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        with self.voiceover(
            text=(
                '<bookmark mark="bk_power"/>Because we used n to stand for any number, '
                'this proof holds for every valid position on the calendar. '
                '<bookmark mark="bk_algebraic"/>That is the power of expressing '
                'a relationship algebraically.'
            )
        ) as tracker:

            self.wait_until_bookmark("bk_power")

            power_card = make_concept_card(
                "n stands for ANY number — so the proof holds for every valid position.",
                position=UP * 0.8,
                font_size=26,
            )
            check_safe_margins(power_card, "power_card")
            self.play(FadeIn(power_card), run_time=0.7)
            active_mobs.append(power_card)

            # Show the proved result centred
            proved = VGroup(
                math_obj(r"(n-7)", font_size=36, color=PURPLE),
                math_obj(r"+", font_size=36),
                math_obj(r"(n+7)", font_size=36, color=PURPLE),
                math_obj(r"=", font_size=36),
                math_obj(r"2n", font_size=36, color=ORANGE_HL),
                Text("  for all n", font="Poppins",
                     font_size=24, color=PALE_PURPLE),
            ).arrange(RIGHT, buff=0.14)
            proved.move_to(DOWN * 0.4)
            check_safe_margins(proved, "proved")
            check_y_gap(proved, active_mobs, name="proved")
            self.play(FadeIn(proved), run_time=0.8)
            active_mobs.append(proved)

            self.wait_until_bookmark("bk_algebraic")

            alg_card = make_concept_card(
                "That is the power of expressing a relationship algebraically.",
                position=DOWN * 1.8,
                font_size=24,
            )
            check_safe_margins(alg_card, "alg_card")
            check_y_gap(alg_card, active_mobs, name="alg_card")
            self.play(FadeIn(alg_card), run_time=0.6)
            active_mobs.append(alg_card)

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
                '<bookmark mark="bk_q"/>For any number n on the calendar, '
                'show algebraically that the sum of the numbers immediately '
                'to its left and right equals two n.'
            )
        ) as tracker:

            self.wait_until_bookmark("bk_q")

            q_lbl = Text(
                "Show algebraically:",
                font="Poppins", font_size=26, color=PURPLE
            )
            q_lbl.move_to(UP * 2.1)
            check_safe_margins(q_lbl, "q_lbl")
            self.play(FadeIn(q_lbl), run_time=0.5)
            active_mobs.append(q_lbl)

            q_stmt = make_concept_card(
                "Left + Right = 2n for any calendar number n.",
                position=UP * 1.1,
                font_size=26,
            )
            check_safe_margins(q_stmt, "q_stmt")
            check_y_gap(q_stmt, active_mobs, name="q_stmt")
            self.play(FadeIn(q_stmt), run_time=0.7)
            active_mobs.append(q_stmt)

            # Show 1×3 calendar row with n centered
            lr_data = make_calendar_lr(center_val=16)
            lr_grid = lr_data["grid"]
            lr_grid.scale(1.2)
            lr_grid.move_to(DOWN * 0.2)
            check_safe_margins(lr_grid, "lr_grid")
            self.play(FadeIn(lr_grid), run_time=0.7)
            active_mobs.append(lr_grid)

            # Algebraic labels below cells
            left_cell  = lr_data["cells"]["left"]
            right_cell = lr_data["cells"]["right"]
            center_cell = lr_data["cells"]["center"]

            lbl_left = math_obj(r"n-1", font_size=26, color=PURPLE)
            lbl_ctr  = math_obj(r"n",   font_size=26, color=ORANGE_HL)
            lbl_rgt  = math_obj(r"n+1", font_size=26, color=PURPLE)

            lbl_left.next_to(left_cell,   DOWN, buff=0.2)
            lbl_ctr.next_to(center_cell,  DOWN, buff=0.2)
            lbl_rgt.next_to(right_cell,   DOWN, buff=0.2)
            check_safe_margins(lbl_left, "lbl_left")
            check_safe_margins(lbl_ctr,  "lbl_ctr")
            check_safe_margins(lbl_rgt,  "lbl_rgt")

            self.play(
                FadeIn(lbl_left), FadeIn(lbl_ctr), FadeIn(lbl_rgt),
                run_time=0.6
            )
            active_mobs.extend([lbl_left, lbl_ctr, lbl_rgt])

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
                '<bookmark mark="bk_s1"/>The number to the left is n minus one. '
                'The number to the right is n plus one. '
                '<bookmark mark="bk_s2"/>Sum equals n minus one plus n plus one. '
                '<bookmark mark="bk_s3"/>Rearranging — two n plus the quantity '
                'minus one plus one. '
                '<bookmark mark="bk_s4"/>Minus one plus one equals zero. '
                '<bookmark mark="bk_s5"/>Sum equals two n. Proved.'
            )
        ) as tracker:

            mgr = StepManager(
                self,
                start_anchor=UP * 2.0 + LEFT * 0.5,
                font_size=28,
                buff=0.38
            )

            # Step 1: define left and right
            self.wait_until_bookmark("bk_s1")
            s1 = VGroup(
                Text("Left:", font="Poppins", font_size=26, color=PURPLE),
                math_obj(r"n-1", font_size=30, color=ORANGE_HL),
                Text("  Right:", font="Poppins",
                     font_size=26, color=PURPLE),
                math_obj(r"n+1", font_size=30, color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.18)
            mgr.add_step(s1)
            active_mobs.append(s1)

            # Step 2: write sum
            self.wait_until_bookmark("bk_s2")
            s2 = VGroup(
                Text("Sum =", font="Poppins", font_size=26, color=PURPLE),
                math_obj(r"(n-1)", font_size=30),
                math_obj(r"+", font_size=30),
                math_obj(r"(n+1)", font_size=30),
            ).arrange(RIGHT, buff=0.16)
            mgr.add_step(s2)
            active_mobs.append(s2)

            # Step 3: rearrange
            self.wait_until_bookmark("bk_s3")
            s3 = VGroup(
                math_obj(r"=", font_size=30),
                math_obj(r"2n", font_size=30, color=ORANGE_HL),
                math_obj(r"+", font_size=30),
                math_obj(r"(-1+1)", font_size=30, color=PALE_PURPLE),
            ).arrange(RIGHT, buff=0.16)
            mgr.add_step(s3)
            active_mobs.append(s3)

            # Step 4: -1+1=0
            self.wait_until_bookmark("bk_s4")
            s4 = VGroup(
                math_obj(r"=", font_size=30),
                math_obj(r"2n", font_size=30, color=ORANGE_HL),
                math_obj(r"+", font_size=30),
                math_obj(r"0", font_size=30, color=PALE_PURPLE),
            ).arrange(RIGHT, buff=0.16)
            mgr.add_step(s4)
            active_mobs.append(s4)

            # Step 5: final proved
            self.wait_until_bookmark("bk_s5")
            s5 = VGroup(
                math_obj(r"=", font_size=36),
                math_obj(r"2n", font_size=36, color=ORANGE_HL),
                MathTex(r"\checkmark",
                        tex_template=TexFontTemplates.gnu_freesans_tx,
                        font_size=38, color=ORANGE_HL),
                Text("Proved", font="Poppins",
                     font_size=28, color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.18)
            mgr.add_step(s5)
            active_mobs.append(s5)

            ans_box = SurroundingRectangle(
                s5, color=ORANGE_HL,
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
            "Use a letter-number to represent any position in a calendar arrangement.",
            "Express surrounding positions in terms of that letter-number.",
            "Algebraic simplification proves the relationship holds for all valid positions.",
        ]
        positions = [UP * 1.5, ORIGIN, DOWN * 1.5]

        with self.voiceover(
            text=(
                '<bookmark mark="bk_sum1"/>Use a letter-number to represent any position '
                'in a calendar arrangement. '
                '<bookmark mark="bk_sum2"/>Express surrounding positions in terms of '
                'that letter-number. '
                '<bookmark mark="bk_sum3"/>Algebraic simplification proves the relationship '
                'holds for all valid positions.'
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