import os
import urllib.request
import manimpango
from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.openai import OpenAIService

# Coschool Color Palette
LAVENDER_BG = "#E7E5F3"
PURPLE      = "#7464CE"
ORANGE_HL   = "#FF9302"
PALE_PURPLE = "#9495D7"
WHITE       = "#FFFFFF"

# ============================================================
# POPPINS AUTO-DOWNLOAD & REGISTRATION
# ============================================================
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

# ============================================================
# BOOKMARK FAILURE TRACKER (DEBUG)
# ============================================================
import manim_voiceover.tracker as _vt
_orig_time_until_bookmark = _vt.VoiceoverTracker.time_until_bookmark
_FAILED_BOOKMARKS = []

def _safe_time_until_bookmark(self, mark, buff=0.0, limit=None):
    try:
        return _orig_time_until_bookmark(self, mark, buff, limit)
    except Exception:
        scene_text = getattr(self, 'data', {}).get('input_text', 'unknown')[:80]
        _FAILED_BOOKMARKS.append((mark, scene_text))
        print(f"WARNING  Bookmark '{mark}' NOT FOUND in: {scene_text}...")
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


# ============================================================
# HELPER FUNCTIONS
# ============================================================
def create_heading_badge(text_str):
    t = Text(text_str, font="Poppins", font_size=28,
             color=WHITE, weight=BOLD)
    badge = RoundedRectangle(
        corner_radius=0.2,
        width=t.width + 0.6, height=t.height + 0.3,
        fill_color=PURPLE, fill_opacity=1, stroke_width=0,
    )
    badge.move_to(t)
    return VGroup(badge, t).to_corner(UL, buff=0.3)

def math_obj(tex_str, color=PURPLE, font_size=36):
    return MathTex(tex_str,
                   tex_template=TexFontTemplates.gnu_freesans_tx,
                   color=color, font_size=font_size)

def create_pencil(pos, color=PURPLE):
    # A vector pencil design
    body = RoundedRectangle(corner_radius=0.08, width=0.25, height=1.0, color=color, stroke_width=2.5, fill_opacity=0.1)
    tip = Triangle(color=color, stroke_width=2.5).scale(0.12).next_to(body, UP, buff=0)
    pencil = VGroup(body, tip).move_to(pos)
    return pencil

def create_bench(pos, student_color=PALE_PURPLE):
    bench = Rectangle(width=1.8, height=0.9, color=PURPLE, stroke_width=2.5, fill_opacity=0.1, fill_color=PALE_PURPLE)
    bench.move_to(pos)
    dot1 = Dot(point=pos + LEFT * 0.4, color=student_color, radius=0.15)
    dot2 = Dot(point=pos + RIGHT * 0.4, color=student_color, radius=0.15)
    return VGroup(bench, dot1, dot2)


# ============================================================
# MAIN MANIM SCENE
# ============================================================
class ParityConcept(VoiceoverScene):
    def construct(self):
        TTS_INSTRUCTIONS = """
        Voice & Personality:
        You are a warm, patient, and encouraging mathematics teacher speaking
        to a middle-school student. Your tone is friendly, calm, and confident.
        The voice profile is shimmer.

        Pacing:
        Speak at a MODERATE-TO-SLOW pace. Honor the commas, dashes, and ellipses.
        """
        self.set_speech_service(
            OpenAIService(
                voice="shimmer",
                model="gpt-4o-mini-tts",
                transcription_model="medium",
                instructions=TTS_INSTRUCTIONS,
            ),
            create_subcaption=False,
        )

        # ------------------------------------------------------------
        # SCENE 1: Title Slide (Full Purple Background)
        # ------------------------------------------------------------
        bg_rect = FullScreenRectangle(fill_color=PURPLE, fill_opacity=1, stroke_width=0)
        self.add(bg_rect)

        title = Text("Number Play", font="Poppins", font_size=48, color=WHITE, weight=BOLD)
        subtitle = Text("Understanding Parity", font="Poppins", font_size=32, color=PALE_PURPLE)
        title_group = VGroup(title, subtitle).arrange(DOWN, buff=0.4).move_to(ORIGIN)

        with self.voiceover(text='<bookmark mark="bk_hook_pencils"/>Hello students!') as tracker:
            self.wait_until_bookmark("bk_hook_pencils")
            self.play(FadeIn(title_group), run_time=1.0)
            self.wait(0.5)

        self.play(FadeOut(title_group), run_time=0.8)
        self.play(bg_rect.animate.set_fill(LAVENDER_BG, opacity=1), run_time=1.0)

        # ------------------------------------------------------------
        # SCENE 2: Pencil Pairing (Intro Hook)
        # ------------------------------------------------------------
        # Create 6 pencils scattered
        pencil_coords = [
            [-3.0, 1.2, 0], [-1.0, -1.0, 0], [1.5, 1.5, 0],
            [3.0, -0.8, 0], [-2.0, -1.5, 0], [0.5, -1.2, 0]
        ]
        pencils = VGroup(*[create_pencil(coord, PURPLE) for coord in pencil_coords])

        with self.voiceover(
            text='Imagine arranging your pencils <bookmark mark="bk_hook_desk"/>into pairs on your desk. '
                 'Sometimes every pencil <bookmark mark="bk_hook_partner"/>finds a partner, and '
                 '<bookmark mark="bk_hook_behind"/>sometimes one is left behind. '
                 'Why does that happen <bookmark mark="bk_hook_happen"/>with some numbers and not others?'
        ) as tracker:
            self.wait_until_bookmark("bk_hook_desk")
            self.play(Create(pencils), run_time=1.2)

            self.wait_until_bookmark("bk_hook_partner")
            # Animate pairing up into clean side-by-side couples
            paired_positions = [
                [-2.2, 0.2, 0], [-1.6, 0.2, 0],   # Pair 1
                [-0.3, 0.2, 0], [0.3, 0.2, 0],    # Pair 2
                [1.6, 0.2, 0], [2.2, 0.2, 0]      # Pair 3
            ]
            self.play(
                *[pencils[i].animate.move_to(paired_positions[i]) for i in range(6)],
                run_time=1.0
            )

            self.wait_until_bookmark("bk_hook_behind")
            # Spawn a 7th pencil which represents the leftover
            leftover_pencil = create_pencil([3.8, 0.2, 0], PURPLE)
            self.play(FadeIn(leftover_pencil), run_time=0.6)

            self.wait_until_bookmark("bk_hook_happen")
            # Highlight leftover
            highlight_circle = Circle(radius=0.7, color=ORANGE_HL, stroke_width=3).move_to(leftover_pencil.get_center())
            self.play(Create(highlight_circle), run_time=0.6)
            self.play(Indicate(leftover_pencil, color=ORANGE_HL), run_time=0.6)

        # Clean Up Scene 2
        self.play(FadeOut(pencils), FadeOut(leftover_pencil), FadeOut(highlight_circle), run_time=0.8)

        # ------------------------------------------------------------
        # SCENE 3: Concept Definitions (Parity, Even, Odd)
        # ------------------------------------------------------------
        badge_concept = create_heading_badge("Concept")
        
        # Display 8 dots to represent split test
        dots_8 = VGroup(*[Dot(radius=0.18, color=PURPLE) for _ in range(8)])
        dots_8.arrange_in_grid(rows=2, cols=4, buff=0.5).shift(UP * 0.5)

        with self.voiceover(
            text='<bookmark mark="bk_def_parity"/>Parity is the property of a whole number that tells us '
                 '<bookmark mark="bk_def_split"/>whether it can be split into two equal groups. '
                 'A number is <bookmark mark="bk_def_even"/>defined as even if it can be divided into '
                 '<bookmark mark="bk_def_divided"/>two equal whole groups, with '
                 '<bookmark mark="bk_def_nothing"/>nothing left over.'
        ) as tracker:
            self.wait_until_bookmark("bk_def_parity")
            self.play(FadeIn(badge_concept), run_time=0.6)
            self.play(FadeIn(dots_8), run_time=0.8)

            self.wait_until_bookmark("bk_def_split")
            # Visualise splitting into two equal columns
            self.play(
                dots_8[0:4].animate.shift(LEFT * 0.5),
                dots_8[4:8].animate.shift(RIGHT * 0.5),
                run_time=1.0
            )

            self.wait_until_bookmark("bk_def_even")
            label_even = Text("Even", font="Poppins", font_size=32, color=PURPLE, weight=BOLD).next_to(dots_8, DOWN, buff=0.4)
            self.play(FadeIn(label_even), run_time=0.6)

            self.wait_until_bookmark("bk_def_divided")
            # Put bounding boxes around them
            box1 = SurroundingRectangle(dots_8[0:4], color=PURPLE, stroke_width=2, corner_radius=0.1)
            box2 = SurroundingRectangle(dots_8[4:8], color=PURPLE, stroke_width=2, corner_radius=0.1)
            self.play(Create(box1), Create(box2), run_time=0.8)

            self.wait_until_bookmark("bk_def_nothing")
            formula_even = math_obj("8 \\div 2 = 4", color=PURPLE).next_to(label_even, DOWN, buff=0.2)
            self.play(FadeIn(formula_even), run_time=0.6)

        # Transition to Odd
        dots_9 = VGroup(*[Dot(radius=0.18, color=PURPLE) for _ in range(9)])
        # Position 8 dots in symmetric columns, and 9th dot alone
        for i in range(4):
            dots_9[i].move_to([-1.0, 1.2 - i * 0.6, 0])
            dots_9[i+4].move_to([1.0, 1.2 - i * 0.6, 0])
        dots_9[8].move_to([0, -1.2, 0])

        with self.voiceover(
            text='A number is <bookmark mark="bk_def_odd"/>defined as odd if it cannot — '
                 '<bookmark mark="bk_def_unpaired"/>one item is always left unpaired. '
                 'So even numbers <bookmark mark="bk_def_pairable"/>are pairable, '
                 'and odd numbers <bookmark mark="bk_def_leftover"/>always have a leftover item.'
        ) as tracker:
            self.wait_until_bookmark("bk_def_odd")
            # Swap visuals from 8 to 9 dots
            self.play(
                ReplacementTransform(dots_8, dots_9[0:8]),
                FadeIn(dots_9[8]),
                FadeOut(box1), FadeOut(box2),
                FadeOut(label_even), FadeOut(formula_even),
                run_time=1.0
            )

            label_odd = Text("Odd", font="Poppins", font_size=32, color=ORANGE_HL, weight=BOLD).next_to(dots_9[8], DOWN, buff=0.4)
            self.play(FadeIn(label_odd), run_time=0.6)

            self.wait_until_bookmark("bk_def_unpaired")
            # Highlight leftover dot
            self.play(dots_9[8].animate.set_color(ORANGE_HL), run_time=0.6)
            self.play(Flash(dots_9[8], color=ORANGE_HL, line_length=0.3), run_time=0.6)

            self.wait_until_bookmark("bk_def_pairable")
            even_rule = Text("Even = Pairable (No Leftover)", font="Poppins", font_size=24, color=PURPLE).move_to([-3.0, -2.5, 0])
            self.play(FadeIn(even_rule), run_time=0.6)

            self.wait_until_bookmark("bk_def_leftover")
            odd_rule = Text("Odd = Leftover Remaining", font="Poppins", font_size=24, color=ORANGE_HL).move_to([3.0, -2.5, 0])
            self.play(FadeIn(odd_rule), run_time=0.6)
            self.wait(1.0)

        # Clear Scene 3
        self.play(
            FadeOut(badge_concept), FadeOut(dots_9), FadeOut(label_odd),
            FadeOut(even_rule), FadeOut(odd_rule),
            run_time=0.8
        )

        # ------------------------------------------------------------
        # SCENE 4: Why it Works (Pattern Demonstration)
        # ------------------------------------------------------------
        badge_pattern = create_heading_badge("Concept")
        
        # Show alternating number line
        numbers = VGroup(*[math_obj(str(i), font_size=40) for i in range(6)])
        numbers.arrange(RIGHT, buff=1.2).shift(UP * 1.0)

        with self.voiceover(
            text='Now, why <bookmark mark="bk_pat_why"/>does this happen? '
                 'Whole numbers <bookmark mark="bk_pat_pattern"/>follow a strict pattern — even, odd, even, odd — '
                 '<bookmark mark="bk_pat_zero"/>starting from zero.'
        ) as tracker:
            self.wait_until_bookmark("bk_pat_why")
            self.play(FadeIn(badge_pattern), run_time=0.6)

            self.wait_until_bookmark("bk_pat_pattern")
            self.play(FadeIn(numbers), run_time=0.8)
            
            # Label them Alternately
            labels = VGroup()
            for idx, num in enumerate(numbers):
                if idx % 2 == 0:
                    lbl = Text("even", font="Poppins", font_size=20, color=PURPLE)
                else:
                    lbl = Text("odd", font="Poppins", font_size=20, color=ORANGE_HL)
                lbl.next_to(num, DOWN, buff=0.3)
                labels.add(lbl)
            
            self.play(FadeIn(labels), run_time=1.0)

            self.wait_until_bookmark("bk_pat_zero")
            # Highlight zero
            self.play(Indicate(numbers[0], color=PURPLE), run_time=0.6)

        # Illustrate addition transitions
        # We start with 2 dots (even), add 1 to get 3 (odd)
        even_pair = VGroup(
            Dot(point=[-1.5, -1.5, 0], color=PURPLE, radius=0.15),
            Dot(point=[-1.5, -2.1, 0], color=PURPLE, radius=0.15)
        )
        plus_sign = math_obj("+", font_size=36).move_to([-0.5, -1.8, 0])
        add_dot = Dot(point=[0.5, -1.8, 0], color=ORANGE_HL, radius=0.15)
        arrow_trans = math_obj("\\rightarrow", font_size=36).move_to([1.5, -1.8, 0])
        
        result_dots = VGroup(
            Dot(point=[2.5, -1.5, 0], color=PURPLE, radius=0.15),
            Dot(point=[2.5, -2.1, 0], color=PURPLE, radius=0.15),
            Dot(point=[3.5, -1.8, 0], color=ORANGE_HL, radius=0.15)
        )

        with self.voiceover(
            text='When we <bookmark mark="bk_pat_add"/>add one to an even number, '
                 '<bookmark mark="bk_pat_break"/>we break a pair and create an unpaired item, '
                 '<bookmark mark="bk_pat_giving"/>giving us an odd number.'
        ) as tracker:
            self.wait_until_bookmark("bk_pat_add")
            self.play(FadeIn(even_pair), FadeIn(plus_sign), FadeIn(add_dot), run_time=0.8)

            self.wait_until_bookmark("bk_pat_break")
            self.play(FadeIn(arrow_trans), FadeIn(result_dots), run_time=0.8)

            self.wait_until_bookmark("bk_pat_giving")
            # Circle leftover in results
            leftover_circ = Circle(radius=0.35, color=ORANGE_HL, stroke_width=2).move_to(result_dots[2].get_center())
            self.play(Create(leftover_circ), run_time=0.6)

        # Transition Odd to Even
        # Clean up formula below, transition to next phase
        plus_sign2 = math_obj("+", font_size=36).move_to([4.3, -1.8, 0])
        add_dot2 = Dot(point=[5.1, -1.8, 0], color=PURPLE, radius=0.15)
        arrow_trans2 = math_obj("\\rightarrow", font_size=36).move_to([6.1, -1.8, 0])
        
        # New paired results
        final_dots = VGroup(
            Dot(point=[1.5, -1.5, 0], color=PURPLE, radius=0.15),
            Dot(point=[1.5, -2.1, 0], color=PURPLE, radius=0.15),
            Dot(point=[2.5, -1.5, 0], color=PURPLE, radius=0.15),
            Dot(point=[2.5, -2.1, 0], color=PURPLE, radius=0.15)
        ).shift(DOWN * 0.8) # shifted to avoid overlap

        with self.voiceover(
            text='Add <bookmark mark="bk_pat_more"/>one more, and the leftover '
                 '<bookmark mark="bk_pat_partner"/>finds a new partner, making it '
                 '<bookmark mark="bk_pat_again"/>even again. '
                 'So parity <bookmark mark="bk_pat_alternates"/>alternates because of how counting itself works.'
        ) as tracker:
            self.wait_until_bookmark("bk_pat_more")
            # Shift the old result to make space if needed
            self.play(FadeIn(plus_sign2), FadeIn(add_dot2), run_time=0.6)

            self.wait_until_bookmark("bk_pat_partner")
            # Leftover dot pairs up with the new dot
            partner_box = RoundedRectangle(corner_radius=0.1, width=1.4, height=0.7, color=PURPLE, stroke_width=2)
            partner_box.move_to([4.7, -1.8, 0])
            self.play(Create(partner_box), run_time=0.6)

            self.wait_until_bookmark("bk_pat_again")
            self.play(FadeIn(arrow_trans2), FadeIn(final_dots), run_time=0.8)

            self.wait_until_bookmark("bk_pat_alternates")
            # Flash final dots to show full balance
            self.play(Flash(final_dots, color=PURPLE, line_length=0.25), run_time=0.6)
            self.wait(1.0)

        # Clear Scene 4
        self.play(
            FadeOut(badge_pattern), FadeOut(numbers), FadeOut(labels),
            FadeOut(even_pair), FadeOut(plus_sign), FadeOut(add_dot), FadeOut(arrow_trans), FadeOut(result_dots), FadeOut(leftover_circ),
            FadeOut(plus_sign2), FadeOut(add_dot2), FadeOut(arrow_trans2), FadeOut(partner_box), FadeOut(final_dots),
            run_time=0.8
        )

        # ------------------------------------------------------------
        # SCENE 5: Question Phase (47 Students Seated in Pairs)
        # ------------------------------------------------------------
        badge_question = create_heading_badge("Question")

        # Verbatim Text Layout (Saves spaces, safe Poppins characters, splits mixed content safely)
        q_line1 = Text("A teacher has 47 students and wants to seat", font="Poppins", font_size=26, color=PURPLE)
        q_line2 = Text("them in pairs on benches.", font="Poppins", font_size=26, color=PURPLE)
        q_line3 = Text("Will every student have a partner?", font="Poppins", font_size=26, color=PURPLE)
        q_line4 = Text("If not, how many pairs will be formed and", font="Poppins", font_size=26, color=PURPLE)
        q_line5 = Text("how many students will be unpaired?", font="Poppins", font_size=26, color=PURPLE)
        
        question_block = VGroup(q_line1, q_line2, q_line3, q_line4, q_line5).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        question_block.to_edge(LEFT, buff=0.8).shift(DOWN * 0.4)

        # Question Diagram: A physical representation of a seating bench
        bench_fig = create_bench(pos=[4.0, 0.0, 0], student_color=PALE_PURPLE)
        bench_label = Text("Bench Seat", font="Poppins", font_size=18, color=PURPLE).next_to(bench_fig, UP, buff=0.2)
        diagram_group = VGroup(bench_fig, bench_label)

        with self.voiceover(
            text='<bookmark mark="bk_q_teacher"/>A teacher has forty seven students and wants '
                 '<bookmark mark="bk_q_seat"/>to seat them in pairs on benches. '
                 '<bookmark mark="bk_q_will"/>Will every student have a partner? If not, '
                 '<bookmark mark="bk_q_how"/>how many pairs will be formed and '
                 '<bookmark mark="bk_q_unpaired"/>how many students will be unpaired?'
        ) as tracker:
            self.wait_until_bookmark("bk_q_teacher")
            self.play(FadeIn(badge_question), run_time=0.6)
            self.play(FadeIn(question_block[0:2]), run_time=0.8)

            self.wait_until_bookmark("bk_q_seat")
            self.play(Create(diagram_group), run_time=1.0)

            self.wait_until_bookmark("bk_q_will")
            self.play(FadeIn(question_block[2]), run_time=0.8)

            self.wait_until_bookmark("bk_q_how")
            self.play(FadeIn(question_block[3]), run_time=0.8)

            self.wait_until_bookmark("bk_q_unpaired")
            self.play(FadeIn(question_block[4]), run_time=0.8)
            # Flash one bench dot to show individual slot
            self.play(Flash(bench_fig[1], color=ORANGE_HL, line_length=0.2), run_time=0.6)
            self.wait(1.5)

        # ------------------------------------------------------------
        # SCENE 6: Solution Phase (Mathematical Calculation)
        # ------------------------------------------------------------
        # Fade out question block but persist the figure (shift right slightly to frame solution steps)
        self.play(FadeOut(question_block), run_time=0.8)
        
        badge_solution = create_heading_badge("Solution")
        self.play(
            ReplacementTransform(badge_question, badge_solution),
            diagram_group.animate.shift(RIGHT * 1.5).scale(0.8),
            run_time=1.0
        )

        # Left Column for solution steps
        sol_x_start = -5.8
        y_pos = 1.8

        sol_step1 = math_obj("\\text{Divide } 47 \\text{ by } 2 \\rightarrow \\dfrac{47}{2}", font_size=32).move_to([sol_x_start, y_pos, 0], aligned_edge=LEFT)
        sol_step2 = math_obj("47 = 2 \\times 23 + 1", font_size=32).move_to([sol_x_start, y_pos - 0.8, 0], aligned_edge=LEFT)
        sol_step3 = Text("Pairs formed: 23", font="Poppins", font_size=28, color=PURPLE).move_to([sol_x_start, y_pos - 1.6, 0], aligned_edge=LEFT)
        sol_step4 = Text("Unpaired: 1 student", font="Poppins", font_size=28, color=ORANGE_HL, weight=BOLD).move_to([sol_x_start, y_pos - 2.4, 0], aligned_edge=LEFT)
        sol_step5 = Text("47 is an ODD number", font="Poppins", font_size=32, color=ORANGE_HL, weight=BOLD).move_to([sol_x_start, y_pos - 3.4, 0], aligned_edge=LEFT)

        with self.voiceover(
            text='For the solution... We <bookmark mark="bk_sol_divide"/>divide forty seven by two. '
                 '<bookmark mark="bk_sol_equals"/>Forty seven equals, two times twenty three, plus one. '
                 '<bookmark mark="bk_sol_pairs"/>So twenty three pairs are formed. '
                 '<bookmark mark="bk_sol_unpaired"/>One student is left unpaired. '
                 '<bookmark mark="bk_sol_odd"/>This tells us forty seven is an odd number. '
                 '<bookmark mark="bk_sol_logic"/>This is the same logic engineers use when checking '
                 '<bookmark mark="bk_sol_balanced"/>whether items can be split into balanced groups.'
        ) as tracker:
            self.wait_until_bookmark("bk_sol_divide")
            self.play(FadeIn(sol_step1), run_time=0.8)

            self.wait_until_bookmark("bk_sol_equals")
            self.play(sol_step1.animate.set_opacity(0.4), FadeIn(sol_step2), run_time=0.8)

            self.wait_until_bookmark("bk_sol_pairs")
            self.play(sol_step2.animate.set_opacity(0.4), FadeIn(sol_step3), run_time=0.8)

            self.wait_until_bookmark("bk_sol_unpaired")
            # Highlight bench model leftovers
            unpaired_dot = Dot(point=[5.5, -1.5, 0], color=ORANGE_HL, radius=0.15)
            leftover_label = Text("Leftover", font="Poppins", font_size=16, color=ORANGE_HL).next_to(unpaired_dot, DOWN, buff=0.1)
            self.play(
                sol_step3.animate.set_opacity(0.4),
                FadeIn(sol_step4),
                FadeIn(unpaired_dot), FadeIn(leftover_label),
                run_time=0.8
            )

            self.wait_until_bookmark("bk_sol_odd")
            self.play(sol_step4.animate.set_opacity(0.4), FadeIn(sol_step5), run_time=0.8)
            self.play(Indicate(sol_step5, color=ORANGE_HL), run_time=0.8)

            self.wait_until_bookmark("bk_sol_logic")
            # Visualise an engineering verification box in corner
            eng_box = RoundedRectangle(corner_radius=0.1, width=3.2, height=1.5, color=PALE_PURPLE, stroke_width=2).move_to([4.5, -2.2, 0])
            eng_lbl = Text("Symmetric Group Check", font="Poppins", font_size=16, color=PALE_PURPLE).move_to(eng_box.get_center())
            self.play(Create(eng_box), FadeIn(eng_lbl), run_time=1.0)

            self.wait_until_bookmark("bk_sol_balanced")
            self.play(Flash(eng_box, color=PALE_PURPLE, line_length=0.2), run_time=0.6)
            self.wait(1.5)

        # Clear Solution Phase
        self.play(
            FadeOut(badge_solution), FadeOut(diagram_group), FadeOut(sol_step1), FadeOut(sol_step2),
            FadeOut(sol_step3), FadeOut(sol_step4), FadeOut(sol_step5), FadeOut(unpaired_dot),
            FadeOut(leftover_label), FadeOut(eng_box), FadeOut(eng_lbl),
            run_time=0.8
        )

        # ------------------------------------------------------------
        # SCENE 7: Summary Phase (Takeaways)
        # ------------------------------------------------------------
        badge_summary = create_heading_badge("Summary")

        bullet1_icon = Dot(color=ORANGE_HL, radius=0.08).move_to([-5.5, 1.2, 0])
        bullet1_txt = Text("Parity tells us whether a number is even or odd.", font="Poppins", font_size=24, color=PURPLE).next_to(bullet1_icon, RIGHT, buff=0.3)
        bullet1 = VGroup(bullet1_icon, bullet1_txt)

        bullet2_icon = Dot(color=ORANGE_HL, radius=0.08).move_to([-5.5, 0.2, 0])
        bullet2_txt1 = Text("Even numbers are pairable;", font="Poppins", font_size=24, color=PURPLE)
        bullet2_txt2 = Text("odd numbers have one unpaired leftover.", font="Poppins", font_size=24, color=ORANGE_HL)
        bullet2_txt = VGroup(bullet2_txt1, bullet2_txt2).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        bullet2_txt.next_to(bullet2_icon, RIGHT, buff=0.3)
        bullet2 = VGroup(bullet2_icon, bullet2_txt)

        with self.voiceover(
            text='To <bookmark mark="bk_sum_main"/>summarize... Parity tells us whether '
                 '<bookmark mark="bk_sum_parity"/>a number is even or odd. '
                 '<bookmark mark="bk_sum_even"/>Even numbers are pairable — and '
                 '<bookmark mark="bk_sum_odd"/>odd numbers have one unpaired leftover.'
        ) as tracker:
            self.wait_until_bookmark("bk_sum_main")
            self.play(FadeIn(badge_summary), run_time=0.6)

            self.wait_until_bookmark("bk_sum_parity")
            self.play(FadeIn(bullet1), run_time=0.8)

            self.wait_until_bookmark("bk_sum_even")
            self.play(FadeIn(bullet2[0]), FadeIn(bullet2[1][0]), run_time=0.8)

            self.wait_until_bookmark("bk_sum_odd")
            self.play(FadeIn(bullet2[1][1]), run_time=0.8)
            self.wait(2.0)

        # Clean up screen
        self.play(FadeOut(badge_summary), FadeOut(bullet1), FadeOut(bullet2), run_time=1.0)
        self.wait(0.6)