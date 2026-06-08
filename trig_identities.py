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
        print("\n" + "="*60)
        print(f"FAILED BOOKMARKS SUMMARY ({len(_FAILED_BOOKMARKS)} total):")
        print("="*60)
        for mark, text in _FAILED_BOOKMARKS:
            print(f"  FAILED: {mark}  ->  {text}")
        print("="*60)
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
# TEMPLATE SETUP
# ============================================================

def _make_cosec_template():
    """
    Clone gnu_freesans_tx using the CORRECT attribute 'preamble'
    (confirmed from diagnostic output), then append the cosec
    operator declaration so LaTeX does not crash on \\cosec.
    """
    base = TexFontTemplates.gnu_freesans_tx
    t = TexTemplate(
        tex_compiler     = base.tex_compiler,      # e.g. "xelatex"
        output_format    = base.output_format,     # e.g. ".xdv"
        preamble         = base.preamble,          # ✅ confirmed attribute
        placeholder_text = base.placeholder_text,
    )
    # Append \cosec declaration AFTER the font preamble is copied
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
    """
    Standard math helper — gnu_freesans_tx font.
    Use for any expression that does NOT contain \\cosec.
    """
    return MathTex(
        tex_str,
        tex_template=TexFontTemplates.gnu_freesans_tx,
        color=color,
        font_size=font_size,
    )


def math_obj_cosec(tex_str, color=PURPLE, font_size=36):
    """
    Use when expression contains \\cosec (Indian notation).
    Same font as math_obj() — gnu_freesans_tx base + cosec declared.
    """
    return MathTex(
        tex_str,
        tex_template=COSEC_TEMPLATE,
        color=color,
        font_size=font_size,
    )


# ============================================================
# SCENE
# ============================================================

class TrigonometricIdentities(VoiceoverScene):

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
                '<bookmark mark="bk_hook_try"/>Try this — pick any angle, find its sine and cosine, square them, and add the two values together. '
                '<bookmark mark="bk_hook_one"/>You will always get one. '
                'Strange, isn\'t it? '
                '<bookmark mark="bk_hook_power"/>That is the power of a trigonometric identity.'
            )
        ) as tracker:

            self.wait_until_bookmark("bk_title")
            self.camera.background_color = PURPLE
            title = Text(
                "Trigonometric Identities",
                font="Poppins",
                font_size=52,
                color=WHITE,
                weight=BOLD,
            ).move_to(ORIGIN)
            self.play(FadeIn(title), run_time=0.8)
            self.wait(0.4)

            self.wait_until_bookmark("bk_hook_try")
            self.play(FadeOut(title), run_time=0.5)
            self.camera.background_color = LAVENDER_BG

            prompt = Text(
                "Try this...",
                font="Poppins",
                font_size=36,
                color=PURPLE,
            ).move_to(UP * 2.5)
            self.play(FadeIn(prompt), run_time=0.7)

            step1 = Text("Pick any angle", font="Poppins", font_size=26, color=PURPLE)
            arr1  = math_obj(r"\rightarrow", font_size=26)
            step2 = math_obj(r"\sin A,\ \cos A", font_size=26)
            arr2  = math_obj(r"\rightarrow", font_size=26)
            step3 = Text("square", font="Poppins", font_size=26, color=PURPLE)
            arr3  = math_obj(r"\rightarrow", font_size=26)
            step4 = Text("add", font="Poppins", font_size=26, color=PURPLE)

            steps = VGroup(step1, arr1, step2, arr2, step3, arr3, step4).arrange(RIGHT, buff=0.18)
            steps.next_to(prompt, DOWN, buff=0.5)
            self.play(FadeIn(steps), run_time=0.8)

            formula_hint = math_obj(r"\sin^2 A + \cos^2 A", font_size=34)
            formula_hint.next_to(steps, DOWN, buff=0.5)
            self.play(FadeIn(formula_hint), run_time=0.7)

            self.wait_until_bookmark("bk_hook_one")
            result = math_obj(r"= 1", color=ORANGE_HL, font_size=40)
            result.next_to(formula_hint, RIGHT, buff=0.2)
            self.play(FadeIn(result), run_time=0.6)
            self.play(Indicate(result, color=ORANGE_HL, scale_factor=1.25), run_time=0.6)

            strange = Text(
                "Strange, isn't it?",
                font="Poppins",
                font_size=28,
                color=PURPLE,
            ).next_to(formula_hint, DOWN, buff=0.5)
            self.play(FadeIn(strange), run_time=0.6)

            self.wait_until_bookmark("bk_hook_power")
            power = Text(
                "That is the power of a trigonometric identity.",
                font="Poppins",
                font_size=26,
                color=PURPLE,
                weight=BOLD,
            ).next_to(strange, DOWN, buff=0.35)
            self.play(FadeIn(power), run_time=0.7)

        self.play(
            FadeOut(prompt), FadeOut(steps), FadeOut(formula_hint),
            FadeOut(result), FadeOut(strange), FadeOut(power),
            run_time=0.8,
        )

        # ============================================================
        # SEGMENT 2 — CONCEPT
        # ============================================================

        with self.voiceover(
            text=(
                '<bookmark mark="bk_concept_def"/>A trigonometric identity — is an equation involving trigonometric ratios of an angle, '
                'that holds true for every angle, where the ratios are defined. '
                '<bookmark mark="bk_identity1"/>The most important one is — sine squared, A, plus cosine squared, A, equals one. '
                '<bookmark mark="bk_identity2"/>From this, two more follow — one plus tangent squared, A, equals secant squared, A, '
                '<bookmark mark="bk_identity3"/>and one plus cotangent squared, A, equals cosecant squared, A. '
                '<bookmark mark="bk_verify_def"/>To verify an identity — means to check whether the left hand side equals the right hand side, '
                'when we substitute a specific value of, A.'
            )
        ) as tracker:

            badge_concept = create_heading_badge("Concept")
            self.play(FadeIn(badge_concept), run_time=0.6)

            self.wait_until_bookmark("bk_concept_def")
            def_line1 = Text(
                "A trigonometric identity is an equation",
                font="Poppins", font_size=26, color=PURPLE,
            ).move_to(UP * 1.8)
            def_line2 = Text(
                "involving trigonometric ratios of an angle",
                font="Poppins", font_size=26, color=PURPLE,
            ).next_to(def_line1, DOWN, buff=0.25)
            def_line3 = Text(
                "that holds true for every angle where the ratios are defined.",
                font="Poppins", font_size=26, color=PURPLE,
            ).next_to(def_line2, DOWN, buff=0.25)
            self.play(FadeIn(def_line1), run_time=0.7)
            self.play(FadeIn(def_line2), run_time=0.7)
            self.play(FadeIn(def_line3), run_time=0.7)

            self.wait_until_bookmark("bk_identity1")
            self.play(
                FadeOut(def_line1), FadeOut(def_line2), FadeOut(def_line3),
                run_time=0.6,
            )
            id1 = math_obj(r"\sin^2 A + \cos^2 A = 1", font_size=40)
            id1.move_to(UP * 1.5)
            self.play(FadeIn(id1), run_time=0.8)
            self.play(Indicate(id1, color=ORANGE_HL, scale_factor=1.15), run_time=0.6)

            self.wait_until_bookmark("bk_identity2")
            id2 = math_obj(r"1 + \tan^2 A = \sec^2 A", font_size=36)
            id2.next_to(id1, DOWN, buff=0.55)
            self.play(FadeIn(id2), run_time=0.8)

            self.wait_until_bookmark("bk_identity3")
            # ✅ contains \cosec — use math_obj_cosec()
            id3 = math_obj_cosec(r"1 + \cot^2 A = \cosec^2 A", font_size=36)
            id3.next_to(id2, DOWN, buff=0.45)
            self.play(FadeIn(id3), run_time=0.8)

            self.wait_until_bookmark("bk_verify_def")
            self.play(
                FadeOut(id1), FadeOut(id2), FadeOut(id3),
                run_time=0.7,
            )
            lhs_box = Text("LHS", font="Poppins", font_size=32, color=PURPLE)
            eq_sign = math_obj(r"\stackrel{?}{=}", color=ORANGE_HL, font_size=36)
            rhs_box = Text("RHS", font="Poppins", font_size=32, color=PURPLE)
            lr_group = VGroup(lhs_box, eq_sign, rhs_box).arrange(RIGHT, buff=0.4)
            lr_group.move_to(UP * 1.0)
            self.play(FadeIn(lr_group), run_time=0.8)

            sub_note = Text(
                "Substitute a specific value of A",
                font="Poppins", font_size=26, color=PURPLE,
            ).next_to(lr_group, DOWN, buff=0.5)
            self.play(FadeIn(sub_note), run_time=0.7)

        self.play(
            FadeOut(badge_concept), FadeOut(lr_group), FadeOut(sub_note),
            run_time=0.8,
        )

        # ============================================================
        # SEGMENT 3 — WHY IDENTITIES
        # ============================================================

        with self.voiceover(
            text=(
                '<bookmark mark="bk_why"/>Now, why are these called identities — and not just equations? '
                '<bookmark mark="bk_equation"/>An equation may be true only for some values. '
                '<bookmark mark="bk_identity_rule"/>But an identity must hold for every valid value of, A. '
                '<bookmark mark="bk_pythagoras"/>This works because these identities come directly from the Pythagoras theorem, applied to a right angled triangle. '
                '<bookmark mark="bk_therefore"/>Since the theorem is true for every right triangle — the identity holds for every valid angle, A.'
            )
        ) as tracker:

            badge_why = create_heading_badge("Why Identities?")
            self.play(FadeIn(badge_why), run_time=0.6)

            self.wait_until_bookmark("bk_why")
            why_q = Text(
                "Why are these called identities — and not just equations?",
                font="Poppins", font_size=26, color=PURPLE,
            ).move_to(UP * 2.2)
            self.play(FadeIn(why_q), run_time=0.7)

            self.wait_until_bookmark("bk_equation")
            eq_line = Text(
                "An equation may be true only for some values.",
                font="Poppins", font_size=26, color=PURPLE,
            ).next_to(why_q, DOWN, buff=0.4)
            self.play(FadeIn(eq_line), run_time=0.7)

            self.wait_until_bookmark("bk_identity_rule")
            id_line = Text(
                "An identity must hold for every valid value of A.",
                font="Poppins", font_size=26, color=ORANGE_HL, weight=BOLD,
            ).next_to(eq_line, DOWN, buff=0.4)
            self.play(FadeIn(id_line), run_time=0.7)
            self.play(Indicate(id_line, color=ORANGE_HL, scale_factor=1.1), run_time=0.6)

            self.wait_until_bookmark("bk_pythagoras")
            self.play(
                FadeOut(why_q), FadeOut(eq_line), FadeOut(id_line),
                run_time=0.6,
            )

            A = LEFT * 1.5 + DOWN * 1.0
            B = RIGHT * 1.5 + DOWN * 1.0
            C = RIGHT * 1.5 + UP * 1.0

            tri = Polygon(A, B, C, color=PURPLE, stroke_width=2.5, fill_opacity=0)
            right_mark = Square(side_length=0.22, color=PURPLE, stroke_width=1.5, fill_opacity=0)
            right_mark.move_to(B + UP * 0.11 + LEFT * 0.11)

            label_a = math_obj(r"a", font_size=28)
            label_a.next_to(Dot((A + C) / 2), LEFT, buff=0.2)
            label_b = math_obj(r"b", font_size=28)
            label_b.next_to(Dot((A + B) / 2), DOWN, buff=0.2)
            label_c = math_obj(r"c", font_size=28)
            label_c.next_to(Dot((B + C) / 2), RIGHT, buff=0.2)

            tri_group = VGroup(tri, right_mark, label_a, label_b, label_c)
            tri_group.move_to(ORIGIN + DOWN * 0.3)
            self.play(Create(tri), run_time=1.2)
            self.play(
                FadeIn(right_mark),
                FadeIn(label_a), FadeIn(label_b), FadeIn(label_c),
                run_time=0.7,
            )

            pyth = math_obj(r"a^2 + b^2 = c^2", font_size=36)
            pyth.next_to(tri_group, DOWN, buff=0.45)
            self.play(FadeIn(pyth), run_time=0.8)

            self.wait_until_bookmark("bk_therefore")
            self.play(Flash(tri, color=ORANGE_HL, flash_radius=1.8), run_time=0.6)
            true_note = Text(
                "True for every right triangle",
                font="Poppins", font_size=24, color=PURPLE,
            ).next_to(pyth, DOWN, buff=0.4)
            self.play(FadeIn(true_note), run_time=0.7)

        self.play(
            FadeOut(badge_why), FadeOut(tri_group),
            FadeOut(pyth), FadeOut(true_note),
            run_time=0.8,
        )

        # ============================================================
        # SEGMENT 4 — QUESTION
        # ============================================================

        with self.voiceover(
            text=(
                '<bookmark mark="bk_question"/>Verify the identity sine squared, A, plus cosine squared, A, equals one, '
                'for, A, equals forty five degrees, '
                'and also verify one plus tangent squared, A, equals secant squared, A, for the same angle.'
            )
        ) as tracker:

            badge_q = create_heading_badge("Question")
            self.play(FadeIn(badge_q), run_time=0.6)

            self.wait_until_bookmark("bk_question")

            q_text1_p1 = Text("Verify the identity", font="Poppins", font_size=26, color=PURPLE)
            q_id1      = math_obj(r"\sin^2 A + \cos^2 A = 1", font_size=32)
            q_line1    = VGroup(q_text1_p1, q_id1).arrange(RIGHT, buff=0.25)
            q_line1.move_to(UP * 2.0)
            self.play(FadeIn(q_line1), run_time=0.8)

            q_for_p1   = Text("for", font="Poppins", font_size=26, color=PURPLE)
            q_angle    = math_obj(r"A = 45^\circ", color=ORANGE_HL, font_size=32)
            q_line2    = VGroup(q_for_p1, q_angle).arrange(RIGHT, buff=0.2)
            q_line2.next_to(q_line1, DOWN, buff=0.4)
            self.play(FadeIn(q_line2), run_time=0.7)

            q_also_p1  = Text("and also verify", font="Poppins", font_size=26, color=PURPLE)
            q_id2      = math_obj(r"1 + \tan^2 A = \sec^2 A", font_size=32)
            q_line3    = VGroup(q_also_p1, q_id2).arrange(RIGHT, buff=0.25)
            q_line3.next_to(q_line2, DOWN, buff=0.4)
            self.play(FadeIn(q_line3), run_time=0.8)

            q_same = Text(
                "for the same angle.",
                font="Poppins", font_size=26, color=PURPLE,
            ).next_to(q_line3, DOWN, buff=0.35)
            self.play(FadeIn(q_same), run_time=0.6)

        self.play(
            FadeOut(badge_q), FadeOut(q_line1), FadeOut(q_line2),
            FadeOut(q_line3), FadeOut(q_same),
            run_time=0.8,
        )

        # ============================================================
        # SEGMENT 5 — SOLUTION
        # ============================================================

        with self.voiceover(
            text=(
                '<bookmark mark="bk_sol_known"/>We know sine forty five degrees equals, one over root two, '
                'and cosine forty five degrees equals, one over root two. '
                '<bookmark mark="bk_sin_sq"/>So sine squared forty five degrees equals, one over two. '
                '<bookmark mark="bk_cos_sq"/>And cosine squared forty five degrees equals, one over two. '
                '<bookmark mark="bk_add"/>Adding them — one over two, plus one over two, equals one. '
                '<bookmark mark="bk_first_holds"/>The first identity holds. '
                '<bookmark mark="bk_tan_sec"/>Now, tangent forty five degrees equals one, and secant forty five degrees equals root two. '
                '<bookmark mark="bk_lhs2"/>So one plus tangent squared forty five degrees equals one plus one — which is two. '
                '<bookmark mark="bk_rhs2"/>And secant squared forty five degrees equals root two, squared — which is also two. '
                '<bookmark mark="bk_second_holds"/>So the second identity also holds.'
            )
        ) as tracker:

            badge_sol = create_heading_badge("Solution")
            self.play(FadeIn(badge_sol), run_time=0.6)

            col_x = LEFT * 3.8
            step_start_y = UP * 2.6
            step_buff    = 0.62

            self.wait_until_bookmark("bk_sol_known")
            s1 = math_obj(r"\sin 45^\circ = \dfrac{1}{\sqrt{2}}", font_size=30)
            s1.move_to(col_x + step_start_y)
            s1.align_to(col_x, LEFT)
            self.play(FadeIn(s1), run_time=0.7)

            s2 = math_obj(r"\cos 45^\circ = \dfrac{1}{\sqrt{2}}", font_size=30)
            s2.next_to(s1, DOWN, buff=step_buff)
            s2.align_to(s1, LEFT)
            self.play(FadeIn(s2), run_time=0.7)

            self.wait_until_bookmark("bk_sin_sq")
            s3 = math_obj(r"\sin^2 45^\circ = \dfrac{1}{2}", font_size=30)
            s3.next_to(s2, DOWN, buff=step_buff)
            s3.align_to(s1, LEFT)
            self.play(FadeIn(s3), run_time=0.7)

            self.wait_until_bookmark("bk_cos_sq")
            s4 = math_obj(r"\cos^2 45^\circ = \dfrac{1}{2}", font_size=30)
            s4.next_to(s3, DOWN, buff=step_buff)
            s4.align_to(s1, LEFT)
            self.play(FadeIn(s4), run_time=0.7)

            self.wait_until_bookmark("bk_add")
            s5 = math_obj(r"\dfrac{1}{2} + \dfrac{1}{2} = 1", font_size=30)
            s5.next_to(s4, DOWN, buff=step_buff)
            s5.align_to(s1, LEFT)
            self.play(FadeIn(s5), run_time=0.7)

            self.wait_until_bookmark("bk_first_holds")
            holds1 = Text(
                "The first identity holds.",
                font="Poppins", font_size=28, color=ORANGE_HL, weight=BOLD,
            ).next_to(s5, DOWN, buff=0.45)
            holds1.align_to(s1, LEFT)
            self.play(FadeIn(holds1), run_time=0.7)
            self.play(Indicate(s5, color=ORANGE_HL, scale_factor=1.1), run_time=0.6)

            self.wait_until_bookmark("bk_tan_sec")
            self.play(
                s1.animate.set_opacity(0.35),
                s2.animate.set_opacity(0.35),
                s3.animate.set_opacity(0.35),
                s4.animate.set_opacity(0.35),
                s5.animate.set_opacity(0.35),
                holds1.animate.set_opacity(0.35),
                run_time=0.6,
            )

            s6 = math_obj(r"\tan 45^\circ = 1", font_size=30)
            s6.move_to(col_x + UP * 2.6)
            s6.align_to(col_x, LEFT)
            self.play(FadeIn(s6), run_time=0.7)

            s7 = math_obj(r"\sec 45^\circ = \sqrt{2}", font_size=30)
            s7.next_to(s6, DOWN, buff=step_buff)
            s7.align_to(s6, LEFT)
            self.play(FadeIn(s7), run_time=0.7)

            self.wait_until_bookmark("bk_lhs2")
            s8 = math_obj(r"1 + \tan^2 45^\circ = 1 + 1 = 2", font_size=30)
            s8.next_to(s7, DOWN, buff=step_buff)
            s8.align_to(s6, LEFT)
            self.play(FadeIn(s8), run_time=0.8)

            self.wait_until_bookmark("bk_rhs2")
            s9 = math_obj(r"\sec^2 45^\circ = (\sqrt{2})^2 = 2", font_size=30)
            s9.next_to(s8, DOWN, buff=step_buff)
            s9.align_to(s6, LEFT)
            self.play(FadeIn(s9), run_time=0.8)

            self.wait_until_bookmark("bk_second_holds")
            holds2 = Text(
                "The second identity also holds.",
                font="Poppins", font_size=28, color=ORANGE_HL, weight=BOLD,
            ).next_to(s9, DOWN, buff=0.45)
            holds2.align_to(s6, LEFT)
            self.play(FadeIn(holds2), run_time=0.7)
            self.play(
                Indicate(s8, color=ORANGE_HL, scale_factor=1.1),
                Indicate(s9, color=ORANGE_HL, scale_factor=1.1),
                run_time=0.7,
            )
            self.wait(0.6)

        self.play(
            FadeOut(badge_sol),
            FadeOut(s1), FadeOut(s2), FadeOut(s3),
            FadeOut(s4), FadeOut(s5), FadeOut(holds1),
            FadeOut(s6), FadeOut(s7), FadeOut(s8),
            FadeOut(s9), FadeOut(holds2),
            run_time=0.8,
        )

        # ============================================================
        # SEGMENT 6 — REAL-LIFE CONNECTION
        # ============================================================

        with self.voiceover(
            text=(
                '<bookmark mark="bk_reallife"/>This is the same idea engineers use, '
                'when checking the stability of bridges, '
                'or designing precise angles in architecture.'
            )
        ) as tracker:

            badge_rl = create_heading_badge("Real-Life Connection")
            self.play(FadeIn(badge_rl), run_time=0.6)

            self.wait_until_bookmark("bk_reallife")
            rl1 = Text(
                "Engineers use this idea when checking",
                font="Poppins", font_size=26, color=PURPLE,
            ).move_to(UP * 0.6)
            rl2 = Text(
                "the stability of bridges",
                font="Poppins", font_size=26, color=PURPLE,
            ).next_to(rl1, DOWN, buff=0.3)
            rl3 = Text(
                "or designing precise angles in architecture.",
                font="Poppins", font_size=26, color=PURPLE,
            ).next_to(rl2, DOWN, buff=0.3)
            self.play(FadeIn(rl1), run_time=0.7)
            self.play(FadeIn(rl2), run_time=0.7)
            self.play(FadeIn(rl3), run_time=0.7)

        self.play(
            FadeOut(badge_rl), FadeOut(rl1), FadeOut(rl2), FadeOut(rl3),
            run_time=0.8,
        )

        # ============================================================
        # SEGMENT 7 — SUMMARY
        # ============================================================

        with self.voiceover(
            text=(
                '<bookmark mark="bk_summary1"/>Trigonometric identities hold true for every valid angle, A. '
                '<bookmark mark="bk_summary2"/>Verification is done by substituting a value, and comparing both sides.'
            )
        ) as tracker:

            badge_sum = create_heading_badge("Summary")
            self.play(FadeIn(badge_sum), run_time=0.6)

            self.wait_until_bookmark("bk_summary1")
            bullet_dot1 = Text("*", font="Poppins", font_size=28, color=PURPLE)
            bullet_text1_p1 = Text(
                "Trigonometric identities hold true for every valid angle",
                font="Poppins", font_size=26, color=PURPLE,
            )
            bullet_text1_p2 = math_obj(r"A.", font_size=26)
            bullet1_line = VGroup(bullet_text1_p1, bullet_text1_p2).arrange(RIGHT, buff=0.15)
            bullet1 = VGroup(bullet_dot1, bullet1_line).arrange(RIGHT, buff=0.2)
            bullet1.move_to(UP * 0.6)
            self.play(FadeIn(bullet1), run_time=0.8)

            self.wait_until_bookmark("bk_summary2")
            bullet_dot2 = Text("*", font="Poppins", font_size=28, color=PURPLE)
            bullet_text2 = Text(
                "Verification is done by substituting a value and comparing both sides.",
                font="Poppins", font_size=26, color=PURPLE,
            )
            bullet2 = VGroup(bullet_dot2, bullet_text2).arrange(RIGHT, buff=0.2)
            bullet2.next_to(bullet1, DOWN, buff=0.5)
            self.play(FadeIn(bullet2), run_time=0.8)
            self.wait(0.6)

        self.play(
            FadeOut(badge_sum), FadeOut(bullet1), FadeOut(bullet2),
            run_time=0.8,
        )