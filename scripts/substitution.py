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
Slow down on variables and formulas. Emphasize final answers.
Read the script EXACTLY. No filler. No improvisation.
"""


def create_heading_badge(text_str):
    t = Text(text_str, font="Poppins", font_size=28,
             color=WHITE)
    bg = RoundedRectangle(
        corner_radius=0.2, width=t.width + 0.6,
        height=t.height + 0.3,
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
        v = MathTex(var_tex,
                    tex_template=TexFontTemplates.gnu_freesans_tx,
                    font_size=20, color=ORANGE_HL)
        d = Text(def_str, font="Poppins", font_size=20, color=PURPLE)
        rows.append(VGroup(v, d).arrange(RIGHT, buff=0.1))
    content = VGroup(*rows).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
    bg = RoundedRectangle(
        corner_radius=0.15,
        width=content.width + 0.4,
        height=content.height + 0.3,
        fill_color=WHITE, fill_opacity=0.85,
        stroke_color=PALE_PURPLE, stroke_width=1.0)
    bg.move_to(content)
    g = VGroup(bg, content)
    if position is not None:
        g.to_corner(position, buff=buff)
    return g


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
    txt = Text(text_str, font="Poppins",
               font_size=font_size, color=PURPLE)
    bg = RoundedRectangle(
        corner_radius=0.2,
        width=min(txt.width + 0.8, 10.5),
        height=txt.height + 0.4,
        fill_color=WHITE, fill_opacity=0.85,
        stroke_color=PALE_PURPLE, stroke_width=1.5)
    bg.move_to(position)
    txt.move_to(bg.get_center())
    return VGroup(bg, txt)


def make_bullet_point(text_str, position=ORIGIN,
                      font_size=24, max_chars=50):
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


def clear_and_transition(scene, active_mobs, new_bg,
                         ft=0.8, buf=0.2, settle=0.1):
    if active_mobs:
        scene.play(*[FadeOut(m) for m in active_mobs],
                   run_time=ft)
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
    if   mob.get_left()[0]   < SAFE_L:
        sx = SAFE_L - mob.get_left()[0]
    elif mob.get_right()[0]  > SAFE_R:
        sx = SAFE_R - mob.get_right()[0]
    if   mob.get_bottom()[1] < SAFE_B:
        sy = SAFE_B - mob.get_bottom()[1]
    elif mob.get_top()[1]    > SAFE_T:
        sy = SAFE_T - mob.get_top()[1]
    if sx or sy:
        mob.shift(RIGHT * sx + UP * sy)
    return mob


def check_y_gap(new_mob, existing_mobs,
                min_gap=0.3, name="new_mob"):
    for mob in existing_mobs:
        if isinstance(mob, VGroup) and len(mob) == 0:
            continue
        nb = new_mob.get_bottom()[1]
        nt = new_mob.get_top()[1]
        mt = mob.get_top()[1]
        mb = mob.get_bottom()[1]
        if nb < mt and nt > mb:
            sh = mt + min_gap - nb
            new_mob.shift(UP * sh)
        elif nb >= mt and (nb - mt) < min_gap:
            sh = min_gap - (nb - mt)
            new_mob.shift(UP * sh)
    return new_mob


def build_expr_row(terms, font_size=32):
    """
    Build a split expression as separate MathTex objects.
    Returns dict: {key: MathTex, ..., 'row': VGroup}
    ✅ Use for any expression needing selective highlighting.
    ❌ Never use single MathTex when parts need set_color().
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


class StepManager:
    LIMITS = {(32, 0.4): 3, (28, 0.3): 4,
              (24, 0.25): 5, (20, 0.2): 6}

    def __init__(self, scene, start_anchor=None,
                 font_size=28, buff=0.3):
        self.scene  = scene
        self.steps  = []
        self.fs     = font_size
        self.buff   = buff
        self.max    = self.LIMITS.get((font_size, buff), 4)
        # ✅ explicit None check — never `or` on numpy arrays
        self.anchor = (
            start_anchor if start_anchor is not None
            else (UP * 2.0 + LEFT * 3.5)
        )

    def add_step(self, mob, run_time=0.7):
        if len(self.steps) >= self.max:
            print(f"WARNING: StepManager at limit ({self.max}).")
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
            self.scene.play(
                *[FadeOut(s) for s in self.steps],
                run_time=rt)
            self.steps.clear()

    def get_all(self):
        return VGroup(*self.steps)


# ══════════════════════════════════════════════════════════
class SubstitutionScene(VoiceoverScene):

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

    # ── TITLE ─────────────────────────────────────────────
    def show_title(self):
        active_mobs = []
        with self.voiceover(
            text='<bookmark mark="bk_hello"/>Hello students!'
        ) as tracker:
            self.wait_until_bookmark("bk_hello")
            self.camera.background_color = PURPLE
            topic = Text(
                "Substitution in Algebraic Expressions",
                font="Poppins", font_size=36,
                color=WHITE)
            topic.move_to(ORIGIN)
            check_safe_margins(topic, "title")
            self.play(FadeIn(topic), run_time=0.8)
            active_mobs.append(topic)
        self.wait(0.4)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── CONCEPT ───────────────────────────────────────────
    def show_concept(self):
        active_mobs = []
        badge = create_heading_badge("Concept")
        check_safe_margins(badge, "badge_concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)
        self._concept_hook(active_mobs)
        self._concept_steps(active_mobs)
        self._concept_worked(active_mobs)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── CONCEPT PART A: hook + definition ─────────────────
    def _concept_hook(self, active_mobs):
        with self.voiceover(
            text=(
                'Suppose your pocket money each week is calculated as '
                'five times the number of chores completed, '
                'plus ten rupees. '
                'If you completed six chores this week, '
                '<bookmark mark="bk_replace"/>you simply replace '
                'the unknown with six and calculate. '
                'This process — replacing a letter-number with a '
                'specific value to find the result — '
                '<bookmark mark="bk_sub_def"/>is called substitution.'
            )
        ) as tracker:
            # hook card
            hook = make_concept_card(
                "Pocket money = 5 x chores + 10",
                position=UP * 1.2, font_size=26)
            check_safe_margins(hook, "hook_card")
            self.play(FadeIn(hook), run_time=0.7)
            active_mobs.append(hook)

            # Pattern F — 5c + 10, replace c with 6
            self.wait_until_bookmark("bk_replace")
            pe = build_expr_row([
                ("p5",  r"5"),
                ("pc",  r"c"),
                ("ppl", r"+"),
                ("p10", r"10"),
            ], font_size=32)
            pe["row"].move_to(ORIGIN)
            check_safe_margins(pe["row"], "pocket_expr")
            self.play(FadeIn(pe["row"]), run_time=0.7)
            active_mobs.append(pe["row"])

            # highlight c then replace IN PLACE
            self.play(
                pe["pc"].animate.set_color(ORANGE_HL),
                run_time=0.5)
            c_replaced = math_obj(r"6", color=ORANGE_HL,
                                  font_size=32)
            c_replaced.move_to(pe["pc"].get_center())
            self.play(
                ReplacementTransform(pe["pc"], c_replaced),
                run_time=0.6)
            active_mobs.append(c_replaced)

            # result
            result_p = math_obj(r"= 5 \times 6 + 10 = 40",
                                 color=ORANGE_HL, font_size=30)
            result_p.next_to(pe["row"], DOWN, buff=0.45)
            check_safe_margins(result_p, "result_pocket")
            self.play(FadeIn(result_p), run_time=0.6)
            active_mobs.append(result_p)

            # definition card
            self.wait_until_bookmark("bk_sub_def")
            self.play(
                FadeOut(pe["row"]), FadeOut(c_replaced),
                FadeOut(result_p), FadeOut(hook),
                run_time=0.5)
            for item in [pe["row"], c_replaced,
                         result_p, hook]:
                if item in active_mobs:
                    active_mobs.remove(item)

            def_card = make_concept_card(
                "Substitution: replace a letter-number"
                " with a specific value.",
                position=UP * 0.5, font_size=24)
            check_safe_margins(def_card, "def_card")
            self.play(FadeIn(def_card), run_time=0.7)
            active_mobs.append(def_card)

    # ── CONCEPT PART B: three steps ───────────────────────
    def _concept_steps(self, active_mobs):
        with self.voiceover(
            text=(
                '<bookmark mark="bk_three_steps"/>To evaluate an expression '
                'by substitution, follow three steps. '
                '<bookmark mark="bk_step1"/>Write the expression clearly. '
                '<bookmark mark="bk_step2"/>Replace every letter-number '
                'with its given value. '
                'Then simplify using the correct order of operations — '
                '<bookmark mark="bk_step3"/>brackets first, then '
                'multiplication and division, then addition and subtraction. '
                '<bookmark mark="bk_matters"/>Showing each step clearly matters. '
                'It allows you to check your working and justify your '
                'reasoning — a correct result with no working shown '
                'cannot be verified.'
            )
        ) as tracker:
            # clear previous def card
            to_clear = [m for m in active_mobs
                        if m is not active_mobs[0]]
            if to_clear:
                self.play(*[FadeOut(m) for m in to_clear],
                          run_time=0.4)
                for m in to_clear:
                    active_mobs.remove(m)

            self.wait_until_bookmark("bk_three_steps")
            heading = make_concept_card(
                "3 Steps to Evaluate by Substitution",
                position=UP * 2.1, font_size=24)
            check_safe_margins(heading, "steps_heading")
            self.play(FadeIn(heading), run_time=0.6)
            active_mobs.append(heading)

            self.wait_until_bookmark("bk_step1")
            s1_card = make_concept_card(
                "Step 1: Write the expression clearly.",
                position=UP * 0.9, font_size=24)
            check_safe_margins(s1_card, "s1_card")
            self.play(FadeIn(s1_card), run_time=0.6)
            active_mobs.append(s1_card)

            self.wait_until_bookmark("bk_step2")
            s2_card = make_concept_card(
                "Step 2: Replace every letter-number"
                " with its given value.",
                position=DOWN * 0.3, font_size=24)
            check_safe_margins(s2_card, "s2_card")
            self.play(FadeIn(s2_card), run_time=0.6)
            active_mobs.append(s2_card)

            self.wait_until_bookmark("bk_step3")
            s3_card = make_concept_card(
                "Step 3: Simplify using BODMAS order.",
                position=DOWN * 1.5, font_size=24)
            check_safe_margins(s3_card, "s3_card")
            self.play(FadeIn(s3_card), run_time=0.6)
            active_mobs.append(s3_card)

            self.wait_until_bookmark("bk_matters")
            self.play(
                FadeOut(heading), FadeOut(s1_card),
                FadeOut(s2_card), FadeOut(s3_card),
                run_time=0.5)
            for item in [heading, s1_card, s2_card, s3_card]:
                if item in active_mobs:
                    active_mobs.remove(item)

            warn_card = make_concept_card(
                "Show every step — a result without"
                " working cannot be verified.",
                position=UP * 0.5, font_size=24)
            check_safe_margins(warn_card, "warn_card")
            self.play(FadeIn(warn_card), run_time=0.6)
            active_mobs.append(warn_card)

    # ── CONCEPT PART C: worked example 5x−3, x=4 ─────────
    def _concept_worked(self, active_mobs):
        with self.voiceover(
            text=(
                'For example, to evaluate five x minus three '
                'when x equals four: '
                '<bookmark mark="bk_ex_replace"/>replace x with four. '
                'Five times four minus three, '
                '<bookmark mark="bk_ex_result"/>equals twenty minus three, '
                'which equals seventeen.'
            )
        ) as tracker:
            # clear warn card
            to_clear = [m for m in active_mobs
                        if m is not active_mobs[0]]
            if to_clear:
                self.play(*[FadeOut(m) for m in to_clear],
                          run_time=0.4)
                for m in to_clear:
                    active_mobs.remove(m)

            # Pattern F — 5x − 3
            we = build_expr_row([
                ("w5",  r"5"),
                ("wx",  r"x"),
                ("wm",  r"-"),
                ("w3",  r"3"),
            ], font_size=34)
            we["wm"].set_stroke(width=2.0)
            we["row"].move_to(UP * 1.2)
            check_safe_margins(we["row"], "worked_expr")
            self.play(FadeIn(we["row"]), run_time=0.7)
            active_mobs.append(we["row"])

            # highlight x, replace IN PLACE with 4
            self.wait_until_bookmark("bk_ex_replace")
            self.play(
                we["wx"].animate.set_color(ORANGE_HL),
                run_time=0.5)
            x_val = math_obj(r"4", color=ORANGE_HL, font_size=34)
            x_val.move_to(we["wx"].get_center())
            self.play(
                ReplacementTransform(we["wx"], x_val),
                run_time=0.6)
            active_mobs.append(x_val)

            # result rows
            self.wait_until_bookmark("bk_ex_result")
            row_mid = build_expr_row([
                ("eq1", r"="),
                ("r20", r"20"),
                ("rm",  r"-"),
                ("r3b", r"3"),
            ], font_size=34)
            row_mid["rm"].set_stroke(width=2.0)
            row_mid["row"].next_to(we["row"], DOWN, buff=0.45)
            check_safe_margins(row_mid["row"], "row_mid")
            self.play(FadeIn(row_mid["row"]), run_time=0.6)
            active_mobs.append(row_mid["row"])

            row_final = build_expr_row([
                ("eq2", r"="),
                ("r17", r"17"),
            ], font_size=34)
            row_final["r17"].set_color(ORANGE_HL)
            row_final["row"].next_to(row_mid["row"],
                                     DOWN, buff=0.35)
            check_safe_margins(row_final["row"], "row_final")
            self.play(FadeIn(row_final["row"]), run_time=0.6)
            active_mobs.append(row_final["row"])

    # ── QUESTION ──────────────────────────────────────────
    def show_question(self):
        active_mobs = []
        badge = create_heading_badge("Question")
        check_safe_margins(badge, "badge_q")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        with self.voiceover(
            text=(
                '<bookmark mark="bk_question"/>Evaluate the expression '
                'four p plus three q minus two, '
                'when p equals five and q equals three.'
            )
        ) as tracker:
            self.wait_until_bookmark("bk_question")
            q_text = Text(
                "Evaluate: 4p + 3q - 2,  p = 5,  q = 3",
                font="Poppins", font_size=26, color=PURPLE)
            q_text.move_to(UP * 2.5)
            check_safe_margins(q_text, "q_text")
            self.play(FadeIn(q_text), run_time=0.7)
            active_mobs.append(q_text)

            # Pattern F figure: 4p + 3q − 2
            qe = build_expr_row([
                ("q4p",  r"4p"),
                ("qpl",  r"+"),
                ("q3q",  r"3q"),
                ("qmn",  r"-"),
                ("q2",   r"2"),
            ], font_size=32)
            qe["qmn"].set_stroke(width=2.0)
            qe["row"].move_to(ORIGIN)
            check_safe_margins(qe["row"], "q_expr")
            self.play(FadeIn(qe["row"]), run_time=0.8)
            active_mobs.append(qe["row"])

            given = Text(
                "p = 5,   q = 3",
                font="Poppins", font_size=22, color=PURPLE)
            given.next_to(qe["row"], DOWN, buff=0.55)
            check_safe_margins(given, "given_vals")
            self.play(FadeIn(given), run_time=0.5)
            active_mobs.append(given)

        self._q_expr_row = qe["row"]
        self._given_text = given
        self._active_from_question = active_mobs

    # ── SOLUTION ──────────────────────────────────────────
    def show_solution(self):
        active_mobs = list(self._active_from_question)

        # shift figure + given label together
        self.play(
            self._q_expr_row.animate.move_to(
                RIGHT * 3.2 + UP * 0.4),
            self._given_text.animate.move_to(
                RIGHT * 3.2 + DOWN * 0.3),
            run_time=1.0)

        # swap badge
        badge_old = active_mobs[0]
        badge_new = create_heading_badge("Solution")
        self.play(
            FadeOut(badge_old), FadeIn(badge_new),
            run_time=0.5)
        active_mobs[0] = badge_new

        with self.voiceover(
            text=(
                '<bookmark mark="bk_s1"/>Replace p with five '
                'and q with three. '
                '<bookmark mark="bk_s2"/>Four times five, plus '
                'three times three, minus two. '
                '<bookmark mark="bk_s3"/>Twenty plus nine minus two. '
                '<bookmark mark="bk_s4"/>The answer is twenty-seven. '
                'Now write each step clearly: the substitution first, '
                'then the multiplication, '
                '<bookmark mark="bk_justify"/>then the addition '
                'and subtraction. '
                'This justifies every part of your working.'
            )
        ) as tracker:
            # 4 steps at (28, 0.3) → max 4 ✅
            mgr = StepManager(
                self,
                start_anchor=UP * 2.0 + LEFT * 3.5,
                font_size=28, buff=0.3)

            # step 1 — substitution
            self.wait_until_bookmark("bk_s1")
            s1 = math_obj(
                r"4(5) + 3(3) - 2",
                font_size=28)
            s1.set_stroke(width=2.0)
            mgr.add_step(s1)
            active_mobs.append(s1)

            # step 2 — multiply
            self.wait_until_bookmark("bk_s2")
            s2 = math_obj(
                r"20 + 9 - 2",
                font_size=28)
            s2.set_stroke(width=2.0)
            mgr.add_step(s2)
            active_mobs.append(s2)

            # step 3 — add
            self.wait_until_bookmark("bk_s3")
            s3 = math_obj(
                r"29 - 2",
                font_size=28)
            s3.set_stroke(width=2.0)
            mgr.add_step(s3)
            active_mobs.append(s3)

            # step 4 — final answer
            self.wait_until_bookmark("bk_s4")
            s4 = math_obj(
                r"= 27",
                font_size=28, color=ORANGE_HL)
            mgr.add_step(s4)
            active_mobs.append(s4)

            # justify caption
            self.wait_until_bookmark("bk_justify")
            just_card = make_concept_card(
                "Justify: substitution first,"
                " then multiply, then add/subtract.",
                position=DOWN * 2.3, font_size=20)
            check_safe_margins(just_card, "just_card")
            self.play(FadeIn(just_card), run_time=0.6)
            active_mobs.append(just_card)

            # legend
            legend = make_legend(
                [("p", "= 5"),
                 ("q", "= 3")],
                position=DR, buff=0.4)
            check_safe_margins(legend, "legend")
            self.play(FadeIn(legend), run_time=0.6)
            active_mobs.append(legend)

        self.wait(0.6)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── SUMMARY ───────────────────────────────────────────
    def show_summary(self):
        active_mobs = []
        badge = create_heading_badge("Summary")
        check_safe_margins(badge, "badge_sum")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        summary_points = [
            "Substitution means replacing each letter-number"
            " with its given numerical value.",
            "Apply the correct order of operations"
            " after substituting.",
            "Show every step clearly to justify"
            " and verify the result.",
        ]
        positions = [UP * 1.5, ORIGIN, DOWN * 1.5]

        with self.voiceover(
            text=(
                '<bookmark mark="bk_sum1"/>Substitution means replacing '
                'each letter-number with its given numerical value. '
                '<bookmark mark="bk_sum2"/>Apply the correct order of '
                'operations after substituting. '
                '<bookmark mark="bk_sum3"/>Show every step clearly to '
                'justify and verify the result.'
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