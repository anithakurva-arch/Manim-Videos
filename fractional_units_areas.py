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
    return MathTex(tex_str,
                   tex_template=TexFontTemplates.gnu_freesans_tx,
                   color=color, font_size=font_size)

def make_fraction(num_tex, den_tex, font_size=36, color=PURPLE):
    num = MathTex(num_tex, tex_template=TexFontTemplates.gnu_freesans_tx,
                  font_size=font_size, color=color)
    den = MathTex(den_tex, tex_template=TexFontTemplates.gnu_freesans_tx,
                  font_size=font_size, color=color)
    bar_width = max(num.width, den.width) + 0.3
    bar = Line(start=LEFT * bar_width / 2, end=RIGHT * bar_width / 2,
               color=color, stroke_width=2.5)
    num.next_to(bar, UP, buff=0.15)
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
        "blocks": blocks, "labels": labels,
        "top_brace": top_brace, "top_label": top_label,
        "bottom_brace": bottom_brace, "bottom_label": bottom_label,
        "diagram": diagram, "active_blocks": active_blocks,
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
Naturally emphasize key terms: fractional unit, equal parts,
one-sixth, area, and any word that introduces a new concept.

Pauses:
Beat at commas, medium pause at dashes.
After stating a key term, pause before continuing.

Mood:
Encouraging, curious, and warm. Avoid monotone.

Do NOT:
- Do not race through sentences.
- Do not add filler words not in the script.
- Do not improvise or paraphrase - read the script exactly.
"""


class FractionalUnitsEqualAreas(VoiceoverScene):

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

        # ═══════════════════════════════════════════════
        # SEGMENT 1 — HOOK
        # ═══════════════════════════════════════════════
        active_mobs = []

        # BLOCK 1A: Title slide (PURPLE — isolated block)
        with self.voiceover(
            text=(
                '<bookmark mark="bk_hook_chocolate"/>Picture one chocolate '
                'on your plate, cut into six equal pieces.'
            )
        ) as tracker:
            self.wait_until_bookmark("bk_hook_chocolate")
            self.camera.background_color = PURPLE
            self.wait(0.1)

            title = Text("Fractional Units",
                         font="Poppins", font_size=52,
                         color=WHITE, weight=BOLD)
            title.move_to(UP * 0.4)
            check_safe_margins(title, "title")
            self.play(FadeIn(title), run_time=0.8)
            active_mobs.append(title)

            sub = Text("Equal Parts and Equal Areas",
                       font="Poppins", font_size=30, color=WHITE)
            sub.next_to(title, DOWN, buff=0.4)
            check_safe_margins(sub, "sub")
            self.play(FadeIn(sub), run_time=0.6)
            active_mobs.append(sub)

        # TRANSITION: Title -> Content
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

        # BLOCK 1B: Hook content
        with self.voiceover(
            text=(
                'Picture one chocolate on your plate, '
                '<bookmark mark="bk_hook_cut"/>cut into six equal pieces. '
                '<bookmark mark="bk_hook_friend"/>Now imagine your friend cuts '
                'an identical chocolate into six equal pieces — '
                'but the cuts go in completely different directions. '
                '<bookmark mark="bk_hook_shapes"/>Some pieces look like rectangles, '
                'others like triangles. '
                '<bookmark mark="bk_hook_question"/>Do they still count as the '
                'same kind of share?'
            )
        ) as tracker:

            # Scene 1b: Chocolate 1 (PATTERN A — Create object)
            choc1 = Rectangle(
                width=4.5, height=1.0,
                color=PURPLE, stroke_width=3.0,
                fill_color=ORANGE_HL, fill_opacity=0.15,
            )
            choc1.move_to(UP * 1.2)
            check_safe_margins(choc1, "choc1")
            self.play(Create(choc1), run_time=0.9)
            active_mobs.append(choc1)

            choc1_label = Text("Chocolate 1", font="Poppins",
                               font_size=20, color=PURPLE)
            choc1_label.next_to(choc1, UP, buff=0.2)
            check_safe_margins(choc1_label, "choc1_label")
            self.play(FadeIn(choc1_label), run_time=0.5)
            active_mobs.append(choc1_label)

            # Scene 1c: Cut lines (PATTERN A — animate the cut)
            self.wait_until_bookmark("bk_hook_cut")
            cut_width = choc1.width / 6
            cut_lines_1 = VGroup()
            for i in range(1, 6):
                x_pos = choc1.get_left()[0] + i * cut_width
                line = Line(
                    start=[x_pos, choc1.get_top()[1], 0],
                    end  =[x_pos, choc1.get_bottom()[1], 0],
                    color=PURPLE, stroke_width=2.0,
                )
                cut_lines_1.add(line)
            for line in cut_lines_1:
                self.play(Create(line), run_time=0.2)
            active_mobs.append(cut_lines_1)

            # Scene 1d: Chocolate 2 (PATTERN A — friend's cuts)
            self.wait_until_bookmark("bk_hook_friend")
            choc2 = Rectangle(
                width=4.5, height=1.0,
                color=PURPLE, stroke_width=3.0,
                fill_color=ORANGE_HL, fill_opacity=0.15,
            )
            choc2.move_to(DOWN * 0.4)
            check_safe_margins(choc2, "choc2")
            self.play(Create(choc2), run_time=0.9)
            active_mobs.append(choc2)

            choc2_label = Text("Chocolate 2", font="Poppins",
                               font_size=20, color=PURPLE)
            choc2_label.next_to(choc2, UP, buff=0.2)
            check_safe_margins(choc2_label, "choc2_label")
            check_y_gap(choc2_label, [choc1, cut_lines_1], name="choc2_label")
            self.play(FadeIn(choc2_label), run_time=0.5)
            active_mobs.append(choc2_label)

            # Diagonal cuts on choc2 (PATTERN A — different direction)
            cut_lines_2 = VGroup()
            diag_cut_width = choc2.width / 6
            for i in range(1, 6):
                x_mid = choc2.get_left()[0] + i * diag_cut_width
                line = Line(
                    start=[x_mid - 0.1, choc2.get_top()[1], 0],
                    end  =[x_mid + 0.1, choc2.get_bottom()[1], 0],
                    color=PURPLE, stroke_width=2.0,
                )
                cut_lines_2.add(line)
            for line in cut_lines_2:
                self.play(Create(line), run_time=0.2)
            active_mobs.append(cut_lines_2)

            # Scene 1e: Highlight shape contrast (PATTERN C)
            self.wait_until_bookmark("bk_hook_shapes")
            # Highlight first piece of choc1 (rectangular)
            rect_piece_hl = Rectangle(
                width=choc1.width / 6, height=choc1.height,
                fill_color=PALE_PURPLE, fill_opacity=0.6,
                stroke_width=0,
            )
            rect_piece_hl.move_to(
                choc1.get_left() + RIGHT * choc1.width / 12
            )
            check_safe_margins(rect_piece_hl, "rect_piece_hl")
            self.play(FadeIn(rect_piece_hl), run_time=0.5)
            active_mobs.append(rect_piece_hl)

            # Highlight first piece of choc2 (diagonal)
            diag_piece_hl = Rectangle(
                width=choc2.width / 6, height=choc2.height,
                fill_color=ORANGE_HL, fill_opacity=0.5,
                stroke_width=0,
            )
            diag_piece_hl.move_to(
                choc2.get_left() + RIGHT * choc2.width / 12
            )
            check_safe_margins(diag_piece_hl, "diag_piece_hl")
            self.play(FadeIn(diag_piece_hl), run_time=0.5)
            active_mobs.append(diag_piece_hl)

            # Scene 1f: Question caption (font_size=22, DOWN zone)
            self.wait_until_bookmark("bk_hook_question")
            q_caption = Text(
                "Do they still count as the same kind of share?",
                font="Poppins", font_size=22, color=PURPLE,
            )
            q_caption.move_to(DOWN * 2.0)
            check_safe_margins(q_caption, "q_caption")
            check_y_gap(q_caption, [choc2, cut_lines_2], name="q_caption")
            self.play(FadeIn(q_caption), run_time=0.7)
            active_mobs.append(q_caption)

        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

        # ═══════════════════════════════════════════════
        # SEGMENT 2 — FRACTIONAL UNIT DEFINITION
        # ═══════════════════════════════════════════════
        with self.voiceover(
            text=(
                '<bookmark mark="bk_def_fractional"/>A fractional unit is one '
                'equal part formed — when a single whole unit is divided into '
                'equal parts. '
                '<bookmark mark="bk_def_unit"/>We also call this a unit fraction. '
                '<bookmark mark="bk_def_sixth"/>So if a chocolate is divided into '
                'six equal parts, each part is one-sixth of the whole. '
                '<bookmark mark="bk_def_written"/>The fractional unit is — '
                'one over six.'
            )
        ) as tracker:

            badge2 = create_heading_badge("Concept")
            self.play(FadeIn(badge2), run_time=0.6)
            active_mobs.append(badge2)

            # Scene 2a: Tape diagram RIGHT half (PATTERN D — highlight 1 part)
            self.wait_until_bookmark("bk_def_fractional")
            tape6 = make_tape_diagram(6, 1, cell_width=1.0, cell_height=0.75)
            tape6["diagram"].move_to(RIGHT * 2.5 + DOWN * 0.2)
            check_safe_margins(tape6["diagram"], "tape6")
            self.play(Create(tape6["blocks"]), run_time=1.2)
            self.play(
                FadeIn(tape6["labels"]),
                FadeIn(tape6["top_brace"]),
                FadeIn(tape6["top_label"]),
                FadeIn(tape6["bottom_brace"]),
                FadeIn(tape6["bottom_label"]),
                run_time=0.7,
            )
            active_mobs.append(tape6["diagram"])

            # Definition text LEFT
            def_text = Text(
                "1 equal part",
                font="Poppins", font_size=24, color=PURPLE,
            )
            def_text.move_to(LEFT * 3.0 + UP * 1.6)
            check_safe_margins(def_text, "def_text")
            self.play(FadeIn(def_text), run_time=0.6)
            active_mobs.append(def_text)

            def_arrow = Arrow(
                start=def_text.get_right() + RIGHT * 0.1,
                end=tape6["active_blocks"].get_left() + LEFT * 0.1,
                color=PURPLE, stroke_width=2.5, tip_length=0.2,
            )
            check_safe_margins(def_arrow, "def_arrow")
            self.play(Create(def_arrow), run_time=0.6)
            active_mobs.append(def_arrow)

            # Scene 2b: "unit fraction" label (PATTERN D)
            self.wait_until_bookmark("bk_def_unit")
            unit_label = Text(
                "= unit fraction",
                font="Poppins", font_size=22, color=ORANGE_HL,
            )
            unit_label.next_to(def_text, DOWN, buff=0.3)
            check_safe_margins(unit_label, "unit_label")
            check_y_gap(unit_label, [def_text], name="unit_label")
            self.play(FadeIn(unit_label), run_time=0.6)
            active_mobs.append(unit_label)

            # Scene 2c: Pulse tape blocks one by one (PATTERN A)
            self.wait_until_bookmark("bk_def_sixth")
            for i, block in enumerate(tape6["blocks"]):
                if i > 0:
                    self.play(
                        block.animate.set_fill(ORANGE_HL, opacity=0.6),
                        run_time=0.25,
                    )
                    self.play(
                        block.animate.set_fill(PALE_PURPLE, opacity=0.3),
                        run_time=0.2,
                    )

            # Scene 2d: Fraction 1/6 (PATTERN D)
            self.wait_until_bookmark("bk_def_written")
            frac16 = make_fraction("1", "6", font_size=44, color=ORANGE_HL)
            frac16.move_to(LEFT * 3.0 + DOWN * 0.8)
            check_safe_margins(frac16, "frac16")
            check_y_gap(frac16, [unit_label], name="frac16")
            self.play(FadeIn(frac16), run_time=0.8)
            active_mobs.append(frac16)

            frac_arrow = Arrow(
                start=frac16.get_right() + RIGHT * 0.1,
                end=tape6["active_blocks"].get_bottom() + DOWN * 0.1,
                color=PURPLE, stroke_width=2.5, tip_length=0.2,
            )
            check_safe_margins(frac_arrow, "frac_arrow")
            self.play(Create(frac_arrow), run_time=0.6)
            active_mobs.append(frac_arrow)

            # Pulse the highlighted block
            self.play(
                Indicate(tape6["active_blocks"], color=ORANGE_HL,
                         scale_factor=1.1), run_time=0.6,
            )

        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

        # ═══════════════════════════════════════════════
        # SEGMENT 3 — SHAPE DOES NOT MATTER
        # ═══════════════════════════════════════════════
        with self.voiceover(
            text=(
                '<bookmark mark="bk_shape_lovely"/>Here is the lovely part. '
                '<bookmark mark="bk_shape_different"/>The pieces can look very '
                'different in shape, but still be equal in size. '
                '<bookmark mark="bk_shape_two"/>Imagine two chocolates of identical '
                'size — one cut into six rectangular pieces, the other into six '
                'triangular pieces of equal area. '
                '<bookmark mark="bk_shape_still"/>Each piece is still one-sixth.'
            )
        ) as tracker:

            badge3 = create_heading_badge("Key Idea")
            self.play(FadeIn(badge3), run_time=0.6)
            active_mobs.append(badge3)

            # Scene 3a: Caption (font_size=22)
            self.wait_until_bookmark("bk_shape_lovely")
            lovely_cap = Text(
                "Here is the lovely part.",
                font="Poppins", font_size=22, color=PURPLE,
            )
            lovely_cap.move_to(UP * 2.5)
            check_safe_margins(lovely_cap, "lovely_cap")
            self.play(FadeIn(lovely_cap), run_time=0.6)
            active_mobs.append(lovely_cap)

            # Scene 3b: Two chocolates side by side (PATTERN C)
            self.wait_until_bookmark("bk_shape_different")
            self.play(FadeOut(lovely_cap), run_time=0.4)
            active_mobs.remove(lovely_cap)

            left_choc = Rectangle(
                width=3.8, height=1.0,
                color=PURPLE, stroke_width=3.0,
                fill_color=ORANGE_HL, fill_opacity=0.12,
            )
            left_choc.move_to(LEFT * 3.0 + UP * 0.5)
            check_safe_margins(left_choc, "left_choc")

            right_choc = Rectangle(
                width=3.8, height=1.0,
                color=PURPLE, stroke_width=3.0,
                fill_color=ORANGE_HL, fill_opacity=0.12,
            )
            right_choc.move_to(RIGHT * 3.0 + UP * 0.5)
            check_safe_margins(right_choc, "right_choc")

            lbl_left = Text("Rectangular cuts", font="Poppins",
                            font_size=18, color=PURPLE)
            lbl_left.next_to(left_choc, UP, buff=0.2)
            check_safe_margins(lbl_left, "lbl_left")

            lbl_right = Text("Triangular cuts", font="Poppins",
                             font_size=18, color=PURPLE)
            lbl_right.next_to(right_choc, UP, buff=0.2)
            check_safe_margins(lbl_right, "lbl_right")

            self.play(
                Create(left_choc), Create(right_choc),
                run_time=1.0,
            )
            self.play(
                FadeIn(lbl_left), FadeIn(lbl_right),
                run_time=0.6,
            )
            active_mobs.extend([left_choc, right_choc, lbl_left, lbl_right])

            # Scene 3c: Draw cuts on each (PATTERN C — both simultaneously)
            self.wait_until_bookmark("bk_shape_two")

            # Rectangular cuts on LEFT
            rect_cut_w = left_choc.width / 6
            left_cuts = VGroup()
            for i in range(1, 6):
                x = left_choc.get_left()[0] + i * rect_cut_w
                ln = Line(
                    start=[x, left_choc.get_top()[1], 0],
                    end  =[x, left_choc.get_bottom()[1], 0],
                    color=PURPLE, stroke_width=2.0,
                )
                left_cuts.add(ln)

            # Diagonal cuts on RIGHT (triangular appearance)
            tri_cut_w = right_choc.width / 6
            right_cuts = VGroup()
            for i in range(1, 6):
                x_mid = right_choc.get_left()[0] + i * tri_cut_w
                ln = Line(
                    start=[x_mid - 0.12, right_choc.get_top()[1], 0],
                    end  =[x_mid + 0.12, right_choc.get_bottom()[1], 0],
                    color=PURPLE, stroke_width=2.0,
                )
                right_cuts.add(ln)

            self.play(
                Create(left_cuts), Create(right_cuts),
                run_time=1.0,
            )
            active_mobs.extend([left_cuts, right_cuts])

            # Scene 3d: Highlight 1 piece each + fraction labels (PATTERN D)
            self.wait_until_bookmark("bk_shape_still")

            # Highlight piece 1 of left choc
            left_hl = Rectangle(
                width=rect_cut_w, height=left_choc.height,
                fill_color=ORANGE_HL, fill_opacity=0.7,
                stroke_width=0,
            )
            left_hl.move_to(
                left_choc.get_left() + RIGHT * rect_cut_w / 2
            )
            check_safe_margins(left_hl, "left_hl")

            # Highlight piece 1 of right choc
            right_hl = Rectangle(
                width=tri_cut_w, height=right_choc.height,
                fill_color=ORANGE_HL, fill_opacity=0.7,
                stroke_width=0,
            )
            right_hl.move_to(
                right_choc.get_left() + RIGHT * tri_cut_w / 2
            )
            check_safe_margins(right_hl, "right_hl")

            self.play(FadeIn(left_hl), FadeIn(right_hl), run_time=0.6)
            active_mobs.extend([left_hl, right_hl])

            # Fraction labels below each choc
            frac_left = make_fraction("1", "6", font_size=32,
                                      color=ORANGE_HL)
            frac_left.next_to(left_choc, DOWN, buff=0.4)
            check_safe_margins(frac_left, "frac_left")
            check_y_gap(frac_left, [left_choc], name="frac_left")

            frac_right = make_fraction("1", "6", font_size=32,
                                       color=ORANGE_HL)
            frac_right.next_to(right_choc, DOWN, buff=0.4)
            check_safe_margins(frac_right, "frac_right")
            check_y_gap(frac_right, [right_choc], name="frac_right")

            self.play(FadeIn(frac_left), FadeIn(frac_right), run_time=0.7)
            active_mobs.extend([frac_left, frac_right])

        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

        # ═══════════════════════════════════════════════
        # SEGMENT 4 — AREA IS WHAT MATTERS
        # ═══════════════════════════════════════════════
        with self.voiceover(
            text=(
                '<bookmark mark="bk_area_because"/>This is because a fractional '
                'unit is about how much area you have — not how it looks. '
                '<bookmark mark="bk_area_example"/>A triangle slice of pizza, '
                'and a rectangle slice of cake, can both be one-sixth — '
                'if each covers the same amount of its whole. '
                '<bookmark mark="bk_area_focus"/>So next time you cut something, '
                'focus on whether the pieces have equal area. '
                '<bookmark mark="bk_area_true"/>That is what makes them true '
                'fractional units.'
            )
        ) as tracker:

            badge4 = create_heading_badge("Key Idea")
            self.play(FadeIn(badge4), run_time=0.6)
            active_mobs.append(badge4)

            # Scene 4a: Triangle LEFT + Rectangle RIGHT (PATTERN B)
            self.wait_until_bookmark("bk_area_because")

            # Triangle shape (LEFT)
            tri_pts = [LEFT * 0.8 + DOWN * 0.5,
                       RIGHT * 0.8 + DOWN * 0.5,
                       UP * 0.5]
            triangle = Polygon(*tri_pts,
                               color=PURPLE, stroke_width=2.5,
                               fill_color=PALE_PURPLE, fill_opacity=0.3)
            triangle.move_to(LEFT * 3.0 + UP * 0.3)
            check_safe_margins(triangle, "triangle")

            # Rectangle shape (RIGHT)
            rect_shape = Rectangle(
                width=1.8, height=1.0,
                color=PURPLE, stroke_width=2.5,
                fill_color=PALE_PURPLE, fill_opacity=0.3,
            )
            rect_shape.move_to(RIGHT * 3.0 + UP * 0.3)
            check_safe_margins(rect_shape, "rect_shape")

            self.play(Create(triangle), Create(rect_shape), run_time=1.0)
            active_mobs.extend([triangle, rect_shape])

            # Fraction at center — both arrows point to it (PATTERN B)
            center_frac = make_fraction("1", "6", font_size=40,
                                        color=ORANGE_HL)
            center_frac.move_to(ORIGIN + UP * 0.3)
            check_safe_margins(center_frac, "center_frac")
            self.play(FadeIn(center_frac), run_time=0.7)
            active_mobs.append(center_frac)

            arr_left = Arrow(
                start=triangle.get_right() + RIGHT * 0.1,
                end=center_frac.get_left() + LEFT * 0.1,
                color=PURPLE, stroke_width=2.5, tip_length=0.2,
            )
            arr_right = Arrow(
                start=rect_shape.get_left() + LEFT * 0.1,
                end=center_frac.get_right() + RIGHT * 0.1,
                color=PURPLE, stroke_width=2.5, tip_length=0.2,
            )
            check_safe_margins(arr_left,  "arr_left")
            check_safe_margins(arr_right, "arr_right")
            self.play(Create(arr_left), Create(arr_right), run_time=0.7)
            active_mobs.extend([arr_left, arr_right])

            # Scene 4b: Area highlight inside both shapes (PATTERN B — effect)
            self.wait_until_bookmark("bk_area_example")
            self.play(
                triangle.animate.set_fill(ORANGE_HL, opacity=0.65),
                rect_shape.animate.set_fill(ORANGE_HL, opacity=0.65),
                run_time=0.8,
            )

            area_label = Text("same area", font="Poppins",
                              font_size=22, color=PURPLE)
            area_label.move_to(DOWN * 1.5)
            check_safe_margins(area_label, "area_label")
            check_y_gap(area_label, [triangle, rect_shape], name="area_label")
            self.play(FadeIn(area_label), run_time=0.6)
            active_mobs.append(area_label)

            # Scene 4c: Brace + equal area label (PATTERN C — confirmation)
            self.wait_until_bookmark("bk_area_focus")
            brace_group = Brace(
                VGroup(triangle, rect_shape),
                direction=DOWN, color=ORANGE_HL,
            )
            brace_label = Text(
                "equal area = equal fractional unit",
                font="Poppins", font_size=20, color=ORANGE_HL,
            )
            brace_label.next_to(brace_group, DOWN, buff=0.15)
            check_safe_margins(brace_label, "brace_label")
            check_y_gap(brace_label, [area_label], name="brace_label")
            self.play(
                FadeOut(area_label),
                run_time=0.4,
            )
            active_mobs.remove(area_label)
            self.play(Create(brace_group), run_time=0.7)
            self.play(FadeIn(brace_label), run_time=0.6)
            active_mobs.extend([brace_group, brace_label])

            # Scene 4d: Pattern E — Concept echo + closing caption
            self.wait_until_bookmark("bk_area_true")
            self.play(
                FadeOut(brace_group), FadeOut(brace_label),
                run_time=0.5,
            )
            active_mobs.remove(brace_group)
            active_mobs.remove(brace_label)

            # Mini tape diagram (scale 0.6) — concept echo
            mini_tape = make_tape_diagram(6, 1, cell_width=0.7,
                                          cell_height=0.5)
            mini_tape["diagram"].move_to(UP * 0.5)
            check_safe_margins(mini_tape["diagram"], "mini_tape")
            self.play(Create(mini_tape["blocks"]), run_time=0.8)
            self.play(
                FadeIn(mini_tape["top_brace"]),
                FadeIn(mini_tape["top_label"]),
                FadeIn(mini_tape["bottom_brace"]),
                FadeIn(mini_tape["bottom_label"]),
                run_time=0.5,
            )
            active_mobs.append(mini_tape["diagram"])

            echo_arrow = Arrow(
                start=mini_tape["active_blocks"].get_bottom() + DOWN * 0.1,
                end=mini_tape["active_blocks"].get_bottom() + DOWN * 0.8,
                color=PURPLE, stroke_width=2.5, tip_length=0.2,
            )
            check_safe_margins(echo_arrow, "echo_arrow")
            self.play(Create(echo_arrow), run_time=0.5)
            active_mobs.append(echo_arrow)

            echo_frac = make_fraction("1", "6", font_size=30,
                                      color=ORANGE_HL)
            echo_frac.next_to(echo_arrow, DOWN, buff=0.15)
            check_safe_margins(echo_frac, "echo_frac")
            check_y_gap(echo_frac, [mini_tape["diagram"]], name="echo_frac")
            self.play(FadeIn(echo_frac), run_time=0.6)
            active_mobs.append(echo_frac)

            # Closing caption at DOWN*2.0, font_size=22
            closing_cap = Text(
                "That is what makes them true fractional units.",
                font="Poppins", font_size=22, color=PURPLE,
            )
            closing_cap.move_to(DOWN * 2.2)
            check_safe_margins(closing_cap, "closing_cap")
            check_y_gap(closing_cap, [echo_frac], name="closing_cap")
            self.play(FadeIn(closing_cap), run_time=0.7)
            active_mobs.append(closing_cap)
            self.wait(0.4)

        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

        # ═══════════════════════════════════════════════
        # SEGMENT 5 — SUMMARY (mini-visuals + text cards)
        # ═══════════════════════════════════════════════
        with self.voiceover(
            text=(
                '<bookmark mark="bk_sum_one"/>A fractional unit is one equal '
                'part of a divided whole. '
                '<bookmark mark="bk_sum_area"/>Equal area means equal fractional '
                'unit. '
                '<bookmark mark="bk_sum_shape"/>Shape can change without '
                'changing the unit.'
            )
        ) as tracker:

            badge5 = create_heading_badge("Summary")
            self.play(FadeIn(badge5), run_time=0.6)
            active_mobs.append(badge5)

            def make_summary_row(mini_mob, text_str, y_pos):
                """Mini-visual LEFT + text card RIGHT."""
                mini_mob.move_to(LEFT * 3.5 + UP * y_pos)
                check_safe_margins(mini_mob, f"mini_{y_pos}")

                txt = Text(text_str, font="Poppins",
                           font_size=22, color=PURPLE)
                card_w = min(txt.width + 0.5, 6.5)
                bg = RoundedRectangle(
                    corner_radius=0.2,
                    width=card_w, height=txt.height + 0.4,
                    fill_color=WHITE, fill_opacity=0.85,
                    stroke_color=PALE_PURPLE, stroke_width=1.5,
                )
                bg.move_to(txt)
                card = VGroup(bg, txt)
                card.move_to(RIGHT * 1.5 + UP * y_pos)
                check_safe_margins(card, f"card_{y_pos}")
                check_y_gap(card, [mini_mob], name=f"card_{y_pos}")
                return mini_mob, card

            # Summary point 1: make_fraction mini + text card
            self.wait_until_bookmark("bk_sum_one")
            mini1 = make_fraction("1", "6", font_size=28, color=ORANGE_HL)
            m1, c1 = make_summary_row(
                mini1,
                "A fractional unit is one equal part of a divided whole.",
                1.5,
            )
            self.play(FadeIn(m1), run_time=0.6)
            self.wait(0.15)
            self.play(FadeIn(c1), run_time=0.6)
            active_mobs.extend([m1, c1])

            # Summary point 2: two equal squares mini + text card
            self.wait_until_bookmark("bk_sum_area")
            sq1 = Rectangle(width=0.55, height=0.55,
                            fill_color=ORANGE_HL, fill_opacity=0.7,
                            color=PURPLE, stroke_width=2.0)
            sq2 = Rectangle(width=0.55, height=0.55,
                            fill_color=ORANGE_HL, fill_opacity=0.7,
                            color=PURPLE, stroke_width=2.0)
            mini2 = VGroup(sq1, sq2).arrange(RIGHT, buff=0.2)
            m2, c2 = make_summary_row(
                mini2,
                "Equal area means equal fractional unit.",
                0.1,
            )
            check_y_gap(m2, [m1, c1], name="m2")
            self.play(FadeIn(m2), run_time=0.6)
            self.wait(0.15)
            self.play(FadeIn(c2), run_time=0.6)
            active_mobs.extend([m2, c2])

            # Summary point 3: triangle + rectangle mini + text card
            self.wait_until_bookmark("bk_sum_shape")
            mini_tri_pts = [LEFT * 0.35 + DOWN * 0.3,
                            RIGHT * 0.35 + DOWN * 0.3,
                            UP * 0.3]
            mini_tri = Polygon(*mini_tri_pts,
                               color=PURPLE, stroke_width=2.0,
                               fill_color=PALE_PURPLE, fill_opacity=0.5)
            mini_rect3 = Rectangle(width=0.7, height=0.5,
                                   color=PURPLE, stroke_width=2.0,
                                   fill_color=PALE_PURPLE, fill_opacity=0.5)
            mini3 = VGroup(mini_tri, mini_rect3).arrange(RIGHT, buff=0.2)
            m3, c3 = make_summary_row(
                mini3,
                "Shape can change without changing the unit.",
                -1.3,
            )
            check_y_gap(m3, [m2, c2], name="m3")
            self.play(FadeIn(m3), run_time=0.6)
            self.wait(0.15)
            self.play(FadeIn(c3), run_time=0.6)
            active_mobs.extend([m3, c3])

            self.wait(0.6)

        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()