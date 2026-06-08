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


# ─────────────────────── SCENE ──────────────────────────────────

class EqualExpressionsScene(VoiceoverScene):

    def construct(self):
        self._setup_tts()
        self.show_title()
        self.show_hook()
        self.show_substitution_method()
        self.show_substitution_test()
        self.show_simplification_proof()
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
            text='<bookmark mark="bk_title"/>Simplification of Algebraic Expressions.'
        ) as tracker:
            self.wait_until_bookmark("bk_title")
            topic = Text(
                "Simplification of\nAlgebraic Expressions",
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
                '<bookmark mark="bk_hook"/>Suppose two friends each work out a different formula '
                'for the cost of n pens. '
                'One writes three n plus six, — and the other writes three times the quantity '
                'n plus two. '
                '<bookmark mark="bk_question"/>Are these two expressions actually the same? '
                'How can we check?'
            )
        ) as tracker:

            self.wait_until_bookmark("bk_hook")

            # Left expression: 3n + 6
            lbl_friend1 = Text("Friend 1:", font="Poppins",
                               font_size=24, color=PURPLE)
            expr1 = VGroup(
                math_obj(r"3n", font_size=38),
                math_obj(r"+", font_size=38),
                math_obj(r"6", font_size=38),
            ).arrange(RIGHT, buff=0.12)
            col1 = VGroup(lbl_friend1, expr1).arrange(DOWN, buff=0.2)
            col1.move_to(LEFT * 3.0 + UP * 0.3)
            check_safe_margins(col1, "col1")
            self.play(FadeIn(col1), run_time=0.8)
            active_mobs.append(col1)

            # Right expression: 3(n + 2)
            lbl_friend2 = Text("Friend 2:", font="Poppins",
                               font_size=24, color=PURPLE)
            expr2 = VGroup(
                math_obj(r"3", font_size=38),
                math_obj(r"(", font_size=38),
                math_obj(r"n", font_size=38),
                math_obj(r"+", font_size=38),
                math_obj(r"2", font_size=38),
                math_obj(r")", font_size=38),
            ).arrange(RIGHT, buff=0.10)
            col2 = VGroup(lbl_friend2, expr2).arrange(DOWN, buff=0.2)
            col2.move_to(RIGHT * 3.0 + UP * 0.3)
            check_safe_margins(col2, "col2")
            self.play(FadeIn(col2), run_time=0.8)
            active_mobs.append(col2)

            self.wait_until_bookmark("bk_question")
            q_card = make_concept_card(
                "Are these two expressions actually the same?",
                position=DOWN * 1.5,
                font_size=26,
            )
            check_safe_margins(q_card, "q_card")
            check_y_gap(q_card, active_mobs, name="q_card")
            self.play(FadeIn(q_card), run_time=0.7)
            active_mobs.append(q_card)

        self.wait(0.4)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── SUBSTITUTION METHOD ─────────────────────────────────────

    def show_substitution_method(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        with self.voiceover(
            text=(
                '<bookmark mark="bk_method"/>One useful method is to substitute the same value '
                'of the letter-number into both expressions, — and compare the results. '
                '<bookmark mark="bk_suggest"/>If both give the same output, — it suggests '
                'the expressions may be equal.'
            )
        ) as tracker:

            self.wait_until_bookmark("bk_method")

            # Pattern B: substitution flow diagram
            # Left box: Expression A
            box_a_txt = Text("Expression A", font="Poppins",
                             font_size=24, color=PURPLE)
            box_a_bg = RoundedRectangle(
                corner_radius=0.2,
                width=box_a_txt.width + 0.6, height=box_a_txt.height + 0.4,
                fill_color=WHITE, fill_opacity=0.9,
                stroke_color=PALE_PURPLE, stroke_width=1.5)
            box_a_bg.move_to(LEFT * 3.5 + UP * 0.8)
            box_a_txt.move_to(box_a_bg.get_center())
            box_a = VGroup(box_a_bg, box_a_txt)

            # Right box: Expression B
            box_b_txt = Text("Expression B", font="Poppins",
                             font_size=24, color=PURPLE)
            box_b_bg = RoundedRectangle(
                corner_radius=0.2,
                width=box_b_txt.width + 0.6, height=box_b_txt.height + 0.4,
                fill_color=WHITE, fill_opacity=0.9,
                stroke_color=PALE_PURPLE, stroke_width=1.5)
            box_b_bg.move_to(RIGHT * 3.5 + UP * 0.8)
            box_b_txt.move_to(box_b_bg.get_center())
            box_b = VGroup(box_b_bg, box_b_txt)

            # Center: same value n = k
            val_label = VGroup(
                math_obj(r"n = k", font_size=34, color=ORANGE_HL)
            )
            val_label.move_to(ORIGIN + UP * 0.8)

            self.play(FadeIn(box_a), FadeIn(box_b), run_time=0.7)
            active_mobs.append(box_a)
            active_mobs.append(box_b)
            self.play(FadeIn(val_label), run_time=0.6)
            active_mobs.append(val_label)

            # Arrows from center value to each box
            arr_left = Arrow(
                start=val_label.get_left() + LEFT * 0.05,
                end=box_a.get_right() + RIGHT * 0.05,
                color=ORANGE_HL, stroke_width=2.5,
                tip_length=0.2, buff=0.1
            )
            arr_right = Arrow(
                start=val_label.get_right() + RIGHT * 0.05,
                end=box_b.get_left() + LEFT * 0.05,
                color=ORANGE_HL, stroke_width=2.5,
                tip_length=0.2, buff=0.1
            )
            self.play(Create(arr_left), Create(arr_right), run_time=0.7)
            active_mobs.append(arr_left)
            active_mobs.append(arr_right)

            # Result boxes below
            res_a_txt = Text("Result A", font="Poppins",
                             font_size=24, color=ORANGE_HL)
            res_a_txt.move_to(LEFT * 3.5 + DOWN * 0.4)

            res_b_txt = Text("Result B", font="Poppins",
                             font_size=24, color=ORANGE_HL)
            res_b_txt.move_to(RIGHT * 3.5 + DOWN * 0.4)

            arr_a_down = Arrow(
                start=box_a.get_bottom(),
                end=res_a_txt.get_top() + UP * 0.1,
                color=PURPLE, stroke_width=2.0,
                tip_length=0.18, buff=0.08
            )
            arr_b_down = Arrow(
                start=box_b.get_bottom(),
                end=res_b_txt.get_top() + UP * 0.1,
                color=PURPLE, stroke_width=2.0,
                tip_length=0.18, buff=0.08
            )
            self.play(
                Create(arr_a_down), Create(arr_b_down),
                FadeIn(res_a_txt), FadeIn(res_b_txt),
                run_time=0.8
            )
            active_mobs.extend([arr_a_down, arr_b_down,
                                 res_a_txt, res_b_txt])

            self.wait_until_bookmark("bk_suggest")
            suggest_card = make_concept_card(
                "Same output suggests expressions may be equal.",
                position=DOWN * 1.8,
                font_size=24,
            )
            check_safe_margins(suggest_card, "suggest_card")
            check_y_gap(suggest_card, active_mobs, name="suggest_card")
            self.play(FadeIn(suggest_card), run_time=0.7)
            active_mobs.append(suggest_card)

        self.wait(0.4)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── SUBSTITUTION TEST (n=4 and n=1) ─────────────────────────

    def show_substitution_test(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        with self.voiceover(
            text=(
                '<bookmark mark="bk_test_intro"/>Let us test three n plus six, — and three times '
                'the quantity n plus two, — with n equal to four. '
                '<bookmark mark="bk_e1_n4"/>First expression — three times four plus six, '
                'equals eighteen. '
                '<bookmark mark="bk_e2_n4"/>Second expression — three times six, equals eighteen. '
                '<bookmark mark="bk_match1"/>They match. '
                '<bookmark mark="bk_n1"/>Try n equal to one — first gives nine, '
                'second gives nine. '
                '<bookmark mark="bk_match2"/>They match again.'
            )
        ) as tracker:

            self.wait_until_bookmark("bk_test_intro")

            # Column headers
            hdr_left = Text("3n + 6", font="Poppins",
                            font_size=28, color=PURPLE)
            hdr_right = Text("3(n + 2)", font="Poppins",
                             font_size=28, color=PURPLE)
            hdr_left.move_to(LEFT * 3.2 + UP * 2.2)
            hdr_right.move_to(RIGHT * 3.2 + UP * 2.2)
            check_safe_margins(hdr_left, "hdr_left")
            check_safe_margins(hdr_right, "hdr_right")
            self.play(FadeIn(hdr_left), FadeIn(hdr_right), run_time=0.6)
            active_mobs.extend([hdr_left, hdr_right])

            # Divider line
            div_line = Line(
                UP * 1.95, DOWN * 2.8,
                color=PALE_PURPLE, stroke_width=1.5
            )
            self.play(Create(div_line), run_time=0.4)
            active_mobs.append(div_line)

            # Row label n=4
            self.wait_until_bookmark("bk_e1_n4")
            n4_label = VGroup(
                math_obj(r"n=4:", font_size=26, color=ORANGE_HL)
            )
            n4_label.move_to(LEFT * 5.5 + UP * 1.3)
            check_safe_margins(n4_label, "n4_label")
            self.play(FadeIn(n4_label), run_time=0.5)
            active_mobs.append(n4_label)

            # Left: 3(4)+6=18
            e1_n4 = VGroup(
                math_obj(r"3(4)", font_size=28),
                math_obj(r"+", font_size=28),
                math_obj(r"6", font_size=28),
                math_obj(r"=", font_size=28),
                math_obj(r"18", font_size=28, color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.10)
            e1_n4.move_to(LEFT * 3.2 + UP * 1.3)
            check_safe_margins(e1_n4, "e1_n4")
            self.play(FadeIn(e1_n4), run_time=0.7)
            active_mobs.append(e1_n4)

            self.wait_until_bookmark("bk_e2_n4")
            # Right: 3(4+2)=3(6)=18
            e2_n4 = VGroup(
                math_obj(r"3(6)", font_size=28),
                math_obj(r"=", font_size=28),
                math_obj(r"18", font_size=28, color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.10)
            e2_n4.move_to(RIGHT * 3.2 + UP * 1.3)
            check_safe_margins(e2_n4, "e2_n4")
            self.play(FadeIn(e2_n4), run_time=0.7)
            active_mobs.append(e2_n4)

            self.wait_until_bookmark("bk_match1")
            match1 = MathTex(r"\checkmark",
                             tex_template=TexFontTemplates.gnu_freesans_tx,
                             font_size=40, color=ORANGE_HL)
            match1.move_to(UP * 1.3)
            self.play(FadeIn(match1), run_time=0.5)
            active_mobs.append(match1)

            # Row n=1
            self.wait_until_bookmark("bk_n1")
            n1_label = VGroup(
                math_obj(r"n=1:", font_size=26, color=ORANGE_HL)
            )
            n1_label.move_to(LEFT * 5.5 + DOWN * 0.1)
            check_safe_margins(n1_label, "n1_label")
            self.play(FadeIn(n1_label), run_time=0.5)
            active_mobs.append(n1_label)

            e1_n1 = VGroup(
                math_obj(r"3(1)", font_size=28),
                math_obj(r"+", font_size=28),
                math_obj(r"6", font_size=28),
                math_obj(r"=", font_size=28),
                math_obj(r"9", font_size=28, color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.10)
            e1_n1.move_to(LEFT * 3.2 + DOWN * 0.1)
            check_safe_margins(e1_n1, "e1_n1")

            e2_n1 = VGroup(
                math_obj(r"3(3)", font_size=28),
                math_obj(r"=", font_size=28),
                math_obj(r"9", font_size=28, color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.10)
            e2_n1.move_to(RIGHT * 3.2 + DOWN * 0.1)
            check_safe_margins(e2_n1, "e2_n1")

            self.play(FadeIn(e1_n1), FadeIn(e2_n1), run_time=0.7)
            active_mobs.extend([e1_n1, e2_n1])

            self.wait_until_bookmark("bk_match2")
            match2 = MathTex(r"\checkmark",
                             tex_template=TexFontTemplates.gnu_freesans_tx,
                             font_size=40, color=ORANGE_HL)
            match2.move_to(DOWN * 0.1)
            self.play(FadeIn(match2), run_time=0.5)
            active_mobs.append(match2)

        self.wait(0.4)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── SIMPLIFICATION PROOF ─────────────────────────────────────

    def show_simplification_proof(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        with self.voiceover(
            text=(
                '<bookmark mark="bk_limit"/>Now, — substitution gives us a useful check, '
                'but it cannot prove that two expressions are always equal — '
                'we would need to test every possible value, which is impossible. '
                '<bookmark mark="bk_simplify"/>To be certain, — we simplify both expressions '
                'fully and compare their forms. '
                '<bookmark mark="bk_expand"/>Expanding three times the quantity n plus two, '
                '— gives three n plus six — identical to the first expression. '
                '<bookmark mark="bk_certain"/>That simplification gives us certainty.'
            )
        ) as tracker:

            self.wait_until_bookmark("bk_limit")
            limit_card = make_concept_card(
                "Substitution cannot prove equality for ALL values.",
                position=UP * 1.8,
                font_size=26,
            )
            check_safe_margins(limit_card, "limit_card")
            self.play(FadeIn(limit_card), run_time=0.7)
            active_mobs.append(limit_card)

            self.wait_until_bookmark("bk_simplify")
            simplify_card = make_concept_card(
                "Simplify both fully and compare forms to be certain.",
                position=UP * 0.6,
                font_size=26,
            )
            check_safe_margins(simplify_card, "simplify_card")
            check_y_gap(simplify_card, active_mobs, name="simplify_card")
            self.play(FadeIn(simplify_card), run_time=0.7)
            active_mobs.append(simplify_card)

            # Pattern F: expand 3(n+2)
            self.wait_until_bookmark("bk_expand")

            t_3     = math_obj(r"3", font_size=40)
            t_open  = math_obj(r"(", font_size=40)
            t_n     = math_obj(r"n", font_size=40)
            t_plus  = math_obj(r"+", font_size=40)
            t_2     = math_obj(r"2", font_size=40)
            t_close = math_obj(r")", font_size=40)

            orig_expr = VGroup(
                t_3, t_open, t_n, t_plus, t_2, t_close
            ).arrange(RIGHT, buff=0.10)
            orig_expr.move_to(DOWN * 0.7)
            check_safe_margins(orig_expr, "orig_expr")
            self.play(FadeIn(orig_expr), run_time=0.7)
            active_mobs.append(orig_expr)

            # Highlight each inner term as distributed
            self.play(
                t_3.animate.set_color(ORANGE_HL),
                run_time=0.4
            )
            self.play(
                t_n.animate.set_color(ORANGE_HL),
                t_2.animate.set_color(ORANGE_HL),
                run_time=0.5
            )

            # Expanded result
            expanded = VGroup(
                math_obj(r"=", font_size=40),
                math_obj(r"3n", font_size=40, color=ORANGE_HL),
                math_obj(r"+", font_size=40),
                math_obj(r"6", font_size=40, color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.12)
            expanded.next_to(orig_expr, DOWN, buff=0.45)
            check_safe_margins(expanded, "expanded")
            check_y_gap(expanded, active_mobs, name="expanded")
            self.play(FadeIn(expanded), run_time=0.8)
            active_mobs.append(expanded)

            self.wait_until_bookmark("bk_certain")
            certain_label = Text(
                "Identical to the first expression!",
                font="Poppins", font_size=26, color=ORANGE_HL
            )
            certain_label.next_to(expanded, DOWN, buff=0.4)
            check_safe_margins(certain_label, "certain_label")
            check_y_gap(certain_label, active_mobs, name="certain_label")
            self.play(FadeIn(certain_label), run_time=0.6)
            active_mobs.append(certain_label)

        self.wait(0.5)
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
                '<bookmark mark="bk_q"/>Check whether two x plus eight, — and two times '
                'the quantity x plus four, — give equal values for x equals three '
                'and x equals five. — Then confirm by simplification.'
            )
        ) as tracker:

            self.wait_until_bookmark("bk_q")

            q_label = Text("Check:", font="Poppins",
                           font_size=28, color=PURPLE)
            q_label.move_to(UP * 2.3)
            check_safe_margins(q_label, "q_label")
            self.play(FadeIn(q_label), run_time=0.5)
            active_mobs.append(q_label)

            # Expression 1: 2x + 8
            e1_lbl = Text("Expression 1:", font="Poppins",
                          font_size=24, color=PURPLE)
            e1_expr = VGroup(
                math_obj(r"2x", font_size=38),
                math_obj(r"+", font_size=38),
                math_obj(r"8", font_size=38),
            ).arrange(RIGHT, buff=0.12)
            e1_row = VGroup(e1_lbl, e1_expr).arrange(RIGHT, buff=0.3)
            e1_row.move_to(UP * 1.3)
            check_safe_margins(e1_row, "e1_row")
            self.play(FadeIn(e1_row), run_time=0.7)
            active_mobs.append(e1_row)

            # Expression 2: 2(x + 4)
            e2_lbl = Text("Expression 2:", font="Poppins",
                          font_size=24, color=PURPLE)
            e2_expr = VGroup(
                math_obj(r"2", font_size=38),
                math_obj(r"(", font_size=38),
                math_obj(r"x", font_size=38),
                math_obj(r"+", font_size=38),
                math_obj(r"4", font_size=38),
                math_obj(r")", font_size=38),
            ).arrange(RIGHT, buff=0.10)
            e2_row = VGroup(e2_lbl, e2_expr).arrange(RIGHT, buff=0.3)
            e2_row.move_to(UP * 0.3)
            check_safe_margins(e2_row, "e2_row")
            self.play(FadeIn(e2_row), run_time=0.7)
            active_mobs.append(e2_row)

            # Test values
            test_card = make_concept_card(
                "Test: x = 3 and x = 5. Then confirm by simplification.",
                position=DOWN * 1.0,
                font_size=24,
            )
            check_safe_margins(test_card, "test_card")
            check_y_gap(test_card, active_mobs, name="test_card")
            self.play(FadeIn(test_card), run_time=0.7)
            active_mobs.append(test_card)

        self.wait(0.4)
        self._q_active = active_mobs[:]
        self._q_badge  = badge

    # ── SOLUTION ────────────────────────────────────────────────

    def show_solution(self):
        active_mobs = self._q_active[:]

        # Swap badge
        old_badge = self._q_badge
        new_badge = create_heading_badge("Solution")
        self.play(FadeOut(old_badge), FadeIn(new_badge), run_time=0.5)
        if old_badge in active_mobs:
            active_mobs.remove(old_badge)
        active_mobs.append(new_badge)

        # Fade out question content, keep badge
        mobs_to_fade = [m for m in active_mobs if m is not new_badge]
        if mobs_to_fade:
            self.play(*[FadeOut(m) for m in mobs_to_fade], run_time=0.6)
        for m in mobs_to_fade:
            if m in active_mobs:
                active_mobs.remove(m)
        self.wait(0.2)

        with self.voiceover(
            text=(
                '<bookmark mark="bk_s1"/>For x equals three — six plus eight equals fourteen. '
                '<bookmark mark="bk_s2"/>Two times seven equals fourteen. — Match. '
                '<bookmark mark="bk_s3"/>For x equals five — ten plus eight equals eighteen. '
                '<bookmark mark="bk_s4"/>Two times nine equals eighteen. — Match. '
                '<bookmark mark="bk_s5"/>Expand — two times the quantity x plus four, '
                'equals two x plus eight. — Identical. '
                '<bookmark mark="bk_s6"/>The expressions are equal.'
            )
        ) as tracker:

            # Phase 1: x = 3
            mgr = StepManager(
                self,
                start_anchor=UP * 1.8 + LEFT * 0.5,
                font_size=28,
                buff=0.32
            )

            self.wait_until_bookmark("bk_s1")
            # x=3 header
            x3_hdr = VGroup(
                math_obj(r"x=3:", font_size=28, color=ORANGE_HL)
            )
            mgr.add_step(x3_hdr)
            active_mobs.append(x3_hdr)

            # Expression 1 with x=3: 2(3)+8 = 14
            self.wait_until_bookmark("bk_s2")
            s1 = VGroup(
                math_obj(r"2(3)", font_size=28),
                math_obj(r"+", font_size=28),
                math_obj(r"8", font_size=28),
                math_obj(r"=", font_size=28),
                math_obj(r"14", font_size=28, color=ORANGE_HL),
                math_obj(r"\quad", font_size=28),
                math_obj(r"2(7)", font_size=28),
                math_obj(r"=", font_size=28),
                math_obj(r"14", font_size=28, color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.10)
            mgr.add_step(s1)
            active_mobs.append(s1)

            chk1 = MathTex(r"\checkmark",
                           tex_template=TexFontTemplates.gnu_freesans_tx,
                           font_size=36, color=ORANGE_HL)
            chk1.next_to(s1, RIGHT, buff=0.25)
            check_safe_margins(chk1, "chk1")
            self.play(FadeIn(chk1), run_time=0.4)
            active_mobs.append(chk1)

            # x = 5
            self.wait_until_bookmark("bk_s3")
            x5_hdr = VGroup(
                math_obj(r"x=5:", font_size=28, color=ORANGE_HL)
            )
            mgr.add_step(x5_hdr)
            active_mobs.append(x5_hdr)

            self.wait_until_bookmark("bk_s4")
            s2 = VGroup(
                math_obj(r"2(5)", font_size=28),
                math_obj(r"+", font_size=28),
                math_obj(r"8", font_size=28),
                math_obj(r"=", font_size=28),
                math_obj(r"18", font_size=28, color=ORANGE_HL),
                math_obj(r"\quad", font_size=28),
                math_obj(r"2(9)", font_size=28),
                math_obj(r"=", font_size=28),
                math_obj(r"18", font_size=28, color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.10)
            mgr.add_step(s2)
            active_mobs.append(s2)

            chk2 = MathTex(r"\checkmark",
                           tex_template=TexFontTemplates.gnu_freesans_tx,
                           font_size=36, color=ORANGE_HL)
            chk2.next_to(s2, RIGHT, buff=0.25)
            check_safe_margins(chk2, "chk2")
            self.play(FadeIn(chk2), run_time=0.4)
            active_mobs.append(chk2)

            # Fade phase 1, start phase 2
            self.wait(0.3)
            mgr.fadeout_all(rt=0.6)
            for mob in [x3_hdr, s1, chk1, x5_hdr, s2, chk2]:
                if mob in active_mobs:
                    active_mobs.remove(mob)

            mgr2 = StepManager(
                self,
                start_anchor=UP * 1.5 + LEFT * 0.5,
                font_size=28,
                buff=0.35
            )

            # Expansion step
            self.wait_until_bookmark("bk_s5")
            exp_step = VGroup(
                math_obj(r"2(x+4)", font_size=28),
                math_obj(r"=", font_size=28),
                math_obj(r"2x", font_size=28, color=ORANGE_HL),
                math_obj(r"+", font_size=28, color=ORANGE_HL),
                math_obj(r"8", font_size=28, color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.12)
            mgr2.add_step(exp_step)
            active_mobs.append(exp_step)

            identical_label = Text(
                "Identical!",
                font="Poppins", font_size=26, color=ORANGE_HL
            )
            identical_label.next_to(exp_step, RIGHT, buff=0.35)
            check_safe_margins(identical_label, "identical_label")
            self.play(FadeIn(identical_label), run_time=0.5)
            active_mobs.append(identical_label)

            # Final answer
            self.wait_until_bookmark("bk_s6")
            final = VGroup(
                math_obj(r"2x+8", font_size=34, color=ORANGE_HL),
                math_obj(r"=", font_size=34, color=ORANGE_HL),
                math_obj(r"2(x+4)", font_size=34, color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.14)
            mgr2.add_step(final)
            active_mobs.append(final)

            ans_box = SurroundingRectangle(
                final, color=ORANGE_HL,
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
            "Substitute the same value into both expressions and compare results.",
            "Matching outputs suggest equality but do not prove it for all values.",
            "Simplify both expressions fully to confirm equality with certainty.",
        ]
        positions = [UP * 1.5, ORIGIN, DOWN * 1.5]

        with self.voiceover(
            text=(
                '<bookmark mark="bk_sum1"/>Substitute the same value into both expressions, '
                'and compare results. '
                '<bookmark mark="bk_sum2"/>Matching outputs suggest equality, '
                'but do not prove it for all values. '
                '<bookmark mark="bk_sum3"/>Simplify both expressions fully, '
                'to confirm equality with certainty.'
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