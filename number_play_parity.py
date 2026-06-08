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
    base_url = "https://raw.githubusercontent.com/google/fonts/main/ofl/poppins/"
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
        print(f"WARNING Bookmark '{mark}' NOT FOUND in: {scene_text}...")
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

TTS_INSTRUCTIONS = """
Voice & Personality:
You are a warm, patient, and encouraging mathematics teacher speaking
to a middle-school student. Your tone is friendly, calm, and confident
never rushed, never robotic. You sound like a human explainer in a
Khan Academy or 3Blue1Brown style video. The voice profile is shimmer
bright, warm, and slightly playful.

Pacing:
Speak at a MODERATE-TO-SLOW pace. Honor the commas, dashes, and
ellipses in the script they are deliberate pacing marks placed by
the director.

Variables and Math Terms:
When pronouncing single-letter variables like x, y, z, a, b, c, h, r,
or t, slow down noticeably and articulate each letter clearly with a
brief micro-pause before and after it.

Formulas:
Slow down further on equations. Pause between each component so the
student can match the spoken word to the symbol on screen.

Numbers and Units:
Pronounce numbers clearly. For units like centimeter square or
meter cube, say them with a confident, deliberate cadence.

Emphasis:
Naturally emphasize key terms: shape names, formulas, the final
answer, and any word that introduces a new concept.

Pauses:
Beat at commas, medium pause at dashes, dramatic pause at ellipses.
After stating a final answer, pause for a moment before continuing.

Mood:
Encouraging, curious, and warm. Avoid monotone. Add gentle warmth.

Do NOT:
- Do not race through sentences.
- Do not flatten your voice into monotone.
- Do not add filler words or commentary not in the script.
- Do not improvise or paraphrase, read the script exactly.
"""


# ============================================================
# COSEC TEMPLATE — gnu_freesans_tx base + \cosec declaration
# Uses confirmed attribute name: .preamble
# ============================================================
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


# ============================================================
# HELPERS
# ============================================================
def create_heading_badge(text_str):
    t = Text(text_str, font="Poppins", font_size=28, color=WHITE, weight=BOLD)
    badge = RoundedRectangle(
        corner_radius=0.2,
        width=t.width + 0.6,
        height=t.height + 0.3,
        fill_color=PURPLE,
        fill_opacity=1,
        stroke_width=0,
    )
    badge.move_to(t)
    return VGroup(badge, t).to_corner(UL, buff=0.3)


def math_obj(tex_str, color=PURPLE, font_size=36):
    return MathTex(
        tex_str,
        tex_template=TexFontTemplates.gnu_freesans_tx,
        color=color,
        font_size=font_size,
    )


def dot_pair(c1=PURPLE, c2=PURPLE, r=0.17):
    d1 = Circle(radius=r, color=c1, fill_opacity=1,
                fill_color=c1, stroke_width=0)
    d2 = Circle(radius=r, color=c2, fill_opacity=1,
                fill_color=c2, stroke_width=0)
    return VGroup(d1, d2).arrange(RIGHT, buff=0.13)


def fade_all(scene, *mobs, rt=0.8):
    targets = [m for m in mobs if m is not None]
    if targets:
        scene.play(*[FadeOut(m) for m in targets], run_time=rt)


# ============================================================
# MAIN SCENE
# ============================================================
class NumberPlayParity(VoiceoverScene):

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

        # ============================================================
        # SEGMENT 1 — HOOK
        # ============================================================
        with self.voiceover(
            text=(
                '<bookmark mark="bk_title"/>Hello students! '
                '<bookmark mark="bk_pencils"/>Imagine arranging your pencils into pairs on your desk. '
                'Sometimes every pencil finds a partner, '
                'and <bookmark mark="bk_leftover"/>sometimes one is left behind. '
                '<bookmark mark="bk_why_q"/>Why does that happen with some numbers — and not others?'
            )
        ) as tracker:

            # Title slide
            self.wait_until_bookmark("bk_title")
            self.camera.background_color = PURPLE
            title = Text(
                "Number Play",
                font="Poppins", font_size=56, color=WHITE, weight=BOLD,
            ).move_to(UP * 0.4)
            subtitle = Text(
                "Parity",
                font="Poppins", font_size=36, color=WHITE,
            ).next_to(title, DOWN, buff=0.35)
            self.play(FadeIn(title), run_time=0.8)
            self.play(FadeIn(subtitle), run_time=0.6)

            # Switch to lavender; prompt line
            self.wait_until_bookmark("bk_pencils")
            self.play(FadeOut(title), FadeOut(subtitle), run_time=0.5)
            self.camera.background_color = LAVENDER_BG

            prompt = Text(
                "Imagine arranging pencils into pairs...",
                font="Poppins", font_size=30, color=PURPLE,
            ).move_to(UP * 2.7)
            self.play(FadeIn(prompt), run_time=0.7)

            # Three pencil pairs
            pencil_pairs = VGroup()
            pair_labels  = VGroup()
            for _ in range(3):
                p1 = Rectangle(width=0.22, height=0.85, color=PURPLE,
                               stroke_width=2, fill_opacity=0.25,
                               fill_color=PURPLE)
                p2 = Rectangle(width=0.22, height=0.85, color=PURPLE,
                               stroke_width=2, fill_opacity=0.25,
                               fill_color=PURPLE)
                pencil_pairs.add(VGroup(p1, p2).arrange(RIGHT, buff=0.13))
            pencil_pairs.arrange(RIGHT, buff=0.6).move_to(ORIGIN + UP * 0.3)
            self.play(FadeIn(pencil_pairs), run_time=0.8)

            for pair in pencil_pairs:
                lbl = Text("pair", font="Poppins", font_size=17, color=PURPLE)
                lbl.next_to(pair, DOWN, buff=0.15)
                pair_labels.add(lbl)
            self.play(FadeIn(pair_labels), run_time=0.6)

            # Lone leftover pencil
            self.wait_until_bookmark("bk_leftover")
            lone = Rectangle(
                width=0.22, height=0.85, color=ORANGE_HL,
                stroke_width=2, fill_opacity=0.4, fill_color=ORANGE_HL,
            )
            lone.next_to(pencil_pairs, RIGHT, buff=0.65)
            lone_lbl = Text(
                "leftover!", font="Poppins", font_size=17,
                color=ORANGE_HL, weight=BOLD,
            )
            lone_lbl.next_to(lone, DOWN, buff=0.15)
            self.play(FadeIn(lone), FadeIn(lone_lbl), run_time=0.7)
            self.play(Indicate(lone, color=ORANGE_HL, scale_factor=1.2), run_time=0.5)

            # Why question
            self.wait_until_bookmark("bk_why_q")
            why = Text(
                "Why does this happen with some numbers and not others?",
                font="Poppins", font_size=25, color=PURPLE,
            ).next_to(pencil_pairs, DOWN, buff=0.65)
            self.play(FadeIn(why), run_time=0.7)

        fade_all(self, prompt, pencil_pairs, pair_labels, lone, lone_lbl, why)

        # ============================================================
        # SEGMENT 2 — CONCEPT
        # ============================================================
        with self.voiceover(
            text=(
                '<bookmark mark="bk_parity"/>Parity — is the property of a whole number '
                'that tells us whether it can be split into two equal groups. '
                '<bookmark mark="bk_even"/>A number is defined as even — '
                'if it can be divided into two equal whole groups, with nothing left over. '
                '<bookmark mark="bk_odd"/>A number is defined as odd — if it cannot — '
                'one item is always left unpaired. '
                '<bookmark mark="bk_sum_concept"/>So even numbers are pairable, '
                'and odd numbers always have a leftover item.'
            )
        ) as tracker:

            badge_c = create_heading_badge("Concept")
            self.play(FadeIn(badge_c), run_time=0.6)

            # Parity definition lines
            self.wait_until_bookmark("bk_parity")
            def1 = Text(
                "Parity — property of a whole number",
                font="Poppins", font_size=26, color=PURPLE,
            ).move_to(UP * 1.9)
            def2 = Text(
                "tells us: can it split into two equal groups?",
                font="Poppins", font_size=26, color=PURPLE,
            ).next_to(def1, DOWN, buff=0.3)
            self.play(FadeIn(def1), run_time=0.7)
            self.play(FadeIn(def2), run_time=0.6)

            # Even visual
            self.wait_until_bookmark("bk_even")
            self.play(FadeOut(def1), FadeOut(def2), run_time=0.5)
            even_lbl = Text(
                "EVEN", font="Poppins", font_size=30, color=PURPLE, weight=BOLD,
            ).move_to(UP * 2.0)
            self.play(FadeIn(even_lbl), run_time=0.6)

            even_dots = VGroup(*[dot_pair() for _ in range(3)])
            even_dots.arrange(RIGHT, buff=0.5)
            even_dots.next_to(even_lbl, DOWN, buff=0.45)
            self.play(FadeIn(even_dots), run_time=0.7)

            even_note = Text(
                "Two equal groups — nothing left over",
                font="Poppins", font_size=24, color=PURPLE,
            ).next_to(even_dots, DOWN, buff=0.35)
            self.play(FadeIn(even_note), run_time=0.6)

            # Odd visual
            self.wait_until_bookmark("bk_odd")
            self.play(
                FadeOut(even_lbl), FadeOut(even_dots), FadeOut(even_note),
                run_time=0.5,
            )
            odd_lbl = Text(
                "ODD", font="Poppins", font_size=30, color=PURPLE, weight=BOLD,
            ).move_to(UP * 2.0)
            self.play(FadeIn(odd_lbl), run_time=0.6)

            odd_pairs = VGroup(*[dot_pair() for _ in range(2)])
            odd_pairs.arrange(RIGHT, buff=0.5)
            lone_dot = Circle(
                radius=0.17, color=ORANGE_HL,
                fill_opacity=1, fill_color=ORANGE_HL, stroke_width=0,
            )
            odd_row = VGroup(odd_pairs, lone_dot).arrange(RIGHT, buff=0.5)
            odd_row.next_to(odd_lbl, DOWN, buff=0.45)
            self.play(FadeIn(odd_pairs), run_time=0.7)
            self.play(FadeIn(lone_dot), run_time=0.5)
            self.play(Indicate(lone_dot, color=ORANGE_HL, scale_factor=1.35), run_time=0.5)

            odd_note = Text(
                "One item always left unpaired",
                font="Poppins", font_size=24, color=ORANGE_HL, weight=BOLD,
            ).next_to(odd_row, DOWN, buff=0.35)
            self.play(FadeIn(odd_note), run_time=0.6)

            # Summary lines
            self.wait_until_bookmark("bk_sum_concept")
            self.play(
                FadeOut(odd_lbl), FadeOut(odd_pairs),
                FadeOut(lone_dot), FadeOut(odd_note),
                run_time=0.5,
            )
            sum1 = Text(
                "Even numbers are pairable.",
                font="Poppins", font_size=28, color=PURPLE, weight=BOLD,
            ).move_to(UP * 0.5)
            sum2 = Text(
                "Odd numbers always have a leftover item.",
                font="Poppins", font_size=28, color=ORANGE_HL, weight=BOLD,
            ).next_to(sum1, DOWN, buff=0.45)
            self.play(FadeIn(sum1), run_time=0.7)
            self.play(FadeIn(sum2), run_time=0.7)

        fade_all(self, badge_c, sum1, sum2)

        # ============================================================
        # SEGMENT 3 — WHY THIS HAPPENS
        # ============================================================
        with self.voiceover(
            text=(
                '<bookmark mark="bk_why"/>Now, why does this happen? '
                '<bookmark mark="bk_sequence"/>Whole numbers follow a strict pattern — '
                'even, odd, even, odd — starting from zero. '
                '<bookmark mark="bk_add_one"/>When we add one to an even number, '
                'we break a pair, and create an unpaired item, '
                '<bookmark mark="bk_giving_odd"/>giving us an odd number. '
                '<bookmark mark="bk_add_more"/>Add one more, and the leftover finds a new partner, '
                '<bookmark mark="bk_even_again"/>making it even again. '
                '<bookmark mark="bk_alternates"/>So parity alternates — '
                'because of how counting itself works.'
            )
        ) as tracker:

            badge_w = create_heading_badge("Why This Happens?")
            self.play(FadeIn(badge_w), run_time=0.6)

            # Why question line
            self.wait_until_bookmark("bk_why")
            why_q = Text(
                "Why does this happen?",
                font="Poppins", font_size=30, color=PURPLE,
            ).move_to(UP * 2.3)
            self.play(FadeIn(why_q), run_time=0.7)

            # Number sequence boxes
            self.wait_until_bookmark("bk_sequence")
            self.play(FadeOut(why_q), run_time=0.4)

            num_vals  = [0, 1, 2, 3, 4, 5]
            num_boxes = VGroup()
            for n in num_vals:
                bg  = PURPLE if n % 2 == 0 else PALE_PURPLE
                box = RoundedRectangle(
                    corner_radius=0.15, width=0.78, height=0.78,
                    fill_color=bg, fill_opacity=1, stroke_width=0,
                )
                lbl = Text(
                    str(n), font="Poppins", font_size=26,
                    color=WHITE, weight=BOLD,
                ).move_to(box)
                num_boxes.add(VGroup(box, lbl))
            num_boxes.arrange(RIGHT, buff=0.22).move_to(UP * 1.1)
            self.play(FadeIn(num_boxes), run_time=0.8)

            eo_labels = VGroup()
            for i, n in enumerate(num_vals):
                e_lbl = Text(
                    "even" if n % 2 == 0 else "odd",
                    font="Poppins", font_size=17, color=PURPLE,
                )
                e_lbl.next_to(num_boxes[i], DOWN, buff=0.18)
                eo_labels.add(e_lbl)
            self.play(FadeIn(eo_labels), run_time=0.7)

            # Add one: even → odd
            self.wait_until_bookmark("bk_add_one")
            self.play(num_boxes[0][0].animate.set_fill(ORANGE_HL), run_time=0.4)
            arr01 = Arrow(
                start=num_boxes[0].get_right() + RIGHT * 0.05,
                end=num_boxes[1].get_left()  + LEFT  * 0.05,
                color=ORANGE_HL, stroke_width=3, buff=0,
                max_tip_length_to_length_ratio=0.3,
            )
            plus1a = Text(
                "+1", font="Poppins", font_size=21,
                color=ORANGE_HL, weight=BOLD,
            ).next_to(arr01, UP, buff=0.1)
            self.play(Create(arr01), FadeIn(plus1a), run_time=0.6)
            self.play(num_boxes[1][0].animate.set_fill(ORANGE_HL), run_time=0.4)

            # Result: odd
            self.wait_until_bookmark("bk_giving_odd")
            odd_res = Text(
                "Even + 1 = Odd",
                font="Poppins", font_size=26, color=PURPLE,
            ).move_to(DOWN * 0.6)
            self.play(FadeIn(odd_res), run_time=0.6)

            # Add one more: odd → even
            self.wait_until_bookmark("bk_add_more")
            self.play(
                num_boxes[0][0].animate.set_fill(PURPLE),
                num_boxes[1][0].animate.set_fill(PALE_PURPLE),
                FadeOut(arr01), FadeOut(plus1a), FadeOut(odd_res),
                run_time=0.4,
            )
            self.play(num_boxes[1][0].animate.set_fill(ORANGE_HL), run_time=0.3)
            arr12 = Arrow(
                start=num_boxes[1].get_right() + RIGHT * 0.05,
                end=num_boxes[2].get_left()  + LEFT  * 0.05,
                color=ORANGE_HL, stroke_width=3, buff=0,
                max_tip_length_to_length_ratio=0.3,
            )
            plus1b = Text(
                "+1", font="Poppins", font_size=21,
                color=ORANGE_HL, weight=BOLD,
            ).next_to(arr12, UP, buff=0.1)
            self.play(Create(arr12), FadeIn(plus1b), run_time=0.6)
            self.play(num_boxes[2][0].animate.set_fill(ORANGE_HL), run_time=0.4)

            # Result: even again
            self.wait_until_bookmark("bk_even_again")
            even_res = Text(
                "Odd + 1 = Even",
                font="Poppins", font_size=26, color=PURPLE,
            ).move_to(DOWN * 0.6)
            self.play(FadeIn(even_res), run_time=0.6)

            # Alternates conclusion
            self.wait_until_bookmark("bk_alternates")
            self.play(
                num_boxes[1][0].animate.set_fill(PALE_PURPLE),
                num_boxes[2][0].animate.set_fill(PURPLE),
                FadeOut(arr12), FadeOut(plus1b), FadeOut(even_res),
                run_time=0.4,
            )
            alt_text = Text(
                "Parity alternates — even, odd, even, odd...",
                font="Poppins", font_size=26, color=PURPLE, weight=BOLD,
            ).move_to(DOWN * 0.8)
            self.play(FadeIn(alt_text), run_time=0.7)

        fade_all(self, badge_w, num_boxes, eo_labels, alt_text)

        # ============================================================
        # SEGMENT 4 — QUESTION
        # ============================================================
        with self.voiceover(
            text=(
                '<bookmark mark="bk_q_teacher"/>A teacher has forty seven students, '
                'and wants to seat them in pairs on benches. '
                '<bookmark mark="bk_q_partner"/>Will every student have a partner? '
                '<bookmark mark="bk_q_unpaired"/>If not, how many pairs will be formed, '
                'and how many students will be unpaired?'
            )
        ) as tracker:

            badge_q = create_heading_badge("Question")
            self.play(FadeIn(badge_q), run_time=0.6)

            # Question line 1
            self.wait_until_bookmark("bk_q_teacher")
            q1a = Text("A teacher has", font="Poppins", font_size=26, color=PURPLE)
            q1b = math_obj(r"47", color=ORANGE_HL, font_size=32)
            q1c = Text("students", font="Poppins", font_size=26, color=PURPLE)
            q_line1 = VGroup(q1a, q1b, q1c).arrange(RIGHT, buff=0.22)
            q_line1.move_to(UP * 2.4)
            self.play(FadeIn(q_line1), run_time=0.8)

            # Question line 2
            q_line2 = Text(
                "and wants to seat them in pairs on benches.",
                font="Poppins", font_size=26, color=PURPLE,
            ).next_to(q_line1, DOWN, buff=0.32)
            self.play(FadeIn(q_line2), run_time=0.7)

            # Bench figure
            bench = Rectangle(
                width=4.2, height=0.65, color=PURPLE,
                stroke_width=2.5, fill_opacity=0.08, fill_color=PURPLE,
            ).move_to(UP * 0.5)
            bench_dots = VGroup(*[dot_pair() for _ in range(3)])
            bench_dots.arrange(RIGHT, buff=0.4)
            bench_dots.next_to(bench, UP, buff=0.14)
            bench_lbl = Text(
                "bench", font="Poppins", font_size=19, color=PURPLE,
            ).next_to(bench, DOWN, buff=0.16)
            self.play(Create(bench), run_time=1.0)
            self.play(FadeIn(bench_dots), FadeIn(bench_lbl), run_time=0.7)

            # Sub-question 1
            self.wait_until_bookmark("bk_q_partner")
            q_line3 = Text(
                "Will every student have a partner?",
                font="Poppins", font_size=26, color=PURPLE,
            ).next_to(bench, DOWN, buff=0.7)
            self.play(FadeIn(q_line3), run_time=0.7)

            # Sub-questions 2 + unknown
            self.wait_until_bookmark("bk_q_unpaired")
            q_line4 = Text(
                "If not, how many pairs will be formed",
                font="Poppins", font_size=26, color=PURPLE,
            ).next_to(q_line3, DOWN, buff=0.28)
            q_line5 = Text(
                "and how many students will be unpaired?",
                font="Poppins", font_size=26, color=PURPLE,
            ).next_to(q_line4, DOWN, buff=0.28)
            self.play(FadeIn(q_line4), run_time=0.7)
            self.play(FadeIn(q_line5), run_time=0.6)

            unk = Text(
                "?", font="Poppins", font_size=36, color=ORANGE_HL, weight=BOLD,
            ).next_to(bench_dots, RIGHT, buff=0.4)
            self.play(FadeIn(unk), run_time=0.5)
            self.play(Indicate(unk, color=ORANGE_HL, scale_factor=1.3), run_time=0.5)

        fade_all(
            self, badge_q,
            q_line1, q_line2, q_line3, q_line4, q_line5,
            bench, bench_dots, bench_lbl, unk,
        )

        # ============================================================
        # SEGMENT 5 — SOLUTION
        # ============================================================
        # ── FRACTION BAR FIX APPLIED HERE ───────────────────────────
        #   BEFORE: math_obj(r"47 \div 2")       → renders as  47 ÷ 2  (no bar)
        #   AFTER:  math_obj(r"\dfrac{47}{2}")   → renders as  47 over 2  (bar shown)
        #   BEFORE: math_obj(r"\dfrac{47}{2} = 23\ \text{R}\ 1")  shown inline
        #   AFTER:  two separate steps for clarity
        # ────────────────────────────────────────────────────────────
        with self.voiceover(
            text=(
                '<bookmark mark="bk_divide"/>We divide forty seven by two. '
                '<bookmark mark="bk_eq47"/>Forty seven equals, two times twenty three, plus one. '
                '<bookmark mark="bk_pairs_formed"/>So twenty three pairs are formed. '
                '<bookmark mark="bk_unpaired_sol"/>One student is left unpaired. '
                '<bookmark mark="bk_odd_result"/>This tells us — forty seven is an odd number.'
            )
        ) as tracker:

            badge_s = create_heading_badge("Solution")
            self.play(FadeIn(badge_s), run_time=0.6)

            step_y   = UP * 2.3
            step_buf = 0.85          # slightly larger buff to accommodate dfrac height

            # ── Step 1: We divide 47 by 2 — shown as fraction with bar ──
            self.wait_until_bookmark("bk_divide")
            s1a = Text("We divide", font="Poppins", font_size=30, color=PURPLE)

            # ✅ FIX — \dfrac{47}{2} shows the horizontal fraction bar
            s1b = math_obj(r"\dfrac{47}{2}", font_size=34)

            s1 = VGroup(s1a, s1b).arrange(RIGHT, buff=0.28)
            s1.move_to(step_y)
            self.play(FadeIn(s1), run_time=0.7)

            # ── Step 2: Division algorithm equation ─────────────────────
            self.wait_until_bookmark("bk_eq47")
            s2 = math_obj(r"47 = 2 \times 23 + 1", font_size=34)
            s2.next_to(s1, DOWN, buff=step_buf).align_to(s1, LEFT)
            self.play(FadeIn(s2), run_time=0.8)
            self.play(Indicate(s2, color=ORANGE_HL, scale_factor=1.1), run_time=0.6)

            # ── Step 3: 23 pairs formed ──────────────────────────────────
            self.wait_until_bookmark("bk_pairs_formed")
            s3a = Text("So", font="Poppins", font_size=30, color=PURPLE)
            s3b = math_obj(r"23", color=ORANGE_HL, font_size=34)
            s3c = Text("pairs are formed.", font="Poppins", font_size=30, color=PURPLE)
            s3  = VGroup(s3a, s3b, s3c).arrange(RIGHT, buff=0.2)
            s3.next_to(s2, DOWN, buff=step_buf).align_to(s2, LEFT)
            self.play(FadeIn(s3), run_time=0.7)

            # ── Step 4: One student unpaired ─────────────────────────────
            self.wait_until_bookmark("bk_unpaired_sol")
            self.play(
                s1.animate.set_opacity(0.35),
                s2.animate.set_opacity(0.35),
                run_time=0.5,
            )
            s4a = Text(
                "One student is left", font="Poppins", font_size=30, color=PURPLE,
            )
            s4b = Text(
                "unpaired.", font="Poppins", font_size=30,
                color=ORANGE_HL, weight=BOLD,
            )
            s4 = VGroup(s4a, s4b).arrange(RIGHT, buff=0.15)
            s4.next_to(s3, DOWN, buff=step_buf).align_to(s3, LEFT)
            self.play(FadeIn(s4), run_time=0.7)

            # ── Step 5: 47 is an odd number ──────────────────────────────
            self.wait_until_bookmark("bk_odd_result")
            self.play(s3.animate.set_opacity(0.35), run_time=0.4)
            s5a = Text("This tells us", font="Poppins", font_size=30, color=PURPLE)
            s5b = math_obj(r"47", color=ORANGE_HL, font_size=34)
            s5c = Text("is an", font="Poppins", font_size=30, color=PURPLE)
            s5d = Text(
                "odd number.", font="Poppins", font_size=30,
                color=ORANGE_HL, weight=BOLD,
            )
            s5 = VGroup(s5a, s5b, s5c, s5d).arrange(RIGHT, buff=0.18)
            s5.next_to(s4, DOWN, buff=step_buf).align_to(s4, LEFT)
            self.play(FadeIn(s5), run_time=0.8)
            self.play(Indicate(s5, color=ORANGE_HL, scale_factor=1.1), run_time=0.6)
            self.wait(0.6)

        fade_all(self, badge_s, s1, s2, s3, s4, s5)

        # ============================================================
        # SEGMENT 6 — REAL-LIFE CONNECTION
        # ============================================================
        with self.voiceover(
            text=(
                '<bookmark mark="bk_engineers"/>This is the same logic engineers use — '
                'when checking whether items can be split into balanced groups.'
            )
        ) as tracker:

            badge_rl = create_heading_badge("Real-Life Connection")
            self.play(FadeIn(badge_rl), run_time=0.6)

            self.wait_until_bookmark("bk_engineers")
            rl1 = Text(
                "This is the same logic engineers use —",
                font="Poppins", font_size=26, color=PURPLE,
            ).move_to(UP * 1.2)
            rl2 = Text(
                "when checking whether items can be",
                font="Poppins", font_size=26, color=PURPLE,
            ).next_to(rl1, DOWN, buff=0.3)
            rl3 = Text(
                "split into balanced groups.",
                font="Poppins", font_size=26, color=PURPLE,
            ).next_to(rl2, DOWN, buff=0.3)
            self.play(FadeIn(rl1), run_time=0.7)
            self.play(FadeIn(rl2), run_time=0.6)
            self.play(FadeIn(rl3), run_time=0.6)

            # Balanced groups visual
            grp_left = VGroup(*[
                Circle(radius=0.15, color=PURPLE, fill_opacity=1,
                       fill_color=PURPLE, stroke_width=0)
                for _ in range(3)
            ]).arrange(RIGHT, buff=0.22)
            grp_right = VGroup(*[
                Circle(radius=0.15, color=PURPLE, fill_opacity=1,
                       fill_color=PURPLE, stroke_width=0)
                for _ in range(3)
            ]).arrange(RIGHT, buff=0.22)
            eq_sym   = math_obj(r"=", font_size=36)
            balanced = VGroup(grp_left, eq_sym, grp_right).arrange(RIGHT, buff=0.5)
            balanced.next_to(rl3, DOWN, buff=0.55)
            self.play(FadeIn(balanced), run_time=0.7)

        fade_all(self, badge_rl, rl1, rl2, rl3, balanced)

        # ============================================================
        # SEGMENT 7 — SUMMARY
        # ============================================================
        with self.voiceover(
            text=(
                '<bookmark mark="bk_sum1"/>Parity tells us whether a number is even or odd. '
                '<bookmark mark="bk_sum2"/>Even numbers are pairable — '
                'odd numbers have one unpaired leftover.'
            )
        ) as tracker:

            badge_sum = create_heading_badge("Summary")
            self.play(FadeIn(badge_sum), run_time=0.6)

            # Bullet 1
            self.wait_until_bookmark("bk_sum1")
            dot1  = Text("*", font="Poppins", font_size=28, color=PURPLE)
            b1txt = Text(
                "Parity tells us whether a number is even or odd.",
                font="Poppins", font_size=26, color=PURPLE,
            )
            bullet1 = VGroup(dot1, b1txt).arrange(RIGHT, buff=0.2)
            bullet1.move_to(UP * 0.6)
            self.play(FadeIn(bullet1), run_time=0.8)

            # Bullet 2
            self.wait_until_bookmark("bk_sum2")
            dot2  = Text("*", font="Poppins", font_size=28, color=PURPLE)
            b2_l1 = Text(
                "Even numbers are pairable;",
                font="Poppins", font_size=26, color=PURPLE,
            )
            b2_l2 = Text(
                "odd numbers have one unpaired leftover.",
                font="Poppins", font_size=26, color=ORANGE_HL,
            )
            b2txt   = VGroup(b2_l1, b2_l2).arrange(DOWN, buff=0.2, aligned_edge=LEFT)
            bullet2 = VGroup(dot2, b2txt).arrange(RIGHT, buff=0.2, aligned_edge=UP)
            bullet2.next_to(bullet1, DOWN, buff=0.5)
            self.play(FadeIn(bullet2), run_time=0.8)
            self.wait(0.6)

        fade_all(self, badge_sum, bullet1, bullet2)