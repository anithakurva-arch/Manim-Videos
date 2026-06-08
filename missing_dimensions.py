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
# HELPER FUNCTIONS (REQUIRED)
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

def create_dimension(start, end, label_str, direction=DOWN, buff=0.3):
    arrow = DoubleArrow(start=start, end=end,
                        color=PURPLE, stroke_width=2,
                        tip_length=0.2, buff=0)
    label = Text(label_str, font="Poppins", font_size=22, color=PURPLE)
    label.next_to(arrow.get_center(), direction, buff=0.15)
    return VGroup(arrow, label)

def create_unknown(position):
    return Text("?", font="Poppins", font_size=36,
                color=ORANGE_HL, weight=BOLD).move_to(position)

def math(tex_str, color=PURPLE, font_size=36):
    return MathTex(tex_str,
                   tex_template=TexFontTemplates.gnu_freesans_tx,
                   color=color, font_size=font_size)


# ============================================================
# MAIN MANIM SCENE
# ============================================================
class MissingDimensions(VoiceoverScene):
    def construct(self):
        # Setup Text-to-Speech service
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

        title = Text("Perimeter and Area", font="Poppins", font_size=48, color=WHITE, weight=BOLD)
        subtitle = Text("Finding Missing Dimensions", font="Poppins", font_size=32, color=PALE_PURPLE)
        title_group = VGroup(title, subtitle).arrange(DOWN, buff=0.4).move_to(ORIGIN)

        with self.voiceover(text='<bookmark mark="bk_intro_1"/>Hello students!') as tracker:
            self.wait_until_bookmark("bk_intro_1")
            self.play(FadeIn(title_group), run_time=1.0)
            self.wait(0.5)

        self.play(FadeOut(title_group), run_time=0.8)

        # Transition Background to Lavender
        self.play(bg_rect.animate.set_fill(LAVENDER_BG, opacity=1), run_time=1.0)

        # ------------------------------------------------------------
        # SCENE 2: Table & Chairs (Intro Segment)
        # ------------------------------------------------------------
        table = Rectangle(width=5.0, height=2.5, color=PURPLE, stroke_width=3)
        table.move_to(ORIGIN)

        # Draw visual chairs around table representation
        chairs = VGroup()
        for x in np.linspace(-2.2, 2.2, 5):
            chairs.add(Dot(point=[x, 1.5, 0], color=PALE_PURPLE, radius=0.15))
            chairs.add(Dot(point=[x, -1.5, 0], color=PALE_PURPLE, radius=0.15))
        for y in np.linspace(-0.8, 0.8, 2):
            chairs.add(Dot(point=[2.8, y, 0], color=PALE_PURPLE, radius=0.15))
            chairs.add(Dot(point=[-2.8, y, 0], color=PALE_PURPLE, radius=0.15))

        with self.voiceover(
            text='<bookmark mark="bk_intro_2"/>Imagine you are arranging chairs around a rectangular classroom table. '
                 '<bookmark mark="bk_intro_3"/>You know the total number of chairs that fit around it, and you know how many fit along one side. '
                 '<bookmark mark="bk_intro_4"/>Could you figure out how many fit along the other side without counting again?'
        ) as tracker:
            self.wait_until_bookmark("bk_intro_2")
            self.play(Create(table), run_time=1.2)

            self.wait_until_bookmark("bk_intro_3")
            self.play(FadeIn(chairs), run_time=1.0)

            self.wait_until_bookmark("bk_intro_4")
            # Highlight top row of chairs and show question mark on the right
            self.play(
                chairs[0:10].animate.set_color(ORANGE_HL),
                run_time=0.8
            )
            q_mark = create_unknown(RIGHT * 3.5)
            self.play(FadeIn(q_mark), run_time=0.6)
            self.wait(1.0)

        # Clean Up Scene 2
        self.play(FadeOut(table), FadeOut(chairs), FadeOut(q_mark), run_time=0.8)

        # ------------------------------------------------------------
        # SCENE 3: Concept Definition & Formulas
        # ------------------------------------------------------------
        badge_concept = create_heading_badge("Concept")
        
        rect_concept = Rectangle(width=4.0, height=2.0, color=PURPLE, stroke_width=2.5).shift(UP * 0.5)
        rect_formula = math("P = 2(l + w)", font_size=36).next_to(rect_concept, DOWN, buff=0.5)

        with self.voiceover(
            text='<bookmark mark="bk_concept_1"/>The perimeter — is the total length around a shape. '
                 '<bookmark mark="bk_concept_2"/>For a rectangle, the perimeter equals, two times the sum of, length, and width.'
        ) as tracker:
            self.wait_until_bookmark("bk_concept_1")
            self.play(FadeIn(badge_concept), run_time=0.6)
            self.play(Create(rect_concept), run_time=1.2)

            # Trace visual outline to show "around"
            tracer = rect_concept.copy().set_color(ORANGE_HL).set_stroke(width=4)
            self.play(Create(tracer), run_time=1.5)
            self.play(FadeOut(tracer), run_time=0.4)

            self.wait_until_bookmark("bk_concept_2")
            self.play(FadeIn(rect_formula), run_time=0.8)

        # Transverse to Square Concept
        sq_concept = Square(side_length=2.0, color=PURPLE, stroke_width=2.5).shift(UP * 0.5)
        sq_formula = math("P = 4s", font_size=36).next_to(sq_concept, DOWN, buff=0.5)

        with self.voiceover(
            text='<bookmark mark="bk_concept_3"/>For a square, the perimeter equals, four times the length of, one side. '
                 '<bookmark mark="bk_concept_4"/>So if we know the perimeter and one dimension, we can rearrange the formula — and find the missing one. '
                 '<bookmark mark="bk_concept_5"/>This means perimeter is not just for measuring — it is also a tool to work backwards.'
        ) as tracker:
            self.wait_until_bookmark("bk_concept_3")
            self.play(
                ReplacementTransform(rect_concept, sq_concept),
                ReplacementTransform(rect_formula, sq_formula),
                run_time=1.0
            )

            self.wait_until_bookmark("bk_concept_4")
            # Show algebraic rearrangement visually
            rearranged_formula = math("s = \\dfrac{P}{4}", font_size=36).next_to(sq_concept, DOWN, buff=0.5)
            self.play(ReplacementTransform(sq_formula, rearranged_formula), run_time=1.0)

            self.wait_until_bookmark("bk_concept_5")
            label_tool = Text("Tool to work backwards", font="Poppins", font_size=26, color=ORANGE_HL).to_edge(DOWN, buff=0.4)
            self.play(FadeIn(label_tool), run_time=0.8)
            self.wait(1.0)

        self.play(FadeOut(badge_concept), FadeOut(sq_concept), FadeOut(rearranged_formula), FadeOut(label_tool), run_time=0.8)

        # ------------------------------------------------------------
        # SCENE 4: Why It Works
        # ------------------------------------------------------------
        badge_why = create_heading_badge("Why it works")
        rect_why = Rectangle(width=4.5, height=2.2, color=PURPLE, stroke_width=2.5).shift(UP * 0.5)
        
        # Labels for sides
        label_top = math("l").next_to(rect_why, UP, buff=0.15)
        label_bottom = math("l").next_to(rect_why, DOWN, buff=0.15)
        label_left = math("w").next_to(rect_why, LEFT, buff=0.15)
        label_right = math("w").next_to(rect_why, RIGHT, buff=0.15)
        labels_rect = VGroup(label_top, label_bottom, label_left, label_right)

        with self.voiceover(
            text='<bookmark mark="bk_why_1"/>Now, why does this work? '
                 '<bookmark mark="bk_why_2"/>A rectangle has two equal lengths and two equal widths. '
                 '<bookmark mark="bk_why_3"/>So once we know the perimeter and one of them, simple algebra gives us the other.'
        ) as tracker:
            self.wait_until_bookmark("bk_why_1")
            self.play(FadeIn(badge_why), run_time=0.6)
            self.play(Create(rect_why), run_time=1.0)

            self.wait_until_bookmark("bk_why_2")
            self.play(FadeIn(labels_rect), run_time=0.8)
            # Flash opposite sides
            self.play(
                label_top.animate.set_color(ORANGE_HL),
                label_bottom.animate.set_color(ORANGE_HL),
                run_time=0.6
            )
            self.play(
                label_top.animate.set_color(PURPLE),
                label_bottom.animate.set_color(PURPLE),
                label_left.animate.set_color(ORANGE_HL),
                label_right.animate.set_color(ORANGE_HL),
                run_time=0.6
            )
            self.play(label_left.animate.set_color(PURPLE), label_right.animate.set_color(PURPLE), run_time=0.4)

            self.wait_until_bookmark("bk_why_3")
            algebra_eq = math("2l + 2w = P", font_size=36).next_to(rect_why, DOWN, buff=0.5)
            self.play(FadeIn(algebra_eq), run_time=0.8)

        # Transition to square
        sq_why = Square(side_length=2.2, color=PURPLE, stroke_width=2.5).shift(UP * 0.5)
        s_labels = VGroup(
            math("s").next_to(sq_why, UP, buff=0.15),
            math("s").next_to(sq_why, DOWN, buff=0.15),
            math("s").next_to(sq_why, LEFT, buff=0.15),
            math("s").next_to(sq_why, RIGHT, buff=0.15)
        )

        with self.voiceover(
            text='<bookmark mark="bk_why_4"/>A square has four equal sides, so its side is simply the perimeter divided by four.'
        ) as tracker:
            self.wait_until_bookmark("bk_why_4")
            self.play(
                ReplacementTransform(rect_why, sq_why),
                ReplacementTransform(labels_rect, s_labels),
                ReplacementTransform(algebra_eq, math("s = \\dfrac{P}{4}", font_size=36).next_to(sq_why, DOWN, buff=0.5)),
                run_time=1.0
            )
            self.wait(1.0)

        self.play(FadeOut(badge_why), FadeOut(sq_why), FadeOut(s_labels), self.mobjects[-1].animate.set_opacity(0), run_time=0.8)

        # ------------------------------------------------------------
        # SCENE 5: Question Phase (Notebook & Tile)
        # ------------------------------------------------------------
        badge_question = create_heading_badge("Question")
        
        # Notebook setup
        notebook_rect = Rectangle(width=4.0, height=2.6, color=PURPLE, stroke_width=2.5).shift(DOWN * 0.5)
        notebook_perim = Text("Perimeter = 34 cm", font="Poppins", font_size=24, color=PURPLE).next_to(notebook_rect, UP, buff=0.4)
        
        len_arrow = create_dimension(
            notebook_rect.get_corner(DL) + DOWN * 0.3,
            notebook_rect.get_corner(DR) + DOWN * 0.3,
            "11 cm", DOWN
        )
        wid_arrow = create_dimension(
            notebook_rect.get_corner(DR) + RIGHT * 0.3,
            notebook_rect.get_corner(UR) + RIGHT * 0.3,
            "?", RIGHT
        )
        # Apply orange color scheme to unknown mark
        wid_arrow[1].set_color(ORANGE_HL).set_opacity(1)

        with self.voiceover(
            text='<bookmark mark="bk_q1_1"/>Part one... The perimeter of a rectangular notebook is, thirty four centimeters. '
                 '<bookmark mark="bk_q1_2"/>Its length is, eleven centimeters. '
                 '<bookmark mark="bk_q1_3"/>Find its width, and check whether two such notebooks would fit along a, twenty four centimeter shelf.'
        ) as tracker:
            self.wait_until_bookmark("bk_q1_1")
            self.play(FadeIn(badge_question), run_time=0.6)
            self.play(Create(notebook_rect), FadeIn(notebook_perim), run_time=1.0)

            self.wait_until_bookmark("bk_q1_2")
            self.play(Create(len_arrow), run_time=0.8)

            self.wait_until_bookmark("bk_q1_3")
            self.play(Create(wid_arrow), run_time=0.8)
            self.wait(1.5)

        # Transition to Question Part 2 (Square Tile)
        tile_sq = Square(side_length=2.8, color=PURPLE, stroke_width=2.5).shift(DOWN * 0.5)
        tile_perim = Text("Perimeter = 48 cm", font="Poppins", font_size=24, color=PURPLE).next_to(tile_sq, UP, buff=0.4)
        tile_side_arrow = create_dimension(
            tile_sq.get_corner(DL) + DOWN * 0.3,
            tile_sq.get_corner(DR) + DOWN * 0.3,
            "?", DOWN
        )
        tile_side_arrow[1].set_color(ORANGE_HL)

        with self.voiceover(
            text='<bookmark mark="bk_q2_1"/>Part two... A square tile has a perimeter of, forty eight centimeters. '
                 '<bookmark mark="bk_q2_2"/>Find the length of one side.'
        ) as tracker:
            self.wait_until_bookmark("bk_q2_1")
            self.play(
                ReplacementTransform(notebook_rect, tile_sq),
                ReplacementTransform(notebook_perim, tile_perim),
                FadeOut(len_arrow),
                ReplacementTransform(wid_arrow, tile_side_arrow),
                run_time=1.0
            )

            self.wait_until_bookmark("bk_q2_2")
            self.play(Indicate(tile_side_arrow[1]), run_time=0.8)
            self.wait(1.0)

        # Clean up Question Phase
        self.play(FadeOut(badge_question), FadeOut(tile_sq), FadeOut(tile_perim), FadeOut(tile_side_arrow), run_time=0.8)

        # ------------------------------------------------------------
        # SCENE 6: Solution Notebook
        # ------------------------------------------------------------
        badge_solution = create_heading_badge("Solution")
        
        # Redraw Notebook (Shifted to the Right)
        notebook_rect = Rectangle(width=3.2, height=2.0, color=PURPLE, stroke_width=2.5).shift(RIGHT * 3.5 + UP * 0.5)
        notebook_perim = Text("P = 34 cm", font="Poppins", font_size=22, color=PURPLE).next_to(notebook_rect, UP, buff=0.3)
        len_arrow = create_dimension(
            notebook_rect.get_corner(DL) + DOWN * 0.3,
            notebook_rect.get_corner(DR) + DOWN * 0.3,
            "11 cm", DOWN
        )
        wid_arrow = create_dimension(
            notebook_rect.get_corner(DR) + RIGHT * 0.3,
            notebook_rect.get_corner(UR) + RIGHT * 0.3,
            "?", RIGHT
        )
        wid_arrow[1].set_color(ORANGE_HL)
        notebook_group = VGroup(notebook_rect, notebook_perim, len_arrow, wid_arrow)

        # Left Column for steps
        step_x_start = -5.5
        y_start = 1.8
        
        step1 = math("2(l + w) = P", font_size=32).move_to([step_x_start, y_start, 0], aligned_edge=LEFT)
        step2 = math("2(11 + w) = 34", font_size=32).move_to([step_x_start, y_start - 0.7, 0], aligned_edge=LEFT)
        step3 = math("11 + w = 17", font_size=32).move_to([step_x_start, y_start - 1.4, 0], aligned_edge=LEFT)
        step4 = math("w = 6\\text{ cm}", color=ORANGE_HL, font_size=36).move_to([step_x_start, y_start - 2.1, 0], aligned_edge=LEFT)

        with self.voiceover(
            text='<bookmark mark="bk_sol1_1"/>For the notebook — two times the sum of length and width, equals the perimeter. '
                 '<bookmark mark="bk_sol1_2"/>Two times, eleven plus width, equals thirty four. '
                 '<bookmark mark="bk_sol1_3"/>Eleven plus width, equals seventeen. '
                 '<bookmark mark="bk_sol1_4"/>So width equals, six centimeters.'
        ) as tracker:
            self.wait_until_bookmark("bk_sol1_1")
            self.play(FadeIn(badge_solution), FadeIn(notebook_group), run_time=0.8)
            self.play(FadeIn(step1), run_time=0.6)

            self.wait_until_bookmark("bk_sol1_2")
            self.play(step1.animate.set_opacity(0.4), FadeIn(step2), run_time=0.6)

            self.wait_until_bookmark("bk_sol1_3")
            self.play(step2.animate.set_opacity(0.4), FadeIn(step3), run_time=0.6)

            self.wait_until_bookmark("bk_sol1_4")
            # Create a localized replacement for the updated label
            updated_wid_label = Text("6 cm", font="Poppins", font_size=22, color=ORANGE_HL).move_to(wid_arrow[1])
            self.play(
                step3.animate.set_opacity(0.4),
                FadeIn(step4),
                ReplacementTransform(wid_arrow[1], updated_wid_label),
                run_time=0.8
            )
            # Re-bind elements to reference the updated group
            wid_arrow = VGroup(wid_arrow[0], updated_wid_label)
            notebook_group = VGroup(notebook_rect, notebook_perim, len_arrow, wid_arrow)
            self.wait(0.5)

        # Fit Check on Shelf Visualization
        shelf_line = Line(start=[-6, -2.8, 0], end=[1, -2.8, 0], color=PURPLE, stroke_width=4)
        shelf_label = Text("24 cm Shelf", font="Poppins", font_size=20, color=PURPLE).next_to(shelf_line, DOWN, buff=0.15)
        
        # Visualize books on shelf
        book1 = Rectangle(width=1.2, height=1.8, color=PURPLE, fill_color=PALE_PURPLE, fill_opacity=0.5).move_to([-5.4, -1.8, 0])
        book2 = Rectangle(width=1.2, height=1.8, color=PURPLE, fill_color=PALE_PURPLE, fill_opacity=0.5).move_to([-4.2, -1.8, 0])
        book1_label = Text("6 cm", font="Poppins", font_size=14, color=WHITE).move_to(book1.get_center())
        book2_label = Text("6 cm", font="Poppins", font_size=14, color=WHITE).move_to(book2.get_center())
        books_group = VGroup(book1, book2, book1_label, book2_label)

        with self.voiceover(
            text='<bookmark mark="bk_sol1_5"/>Two notebooks placed side by side would need twelve centimeters — which fits well on the shelf.'
        ) as tracker:
            self.wait_until_bookmark("bk_sol1_5")
            self.play(Create(shelf_line), FadeIn(shelf_label), run_time=0.6)
            self.play(FadeIn(books_group), run_time=0.8)
            
            # Show calculation visually
            calc_text = math("6 + 6 = 12\\text{ cm} < 24\\text{ cm}", font_size=26).next_to(shelf_line, UP, buff=1.2).shift(RIGHT * 3)
            self.play(FadeIn(calc_text), run_time=0.6)
            self.wait(2.0)

        # Clear Notebook Solution
        self.play(
            FadeOut(notebook_group), FadeOut(step1), FadeOut(step2), FadeOut(step3), FadeOut(step4),
            FadeOut(shelf_line), FadeOut(shelf_label), FadeOut(books_group), FadeOut(calc_text),
            run_time=0.8
        )

        # ------------------------------------------------------------
        # SCENE 7: Solution Tile
        # ------------------------------------------------------------
        # Re-draw Square Tile (Shifted to the Right)
        tile_sq = Square(side_length=2.4, color=PURPLE, stroke_width=2.5).shift(RIGHT * 3.5 + UP * 0.5)
        tile_perim = Text("P = 48 cm", font="Poppins", font_size=22, color=PURPLE).next_to(tile_sq, UP, buff=0.3)
        tile_side_arrow = create_dimension(
            tile_sq.get_corner(DL) + DOWN * 0.3,
            tile_sq.get_corner(DR) + DOWN * 0.3,
            "?", DOWN
        )
        tile_side_arrow[1].set_color(ORANGE_HL)
        tile_group = VGroup(tile_sq, tile_perim, tile_side_arrow)

        # Left Column steps
        tile_step1 = math("P = 4s", font_size=32).move_to([step_x_start, y_start, 0], aligned_edge=LEFT)
        tile_step2 = math("4s = 48", font_size=32).move_to([step_x_start, y_start - 0.7, 0], aligned_edge=LEFT)
        tile_step3 = math("s = 12\\text{ cm}", color=ORANGE_HL, font_size=36).move_to([step_x_start, y_start - 1.4, 0], aligned_edge=LEFT)

        with self.voiceover(
            text='<bookmark mark="bk_sol2_1"/>For the tile — the perimeter equals, four times the side. '
                 '<bookmark mark="bk_sol2_2"/>Four times the side, equals forty eight. '
                 '<bookmark mark="bk_sol2_3"/>So the side equals, twelve centimeters.'
        ) as tracker:
            self.wait_until_bookmark("bk_sol2_1")
            self.play(FadeIn(tile_group), run_time=0.8)
            self.play(FadeIn(tile_step1), run_time=0.6)

            self.wait_until_bookmark("bk_sol2_2")
            self.play(tile_step1.animate.set_opacity(0.4), FadeIn(tile_step2), run_time=0.6)

            self.wait_until_bookmark("bk_sol2_3")
            updated_tile_label = Text("12 cm", font="Poppins", font_size=22, color=ORANGE_HL).move_to(tile_side_arrow[1])
            self.play(
                tile_step2.animate.set_opacity(0.4),
                FadeIn(tile_step3),
                ReplacementTransform(tile_side_arrow[1], updated_tile_label),
                run_time=0.8
            )
            tile_side_arrow = VGroup(tile_side_arrow[0], updated_tile_label)
            tile_group = VGroup(tile_sq, tile_perim, tile_side_arrow)
            self.wait(0.5)

        # Build visual tile grid to represent flooring application
        floor_grid = VGroup()
        for i in range(3):
            for j in range(3):
                tile = Square(side_length=0.6, color=PURPLE, stroke_width=1, fill_color=PALE_PURPLE, fill_opacity=0.3)
                tile.move_to([-2 + j * 0.6, -1.5 + i * 0.6, 0])
                floor_grid.add(tile)

        with self.voiceover(
            text='<bookmark mark="bk_sol2_4"/>This is the same idea builders use, when calculating tile sizes for a floor.'
        ) as tracker:
            self.wait_until_bookmark("bk_sol2_4")
            self.play(FadeIn(floor_grid), run_time=1.0)
            self.wait(2.0)

        # Clear Tile Solution
        self.play(
            FadeOut(tile_group), FadeOut(tile_step1), FadeOut(tile_step2), FadeOut(tile_step3),
            FadeOut(floor_grid), FadeOut(badge_solution),
            run_time=0.8
        )

        # ------------------------------------------------------------
        # SCENE 8: Summary
        # ------------------------------------------------------------
        badge_summary = create_heading_badge("Summary")
        
        bullet1_p1 = Text("Perimeter formulas can be rearranged to find missing dimensions.", font="Poppins", font_size=24, color=PURPLE)
        bullet2_p1 = Text("Rectangle:", font="Poppins", font_size=24, color=PURPLE)
        bullet2_p2 = math("s = \\dfrac{P - 2l}{2}", font_size=26)
        bullet2 = VGroup(bullet2_p1, bullet2_p2).arrange(RIGHT, buff=0.2)
        
        bullet3_p1 = Text("Square:", font="Poppins", font_size=24, color=PURPLE)
        bullet3_p2 = math("s = \\dfrac{P}{4}", font_size=26)
        bullet3 = VGroup(bullet3_p1, bullet3_p2).arrange(RIGHT, buff=0.2)

        summary_list = VGroup(bullet1_p1, bullet2, bullet3).arrange(DOWN, buff=0.6, aligned_edge=LEFT).shift(LEFT * 1.5 + DOWN * 0.5)

        with self.voiceover(
            text='<bookmark mark="bk_sum_1"/>To summarize... Perimeter formulas can be rearranged to find missing dimensions. '
                 '<bookmark mark="bk_sum_2"/>For a rectangle, perimeter is two times the sum of length and width. '
                 '<bookmark mark="bk_sum_3"/>For a square — the side is the perimeter, divided by four.'
        ) as tracker:
            self.wait_until_bookmark("bk_sum_1")
            self.play(FadeIn(badge_summary), run_time=0.6)
            self.play(FadeIn(bullet1_p1), run_time=0.8)

            self.wait_until_bookmark("bk_sum_2")
            self.play(FadeIn(bullet2), run_time=0.8)

            self.wait_until_bookmark("bk_sum_3")
            self.play(FadeIn(bullet3), run_time=0.8)
            self.wait(2.0)

        # Fade out everything at the end
        self.play(FadeOut(badge_summary), FadeOut(summary_list), run_time=1.0)
        self.wait(0.6)