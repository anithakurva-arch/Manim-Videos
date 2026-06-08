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
             color=WHITE)
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
                shift_x = (mob.get_right()[0]
                           - new_mob.get_left()[0] + 0.3)
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


# ══════════════════════════════════════════════════════════════
# HELPER — build a split algebraic expression row
# Returns dict of named term objects + the VGroup row
# ══════════════════════════════════════════════════════════════
def build_expr_row(terms, font_size=34):
    """
    terms: list of (key, latex_string) tuples
    Returns {"row": VGroup, key: MathTex, ...}
    """
    mobs = {}
    parts = []
    for key, tex in terms:
        mo = math_obj(tex, font_size=font_size)
        mobs[key] = mo
        parts.append(mo)
    row = VGroup(*parts).arrange(RIGHT, buff=0.18)
    mobs["row"] = row
    return mobs


class SimplificationScene(VoiceoverScene):

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
                "Simplification of Algebraic Expressions",
                font="Poppins", font_size=36,
                color=WHITE)
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
        self._concept_part_a(active_mobs)
        self._concept_part_b(active_mobs)
        self._concept_part_c(active_mobs)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    def _concept_part_a(self, active_mobs):
        """Hook + two properties intro."""
        with self.voiceover(
            text=(
                'Think about adding up your marks from different subjects. '
                'It does not matter what order you add them '
                '— the total stays the same. '
                'Whether you start with maths or English, '
                '<bookmark mark="bk_algebra"/>the answer does not change. '
                'In algebra, we do the same thing with terms. '
                '<bookmark mark="bk_two_props"/>We use two key properties '
                'to rearrange expressions.'
            )
        ) as tracker:
            hook = make_concept_card(
                "Adding marks in any order gives the same total.",
                position=UP * 0.5, font_size=24)
            check_safe_margins(hook, "hook_card")
            self.play(FadeIn(hook), run_time=0.7)
            active_mobs.append(hook)

            self.wait_until_bookmark("bk_algebra")
            alg_card = make_concept_card(
                "In algebra, we do the same thing with terms.",
                position=DOWN * 0.8, font_size=24)
            check_safe_margins(alg_card, "alg_card")
            self.play(FadeIn(alg_card), run_time=0.6)
            active_mobs.append(alg_card)

            self.wait_until_bookmark("bk_two_props")
            self.play(FadeOut(hook), FadeOut(alg_card), run_time=0.5)
            active_mobs.remove(hook)
            active_mobs.remove(alg_card)

            props_card = make_concept_card(
                "Two key properties let us rearrange expressions.",
                position=UP * 0.5, font_size=24)
            check_safe_margins(props_card, "props_card")
            self.play(FadeIn(props_card), run_time=0.6)
            active_mobs.append(props_card)

    def _concept_part_b(self, active_mobs):
        """Swapping and grouping properties with Pattern F."""
        with self.voiceover(
            text=(
                'The swapping property tells us that the order of terms '
                'does not affect the sum — '
                '<bookmark mark="bk_swap_ex"/>so five x plus three y, '
                'is the same as three y plus five x. '
                'The grouping property tells us we can regroup terms '
                'freely using brackets — '
                '<bookmark mark="bk_group_prop"/>the result stays unchanged. '
                'These two properties let us '
                '<bookmark mark="bk_move"/>move terms around, '
                'so that like terms end up next to each other. '
                'Once like terms are next to each other, '
                '<bookmark mark="bk_combine_easy"/>combining them becomes easy.'
            )
        ) as tracker:
            # clear props card first
            for m in list(active_mobs[1:]):
                self.play(FadeOut(m), run_time=0.4)
                active_mobs.remove(m)

            swap_card = make_concept_card(
                "Swapping property: order does not affect the sum.",
                position=UP * 1.6, font_size=24)
            check_safe_margins(swap_card, "swap_card")
            self.play(FadeIn(swap_card), run_time=0.6)
            active_mobs.append(swap_card)

            # Pattern F — 5x + 3y
            self.wait_until_bookmark("bk_swap_ex")
            e = build_expr_row([
                ("t1", r"5x"),
                ("op1", r"+"),
                ("t2", r"3y"),
                ("eq", r"="),
                ("t3", r"3y"),
                ("op2", r"+"),
                ("t4", r"5x"),
            ], font_size=32)
            e["row"].move_to(UP * 0.5)
            check_safe_margins(e["row"], "swap_expr")
            self.play(FadeIn(e["row"]), run_time=0.7)
            active_mobs.append(e["row"])
            # highlight left side
            self.play(
                e["t1"].animate.set_color(ORANGE_HL),
                e["t2"].animate.set_color(ORANGE_HL),
                run_time=0.5)
            self.wait(0.3)
            self.play(
                e["t1"].animate.set_color(PURPLE),
                e["t2"].animate.set_color(PURPLE),
                run_time=0.3)

            # grouping property card
            self.wait_until_bookmark("bk_group_prop")
            grp_card = make_concept_card(
                "Grouping property: brackets can be rearranged freely.",
                position=DOWN * 0.7, font_size=24)
            check_safe_margins(grp_card, "grp_card")
            self.play(FadeIn(grp_card), run_time=0.6)
            active_mobs.append(grp_card)

            # like terms goal card
            self.wait_until_bookmark("bk_move")
            self.play(
                FadeOut(e["row"]),
                FadeOut(swap_card),
                FadeOut(grp_card),
                run_time=0.5)
            for item in [e["row"], swap_card, grp_card]:
                if item in active_mobs:
                    active_mobs.remove(item)

            like_card = make_concept_card(
                "Move terms so like terms are next to each other.",
                position=UP * 0.5, font_size=24)
            check_safe_margins(like_card, "like_card")
            self.play(FadeIn(like_card), run_time=0.6)
            active_mobs.append(like_card)

            self.wait_until_bookmark("bk_combine_easy")
            easy_card = make_concept_card(
                "Once like terms are adjacent, combining becomes easy.",
                position=DOWN * 0.6, font_size=24)
            check_safe_margins(easy_card, "easy_card")
            self.play(FadeIn(easy_card), run_time=0.6)
            active_mobs.append(easy_card)

    def _concept_part_c(self, active_mobs):
        """Worked example: 2a+5b+3a+b using Pattern F."""
        with self.voiceover(
            text=(
                '<bookmark mark="bk_example"/>For example, take the expression '
                'two a plus five b plus three a plus b. '
                'We rearrange to place the a terms together '
                'and the b terms together: '
                '<bookmark mark="bk_rearrange"/>two a plus three a, '
                'plus five b plus b. '
                'Now we combine: two a plus three a is '
                '<bookmark mark="bk_five_a"/>five a, '
                'and five b plus b is six b. '
                'The simplified expression is '
                '<bookmark mark="bk_result"/>five a plus six b. '
                'Rearranging never changes the value of the expression — '
                '<bookmark mark="bk_echo"/>it simply makes simplification easier.'
            )
        ) as tracker:
            # clear previous cards
            to_clear = [m for m in active_mobs if m is not active_mobs[0]]
            if to_clear:
                self.play(*[FadeOut(m) for m in to_clear], run_time=0.5)
                for m in to_clear:
                    active_mobs.remove(m)

            # Pattern F — original expression: 2a + 5b + 3a + b
            self.wait_until_bookmark("bk_example")
            orig = build_expr_row([
                ("a1", r"2a"),
                ("p1", r"+"),
                ("b1", r"5b"),
                ("p2", r"+"),
                ("a2", r"3a"),
                ("p3", r"+"),
                ("b2", r"b"),
            ], font_size=32)
            orig["row"].move_to(UP * 1.5)
            check_safe_margins(orig["row"], "orig_expr")
            self.play(FadeIn(orig["row"]), run_time=0.8)
            active_mobs.append(orig["row"])

            # highlight a-terms then b-terms
            self.wait_until_bookmark("bk_rearrange")
            self.play(
                orig["a1"].animate.set_color(ORANGE_HL),
                orig["a2"].animate.set_color(ORANGE_HL),
                run_time=0.5)
            self.wait(0.25)
            self.play(
                orig["a1"].animate.set_color(PURPLE),
                orig["a2"].animate.set_color(PURPLE),
                run_time=0.3)
            self.play(
                orig["b1"].animate.set_color(ORANGE_HL),
                orig["b2"].animate.set_color(ORANGE_HL),
                run_time=0.5)
            self.wait(0.25)
            self.play(
                orig["b1"].animate.set_color(PURPLE),
                orig["b2"].animate.set_color(PURPLE),
                run_time=0.3)

            # rearranged row: 2a + 3a + 5b + b
            rearr = build_expr_row([
                ("ra1", r"2a"),
                ("rp1", r"+"),
                ("ra2", r"3a"),
                ("rp2", r"+"),
                ("rb1", r"5b"),
                ("rp3", r"+"),
                ("rb2", r"b"),
            ], font_size=32)
            rearr["row"].next_to(orig["row"], DOWN, buff=0.5)
            check_safe_margins(rearr["row"], "rearr_expr")
            self.play(FadeIn(rearr["row"]), run_time=0.7)
            active_mobs.append(rearr["row"])

            # combine a-terms in place
            self.wait_until_bookmark("bk_five_a")
            self.play(
                rearr["ra1"].animate.set_color(ORANGE_HL),
                rearr["ra2"].animate.set_color(ORANGE_HL),
                run_time=0.5)
            combined_a = math_obj(r"5a", color=ORANGE_HL, font_size=32)
            a_group = VGroup(rearr["ra1"], rearr["rp1"], rearr["ra2"])
            combined_a.move_to(a_group.get_center())
            self.play(
                ReplacementTransform(a_group, combined_a),
                run_time=0.7)
            active_mobs.append(combined_a)

            # combine b-terms in place
            self.play(
                rearr["rb1"].animate.set_color(ORANGE_HL),
                rearr["rb2"].animate.set_color(ORANGE_HL),
                run_time=0.5)
            combined_b = math_obj(r"6b", color=ORANGE_HL, font_size=32)
            b_group = VGroup(rearr["rb1"], rearr["rp3"], rearr["rb2"])
            combined_b.move_to(b_group.get_center())
            self.play(
                ReplacementTransform(b_group, combined_b),
                run_time=0.7)
            active_mobs.append(combined_b)

            # show final result below
            self.wait_until_bookmark("bk_result")
            result_row = build_expr_row([
                ("res_eq", r"="),
                ("res_5a", r"5a"),
                ("res_p",  r"+"),
                ("res_6b", r"6b"),
            ], font_size=34)
            result_row["res_5a"].set_color(ORANGE_HL)
            result_row["res_6b"].set_color(ORANGE_HL)
            result_row["row"].next_to(rearr["row"], DOWN, buff=0.45)
            check_safe_margins(result_row["row"], "result_row")
            self.play(FadeIn(result_row["row"]), run_time=0.7)
            active_mobs.append(result_row["row"])

            # echo closing card
            self.wait_until_bookmark("bk_echo")
            echo_card = make_concept_card(
                "Rearranging never changes the value"
                " — it makes simplification easier.",
                position=DOWN * 2.2, font_size=22)
            check_safe_margins(echo_card, "echo_card")
            self.play(FadeIn(echo_card), run_time=0.6)
            active_mobs.append(echo_card)

    # ── QUESTION ───────────────────────────────────────────
    def show_question(self):
        active_mobs = []
        badge = create_heading_badge("Question")
        check_safe_margins(badge, "badge_q")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        with self.voiceover(
            text=(
                '<bookmark mark="bk_question"/>Simplify four m plus nine n '
                'plus three m minus two n, '
                'by rearranging and grouping like terms.'
            )
        ) as tracker:
            self.wait_until_bookmark("bk_question")
            q1 = Text(
                "Simplify: 4m + 9n + 3m - 2n",
                font="Poppins", font_size=26, color=PURPLE)
            q1.move_to(UP * 2.5)
            check_safe_margins(q1, "q_text1")
            self.play(FadeIn(q1), run_time=0.7)
            active_mobs.append(q1)

            q2 = Text(
                "by rearranging and grouping like terms.",
                font="Poppins", font_size=24, color=PURPLE)
            q2.next_to(q1, DOWN, buff=0.2)
            check_safe_margins(q2, "q_text2")
            self.play(FadeIn(q2), run_time=0.6)
            active_mobs.append(q2)

            # Pattern F figure — question expression
            q_expr = build_expr_row([
                ("q4m",  r"4m"),
                ("qp1",  r"+"),
                ("q9n",  r"9n"),
                ("qp2",  r"+"),
                ("q3m",  r"3m"),
                ("qm",   r"-"),
                ("q2n",  r"2n"),
            ], font_size=32)
            q_expr["row"].move_to(ORIGIN)
            check_safe_margins(q_expr["row"], "q_expr")
            self.play(FadeIn(q_expr["row"]), run_time=0.8)
            active_mobs.append(q_expr["row"])

        self._q_expr_row  = q_expr["row"]
        self._active_from_question = active_mobs

    # ── SOLUTION ───────────────────────────────────────────
    def show_solution(self):
        active_mobs = list(self._active_from_question)

        # shift expression figure to right
        self.play(
            self._q_expr_row.animate.move_to(RIGHT * 3.2 + DOWN * 0.3),
            run_time=1.0)

        # swap badge
        badge_old = active_mobs[0]
        badge_new = create_heading_badge("Solution")
        self.play(FadeOut(badge_old), FadeIn(badge_new), run_time=0.5)
        active_mobs[0] = badge_new

        with self.voiceover(
            text=(
                '<bookmark mark="bk_s1"/>Rearrange: '
                'four m plus three m, plus nine n minus two n. '
                '<bookmark mark="bk_s2"/>Combine m terms: '
                'four m plus three m equals seven m. '
                '<bookmark mark="bk_s3"/>Combine n terms: '
                'nine n minus two n equals seven n. '
                '<bookmark mark="bk_s4"/>Simplified expression '
                'is seven m plus seven n.'
            )
        ) as tracker:
            mgr = StepManager(
                self,
                start_anchor=UP * 2.0 + LEFT * 3.5,
                font_size=28, buff=0.3)

            # step 1 — rearranged form
            self.wait_until_bookmark("bk_s1")
            s1 = math_obj(
                r"4m + 3m + 9n - 2n",
                font_size=28)
            s1.set_stroke(width=2.0)
            mgr.add_step(s1)
            active_mobs.append(s1)

            # step 2 — combine m
            self.wait_until_bookmark("bk_s2")
            s2 = math_obj(
                r"4m + 3m = 7m",
                font_size=28)
            s2.set_stroke(width=2.0)
            mgr.add_step(s2)
            active_mobs.append(s2)

            # step 3 — combine n
            self.wait_until_bookmark("bk_s3")
            s3 = math_obj(
                r"9n - 2n = 7n",
                font_size=28)
            s3.set_stroke(width=2.0)
            mgr.add_step(s3)
            active_mobs.append(s3)

            # step 4 — final answer
            self.wait_until_bookmark("bk_s4")
            s4 = math_obj(
                r"= 7m + 7n",
                font_size=28, color=ORANGE_HL)
            mgr.add_step(s4)
            active_mobs.append(s4)

            # legend
            legend = make_legend(
                [("m", "= first variable"),
                 ("n", "= second variable")],
                position=DR, buff=0.4)
            check_safe_margins(legend, "legend")
            self.play(FadeIn(legend), run_time=0.6)
            active_mobs.append(legend)

        self.wait(0.6)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── SUMMARY ────────────────────────────────────────────
    def show_summary(self):
        active_mobs = []
        badge = create_heading_badge("Summary")
        check_safe_margins(badge, "badge_sum")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        summary_points = [
            "The swapping property: terms can be added in any order.",
            "The grouping property: terms can be regrouped freely.",
            "Rearrange so like terms are next to each other,\nthen combine them.",
        ]
        positions = [UP * 1.5, ORIGIN, DOWN * 1.5]

        with self.voiceover(
            text=(
                '<bookmark mark="bk_sum1"/>The swapping property: '
                'terms can be added in any order. '
                '<bookmark mark="bk_sum2"/>The grouping property: '
                'terms can be regrouped freely. '
                '<bookmark mark="bk_sum3"/>Rearrange so like terms '
                'are next to each other, then combine them.'
            )
        ) as tracker:
            for i, (txt, pos) in enumerate(
                    zip(summary_points, positions)):
                self.wait_until_bookmark(f"bk_sum{i + 1}")
                bullet = make_bullet_point(txt, position=pos,
                                           font_size=24)
                check_safe_margins(bullet, f"bullet_{i}")
                self.play(FadeIn(bullet), run_time=0.7)
                active_mobs.append(bullet)

        self.wait(0.6)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()