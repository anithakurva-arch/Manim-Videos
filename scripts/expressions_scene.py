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

# ─── HELPER FUNCTIONS ────────────────────────────────────────────────────────

def create_heading_badge(text_str):
    t = Text(text_str, font="Poppins", font_size=28,
             color=WHITE)
    bg = RoundedRectangle(
        corner_radius=0.2, width=t.width+0.6, height=t.height+0.3,
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
                color=ORANGE_HL).move_to(position)


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
    bar = Line(LEFT*w/2, RIGHT*w/2, color=color, stroke_width=2.5)
    n.next_to(bar, UP, buff=0.15)
    d.next_to(bar, DOWN, buff=0.15)
    return VGroup(n, bar, d)


def make_overline_label(tex_str, font_size=36, color=PURPLE):
    lbl = MathTex(tex_str, tex_template=TexFontTemplates.gnu_freesans_tx,
                  font_size=font_size, color=color)
    bar = Line(lbl.get_corner(UL)+UP*0.08, lbl.get_corner(UR)+UP*0.08,
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
        corner_radius=0.15, width=content.width+0.4,
        height=content.height+0.3,
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
                lines.append(cur); cur = w
        if cur: lines.append(cur)
        text_str = "\n".join(lines)
    txt = Text(text_str, font="Poppins", font_size=font_size,
               color=PURPLE)
    bg = RoundedRectangle(
        corner_radius=0.2, width=min(txt.width+0.8, 10.5),
        height=txt.height+0.4, fill_color=WHITE, fill_opacity=0.85,
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
    row = VGroup(dot, txt).arrange(RIGHT, buff=0.25,
                                   aligned_edge=UP)
    row.move_to(position)
    return row


def make_grid_overlay(w, h, cell=0.5, color=PALE_PURPLE):
    cols, rows_n = int(w/cell), int(h/cell)
    cells = VGroup()
    for r in range(rows_n):
        for c in range(cols):
            sq = Rectangle(width=cell, height=cell,
                          fill_color=color, fill_opacity=0.15,
                          stroke_color=PURPLE, stroke_width=0.5)
            sq.move_to(RIGHT*(c+0.5)*cell + DOWN*(r+0.5)*cell)
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
            "diagram": VGroup(blocks, top_br, top_lbl,
                              bot_br, bot_lbl)}


def make_balance_scale():
    beam = Line(LEFT*2.5, RIGHT*2.5,
                color=PURPLE, stroke_width=3).shift(UP*0.3)
    pivot = Dot(beam.get_center(), color=PURPLE, radius=0.08)
    post = Line(beam.get_center()+DOWN*0.05,
                beam.get_center()+DOWN*1,
                color=PURPLE, stroke_width=2.5)
    base = Line(post.get_bottom()+LEFT*0.8,
                post.get_bottom()+RIGHT*0.8,
                color=PURPLE, stroke_width=2.5)
    lp = Line(beam.get_left()+LEFT*0.4+DOWN*0.4,
              beam.get_left()+RIGHT*0.4+DOWN*0.4,
              color=PURPLE, stroke_width=3)
    rp = Line(beam.get_right()+LEFT*0.4+DOWN*0.4,
              beam.get_right()+RIGHT*0.4+DOWN*0.4,
              color=PURPLE, stroke_width=3)
    ls = Line(beam.get_left(), lp.get_center(),
              color=PURPLE, stroke_width=1.5)
    rs = Line(beam.get_right(), rp.get_center(),
              color=PURPLE, stroke_width=1.5)
    g = VGroup(beam, pivot, post, base, lp, rp, ls, rs)
    return {"scale_group": g, "beam": beam, "pivot": pivot,
            "left_anchor":  lp.get_top()+UP*0.35,
            "right_anchor": rp.get_top()+UP*0.35}


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
    if sx or sy: mob.shift(RIGHT*sx + UP*sy)
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
            print(f"WARNING: '{name}' overlapped. "
                  f"Shifted UP by {shift_needed:.2f}")
        elif (new_bottom >= mob_top and
              (new_bottom - mob_top) < min_gap):
            shift_needed = min_gap - (new_bottom - mob_top)
            new_mob.shift(UP * shift_needed)
            print(f"WARNING: '{name}' too close. "
                  f"Shifted UP by {shift_needed:.2f}")
    return new_mob


def has_overlap(a, b, margin=0.15):
    return (a.get_left()[0]-margin   < b.get_right()[0] and
            a.get_right()[0]+margin  > b.get_left()[0]  and
            a.get_bottom()[1]-margin < b.get_top()[1]   and
            a.get_top()[1]+margin    > b.get_bottom()[1])


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
    LIMITS = {(32,0.4):3, (28,0.3):4, (24,0.25):5, (20,0.2):6}

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
            self.scene.play(*[FadeOut(s) for s in self.steps],
                            run_time=rt)
            self.steps.clear()


# ─── MAIN SCENE ──────────────────────────────────────────────────────────────

class ExpressionsScene(VoiceoverScene):

    def construct(self):
        self._setup_tts()
        self.show_title()
        self.show_concept_hook()
        self.show_concept_terms()
        self.show_concept_evaluate()
        self.show_concept_order()
        self.show_question()
        self.show_solution()
        self.show_summary()

    # ── TTS SETUP ────────────────────────────────────────────────────────────

    def _setup_tts(self):
        self.set_speech_service(
            OpenAIService(
                voice="shimmer",
                model="gpt-4o-mini-tts",
                instructions=TTS_INSTRUCTIONS,
            )
        )

    # ── TITLE ────────────────────────────────────────────────────────────────

    def show_title(self):
        active_mobs = []
        self.camera.background_color = PURPLE

        with self.voiceover(
            text='<bookmark mark="bk_title"/>Expressions Using Letter Numbers.'
        ) as tracker:
            self.wait_until_bookmark("bk_title")
            topic = Text(
                "Expressions Using Letter Numbers",
                font="Poppins", font_size=48, color=WHITE
            )
            topic.move_to(ORIGIN)
            check_safe_margins(topic, "topic_title")
            self.play(FadeIn(topic), run_time=0.8)
            active_mobs.append(topic)

        self.wait(0.4)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── CONCEPT — SHELF HOOK ─────────────────────────────────────────────────

    def show_concept_hook(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        with self.voiceover(
            text=(
                '<bookmark mark="bk_shelf"/>Suppose you want to find the total'
                ' number of items, on three shelves. '
                'The first shelf has eight items. '
                'The second has two boxes, with five items each. '
                'The third shelf has three items. '
                '<bookmark mark="bk_evaluate_need"/>Before you can find the'
                ' total, you need to work out how many items are on the'
                ' second shelf. '
                'You cannot just count boxes — you must evaluate the box'
                ' contents first. '
                '<bookmark mark="bk_same_way"/>Expressions in arithmetic,'
                ' work exactly the same way.'
            )
        ) as tracker:

            # ── Three shelf cards ─────────────────────────────────────────
            self.wait_until_bookmark("bk_shelf")

            card1 = make_concept_card(
                "Shelf 1:  8 items", position=LEFT*2.5 + UP*1.2,
                font_size=24
            )
            check_safe_margins(card1, "card1")
            self.play(FadeIn(card1), run_time=0.6)
            active_mobs.append(card1)

            card2 = make_concept_card(
                "Shelf 2:  2 boxes x 5 items", position=LEFT*2.5 + ORIGIN,
                font_size=24
            )
            check_safe_margins(card2, "card2")
            self.play(FadeIn(card2), run_time=0.6)
            active_mobs.append(card2)

            card3 = make_concept_card(
                "Shelf 3:  3 items", position=LEFT*2.5 + DOWN*1.2,
                font_size=24
            )
            check_safe_margins(card3, "card3")
            self.play(FadeIn(card3), run_time=0.6)
            active_mobs.append(card3)

            # ── Highlight shelf 2 ─────────────────────────────────────────
            self.wait_until_bookmark("bk_evaluate_need")
            self.play(
                card2[1].animate.set_color(ORANGE_HL),
                run_time=0.5
            )
            self.wait(0.3)
            self.play(
                card2[1].animate.set_color(PURPLE),
                run_time=0.3
            )

            # ── Bridge card ───────────────────────────────────────────────
            self.wait_until_bookmark("bk_same_way")
            bridge = make_concept_card(
                "Expressions work exactly the same way.",
                position=RIGHT*2.0 + UP*0.2,
                font_size=24
            )
            check_safe_margins(bridge, "bridge")
            self.play(FadeIn(bridge), run_time=0.7)
            active_mobs.append(bridge)

        self.wait(0.4)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── CONCEPT — IDENTIFYING TERMS ──────────────────────────────────────────

    def show_concept_terms(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        # Build expression as separate MathTex objects (Pattern F)
        t1  = math_obj(r"23",            font_size=44)
        op  = math_obj(r"-",             font_size=44)
        t2a = math_obj(r"10",            font_size=44)
        t2b = math_obj(r"\times",        font_size=44)
        t2c = math_obj(r"2",             font_size=44)

        t2_group = VGroup(t2a, t2b, t2c).arrange(RIGHT, buff=0.08)
        expr_row = VGroup(t1, op, t2_group).arrange(RIGHT, buff=0.2)
        expr_row.move_to(UP * 0.5)
        check_safe_margins(expr_row, "expr_row")

        with self.voiceover(
            text=(
                '<bookmark mark="bk_expression_def"/>An expression is made up'
                ' of individual terms, separated by addition or subtraction. '
                '<bookmark mark="bk_first_skill"/>The first skill is'
                ' identifying each term clearly. '
                '<bookmark mark="bk_expr_show"/>In the expression'
                ' twenty-three minus ten times two,'
                ' <bookmark mark="bk_terms_are"/>the terms are twenty-three,'
                ' and ten times two. '
                '<bookmark mark="bk_separated"/>Each is separated by a'
                ' subtraction sign.'
            )
        ) as tracker:

            # ── Show full expression ──────────────────────────────────────
            self.wait_until_bookmark("bk_expression_def")
            self.play(FadeIn(expr_row), run_time=0.8)
            active_mobs.append(expr_row)

            # Caption: terms separated by + or −
            caption = Text(
                "Terms are separated by + or \u2212",
                font="Poppins", font_size=22, color=PURPLE
            )
            caption.move_to(DOWN * 2.5)
            check_safe_margins(caption, "caption")
            self.play(FadeIn(caption), run_time=0.6)
            active_mobs.append(caption)

            # ── First skill label ─────────────────────────────────────────
            self.wait_until_bookmark("bk_first_skill")
            skill_card = make_concept_card(
                "Skill 1: Identify each term",
                position=DOWN * 1.6,
                font_size=24
            )
            check_safe_margins(skill_card, "skill_card")
            self.play(FadeIn(skill_card), run_time=0.6)
            active_mobs.append(skill_card)

            # ── Highlight t1 (23) ─────────────────────────────────────────
            self.wait_until_bookmark("bk_expr_show")
            self.play(t1.animate.set_color(ORANGE_HL), run_time=0.5)
            self.wait(0.5)

            # ── Highlight t2_group (10×2) ─────────────────────────────────
            self.wait_until_bookmark("bk_terms_are")
            self.play(
                t1.animate.set_color(PURPLE),
                t2_group.animate.set_color(ORANGE_HL),
                run_time=0.5
            )
            self.wait(0.5)
            self.play(t2_group.animate.set_color(PURPLE), run_time=0.3)

            # ── Highlight minus sign ──────────────────────────────────────
            self.wait_until_bookmark("bk_separated")
            self.play(op.animate.set_color(ORANGE_HL), run_time=0.5)

            # Arrow from minus downward
            arrow_minus = Arrow(
                op.get_bottom() + DOWN*0.05,
                op.get_bottom() + DOWN*0.7,
                color=ORANGE_HL, stroke_width=2.5,
                tip_length=0.18, buff=0
            )
            check_safe_margins(arrow_minus, "arrow_minus")
            self.play(FadeIn(arrow_minus), run_time=0.4)
            active_mobs.append(arrow_minus)

            self.wait(0.4)
            self.play(
                op.animate.set_color(PURPLE),
                run_time=0.3
            )

        self.wait(0.4)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── CONCEPT — EVALUATING TERMS ───────────────────────────────────────────

    def show_concept_evaluate(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        # Rebuild expression (Pattern F) for this slide
        t1   = math_obj(r"23",      font_size=44)
        op   = math_obj(r"-",       font_size=44)
        t2a  = math_obj(r"10",      font_size=44)
        t2b  = math_obj(r"\times",  font_size=44)
        t2c  = math_obj(r"2",       font_size=44)
        t2_group = VGroup(t2a, t2b, t2c).arrange(RIGHT, buff=0.08)

        expr_row = VGroup(t1, op, t2_group).arrange(RIGHT, buff=0.2)
        expr_row.move_to(UP * 1.5)
        check_safe_margins(expr_row, "expr_row_eval")

        with self.voiceover(
            text=(
                '<bookmark mark="bk_second_skill"/>The second skill is'
                ' evaluating non-numerical terms — those that involve a'
                ' product — before combining. '
                '<bookmark mark="bk_ten_times_two"/>Ten times two is a term,'
                ' and its value is twenty. '
                '<bookmark mark="bk_becomes"/>Once evaluated, the expression'
                ' becomes twenty-three minus twenty,'
                ' <bookmark mark="bk_equals_three"/>which equals three.'
            )
        ) as tracker:

            # ── Show expression ───────────────────────────────────────────
            self.wait_until_bookmark("bk_second_skill")
            self.play(FadeIn(expr_row), run_time=0.8)
            active_mobs.append(expr_row)

            skill2_card = make_concept_card(
                "Skill 2: Evaluate non-numerical terms first",
                position=DOWN * 1.6,
                font_size=24
            )
            check_safe_margins(skill2_card, "skill2_card")
            self.play(FadeIn(skill2_card), run_time=0.6)
            active_mobs.append(skill2_card)

            # ── Highlight t2_group, then replace with 20 ─────────────────
            self.wait_until_bookmark("bk_ten_times_two")
            self.play(t2_group.animate.set_color(ORANGE_HL), run_time=0.5)
            self.wait(0.3)

            t2_val = math_obj(r"20", font_size=44, color=ORANGE_HL)
            t2_val.move_to(t2_group.get_center())
            self.play(
                ReplacementTransform(t2_group, t2_val),
                run_time=0.7
            )
            # Update expr_row components (t2_group is now gone,
            # t2_val is in scene at same position)
            active_mobs.append(t2_val)

            self.wait(0.3)

            # ── Show new expression line ───────────────────────────────────
            self.wait_until_bookmark("bk_becomes")

            # Build "= 23 - 20" row below
            eq_lbl   = math_obj(r"=",    font_size=40)
            n23      = math_obj(r"23",   font_size=40)
            minus2   = math_obj(r"-",    font_size=40)
            n20      = math_obj(r"20",   font_size=40)
            step_row = VGroup(eq_lbl, n23, minus2, n20).arrange(
                RIGHT, buff=0.15
            )
            step_row.next_to(expr_row, DOWN, buff=0.5)
            check_safe_margins(step_row, "step_row")
            self.play(FadeIn(step_row), run_time=0.7)
            active_mobs.append(step_row)

            # ── Show result ───────────────────────────────────────────────
            self.wait_until_bookmark("bk_equals_three")
            result = math_obj(r"= 3", font_size=44, color=ORANGE_HL)
            result.next_to(step_row, DOWN, buff=0.4)
            check_safe_margins(result, "result")
            self.play(FadeIn(result), run_time=0.7)
            active_mobs.append(result)

        self.wait(0.5)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── CONCEPT — ORDER OF OPERATIONS ────────────────────────────────────────

    def show_concept_order(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        with self.voiceover(
            text=(
                '<bookmark mark="bk_never"/>We must never combine terms,'
                ' before fully evaluating each one. '
                '<bookmark mark="bk_if_mult"/>If a term contains a'
                ' multiplication, evaluate that first. '
                '<bookmark mark="bk_order_ops"/>This is directly connected'
                ' to the order of operations.'
            )
        ) as tracker:

            # ── Pattern C: LEFT = WRONG, RIGHT = CORRECT ──────────────────
            self.wait_until_bookmark("bk_never")

            # WRONG side — combine before evaluating
            wrong_label = Text(
                "Wrong", font="Poppins", font_size=22,
                color=WHITE
            )
            wrong_bg = RoundedRectangle(
                corner_radius=0.15,
                width=wrong_label.width + 0.5,
                height=wrong_label.height + 0.25,
                fill_color=RED, fill_opacity=0.85,
                stroke_width=0
            )
            wrong_bg.move_to(LEFT*3.2 + UP*1.5)
            wrong_label.move_to(wrong_bg.get_center())
            wrong_badge = VGroup(wrong_bg, wrong_label)

            wrong_expr_a = math_obj(r"23 - 10", font_size=34, color=RED)
            wrong_expr_a.next_to(wrong_bg, DOWN, buff=0.25)
            wrong_expr_b = math_obj(r"\times 2", font_size=34, color=RED)
            wrong_expr_b.next_to(wrong_expr_a, DOWN, buff=0.12)
            wrong_note = Text(
                "Combine first — WRONG",
                font="Poppins", font_size=20, color=RED
            )
            wrong_note.next_to(wrong_expr_b, DOWN, buff=0.18)
            wrong_group = VGroup(
                wrong_badge, wrong_expr_a, wrong_expr_b, wrong_note
            )
            check_safe_margins(wrong_group, "wrong_group")

            # CORRECT side — evaluate product first
            right_label = Text(
                "Correct", font="Poppins", font_size=22,
                color=WHITE
            )
            right_bg = RoundedRectangle(
                corner_radius=0.15,
                width=right_label.width + 0.5,
                height=right_label.height + 0.25,
                fill_color="#2E8B57", fill_opacity=0.9,
                stroke_width=0
            )
            right_bg.move_to(RIGHT*2.2 + UP*1.5)
            right_label.move_to(right_bg.get_center())
            right_badge = VGroup(right_bg, right_label)

            right_expr_a = math_obj(
                r"10 \times 2 = 20", font_size=34, color="#2E8B57"
            )
            right_expr_a.next_to(right_bg, DOWN, buff=0.25)
            right_expr_b = math_obj(
                r"23 - 20 = 3", font_size=34, color="#2E8B57"
            )
            right_expr_b.next_to(right_expr_a, DOWN, buff=0.12)
            right_note = Text(
                "Evaluate first — CORRECT",
                font="Poppins", font_size=20, color="#2E8B57"
            )
            right_note.next_to(right_expr_b, DOWN, buff=0.18)
            right_group = VGroup(
                right_badge, right_expr_a, right_expr_b, right_note
            )
            check_safe_margins(right_group, "right_group")

            self.play(FadeIn(wrong_group), run_time=0.8)
            active_mobs.append(wrong_group)
            self.play(FadeIn(right_group), run_time=0.8)
            active_mobs.append(right_group)

            # ── Pattern B: Arrow from product → evaluated value ───────────
            self.wait_until_bookmark("bk_if_mult")
            self.play(
                right_expr_a.animate.set_color(ORANGE_HL),
                run_time=0.5
            )
            self.wait(0.4)
            self.play(
                right_expr_a.animate.set_color("#2E8B57"),
                run_time=0.3
            )

            # ── Pattern E: Order of operations echo card ──────────────────
            self.wait_until_bookmark("bk_order_ops")
            ooo_card = make_concept_card(
                "Order of Operations",
                position=DOWN * 2.2,
                font_size=26
            )
            check_safe_margins(ooo_card, "ooo_card")
            self.play(FadeIn(ooo_card), run_time=0.7)
            active_mobs.append(ooo_card)

        self.wait(0.5)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── QUESTION ─────────────────────────────────────────────────────────────

    def show_question(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Question")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        with self.voiceover(
            text=(
                '<bookmark mark="bk_question"/>Evaluate the expression,'
                ' five plus four times three,'
                ' minus two times six.'
            )
        ) as tracker:

            self.wait_until_bookmark("bk_question")

            q_text = Text(
                "Evaluate the expression:",
                font="Poppins", font_size=28, color=PURPLE
            )
            q_text.move_to(UP * 2.8)
            check_safe_margins(q_text, "q_text")
            self.play(FadeIn(q_text), run_time=0.6)
            active_mobs.append(q_text)

            # Pattern F: split expression into addressable parts
            qt1  = math_obj(r"5",           font_size=44)
            qop1 = math_obj(r"+",           font_size=44)
            qt2a = math_obj(r"4",           font_size=44)
            qt2b = math_obj(r"\times",      font_size=44)
            qt2c = math_obj(r"3",           font_size=44)
            qop2 = math_obj(r"-",           font_size=44)
            qt3a = math_obj(r"2",           font_size=44)
            qt3b = math_obj(r"\times",      font_size=44)
            qt3c = math_obj(r"6",           font_size=44)

            qt2_group = VGroup(qt2a, qt2b, qt2c).arrange(RIGHT, buff=0.08)
            qt3_group = VGroup(qt3a, qt3b, qt3c).arrange(RIGHT, buff=0.08)
            q_expr = VGroup(
                qt1, qop1, qt2_group, qop2, qt3_group
            ).arrange(RIGHT, buff=0.18)
            q_expr.move_to(ORIGIN)
            check_safe_margins(q_expr, "q_expr")

            self.play(FadeIn(q_expr), run_time=0.8)
            active_mobs.append(q_expr)

            # Store for solution
            self._q_expr       = q_expr
            self._q_expr_parts = (
                qt1, qop1, qt2_group, qop2, qt3_group,
                qt2a, qt2b, qt2c, qt3a, qt3b, qt3c
            )

        self._active_from_question = list(active_mobs)
        self._q_badge = badge
        # Keep screen populated — solution will clear

    # ── SOLUTION ─────────────────────────────────────────────────────────────

    def show_solution(self):
        active_mobs = list(self._active_from_question)

        # Swap badge: Question → Solution
        sol_badge = create_heading_badge("Solution")
        self.play(
            FadeOut(self._q_badge),
            FadeIn(sol_badge),
            run_time=0.5
        )
        active_mobs[0] = sol_badge

        # Shift question expression to right zone
        q_expr = self._q_expr
        self.play(
            q_expr.animate.move_to(RIGHT * 3.2 + UP * 1.0),
            run_time=1.0
        )

        # ── Stack height pre-computation ──────────────────────────────────
        # 5 steps, font_size=24, buff=0.25
        # height ≈ 5 × (0.38 + 0.25) = 3.15 units  ✓
        # StepManager LIMITS[(24, 0.25)] = 5  ✓

        with self.voiceover(
            text=(
                '<bookmark mark="bk_identify"/>Identify the terms — five,'
                ' four times three, and two times six. '
                '<bookmark mark="bk_eval_first"/>Evaluate — four times three'
                ' equals twelve. '
                '<bookmark mark="bk_eval_second"/>Two times six equals'
                ' twelve. '
                '<bookmark mark="bk_becomes_sol"/>Expression becomes five'
                ' plus twelve, minus twelve. '
                '<bookmark mark="bk_final"/>Final answer is five.'
            )
        ) as tracker:

            mgr = StepManager(
                self,
                start_anchor=UP * 2.0 + LEFT * 3.5,
                font_size=24, buff=0.25
            )

            # ── Step 1: identify terms ────────────────────────────────────
            self.wait_until_bookmark("bk_identify")

            # Highlight each term group on the expression
            qt1, qop1, qt2_group, qop2, qt3_group = (
                self._q_expr_parts[0],
                self._q_expr_parts[1],
                self._q_expr_parts[2],
                self._q_expr_parts[3],
                self._q_expr_parts[4],
            )

            self.play(qt1.animate.set_color(ORANGE_HL), run_time=0.4)
            self.wait(0.2)
            self.play(
                qt1.animate.set_color(PURPLE),
                qt2_group.animate.set_color(ORANGE_HL),
                run_time=0.4
            )
            self.wait(0.2)
            self.play(
                qt2_group.animate.set_color(PURPLE),
                qt3_group.animate.set_color(ORANGE_HL),
                run_time=0.4
            )
            self.wait(0.2)
            self.play(qt3_group.animate.set_color(PURPLE), run_time=0.3)

            s1 = math_obj(
                r"\text{Terms: } 5, \; 4\times3, \; 2\times6",
                font_size=24
            )
            mgr.add_step(s1)
            active_mobs.append(s1)

            # ── Step 2: 4 × 3 = 12 ───────────────────────────────────────
            self.wait_until_bookmark("bk_eval_first")
            self.play(qt2_group.animate.set_color(ORANGE_HL), run_time=0.4)

            s2 = math_obj(r"4 \times 3 = 12", font_size=24)
            mgr.add_step(s2)
            active_mobs.append(s2)
            self.play(qt2_group.animate.set_color(PURPLE), run_time=0.3)

            # ── Step 3: 2 × 6 = 12 ───────────────────────────────────────
            self.wait_until_bookmark("bk_eval_second")
            self.play(qt3_group.animate.set_color(ORANGE_HL), run_time=0.4)

            s3 = math_obj(r"2 \times 6 = 12", font_size=24)
            mgr.add_step(s3)
            active_mobs.append(s3)
            self.play(qt3_group.animate.set_color(PURPLE), run_time=0.3)

            # ── Step 4: expression becomes 5 + 12 − 12 ───────────────────
            self.wait_until_bookmark("bk_becomes_sol")
            s4 = math_obj(r"5 + 12 - 12", font_size=24)
            mgr.add_step(s4)
            active_mobs.append(s4)

            # ── Step 5: final answer ──────────────────────────────────────
            self.wait_until_bookmark("bk_final")
            s5 = math_obj(r"= 5", font_size=28, color=ORANGE_HL)
            mgr.add_step(s5)
            active_mobs.append(s5)

        self.wait(0.8)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── SUMMARY ──────────────────────────────────────────────────────────────

    def show_summary(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Summary")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        summary_points = [
            "Identify each term in the expression before calculating.",
            "Evaluate non-numerical terms — those involving products — first.",
            "Only combine terms after every individual term has been fully evaluated.",
        ]
        positions = [UP * 1.5, ORIGIN, DOWN * 1.5]

        with self.voiceover(
            text=(
                '<bookmark mark="bk_sum1"/>Identify each term in the'
                ' expression before calculating. '
                '<bookmark mark="bk_sum2"/>Evaluate non-numerical terms'
                ' — those involving products — first. '
                '<bookmark mark="bk_sum3"/>Only combine terms after every'
                ' individual term has been fully evaluated.'
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