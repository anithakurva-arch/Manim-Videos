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
Slow down on variables and formulas. Emphasize pattern findings and rules.

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


# ── TABLE HELPER ──────────────────────────────────────────────────────────────

def make_io_table(rows, col_w=1.2, row_h=0.6,
                  header=True, font_size=28):
    """
    rows: list of (input_str, output_str) tuples.
    Returns VGroup of Rectangle cells + Text labels.
    Exposes .input_cells, .output_cells, .rows_group per row.
    """
    all_cells  = VGroup()
    in_cells   = []
    out_cells  = []
    row_groups = []

    # Header row
    if header:
        h_in_bg = Rectangle(
            width=col_w, height=row_h,
            fill_color=PURPLE, fill_opacity=1,
            stroke_color=PURPLE, stroke_width=2
        )
        h_in_lbl = Text(
            "Input", font="Poppins",
            font_size=font_size - 4, color=WHITE
        )
        h_in_lbl.move_to(h_in_bg.get_center())
        h_in = VGroup(h_in_bg, h_in_lbl)

        h_out_bg = Rectangle(
            width=col_w, height=row_h,
            fill_color=PURPLE, fill_opacity=1,
            stroke_color=PURPLE, stroke_width=2
        )
        h_out_lbl = Text(
            "Output", font="Poppins",
            font_size=font_size - 4, color=WHITE
        )
        h_out_lbl.move_to(h_out_bg.get_center())
        h_out = VGroup(h_out_bg, h_out_lbl)

        header_row = VGroup(h_in, h_out).arrange(RIGHT, buff=0)
        all_cells.add(header_row)

    # Data rows
    data_row_groups = []
    for (in_s, out_s) in rows:
        in_bg = Rectangle(
            width=col_w, height=row_h,
            fill_color=WHITE, fill_opacity=0.9,
            stroke_color=PURPLE, stroke_width=2
        )
        in_lbl = Text(
            in_s, font="Poppins",
            font_size=font_size, color=PURPLE
        )
        in_lbl.move_to(in_bg.get_center())
        in_cell = VGroup(in_bg, in_lbl)

        out_bg = Rectangle(
            width=col_w, height=row_h,
            fill_color=WHITE, fill_opacity=0.9,
            stroke_color=PURPLE, stroke_width=2
        )
        out_lbl = Text(
            out_s, font="Poppins",
            font_size=font_size, color=PURPLE
        )
        out_lbl.move_to(out_bg.get_center())
        out_cell = VGroup(out_bg, out_lbl)

        data_row = VGroup(in_cell, out_cell).arrange(RIGHT, buff=0)
        data_row_groups.append(data_row)
        in_cells.append(in_cell)
        out_cells.append(out_cell)

    # Stack header + data rows
    if header and len(all_cells) > 0:
        all_stacked = VGroup(all_cells[0],
                             *data_row_groups).arrange(DOWN, buff=0)
    else:
        all_stacked = VGroup(*data_row_groups).arrange(DOWN, buff=0)

    all_stacked.input_cells  = in_cells
    all_stacked.output_cells = out_cells
    all_stacked.data_rows    = data_row_groups
    return all_stacked


# ── MAIN SCENE ────────────────────────────────────────────────────────────────

class InputOutputScene(VoiceoverScene):

    def construct(self):
        self._setup_tts()
        self.show_title()
        self.show_concept_hook()
        self.show_concept_analyse()
        self.show_concept_verify()
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

    # ── CONCEPT 1: INPUT–OUTPUT HOOK ─────────────────────────────────────────

    def show_concept_hook(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        # Build table shell (header only first)
        table_shell = make_io_table([], header=True,
                                    col_w=1.4, row_h=0.6, font_size=26)
        table_shell.move_to(LEFT * 1.5 + UP * 0.3)
        check_safe_margins(table_shell, "table_shell")

        # Pre-build data rows (hidden, revealed one by one)
        row_data = [("1", "5"), ("2", "8"), ("3", "11")]
        data_rows_built = []
        for in_s, out_s in row_data:
            in_bg = Rectangle(
                width=1.4, height=0.6,
                fill_color=WHITE, fill_opacity=0.9,
                stroke_color=PURPLE, stroke_width=2
            )
            in_lbl = Text(in_s, font="Poppins",
                          font_size=26, color=PURPLE)
            in_lbl.move_to(in_bg.get_center())
            in_cell = VGroup(in_bg, in_lbl)

            out_bg = Rectangle(
                width=1.4, height=0.6,
                fill_color=WHITE, fill_opacity=0.9,
                stroke_color=PURPLE, stroke_width=2
            )
            out_lbl = Text(out_s, font="Poppins",
                           font_size=26, color=PURPLE)
            out_lbl.move_to(out_bg.get_center())
            out_cell = VGroup(out_bg, out_lbl)

            dr = VGroup(in_cell, out_cell).arrange(RIGHT, buff=0)
            data_rows_built.append(dr)

        # Position rows below header
        for i, dr in enumerate(data_rows_built):
            dr.next_to(table_shell if i == 0
                       else data_rows_built[i - 1],
                       DOWN, buff=0)
            check_safe_margins(dr, f"data_row_{i}")

        with self.voiceover(
            text=(
                '<bookmark mark="bk_machine"/>Imagine a machine that takes'
                ' a number, performs some operations on it, and gives you'
                ' a result. '
                '<bookmark mark="bk_row1"/>You put in one, and get five. '
                '<bookmark mark="bk_row2"/>You put in two, and get eight. '
                '<bookmark mark="bk_row3"/>You put in three, and get eleven. '
                '<bookmark mark="bk_what"/>What is the machine doing? '
                '<bookmark mark="bk_pattern"/>This is an input-output'
                ' pattern — and algebra helps us find the rule.'
            )
        ) as tracker:

            # Show table header
            self.wait_until_bookmark("bk_machine")
            self.play(FadeIn(table_shell), run_time=0.7)
            active_mobs.append(table_shell)

            # Add rows one by one
            self.wait_until_bookmark("bk_row1")
            self.play(FadeIn(data_rows_built[0]), run_time=0.6)
            active_mobs.append(data_rows_built[0])

            self.wait_until_bookmark("bk_row2")
            self.play(FadeIn(data_rows_built[1]), run_time=0.6)
            active_mobs.append(data_rows_built[1])

            self.wait_until_bookmark("bk_row3")
            self.play(FadeIn(data_rows_built[2]), run_time=0.6)
            active_mobs.append(data_rows_built[2])

            # "?" appears
            self.wait_until_bookmark("bk_what")
            q_mark = Text("?", font="Poppins",
                          font_size=48, color=ORANGE_HL)
            q_mark.next_to(data_rows_built[2], DOWN, buff=0.35)
            check_safe_margins(q_mark, "q_mark")
            self.play(FadeIn(q_mark), run_time=0.5)
            active_mobs.append(q_mark)

            # Pattern label card
            self.wait_until_bookmark("bk_pattern")
            pattern_card = make_concept_card(
                "Input-output pattern: algebra finds the rule",
                position=RIGHT * 2.8 + UP * 0.2,
                font_size=22
            )
            check_safe_margins(pattern_card, "pattern_card")
            self.play(FadeIn(pattern_card), run_time=0.7)
            active_mobs.append(pattern_card)

        # Store table for next segment
        self._hook_table_parts = (
            table_shell, data_rows_built
        )

        self.wait(0.4)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── CONCEPT 2: ANALYSING THE PATTERN ─────────────────────────────────────

    def show_concept_analyse(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        # Rebuild the same table (rows 1–3)
        table_shell = make_io_table([], header=True,
                                    col_w=1.4, row_h=0.6, font_size=26)
        row_data = [("1", "5"), ("2", "8"), ("3", "11")]
        data_rows = []
        for i, (in_s, out_s) in enumerate(row_data):
            in_bg = Rectangle(width=1.4, height=0.6,
                              fill_color=WHITE, fill_opacity=0.9,
                              stroke_color=PURPLE, stroke_width=2)
            in_lbl = Text(in_s, font="Poppins",
                          font_size=26, color=PURPLE)
            in_lbl.move_to(in_bg.get_center())
            out_bg = Rectangle(width=1.4, height=0.6,
                               fill_color=WHITE, fill_opacity=0.9,
                               stroke_color=PURPLE, stroke_width=2)
            out_lbl = Text(out_s, font="Poppins",
                           font_size=26, color=PURPLE)
            out_lbl.move_to(out_bg.get_center())
            dr = VGroup(
                VGroup(in_bg, in_lbl),
                VGroup(out_bg, out_lbl)
            ).arrange(RIGHT, buff=0)
            data_rows.append(dr)

        full_table = VGroup(table_shell, *data_rows).arrange(DOWN, buff=0)
        full_table.move_to(LEFT * 2.2 + UP * 0.2)
        check_safe_margins(full_table, "full_table")

        # Reference to output cells for arrow placement
        # output cell centers (right column)
        # Each data row: dr[1] is the output cell VGroup
        out_centers = [dr[1].get_center() for dr in data_rows]

        with self.voiceover(
            text=(
                '<bookmark mark="bk_analyse"/>To analyse an input-output'
                ' pattern, look at how the output changes as the input'
                ' increases. '
                '<bookmark mark="bk_up_three"/>Here, every time the input'
                ' goes up by one, the output goes up by three. '
                '<bookmark mark="bk_mult_three"/>So the rule involves'
                ' multiplying the input by three. '
                '<bookmark mark="bk_not_five"/>But three times one is three,'
                ' not five — so we are adding two more each time. '
                '<bookmark mark="bk_words"/>Always describe the rule in'
                ' words first — output equals three times input plus two. '
                '<bookmark mark="bk_algebra"/>Then write it as an algebraic'
                ' expression — if n is the input, the output is'
                ' three n plus two.'
            )
        ) as tracker:

            # Show full table
            self.wait_until_bookmark("bk_analyse")
            self.play(FadeIn(full_table), run_time=0.8)
            active_mobs.append(full_table)

            # Pattern B: difference arrows between output rows
            self.wait_until_bookmark("bk_up_three")

            arrow_color = ORANGE_HL
            diff_arrows = VGroup()
            plus3_labels = VGroup()

            # Output column right edge x position
            out_right_x = data_rows[0][1].get_right()[0] + 0.35

            for i in range(len(data_rows) - 1):
                top_y    = out_centers[i][1]
                bot_y    = out_centers[i + 1][1]
                arr = Arrow(
                    start=np.array([out_right_x, top_y + 0.05, 0]),
                    end=np.array([out_right_x, bot_y - 0.05, 0]),
                    color=arrow_color, stroke_width=2.5,
                    tip_length=0.18, buff=0
                )
                lbl = Text("+3", font="Poppins",
                           font_size=22, color=ORANGE_HL)
                lbl.next_to(arr, RIGHT, buff=0.12)
                diff_arrows.add(arr)
                plus3_labels.add(lbl)

            check_safe_margins(diff_arrows,   "diff_arrows")
            check_safe_margins(plus3_labels,  "plus3_labels")
            self.play(
                *[FadeIn(a) for a in diff_arrows],
                *[FadeIn(l) for l in plus3_labels],
                run_time=0.8
            )
            active_mobs.append(diff_arrows)
            active_mobs.append(plus3_labels)

            # Show "3 × n" trial
            self.wait_until_bookmark("bk_mult_three")
            trial_n   = math_obj(r"3 \times n", font_size=36)
            trial_n.move_to(RIGHT * 3.0 + UP * 1.2)
            check_safe_margins(trial_n, "trial_n")
            self.play(FadeIn(trial_n), run_time=0.7)
            active_mobs.append(trial_n)

            # Pattern F: show gap — 3×1=3, not 5, so +2
            self.wait_until_bookmark("bk_not_five")

            # Split expression: "3", "×", "1", "=", "3"
            g_3a  = math_obj(r"3", font_size=32)
            g_mul = math_obj(r"\times", font_size=32)
            g_1   = math_obj(r"1", font_size=32)
            g_eq  = math_obj(r"=", font_size=32)
            g_3b  = math_obj(r"3", font_size=32)
            g_neq = math_obj(r"\neq 5", font_size=32, color=RED)
            gap_row = VGroup(
                g_3a, g_mul, g_1, g_eq, g_3b, g_neq
            ).arrange(RIGHT, buff=0.12)
            gap_row.move_to(RIGHT * 3.0 + UP * 0.3)
            check_safe_margins(gap_row, "gap_row")

            plus2_lbl = math_obj(r"+2", font_size=36, color=ORANGE_HL)
            plus2_lbl.next_to(gap_row, DOWN, buff=0.25)
            check_safe_margins(plus2_lbl, "plus2_lbl")

            self.play(FadeIn(gap_row), run_time=0.7)
            active_mobs.append(gap_row)
            self.play(
                g_neq.animate.set_color(RED),
                run_time=0.3
            )
            self.play(FadeIn(plus2_lbl), run_time=0.5)
            active_mobs.append(plus2_lbl)

            # Word rule card
            self.wait_until_bookmark("bk_words")
            word_rule = make_concept_card(
                "output = 3 x input + 2",
                position=RIGHT * 3.0 + DOWN * 0.7,
                font_size=24
            )
            check_safe_margins(word_rule, "word_rule")
            self.play(FadeIn(word_rule), run_time=0.7)
            active_mobs.append(word_rule)

            # Algebraic rule — ReplacementTransform word_rule → alg form
            self.wait_until_bookmark("bk_algebra")
            alg_rule = math_obj(r"3n + 2", font_size=40, color=ORANGE_HL)
            alg_rule.move_to(word_rule.get_center())
            check_safe_margins(alg_rule, "alg_rule")
            self.play(
                ReplacementTransform(word_rule, alg_rule),
                run_time=0.9
            )
            active_mobs.remove(word_rule)
            active_mobs.append(alg_rule)

        self.wait(0.5)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── CONCEPT 3: VERIFICATION ───────────────────────────────────────────────

    def show_concept_verify(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        # Positions for three verification rows
        v_positions = [UP * 1.0, ORIGIN, DOWN * 1.0]

        # Pre-build verification expressions as split MathTex rows
        # Each: "n=k: 3(k)+2 = ?+2 = result ✓"
        verify_cases = [
            (r"n=1:", r"3(1)+2", r"= 3+2 =", r"5",  "5"),
            (r"n=2:", r"3(2)+2", r"= 6+2 =", r"8",  "8"),
            (r"n=3:", r"3(3)+2", r"= 9+2 =", r"11", "11"),
        ]

        with self.voiceover(
            text=(
                '<bookmark mark="bk_verify_intro"/>Verifying the rule across'
                ' multiple cases is an essential step — it confirms the rule'
                ' holds, and is not a coincidence for one case. '
                '<bookmark mark="bk_v1"/>Test n equals one —'
                ' three plus two equals five. '
                '<bookmark mark="bk_v2"/>Test n equals two —'
                ' six plus two equals eight. '
                '<bookmark mark="bk_v3"/>Test n equals three —'
                ' nine plus two equals eleven. '
                '<bookmark mark="bk_holds"/>The rule holds.'
            )
        ) as tracker:

            # Verify intro card
            self.wait_until_bookmark("bk_verify_intro")
            v_card = make_concept_card(
                "Verify the rule across multiple cases",
                position=UP * 2.2,
                font_size=24
            )
            check_safe_margins(v_card, "v_card")
            self.play(FadeIn(v_card), run_time=0.7)
            active_mobs.append(v_card)

            bk_marks = ["bk_v1", "bk_v2", "bk_v3"]
            v_rows_mobs = []

            for i, (lbl, expr, mid, res, _) in enumerate(verify_cases):
                self.wait_until_bookmark(bk_marks[i])

                # Build as separate math objects (Pattern F)
                v_lbl  = math_obj(lbl,  font_size=30, color=PURPLE)
                v_expr = math_obj(expr, font_size=30, color=PURPLE)
                v_mid  = math_obj(mid,  font_size=30, color=PURPLE)
                v_res  = math_obj(res,  font_size=30, color=GREEN_OK)
                v_chk  = math_obj(r"\checkmark", font_size=30,
                                  color=GREEN_OK)

                v_row = VGroup(
                    v_lbl, v_expr, v_mid, v_res, v_chk
                ).arrange(RIGHT, buff=0.18)
                v_row.move_to(v_positions[i])
                check_safe_margins(v_row, f"v_row_{i}")

                self.play(FadeIn(v_row), run_time=0.7)
                active_mobs.append(v_row)
                v_rows_mobs.append(v_row)

            # Pattern E: echo — rule confirmed
            self.wait_until_bookmark("bk_holds")
            rule_echo = math_obj(r"3n + 2 \;\; \checkmark",
                                 font_size=40, color=ORANGE_HL)
            rule_echo.move_to(DOWN * 2.2)
            check_safe_margins(rule_echo, "rule_echo")
            self.play(FadeIn(rule_echo), run_time=0.7)
            active_mobs.append(rule_echo)

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
                '<bookmark mark="bk_question"/>An input-output table shows —'
                ' input one gives four, input two gives seven,'
                ' input three gives ten. '
                '<bookmark mark="bk_formulate"/>Formulate the rule and'
                ' verify it for input four.'
            )
        ) as tracker:

            self.wait_until_bookmark("bk_question")

            q_text = Text(
                "Formulate the rule and verify for input 4:",
                font="Poppins", font_size=26, color=PURPLE
            )
            q_text.move_to(UP * 2.8)
            check_safe_margins(q_text, "q_text")
            self.play(FadeIn(q_text), run_time=0.6)
            active_mobs.append(q_text)

            # Build question table rows 1–3
            q_row_data = [("1", "4"), ("2", "7"), ("3", "10")]
            q_shell    = make_io_table([], header=True,
                                       col_w=1.4, row_h=0.6, font_size=26)
            q_data_rows = []
            for in_s, out_s in q_row_data:
                in_bg = Rectangle(width=1.4, height=0.6,
                                  fill_color=WHITE, fill_opacity=0.9,
                                  stroke_color=PURPLE, stroke_width=2)
                in_lbl = Text(in_s, font="Poppins",
                              font_size=26, color=PURPLE)
                in_lbl.move_to(in_bg.get_center())
                out_bg = Rectangle(width=1.4, height=0.6,
                                   fill_color=WHITE, fill_opacity=0.9,
                                   stroke_color=PURPLE, stroke_width=2)
                out_lbl = Text(out_s, font="Poppins",
                               font_size=26, color=PURPLE)
                out_lbl.move_to(out_bg.get_center())
                dr = VGroup(
                    VGroup(in_bg, in_lbl),
                    VGroup(out_bg, out_lbl)
                ).arrange(RIGHT, buff=0)
                q_data_rows.append(dr)

            q_full = VGroup(q_shell, *q_data_rows).arrange(DOWN, buff=0)
            q_full.move_to(ORIGIN)
            check_safe_margins(q_full, "q_full")

            self.play(FadeIn(q_full), run_time=0.8)
            active_mobs.append(q_full)

            # Row 4: "4 | ?" in ORANGE_HL
            self.wait_until_bookmark("bk_formulate")

            in4_bg = Rectangle(width=1.4, height=0.6,
                               fill_color=ORANGE_HL, fill_opacity=0.25,
                               stroke_color=ORANGE_HL, stroke_width=2.5)
            in4_lbl = Text("4", font="Poppins",
                           font_size=26, color=ORANGE_HL)
            in4_lbl.move_to(in4_bg.get_center())
            out4_bg = Rectangle(width=1.4, height=0.6,
                                fill_color=ORANGE_HL, fill_opacity=0.25,
                                stroke_color=ORANGE_HL, stroke_width=2.5)
            out4_lbl = Text("?", font="Poppins",
                            font_size=26, color=ORANGE_HL)
            out4_lbl.move_to(out4_bg.get_center())
            row4 = VGroup(
                VGroup(in4_bg, in4_lbl),
                VGroup(out4_bg, out4_lbl)
            ).arrange(RIGHT, buff=0)
            row4.next_to(q_full, DOWN, buff=0)
            check_safe_margins(row4, "row4")

            self.play(FadeIn(row4), run_time=0.6)
            active_mobs.append(row4)

        self._q_full     = q_full
        self._q_row4     = row4
        self._q_text     = q_text
        self._q_badge    = badge
        self._active_q   = list(active_mobs)

    # ── SOLUTION ──────────────────────────────────────────────────────────────

    def show_solution(self):
        # STACK HEIGHT PRE-COMPUTATION:
        # Phase 1: 4 steps (s1–s4), font_size=24, buff=0.25
        #   height ≈ 4 × (0.33 + 0.25) = 2.32 units ✓
        # Phase 2: 4 steps (s5–s8), font_size=24, buff=0.25
        #   height ≈ 4 × (0.33 + 0.25) = 2.32 units ✓
        # LIMITS[(24,0.25)] = 5 → 4 per phase ✓

        active_mobs = list(self._active_q)

        # Swap badge
        sol_badge = create_heading_badge("Solution")
        self.play(
            FadeOut(self._q_badge),
            FadeIn(sol_badge),
            run_time=0.5
        )
        active_mobs[0] = sol_badge

        # Shift table group to right zone
        table_group = VGroup(self._q_full, self._q_row4)
        self.play(
            table_group.animate.move_to(RIGHT * 3.2 + UP * 0.3),
            self._q_text.animate.move_to(UP * 2.8),
            run_time=1.0
        )

        anchor = UP * 2.2 + LEFT * 3.5

        with self.voiceover(
            text=(
                '<bookmark mark="bk_s1"/>Output increases by three —'
                ' rule involves three n. '
                '<bookmark mark="bk_s2"/>Three times one gives three,'
                ' but the output is four. '
                '<bookmark mark="bk_s3"/>So add one. '
                '<bookmark mark="bk_s4"/>Rule is three n plus one. '
                '<bookmark mark="bk_s5"/>Verify — three times two plus'
                ' one equals seven. '
                '<bookmark mark="bk_s6"/>Three times three plus one'
                ' equals ten. '
                '<bookmark mark="bk_s7"/>Both correct. '
                '<bookmark mark="bk_s8"/>For input four — three times'
                ' four plus one equals thirteen.'
            )
        ) as tracker:

            # ── PHASE 1: find rule (steps 1–4) ───────────────────────────
            mgr1 = StepManager(
                self, start_anchor=anchor,
                font_size=24, buff=0.25
            )

            self.wait_until_bookmark("bk_s1")
            # Highlight +3 on table (output column)
            self.play(
                self._q_full[1][1].animate.set_color(ORANGE_HL),
                run_time=0.4
            )
            s1 = math_obj(
                r"\Delta \text{ output} = +3"
                r"\;\Rightarrow\; 3n",
                font_size=24
            )
            mgr1.add_step(s1)
            active_mobs.append(s1)
            self.play(
                self._q_full[1][1].animate.set_color(PURPLE),
                run_time=0.3
            )

            self.wait_until_bookmark("bk_s2")
            s2 = math_obj(
                r"3 \times 1 = 3, \text{ output} = 4",
                font_size=24
            )
            mgr1.add_step(s2)
            active_mobs.append(s2)

            self.wait_until_bookmark("bk_s3")
            s3 = math_obj(
                r"4 - 3 = 1 \;\Rightarrow\; +1",
                font_size=24
            )
            mgr1.add_step(s3)
            active_mobs.append(s3)

            self.wait_until_bookmark("bk_s4")
            s4 = math_obj(r"3n + 1", font_size=28, color=ORANGE_HL)
            mgr1.add_step(s4)
            active_mobs.append(s4)

            self.wait(0.4)

            # ── PHASE 2: verify + final answer (steps 5–8) ───────────────
            # Fade out phase 1 steps cleanly
            mgr1.fadeout_all(rt=0.7)
            for mob in [s1, s2, s3, s4]:
                if mob in active_mobs:
                    active_mobs.remove(mob)

            mgr2 = StepManager(
                self, start_anchor=anchor,
                font_size=24, buff=0.25
            )

            self.wait_until_bookmark("bk_s5")
            s5 = math_obj(
                r"3(2)+1 = 7 \;\checkmark",
                font_size=24, color=GREEN_OK
            )
            mgr2.add_step(s5)
            active_mobs.append(s5)

            self.wait_until_bookmark("bk_s6")
            s6 = math_obj(
                r"3(3)+1 = 10 \;\checkmark",
                font_size=24, color=GREEN_OK
            )
            mgr2.add_step(s6)
            active_mobs.append(s6)

            self.wait_until_bookmark("bk_s7")
            s7 = math_obj(
                r"\text{Both correct.}",
                font_size=24, color=GREEN_OK
            )
            mgr2.add_step(s7)
            active_mobs.append(s7)

            self.wait_until_bookmark("bk_s8")
            # Highlight row4 on table
            self.play(
                self._q_row4.animate.set_color(ORANGE_HL),
                run_time=0.4
            )
            s8 = math_obj(
                r"3(4)+1 = 13",
                font_size=28, color=ORANGE_HL
            )
            mgr2.add_step(s8)
            active_mobs.append(s8)

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
            "Study how the output changes as the input"
            " increases to find the pattern.",
            "Describe the rule in words first, then write"
            " it as an algebraic expression.",
            "Always verify the rule across multiple"
            " input-output cases.",
        ]
        positions = [UP * 1.5, ORIGIN, DOWN * 1.5]

        with self.voiceover(
            text=(
                '<bookmark mark="bk_sum1"/>Study how the output changes'
                ' as the input increases to find the pattern. '
                '<bookmark mark="bk_sum2"/>Describe the rule in words'
                ' first, then write it as an algebraic expression. '
                '<bookmark mark="bk_sum3"/>Always verify the rule across'
                ' multiple input-output cases.'
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