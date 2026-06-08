import os
import urllib.request
import manimpango
from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.openai import OpenAIService

# ============================================================
# COSCHOOL COLOR PALETTE
# ============================================================
LAVENDER_BG = "#E7E5F3"
PURPLE      = "#7464CE"
ORANGE_HL   = "#FF9302"
PALE_PURPLE = "#9495D7"

# ============================================================
# POPPINS AUTO-DOWNLOAD & REGISTRATION
# ============================================================
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
                print(f"Downloading {fname}")
                urllib.request.urlretrieve(url, path)
            except Exception as e:
                print(f"   Could not download {fname}: {e}")
                continue
        try:
            manimpango.register_font(path)
        except Exception:
            pass
    print("Poppins setup complete.")

_setup_poppins()

# ============================================================
# BOOKMARK FAILURE TRACKER (DEBUG)
# ============================================================
import manim_voiceover.tracker as _vt
_orig_time_until_bookmark = _vt.VoiceoverTracker.time_until_bookmark
_FAILED_BOOKMARKS = []

def _safe_time_until_bookmark(self, mark, buff=0.0, limit=None):
    try:
        return _orig_time_until_bookmark(self, mark, buff, limit)
    except Exception:
        scene_text = getattr(
            self, 'data', {}
        ).get('input_text', 'unknown')[:80]
        _FAILED_BOOKMARKS.append((mark, scene_text))
        print(
            f"WARNING  Bookmark '{mark}' NOT FOUND in: "
            f"{scene_text}..."
        )
        return 0.0

_vt.VoiceoverTracker.time_until_bookmark = _safe_time_until_bookmark

import atexit
def _report():
    if _FAILED_BOOKMARKS:
        print("\n" + "=" * 60)
        print(
            f"FAILED BOOKMARKS SUMMARY "
            f"({len(_FAILED_BOOKMARKS)} total):"
        )
        print("=" * 60)
        for mark, text in _FAILED_BOOKMARKS:
            print(f"  FAILED: {mark}  ->  {text}")
        print("=" * 60)
atexit.register(_report)

# ============================================================
# SAFE MARGIN CONSTANTS
# ============================================================
SAFE_LEFT   = -6.11
SAFE_RIGHT  = +6.11
SAFE_TOP    = +3.25
SAFE_BOTTOM = -3.25
SAFE_BUFF_H = 0.5
SAFE_BUFF_V = 0.75


def check_safe_margins(mob, name="object"):
    left   = mob.get_left()[0]
    right  = mob.get_right()[0]
    top    = mob.get_top()[1]
    bottom = mob.get_bottom()[1]
    violations = []
    if left   < SAFE_LEFT:   violations.append(f"LEFT   {left:.2f}")
    if right  > SAFE_RIGHT:  violations.append(f"RIGHT  {right:.2f}")
    if top    > SAFE_TOP:    violations.append(f"TOP    {top:.2f}")
    if bottom < SAFE_BOTTOM: violations.append(f"BOTTOM {bottom:.2f}")
    if violations:
        print(f"SAFE MARGIN WARNING - '{name}':")
        for v in violations:
            print(f"   VIOLATION: {v}")
    return len(violations) == 0


def clamp_to_safe_area(mob):
    sx, sy = 0.0, 0.0
    if   mob.get_left()[0]   < SAFE_LEFT:   sx = SAFE_LEFT   - mob.get_left()[0]
    elif mob.get_right()[0]  > SAFE_RIGHT:  sx = SAFE_RIGHT  - mob.get_right()[0]
    if   mob.get_bottom()[1] < SAFE_BOTTOM: sy = SAFE_BOTTOM - mob.get_bottom()[1]
    elif mob.get_top()[1]    > SAFE_TOP:    sy = SAFE_TOP    - mob.get_top()[1]
    if sx != 0.0 or sy != 0.0:
        mob.shift(RIGHT * sx + UP * sy)
    return mob


def fit_stack_to_safe_area(vgroup):
    max_h = (SAFE_TOP - SAFE_BOTTOM) - 0.5
    if vgroup.height > max_h:
        vgroup.scale_to_fit_height(max_h)
    return vgroup


# ============================================================
# STANDARD HELPERS
# ============================================================

def create_heading_badge(text_str):
    t = Text(text_str, font="Poppins", font_size=28,
             color=WHITE, weight=BOLD)
    badge = RoundedRectangle(
        corner_radius=0.2,
        width=t.width + 0.6, height=t.height + 0.3,
        fill_color=PURPLE, fill_opacity=1, stroke_width=0,
    )
    badge.move_to(t)
    return VGroup(badge, t).to_corner(UL, buff=0.3)


def create_dimension(start, end, label_str,
                     direction=DOWN, buff=0.3):
    arrow = DoubleArrow(
        start=start, end=end,
        color=PURPLE, stroke_width=2,
        tip_length=0.2, buff=0,
    )
    label = Text(label_str, font="Poppins",
                 font_size=22, color=PURPLE)
    label.next_to(arrow.get_center(), direction, buff=0.15)
    return VGroup(arrow, label)


def create_unknown(position):
    return Text("?", font="Poppins", font_size=36,
                color=ORANGE_HL, weight=BOLD).move_to(position)


def math_obj(tex_str, color=PURPLE, font_size=36):
    return MathTex(
        tex_str,
        tex_template=TexFontTemplates.gnu_freesans_tx,
        color=color,
        font_size=font_size,
    )


def _make_cosec_template():
    base = TexFontTemplates.gnu_freesans_tx
    t = TexTemplate(
        tex_compiler     = base.tex_compiler,
        output_format    = base.output_format,
        preamble         = base.preamble,
        placeholder_text = base.placeholder_text,
    )
    t.add_to_preamble(r"\DeclareMathOperator{\cosec}{cosec}")
    return t

COSEC_TEMPLATE = _make_cosec_template()


def math_obj_cosec(tex_str, color=PURPLE, font_size=36):
    return MathTex(
        tex_str,
        tex_template=COSEC_TEMPLATE,
        color=color,
        font_size=font_size,
    )


def make_fraction(num_tex, den_tex, font_size=36, color=PURPLE):
    num = MathTex(num_tex,
                  tex_template=TexFontTemplates.gnu_freesans_tx,
                  font_size=font_size, color=color)
    den = MathTex(den_tex,
                  tex_template=TexFontTemplates.gnu_freesans_tx,
                  font_size=font_size, color=color)
    bar_width = max(num.width, den.width) + 0.3
    bar = Line(
        start=LEFT  * bar_width / 2,
        end  =RIGHT * bar_width / 2,
        color=color, stroke_width=2.5,
    )
    num.next_to(bar, UP,   buff=0.15)
    den.next_to(bar, DOWN, buff=0.15)
    return VGroup(num, bar, den)


def make_overline_label(tex_str, font_size=36, color=PURPLE):
    label = MathTex(tex_str,
                    tex_template=TexFontTemplates.gnu_freesans_tx,
                    font_size=font_size, color=color)
    bar = Line(
        start=label.get_corner(UL) + UP * 0.08,
        end  =label.get_corner(UR) + UP * 0.08,
        color=color, stroke_width=2.5,
    )
    return VGroup(label, bar)


def safe_math(tex_str, color=PURPLE, font_size=36,
              stroke_width=None):
    obj = MathTex(tex_str,
                  tex_template=TexFontTemplates.gnu_freesans_tx,
                  color=color, font_size=font_size)
    if stroke_width is not None:
        obj.set_stroke(width=stroke_width)
    return obj


def make_legend(entries, position=DR, buff=0.4):
    rows = []
    for var_tex, def_str in entries:
        var_mob = MathTex(
            var_tex,
            tex_template=TexFontTemplates.gnu_freesans_tx,
            font_size=20, color=ORANGE_HL,
        )
        def_mob = Text(def_str, font="Poppins",
                       font_size=20, color=PURPLE)
        row = VGroup(var_mob, def_mob).arrange(RIGHT, buff=0.1)
        rows.append(row)
    content = VGroup(*rows).arrange(DOWN,
                                    aligned_edge=LEFT, buff=0.25)
    bg = RoundedRectangle(
        corner_radius=0.15,
        width        = content.width  + 0.4,
        height       = content.height + 0.3,
        fill_color   = WHITE,
        fill_opacity = 0.85,
        stroke_color = PALE_PURPLE,
        stroke_width = 1.0,
    )
    bg.move_to(content)
    group = VGroup(bg, content)
    if position is not None:
        group.to_corner(position, buff=buff)
    return group


def make_grid_overlay(shape_width, shape_height,
                      cell_size=0.5, color=PALE_PURPLE):
    cols   = int(shape_width  / cell_size)
    rows_n = int(shape_height / cell_size)
    all_cells  = VGroup()
    row_groups = []
    for r in range(rows_n):
        row_vg = VGroup()
        for c in range(cols):
            cell = Rectangle(
                width        = cell_size,
                height       = cell_size,
                fill_color   = color,
                fill_opacity = 0.15,
                stroke_color = PURPLE,
                stroke_width = 0.5,
            )
            cell.move_to(
                RIGHT * (c + 0.5) * cell_size +
                DOWN  * (r + 0.5) * cell_size
            )
            row_vg.add(cell)
            all_cells.add(cell)
        row_groups.append(row_vg)
    all_cells.move_to(ORIGIN)
    all_cells.row_groups = row_groups
    return all_cells


def make_tape_diagram(total_parts, active_parts,
                      cell_width=1.2, cell_height=0.8):
    blocks        = VGroup()
    labels        = VGroup()
    active_blocks = VGroup()
    for i in range(total_parts):
        is_active = i < active_parts
        block = Rectangle(
            width        = cell_width,
            height       = cell_height,
            color        = PURPLE,
            stroke_width = 2.5,
            fill_color   = ORANGE_HL   if is_active else PALE_PURPLE,
            fill_opacity = 0.8         if is_active else 0.3,
        )
        blocks.add(block)
        if is_active:
            active_blocks.add(block)
        lbl = MathTex("1",
                      tex_template=TexFontTemplates.gnu_freesans_tx,
                      font_size=20, color=PURPLE)
        labels.add(lbl)
    blocks.arrange(RIGHT, buff=0)
    if blocks.width > 8.0:
        sf = 8.0 / blocks.width
        blocks.scale(sf)
        for lbl in labels:
            lbl.scale(sf)
    for i, block in enumerate(blocks):
        labels[i].move_to(block.get_center())
    top_brace = Brace(
        VGroup(*list(blocks)[:active_parts]),
        direction=UP, color=ORANGE_HL,
    )
    top_label = MathTex(
        str(active_parts),
        tex_template=TexFontTemplates.gnu_freesans_tx,
        font_size=28, color=ORANGE_HL,
    ).next_to(top_brace, UP, buff=0.1)
    bottom_brace = Brace(blocks, direction=DOWN, color=PURPLE)
    bottom_label = MathTex(
        str(total_parts),
        tex_template=TexFontTemplates.gnu_freesans_tx,
        font_size=28, color=PURPLE,
    ).next_to(bottom_brace, DOWN, buff=0.1)
    diagram = VGroup(
        blocks, labels,
        top_brace, top_label,
        bottom_brace, bottom_label,
    )
    return {
        "blocks"        : blocks,
        "labels"        : labels,
        "top_brace"     : top_brace,
        "top_label"     : top_label,
        "bottom_brace"  : bottom_brace,
        "bottom_label"  : bottom_label,
        "diagram"       : diagram,
        "active_blocks" : active_blocks,
    }


def make_balance_scale(scene):
    beam = Line(
        start=LEFT  * 2.5,
        end  =RIGHT * 2.5,
        color=PURPLE, stroke_width=3.0,
    ).shift(UP * 0.3)
    pivot = Dot(point=beam.get_center(), color=PURPLE, radius=0.08)
    post  = Line(
        start=beam.get_center() + DOWN * 0.05,
        end  =beam.get_center() + DOWN * 1.0,
        color=PURPLE, stroke_width=2.5,
    )
    base = Line(
        start=post.get_bottom() + LEFT  * 0.8,
        end  =post.get_bottom() + RIGHT * 0.8,
        color=PURPLE, stroke_width=2.5,
    )
    left_pan = Line(
        start=beam.get_left() + LEFT  * 0.4 + DOWN * 0.4,
        end  =beam.get_left() + RIGHT * 0.4 + DOWN * 0.4,
        color=PURPLE, stroke_width=3.0,
    )
    right_pan = Line(
        start=beam.get_right() + LEFT  * 0.4 + DOWN * 0.4,
        end  =beam.get_right() + RIGHT * 0.4 + DOWN * 0.4,
        color=PURPLE, stroke_width=3.0,
    )
    left_string = Line(
        start=beam.get_left(),
        end  =left_pan.get_center(),
        color=PURPLE, stroke_width=1.5,
    )
    right_string = Line(
        start=beam.get_right(),
        end  =right_pan.get_center(),
        color=PURPLE, stroke_width=1.5,
    )
    scale_group = VGroup(
        beam, pivot, post, base,
        left_pan, right_pan,
        left_string, right_string,
    )
    left_anchor  = left_pan.get_top()  + UP * 0.35
    right_anchor = right_pan.get_top() + UP * 0.35
    return {
        "beam"         : beam,
        "pivot"        : pivot,
        "post"         : post,
        "base"         : base,
        "left_pan"     : left_pan,
        "right_pan"    : right_pan,
        "left_string"  : left_string,
        "right_string" : right_string,
        "scale_group"  : scale_group,
        "left_anchor"  : left_anchor,
        "right_anchor" : right_anchor,
    }


class StepManager:
    SAFE_LIMITS = {
        (32, 0.4):  3,
        (28, 0.3):  4,
        (24, 0.25): 5,
        (20, 0.2):  6,
    }

    def __init__(self, scene, start_anchor=None,
                 font_size=24, buff=0.25):
        self.scene     = scene
        self.steps     = []
        self.font_size = font_size
        self.buff      = buff
        self.max_safe  = self.SAFE_LIMITS.get((font_size, buff), 4)
        self.anchor    = (
            start_anchor
            if start_anchor is not None
            else (UP * 2.7 + LEFT * 4.5)
        )

    def add_step(self, mobject, run_time=0.7):
        if len(self.steps) >= self.max_safe:
            print(
                f"WARNING: StepManager at safe limit "
                f"({self.max_safe})."
            )
        if self.steps:
            mobject.next_to(
                self.steps[-1], DOWN,
                aligned_edge=LEFT, buff=self.buff,
            )
            self.scene.play(
                *[s.animate.set_opacity(0.4) for s in self.steps],
                FadeIn(mobject),
                run_time=run_time,
            )
        else:
            mobject.move_to(self.anchor)
            self.scene.play(FadeIn(mobject), run_time=run_time)
        self.steps.append(mobject)
        if mobject.get_bottom()[1] < SAFE_BOTTOM:
            print(
                f"WARNING: Step bottom at "
                f"{mobject.get_bottom()[1]:.2f} below "
                f"SAFE_BOTTOM ({SAFE_BOTTOM})."
            )
        return mobject

    def can_add(self):
        return len(self.steps) < self.max_safe

    def get_bottom_y(self):
        if not self.steps:
            return self.anchor[1]
        return min(s.get_bottom()[1] for s in self.steps)

    def highlight_current(self, run_time=0.5):
        if self.steps:
            self.scene.play(
                self.steps[-1].animate.set_color(ORANGE_HL),
                run_time=run_time,
            )

    def revert_current(self, run_time=0.4):
        if self.steps:
            self.scene.play(
                self.steps[-1].animate.set_color(PURPLE),
                run_time=run_time,
            )

    def get_all(self):
        return VGroup(*self.steps)

    def fadeout_all(self, run_time=0.8):
        if self.steps:
            self.scene.play(
                *[FadeOut(s) for s in self.steps],
                run_time=run_time,
            )
            self.steps.clear()


# ============================================================
# TTS INSTRUCTIONS
# ============================================================
TTS_INSTRUCTIONS = """
Voice & Personality:
You are a warm, patient, and encouraging mathematics teacher
speaking to a middle-school student. Your tone is friendly,
calm, and confident - never rushed, never robotic. You sound
like a human explainer in a Khan Academy or 3Blue1Brown style
video. The voice profile is shimmer - bright, warm, and
slightly playful.

Pacing:
Speak at a MODERATE-TO-SLOW pace. Honor the commas, dashes,
and ellipses in the script - they are deliberate pacing marks
placed by the director.

Variables and Math Terms:
When pronouncing single-letter variables like x, y, z, a, b,
c, h, r, or t, slow down noticeably and articulate each letter
clearly with a brief micro-pause before and after it.

Formulas:
Slow down further on equations. Pause between each component
so the student can match the spoken word to the symbol on screen.

Numbers and Units:
Pronounce numbers clearly.

Emphasis:
Naturally emphasize key terms: fraction names, the method
steps, the final answer, and any word that introduces a new
concept.

Pauses:
Beat at commas, medium pause at dashes, dramatic pause at
ellipses. After stating a final answer, pause for a moment
before continuing.

Mood:
Encouraging, curious, and warm. Avoid monotone. Add gentle warmth.

Do NOT:
- Do not race through sentences.
- Do not flatten your voice into monotone.
- Do not add filler words or commentary not in the script.
- Do not improvise or paraphrase - read the script exactly.
"""


# ============================================================
# MAIN SCENE
# ============================================================
class EgyptianFractions(VoiceoverScene):

    def construct(self):
        self.set_speech_service(
            OpenAIService(
                voice="shimmer",
                model="gpt-4o-mini-tts",
                transcription_model="medium",
                instructions=TTS_INSTRUCTIONS,
            ),
            create_subcaption=False,
        )

        # ----------------------------------------------------------
        # SEGMENT 1 — HOOK / INTRODUCTION
        # ----------------------------------------------------------
        with self.voiceover(
            text=(
                '<bookmark mark="bk_hook_intro"/>Imagine you want to give a friend, '
                'three-fifths of a chocolate bar — but only using simple, neat pieces, '
                'like one-half and one-tenth. '
                '<bookmark mark="bk_hook_question"/>Can two such pieces add up exactly '
                'to three-fifths? '
                '<bookmark mark="bk_hook_egypt"/>Long ago, in ancient Egypt, people '
                'wrote every fraction this way — as sums of different unit fractions. '
                '<bookmark mark="bk_hook_see"/>Let us see how it works.'
            )
        ) as tracker:

            # Scene 1a — Title slide
            self.wait_until_bookmark("bk_hook_intro")
            self.camera.background_color = PURPLE
            title_main = Text(
                "Egyptian Fractions",
                font="Poppins", font_size=56,
                color=WHITE, weight=BOLD,
            ).move_to(UP * 0.5)
            title_sub = Text(
                "Unit Fraction Sums",
                font="Poppins", font_size=36,
                color=WHITE,
            ).next_to(title_main, DOWN, buff=0.4)
            check_safe_margins(title_main, "title_main")
            check_safe_margins(title_sub, "title_sub")
            self.play(FadeIn(title_main), run_time=0.8)
            self.play(FadeIn(title_sub), run_time=0.6)
            self.wait(0.4)
            self.play(FadeOut(title_main), FadeOut(title_sub), run_time=0.6)

            # Scene 1b — Lavender bg, tape diagram 3/5
            self.wait_until_bookmark("bk_hook_question")
            self.camera.background_color = LAVENDER_BG
            tape_hook = make_tape_diagram(5, 3, cell_width=1.1, cell_height=0.75)
            tape_hook["diagram"].move_to(DOWN * 0.3)
            check_safe_margins(tape_hook["diagram"], "tape_hook")
            self.play(Create(tape_hook["blocks"]), run_time=1.2)
            self.play(
                FadeIn(tape_hook["labels"]),
                FadeIn(tape_hook["top_brace"]),
                FadeIn(tape_hook["top_label"]),
                FadeIn(tape_hook["bottom_brace"]),
                FadeIn(tape_hook["bottom_label"]),
                run_time=0.7,
            )

            # Scene 1c — Question text above tape
            hook_q_text = Text(
                "Can two such pieces add up exactly?",
                font="Poppins", font_size=28, color=PURPLE,
            ).move_to(UP * 2.0)
            check_safe_margins(hook_q_text, "hook_q_text")
            self.play(FadeIn(hook_q_text), run_time=0.7)

            # Scene 1d — Ancient Egypt badge
            self.wait_until_bookmark("bk_hook_egypt")
            egypt_badge_txt = Text(
                "Ancient Egypt",
                font="Poppins", font_size=26,
                color=ORANGE_HL, weight=BOLD,
            ).move_to(UP * 2.9)
            check_safe_margins(egypt_badge_txt, "egypt_badge_txt")
            self.play(FadeIn(egypt_badge_txt), run_time=0.7)

            # Scene 1e — FadeOut all
            self.wait_until_bookmark("bk_hook_see")
            self.play(
                FadeOut(tape_hook["diagram"]),
                FadeOut(hook_q_text),
                FadeOut(egypt_badge_txt),
                run_time=0.8,
            )

        # ----------------------------------------------------------
        # SEGMENT 2 — CONCEPT: UNIT FRACTIONS AND EGYPTIAN FRACTIONS
        # ----------------------------------------------------------
        with self.voiceover(
            text=(
                '<bookmark mark="bk_concept_unit"/>A unit fraction is a fraction '
                'whose numerator is one, '
                '<bookmark mark="bk_concept_examples"/>like one-half, one-third, '
                'or one-fifth. '
                '<bookmark mark="bk_concept_egyptian"/>An Egyptian fraction is a way '
                'of writing a fraction as a sum of different unit fractions. '
                '<bookmark mark="bk_concept_key"/>The key word is different — '
                'no unit fraction may be repeated. '
                '<bookmark mark="bk_concept_instance"/>For instance, three-fifths '
                'can be written as one-half plus one-tenth — '
                'and we will see why shortly.'
            )
        ) as tracker:

            self.camera.background_color = LAVENDER_BG
            badge_concept = create_heading_badge("Concept")
            self.play(FadeIn(badge_concept), run_time=0.6)

            # Scene 2a — Unit fraction definition text
            self.wait_until_bookmark("bk_concept_unit")
            unit_def_part1 = Text(
                "A unit fraction has numerator",
                font="Poppins", font_size=28, color=PURPLE,
            )
            unit_def_part2 = math_obj("1", font_size=32)
            unit_def_line = VGroup(
                unit_def_part1, unit_def_part2
            ).arrange(RIGHT, buff=0.2).move_to(UP * 2.2)
            check_safe_margins(unit_def_line, "unit_def_line")
            self.play(FadeIn(unit_def_line), run_time=0.7)

            # Scene 2b — Three tape diagrams for 1/2, 1/3, 1/5
            self.wait_until_bookmark("bk_concept_examples")
            tape_half  = make_tape_diagram(2, 1, cell_width=0.9, cell_height=0.6)
            tape_third = make_tape_diagram(3, 1, cell_width=0.9, cell_height=0.6)
            tape_fifth = make_tape_diagram(5, 1, cell_width=0.9, cell_height=0.6)

            diagrams_row = VGroup(
                tape_half["diagram"],
                tape_third["diagram"],
                tape_fifth["diagram"],
            ).arrange(RIGHT, buff=0.6).move_to(UP * 0.7)
            check_safe_margins(diagrams_row, "diagrams_row")

            self.play(Create(tape_half["blocks"]),   run_time=0.8)
            self.play(Create(tape_third["blocks"]),  run_time=0.8)
            self.play(Create(tape_fifth["blocks"]),  run_time=0.8)
            self.play(
                FadeIn(tape_half["top_brace"]),
                FadeIn(tape_half["top_label"]),
                FadeIn(tape_half["bottom_brace"]),
                FadeIn(tape_half["bottom_label"]),
                FadeIn(tape_third["top_brace"]),
                FadeIn(tape_third["top_label"]),
                FadeIn(tape_third["bottom_brace"]),
                FadeIn(tape_third["bottom_label"]),
                FadeIn(tape_fifth["top_brace"]),
                FadeIn(tape_fifth["top_label"]),
                FadeIn(tape_fifth["bottom_brace"]),
                FadeIn(tape_fifth["bottom_label"]),
                run_time=0.7,
            )

            # Fractions below tape diagrams
            frac_half  = make_fraction("1", "2", font_size=28)
            frac_third = make_fraction("1", "3", font_size=28)
            frac_fifth = make_fraction("1", "5", font_size=28)

            frac_half.next_to(tape_half["diagram"],   DOWN, buff=0.3)
            frac_third.next_to(tape_third["diagram"], DOWN, buff=0.3)
            frac_fifth.next_to(tape_fifth["diagram"], DOWN, buff=0.3)
            check_safe_margins(frac_half,  "frac_half")
            check_safe_margins(frac_third, "frac_third")
            check_safe_margins(frac_fifth, "frac_fifth")
            self.play(
                FadeIn(frac_half),
                FadeIn(frac_third),
                FadeIn(frac_fifth),
                run_time=0.7,
            )

            # Scene 2c — Egyptian fraction concept
            self.wait_until_bookmark("bk_concept_egyptian")
            egyptian_label = Text(
                "Egyptian Fraction",
                font="Poppins", font_size=26,
                color=ORANGE_HL, weight=BOLD,
            ).move_to(DOWN * 2.2)
            check_safe_margins(egyptian_label, "egyptian_label")
            self.play(FadeIn(egyptian_label), run_time=0.7)

            # Scene 2d — Highlight "different"
            self.wait_until_bookmark("bk_concept_key")
            different_text = Text(
                "Key: different unit fractions only",
                font="Poppins", font_size=26,
                color=PURPLE,
            ).move_to(DOWN * 2.9)
            check_safe_margins(different_text, "different_text")
            self.play(FadeIn(different_text), run_time=0.6)
            self.play(
                different_text.animate.set_color(ORANGE_HL),
                run_time=0.5,
            )
            self.play(
                different_text.animate.set_color(PURPLE),
                run_time=0.4,
            )

            # Scene 2e — Instance: 3/5 = 1/2 + 1/10
            self.wait_until_bookmark("bk_concept_instance")
            self.play(
                FadeOut(unit_def_line),
                FadeOut(diagrams_row),
                FadeOut(frac_half),
                FadeOut(frac_third),
                FadeOut(frac_fifth),
                FadeOut(egyptian_label),
                FadeOut(different_text),
                run_time=0.7,
            )

            frac_35  = make_fraction("3", "5",  font_size=32)
            equals_t = Text("=", font="Poppins", font_size=32, color=PURPLE)
            frac_12  = make_fraction("1", "2",  font_size=32)
            plus_t   = Text("+", font="Poppins", font_size=32, color=PURPLE)
            frac_110 = make_fraction("1", "10", font_size=32)

            instance_row = VGroup(
                frac_35, equals_t, frac_12, plus_t, frac_110,
            ).arrange(RIGHT, buff=0.35).move_to(ORIGIN)
            check_safe_margins(instance_row, "instance_row")
            self.play(FadeIn(instance_row), run_time=0.9)
            self.wait(0.5)
            self.play(
                FadeOut(instance_row),
                FadeOut(badge_concept),
                run_time=0.7,
            )

        # ----------------------------------------------------------
        # SEGMENT 3 — METHOD
        # ----------------------------------------------------------
        with self.voiceover(
            text=(
                '<bookmark mark="bk_method_find"/>To express a fraction this way, '
                'we find the largest unit fraction that fits inside our fraction. '
                '<bookmark mark="bk_method_subtract"/>We subtract it using a common '
                'denominator, just as Brahmagupta taught us. '
                '<bookmark mark="bk_method_left"/>Then we look at what is left. '
                '<bookmark mark="bk_method_stop"/>If the remainder is itself a unit '
                'fraction, we stop. '
                '<bookmark mark="bk_method_repeat"/>If not, we repeat.'
            )
        ) as tracker:

            self.camera.background_color = LAVENDER_BG
            badge_method = create_heading_badge("Method")
            self.play(FadeIn(badge_method), run_time=0.6)

            # Scene 3a — Step 1 text + tape diagram for 3/5 at right
            self.wait_until_bookmark("bk_method_find")
            tape_method = make_tape_diagram(5, 3, cell_width=1.0, cell_height=0.7)
            tape_method["diagram"].move_to(RIGHT * 3.0)
            check_safe_margins(tape_method["diagram"], "tape_method")
            self.play(Create(tape_method["blocks"]), run_time=1.0)
            self.play(
                FadeIn(tape_method["top_brace"]),
                FadeIn(tape_method["top_label"]),
                FadeIn(tape_method["bottom_brace"]),
                FadeIn(tape_method["bottom_label"]),
                run_time=0.7,
            )

            step1 = Text(
                "Step 1: Find largest unit fraction",
                font="Poppins", font_size=24, color=PURPLE,
            ).move_to(LEFT * 2.5 + UP * 1.5)
            check_safe_margins(step1, "step1")
            self.play(FadeIn(step1), run_time=0.7)

            # Scene 3b — Highlight first blocks to show 1/2 fitting
            frac_12_method = make_fraction("1", "2", font_size=28, color=ORANGE_HL)
            frac_12_method.move_to(LEFT * 2.5 + UP * 0.4)
            check_safe_margins(frac_12_method, "frac_12_method")

            # Highlight first 2 blocks (closest to 1/2 of 5 = 2.5 blocks)
            for i, block in enumerate(tape_method["blocks"]):
                if i < 2:
                    self.play(
                        block.animate.set_fill(ORANGE_HL, opacity=1.0),
                        run_time=0.4,
                    )
            self.play(FadeIn(frac_12_method), run_time=0.6)

            # Scene 3c — Step 2
            self.wait_until_bookmark("bk_method_subtract")
            step2 = Text(
                "Step 2: Subtract using common denominator",
                font="Poppins", font_size=22, color=PURPLE,
            ).next_to(step1, DOWN, aligned_edge=LEFT, buff=0.3)
            check_safe_margins(step2, "step2")
            self.play(
                step1.animate.set_opacity(0.4),
                FadeIn(step2),
                run_time=0.7,
            )

            # Scene 3d — Step 3
            self.wait_until_bookmark("bk_method_left")
            step3 = Text(
                "Step 3: Look at the remainder",
                font="Poppins", font_size=24, color=PURPLE,
            ).next_to(step2, DOWN, aligned_edge=LEFT, buff=0.3)
            check_safe_margins(step3, "step3")
            self.play(
                step2.animate.set_opacity(0.4),
                FadeIn(step3),
                run_time=0.7,
            )

            # Scene 3e — Step 4 (STOP condition)
            self.wait_until_bookmark("bk_method_stop")
            step4_part1 = Text(
                "Step 4: Remainder = unit fraction",
                font="Poppins", font_size=24, color=PURPLE,
            )
            stop_badge = Text(
                "-> STOP",
                font="Poppins", font_size=24,
                color=ORANGE_HL, weight=BOLD,
            )
            step4 = VGroup(step4_part1, stop_badge).arrange(RIGHT, buff=0.2)
            step4.next_to(step3, DOWN, aligned_edge=LEFT, buff=0.3)
            check_safe_margins(step4, "step4")
            self.play(
                step3.animate.set_opacity(0.4),
                FadeIn(step4),
                run_time=0.7,
            )

            # Scene 3f — Step 5 (Repeat)
            self.wait_until_bookmark("bk_method_repeat")
            step5 = Text(
                "Step 5: If not -> Repeat",
                font="Poppins", font_size=24, color=PURPLE,
            ).next_to(step4, DOWN, aligned_edge=LEFT, buff=0.3)
            check_safe_margins(step5, "step5")
            self.play(
                step4.animate.set_opacity(0.4),
                FadeIn(step5),
                run_time=0.7,
            )
            self.wait(0.4)
            self.play(
                FadeOut(step1),
                FadeOut(step2),
                FadeOut(step3),
                FadeOut(step4),
                FadeOut(step5),
                FadeOut(frac_12_method),
                FadeOut(tape_method["diagram"]),
                FadeOut(badge_method),
                run_time=0.8,
            )

        # ----------------------------------------------------------
        # SEGMENT 4 — QUESTION
        # ----------------------------------------------------------
        with self.voiceover(
            text=(
                '<bookmark mark="bk_question"/>Express three-fifths as a sum '
                'of different unit fractions.'
            )
        ) as tracker:

            self.camera.background_color = LAVENDER_BG
            badge_q = create_heading_badge("Question")
            self.play(FadeIn(badge_q), run_time=0.6)

            self.wait_until_bookmark("bk_question")

            # Question text verbatim
            q_text_part1 = Text(
                "Express",
                font="Poppins", font_size=26, color=PURPLE,
            )
            q_frac = make_fraction("3", "5", font_size=26)
            q_text_part2 = Text(
                "as a sum of different unit fractions.",
                font="Poppins", font_size=26, color=PURPLE,
            )
            q_line = VGroup(q_text_part1, q_frac, q_text_part2).arrange(
                RIGHT, buff=0.25
            ).move_to(UP * 2.5)
            check_safe_margins(q_line, "q_line")
            self.play(FadeIn(q_line), run_time=0.7)

            # Tape diagram for 3/5 as question anchor
            tape_q = make_tape_diagram(5, 3, cell_width=1.1, cell_height=0.75)
            tape_q["diagram"].move_to(RIGHT * 2.0 + DOWN * 0.3)
            check_safe_margins(tape_q["diagram"], "tape_q")
            self.play(Create(tape_q["blocks"]), run_time=1.2)
            self.play(
                FadeIn(tape_q["top_brace"]),
                FadeIn(tape_q["top_label"]),
                FadeIn(tape_q["bottom_brace"]),
                FadeIn(tape_q["bottom_label"]),
                run_time=0.7,
            )
            self.wait(0.5)

        # ----------------------------------------------------------
        # SEGMENT 5 — SOLUTION
        # ----------------------------------------------------------
        with self.voiceover(
            text=(
                '<bookmark mark="bk_sol_compare"/>One-half is less than '
                'three-fifths because three-fifths equals six-tenths, '
                '<bookmark mark="bk_sol_while"/>while one-half equals five-tenths. '
                '<bookmark mark="bk_sol_no_bigger"/>No bigger unit fraction fits '
                'inside three-fifths. '
                '<bookmark mark="bk_sol_subtract"/>Subtract one-half from '
                'three-fifths using ten as a common denominator. '
                '<bookmark mark="bk_sol_result"/>Six-tenths minus five-tenths '
                'gives one-tenth. '
                '<bookmark mark="bk_sol_stop"/>One-tenth is already a unit '
                'fraction, so we stop. '
                '<bookmark mark="bk_sol_final"/>So three-fifths equals '
                'one-half plus one-tenth.'
            )
        ) as tracker:

            # Transition: swap badge, shift tape right
            badge_sol = create_heading_badge("Solution")
            self.play(
                FadeOut(badge_q),
                FadeIn(badge_sol),
                run_time=0.5,
            )

            # Shift tape diagram to right half for solution
            self.play(
                tape_q["diagram"].animate.move_to(RIGHT * 3.5 + DOWN * 0.3),
                run_time=1.0,
            )
            check_safe_margins(tape_q["diagram"], "tape_q_shifted")

            # StepManager on left
            mgr = StepManager(
                self,
                start_anchor=UP * 1.8 + LEFT * 3.5,
                font_size=24,
                buff=0.3,
            )

            # Scene 5a — Show 3/5 = 6/10
            self.wait_until_bookmark("bk_sol_compare")
            step_35 = make_fraction("3", "5", font_size=28)
            eq1 = Text("=", font="Poppins", font_size=28, color=PURPLE)
            step_610 = make_fraction("6", "10", font_size=28)
            row_35_610 = VGroup(step_35, eq1, step_610).arrange(RIGHT, buff=0.25)
            row_35_610.move_to(UP * 1.8 + LEFT * 3.2)
            check_safe_margins(row_35_610, "row_35_610")
            mgr.steps.append(row_35_610)
            self.play(FadeIn(row_35_610), run_time=0.7)

            # Scene 5b — Show 1/2 = 5/10
            self.wait_until_bookmark("bk_sol_while")
            step_12 = make_fraction("1", "2", font_size=28)
            eq2 = Text("=", font="Poppins", font_size=28, color=PURPLE)
            step_510 = make_fraction("5", "10", font_size=28)
            row_12_510 = VGroup(step_12, eq2, step_510).arrange(RIGHT, buff=0.25)
            row_12_510.next_to(row_35_610, DOWN, aligned_edge=LEFT, buff=0.3)
            check_safe_margins(row_12_510, "row_12_510")
            self.play(
                row_35_610.animate.set_opacity(0.4),
                FadeIn(row_12_510),
                run_time=0.7,
            )
            mgr.steps.append(row_12_510)

            # Highlight tape blocks 1-2 to show 1/2 region
            for i, block in enumerate(tape_q["blocks"]):
                if i < 2:
                    self.play(
                        block.animate.set_fill(PALE_PURPLE, opacity=0.6),
                        run_time=0.3,
                    )

            # Scene 5c — No bigger unit fraction
            self.wait_until_bookmark("bk_sol_no_bigger")
            no_bigger = Text(
                "No bigger unit fraction fits",
                font="Poppins", font_size=22, color=PURPLE,
            )
            no_bigger.next_to(row_12_510, DOWN, aligned_edge=LEFT, buff=0.3)
            check_safe_margins(no_bigger, "no_bigger")
            self.play(
                row_12_510.animate.set_opacity(0.4),
                FadeIn(no_bigger),
                run_time=0.7,
            )
            mgr.steps.append(no_bigger)

            # Scene 5d — Subtraction: 3/5 - 1/2
            self.wait_until_bookmark("bk_sol_subtract")
            sub_35 = make_fraction("3", "5", font_size=26)
            minus_t = safe_math(r"-", font_size=26, stroke_width=2.0)
            sub_12 = make_fraction("1", "2", font_size=26)
            sub_row = VGroup(sub_35, minus_t, sub_12).arrange(RIGHT, buff=0.2)
            sub_row.next_to(no_bigger, DOWN, aligned_edge=LEFT, buff=0.3)
            check_safe_margins(sub_row, "sub_row")
            self.play(
                no_bigger.animate.set_opacity(0.4),
                FadeIn(sub_row),
                run_time=0.7,
            )
            mgr.steps.append(sub_row)

            # Scene 5e — 6/10 - 5/10
            self.wait_until_bookmark("bk_sol_result")
            sub_610 = make_fraction("6", "10", font_size=26)
            minus_t2 = safe_math(r"-", font_size=26, stroke_width=2.0)
            sub_510 = make_fraction("5", "10", font_size=26)
            sub_row2 = VGroup(sub_610, minus_t2, sub_510).arrange(RIGHT, buff=0.2)
            sub_row2.next_to(sub_row, DOWN, aligned_edge=LEFT, buff=0.3)
            check_safe_margins(sub_row2, "sub_row2")
            self.play(
                sub_row.animate.set_opacity(0.4),
                FadeIn(sub_row2),
                run_time=0.7,
            )
            mgr.steps.append(sub_row2)

            # Result: = 1/10
            eq_result = Text("=", font="Poppins", font_size=26, color=ORANGE_HL)
            result_110 = make_fraction("1", "10", font_size=26, color=ORANGE_HL)
            result_row = VGroup(eq_result, result_110).arrange(RIGHT, buff=0.2)
            result_row.next_to(sub_row2, RIGHT, buff=0.25)
            check_safe_margins(result_row, "result_row")
            self.play(FadeIn(result_row), run_time=0.7)

            # Pulse last tape block ORANGE_HL to show 1/10 remainder
            last_block = tape_q["blocks"][-1]
            self.play(
                last_block.animate.set_fill(ORANGE_HL, opacity=1.0),
                run_time=0.5,
            )

            # Scene 5f — Stop condition
            self.wait_until_bookmark("bk_sol_stop")
            stop_text_part = Text(
                "One-tenth is a unit fraction —",
                font="Poppins", font_size=22, color=PURPLE,
            )
            stop_badge_t = Text(
                "STOP",
                font="Poppins", font_size=22,
                color=ORANGE_HL, weight=BOLD,
            )
            stop_row = VGroup(stop_text_part, stop_badge_t).arrange(
                RIGHT, buff=0.2
            )
            stop_row.next_to(sub_row2, DOWN, aligned_edge=LEFT, buff=0.3)
            check_safe_margins(stop_row, "stop_row")
            self.play(
                sub_row2.animate.set_opacity(0.4),
                result_row.animate.set_opacity(0.4),
                FadeIn(stop_row),
                run_time=0.7,
            )
            mgr.steps.append(stop_row)

            # Check stack height
            fit_stack_to_safe_area(mgr.get_all())

            # Scene 5g — Final answer
            self.wait_until_bookmark("bk_sol_final")
            # Fade out step stack
            self.play(
                *[FadeOut(s) for s in mgr.steps],
                FadeOut(q_line),
                run_time=0.7,
            )
            mgr.steps.clear()

            # Final answer row: 3/5 = 1/2 + 1/10
            ans_35  = make_fraction("3", "5",  font_size=34, color=ORANGE_HL)
            ans_eq  = Text("=", font="Poppins", font_size=34, color=ORANGE_HL)
            ans_12  = make_fraction("1", "2",  font_size=34, color=ORANGE_HL)
            ans_pl  = Text("+", font="Poppins", font_size=34, color=ORANGE_HL)
            ans_110 = make_fraction("1", "10", font_size=34, color=ORANGE_HL)

            final_row = VGroup(
                ans_35, ans_eq, ans_12, ans_pl, ans_110,
            ).arrange(RIGHT, buff=0.35).move_to(LEFT * 1.0 + DOWN * 0.2)
            check_safe_margins(final_row, "final_row")

            # RoundedRectangle border around answer
            ans_border = RoundedRectangle(
                corner_radius=0.2,
                width  = final_row.width  + 0.5,
                height = final_row.height + 0.4,
                stroke_color  = ORANGE_HL,
                stroke_width  = 2.5,
                fill_opacity  = 0,
            )
            ans_border.move_to(final_row)
            check_safe_margins(ans_border, "ans_border")

            self.play(FadeIn(final_row), run_time=0.8)
            self.play(Create(ans_border), run_time=0.8)
            self.wait(0.6)

            # FadeOut solution
            self.play(
                FadeOut(final_row),
                FadeOut(ans_border),
                FadeOut(tape_q["diagram"]),
                FadeOut(badge_sol),
                run_time=0.8,
            )

        # ----------------------------------------------------------
        # SEGMENT 6 — SUMMARY
        # ----------------------------------------------------------
        with self.voiceover(
            text=(
                '<bookmark mark="bk_summary_unit"/>A unit fraction has one '
                'as its numerator. '
                '<bookmark mark="bk_summary_egyptian"/>Egyptian fractions are '
                'sums of different unit fractions. '
                '<bookmark mark="bk_summary_method"/>Subtract the largest '
                'possible unit fraction, then repeat.'
            )
        ) as tracker:

            self.camera.background_color = LAVENDER_BG
            badge_sum = create_heading_badge("Summary")
            self.play(FadeIn(badge_sum), run_time=0.6)

            def make_summary_card(text_str, y_pos):
                txt = Text(
                    text_str,
                    font="Poppins", font_size=24, color=PURPLE,
                )
                bg = RoundedRectangle(
                    corner_radius=0.2,
                    width        = min(txt.width + 0.6, 11.0),
                    height       = txt.height + 0.4,
                    fill_color   = WHITE,
                    fill_opacity = 0.85,
                    stroke_color = PALE_PURPLE,
                    stroke_width = 1.5,
                )
                bg.move_to(txt)
                card = VGroup(bg, txt).move_to(UP * y_pos)
                check_safe_margins(card, f"summary_card_{y_pos}")
                return card

            # Scene 6a — Card 1
            self.wait_until_bookmark("bk_summary_unit")
            card1 = make_summary_card(
                "A unit fraction has one as its numerator.", 1.5
            )
            self.play(FadeIn(card1), run_time=0.7)

            # Scene 6b — Card 2
            self.wait_until_bookmark("bk_summary_egyptian")
            card2 = make_summary_card(
                "Egyptian fractions: sums of different unit fractions.", 0.2
            )
            self.play(FadeIn(card2), run_time=0.7)

            # Scene 6c — Card 3
            self.wait_until_bookmark("bk_summary_method")
            card3 = make_summary_card(
                "Subtract the largest unit fraction, then repeat.", -1.1
            )
            self.play(FadeIn(card3), run_time=0.7)
            self.wait(0.6)

            self.play(
                FadeOut(card1),
                FadeOut(card2),
                FadeOut(card3),
                FadeOut(badge_sum),
                run_time=0.8,
            )