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

FRACTIONS: When you see "X over Y", say exactly "X over Y".
Never say "X-Yths" or common names like "one half" or "three quarters".
Example: "three over four" NOT "three quarters".

Read the script EXACTLY. No filler. No improvisation.
"""


def create_heading_badge(text_str):
    t = Text(text_str, font="Poppins", font_size=28,
             color=WHITE, weight=BOLD)
    bg = RoundedRectangle(
        corner_radius=0.2, width=t.width + 0.6, height=t.height + 0.3,
        fill_color=PURPLE, fill_opacity=1, stroke_width=0)
    bg.move_to(t)
    return VGroup(bg, t).to_corner(UL, buff=0.3)


def create_dimension(start, end, label_str, direction=DOWN, buff=0.3):
    arrow = DoubleArrow(start=start, end=end, color=PURPLE,
                        stroke_width=2, tip_length=0.2, buff=0)
    label = Text(label_str, font="Poppins", font_size=22, color=PURPLE)
    label.next_to(arrow.get_center(), direction, buff=0.15)
    return VGroup(arrow, label)


def create_unknown(position):
    return Text("?", font="Poppins", font_size=36,
                color=ORANGE_HL, weight=BOLD).move_to(position)


def math_obj(tex_str, color=PURPLE, font_size=36):
    return MathTex(tex_str,
                   tex_template=TexFontTemplates.gnu_freesans_tx,
                   color=color, font_size=font_size)


def _make_cosec_template():
    base = TexFontTemplates.gnu_freesans_tx
    t = TexTemplate(
        tex_compiler=base.tex_compiler,
        output_format=base.output_format,
        preamble=base.preamble,
        placeholder_text=base.placeholder_text,
    )
    t.add_to_preamble(r"\DeclareMathOperator{\cosec}{cosec}")
    return t

COSEC_TEMPLATE = _make_cosec_template()


def math_obj_cosec(tex_str, color=PURPLE, font_size=36):
    return MathTex(tex_str, tex_template=COSEC_TEMPLATE,
                   color=color, font_size=font_size)


def make_fraction(num_tex, den_tex, font_size=36, color=PURPLE):
    n = MathTex(num_tex, tex_template=TexFontTemplates.gnu_freesans_tx,
                font_size=font_size, color=color)
    d = MathTex(den_tex, tex_template=TexFontTemplates.gnu_freesans_tx,
                font_size=font_size, color=color)
    w = max(n.width, d.width) + 0.3
    bar = Line(LEFT * w / 2, RIGHT * w / 2, color=color, stroke_width=2.5)
    n.next_to(bar, UP, buff=0.15)
    d.next_to(bar, DOWN, buff=0.15)
    return VGroup(n, bar, d)


def make_overline_label(tex_str, font_size=36, color=PURPLE):
    lbl = MathTex(tex_str, tex_template=TexFontTemplates.gnu_freesans_tx,
                  font_size=font_size, color=color)
    bar = Line(lbl.get_corner(UL) + UP * 0.08,
               lbl.get_corner(UR) + UP * 0.08,
               color=color, stroke_width=2.5)
    return VGroup(lbl, bar)


def safe_math(tex_str, color=PURPLE, font_size=36, stroke_width=None):
    obj = math_obj(tex_str, color=color, font_size=font_size)
    if stroke_width:
        obj.set_stroke(width=stroke_width)
    return obj


def make_legend(entries, position=DR, buff=0.4):
    rows = []
    for var_tex, def_str in entries:
        v = MathTex(var_tex, tex_template=TexFontTemplates.gnu_freesans_tx,
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
    txt = Text(text_str, font="Poppins", font_size=font_size, color=PURPLE)
    bg = RoundedRectangle(
        corner_radius=0.2, width=min(txt.width + 0.8, 10.5),
        height=txt.height + 0.4, fill_color=WHITE, fill_opacity=0.85,
        stroke_color=PALE_PURPLE, stroke_width=1.5)
    bg.move_to(position)
    txt.move_to(bg.get_center())
    return VGroup(bg, txt)


def make_grid_overlay(w, h, cell=0.5, color=PALE_PURPLE):
    cols, rows_n = int(w / cell), int(h / cell)
    cells = VGroup()
    for r in range(rows_n):
        for c in range(cols):
            sq = Rectangle(width=cell, height=cell,
                           fill_color=color, fill_opacity=0.15,
                           stroke_color=PURPLE, stroke_width=0.5)
            sq.move_to(RIGHT * (c + 0.5) * cell + DOWN * (r + 0.5) * cell)
            cells.add(sq)
    cells.move_to(ORIGIN)
    return cells


def make_tape_diagram(total, active, cw=1.2, ch=0.8):
    blocks = VGroup()
    for i in range(total):
        is_a = i < active
        b = Rectangle(width=cw, height=ch, color=PURPLE,
                      stroke_width=2.5,
                      fill_color=ORANGE_HL if is_a else PALE_PURPLE,
                      fill_opacity=0.8 if is_a else 0.3)
        blocks.add(b)
    blocks.arrange(RIGHT, buff=0)
    if blocks.width > 8.0:
        blocks.scale(8.0 / blocks.width)
    top_br = Brace(VGroup(*list(blocks)[:active]), UP, color=ORANGE_HL)
    top_lbl = math_obj(str(active), color=ORANGE_HL,
                       font_size=28).next_to(top_br, UP, buff=0.1)
    bot_br = Brace(blocks, DOWN, color=PURPLE)
    bot_lbl = math_obj(str(total), font_size=28
                       ).next_to(bot_br, DOWN, buff=0.1)
    return {"blocks": blocks,
            "diagram": VGroup(blocks, top_br, top_lbl, bot_br, bot_lbl)}


def make_balance_scale():
    beam = Line(LEFT * 2.5, RIGHT * 2.5,
                color=PURPLE, stroke_width=3).shift(UP * 0.3)
    pivot = Dot(beam.get_center(), color=PURPLE, radius=0.08)
    post = Line(beam.get_center() + DOWN * 0.05,
                beam.get_center() + DOWN * 1,
                color=PURPLE, stroke_width=2.5)
    base = Line(post.get_bottom() + LEFT * 0.8,
                post.get_bottom() + RIGHT * 0.8,
                color=PURPLE, stroke_width=2.5)
    lp = Line(beam.get_left() + LEFT * 0.4 + DOWN * 0.4,
              beam.get_left() + RIGHT * 0.4 + DOWN * 0.4,
              color=PURPLE, stroke_width=3)
    rp = Line(beam.get_right() + LEFT * 0.4 + DOWN * 0.4,
              beam.get_right() + RIGHT * 0.4 + DOWN * 0.4,
              color=PURPLE, stroke_width=3)
    ls = Line(beam.get_left(), lp.get_center(),
              color=PURPLE, stroke_width=1.5)
    rs = Line(beam.get_right(), rp.get_center(),
              color=PURPLE, stroke_width=1.5)
    g = VGroup(beam, pivot, post, base, lp, rp, ls, rs)
    return {"scale_group": g, "beam": beam, "pivot": pivot,
            "left_anchor": lp.get_top() + UP * 0.35,
            "right_anchor": rp.get_top() + UP * 0.35}


def clear_and_transition(scene, active_mobs, new_bg,
                         ft=0.8, buf=0.2, settle=0.1):
    if active_mobs:
        scene.play(*[FadeOut(m) for m in active_mobs], run_time=ft)
    scene.wait(buf)
    scene.camera.background_color = new_bg
    scene.wait(settle)


SAFE_L, SAFE_R = -6.11, 6.11
SAFE_T, SAFE_B = 3.25, -3.25


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


def fit_stack_to_safe_area(vgroup):
    max_h = (SAFE_T - SAFE_B) - 0.5
    if vgroup.height > max_h:
        vgroup.scale_to_fit_height(max_h)
    return vgroup


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
            print(f"WARNING: '{name}' overlapped. Shifted UP by {shift_needed:.2f}")
        elif (new_bottom >= mob_top and
              (new_bottom - mob_top) < min_gap):
            shift_needed = min_gap - (new_bottom - mob_top)
            new_mob.shift(UP * shift_needed)
            print(f"WARNING: '{name}' too close. Shifted UP by {shift_needed:.2f}")
    return new_mob


def has_overlap(a, b, margin=0.15):
    return (a.get_left()[0] - margin   < b.get_right()[0] and
            a.get_right()[0] + margin  > b.get_left()[0]  and
            a.get_bottom()[1] - margin < b.get_top()[1]   and
            a.get_top()[1] + margin    > b.get_bottom()[1])


def resolve_overlaps(new_mob, active_mobs, name="new"):
    for mob in active_mobs:
        if isinstance(mob, VGroup) and len(mob) == 0:
            continue
        if has_overlap(new_mob, mob):
            shift_y = mob.get_bottom()[1] - new_mob.get_top()[1] - 0.2
            new_mob.shift(DOWN * abs(shift_y))
            if new_mob.get_bottom()[1] < SAFE_B:
                new_mob.shift(UP * abs(shift_y))
                shift_x = mob.get_right()[0] - new_mob.get_left()[0] + 0.3
                new_mob.shift(RIGHT * shift_x)
            print(f"OVERLAP FIX: {name} repositioned")
    clamp_to_safe_area(new_mob)
    return new_mob


def safe_fadein(scene, mob, active_mobs, name="obj", run_time=0.7):
    check_safe_margins(mob, name)
    check_y_gap(mob, active_mobs, name=name)
    resolve_overlaps(mob, active_mobs, name)
    scene.play(FadeIn(mob), run_time=run_time)
    active_mobs.append(mob)
    return mob


def safe_create(scene, mob, active_mobs, name="obj", run_time=1.0):
    check_safe_margins(mob, name)
    resolve_overlaps(mob, active_mobs, name)
    scene.play(Create(mob), run_time=run_time)
    active_mobs.append(mob)
    return mob


class StepManager:
    LIMITS = {(32, 0.4): 3, (28, 0.3): 4, (24, 0.25): 5, (20, 0.2): 6}

    def __init__(self, scene, start_anchor=None, font_size=28, buff=0.3):
        self.scene  = scene
        self.steps  = []
        self.fs     = font_size
        self.buff   = buff
        self.max    = self.LIMITS.get((font_size, buff), 4)
        self.anchor = start_anchor or (UP * 2.0 + LEFT * 3.5)

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
            self.scene.play(*[FadeOut(s) for s in self.steps],
                            run_time=rt)
            self.steps.clear()


class PickPatternsScene(VoiceoverScene):

    def construct(self):
        self._setup_tts()
        self.show_title()
        self.show_concept()
        self.show_question()
        self.show_solution()
        self.show_summary()

    def _setup_tts(self):
        self.set_speech_service(
            OpenAIService(
                voice="shimmer",
                model="gpt-4o-mini-tts",
                transcription_model="medium",
                instructions=TTS_INSTRUCTIONS,
            ),
            create_subcaption=False,
        )

    # ── TITLE ──────────────────────────────────────────────
    def show_title(self):
        active_mobs = []
        with self.voiceover(
            text='<bookmark mark="bk_hello"/>Hello students!'
        ) as tracker:
            self.wait_until_bookmark("bk_hello")
            self.camera.background_color = PURPLE
            topic = Text(
                "Pick Patterns and Reveal Relationships",
                font="Poppins", font_size=36, color=WHITE, weight=BOLD)
            topic.move_to(ORIGIN)
            check_safe_margins(topic, "title")
            self.play(FadeIn(topic), run_time=0.8)
            active_mobs.append(topic)
        self.wait(0.4)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── CONCEPT ────────────────────────────────────────────
    def show_concept(self):
        active_mobs = []
        badge = create_heading_badge("Concept")
        check_safe_margins(badge, "badge_concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        with self.voiceover(
            text=(
                'Think about days of the week. '
                'Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday '
                '— then back to Monday. '
                'If today is Monday and you want to know what day it will be in '
                '<bookmark mark="bk_thirty"/>thirty days, '
                'you would not count day by day all the way to thirty. '
                'You would use <bookmark mark="bk_cycle"/>the cycle. '
                'And the mathematical tool for this — is the remainder. '
                '<bookmark mark="bk_concept1"/>When a pattern repeats with a fixed cycle length '
                '— the number of elements in one complete cycle — '
                'we use division with remainders, to find any position quickly. '
                'The remainder after dividing the position number by the cycle length, '
                '<bookmark mark="bk_concept2"/>tells us exactly where we land within the cycle. '
                'For the days of the week, <bookmark mark="bk_seven"/>the cycle length is seven. '
                'Counting from Monday as position one, position thirty means '
                '<bookmark mark="bk_divide"/>we divide thirty by seven. '
                'Seven goes into thirty four times, '
                '<bookmark mark="bk_rem2"/>with a remainder of two. '
                'Remainder two points to <bookmark mark="bk_tuesday"/>the second element '
                'of the cycle — Tuesday. '
                'So thirty days from Monday — is a Tuesday. '
                'If the remainder is zero, <bookmark mark="bk_zero"/>we are at the last '
                'element of the cycle. '
                'A remainder of zero is a meaningful answer — never ignore it. '
                'This same idea is used when <bookmark mark="bk_timetable"/>timetables '
                'or duty rosters cycle through a fixed rotation.'
            )
        ) as tracker:
            # ── build week block row ──
            day_names   = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            day_colors  = [PURPLE] * 7
            week_blocks = VGroup()
            day_labels  = VGroup()
            for i, day in enumerate(day_names):
                blk = Rectangle(
                    width=0.9, height=0.7,
                    fill_color=PALE_PURPLE, fill_opacity=0.35,
                    stroke_color=PURPLE, stroke_width=2.5)
                lbl = Text(day, font="Poppins", font_size=16, color=PURPLE)
                week_blocks.add(blk)
                day_labels.add(lbl)
            week_blocks.arrange(RIGHT, buff=0.08)
            week_blocks.move_to(ORIGIN)
            for i, blk in enumerate(week_blocks):
                day_labels[i].move_to(blk.get_center())
            week_group = VGroup(week_blocks, day_labels)
            check_safe_margins(week_group, "week_group")
            self.play(Create(week_blocks), run_time=1.0)
            self.play(FadeIn(day_labels), run_time=0.5)
            active_mobs.append(week_group)

            # ── position 30 arrow ──
            self.wait_until_bookmark("bk_thirty")
            pos30_lbl = Text("Position 30", font="Poppins",
                             font_size=20, color=ORANGE_HL)
            pos30_lbl.move_to(week_group.get_top() + UP * 0.6)
            arr30 = Arrow(
                pos30_lbl.get_bottom(),
                week_group.get_top() + UP * 0.05,
                color=ORANGE_HL, stroke_width=2.5,
                tip_length=0.18, buff=0.05)
            check_safe_margins(pos30_lbl, "pos30_lbl")
            self.play(FadeIn(pos30_lbl), Create(arr30), run_time=0.7)
            active_mobs.append(pos30_lbl)
            active_mobs.append(arr30)

            # ── cycle card ──
            self.wait_until_bookmark("bk_cycle")
            card_cycle = make_concept_card(
                "You would use the cycle.",
                position=DOWN * 1.8, font_size=22)
            check_safe_margins(card_cycle, "card_cycle")
            self.play(FadeIn(card_cycle), run_time=0.6)
            active_mobs.append(card_cycle)

            # ── cycle length definition card ──
            self.wait_until_bookmark("bk_concept1")
            self.play(FadeOut(pos30_lbl), FadeOut(arr30),
                      FadeOut(card_cycle), run_time=0.5)
            active_mobs.remove(pos30_lbl)
            active_mobs.remove(arr30)
            active_mobs.remove(card_cycle)

            card_def = make_concept_card(
                "Cycle length = number of elements in one complete cycle",
                position=DOWN * 1.6, font_size=22)
            check_safe_margins(card_def, "card_def")
            self.play(FadeIn(card_def), run_time=0.7)
            active_mobs.append(card_def)

            # ── remainder rule card ──
            self.wait_until_bookmark("bk_concept2")
            card_rule = make_concept_card(
                "Remainder after (position / cycle length) = where we land",
                position=DOWN * 2.5, font_size=20)
            check_safe_margins(card_rule, "card_rule")
            self.play(FadeIn(card_rule), run_time=0.7)
            active_mobs.append(card_rule)

            # ── highlight cycle length 7 ──
            self.wait_until_bookmark("bk_seven")
            self.play(FadeOut(card_def), FadeOut(card_rule), run_time=0.5)
            active_mobs.remove(card_def)
            active_mobs.remove(card_rule)
            cycle_brace = Brace(week_blocks, DOWN, color=ORANGE_HL)
            cycle_lbl   = Text("Cycle length = 7", font="Poppins",
                               font_size=22, color=ORANGE_HL)
            cycle_lbl.next_to(cycle_brace, DOWN, buff=0.15)
            check_safe_margins(cycle_lbl, "cycle_lbl")
            self.play(Create(cycle_brace), FadeIn(cycle_lbl), run_time=0.7)
            active_mobs.append(cycle_brace)
            active_mobs.append(cycle_lbl)

            # ── division step: 30 ÷ 7 ──
            self.wait_until_bookmark("bk_divide")
            mgr_concept = StepManager(
                self, start_anchor=UP * 2.0 + LEFT * 1.0,
                font_size=28, buff=0.3)
            s_div = math_obj(r"30 \div 7", font_size=28)
            mgr_concept.add_step(s_div)
            active_mobs.append(s_div)

            # ── remainder result ──
            self.wait_until_bookmark("bk_rem2")
            s_rem = math_obj(
                r"= 4 \text{ whole and remainder } 2", font_size=28)
            mgr_concept.add_step(s_rem)
            active_mobs.append(s_rem)

            # ── highlight Tuesday block ──
            self.wait_until_bookmark("bk_tuesday")
            tue_block = week_blocks[1]
            self.play(tue_block.animate.set_fill(ORANGE_HL, opacity=0.8),
                      run_time=0.5)
            tue_arrow = Arrow(
                s_rem.get_right() + RIGHT * 0.1,
                tue_block.get_top(),
                color=ORANGE_HL, stroke_width=2.0,
                tip_length=0.15, buff=0.05)
            tue_lbl = Text("Tuesday", font="Poppins",
                           font_size=20, color=ORANGE_HL)
            tue_lbl.next_to(tue_block, UP, buff=0.25)
            check_safe_margins(tue_lbl, "tue_lbl")
            self.play(Create(tue_arrow), FadeIn(tue_lbl), run_time=0.7)
            active_mobs.append(tue_arrow)
            active_mobs.append(tue_lbl)
            self.wait(0.4)
            self.play(tue_block.animate.set_fill(PALE_PURPLE, opacity=0.35),
                      run_time=0.4)

            # ── zero remainder card ──
            self.wait_until_bookmark("bk_zero")
            self.play(FadeOut(tue_arrow), FadeOut(tue_lbl),
                      FadeOut(cycle_brace), FadeOut(cycle_lbl),
                      FadeOut(s_div), FadeOut(s_rem), run_time=0.6)
            for item in [tue_arrow, tue_lbl, cycle_brace,
                         cycle_lbl, s_div, s_rem]:
                if item in active_mobs:
                    active_mobs.remove(item)
            card_zero = make_concept_card(
                "Remainder 0 means the element is the last in the cycle.",
                position=DOWN * 1.5, font_size=22)
            check_safe_margins(card_zero, "card_zero")
            self.play(FadeIn(card_zero), run_time=0.7)
            active_mobs.append(card_zero)

            # ── timetable card ──
            self.wait_until_bookmark("bk_timetable")
            card_tt = make_concept_card(
                "Used in timetables and duty rosters.",
                position=DOWN * 2.4, font_size=22)
            check_safe_margins(card_tt, "card_tt")
            self.play(FadeIn(card_tt), run_time=0.6)
            active_mobs.append(card_tt)

        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── QUESTION ───────────────────────────────────────────
    def show_question(self):
        active_mobs = []
        badge = create_heading_badge("Question")
        check_safe_margins(badge, "badge_question")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        with self.voiceover(
            text=(
                '<bookmark mark="bk_question"/>A sequence of colours repeats: '
                'yellow, blue, green, red — then repeats. '
                'What colour appears at position <bookmark mark="bk_pos54"/>fifty-four?'
            )
        ) as tracker:
            self.wait_until_bookmark("bk_question")
            q_text = Text(
                "A sequence of colours repeats: yellow, blue, green, red.",
                font="Poppins", font_size=24, color=PURPLE)
            q_text.move_to(UP * 2.5)
            check_safe_margins(q_text, "q_text")
            self.play(FadeIn(q_text), run_time=0.7)
            active_mobs.append(q_text)

            q_text2 = Text(
                "What colour appears at position 54?",
                font="Poppins", font_size=24, color=PURPLE)
            q_text2.next_to(q_text, DOWN, buff=0.2)
            check_safe_margins(q_text2, "q_text2")
            self.play(FadeIn(q_text2), run_time=0.6)
            active_mobs.append(q_text2)

            # ── colour block sequence ──
            self.wait_until_bookmark("bk_pos54")
            col_names  = ["Yellow", "Blue", "Green", "Red"]
            col_fills  = ["#FFD600", "#1565C0", "#2E7D32", "#C62828"]
            col_blocks = VGroup()
            col_labels = VGroup()
            for i, (name, fill) in enumerate(zip(col_names, col_fills)):
                blk = Rectangle(
                    width=1.4, height=1.0,
                    fill_color=fill, fill_opacity=0.85,
                    stroke_color=PURPLE, stroke_width=2.5)
                lbl = Text(name, font="Poppins",
                           font_size=18, color=WHITE)
                col_blocks.add(blk)
                col_labels.add(lbl)
            col_blocks.arrange(RIGHT, buff=0.15)
            col_blocks.move_to(ORIGIN)
            for i, blk in enumerate(col_blocks):
                col_labels[i].move_to(blk.get_center())
            col_group = VGroup(col_blocks, col_labels)
            check_safe_margins(col_group, "col_group")
            self.play(Create(col_blocks), run_time=1.0)
            self.play(FadeIn(col_labels), run_time=0.5)
            active_mobs.append(col_group)

            pos54_lbl = Text("Position 54 = ?",
                             font="Poppins", font_size=24,
                             color=ORANGE_HL, weight=BOLD)
            pos54_lbl.move_to(DOWN * 1.8)
            check_safe_margins(pos54_lbl, "pos54_lbl")
            self.play(FadeIn(pos54_lbl), run_time=0.6)
            active_mobs.append(pos54_lbl)

        self._col_group  = col_group
        self._pos54_lbl  = pos54_lbl
        self._active_from_question = active_mobs

    # ── SOLUTION ───────────────────────────────────────────
    def show_solution(self):
        active_mobs = list(self._active_from_question)

        # shift figure to right
        col_group = self._col_group
        pos54_lbl = self._pos54_lbl
        self.play(
            col_group.animate.move_to(RIGHT * 3.2),
            pos54_lbl.animate.move_to(RIGHT * 3.2 + DOWN * 1.6),
            run_time=1.0)

        # swap badge
        badge_old = active_mobs[0]
        badge_new = create_heading_badge("Solution")
        self.play(FadeOut(badge_old), FadeIn(badge_new), run_time=0.5)
        active_mobs[0] = badge_new

        with self.voiceover(
            text=(
                '<bookmark mark="bk_s1"/>Cycle length is four. '
                '<bookmark mark="bk_s2"/>Divide fifty-four by four: '
                'thirteen groups of four, with a remainder of two. '
                '<bookmark mark="bk_s3"/>Remainder two corresponds to '
                'the second element — blue. '
                '<bookmark mark="bk_s4"/>The colour at position fifty-four is blue.'
            )
        ) as tracker:
            mgr = StepManager(
                self, start_anchor=UP * 2.0 + LEFT * 3.5,
                font_size=28, buff=0.3)

            # step 1
            self.wait_until_bookmark("bk_s1")
            s1 = math_obj(r"\text{Cycle length} = 4", font_size=28)
            mgr.add_step(s1)
            active_mobs.append(s1)

            # step 2
            self.wait_until_bookmark("bk_s2")
            s2 = math_obj(
                r"54 \div 4 = 13 \text{ whole and remainder } 2",
                font_size=24)
            mgr.add_step(s2)
            active_mobs.append(s2)

            # step 3 — highlight blue block
            self.wait_until_bookmark("bk_s3")
            s3 = math_obj(
                r"\text{Remainder } 2 \rightarrow \text{position } 2",
                font_size=28)
            mgr.add_step(s3)
            active_mobs.append(s3)
            col_blocks_obj = self._col_group[0]
            self.play(
                col_blocks_obj[1].animate.set_fill("#1565C0", opacity=1.0),
                col_blocks_obj[1].animate.set_stroke(color=ORANGE_HL,
                                                      width=4.0),
                run_time=0.6)

            # step 4 — final answer
            self.wait_until_bookmark("bk_s4")
            s4 = math_obj(
                r"\text{Position 54} = \textbf{Blue}",
                font_size=28, color=ORANGE_HL)
            mgr.add_step(s4)
            active_mobs.append(s4)

            # legend
            legend = make_legend(
                [("n", "= position number"),
                 ("c", "= cycle length"),
                 ("r", "= remainder")],
                position=DR, buff=0.4)
            check_safe_margins(legend, "legend")
            self.play(FadeIn(legend), run_time=0.7)
            active_mobs.append(legend)

        self.wait(0.6)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── SUMMARY ────────────────────────────────────────────
    def show_summary(self):
        active_mobs = []
        badge = create_heading_badge("Summary")
        check_safe_margins(badge, "badge_summary")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        summary_texts = [
            "Divide the position number by the cycle length to find the remainder.",
            "The remainder identifies the element's position within the cycle.",
            "A remainder of zero means the element is the last in the cycle.",
        ]
        positions = [UP * 1.5, ORIGIN, DOWN * 1.5]

        with self.voiceover(
            text=(
                '<bookmark mark="bk_sum1"/>Divide the position number '
                'by the cycle length to find the remainder. '
                '<bookmark mark="bk_sum2"/>The remainder identifies '
                'the element\'s position within the cycle. '
                '<bookmark mark="bk_sum3"/>A remainder of zero means '
                'the element is the last in the cycle.'
            )
        ) as tracker:
            for i, (txt, pos) in enumerate(
                    zip(summary_texts, positions)):
                self.wait_until_bookmark(f"bk_sum{i + 1}")
                card = make_concept_card(txt, position=pos, font_size=22)
                check_safe_margins(card, f"sum_card_{i}")
                self.play(FadeIn(card), run_time=0.7)
                active_mobs.append(card)

        self.wait(0.6)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()