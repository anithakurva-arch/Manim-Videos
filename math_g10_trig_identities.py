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
# BOOKMARK NAME CONSTANTS (define once — use everywhere)
# ============================================================
BK_HELLO           = "bk_hello"
BK_TRY             = "bk_try"
BK_ALWAYS_ONE      = "bk_always_one"
BK_STRANGE         = "bk_strange"
BK_POWER           = "bk_power"
BK_IDENTITY_DEF    = "bk_identity_def"
BK_MAIN_IDENTITY   = "bk_main_identity"
BK_SECOND_IDENTITY = "bk_second_identity"
BK_THIRD_IDENTITY  = "bk_third_identity"
BK_VERIFY_DEF      = "bk_verify_def"
BK_WHY             = "bk_why"
BK_EQUATION        = "bk_equation"
BK_IDENTITY_MUST   = "bk_identity_must"
BK_PYTHAGORAS      = "bk_pythagoras"
BK_THEREFORE       = "bk_therefore"
BK_QUESTION        = "bk_question"
BK_BOTH_45         = "bk_both_45"
BK_SIN45           = "bk_sin45"
BK_COS45           = "bk_cos45"
BK_ADDING          = "bk_adding"
BK_FIRST_HOLDS     = "bk_first_holds"
BK_TAN45           = "bk_tan45"
BK_SEC45           = "bk_sec45"
BK_SECOND_HOLDS    = "bk_second_holds"
BK_ENGINEERS       = "bk_engineers"
BK_SUMMARY_1       = "bk_summary_1"
BK_SUMMARY_2       = "bk_summary_2"

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


# ============================================================
# COSEC TEMPLATE
# ============================================================
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


# ============================================================
# FRACTION BUILDER
# ============================================================
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


# ============================================================
# OVERLINE BUILDER
# ============================================================
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


# ============================================================
# SAFE MATH
# ============================================================
def safe_math(tex_str, color=PURPLE, font_size=36,
              stroke_width=None):
    obj = MathTex(tex_str,
                  tex_template=TexFontTemplates.gnu_freesans_tx,
                  color=color, font_size=font_size)
    if stroke_width is not None:
        obj.set_stroke(width=stroke_width)
    return obj


# ============================================================
# SILENT LEGEND BUILDER
# ============================================================
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


# ============================================================
# COGNITIVE ANCHOR — CATEGORY 1
# ============================================================
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


# ============================================================
# COGNITIVE ANCHOR — CATEGORY 2
# ============================================================
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


# ============================================================
# COGNITIVE ANCHOR — CATEGORY 3
# ============================================================
def make_balance_scale(scene):
    beam = Line(
        start=LEFT  * 3.0,
        end  =RIGHT * 3.0,
        color=PURPLE, stroke_width=3.0,
    ).shift(UP * 0.5)

    pivot = Dot(
        point=beam.get_center(),
        color=PURPLE, radius=0.08,
    )
    post = Line(
        start=beam.get_center() + DOWN * 0.05,
        end  =beam.get_center() + DOWN * 1.0,
        color=PURPLE, stroke_width=2.5,
    )
    base = Line(
        start=post.get_bottom() + LEFT  * 0.8,
        end  =post.get_bottom() + RIGHT * 0.8,
        color=PURPLE, stroke_width=2.5,
    )
    scale_group  = VGroup(beam, pivot, post, base)
    left_anchor  = beam.get_left()  + UP * 0.5
    right_anchor = beam.get_right() + UP * 0.5

    return {
        "beam"         : beam,
        "pivot"        : pivot,
        "post"         : post,
        "base"         : base,
        "scale_group"  : scale_group,
        "left_anchor"  : left_anchor,
        "right_anchor" : right_anchor,
    }


# ============================================================
# SOLUTION STEP MANAGER — PATCHED
# ============================================================
class StepManager:
    """
    Sequential algebra steps with automatic opacity dimming.
    PATCH: uses 'is not None' to avoid NumPy array truth ambiguity.
    """

    def __init__(self, scene, start_anchor=None):
        self.scene  = scene
        self.steps  = []
        # PATCHED: never use 'or' with NumPy array — use 'is not None'
        self.anchor = (
            start_anchor
            if start_anchor is not None
            else (UP * 2.0 + LEFT * 5.5)
        )

    def add_step(self, mobject, run_time=0.7):
        if self.steps:
            mobject.next_to(
                self.steps[-1], DOWN,
                aligned_edge=LEFT, buff=0.4,
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
        return mobject

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
# SAFE MARGIN CONSTANTS & HELPERS
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
        print(f"SAFE MARGIN WARNING — '{name}':")
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
# TTS INSTRUCTIONS
# ============================================================
TTS_INSTRUCTIONS = """
Voice & Personality:
You are a warm, patient, and encouraging mathematics teacher
speaking to a middle-school student. Your tone is friendly,
calm, and confident — never rushed, never robotic. You sound
like a human explainer in a Khan Academy or 3Blue1Brown style
video. The voice profile is shimmer — bright, warm, and
slightly playful.

Pacing:
Speak at a MODERATE-TO-SLOW pace. Honor the commas, dashes,
and ellipses in the script — they are deliberate pacing marks
placed by the director.

Variables and Math Terms:
When pronouncing single-letter variables like x, y, z, a, b,
c, h, r, or t, slow down noticeably and articulate each letter
clearly with a brief micro-pause before and after it.

Formulas:
Slow down further on equations. Pause between each component
so the student can match the spoken word to the symbol on screen.

Numbers and Units:
Pronounce numbers clearly. For units like "centimeter square"
or "meter cube," say them with a confident, deliberate cadence.

Emphasis:
Naturally emphasize key terms: shape names, formulas, the final
answer, and any word that introduces a new concept.

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
- Do not improvise or paraphrase — read the script exactly.
"""


# ============================================================
# MAIN SCENE
# ============================================================
class TrigonometricIdentities(VoiceoverScene):

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

        # ==================================================
        # SEGMENT 1 — HOOK / INTRODUCTION
        # ==================================================
        self.camera.background_color = PURPLE

        with self.voiceover(
            text=f'<bookmark mark="{BK_HELLO}"/>Hello students!'
        ) as tracker:
            self.wait_until_bookmark(BK_HELLO)
            hello_text = Text(
                "Hello students!",
                font="Poppins", font_size=72,
                color=WHITE,
            ).move_to(ORIGIN)
            check_safe_margins(hello_text, "hello_text")
            self.play(FadeIn(hello_text), run_time=0.8)

        self.play(FadeOut(hello_text), run_time=0.6)
        self.camera.background_color = LAVENDER_BG

        with self.voiceover(
            text=(
                f'<bookmark mark="{BK_TRY}"/>Try this — pick any angle, '
                f'find its sine and cosine, square them, and add.'
            )
        ) as tracker:
            self.wait_until_bookmark(BK_TRY)
            hook_line = Text(
                "Pick any angle — find sine, cosine, square, and add.",
                font="Poppins", font_size=32, color=PURPLE,
            ).move_to(ORIGIN)
            check_safe_margins(hook_line, "hook_line")
            self.play(FadeIn(hook_line), run_time=0.8)

        # Balance scale cognitive anchor for hook
        scale_hook = make_balance_scale(self)
        scale_group_hook = scale_hook["scale_group"]
        scale_group_hook.move_to(DOWN * 0.5)
        check_safe_margins(scale_group_hook, "scale_group_hook")

        lhs_hook = math_obj(
            r"\sin^2 A + \cos^2 A",
            font_size=28,
        ).move_to(scale_hook["left_anchor"] + LEFT * 0.3)
        check_safe_margins(lhs_hook, "lhs_hook")

        rhs_question = Text(
            "?", font="Poppins", font_size=36,
            color=ORANGE_HL, weight=BOLD,
        ).move_to(scale_hook["right_anchor"])
        check_safe_margins(rhs_question, "rhs_question")

        with self.voiceover(
            text=f'<bookmark mark="{BK_ALWAYS_ONE}"/>You will always get one.'
        ) as tracker:
            self.wait_until_bookmark(BK_ALWAYS_ONE)
            self.play(FadeOut(hook_line), run_time=0.5)
            self.play(Create(scale_group_hook), run_time=1.2)
            self.play(
                FadeIn(lhs_hook),
                FadeIn(rhs_question),
                run_time=0.7,
            )
            self.play(
                scale_hook["beam"].animate.rotate(
                    -8 * DEGREES,
                    about_point=scale_hook["pivot"].get_center(),
                ),
                run_time=0.8,
            )

        rhs_one = math_obj(r"1", font_size=36).move_to(
            scale_hook["right_anchor"]
        )
        check_safe_margins(rhs_one, "rhs_one")

        with self.voiceover(
            text=f'<bookmark mark="{BK_STRANGE}"/>Strange, isn\'t it?'
        ) as tracker:
            self.wait_until_bookmark(BK_STRANGE)
            self.play(
                ReplacementTransform(rhs_question, rhs_one),
                run_time=0.8,
            )
            self.play(
                scale_hook["beam"].animate.rotate(
                    8 * DEGREES,
                    about_point=scale_hook["pivot"].get_center(),
                ),
                run_time=0.8,
            )

        identity_label = Text(
            "trigonometric identity",
            font="Poppins", font_size=32,
            color=ORANGE_HL,
        ).next_to(scale_group_hook, DOWN, buff=0.4)
        check_safe_margins(identity_label, "identity_label")

        with self.voiceover(
            text=(
                f'<bookmark mark="{BK_POWER}"/>That is the power of '
                f'a trigonometric identity.'
            )
        ) as tracker:
            self.wait_until_bookmark(BK_POWER)
            self.play(
                Indicate(scale_group_hook, color=ORANGE_HL),
                run_time=0.7,
            )
            self.play(FadeIn(identity_label), run_time=0.7)

        self.play(
            FadeOut(scale_group_hook),
            FadeOut(lhs_hook),
            FadeOut(rhs_one),
            FadeOut(identity_label),
            run_time=0.8,
        )

        # ==================================================
        # SEGMENT 2 — CONCEPT: DEFINING IDENTITIES
        # ==================================================
        badge_concept = create_heading_badge("Concept")
        check_safe_margins(badge_concept, "badge_concept")

        with self.voiceover(
            text=(
                f'<bookmark mark="{BK_IDENTITY_DEF}"/>A trigonometric '
                f'identity is an equation, involving trigonometric '
                f'ratios of an angle, that holds true for every '
                f'angle — where the ratios are defined.'
            )
        ) as tracker:
            self.wait_until_bookmark(BK_IDENTITY_DEF)
            self.play(FadeIn(badge_concept), run_time=0.6)

            def_line1 = Text(
                "A trigonometric identity is an equation",
                font="Poppins", font_size=26, color=PURPLE,
            ).move_to(UP * 1.2)
            def_line2 = Text(
                "involving trigonometric ratios of an angle",
                font="Poppins", font_size=26, color=PURPLE,
            ).next_to(def_line1, DOWN, buff=0.3)
            def_line3 = Text(
                "that holds true for every angle where ratios are defined.",
                font="Poppins", font_size=26, color=PURPLE,
            ).next_to(def_line2, DOWN, buff=0.3)
            check_safe_margins(def_line1, "def_line1")
            check_safe_margins(def_line2, "def_line2")
            check_safe_margins(def_line3, "def_line3")
            self.play(
                FadeIn(def_line1),
                FadeIn(def_line2),
                FadeIn(def_line3),
                run_time=0.8,
            )

        # Cognitive anchor — balance scale for identities segment
        scale_c2 = make_balance_scale(self)
        sg_c2    = scale_c2["scale_group"]
        sg_c2.move_to(DOWN * 0.8)
        check_safe_margins(sg_c2, "sg_c2")

        lhs_id1 = math_obj(
            r"\sin^2 A + \cos^2 A",
            font_size=28,
        ).move_to(scale_c2["left_anchor"] + LEFT * 0.2)
        check_safe_margins(lhs_id1, "lhs_id1")

        rhs_id1 = math_obj(
            r"1", font_size=32,
        ).move_to(scale_c2["right_anchor"])
        check_safe_margins(rhs_id1, "rhs_id1")

        formula_id1 = math_obj(
            r"\sin^2 A + \cos^2 A = 1",
            font_size=36,
        ).next_to(sg_c2, DOWN, buff=0.5)
        check_safe_margins(formula_id1, "formula_id1")

        with self.voiceover(
            text=(
                f'The main one is — '
                f'<bookmark mark="{BK_MAIN_IDENTITY}"/>'
                f'sine squared, A, plus cosine squared, A, equals one.'
            )
        ) as tracker:
            self.play(
                FadeOut(def_line1),
                FadeOut(def_line2),
                FadeOut(def_line3),
                run_time=0.6,
            )
            self.wait_until_bookmark(BK_MAIN_IDENTITY)
            self.play(Create(sg_c2), run_time=1.2)
            self.play(
                FadeIn(lhs_id1),
                FadeIn(rhs_id1),
                run_time=0.7,
            )
            self.play(FadeIn(formula_id1), run_time=0.7)

        # Second identity
        lhs_id2 = math_obj(
            r"1 + \tan^2 A",
            font_size=28,
        ).move_to(scale_c2["left_anchor"] + LEFT * 0.1)
        check_safe_margins(lhs_id2, "lhs_id2")

        rhs_id2 = math_obj(
            r"\sec^2 A",
            font_size=28,
        ).move_to(scale_c2["right_anchor"])
        check_safe_margins(rhs_id2, "rhs_id2")

        formula_id2 = math_obj(
            r"1 + \tan^2 A = \sec^2 A",
            font_size=32,
        ).next_to(formula_id1, DOWN, buff=0.35)
        check_safe_margins(formula_id2, "formula_id2")

        with self.voiceover(
            text=(
                f'From this, two more follow — '
                f'<bookmark mark="{BK_SECOND_IDENTITY}"/>'
                f'one plus tangent squared, A, equals secant squared, A,'
            )
        ) as tracker:
            self.wait_until_bookmark(BK_SECOND_IDENTITY)
            self.play(
                ReplacementTransform(lhs_id1, lhs_id2),
                ReplacementTransform(rhs_id1, rhs_id2),
                run_time=0.9,
            )
            self.play(FadeIn(formula_id2), run_time=0.7)

        # Third identity
        lhs_id3 = math_obj(
            r"1 + \cot^2 A",
            font_size=28,
        ).move_to(scale_c2["left_anchor"] + LEFT * 0.1)
        check_safe_margins(lhs_id3, "lhs_id3")

        rhs_id3 = math_obj_cosec(
            r"\cosec^2 A",
            font_size=28,
        ).move_to(scale_c2["right_anchor"])
        check_safe_margins(rhs_id3, "rhs_id3")

        formula_id3 = math_obj_cosec(
            r"1 + \cot^2 A = \cosec^2 A",
            font_size=32,
        ).next_to(formula_id2, DOWN, buff=0.35)
        check_safe_margins(formula_id3, "formula_id3")

        with self.voiceover(
            text=(
                f'<bookmark mark="{BK_THIRD_IDENTITY}"/>'
                f'and one plus cotangent squared, A, '
                f'equals cosecant squared, A.'
            )
        ) as tracker:
            self.wait_until_bookmark(BK_THIRD_IDENTITY)
            self.play(
                ReplacementTransform(lhs_id2, lhs_id3),
                ReplacementTransform(rhs_id2, rhs_id3),
                run_time=0.9,
            )
            self.play(FadeIn(formula_id3), run_time=0.7)

        # Verify definition visual
        lhs_verify = Text(
            "LHS",
            font="Poppins", font_size=32, color=ORANGE_HL,
        ).move_to(LEFT * 2.5 + UP * 2.2)
        check_safe_margins(lhs_verify, "lhs_verify")

        rhs_verify = Text(
            "RHS",
            font="Poppins", font_size=32, color=PURPLE,
        ).move_to(RIGHT * 2.5 + UP * 2.2)
        check_safe_margins(rhs_verify, "rhs_verify")

        verify_arrow = Arrow(
            start=lhs_verify.get_right() + RIGHT * 0.1,
            end=rhs_verify.get_left()    + LEFT  * 0.1,
            color=PURPLE,
            stroke_width=2.5,
            tip_length=0.2,
        )
        check_safe_margins(verify_arrow, "verify_arrow")

        verify_label = Text(
            "verify",
            font="Poppins", font_size=22, color=PURPLE,
        ).next_to(verify_arrow, UP, buff=0.1)
        check_safe_margins(verify_label, "verify_label")

        specific_val = Text(
            "for a specific value of A",
            font="Poppins", font_size=24, color=PURPLE,
        ).move_to(UP * 1.6)
        check_safe_margins(specific_val, "specific_val")

        with self.voiceover(
            text=(
                f'<bookmark mark="{BK_VERIFY_DEF}"/>To verify an identity '
                f'means, to check whether the left-hand side equals the '
                f'right-hand side — for a specific value of, A.'
            )
        ) as tracker:
            self.wait_until_bookmark(BK_VERIFY_DEF)
            self.play(
                sg_c2.animate.set_opacity(0.3),
                formula_id1.animate.set_opacity(0.3),
                formula_id2.animate.set_opacity(0.3),
                formula_id3.animate.set_opacity(0.3),
                lhs_id3.animate.set_opacity(0.3),
                rhs_id3.animate.set_opacity(0.3),
                run_time=0.6,
            )
            self.play(
                FadeIn(lhs_verify),
                FadeIn(rhs_verify),
                run_time=0.7,
            )
            self.play(
                Create(verify_arrow),
                FadeIn(verify_label),
                run_time=0.7,
            )
            self.play(FadeIn(specific_val), run_time=0.6)

        self.play(
            FadeOut(sg_c2),
            FadeOut(lhs_id3),
            FadeOut(rhs_id3),
            FadeOut(formula_id1),
            FadeOut(formula_id2),
            FadeOut(formula_id3),
            FadeOut(lhs_verify),
            FadeOut(rhs_verify),
            FadeOut(verify_arrow),
            FadeOut(verify_label),
            FadeOut(specific_val),
            FadeOut(badge_concept),
            run_time=0.8,
        )

        # ==================================================
        # SEGMENT 3 — WHY IDENTITIES (PYTHAGORAS)
        # ==================================================
        badge_why = create_heading_badge("Why Identities?")
        check_safe_margins(badge_why, "badge_why")

        with self.voiceover(
            text=(
                f'<bookmark mark="{BK_WHY}"/>Now, why are these called '
                f'identities — and not just equations?'
            )
        ) as tracker:
            self.wait_until_bookmark(BK_WHY)
            self.play(FadeIn(badge_why), run_time=0.6)
            why_q = Text(
                "Why identities — not just equations?",
                font="Poppins", font_size=32, color=PURPLE,
            ).move_to(UP * 0.5)
            check_safe_margins(why_q, "why_q")
            self.play(FadeIn(why_q), run_time=0.7)

        # Equation vs Identity comparison boxes
        eq_bg = RoundedRectangle(
            corner_radius=0.2,
            width=4.5, height=2.0,
            fill_color=PALE_PURPLE, fill_opacity=0.4,
            stroke_color=PURPLE, stroke_width=2.5,
        ).move_to(LEFT * 3.0 + DOWN * 0.8)
        check_safe_margins(eq_bg, "eq_bg")

        eq_title = Text(
            "Equation",
            font="Poppins", font_size=26,
            color=PURPLE, weight=BOLD,
        ).move_to(eq_bg.get_top() + DOWN * 0.35)
        check_safe_margins(eq_title, "eq_title")

        eq_body = Text(
            "True for some values",
            font="Poppins", font_size=22, color=PURPLE,
        ).move_to(eq_bg.get_center() + DOWN * 0.1)
        check_safe_margins(eq_body, "eq_body")

        with self.voiceover(
            text=(
                f'<bookmark mark="{BK_EQUATION}"/>An equation may be '
                f'true only for some values.'
            )
        ) as tracker:
            self.wait_until_bookmark(BK_EQUATION)
            self.play(FadeOut(why_q), run_time=0.4)
            self.play(
                FadeIn(eq_bg),
                FadeIn(eq_title),
                run_time=0.7,
            )
            self.play(FadeIn(eq_body), run_time=0.6)

        id_bg = RoundedRectangle(
            corner_radius=0.2,
            width=4.5, height=2.0,
            fill_color=ORANGE_HL, fill_opacity=0.2,
            stroke_color=ORANGE_HL, stroke_width=2.5,
        ).move_to(RIGHT * 3.0 + DOWN * 0.8)
        check_safe_margins(id_bg, "id_bg")

        id_title = Text(
            "Identity",
            font="Poppins", font_size=26,
            color=ORANGE_HL, weight=BOLD,
        ).move_to(id_bg.get_top() + DOWN * 0.35)
        check_safe_margins(id_title, "id_title")

        id_body = Text(
            "Holds for every valid value of A",
            font="Poppins", font_size=20, color=ORANGE_HL,
        ).move_to(id_bg.get_center() + DOWN * 0.1)
        check_safe_margins(id_body, "id_body")

        with self.voiceover(
            text=(
                f'But <bookmark mark="{BK_IDENTITY_MUST}"/>an identity '
                f'must hold — for every valid value of, A.'
            )
        ) as tracker:
            self.wait_until_bookmark(BK_IDENTITY_MUST)
            self.play(
                FadeIn(id_bg),
                FadeIn(id_title),
                run_time=0.7,
            )
            self.play(FadeIn(id_body), run_time=0.6)
            self.play(Indicate(id_bg, color=ORANGE_HL), run_time=0.6)

        # Right-angled triangle + Pythagoras anchor
        self.play(
            FadeOut(eq_bg), FadeOut(eq_title), FadeOut(eq_body),
            FadeOut(id_bg), FadeOut(id_title), FadeOut(id_body),
            run_time=0.7,
        )

        tri_bl = DOWN * 0.8 + LEFT  * 1.8
        tri_br = DOWN * 0.8 + RIGHT * 1.8
        tri_tr = UP   * 1.4 + RIGHT * 1.8

        right_triangle = Polygon(
            tri_bl, tri_br, tri_tr,
            color=PURPLE, stroke_width=2.5,
            fill_color=PALE_PURPLE, fill_opacity=0.15,
        )
        check_safe_margins(right_triangle, "right_triangle")

        ra_size   = 0.2
        ra_corner = tri_br
        ra_mark   = Polygon(
            ra_corner + LEFT  * ra_size,
            ra_corner + LEFT  * ra_size + UP * ra_size,
            ra_corner + UP    * ra_size,
            ra_corner,
            color=PURPLE, stroke_width=1.5,
        )

        hyp_label = Text(
            "hyp",
            font="Poppins", font_size=20, color=PURPLE,
        ).next_to(
            Line(tri_bl, tri_tr).get_center(),
            LEFT, buff=0.2,
        )
        opp_label = Text(
            "opp",
            font="Poppins", font_size=20, color=PURPLE,
        ).next_to(
            Line(tri_br, tri_tr).get_center(),
            RIGHT, buff=0.2,
        )
        adj_label = Text(
            "adj",
            font="Poppins", font_size=20, color=PURPLE,
        ).next_to(
            Line(tri_bl, tri_br).get_center(),
            DOWN, buff=0.2,
        )
        check_safe_margins(hyp_label, "hyp_label")
        check_safe_margins(opp_label, "opp_label")
        check_safe_margins(adj_label, "adj_label")

        pythag_formula = safe_math(
            r"a^2 + b^2 = c^2",
            font_size=36,
            stroke_width=2.0,
        ).next_to(right_triangle, DOWN, buff=0.45)
        check_safe_margins(pythag_formula, "pythag_formula")

        with self.voiceover(
            text=(
                f'<bookmark mark="{BK_PYTHAGORAS}"/>This works because '
                f'these identities come directly from the Pythagoras '
                f'theorem, applied to a right-angled triangle.'
            )
        ) as tracker:
            self.wait_until_bookmark(BK_PYTHAGORAS)
            self.play(
                Create(right_triangle),
                Create(ra_mark),
                run_time=1.2,
            )
            self.play(
                FadeIn(hyp_label),
                FadeIn(opp_label),
                FadeIn(adj_label),
                run_time=0.7,
            )
            self.play(FadeIn(pythag_formula), run_time=0.7)

        identity_ref = math_obj(
            r"\sin^2 A + \cos^2 A = 1",
            font_size=32,
        ).move_to(RIGHT * 3.5 + UP * 0.3)
        check_safe_margins(identity_ref, "identity_ref")

        bridge_arrow = Arrow(
            start=right_triangle.get_right() + RIGHT * 0.2,
            end=identity_ref.get_left()       + LEFT  * 0.2,
            color=PURPLE,
            stroke_width=2.5,
            tip_length=0.2,
        )
        check_safe_margins(bridge_arrow, "bridge_arrow")

        with self.voiceover(
            text=(
                f'Since the theorem is true for every right triangle — '
                f'<bookmark mark="{BK_THEREFORE}"/>the identity holds '
                f'for every valid angle, A.'
            )
        ) as tracker:
            self.wait_until_bookmark(BK_THEREFORE)
            self.play(
                Indicate(right_triangle, color=ORANGE_HL),
                run_time=0.6,
            )
            self.play(Create(bridge_arrow), run_time=0.8)
            self.play(FadeIn(identity_ref), run_time=0.7)

        self.play(
            FadeOut(right_triangle),
            FadeOut(ra_mark),
            FadeOut(hyp_label),
            FadeOut(opp_label),
            FadeOut(adj_label),
            FadeOut(pythag_formula),
            FadeOut(bridge_arrow),
            FadeOut(identity_ref),
            FadeOut(badge_why),
            run_time=0.8,
        )

        # ==================================================
        # SEGMENT 4 — QUESTION
        # ==================================================
        badge_q = create_heading_badge("Question")
        check_safe_margins(badge_q, "badge_q")

        q_line1_p1 = Text(
            "Verify",
            font="Poppins", font_size=26, color=PURPLE,
        )
        q_line1_p2 = math_obj(
            r"\sin^2 A + \cos^2 A = 1",
            font_size=26,
        )
        q_line1 = VGroup(q_line1_p1, q_line1_p2).arrange(
            RIGHT, buff=0.2
        ).move_to(UP * 1.5)
        check_safe_margins(q_line1, "q_line1")

        q_line2_p1 = Text(
            "and",
            font="Poppins", font_size=26, color=PURPLE,
        )
        q_line2_p2 = math_obj(
            r"1 + \tan^2 A = \sec^2 A",
            font_size=26,
        )
        q_line2 = VGroup(q_line2_p1, q_line2_p2).arrange(
            RIGHT, buff=0.2
        ).next_to(q_line1, DOWN, buff=0.3)
        check_safe_margins(q_line2, "q_line2")

        with self.voiceover(
            text=(
                f'<bookmark mark="{BK_QUESTION}"/>Verify — sine squared, '
                f'A, plus cosine squared, A, equals one, and one plus '
                f'tangent squared, A, equals secant squared, A,'
            )
        ) as tracker:
            self.wait_until_bookmark(BK_QUESTION)
            self.play(FadeIn(badge_q), run_time=0.6)
            self.play(FadeIn(q_line1), run_time=0.7)
            self.play(FadeIn(q_line2), run_time=0.7)

        q_line3_p1 = Text(
            "both for",
            font="Poppins", font_size=26, color=PURPLE,
        )
        q_line3_p2 = math_obj(
            r"A = 45^\circ",
            font_size=26,
        )
        q_line3 = VGroup(q_line3_p1, q_line3_p2).arrange(
            RIGHT, buff=0.2
        ).next_to(q_line2, DOWN, buff=0.3)
        check_safe_margins(q_line3, "q_line3")

        unknown_q = Text(
            "?", font="Poppins", font_size=36,
            color=ORANGE_HL, weight=BOLD,
        ).next_to(q_line3, RIGHT, buff=0.3)
        check_safe_margins(unknown_q, "unknown_q")

        with self.voiceover(
            text=(
                f'<bookmark mark="{BK_BOTH_45}"/>both for, A, '
                f'equals forty-five degrees.'
            )
        ) as tracker:
            self.wait_until_bookmark(BK_BOTH_45)
            self.play(FadeIn(q_line3), run_time=0.7)
            self.play(FadeIn(unknown_q), run_time=0.6)

        self.play(
            FadeOut(q_line1),
            FadeOut(q_line2),
            FadeOut(q_line3),
            FadeOut(unknown_q),
            FadeOut(badge_q),
            run_time=0.8,
        )

        # ==================================================
        # SEGMENT 5 — SOLUTION
        # ==================================================
        badge_sol = create_heading_badge("Solution")
        check_safe_margins(badge_sol, "badge_sol")

        # Balance scale — RIGHT half (cognitive anchor)
        scale_sol = make_balance_scale(self)
        sg_sol    = scale_sol["scale_group"]
        sg_sol.move_to(RIGHT * 3.2 + DOWN * 0.5)
        check_safe_margins(sg_sol, "sg_sol")

        # Silent legend
        legend_sol = make_legend(
            [("A", "= 45")],
            position=DR, buff=0.4,
        )
        check_safe_margins(legend_sol, "legend_sol")

        self.play(FadeIn(badge_sol), run_time=0.6)
        self.play(Create(sg_sol), run_time=1.2)
        self.play(FadeIn(legend_sol), run_time=0.7)

        # StepManager — left half  (PATCHED: is not None)
        mgr = StepManager(
            self,
            start_anchor=UP * 2.3 + LEFT * 4.5,
        )

        # ---- sin 45 substitution ----
        sin_val = math_obj(
            r"\sin 45^\circ = \dfrac{1}{\sqrt{2}}",
            font_size=28,
        )
        sin_val.set_stroke(width=1.8)
        check_safe_margins(sin_val, "sin_val")

        sin_sq_val = math_obj(
            r"\sin^2 45^\circ = \dfrac{1}{2}",
            font_size=28,
        )
        sin_sq_val.set_stroke(width=1.8)

        lhs_sol_pan = math_obj(
            r"\sin^2 45^\circ",
            font_size=22,
        ).move_to(scale_sol["left_anchor"] + LEFT * 0.2)
        check_safe_margins(lhs_sol_pan, "lhs_sol_pan")

        with self.voiceover(
            text=(
                f'We know <bookmark mark="{BK_SIN45}"/>sine forty-five '
                f'degrees, equals one over square root of two, so sine '
                f'squared forty-five degrees, equals one over two.'
            )
        ) as tracker:
            self.wait_until_bookmark(BK_SIN45)
            mgr.add_step(sin_val, run_time=0.8)
            sin_sq_val.next_to(
                sin_val, DOWN, aligned_edge=LEFT, buff=0.4,
            )
            self.play(
                *[s.animate.set_opacity(0.4) for s in mgr.steps],
                FadeIn(sin_sq_val),
                run_time=0.7,
            )
            mgr.steps.append(sin_sq_val)
            self.play(FadeIn(lhs_sol_pan), run_time=0.6)

        # ---- cos 45 substitution ----
        cos_val = math_obj(
            r"\cos 45^\circ = \dfrac{1}{\sqrt{2}}",
            font_size=28,
        )
        cos_val.set_stroke(width=1.8)

        cos_sq_val = math_obj(
            r"\cos^2 45^\circ = \dfrac{1}{2}",
            font_size=28,
        )
        cos_sq_val.set_stroke(width=1.8)

        rhs_sol_pan1 = math_obj(
            r"\cos^2 45^\circ",
            font_size=22,
        ).move_to(scale_sol["right_anchor"] + RIGHT * 0.2)
        check_safe_margins(rhs_sol_pan1, "rhs_sol_pan1")

        with self.voiceover(
            text=(
                f'And <bookmark mark="{BK_COS45}"/>cosine forty-five '
                f'degrees, equals one over square root of two, so '
                f'cosine squared forty-five degrees, equals one over two.'
            )
        ) as tracker:
            self.wait_until_bookmark(BK_COS45)
            mgr.add_step(cos_val, run_time=0.8)
            cos_sq_val.next_to(
                cos_val, DOWN, aligned_edge=LEFT, buff=0.4,
            )
            self.play(
                *[s.animate.set_opacity(0.4) for s in mgr.steps],
                FadeIn(cos_sq_val),
                run_time=0.7,
            )
            mgr.steps.append(cos_sq_val)
            self.play(FadeIn(rhs_sol_pan1), run_time=0.6)

        # ---- Addition step ----
        add_step = math_obj(
            r"\dfrac{1}{2} + \dfrac{1}{2} = 1",
            font_size=28,
            color=ORANGE_HL,
        )
        add_step.set_stroke(width=1.8)

        lhs_sum_pan = math_obj(
            r"\sin^2\!45^\circ + \cos^2\!45^\circ",
            font_size=20,
        ).move_to(scale_sol["left_anchor"] + LEFT * 0.2)
        check_safe_margins(lhs_sum_pan, "lhs_sum_pan")

        rhs_one_pan = math_obj(
            r"1", font_size=26,
        ).move_to(scale_sol["right_anchor"])
        check_safe_margins(rhs_one_pan, "rhs_one_pan")

        with self.voiceover(
            text=(
                f'<bookmark mark="{BK_ADDING}"/>Adding — one over two, '
                f'plus one over two, equals one.'
            )
        ) as tracker:
            self.wait_until_bookmark(BK_ADDING)
            mgr.add_step(add_step, run_time=0.8)
            self.play(
                ReplacementTransform(lhs_sol_pan, lhs_sum_pan),
                run_time=0.7,
            )
            self.play(
                FadeOut(rhs_sol_pan1),
                FadeIn(rhs_one_pan),
                run_time=0.7,
            )

        confirm1 = Text(
            "First identity holds",
            font="Poppins", font_size=32, color=ORANGE_HL,
        ).move_to(DOWN * 2.5 + LEFT * 2.0)
        check_safe_margins(confirm1, "confirm1")

        with self.voiceover(
            text=f'<bookmark mark="{BK_FIRST_HOLDS}"/>First identity holds.'
        ) as tracker:
            self.wait_until_bookmark(BK_FIRST_HOLDS)
            self.play(FadeIn(confirm1), run_time=0.7)
            self.play(
                Indicate(confirm1, color=ORANGE_HL),
                run_time=0.6,
            )

        # Clear first-identity steps, keep scale
        self.play(
            *[FadeOut(s) for s in mgr.steps],
            FadeOut(lhs_sum_pan),
            FadeOut(rhs_one_pan),
            FadeOut(confirm1),
            run_time=0.8,
        )
        mgr.steps.clear()

        # ---- tan 45 / second identity ----
        tan_val = math_obj(
            r"\tan 45^\circ = 1",
            font_size=28,
        )
        check_safe_margins(tan_val, "tan_val")

        one_plus_tan = math_obj(
            r"1 + \tan^2 45^\circ = 1 + 1 = 2",
            font_size=28,
        )

        lhs_tan_pan = math_obj(
            r"1 + \tan^2 45^\circ",
            font_size=20,
        ).move_to(scale_sol["left_anchor"] + LEFT * 0.1)
        check_safe_margins(lhs_tan_pan, "lhs_tan_pan")

        rhs_q_pan = Text(
            "?", font="Poppins", font_size=28,
            color=ORANGE_HL, weight=BOLD,
        ).move_to(scale_sol["right_anchor"])
        check_safe_margins(rhs_q_pan, "rhs_q_pan")

        with self.voiceover(
            text=(
                f'Now, <bookmark mark="{BK_TAN45}"/>tangent forty-five '
                f'degrees, equals one, so one plus tangent squared '
                f'forty-five degrees, equals two.'
            )
        ) as tracker:
            self.wait_until_bookmark(BK_TAN45)
            mgr.add_step(tan_val, run_time=0.8)
            one_plus_tan.next_to(
                tan_val, DOWN, aligned_edge=LEFT, buff=0.4,
            )
            self.play(
                *[s.animate.set_opacity(0.4) for s in mgr.steps],
                FadeIn(one_plus_tan),
                run_time=0.7,
            )
            mgr.steps.append(one_plus_tan)
            self.play(
                FadeIn(lhs_tan_pan),
                FadeIn(rhs_q_pan),
                run_time=0.6,
            )
            self.play(
                scale_sol["beam"].animate.rotate(
                    -8 * DEGREES,
                    about_point=scale_sol["pivot"].get_center(),
                ),
                run_time=0.8,
            )

        # ---- sec 45 substitution ----
        sec_val = safe_math(
            r"\sec 45^\circ = \sqrt{2}",
            font_size=28,
            stroke_width=1.8,
        )
        check_safe_margins(sec_val, "sec_val")

        sec_sq_val = safe_math(
            r"\sec^2 45^\circ = 2",
            font_size=28,
            stroke_width=1.8,
        )

        rhs_two_pan = math_obj(
            r"2", font_size=26,
        ).move_to(scale_sol["right_anchor"])
        check_safe_margins(rhs_two_pan, "rhs_two_pan")

        lhs_two_val = math_obj(
            r"2", font_size=26,
        ).move_to(scale_sol["left_anchor"])
        check_safe_margins(lhs_two_val, "lhs_two_val")

        with self.voiceover(
            text=(
                f'And <bookmark mark="{BK_SEC45}"/>secant forty-five '
                f'degrees, equals square root of two, so secant '
                f'squared forty-five degrees, equals two.'
            )
        ) as tracker:
            self.wait_until_bookmark(BK_SEC45)
            mgr.add_step(sec_val, run_time=0.8)
            sec_sq_val.next_to(
                sec_val, DOWN, aligned_edge=LEFT, buff=0.4,
            )
            self.play(
                *[s.animate.set_opacity(0.4) for s in mgr.steps],
                FadeIn(sec_sq_val),
                run_time=0.7,
            )
            mgr.steps.append(sec_sq_val)
            self.play(
                FadeOut(rhs_q_pan),
                FadeIn(rhs_two_pan),
                FadeIn(lhs_two_val),
                run_time=0.6,
            )
            self.play(
                scale_sol["beam"].animate.rotate(
                    8 * DEGREES,
                    about_point=scale_sol["pivot"].get_center(),
                ),
                run_time=0.8,
            )

        confirm2 = Text(
            "Second identity also holds",
            font="Poppins", font_size=32, color=ORANGE_HL,
        ).move_to(DOWN * 2.5 + LEFT * 2.0)
        check_safe_margins(confirm2, "confirm2")

        with self.voiceover(
            text=(
                f'<bookmark mark="{BK_SECOND_HOLDS}"/>Second identity '
                f'also holds.'
            )
        ) as tracker:
            self.wait_until_bookmark(BK_SECOND_HOLDS)
            self.play(FadeIn(confirm2), run_time=0.7)
            self.play(
                Indicate(confirm2, color=ORANGE_HL),
                run_time=0.6,
            )
            self.play(
                legend_sol.animate.set_opacity(0.3),
                run_time=0.5,
            )

        self.wait(0.6)

        self.play(
            *[FadeOut(s) for s in mgr.steps],
            FadeOut(sg_sol),
            FadeOut(lhs_tan_pan),
            FadeOut(rhs_two_pan),
            FadeOut(lhs_two_val),
            FadeOut(confirm2),
            FadeOut(legend_sol),
            FadeOut(badge_sol),
            run_time=0.8,
        )
        mgr.steps.clear()

        # Real-world connection
        with self.voiceover(
            text=(
                f'<bookmark mark="{BK_ENGINEERS}"/>This is the same idea '
                f'engineers use, to verify angle relationships in design.'
            )
        ) as tracker:
            self.wait_until_bookmark(BK_ENGINEERS)
            eng_line1 = Text(
                "Engineers verify angle relationships",
                font="Poppins", font_size=28, color=PURPLE,
            ).move_to(UP * 0.3)
            eng_line2 = Text(
                "in design — using the same identities.",
                font="Poppins", font_size=28, color=PURPLE,
            ).next_to(eng_line1, DOWN, buff=0.3)
            check_safe_margins(eng_line1, "eng_line1")
            check_safe_margins(eng_line2, "eng_line2")
            self.play(FadeIn(eng_line1), run_time=0.7)
            self.play(FadeIn(eng_line2), run_time=0.7)

        self.play(
            FadeOut(eng_line1),
            FadeOut(eng_line2),
            run_time=0.7,
        )

        # ==================================================
        # SEGMENT 6 — SUMMARY
        # ==================================================
        badge_sum = create_heading_badge("Summary")
        check_safe_margins(badge_sum, "badge_sum")

        sum_bullet1 = Text(
            "Trigonometric identities hold true for every valid angle A.",
            font="Poppins", font_size=26, color=PURPLE,
        ).move_to(UP * 0.6)
        check_safe_margins(sum_bullet1, "sum_bullet1")

        sum_bullet2 = Text(
            "Verification means substituting a value and comparing both sides.",
            font="Poppins", font_size=26, color=PURPLE,
        ).next_to(sum_bullet1, DOWN, buff=0.45)
        check_safe_margins(sum_bullet2, "sum_bullet2")

        fit_stack_to_safe_area(VGroup(sum_bullet1, sum_bullet2))

        with self.voiceover(
            text=(
                f'<bookmark mark="{BK_SUMMARY_1}"/>Trigonometric identities '
                f'hold true — for every valid angle, A.'
            )
        ) as tracker:
            self.wait_until_bookmark(BK_SUMMARY_1)
            self.play(FadeIn(badge_sum), run_time=0.6)
            self.play(FadeIn(sum_bullet1), run_time=0.7)

        with self.voiceover(
            text=(
                f'<bookmark mark="{BK_SUMMARY_2}"/>Verification means '
                f'substituting a value, and comparing both sides.'
            )
        ) as tracker:
            self.wait_until_bookmark(BK_SUMMARY_2)
            self.play(FadeIn(sum_bullet2), run_time=0.7)

        self.wait(0.6)

        self.play(
            FadeOut(sum_bullet1),
            FadeOut(sum_bullet2),
            FadeOut(badge_sum),
            run_time=0.8,
        )