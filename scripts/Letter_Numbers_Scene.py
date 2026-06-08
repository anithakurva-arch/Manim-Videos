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

class LetterNumbersScene(VoiceoverScene):

    def construct(self):
        self._setup_tts()
        self.show_title()
        self.show_hook()
        self.show_letter_number_intro()
        self.show_power_of_letter_numbers()
        self.show_reformulation()
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
            text='<bookmark mark="bk_title"/>The Notion of Letter-Numbers.'
        ) as tracker:
            self.wait_until_bookmark("bk_title")
            topic = Text(
                "The Notion of\nLetter-Numbers",
                font="Poppins", font_size=52,
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
                '<bookmark mark="bk_hook"/>Imagine you know that your friend is always '
                'three years older than you. '
                '<bookmark mark="bk_table"/>When you were ten, your friend was thirteen. '
                'When you were fifteen, your friend was eighteen. '
                '<bookmark mark="bk_pattern"/>Every single time, — it is your age plus three. '
                'But writing that out again and again is slow. '
                '<bookmark mark="bk_shorter"/>There has to be a shorter way.'
            )
        ) as tracker:

            self.wait_until_bookmark("bk_hook")

            hook_card = make_concept_card(
                "Your friend is always 3 years older than you.",
                position=UP * 2.0,
                font_size=26,
            )
            check_safe_margins(hook_card, "hook_card")
            self.play(FadeIn(hook_card), run_time=0.7)
            active_mobs.append(hook_card)

            # Pattern C: table of two cases
            self.wait_until_bookmark("bk_table")

            # Header row
            hdr_you = Text("Your age", font="Poppins",
                           font_size=24, color=PURPLE)
            hdr_friend = Text("Friend's age", font="Poppins",
                              font_size=24, color=PURPLE)
            hdr_you.move_to(LEFT * 2.5 + UP * 0.9)
            hdr_friend.move_to(RIGHT * 2.5 + UP * 0.9)
            check_safe_margins(hdr_you, "hdr_you")
            check_safe_margins(hdr_friend, "hdr_friend")

            hdr_line = Line(LEFT * 5.0, RIGHT * 5.0,
                            color=PALE_PURPLE, stroke_width=1.5)
            hdr_line.move_to(UP * 0.6)

            self.play(
                FadeIn(hdr_you), FadeIn(hdr_friend),
                Create(hdr_line), run_time=0.6
            )
            active_mobs.extend([hdr_you, hdr_friend, hdr_line])

            # Row 1: 10 → 13
            r1_you = math_obj(r"10", font_size=34)
            r1_friend = math_obj(r"13", font_size=34, color=ORANGE_HL)
            r1_you.move_to(LEFT * 2.5 + UP * 0.15)
            r1_friend.move_to(RIGHT * 2.5 + UP * 0.15)
            check_safe_margins(r1_you, "r1_you")
            check_safe_margins(r1_friend, "r1_friend")
            self.play(FadeIn(r1_you), FadeIn(r1_friend), run_time=0.6)
            active_mobs.extend([r1_you, r1_friend])

            # Row 2: 15 → 18
            r2_you = math_obj(r"15", font_size=34)
            r2_friend = math_obj(r"18", font_size=34, color=ORANGE_HL)
            r2_you.move_to(LEFT * 2.5 + DOWN * 0.55)
            r2_friend.move_to(RIGHT * 2.5 + DOWN * 0.55)
            check_safe_margins(r2_you, "r2_you")
            check_safe_margins(r2_friend, "r2_friend")
            self.play(FadeIn(r2_you), FadeIn(r2_friend), run_time=0.6)
            active_mobs.extend([r2_you, r2_friend])

            self.wait_until_bookmark("bk_pattern")

            pattern_lbl = Text(
                "Always: your age + 3",
                font="Poppins", font_size=26, color=ORANGE_HL
            )
            pattern_lbl.move_to(DOWN * 1.4)
            check_safe_margins(pattern_lbl, "pattern_lbl")
            check_y_gap(pattern_lbl, active_mobs, name="pattern_lbl")
            self.play(FadeIn(pattern_lbl), run_time=0.6)
            active_mobs.append(pattern_lbl)

            self.wait_until_bookmark("bk_shorter")
            shorter_card = make_concept_card(
                "There has to be a shorter way.",
                position=DOWN * 2.3,
                font_size=24,
            )
            check_safe_margins(shorter_card, "shorter_card")
            check_y_gap(shorter_card, active_mobs, name="shorter_card")
            self.play(FadeIn(shorter_card), run_time=0.6)
            active_mobs.append(shorter_card)

        self.wait(0.4)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── LETTER-NUMBER INTRO ─────────────────────────────────────

    def show_letter_number_intro(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        with self.voiceover(
            text=(
                '<bookmark mark="bk_def"/>A letter-number is a symbol, — usually a letter, '
                '— that represents a number or an unknown quantity. '
                '<bookmark mark="bk_use_a"/>Instead of writing the phrase "your age" every time, '
                '— we simply use a letter — say, a. '
                '<bookmark mark="bk_formula"/>Then your friend\'s age is always, a plus three. '
                'This single short expression works for every possible value of a.'
            )
        ) as tracker:

            # Definition card
            self.wait_until_bookmark("bk_def")
            def_card = make_concept_card(
                "A letter-number is a symbol representing a number or unknown quantity.",
                position=UP * 2.0,
                font_size=26,
            )
            check_safe_margins(def_card, "def_card")
            self.play(FadeIn(def_card), run_time=0.7)
            active_mobs.append(def_card)

            # Pattern D: show "your age" → a substitution
            self.wait_until_bookmark("bk_use_a")

            phrase_txt = Text(
                "your age", font="Poppins",
                font_size=38, color=PALE_PURPLE
            )
            phrase_txt.move_to(LEFT * 2.5 + UP * 0.6)
            check_safe_margins(phrase_txt, "phrase_txt")
            self.play(FadeIn(phrase_txt), run_time=0.6)
            active_mobs.append(phrase_txt)

            # Arrow → a
            sub_arrow = Arrow(
                start=phrase_txt.get_right() + RIGHT * 0.1,
                end=phrase_txt.get_right() + RIGHT * 1.4,
                color=ORANGE_HL, stroke_width=2.5,
                tip_length=0.2, buff=0.05
            )
            letter_a = math_obj(r"a", font_size=52, color=ORANGE_HL)
            letter_a.next_to(sub_arrow, RIGHT, buff=0.2)
            check_safe_margins(letter_a, "letter_a")
            self.play(Create(sub_arrow), FadeIn(letter_a), run_time=0.7)
            active_mobs.extend([sub_arrow, letter_a])

            # Pattern F: friend's age = a + 3
            self.wait_until_bookmark("bk_formula")

            friend_lbl = Text(
                "Friend's age:", font="Poppins",
                font_size=26, color=PURPLE
            )

            t_a2    = math_obj(r"a", font_size=44, color=ORANGE_HL)
            t_plus  = math_obj(r"+", font_size=44)
            t_3     = math_obj(r"3", font_size=44)

            formula_row = VGroup(t_a2, t_plus, t_3).arrange(RIGHT, buff=0.14)
            formula_block = VGroup(friend_lbl, formula_row).arrange(
                RIGHT, buff=0.3)
            formula_block.move_to(DOWN * 0.6)
            check_safe_margins(formula_block, "formula_block")
            check_y_gap(formula_block, active_mobs, name="formula_block")
            self.play(FadeIn(formula_block), run_time=0.8)
            active_mobs.append(formula_block)

            # Highlight: works for every value of a
            self.play(
                t_a2.animate.set_color(ORANGE_HL),
                run_time=0.4
            )

            every_lbl = Text(
                "Works for every value of a",
                font="Poppins", font_size=22, color=PALE_PURPLE
            )
            every_lbl.next_to(formula_block, DOWN, buff=0.35)
            check_safe_margins(every_lbl, "every_lbl")
            check_y_gap(every_lbl, active_mobs, name="every_lbl")
            self.play(FadeIn(every_lbl), run_time=0.5)
            active_mobs.append(every_lbl)

        self.wait(0.4)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── POWER OF LETTER-NUMBERS ─────────────────────────────────

    def show_power_of_letter_numbers(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        with self.voiceover(
            text=(
                '<bookmark mark="bk_power"/>This is what makes letter-numbers so powerful. '
                'They let us express general relationships, — in a concise form. '
                '<bookmark mark="bk_formula_name"/>Mathematical relations written this way '
                'are often called formulas.'
            )
        ) as tracker:

            self.wait_until_bookmark("bk_power")

            power_card = make_concept_card(
                "Letter-numbers express general relationships in concise form.",
                position=UP * 1.5,
                font_size=26,
            )
            check_safe_margins(power_card, "power_card")
            self.play(FadeIn(power_card), run_time=0.7)
            active_mobs.append(power_card)

            # Show the compact formula vs verbose form — Pattern C
            verbose_lbl = Text("Verbose:", font="Poppins",
                               font_size=22, color=PALE_PURPLE)
            verbose_expr = Text(
                "friend's age = your age + 3",
                font="Poppins", font_size=24, color=PURPLE
            )
            verbose_block = VGroup(
                verbose_lbl, verbose_expr
            ).arrange(DOWN, buff=0.15, aligned_edge=LEFT)
            verbose_block.move_to(LEFT * 2.8 + UP * 0.1)
            check_safe_margins(verbose_block, "verbose_block")
            self.play(FadeIn(verbose_block), run_time=0.7)
            active_mobs.append(verbose_block)

            concise_lbl = Text("Concise:", font="Poppins",
                               font_size=22, color=ORANGE_HL)
            concise_expr = VGroup(
                math_obj(r"f", font_size=34, color=ORANGE_HL),
                math_obj(r"=", font_size=34),
                math_obj(r"a", font_size=34, color=ORANGE_HL),
                math_obj(r"+", font_size=34),
                math_obj(r"3", font_size=34),
            ).arrange(RIGHT, buff=0.12)
            concise_block = VGroup(
                concise_lbl, concise_expr
            ).arrange(DOWN, buff=0.15, aligned_edge=LEFT)
            concise_block.move_to(RIGHT * 2.8 + UP * 0.1)
            check_safe_margins(concise_block, "concise_block")
            self.play(FadeIn(concise_block), run_time=0.7)
            active_mobs.append(concise_block)

            self.wait_until_bookmark("bk_formula_name")

            formula_card = make_concept_card(
                "Mathematical relations written this way are called formulas.",
                position=DOWN * 1.8,
                font_size=24,
            )
            check_safe_margins(formula_card, "formula_card")
            check_y_gap(formula_card, active_mobs, name="formula_card")
            self.play(FadeIn(formula_card), run_time=0.7)
            active_mobs.append(formula_card)

        self.wait(0.4)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── REFORMULATION ───────────────────────────────────────────

    def show_reformulation(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        with self.voiceover(
            text=(
                '<bookmark mark="bk_reform"/>We can also reformulate. '
                'If we know your friend\'s age, — we can work backwards. '
                '<bookmark mark="bk_s_def"/>Your friend\'s age is s. '
                '<bookmark mark="bk_derive"/>Since s equals a plus three, '
                '— your age is s minus three. '
                '<bookmark mark="bk_both"/>The same relationship, — expressed the other way around.'
            )
        ) as tracker:

            self.wait_until_bookmark("bk_reform")

            reform_card = make_concept_card(
                "We can reformulate to express either quantity in terms of the other.",
                position=UP * 2.0,
                font_size=26,
            )
            check_safe_margins(reform_card, "reform_card")
            self.play(FadeIn(reform_card), run_time=0.7)
            active_mobs.append(reform_card)

            # Forward formula: f = a + 3
            self.wait_until_bookmark("bk_s_def")

            fwd_lbl = Text("Forward:", font="Poppins",
                           font_size=24, color=PURPLE)
            fwd_expr = VGroup(
                math_obj(r"s", font_size=38, color=ORANGE_HL),
                math_obj(r"=", font_size=38),
                math_obj(r"a", font_size=38),
                math_obj(r"+", font_size=38),
                math_obj(r"3", font_size=38),
            ).arrange(RIGHT, buff=0.12)
            fwd_block = VGroup(fwd_lbl, fwd_expr).arrange(
                RIGHT, buff=0.3)
            fwd_block.move_to(UP * 0.7)
            check_safe_margins(fwd_block, "fwd_block")
            check_y_gap(fwd_block, active_mobs, name="fwd_block")
            self.play(FadeIn(fwd_block), run_time=0.7)
            active_mobs.append(fwd_block)

            # Backward formula: a = s - 3
            self.wait_until_bookmark("bk_derive")

            bwd_lbl = Text("Backwards:", font="Poppins",
                           font_size=24, color=PURPLE)
            bwd_expr = VGroup(
                math_obj(r"a", font_size=38, color=ORANGE_HL),
                math_obj(r"=", font_size=38),
                math_obj(r"s", font_size=38),
                math_obj(r"-", font_size=38),
                math_obj(r"3", font_size=38),
            ).arrange(RIGHT, buff=0.12)
            bwd_block = VGroup(bwd_lbl, bwd_expr).arrange(
                RIGHT, buff=0.3)
            bwd_block.move_to(DOWN * 0.2)
            check_safe_margins(bwd_block, "bwd_block")
            check_y_gap(bwd_block, active_mobs, name="bwd_block")
            self.play(FadeIn(bwd_block), run_time=0.7)
            active_mobs.append(bwd_block)

            # Arrow between the two showing they are related
            rel_arrow = Arrow(
                start=fwd_block.get_bottom() + DOWN * 0.05,
                end=bwd_block.get_top() + UP * 0.05,
                color=ORANGE_HL, stroke_width=2.0,
                tip_length=0.18, buff=0.08
            )
            self.play(Create(rel_arrow), run_time=0.5)
            active_mobs.append(rel_arrow)

            self.wait_until_bookmark("bk_both")
            both_card = make_concept_card(
                "Same relationship, expressed the other way around.",
                position=DOWN * 1.8,
                font_size=24,
            )
            check_safe_margins(both_card, "both_card")
            check_y_gap(both_card, active_mobs, name="both_card")
            self.play(FadeIn(both_card), run_time=0.6)
            active_mobs.append(both_card)

        self.wait(0.4)
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
                '<bookmark mark="bk_q"/>Priya has some marbles. '
                'Rohan has eight more marbles than Priya. '
                'Write an expression for Rohan\'s number of marbles. '
                '<bookmark mark="bk_q2"/>If Priya has fifteen marbles, '
                'how many does Rohan have?'
            )
        ) as tracker:

            self.wait_until_bookmark("bk_q")

            q1_card = make_concept_card(
                "Priya has some marbles. Rohan has 8 more than Priya.",
                position=UP * 1.8,
                font_size=26,
            )
            check_safe_margins(q1_card, "q1_card")
            self.play(FadeIn(q1_card), run_time=0.7)
            active_mobs.append(q1_card)

            task1 = Text(
                "Write an expression for Rohan's marbles.",
                font="Poppins", font_size=24, color=PURPLE
            )
            task1.move_to(UP * 0.6)
            check_safe_margins(task1, "task1")
            check_y_gap(task1, active_mobs, name="task1")
            self.play(FadeIn(task1), run_time=0.6)
            active_mobs.append(task1)

            self.wait_until_bookmark("bk_q2")

            task2 = Text(
                "If Priya has 15 marbles, how many does Rohan have?",
                font="Poppins", font_size=24, color=PURPLE
            )
            task2.move_to(DOWN * 0.3)
            check_safe_margins(task2, "task2")
            check_y_gap(task2, active_mobs, name="task2")
            self.play(FadeIn(task2), run_time=0.6)
            active_mobs.append(task2)

        self.wait(0.4)
        self._q_active = active_mobs[:]
        self._q_badge  = badge

    # ── SOLUTION ────────────────────────────────────────────────

    def show_solution(self):
        active_mobs = self._q_active[:]

        old_badge = self._q_badge
        new_badge = create_heading_badge("Solution")
        self.play(FadeOut(old_badge), FadeIn(new_badge), run_time=0.5)
        if old_badge in active_mobs:
            active_mobs.remove(old_badge)
        active_mobs.append(new_badge)

        mobs_to_fade = [m for m in active_mobs if m is not new_badge]
        if mobs_to_fade:
            self.play(*[FadeOut(m) for m in mobs_to_fade], run_time=0.6)
        for m in mobs_to_fade:
            if m in active_mobs:
                active_mobs.remove(m)
        self.wait(0.2)

        with self.voiceover(
            text=(
                '<bookmark mark="bk_s1"/>Let p represent Priya\'s number of marbles. '
                '<bookmark mark="bk_s2"/>Rohan\'s marbles equals p plus eight. '
                '<bookmark mark="bk_s3"/>Substitute p equals fifteen — '
                'fifteen plus eight equals twenty-three. '
                '<bookmark mark="bk_s4"/>Rohan has twenty-three marbles.'
            )
        ) as tracker:

            mgr = StepManager(
                self,
                start_anchor=UP * 1.6 + LEFT * 0.5,
                font_size=28,
                buff=0.38
            )

            # Step 1: define p
            self.wait_until_bookmark("bk_s1")
            s1 = VGroup(
                Text("Let", font="Poppins", font_size=28, color=PURPLE),
                math_obj(r"p", font_size=32, color=ORANGE_HL),
                Text("= Priya's marbles", font="Poppins",
                     font_size=28, color=PURPLE),
            ).arrange(RIGHT, buff=0.18)
            mgr.add_step(s1)
            active_mobs.append(s1)

            # Step 2: Rohan's expression
            self.wait_until_bookmark("bk_s2")
            s2 = VGroup(
                Text("Rohan =", font="Poppins", font_size=28, color=PURPLE),
                math_obj(r"p", font_size=32, color=ORANGE_HL),
                math_obj(r"+", font_size=32),
                math_obj(r"8", font_size=32),
            ).arrange(RIGHT, buff=0.18)
            mgr.add_step(s2)
            active_mobs.append(s2)

            # Step 3: substitute p = 15
            self.wait_until_bookmark("bk_s3")
            s3 = VGroup(
                math_obj(r"=", font_size=32),
                math_obj(r"15", font_size=32, color=ORANGE_HL),
                math_obj(r"+", font_size=32),
                math_obj(r"8", font_size=32),
                math_obj(r"=", font_size=32),
                math_obj(r"23", font_size=32, color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.14)
            mgr.add_step(s3)
            active_mobs.append(s3)

            # Step 4: conclusion
            self.wait_until_bookmark("bk_s4")
            s4 = VGroup(
                Text("Rohan has", font="Poppins",
                     font_size=30, color=PURPLE),
                math_obj(r"23", font_size=36, color=ORANGE_HL),
                Text("marbles.", font="Poppins",
                     font_size=30, color=PURPLE),
            ).arrange(RIGHT, buff=0.2)
            mgr.add_step(s4)
            active_mobs.append(s4)

            ans_box = SurroundingRectangle(
                s4, color=ORANGE_HL,
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
            "A letter-number is a symbol representing a number or unknown quantity.",
            "Letter-numbers let us write general relationships as concise expressions.",
            "The same relationship can be reformulated to express either quantity in terms of the other.",
        ]
        positions = [UP * 1.5, ORIGIN, DOWN * 1.5]

        with self.voiceover(
            text=(
                '<bookmark mark="bk_sum1"/>A letter-number is a symbol, '
                'representing a number or unknown quantity. '
                '<bookmark mark="bk_sum2"/>Letter-numbers let us write general relationships, '
                'as concise expressions. '
                '<bookmark mark="bk_sum3"/>The same relationship can be reformulated, '
                'to express either quantity in terms of the other.'
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
