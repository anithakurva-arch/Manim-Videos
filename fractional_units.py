import os
import urllib.request
import manimpango
from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.openai import OpenAIService

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

import manim_voiceover.tracker as _vt
_orig_time_until_bookmark = _vt.VoiceoverTracker.time_until_bookmark
_FAILED_BOOKMARKS = []

def _safe_time_until_bookmark(self, mark, buff=0.0, limit=None):
    try:
        return _orig_time_until_bookmark(self, mark, buff, limit)
    except Exception:
        scene_text = getattr(self, 'data', {}).get('input_text', 'unknown')[:80]
        _FAILED_BOOKMARKS.append((mark, scene_text))
        print(f"WARNING  Bookmark '{mark}' NOT FOUND in: {scene_text}...")
        return 0.0

_vt.VoiceoverTracker.time_until_bookmark = _safe_time_until_bookmark

import atexit
def _report():
    if _FAILED_BOOKMARKS:
        print("\n" + "=" * 60)
        print(f"FAILED BOOKMARKS SUMMARY ({len(_FAILED_BOOKMARKS)} total):")
        print("=" * 60)
        for mark, text in _FAILED_BOOKMARKS:
            print(f"  FAILED: {mark}  ->  {text}")
        print("=" * 60)
atexit.register(_report)

SAFE_LEFT   = -6.11
SAFE_RIGHT  = +6.11
SAFE_TOP    = +3.25
SAFE_BOTTOM = -3.25

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

def check_y_gap(new_mob, existing_mobs, min_gap=0.3, name="new_mob"):
    for mob in existing_mobs:
        gap_above = new_mob.get_bottom()[1] - mob.get_top()[1]
        gap_below = mob.get_bottom()[1] - new_mob.get_top()[1]
        if gap_above < min_gap and gap_below < min_gap:
            shift_needed = min_gap - gap_above
            new_mob.shift(UP * shift_needed)
            print(f"WARNING: '{name}' overlapped. Shifted UP by {shift_needed:.2f}")
    return new_mob

def clear_and_transition(scene, active_mobs, new_bg_color,
                         fadeout_time=0.8, buffer=0.2, settle=0.1):
    if active_mobs:
        scene.play(*[FadeOut(m) for m in active_mobs], run_time=fadeout_time)
    scene.wait(buffer)
    scene.camera.background_color = new_bg_color
    scene.wait(settle)

def create_heading_badge(text_str):
    t = Text(text_str, font="Poppins", font_size=28, color=WHITE, weight=BOLD)
    badge = RoundedRectangle(
        corner_radius=0.2,
        width=t.width + 0.6, height=t.height + 0.3,
        fill_color=PURPLE, fill_opacity=1, stroke_width=0,
    )
    badge.move_to(t)
    return VGroup(badge, t).to_corner(UL, buff=0.3)

def math_obj(tex_str, color=PURPLE, font_size=36):
    return MathTex(
        tex_str,
        tex_template=TexFontTemplates.gnu_freesans_tx,
        color=color, font_size=font_size,
    )

def make_fraction(num_tex, den_tex, font_size=36, color=PURPLE):
    num = MathTex(num_tex, tex_template=TexFontTemplates.gnu_freesans_tx,
                  font_size=font_size, color=color)
    den = MathTex(den_tex, tex_template=TexFontTemplates.gnu_freesans_tx,
                  font_size=font_size, color=color)
    bar_width = max(num.width, den.width) + 0.3
    bar = Line(start=LEFT * bar_width / 2, end=RIGHT * bar_width / 2,
               color=color, stroke_width=2.5)
    num.next_to(bar, UP,   buff=0.15)
    den.next_to(bar, DOWN, buff=0.15)
    return VGroup(num, bar, den)

def safe_math(tex_str, color=PURPLE, font_size=36, stroke_width=None):
    obj = MathTex(tex_str, tex_template=TexFontTemplates.gnu_freesans_tx,
                  color=color, font_size=font_size)
    if stroke_width is not None:
        obj.set_stroke(width=stroke_width)
    return obj

def make_legend(entries, position=DR, buff=0.4):
    rows = []
    for var_tex, def_str in entries:
        var_mob = MathTex(var_tex, tex_template=TexFontTemplates.gnu_freesans_tx,
                          font_size=20, color=ORANGE_HL)
        def_mob = Text(def_str, font="Poppins", font_size=20, color=PURPLE)
        row = VGroup(var_mob, def_mob).arrange(RIGHT, buff=0.1)
        rows.append(row)
    content = VGroup(*rows).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
    bg = RoundedRectangle(
        corner_radius=0.15,
        width=content.width + 0.4, height=content.height + 0.3,
        fill_color=WHITE, fill_opacity=0.85,
        stroke_color=PALE_PURPLE, stroke_width=1.0,
    )
    bg.move_to(content)
    group = VGroup(bg, content)
    if position is not None:
        group.to_corner(position, buff=buff)
    return group

def make_tape_diagram(total_parts, active_parts,
                      cell_width=1.2, cell_height=0.8):
    blocks        = VGroup()
    labels        = VGroup()
    active_blocks = VGroup()
    for i in range(total_parts):
        is_active = i < active_parts
        block = Rectangle(
            width=cell_width, height=cell_height,
            color=PURPLE, stroke_width=2.5,
            fill_color=ORANGE_HL if is_active else PALE_PURPLE,
            fill_opacity=0.8    if is_active else 0.3,
        )
        blocks.add(block)
        if is_active:
            active_blocks.add(block)
        lbl = MathTex("1", tex_template=TexFontTemplates.gnu_freesans_tx,
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
    top_brace = Brace(VGroup(*list(blocks)[:active_parts]),
                      direction=UP, color=ORANGE_HL)
    top_label = MathTex(str(active_parts),
                        tex_template=TexFontTemplates.gnu_freesans_tx,
                        font_size=28, color=ORANGE_HL
                        ).next_to(top_brace, UP, buff=0.1)
    bottom_brace = Brace(blocks, direction=DOWN, color=PURPLE)
    bottom_label = MathTex(str(total_parts),
                           tex_template=TexFontTemplates.gnu_freesans_tx,
                           font_size=28, color=PURPLE
                           ).next_to(bottom_brace, DOWN, buff=0.1)
    diagram = VGroup(blocks, labels,
                     top_brace, top_label,
                     bottom_brace, bottom_label)
    return {
        "blocks":        blocks,
        "labels":        labels,
        "top_brace":     top_brace,
        "top_label":     top_label,
        "bottom_brace":  bottom_brace,
        "bottom_label":  bottom_label,
        "diagram":       diagram,
        "active_blocks": active_blocks,
    }

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
                width=cell_size, height=cell_size,
                fill_color=color, fill_opacity=0.15,
                stroke_color=PURPLE, stroke_width=0.5,
            )
            cell.move_to(RIGHT * (c + 0.5) * cell_size +
                         DOWN  * (r + 0.5) * cell_size)
            row_vg.add(cell)
            all_cells.add(cell)
        row_groups.append(row_vg)
    all_cells.move_to(ORIGIN)
    all_cells.row_groups = row_groups
    return all_cells

def make_balance_scale(scene):
    beam = Line(start=LEFT * 2.5, end=RIGHT * 2.5,
                color=PURPLE, stroke_width=3.0).shift(UP * 0.3)
    pivot = Dot(point=beam.get_center(), color=PURPLE, radius=0.08)
    post  = Line(start=beam.get_center() + DOWN * 0.05,
                 end=beam.get_center()   + DOWN * 1.0,
                 color=PURPLE, stroke_width=2.5)
    base  = Line(start=post.get_bottom() + LEFT  * 0.8,
                 end=post.get_bottom()   + RIGHT * 0.8,
                 color=PURPLE, stroke_width=2.5)
    left_pan = Line(
        start=beam.get_left() + LEFT  * 0.4 + DOWN * 0.4,
        end  =beam.get_left() + RIGHT * 0.4 + DOWN * 0.4,
        color=PURPLE, stroke_width=3.0)
    right_pan = Line(
        start=beam.get_right() + LEFT  * 0.4 + DOWN * 0.4,
        end  =beam.get_right() + RIGHT * 0.4 + DOWN * 0.4,
        color=PURPLE, stroke_width=3.0)
    left_string  = Line(start=beam.get_left(),  end=left_pan.get_center(),
                        color=PURPLE, stroke_width=1.5)
    right_string = Line(start=beam.get_right(), end=right_pan.get_center(),
                        color=PURPLE, stroke_width=1.5)
    scale_group = VGroup(beam, pivot, post, base,
                         left_pan, right_pan,
                         left_string, right_string)
    return {
        "beam": beam, "pivot": pivot, "post": post, "base": base,
        "left_pan": left_pan, "right_pan": right_pan,
        "left_string": left_string, "right_string": right_string,
        "scale_group": scale_group,
        "left_anchor":  left_pan.get_top()  + UP * 0.35,
        "right_anchor": right_pan.get_top() + UP * 0.35,
    }

class StepManager:
    SAFE_LIMITS = {(32,0.4):3,(28,0.3):4,(24,0.25):5,(20,0.2):6}
    def __init__(self, scene, start_anchor=None, font_size=24, buff=0.25):
        self.scene     = scene
        self.steps     = []
        self.font_size = font_size
        self.buff      = buff
        self.max_safe  = self.SAFE_LIMITS.get((font_size, buff), 4)
        self.anchor    = start_anchor if start_anchor is not None else (UP*2.7+LEFT*4.5)
    def add_step(self, mobject, run_time=0.7):
        if len(self.steps) >= self.max_safe:
            print(f"WARNING: StepManager at safe limit ({self.max_safe}).")
        if self.steps:
            mobject.next_to(self.steps[-1], DOWN, aligned_edge=LEFT, buff=self.buff)
            self.scene.play(*[s.animate.set_opacity(0.4) for s in self.steps],
                            FadeIn(mobject), run_time=run_time)
        else:
            mobject.move_to(self.anchor)
            self.scene.play(FadeIn(mobject), run_time=run_time)
        self.steps.append(mobject)
        if mobject.get_bottom()[1] < SAFE_BOTTOM:
            print(f"WARNING: Step bottom {mobject.get_bottom()[1]:.2f} below SAFE_BOTTOM.")
        return mobject
    def fadeout_all(self, run_time=0.8):
        if self.steps:
            self.scene.play(*[FadeOut(s) for s in self.steps], run_time=run_time)
            self.steps.clear()
    def get_all(self):
        return VGroup(*self.steps)
    def highlight_current(self, run_time=0.5):
        if self.steps:
            self.scene.play(self.steps[-1].animate.set_color(ORANGE_HL), run_time=run_time)
    def revert_current(self, run_time=0.4):
        if self.steps:
            self.scene.play(self.steps[-1].animate.set_color(PURPLE), run_time=run_time)

TTS_INSTRUCTIONS = """
Voice & Personality:
You are a warm, patient, and encouraging mathematics teacher
speaking to a middle-school student. Your tone is friendly,
calm, and confident - never rushed, never robotic.
The voice profile is shimmer - bright, warm, and slightly playful.

Pacing:
Speak at a MODERATE-TO-SLOW pace. Honor the commas, dashes,
and ellipses in the script.

Emphasis:
Naturally emphasize key terms: fraction names, the final
answer, and any word that introduces a new concept.

Pauses:
Beat at commas, medium pause at dashes, dramatic pause at
ellipses. After stating a final answer, pause before continuing.

Mood:
Encouraging, curious, and warm. Avoid monotone.

Do NOT:
- Do not race through sentences.
- Do not add filler words or commentary not in the script.
- Do not improvise or paraphrase - read the script exactly.
"""


class FractionalUnitsEqualShares(VoiceoverScene):

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

        # ──────────────────────────────────────────────────
        # SEGMENT 1 — HOOK
        # ──────────────────────────────────────────────────
        active_mobs = []

        # BLOCK 1A: Title slide (PURPLE bg — isolated voiceover block)
        with self.voiceover(
            text=(
                '<bookmark mark="bk_hook_roti"/>Imagine you and your friend '
                'bring just one roti to the lunch break.'
            )
        ) as tracker:
            self.wait_until_bookmark("bk_hook_roti")
            self.camera.background_color = PURPLE
            self.wait(0.1)

            title = Text("Fractional Units and Equal Shares",
                         font="Poppins", font_size=44,
                         color=WHITE, weight=BOLD)
            title.move_to(UP * 0.4)
            check_safe_margins(title, "title")
            self.play(FadeIn(title), run_time=0.8)
            active_mobs.append(title)

            sub = Text("Grade 6 - Fractions",
                       font="Poppins", font_size=30, color=WHITE)
            sub.next_to(title, DOWN, buff=0.4)
            check_safe_margins(sub, "sub")
            self.play(FadeIn(sub), run_time=0.6)
            active_mobs.append(sub)

        # TRANSITION: Title -> Content
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

        # BLOCK 1B: Hook content (LAVENDER bg)
        with self.voiceover(
            text=(
                'Both of you are hungry, '
                '<bookmark mark="bk_hook_same"/>and both want the same amount. '
                'So you tear it neatly '
                '<bookmark mark="bk_hook_tear"/>down the middle. '
                'Now each of you holds one part, '
                '<bookmark mark="bk_hook_parts"/>out of two equal parts. '
                '<bookmark mark="bk_hook_name"/>That single piece in your hand '
                'has a name in maths.'
            )
        ) as tracker:

            # Roti rectangle on LAVENDER bg
            roti = Rectangle(width=5.0, height=1.2,
                             color=PURPLE, stroke_width=3.0,
                             fill_color=ORANGE_HL, fill_opacity=0.15)
            roti.move_to(UP * 0.8)
            check_safe_margins(roti, "roti")
            self.play(Create(roti), run_time=1.0)
            active_mobs.append(roti)

            roti_label = Text("1 roti", font="Poppins",
                              font_size=24, color=PURPLE)
            roti_label.next_to(roti, UP, buff=0.2)
            check_safe_margins(roti_label, "roti_label")
            self.play(FadeIn(roti_label), run_time=0.6)
            active_mobs.append(roti_label)

            # Indicate roti at "same amount"
            self.wait_until_bookmark("bk_hook_same")
            self.play(Indicate(roti, color=ORANGE_HL, scale_factor=1.05),
                      run_time=0.6)

            # Split line down middle
            self.wait_until_bookmark("bk_hook_tear")
            split_line = Line(
                start=roti.get_top(),
                end=roti.get_bottom(),
                color=PURPLE, stroke_width=2.5,
            )
            self.play(Create(split_line), run_time=0.8)
            active_mobs.append(split_line)

            # Tape diagram at DOWN*1.2
            self.wait_until_bookmark("bk_hook_parts")
            tape_h = make_tape_diagram(2, 1, cell_width=1.8, cell_height=0.75)
            tape_h["diagram"].move_to(DOWN * 1.8)
            check_safe_margins(tape_h["diagram"], "tape_hook")
            self.play(Create(tape_h["blocks"]), run_time=1.0)
            self.play(
                FadeIn(tape_h["labels"]),
                FadeIn(tape_h["top_brace"]),
                FadeIn(tape_h["top_label"]),
                FadeIn(tape_h["bottom_brace"]),
                FadeIn(tape_h["bottom_label"]),
                run_time=0.7,
            )
            active_mobs.append(tape_h["diagram"])

            # Name badge
            self.wait_until_bookmark("bk_hook_name")
            name_text = Text("This piece has a name in maths.",
                             font="Poppins", font_size=22, color=PURPLE)
            name_text.move_to(DOWN * 3.0)
            check_safe_margins(name_text, "name_text")
            check_y_gap(name_text, [tape_h["diagram"]], name="name_text")
            self.play(FadeIn(name_text), run_time=0.6)
            active_mobs.append(name_text)

        # TRANSITION to Segment 2
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

        # ──────────────────────────────────────────────────
        # SEGMENT 2 — CONCEPT: FRACTION DEFINITION
        # ──────────────────────────────────────────────────
        with self.voiceover(
            text=(
                '<bookmark mark="bk_concept_fraction"/>A fraction is the number '
                'we get — when a whole is divided into equal parts, '
                'and shared equally among a group. '
                '<bookmark mark="bk_concept_share"/>Each equal part is called a share. '
                'So when one roti becomes two equal pieces, '
                '<bookmark mark="bk_concept_half"/>each piece is one-half — '
                'written as one over two.'
            )
        ) as tracker:

            badge2 = create_heading_badge("Concept")
            self.play(FadeIn(badge2), run_time=0.6)
            active_mobs.append(badge2)

            # Tape diagram at right half
            self.wait_until_bookmark("bk_concept_fraction")
            tape2 = make_tape_diagram(2, 1, cell_width=1.6, cell_height=0.75)
            tape2["diagram"].move_to(RIGHT * 3.0 + DOWN * 0.2)
            check_safe_margins(tape2["diagram"], "tape2")
            self.play(Create(tape2["blocks"]), run_time=1.0)
            self.play(
                FadeIn(tape2["labels"]),
                FadeIn(tape2["top_brace"]),
                FadeIn(tape2["top_label"]),
                FadeIn(tape2["bottom_brace"]),
                FadeIn(tape2["bottom_label"]),
                run_time=0.7,
            )
            active_mobs.append(tape2["diagram"])

            # Definition line 1
            def_line1 = Text(
                "A fraction = whole divided into equal parts",
                font="Poppins", font_size=22, color=PURPLE,
            )
            def_line1.move_to(LEFT * 2.0 + UP * 1.8)
            check_safe_margins(def_line1, "def_line1")
            check_y_gap(def_line1, [tape2["diagram"]], name="def_line1")
            self.play(FadeIn(def_line1), run_time=0.7)
            active_mobs.append(def_line1)

            # Definition line 2
            self.wait_until_bookmark("bk_concept_share")
            def_line2 = Text(
                "Each equal part = a share",
                font="Poppins", font_size=22, color=PURPLE,
            )
            def_line2.next_to(def_line1, DOWN, aligned_edge=LEFT, buff=0.35)
            check_safe_margins(def_line2, "def_line2")
            self.play(FadeIn(def_line2), run_time=0.6)
            active_mobs.append(def_line2)

            # Fraction 1/2
            self.wait_until_bookmark("bk_concept_half")
            frac_half = make_fraction("1", "2", font_size=44, color=ORANGE_HL)
            frac_half.move_to(LEFT * 2.5 + DOWN * 0.8)
            check_safe_margins(frac_half, "frac_half")
            check_y_gap(frac_half, [def_line2], name="frac_half")
            self.play(FadeIn(frac_half), run_time=0.8)
            active_mobs.append(frac_half)

            written_half = Text("written as one over two",
                                font="Poppins", font_size=20, color=PURPLE)
            written_half.next_to(frac_half, DOWN, buff=0.25)
            check_safe_margins(written_half, "written_half")
            check_y_gap(written_half, [frac_half], name="written_half")
            self.play(FadeIn(written_half), run_time=0.6)
            active_mobs.append(written_half)

            # Pulse tape active block
            self.play(Indicate(tape2["active_blocks"],
                               color=ORANGE_HL, scale_factor=1.08),
                      run_time=0.6)

        # TRANSITION to Segment 3
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

        # ──────────────────────────────────────────────────
        # SEGMENT 3 — ONE-FOURTH AND NUMBER ROLES
        # ──────────────────────────────────────────────────
        with self.voiceover(
            text=(
                '<bookmark mark="bk_four_friends"/>Now think of four friends '
                'sharing the same one roti equally. '
                'The roti splits into four equal pieces, '
                '<bookmark mark="bk_four_pieces"/>and each friend takes one piece. '
                'Each share is one-fourth — '
                '<bookmark mark="bk_four_written"/>written as one over four. '
                '<bookmark mark="bk_four_notice"/>Notice how the same roti gives '
                'different fractions, depending on how many people share it. '
                '<bookmark mark="bk_bottom_number"/>The bottom number tells how many '
                'equal pieces the whole was cut into. '
                '<bookmark mark="bk_top_number"/>The top number tells how many of '
                'those pieces we are talking about.'
            )
        ) as tracker:

            badge3 = create_heading_badge("Concept")
            self.play(FadeIn(badge3), run_time=0.6)
            active_mobs.append(badge3)

            # Tape diagram for 1/4
            self.wait_until_bookmark("bk_four_friends")
            tape4 = make_tape_diagram(4, 1, cell_width=1.3, cell_height=0.75)
            tape4["diagram"].move_to(RIGHT * 2.5 + DOWN * 0.2)
            check_safe_margins(tape4["diagram"], "tape4")
            self.play(Create(tape4["blocks"]), run_time=1.2)
            self.play(
                FadeIn(tape4["labels"]),
                FadeIn(tape4["top_brace"]),
                FadeIn(tape4["top_label"]),
                FadeIn(tape4["bottom_brace"]),
                FadeIn(tape4["bottom_label"]),
                run_time=0.7,
            )
            active_mobs.append(tape4["diagram"])

            # Description text
            self.wait_until_bookmark("bk_four_pieces")
            four_desc = Text(
                "4 equal pieces, 1 per friend",
                font="Poppins", font_size=22, color=PURPLE,
            )
            four_desc.move_to(LEFT * 2.5 + UP * 1.5)
            check_safe_margins(four_desc, "four_desc")
            check_y_gap(four_desc, [tape4["diagram"]], name="four_desc")
            self.play(FadeIn(four_desc), run_time=0.6)
            active_mobs.append(four_desc)

            # Fraction 1/4
            self.wait_until_bookmark("bk_four_written")
            frac_fourth = make_fraction("1", "4", font_size=44, color=ORANGE_HL)
            frac_fourth.move_to(LEFT * 2.5 + DOWN * 0.5)
            check_safe_margins(frac_fourth, "frac_fourth")
            check_y_gap(frac_fourth, [four_desc], name="frac_fourth")
            self.play(FadeIn(frac_fourth), run_time=0.8)
            active_mobs.append(frac_fourth)

            # Show 1/2 beside 1/4 for comparison
            self.wait_until_bookmark("bk_four_notice")
            frac_half_cmp = make_fraction("1", "2", font_size=36, color=PALE_PURPLE)
            frac_half_cmp.next_to(frac_fourth, LEFT, buff=0.8)
            check_safe_margins(frac_half_cmp, "frac_half_cmp")
            check_y_gap(frac_half_cmp, [four_desc], name="frac_half_cmp")
            self.play(
                frac_fourth.animate.set_opacity(0.5),
                FadeIn(frac_half_cmp),
                run_time=0.7,
            )
            self.play(frac_fourth.animate.set_opacity(1.0), run_time=0.3)
            active_mobs.append(frac_half_cmp)

            # Bottom number label
            self.wait_until_bookmark("bk_bottom_number")
            # Highlight denominator of frac_fourth
            den_fourth = frac_fourth[2]  # denominator MathTex
            self.play(den_fourth.animate.set_color(ORANGE_HL), run_time=0.5)

            bottom_arrow = Arrow(
                start=den_fourth.get_bottom() + DOWN * 0.1,
                end=den_fourth.get_bottom()   + DOWN * 0.7,
                color=PURPLE, stroke_width=2.5, tip_length=0.2,
            )
            bottom_label = Text("total pieces", font="Poppins",
                                font_size=20, color=PURPLE)
            bottom_label.next_to(bottom_arrow, DOWN, buff=0.1)
            check_safe_margins(bottom_arrow, "bottom_arrow")
            check_safe_margins(bottom_label, "bottom_label")
            self.play(Create(bottom_arrow), run_time=0.6)
            self.play(FadeIn(bottom_label), run_time=0.5)
            active_mobs.append(bottom_arrow)
            active_mobs.append(bottom_label)

            # Top number label
            self.wait_until_bookmark("bk_top_number")
            num_fourth = frac_fourth[0]  # numerator MathTex
            self.play(
                den_fourth.animate.set_color(ORANGE_HL),
                num_fourth.animate.set_color(ORANGE_HL),
                run_time=0.5,
            )
            top_arrow = Arrow(
                start=num_fourth.get_top() + UP * 0.1,
                end=num_fourth.get_top()   + UP * 0.7,
                color=PURPLE, stroke_width=2.5, tip_length=0.2,
            )
            top_label = Text("pieces we have", font="Poppins",
                             font_size=20, color=PURPLE)
            top_label.next_to(top_arrow, UP, buff=0.1)
            check_safe_margins(top_arrow, "top_arrow")
            check_safe_margins(top_label, "top_label")
            self.play(Create(top_arrow), run_time=0.6)
            self.play(FadeIn(top_label), run_time=0.5)
            active_mobs.append(top_arrow)
            active_mobs.append(top_label)

        # TRANSITION to Segment 4
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

        # ──────────────────────────────────────────────────
        # SEGMENT 4 — EQUAL MATTERS (ANCHOR SKIPPED)
        # ──────────────────────────────────────────────────
        with self.voiceover(
            text=(
                '<bookmark mark="bk_equal_matters"/>What matters most is the '
                'word equal. '
                'If your friend cuts a bigger piece for himself, '
                '<bookmark mark="bk_unequal_cut"/>your part is no longer a true half. '
                '<bookmark mark="bk_equal_rule"/>A fraction only works when every '
                'share is the same size.'
            )
        ) as tracker:

            badge4 = create_heading_badge("Key Idea")
            self.play(FadeIn(badge4), run_time=0.6)
            active_mobs.append(badge4)

            # EQUAL emphasis
            self.wait_until_bookmark("bk_equal_matters")
            equal_text = Text("EQUAL", font="Poppins", font_size=52,
                              color=ORANGE_HL, weight=BOLD)
            equal_text.move_to(UP * 1.8)
            check_safe_margins(equal_text, "equal_text")
            self.play(FadeIn(equal_text), run_time=0.6)
            self.play(Indicate(equal_text, color=ORANGE_HL, scale_factor=1.08),
                      run_time=0.5)
            active_mobs.append(equal_text)

            # Unequal vs Equal rectangles
            self.wait_until_bookmark("bk_unequal_cut")

            # Unequal group (LEFT)
            unequal_big = Rectangle(width=2.8, height=0.9,
                                    color=PURPLE, stroke_width=2.5,
                                    fill_color=ORANGE_HL, fill_opacity=0.3)
            unequal_small = Rectangle(width=1.2, height=0.9,
                                      color=PURPLE, stroke_width=2.5,
                                      fill_color=PALE_PURPLE, fill_opacity=0.3)
            unequal_group = VGroup(unequal_big, unequal_small).arrange(RIGHT, buff=0)
            unequal_group.move_to(LEFT * 3.0 + DOWN * 0.3)
            check_safe_margins(unequal_group, "unequal_group")
            check_y_gap(unequal_group, [equal_text], name="unequal_group")

            # Equal group (RIGHT)
            equal_left = Rectangle(width=2.0, height=0.9,
                                   color=PURPLE, stroke_width=2.5,
                                   fill_color=ORANGE_HL, fill_opacity=0.3)
            equal_right = Rectangle(width=2.0, height=0.9,
                                    color=PURPLE, stroke_width=2.5,
                                    fill_color=ORANGE_HL, fill_opacity=0.3)
            equal_group = VGroup(equal_left, equal_right).arrange(RIGHT, buff=0)
            equal_group.move_to(RIGHT * 2.0 + DOWN * 0.3)
            check_safe_margins(equal_group, "equal_group")
            check_y_gap(equal_group, [equal_text], name="equal_group")

            self.play(Create(unequal_group), run_time=0.9)
            self.play(Create(equal_group),   run_time=0.9)
            active_mobs.append(unequal_group)
            active_mobs.append(equal_group)

            # X mark above unequal
            x_mark = Text("X", font="Poppins", font_size=32,
                          color=RED, weight=BOLD)
            x_mark.next_to(unequal_group, UP, buff=0.2)
            check_safe_margins(x_mark, "x_mark")
            check_y_gap(x_mark, [equal_text], name="x_mark")
            self.play(FadeIn(x_mark), run_time=0.5)
            active_mobs.append(x_mark)

            # Checkmark above equal
            check_mark = Text("OK", font="Poppins", font_size=28,
                              color=GREEN, weight=BOLD)
            check_mark.next_to(equal_group, UP, buff=0.2)
            check_safe_margins(check_mark, "check_mark")
            check_y_gap(check_mark, [equal_text], name="check_mark")
            self.play(FadeIn(check_mark), run_time=0.5)
            active_mobs.append(check_mark)

            # Rule text
            self.wait_until_bookmark("bk_equal_rule")
            rule_text = Text(
                "Every share must be the same size.",
                font="Poppins", font_size=22, color=PURPLE,
            )
            rule_text.move_to(DOWN * 1.8)
            check_safe_margins(rule_text, "rule_text")
            check_y_gap(rule_text, [unequal_group, equal_group],
                        name="rule_text")
            self.play(FadeIn(rule_text), run_time=0.7)
            active_mobs.append(rule_text)

        # TRANSITION to Segment 5
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

        # ──────────────────────────────────────────────────
        # SEGMENT 5 — CLOSING: FAIR SHARING
        # ──────────────────────────────────────────────────
        with self.voiceover(
            text=(
                '<bookmark mark="bk_closing_split"/>So whenever something is split '
                'fairly among a group, you can describe each share as a fraction. '
                '<bookmark mark="bk_closing_language"/>It is the language of '
                'fair sharing.'
            )
        ) as tracker:

            self.wait_until_bookmark("bk_closing_split")
            close_line1 = Text(
                "Split fairly among a group",
                font="Poppins", font_size=26, color=PURPLE,
            )
            close_line1.move_to(UP * 0.6)
            check_safe_margins(close_line1, "close_line1")
            self.play(FadeIn(close_line1), run_time=0.7)
            active_mobs.append(close_line1)

            close_line2 = Text(
                "= describe each share as a fraction",
                font="Poppins", font_size=26, color=ORANGE_HL,
            )
            close_line2.next_to(close_line1, DOWN, buff=0.35)
            check_safe_margins(close_line2, "close_line2")
            check_y_gap(close_line2, [close_line1], name="close_line2")
            self.play(FadeIn(close_line2), run_time=0.7)
            active_mobs.append(close_line2)

            self.wait_until_bookmark("bk_closing_language")
            close_final = Text(
                "It is the language of fair sharing.",
                font="Poppins", font_size=28, color=PURPLE, weight=BOLD,
            )
            close_final.next_to(close_line2, DOWN, buff=0.5)
            check_safe_margins(close_final, "close_final")
            check_y_gap(close_final, [close_line2], name="close_final")
            self.play(FadeIn(close_final), run_time=0.7)
            self.play(Indicate(close_final, color=ORANGE_HL, scale_factor=1.05),
                      run_time=0.6)
            active_mobs.append(close_final)

        # TRANSITION to Segment 6
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

        # ──────────────────────────────────────────────────
        # SEGMENT 6 — SUMMARY
        # ──────────────────────────────────────────────────
        with self.voiceover(
            text=(
                '<bookmark mark="bk_summary_one"/>A fraction is one equal share '
                'of a whole. '
                '<bookmark mark="bk_summary_bottom"/>The bottom number shows total '
                'equal pieces. '
                '<bookmark mark="bk_summary_equal"/>Equal sharing is what makes '
                'a fraction true.'
            )
        ) as tracker:

            badge6 = create_heading_badge("Summary")
            self.play(FadeIn(badge6), run_time=0.6)
            active_mobs.append(badge6)

            def make_summary_card(text_str, y_pos):
                txt = Text(text_str, font="Poppins",
                           font_size=22, color=PURPLE)
                card_width = min(txt.width + 0.6, 10.5)
                bg = RoundedRectangle(
                    corner_radius=0.2,
                    width=card_width, height=txt.height + 0.4,
                    fill_color=WHITE, fill_opacity=0.85,
                    stroke_color=PALE_PURPLE, stroke_width=1.5,
                )
                bg.move_to(txt)
                card = VGroup(bg, txt).move_to(UP * y_pos)
                check_safe_margins(card, f"sum_card_{y_pos}")
                return card

            self.wait_until_bookmark("bk_summary_one")
            card1 = make_summary_card(
                "A fraction is one equal share of a whole.", 1.5
            )
            self.play(FadeIn(card1), run_time=0.7)
            active_mobs.append(card1)

            self.wait_until_bookmark("bk_summary_bottom")
            card2 = make_summary_card(
                "The bottom number shows total equal pieces.", 0.2
            )
            check_y_gap(card2, [card1], name="card2")
            self.play(FadeIn(card2), run_time=0.7)
            active_mobs.append(card2)

            self.wait_until_bookmark("bk_summary_equal")
            card3 = make_summary_card(
                "Equal sharing is what makes a fraction true.", -1.1
            )
            check_y_gap(card3, [card2], name="card3")
            self.play(FadeIn(card3), run_time=0.7)
            active_mobs.append(card3)

            self.wait(0.6)

        # Final clear
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()