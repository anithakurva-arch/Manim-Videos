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
                      font_size=24, max_chars=52):
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
        corner_radius=0.2,
        width=min(txt.width + 0.8, 10.2),
        height=txt.height + 0.4,
        fill_color=WHITE, fill_opacity=0.85,
        stroke_color=PALE_PURPLE, stroke_width=1.5)
    bg.move_to(position)
    txt.move_to(bg.get_center())
    return VGroup(bg, txt)


def make_bullet_point(text_str, position=ORIGIN,
                      font_size=25, max_chars=50):
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


def check_y_gap(new_mob, existing_mobs, min_gap=0.32, name="new_mob"):
    for mob in existing_mobs:
        if isinstance(mob, VGroup) and len(mob) == 0:
            continue
        nb = new_mob.get_bottom()[1]
        nt = new_mob.get_top()[1]
        mb = mob.get_bottom()[1]
        mt = mob.get_top()[1]
        if nb < mt and nt > mb:
            shift = mt + min_gap - nb
            new_mob.shift(UP * shift)
            print(f"WARNING: '{name}' overlapped. Shifted UP {shift:.2f}")
        elif nb >= mt and (nb - mt) < min_gap:
            shift = min_gap - (nb - mt)
            new_mob.shift(UP * shift)
            print(f"WARNING: '{name}' too close. Shifted UP {shift:.2f}")
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

class ConsecutiveNumbersScene(VoiceoverScene):

    def construct(self):
        self._setup_tts()
        self.show_title()
        self.show_hook()
        self.show_generalise_method()
        self.show_consecutive_proof()
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
            text='<bookmark mark="bk_title"/>Pick Patterns and Reveal Relationships.'
        ) as tracker:
            self.wait_until_bookmark("bk_title")
            topic = Text(
                "Pick Patterns and\nReveal Relationships",
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
                '<bookmark mark="bk_notice"/>Suppose you notice that whenever you add '
                'two consecutive numbers — like one and two, or five and six, '
                'or forty-nine and fifty — the answer is always odd. '
                '<bookmark mark="bk_confidence"/>Interesting. But checking a few examples '
                'only gives you confidence, not certainty. '
                '<bookmark mark="bk_prove"/>To prove it works for every pair, '
                'we need a variable-based model.'
            )
        ) as tracker:

            self.wait_until_bookmark("bk_notice")

            # Pattern C: three numeric examples LEFT side
            ex_hdr = Text("Examples:", font="Poppins",
                          font_size=24, color=PURPLE)
            ex_hdr.move_to(LEFT * 4.2 + UP * 1.8)
            check_safe_margins(ex_hdr, "ex_hdr")
            self.play(FadeIn(ex_hdr), run_time=0.4)
            active_mobs.append(ex_hdr)

            examples = [
                (r"1 + 2 = 3",   "odd"),
                (r"5 + 6 = 11",  "odd"),
                (r"49 + 50 = 99","odd"),
            ]
            ex_mobs = []
            for i, (expr, note) in enumerate(examples):
                row = VGroup(
                    math_obj(expr, font_size=30),
                    Text(note, font="Poppins",
                         font_size=22, color=ORANGE_HL),
                ).arrange(RIGHT, buff=0.3)
                row.move_to(LEFT * 3.8 + UP * (1.0 - i * 0.75))
                check_safe_margins(row, f"ex_row_{i}")
                self.play(FadeIn(row), run_time=0.5)
                active_mobs.append(row)
                ex_mobs.append(row)

            self.wait_until_bookmark("bk_confidence")

            conf_card = make_concept_card(
                "Examples give confidence — not certainty.",
                position=RIGHT * 2.8 + UP * 0.8,
                font_size=24,
            )
            check_safe_margins(conf_card, "conf_card")
            self.play(FadeIn(conf_card), run_time=0.6)
            active_mobs.append(conf_card)

            self.wait_until_bookmark("bk_prove")

            prove_card = make_concept_card(
                "To prove it for ALL pairs, use a variable-based model.",
                position=RIGHT * 2.8 + DOWN * 0.5,
                font_size=24,
            )
            check_safe_margins(prove_card, "prove_card")
            check_y_gap(prove_card, active_mobs, name="prove_card")
            self.play(FadeIn(prove_card), run_time=0.6)
            active_mobs.append(prove_card)

        self.wait(0.4)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── GENERALISE METHOD ────────────────────────────────────────

    def show_generalise_method(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        with self.voiceover(
            text=(
                '<bookmark mark="bk_method"/>To generalise a pattern, — we represent '
                'the varying quantity with a letter-number, — construct a model that '
                'captures the relationship, — and use algebra to show the result holds '
                'in every case.'
            )
        ) as tracker:

            self.wait_until_bookmark("bk_method")

            # Three-step flow — Pattern B
            steps_data = [
                ("1", "Represent",
                 "Let the varying quantity\nbe a letter-number."),
                ("2", "Construct",
                 "Build the algebraic model\nfor the relationship."),
                ("3", "Prove",
                 "Use algebra to show\nit holds for all cases."),
            ]

            step_mobs = []
            for i, (num, head, body) in enumerate(steps_data):
                x_pos = (i - 1) * 4.0

                num_circ = Circle(radius=0.38, color=ORANGE_HL,
                                  fill_color=ORANGE_HL,
                                  fill_opacity=1,
                                  stroke_width=0)
                num_lbl = Text(num, font="Poppins", font_size=26,
                               color=WHITE)
                num_lbl.move_to(num_circ.get_center())
                icon = VGroup(num_circ, num_lbl)

                head_txt = Text(head, font="Poppins",
                                font_size=24, color=ORANGE_HL,
                                )
                body_txt = Text(body, font="Poppins",
                                font_size=20, color=PURPLE)

                col = VGroup(icon, head_txt, body_txt).arrange(
                    DOWN, buff=0.18)
                col.move_to(RIGHT * x_pos + DOWN * 0.2)
                check_safe_margins(col, f"step_col_{i}")
                step_mobs.append(col)

            self.play(FadeIn(step_mobs[0]), run_time=0.6)
            active_mobs.append(step_mobs[0])

            # Arrows between steps
            for i in range(2):
                arr = Arrow(
                    start=step_mobs[i].get_right() + RIGHT * 0.1,
                    end=step_mobs[i + 1].get_left() + LEFT * 0.1,
                    color=PALE_PURPLE, stroke_width=2.0,
                    tip_length=0.18, buff=0.05
                )
                self.play(
                    Create(arr),
                    FadeIn(step_mobs[i + 1]),
                    run_time=0.6
                )
                active_mobs.extend([arr, step_mobs[i + 1]])

        self.wait(0.4)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── CONSECUTIVE PROOF ────────────────────────────────────────

    def show_consecutive_proof(self):
        active_mobs = []
        self.camera.background_color = LAVENDER_BG

        badge = create_heading_badge("Concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        with self.voiceover(
            text=(
                '<bookmark mark="bk_let_n"/>For two consecutive numbers, — let the '
                'first be n. '
                '<bookmark mark="bk_next"/>The next consecutive number is always n plus one. '
                '<bookmark mark="bk_sum"/>Their sum is n plus n plus one, '
                'which equals two n plus one. '
                '<bookmark mark="bk_even"/>We say a number is even when it is a multiple '
                'of two. So two n is always even. '
                '<bookmark mark="bk_odd"/>Adding one to any even number always gives '
                'an odd number. '
                '<bookmark mark="bk_conclude"/>Therefore, the sum of any two consecutive '
                'numbers is always odd. '
                'This is not a coincidence — it is proved for all values of n at once.'
            )
        ) as tracker:

            self.wait_until_bookmark("bk_let_n")

            # Define n
            n_def = VGroup(
                Text("Let first number:", font="Poppins",
                     font_size=26, color=PURPLE),
                math_obj(r"n", font_size=38, color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.25)
            n_def.move_to(UP * 2.2)
            check_safe_margins(n_def, "n_def")
            self.play(FadeIn(n_def), run_time=0.6)
            active_mobs.append(n_def)

            self.wait_until_bookmark("bk_next")

            next_def = VGroup(
                Text("Next number:", font="Poppins",
                     font_size=26, color=PURPLE),
                math_obj(r"n + 1", font_size=38, color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.25)
            next_def.move_to(UP * 1.4)
            check_safe_margins(next_def, "next_def")
            check_y_gap(next_def, active_mobs, name="next_def")
            self.play(FadeIn(next_def), run_time=0.6)
            active_mobs.append(next_def)

            self.wait_until_bookmark("bk_sum")

            # Pattern F: sum expression
            t_n1   = math_obj(r"n", font_size=40)
            t_pl   = math_obj(r"+", font_size=40)
            t_np1  = math_obj(r"(n+1)", font_size=40)
            t_eq   = math_obj(r"=", font_size=40)
            t_2np1 = math_obj(r"2n+1", font_size=40, color=ORANGE_HL)

            sum_row = VGroup(
                t_n1, t_pl, t_np1, t_eq, t_2np1
            ).arrange(RIGHT, buff=0.14)
            sum_row.move_to(UP * 0.4)
            check_safe_margins(sum_row, "sum_row")
            check_y_gap(sum_row, active_mobs, name="sum_row")
            self.play(FadeIn(sum_row), run_time=0.7)
            active_mobs.append(sum_row)

            self.wait_until_bookmark("bk_even")

            even_card = make_concept_card(
                "2n is always even (multiple of 2).",
                position=DOWN * 0.5,
                font_size=24,
            )
            check_safe_margins(even_card, "even_card")
            check_y_gap(even_card, active_mobs, name="even_card")
            self.play(FadeIn(even_card), run_time=0.6)
            active_mobs.append(even_card)

            self.wait_until_bookmark("bk_odd")

            odd_card = make_concept_card(
                "even + 1 = odd, always.",
                position=DOWN * 1.4,
                font_size=24,
            )
            check_safe_margins(odd_card, "odd_card")
            check_y_gap(odd_card, active_mobs, name="odd_card")
            self.play(FadeIn(odd_card), run_time=0.6)
            active_mobs.append(odd_card)

            self.wait_until_bookmark("bk_conclude")

            concl_bg = RoundedRectangle(
                corner_radius=0.2, width=8.5, height=0.75,
                fill_color=WHITE, fill_opacity=0.9,
                stroke_color=ORANGE_HL, stroke_width=2.5
            )
            concl_bg.move_to(DOWN * 2.35)
            concl_txt = Text(
                "Sum of any two consecutive numbers is always ODD.",
                font="Poppins", font_size=22, color=PURPLE
            )
            concl_txt.move_to(concl_bg.get_center())
            concl_card = VGroup(concl_bg, concl_txt)
            check_safe_margins(concl_card, "concl_card")
            check_y_gap(concl_card, active_mobs, name="concl_card")
            self.play(FadeIn(concl_card), run_time=0.7)
            active_mobs.append(concl_card)

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
                '<bookmark mark="bk_q"/>Show that the sum of three consecutive numbers '
                'is always a multiple of three.'
            )
        ) as tracker:

            self.wait_until_bookmark("bk_q")

            q_lbl = Text(
                "Show that:",
                font="Poppins", font_size=28, color=PURPLE
            )
            q_lbl.move_to(UP * 1.8)
            check_safe_margins(q_lbl, "q_lbl")
            self.play(FadeIn(q_lbl), run_time=0.5)
            active_mobs.append(q_lbl)

            q_stmt_bg = RoundedRectangle(
                corner_radius=0.2, width=9.0, height=1.1,
                fill_color=WHITE, fill_opacity=0.9,
                stroke_color=PALE_PURPLE, stroke_width=1.5
            )
            q_stmt_bg.move_to(UP * 0.8)
            q_stmt_txt = Text(
                "Sum of three consecutive numbers is always a multiple of 3.",
                font="Poppins", font_size=24, color=PURPLE
            )
            q_stmt_txt.move_to(q_stmt_bg.get_center())
            q_stmt = VGroup(q_stmt_bg, q_stmt_txt)
            check_safe_margins(q_stmt, "q_stmt")
            check_y_gap(q_stmt, active_mobs, name="q_stmt")
            self.play(FadeIn(q_stmt), run_time=0.7)
            active_mobs.append(q_stmt)

            # Show three consecutive number boxes as hint
            boxes = VGroup()
            labels = [r"n", r"n+1", r"n+2"]
            for i, lbl in enumerate(labels):
                rect = RoundedRectangle(
                    corner_radius=0.12,
                    width=1.4, height=0.9,
                    fill_color=ORANGE_HL if i == 0 else PURPLE,
                    fill_opacity=0.15,
                    stroke_color=ORANGE_HL if i == 0 else PURPLE,
                    stroke_width=2.0
                )
                txt = math_obj(lbl, font_size=32,
                               color=ORANGE_HL if i == 0 else PURPLE)
                txt.move_to(rect.get_center())
                boxes.add(VGroup(rect, txt))

            boxes.arrange(RIGHT, buff=0.35)
            boxes.move_to(DOWN * 0.6)
            check_safe_margins(boxes, "boxes")
            check_y_gap(boxes, active_mobs, name="boxes")
            self.play(FadeIn(boxes), run_time=0.7)
            active_mobs.append(boxes)

            sum_hint = VGroup(
                math_obj(r"n", font_size=28, color=ORANGE_HL),
                math_obj(r"+", font_size=28),
                math_obj(r"(n+1)", font_size=28, color=PURPLE),
                math_obj(r"+", font_size=28),
                math_obj(r"(n+2)", font_size=28, color=PURPLE),
                math_obj(r"= \, ?", font_size=28),
            ).arrange(RIGHT, buff=0.12)
            sum_hint.move_to(DOWN * 1.85)
            check_safe_margins(sum_hint, "sum_hint")
            check_y_gap(sum_hint, active_mobs, name="sum_hint")
            self.play(FadeIn(sum_hint), run_time=0.6)
            active_mobs.append(sum_hint)

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
                '<bookmark mark="bk_s1"/>Let the first number be n. '
                '<bookmark mark="bk_s2"/>The three consecutive numbers are n, '
                'n plus one, and n plus two. '
                '<bookmark mark="bk_s3"/>Their sum is n plus n plus one plus n plus two, '
                'which equals three n plus three. '
                '<bookmark mark="bk_s4"/>Factor — three times the quantity n plus one. '
                '<bookmark mark="bk_s5"/>This is always a multiple of three, '
                'for any value of n. Proved.'
            )
        ) as tracker:

            mgr = StepManager(
                self,
                start_anchor=UP * 2.0 + LEFT * 0.5,
                font_size=28,
                buff=0.40
            )

            # Step 1: let n be first
            self.wait_until_bookmark("bk_s1")
            s1 = VGroup(
                Text("Let first number:", font="Poppins",
                     font_size=26, color=PURPLE),
                math_obj(r"n", font_size=32, color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.2)
            mgr.add_step(s1)
            active_mobs.append(s1)

            # Step 2: three consecutive numbers
            self.wait_until_bookmark("bk_s2")
            s2 = VGroup(
                math_obj(r"n,", font_size=30, color=ORANGE_HL),
                math_obj(r"n+1,", font_size=30, color=PURPLE),
                math_obj(r"n+2", font_size=30, color=PURPLE),
            ).arrange(RIGHT, buff=0.18)
            mgr.add_step(s2)
            active_mobs.append(s2)

            # Step 3: compute sum
            self.wait_until_bookmark("bk_s3")
            s3 = VGroup(
                math_obj(r"n", font_size=28),
                math_obj(r"+", font_size=28),
                math_obj(r"(n+1)", font_size=28),
                math_obj(r"+", font_size=28),
                math_obj(r"(n+2)", font_size=28),
                math_obj(r"=", font_size=28),
                math_obj(r"3n+3", font_size=28, color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.12)
            mgr.add_step(s3)
            active_mobs.append(s3)

            # Step 4: factor
            self.wait_until_bookmark("bk_s4")
            s4 = VGroup(
                math_obj(r"=", font_size=32),
                math_obj(r"3", font_size=32, color=ORANGE_HL),
                math_obj(r"(n+1)", font_size=32, color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.14)
            mgr.add_step(s4)
            active_mobs.append(s4)

            ans_box = SurroundingRectangle(
                s4, color=ORANGE_HL,
                corner_radius=0.15,
                stroke_width=2.5,
                buff=0.15
            )
            self.play(Create(ans_box), run_time=0.5)
            active_mobs.append(ans_box)

            # Step 5: proved statement
            self.wait_until_bookmark("bk_s5")
            proved_bg = RoundedRectangle(
                corner_radius=0.18, width=7.5, height=0.72,
                fill_color=WHITE, fill_opacity=0.9,
                stroke_color=ORANGE_HL, stroke_width=2.5
            )
            proved_row = VGroup(
                Text("Multiple of 3 for any n.",
                     font="Poppins", font_size=24, color=PURPLE),
                MathTex(r"\checkmark",
                        tex_template=TexFontTemplates.gnu_freesans_tx,
                        font_size=34, color=ORANGE_HL),
                Text("Proved", font="Poppins", font_size=24,
                     color=ORANGE_HL),
            ).arrange(RIGHT, buff=0.3)

            # Place proved block below StepManager stack
            last_step = s4
            proved_bg.next_to(last_step, DOWN, buff=0.65)
            proved_row.move_to(proved_bg.get_center())
            proved_card = VGroup(proved_bg, proved_row)
            check_safe_margins(proved_card, "proved_card")
            check_y_gap(proved_card, active_mobs, name="proved_card")
            self.play(FadeIn(proved_card), run_time=0.7)
            active_mobs.append(proved_card)

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
            "Use a letter-number to represent the general case, not just specific values.",
            "Build the algebraic model, then simplify to reveal the pattern.",
            "A proof using letter-numbers holds for all valid values simultaneously.",
        ]
        positions = [UP * 1.5, ORIGIN, DOWN * 1.5]

        with self.voiceover(
            text=(
                '<bookmark mark="bk_sum1"/>Use a letter-number to represent the general case, '
                'not just specific values. '
                '<bookmark mark="bk_sum2"/>Build the algebraic model, then simplify '
                'to reveal the pattern. '
                '<bookmark mark="bk_sum3"/>A proof using letter-numbers holds for all '
                'valid values simultaneously.'
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