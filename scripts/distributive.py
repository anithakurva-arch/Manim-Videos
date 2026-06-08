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


def math_obj(tex_str, color=PURPLE, font_size=36):
    return MathTex(tex_str,
                   tex_template=TexFontTemplates.gnu_freesans_tx,
                   color=color, font_size=font_size)


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


def check_y_gap(new_mob, existing_mobs, min_gap=0.3, name="new_mob"):
    for mob in existing_mobs:
        if isinstance(mob, VGroup) and len(mob) == 0:
            continue
        new_bottom = new_mob.get_bottom()[1]
        new_top    = new_mob.get_top()[1]
        mob_top    = mob.get_top()[1]
        mob_bottom = mob.get_bottom()[1]
        if new_bottom < mob_top and new_top > mob_bottom:
            shift_needed = mob_top + min_gap - new_bottom
            new_mob.shift(UP * shift_needed)
        elif new_bottom >= mob_top and (new_bottom - mob_top) < min_gap:
            shift_needed = min_gap - (new_bottom - mob_top)
            new_mob.shift(UP * shift_needed)
    return new_mob


def build_expr_row(terms, font_size=32):
    mobs = {}
    parts = []
    for key, tex in terms:
        mo = math_obj(tex, font_size=font_size)
        mobs[key] = mo
        parts.append(mo)
    row = VGroup(*parts).arrange(RIGHT, buff=0.18)
    mobs["row"] = row
    return mobs


class StepManager:
    LIMITS = {(32, 0.4): 3, (28, 0.3): 4, (24, 0.25): 5, (20, 0.2): 6}

    def __init__(self, scene, start_anchor=None,
                 font_size=24, buff=0.25):
        self.scene  = scene
        self.steps  = []
        self.fs     = font_size
        self.buff   = buff
        self.max    = self.LIMITS.get((font_size, buff), 5)
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

    def fadeout_all(self, rt=0.8):
        if self.steps:
            self.scene.play(*[FadeOut(s) for s in self.steps],
                            run_time=rt)
            self.steps.clear()

    def get_all(self):
        return VGroup(*self.steps)


class DistributivePropertyScene(VoiceoverScene):

    def construct(self):
        self._setup_tts()
        self.show_title()
        self.show_hook()
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
                font="Poppins", font_size=34,
                color=WHITE)
            topic.move_to(ORIGIN)
            check_safe_margins(topic, "title")
            self.play(FadeIn(topic), run_time=0.8)
            active_mobs.append(topic)
        self.wait(0.4)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── HOOK — RECTANGLE ANCHOR ─────────────────────────────
    def show_hook(self):
        active_mobs = []
        badge = create_heading_badge("Concept")
        check_safe_margins(badge, "badge_hook")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        with self.voiceover(
            text=(
                'Imagine a large rectangle split into two smaller '
                'rectangles side by side. '
                'One smaller rectangle has width four and the other '
                'has width three, '
                '<bookmark mark="bk_rect"/>and both share the same height, v. '
                'You can find the total area in two ways: '
                '<bookmark mark="bk_way1"/>multiply v by the full width '
                'of seven, giving seven v. '
                'Or add the two smaller areas: '
                '<bookmark mark="bk_way2"/>four v plus three v, '
                'which also gives seven v. '
                'Both methods agree — '
                '<bookmark mark="bk_agree"/>and that agreement is '
                'the distributive property in action.'
            )
        ) as tracker:

            # ── build scaled rectangle that fits safe area ──
            SCALE   = 0.82          # 7 raw units × 0.82 = 5.74 wide
            RW      = 7.0 * SCALE   # total width  ≈ 5.74
            RH      = 2.0           # height
            LW      = 4.0 * SCALE   # left section ≈ 3.28
            RightW  = 3.0 * SCALE   # right section ≈ 2.46

            big_rect = Rectangle(
                width=RW, height=RH,
                color=PURPLE, stroke_width=3.0,
                fill_color=LAVENDER_BG, fill_opacity=0.0)
            big_rect.move_to(ORIGIN)
            check_safe_margins(big_rect, "big_rect")
            self.play(Create(big_rect), run_time=1.0)
            active_mobs.append(big_rect)

            # divider
            divider_x = big_rect.get_left()[0] + LW
            div_top   = np.array([divider_x, big_rect.get_top()[1],    0])
            div_bot   = np.array([divider_x, big_rect.get_bottom()[1], 0])
            divider   = Line(div_top, div_bot,
                             color=PURPLE, stroke_width=2.5)
            self.play(Create(divider), run_time=0.5)
            active_mobs.append(divider)

            # ── dimension arrows ──
            self.wait_until_bookmark("bk_rect")

            # bottom arrow — left section
            left_mid_x = big_rect.get_left()[0] + LW / 2
            arr_left = DoubleArrow(
                start=np.array([big_rect.get_left()[0],
                                big_rect.get_bottom()[1] - 0.4, 0]),
                end  =np.array([divider_x,
                                big_rect.get_bottom()[1] - 0.4, 0]),
                color=PURPLE, stroke_width=2, tip_length=0.18, buff=0)
            lbl_4 = Text("4", font="Poppins", font_size=22, color=PURPLE)
            lbl_4.next_to(arr_left.get_center(), DOWN, buff=0.15)

            # bottom arrow — right section
            arr_right = DoubleArrow(
                start=np.array([divider_x,
                                big_rect.get_bottom()[1] - 0.4, 0]),
                end  =np.array([big_rect.get_right()[0],
                                big_rect.get_bottom()[1] - 0.4, 0]),
                color=PURPLE, stroke_width=2, tip_length=0.18, buff=0)
            lbl_3 = Text("3", font="Poppins", font_size=22, color=PURPLE)
            lbl_3.next_to(arr_right.get_center(), DOWN, buff=0.15)

            # right arrow — height
            arr_h = DoubleArrow(
                start=np.array([big_rect.get_right()[0] + 0.4,
                                big_rect.get_bottom()[1], 0]),
                end  =np.array([big_rect.get_right()[0] + 0.4,
                                big_rect.get_top()[1], 0]),
                color=PURPLE, stroke_width=2, tip_length=0.18, buff=0)
            lbl_v = Text("v", font="Poppins", font_size=22, color=PURPLE)
            lbl_v.next_to(arr_h.get_center(), RIGHT, buff=0.15)
            check_safe_margins(lbl_v, "lbl_v")

            dim_group = VGroup(arr_left, lbl_4, arr_right,
                               lbl_3, arr_h, lbl_v)
            self.play(Create(arr_left), Create(arr_right),
                      Create(arr_h), run_time=0.8)
            self.play(FadeIn(lbl_4), FadeIn(lbl_3),
                      FadeIn(lbl_v), run_time=0.6)
            active_mobs.append(dim_group)

            # ── Method 1: whole rectangle → 7v ──
            self.wait_until_bookmark("bk_way1")
            lbl_7v = math_obj(r"7v", color=ORANGE_HL, font_size=32)
            lbl_7v.next_to(big_rect, UP, buff=0.35)
            check_safe_margins(lbl_7v, "lbl_7v")
            self.play(
                big_rect.animate.set_stroke(color=ORANGE_HL),
                FadeIn(lbl_7v), run_time=0.7)
            active_mobs.append(lbl_7v)
            self.wait(0.3)
            self.play(big_rect.animate.set_stroke(color=PURPLE),
                      run_time=0.4)

            # ── Method 2: two parts → 4v + 3v ──
            self.wait_until_bookmark("bk_way2")
            left_cx  = big_rect.get_left()[0] + LW / 2
            right_cx = divider_x + RightW / 2
            cy       = big_rect.get_center()[1]

            lbl_4v = math_obj(r"4v", color=PURPLE, font_size=28)
            lbl_4v.move_to(np.array([left_cx, cy, 0]))
            lbl_3v = math_obj(r"3v", color=PURPLE, font_size=28)
            lbl_3v.move_to(np.array([right_cx, cy, 0]))

            eq_row = build_expr_row([
                ("l4v",  r"4v"),
                ("plus", r"+"),
                ("r3v",  r"3v"),
                ("eq",   r"="),
                ("sv",   r"7v"),
            ], font_size=28)
            eq_row["l4v"].set_color(ORANGE_HL)
            eq_row["r3v"].set_color(ORANGE_HL)
            eq_row["sv"].set_color(ORANGE_HL)
            eq_row["row"].next_to(dim_group, DOWN, buff=0.45)
            check_safe_margins(eq_row["row"], "eq_row")

            self.play(FadeIn(lbl_4v), FadeIn(lbl_3v), run_time=0.6)
            active_mobs.append(lbl_4v)
            active_mobs.append(lbl_3v)
            self.play(FadeIn(eq_row["row"]), run_time=0.7)
            active_mobs.append(eq_row["row"])

            # ── agreement pulse ──
            self.wait_until_bookmark("bk_agree")
            self.play(
                Indicate(lbl_7v, color=ORANGE_HL, scale_factor=1.15),
                Indicate(eq_row["sv"], color=ORANGE_HL, scale_factor=1.15),
                run_time=0.8)

        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── CONCEPT ────────────────────────────────────────────
    def show_concept(self):
        active_mobs = []
        badge = create_heading_badge("Concept")
        check_safe_margins(badge, "badge_concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)
        self._concept_property(active_mobs)
        self._concept_worked(active_mobs)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    def _concept_property(self, active_mobs):
        with self.voiceover(
            text=(
                'The distributive property states that a number multiplied '
                'by a sum, equals the sum of that number multiplied by '
                'each part separately. '
                'So three times the quantity x plus four, '
                '<bookmark mark="bk_expand"/>equals three times x, '
                'plus three times four, which gives three x plus twelve. '
                'We must not add the terms inside the bracket first — '
                '<bookmark mark="bk_must"/>we must distribute the multiplication '
                'across every term inside. '
                'Then, after distributing, '
                '<bookmark mark="bk_collect"/>we collect any like terms '
                'that appear.'
            )
        ) as tracker:
            # property definition card
            prop_card = make_concept_card(
                "a(x + y) = ax + ay",
                position=UP * 1.8, font_size=28)
            check_safe_margins(prop_card, "prop_card")
            self.play(FadeIn(prop_card), run_time=0.7)
            active_mobs.append(prop_card)

            # Pattern F — 3(x+4) split expression
            self.wait_until_bookmark("bk_expand")
            e = build_expr_row([
                ("t3",   r"3"),
                ("tlp",  r"("),
                ("tx",   r"x"),
                ("tpl",  r"+"),
                ("t4",   r"4"),
                ("trp",  r")"),
            ], font_size=32)
            e["row"].move_to(UP * 0.6)
            check_safe_margins(e["row"], "expr_3x4")
            self.play(FadeIn(e["row"]), run_time=0.7)
            active_mobs.append(e["row"])

            # distribute arrows from 3 to x and 4
            arr_to_x = Arrow(
                e["t3"].get_bottom() + DOWN * 0.05,
                e["tx"].get_bottom() + DOWN * 0.05,
                color=ORANGE_HL, stroke_width=2.0,
                tip_length=0.15, buff=0.05,
                path_arc=-PI / 3)
            arr_to_4 = Arrow(
                e["t3"].get_bottom() + DOWN * 0.05,
                e["t4"].get_bottom() + DOWN * 0.05,
                color=ORANGE_HL, stroke_width=2.0,
                tip_length=0.15, buff=0.05,
                path_arc=-PI / 2)
            self.play(Create(arr_to_x), Create(arr_to_4), run_time=0.8)
            active_mobs.append(arr_to_x)
            active_mobs.append(arr_to_4)

            # result row
            result_e = build_expr_row([
                ("eq",   r"="),
                ("r3x",  r"3x"),
                ("rpl",  r"+"),
                ("r12",  r"12"),
            ], font_size=32)
            result_e["r3x"].set_color(ORANGE_HL)
            result_e["r12"].set_color(ORANGE_HL)
            result_e["row"].next_to(e["row"], DOWN, buff=0.45)
            check_safe_margins(result_e["row"], "result_3x4")
            self.play(FadeIn(result_e["row"]), run_time=0.7)
            active_mobs.append(result_e["row"])

            # warning card
            self.wait_until_bookmark("bk_must")
            self.play(
                FadeOut(e["row"]), FadeOut(arr_to_x),
                FadeOut(arr_to_4), FadeOut(result_e["row"]),
                run_time=0.5)
            for item in [e["row"], arr_to_x,
                         arr_to_4, result_e["row"]]:
                if item in active_mobs:
                    active_mobs.remove(item)

            warn_card = make_concept_card(
                "Never add inside brackets first — distribute first.",
                position=UP * 0.4, font_size=24)
            check_safe_margins(warn_card, "warn_card")
            self.play(FadeIn(warn_card), run_time=0.6)
            active_mobs.append(warn_card)

            self.wait_until_bookmark("bk_collect")
            collect_card = make_concept_card(
                "After distributing, collect like terms.",
                position=DOWN * 0.7, font_size=24)
            check_safe_margins(collect_card, "collect_card")
            self.play(FadeIn(collect_card), run_time=0.6)
            active_mobs.append(collect_card)

    def _concept_worked(self, active_mobs):
        with self.voiceover(
            text=(
                'For example, three times the quantity two x plus five, '
                'plus four x, '
                '<bookmark mark="bk_worked"/>gives six x plus fifteen, '
                'plus four x. '
                'Now six x and four x '
                '<bookmark mark="bk_like"/>are like terms. '
                'Combining them gives '
                '<bookmark mark="bk_ten"/>ten x plus fifteen. '
                '<bookmark mark="bk_rule"/>Always distribute first, '
                'then collect like terms.'
            )
        ) as tracker:
            # clear previous cards
            to_clear = [m for m in active_mobs
                        if m is not active_mobs[0]]
            if to_clear:
                self.play(*[FadeOut(m) for m in to_clear],
                          run_time=0.5)
                for m in to_clear:
                    active_mobs.remove(m)

            # Pattern F — 3(2x+5)+4x
            we = build_expr_row([
                ("w3",   r"3"),
                ("wlp",  r"("),
                ("w2x",  r"2x"),
                ("wpl",  r"+"),
                ("w5",   r"5"),
                ("wrp",  r")"),
                ("wpp",  r"+"),
                ("w4x",  r"4x"),
            ], font_size=30)
            we["row"].move_to(UP * 1.6)
            check_safe_margins(we["row"], "worked_expr")
            self.play(FadeIn(we["row"]), run_time=0.7)
            active_mobs.append(we["row"])

            # distribute arrows
            self.wait_until_bookmark("bk_worked")
            a1 = Arrow(
                we["w3"].get_bottom(),
                we["w2x"].get_bottom() + DOWN * 0.05,
                color=ORANGE_HL, stroke_width=2.0,
                tip_length=0.14, buff=0.05,
                path_arc=-PI / 3)
            a2 = Arrow(
                we["w3"].get_bottom(),
                we["w5"].get_bottom() + DOWN * 0.05,
                color=ORANGE_HL, stroke_width=2.0,
                tip_length=0.14, buff=0.05,
                path_arc=-PI / 2)
            self.play(Create(a1), Create(a2), run_time=0.7)
            active_mobs.append(a1)
            active_mobs.append(a2)

            # expanded row: 6x + 15 + 4x
            exp = build_expr_row([
                ("e6x",  r"6x"),
                ("epl",  r"+"),
                ("e15",  r"15"),
                ("epp",  r"+"),
                ("e4x",  r"4x"),
            ], font_size=30)
            exp["row"].next_to(we["row"], DOWN, buff=0.45)
            check_safe_margins(exp["row"], "exp_row")
            self.play(FadeIn(exp["row"]), run_time=0.7)
            active_mobs.append(exp["row"])
            self.play(FadeOut(a1), FadeOut(a2), run_time=0.4)
            active_mobs.remove(a1)
            active_mobs.remove(a2)

            # highlight like terms
            self.wait_until_bookmark("bk_like")
            self.play(
                exp["e6x"].animate.set_color(ORANGE_HL),
                exp["e4x"].animate.set_color(ORANGE_HL),
                run_time=0.5)

            # combine in place
            self.wait_until_bookmark("bk_ten")
            combined = math_obj(r"10x", color=ORANGE_HL, font_size=30)
            like_grp = VGroup(exp["e6x"], exp["epp"], exp["e4x"])
            combined.move_to(like_grp.get_center())
            self.play(
                ReplacementTransform(like_grp, combined),
                run_time=0.7)
            active_mobs.append(combined)

            result_w = build_expr_row([
                ("req", r"="),
                ("r10", r"10x"),
                ("rpl", r"+"),
                ("r15", r"15"),
            ], font_size=30)
            result_w["r10"].set_color(ORANGE_HL)
            result_w["r15"].set_color(ORANGE_HL)
            result_w["row"].next_to(exp["row"], DOWN, buff=0.4)
            check_safe_margins(result_w["row"], "result_worked")
            self.play(FadeIn(result_w["row"]), run_time=0.7)
            active_mobs.append(result_w["row"])

            # rule card
            self.wait_until_bookmark("bk_rule")
            rule_card = make_concept_card(
                "Always distribute first, then collect like terms.",
                position=DOWN * 2.3, font_size=22)
            check_safe_margins(rule_card, "rule_card")
            self.play(FadeIn(rule_card), run_time=0.6)
            active_mobs.append(rule_card)

    # ── QUESTION ───────────────────────────────────────────
    def show_question(self):
        active_mobs = []
        badge = create_heading_badge("Question")
        check_safe_margins(badge, "badge_q")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        with self.voiceover(
            text=(
                '<bookmark mark="bk_question"/>Simplify two times the quantity '
                'three a plus four, plus five a minus three.'
            )
        ) as tracker:
            self.wait_until_bookmark("bk_question")
            q_text = Text(
                "Simplify: 2(3a + 4) + 5a - 3",
                font="Poppins", font_size=26, color=PURPLE)
            q_text.move_to(UP * 2.5)
            check_safe_margins(q_text, "q_text")
            self.play(FadeIn(q_text), run_time=0.7)
            active_mobs.append(q_text)

            # Pattern F figure
            qe = build_expr_row([
                ("q2",   r"2"),
                ("qlp",  r"("),
                ("q3a",  r"3a"),
                ("qpl",  r"+"),
                ("q4",   r"4"),
                ("qrp",  r")"),
                ("qpp",  r"+"),
                ("q5a",  r"5a"),
                ("qmn",  r"-"),
                ("q3",   r"3"),
            ], font_size=30)
            qe["row"].move_to(ORIGIN)
            check_safe_margins(qe["row"], "q_expr")
            self.play(FadeIn(qe["row"]), run_time=0.8)
            active_mobs.append(qe["row"])

        self._q_expr_row = qe["row"]
        self._active_from_question = active_mobs

    # ── SOLUTION ───────────────────────────────────────────
    def show_solution(self):
        active_mobs = list(self._active_from_question)

        self.play(
            self._q_expr_row.animate.move_to(
                RIGHT * 3.2 + DOWN * 0.3),
            run_time=1.0)

        badge_old = active_mobs[0]
        badge_new = create_heading_badge("Solution")
        self.play(FadeOut(badge_old), FadeIn(badge_new), run_time=0.5)
        active_mobs[0] = badge_new

        with self.voiceover(
            text=(
                '<bookmark mark="bk_s1"/>Distribute: two times three a '
                'equals six a, and two times four equals eight. '
                '<bookmark mark="bk_s2"/>Expression becomes six a plus '
                'eight plus five a minus three. '
                '<bookmark mark="bk_s3"/>Collect like terms: six a plus '
                'five a equals eleven a. '
                '<bookmark mark="bk_s4"/>Combine constants: eight minus '
                'three equals five. '
                '<bookmark mark="bk_s5"/>Simplified expression is '
                'eleven a plus five.'
            )
        ) as tracker:
            # 5 steps at font_size=24, buff=0.25 → max 5 ✅
            mgr = StepManager(
                self,
                start_anchor=UP * 2.0 + LEFT * 3.5,
                font_size=24, buff=0.25)

            self.wait_until_bookmark("bk_s1")
            s1 = math_obj(
                r"2 \times 3a = 6a, \quad 2 \times 4 = 8",
                font_size=24)
            s1.set_stroke(width=2.0)
            mgr.add_step(s1)
            active_mobs.append(s1)

            self.wait_until_bookmark("bk_s2")
            s2 = math_obj(
                r"6a + 8 + 5a - 3",
                font_size=24)
            s2.set_stroke(width=2.0)
            mgr.add_step(s2)
            active_mobs.append(s2)

            self.wait_until_bookmark("bk_s3")
            s3 = math_obj(
                r"6a + 5a = 11a",
                font_size=24)
            s3.set_stroke(width=2.0)
            mgr.add_step(s3)
            active_mobs.append(s3)

            self.wait_until_bookmark("bk_s4")
            s4 = math_obj(
                r"8 - 3 = 5",
                font_size=24)
            s4.set_stroke(width=2.0)
            mgr.add_step(s4)
            active_mobs.append(s4)

            self.wait_until_bookmark("bk_s5")
            s5 = math_obj(
                r"= 11a + 5",
                font_size=24, color=ORANGE_HL)
            mgr.add_step(s5)
            active_mobs.append(s5)

            legend = make_legend(
                [("a", "= variable")],
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
            "Always distribute first, then collect like terms.",
            "Distribute: multiply the factor by every term\ninside the brackets.",
            "Collect: add or subtract the like terms to simplify.",
        ]
        positions = [UP * 1.5, ORIGIN, DOWN * 1.5]

        with self.voiceover(
            text=(
                '<bookmark mark="bk_sum1"/>Always distribute first, '
                'then collect like terms. '
                '<bookmark mark="bk_sum2"/>Distribute: multiply the factor '
                'by every term inside the brackets. '
                '<bookmark mark="bk_sum3"/>Collect: add or subtract '
                'the like terms to simplify.'
            )
        ) as tracker:
            for i, (txt, pos) in enumerate(
                    zip(summary_points, positions)):
                self.wait_until_bookmark(f"bk_sum{i + 1}")
                bullet = make_bullet_point(
                    txt, position=pos, font_size=24)
                check_safe_margins(bullet, f"bullet_{i}")
                self.play(FadeIn(bullet), run_time=0.7)
                active_mobs.append(bullet)

        self.wait(0.6)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()