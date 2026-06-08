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
                urllib.request.urlretrieve(url, path)
            except Exception:
                continue
        try:
            manimpango.register_font(path)
        except Exception:
            pass

_setup_poppins()

# ============================================================
# HELPER FUNCTIONS
# ============================================================
def create_heading_badge(text_str):
    t = Text(text_str, font="Poppins", font_size=28, color=WHITE, weight=BOLD)
    badge = RoundedRectangle(
        corner_radius=0.2,
        width=t.width + 0.6, height=t.height + 0.3,
        fill_color=PURPLE, fill_opacity=1, stroke_width=0,
    )
    badge.move_to(t)
    return VGroup(badge, t).to_corner(UL, buff=0.5)

def create_dimension(start, end, label_str, direction=DOWN, color=PURPLE):
    arrow = DoubleArrow(start=start, end=end, color=color, stroke_width=2, tip_length=0.15, buff=0)
    label = Text(label_str, font="Poppins", font_size=20, color=color)
    label.next_to(arrow.get_center(), direction, buff=0.1)
    return VGroup(arrow, label)

def math(tex_str, color=PURPLE, font_size=32):
    return MathTex(tex_str, tex_template=TexFontTemplates.gnu_freesans_tx, color=color, font_size=font_size)

# ============================================================
# MAIN MANIM SCENE
# ============================================================
class MissingDimensions(VoiceoverScene):
    def construct(self):
        self.set_speech_service(
            OpenAIService(
                voice="shimmer",
                model="gpt-4o-mini-tts",
                instructions="Warm, patient teacher. Moderate-to-slow pace.",
            ),
            create_subcaption=False,
        )

        # 1. INTRO
        bg_rect = FullScreenRectangle(fill_color=PURPLE, fill_opacity=1, stroke_width=0)
        self.add(bg_rect)
        title = Text("Perimeter and Area", font="Poppins", font_size=48, color=WHITE, weight=BOLD)
        subtitle = Text("Finding Missing Dimensions", font="Poppins", font_size=32, color=PALE_PURPLE)
        title_group = VGroup(title, subtitle).arrange(DOWN, buff=0.4)

        with self.voiceover(text='<bookmark mark="bk_intro_1"/>Hello students!') as tracker:
            self.play(FadeIn(title_group))
        self.play(FadeOut(title_group), bg_rect.animate.set_fill(LAVENDER_BG))

        # 2. VISUAL INTRO (TABLE)
        table = Rectangle(width=4.0, height=2.0, color=PURPLE)
        chairs = VGroup(*[Dot(color=PALE_PURPLE).move_to([x, y, 0]) 
                         for x in np.linspace(-1.8, 1.8, 5) for y in [-1.2, 1.2]])
        table_scene = VGroup(table, chairs).center()

        with self.voiceover(text='<bookmark mark="bk_intro_2"/>Imagine arranging chairs around a table. You know the total, and one side. Can you find the other?') as tracker:
            self.play(Create(table))
            self.play(FadeIn(chairs))
        self.play(FadeOut(table_scene))

        # 3. CONCEPT & FORMULAS (ZONING APPLIED)
        badge = create_heading_badge("Concept")
        self.add(badge)

        # Left Zone: Formulas
        formula_rect = math("P = 2(l + w)").to_edge(LEFT, buff=1.5).shift(UP * 0.5)
        formula_sq = math("P = 4s").next_to(formula_rect, DOWN, buff=1, aligned_edge=LEFT)
        
        # Right Zone: Shapes
        rect_shape = Rectangle(width=3, height=1.5, color=PURPLE).to_edge(RIGHT, buff=1.5).shift(UP * 0.5)
        sq_shape = Square(side_length=2, color=PURPLE).move_to(rect_shape)

        with self.voiceover(text='The perimeter is the length around a shape. For a rectangle, it is twice the length plus width.') as tracker:
            self.play(Write(formula_rect), Create(rect_shape))
        
        with self.voiceover(text='For a square, it is simply four times the side.') as tracker:
            self.play(
                ReplacementTransform(rect_shape, sq_shape),
                Write(formula_sq)
            )
        self.play(FadeOut(formula_rect), FadeOut(formula_sq), FadeOut(sq_shape), FadeOut(badge))

        # 4. QUESTION PHASE
        badge = create_heading_badge("Question")
        self.add(badge)
        
        q_text = Text("Notebook: P = 34cm, L = 11cm. Find W.\nSquare Tile: P = 48cm. Find Side.", 
                      font="Poppins", font_size=24, color=PURPLE, line_spacing=1).center()
        
        with self.voiceover(text='Part one: A notebook with perimeter 34 and length 11. Part two: A tile with perimeter 48.') as tracker:
            self.play(Write(q_text))
        self.play(FadeOut(q_text), FadeOut(badge))

        # 5. SOLUTION 1: NOTEBOOK (PROPER SPLIT SCREEN)
        badge = create_heading_badge("Solution: Notebook")
        self.add(badge)

        # Right: Visual Group
        nb_rect = Rectangle(width=2.5, height=3.5, color=PURPLE).to_edge(RIGHT, buff=1.5)
        nb_len = create_dimension(nb_rect.get_corner(UL), nb_rect.get_corner(DL), "11 cm", LEFT)
        nb_wid = create_dimension(nb_rect.get_corner(DL), nb_rect.get_corner(DR), "?", DOWN, color=ORANGE_HL)
        nb_label = Text("P = 34 cm", font_size=20, color=PURPLE).next_to(nb_rect, UP)
        nb_group = VGroup(nb_rect, nb_len, nb_wid, nb_label)

        # Left: Algebraic Steps
        steps = VGroup(
            math("2(l + w) = P"),
            math("2(11 + w) = 34"),
            math("11 + w = 17"),
            math("w = 6\\text{ cm}", color=ORANGE_HL)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.5).to_edge(LEFT, buff=1.2)

        with self.voiceover(text='Using the formula, 2 times 11 plus width equals 34.') as tracker:
            self.play(FadeIn(nb_group))
            self.play(Write(steps[0]))
            self.play(Write(steps[1]))

        with self.voiceover(text='Dividing by 2 gives 17, so the width must be 6 centimeters.') as tracker:
            self.play(steps[0:2].animate.set_opacity(0.3))
            self.play(Write(steps[2]))
            self.play(Write(steps[3]))
            
            # Update visual label
            new_wid = create_dimension(nb_rect.get_corner(DL), nb_rect.get_corner(DR), "6 cm", DOWN, color=ORANGE_HL)
            self.play(ReplacementTransform(nb_wid, new_wid))

        # Shelf check (Bottom Zone)
        shelf = Line(LEFT*2, RIGHT*2, color=PURPLE).to_edge(DOWN, buff=1.5).shift(RIGHT*2.5)
        shelf_txt = Text("24 cm Shelf", font_size=18, color=PURPLE).next_to(shelf, DOWN)
        books = VGroup(
            Rectangle(width=0.8, height=1.2, fill_opacity=0.5, color=PURPLE).next_to(shelf, UP, buff=0, aligned_edge=LEFT),
            Rectangle(width=0.8, height=1.2, fill_opacity=0.5, color=PURPLE).next_to(shelf, UP, buff=0).shift(LEFT*0.2)
        )
        
        with self.voiceover(text='Two notebooks total 12 centimeters, so they fit easily on a 24 centimeter shelf.') as tracker:
            self.play(Create(shelf), Write(shelf_txt))
            self.play(FadeIn(books))
        
        self.play(FadeOut(nb_group), FadeOut(steps), FadeOut(shelf), FadeOut(shelf_txt), FadeOut(books), FadeOut(badge))

        # 6. SOLUTION 2: SQUARE TILE
        badge = create_heading_badge("Solution: Square Tile")
        self.add(badge)

        # Right: Visual Group
        tile_sq = Square(side_length=2.5, color=PURPLE).to_edge(RIGHT, buff=1.5)
        tile_side = create_dimension(tile_sq.get_corner(DL), tile_sq.get_corner(DR), "?", DOWN, color=ORANGE_HL)
        tile_label = Text("P = 48 cm", font_size=20, color=PURPLE).next_to(tile_sq, UP)
        tile_group = VGroup(tile_sq, tile_side, tile_label)

        # Left: Steps
        t_steps = VGroup(
            math("P = 4s"),
            math("48 = 4s"),
            math("s = 12\\text{ cm}", color=ORANGE_HL)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.6).to_edge(LEFT, buff=1.2)

        with self.voiceover(text='For the square, perimeter is 4 times the side. 48 divided by 4 is 12.') as tracker:
            self.play(FadeIn(tile_group))
            self.play(Write(t_steps[0]))
            self.play(Write(t_steps[1]))
            self.play(t_steps[0:2].animate.set_opacity(0.3))
            self.play(Write(t_steps[2]))
            
            new_tile_side = create_dimension(tile_sq.get_corner(DL), tile_sq.get_corner(DR), "12 cm", DOWN, color=ORANGE_HL)
            self.play(ReplacementTransform(tile_side, new_tile_side))

        # Grid (Bottom Zone)
        grid = VGroup(*[Square(side_length=0.4, color=PALE_PURPLE) for _ in range(9)]).arrange_in_grid(3,3, buff=0.05)
        grid.next_to(tile_sq, DOWN, buff=0.5)
        
        with self.voiceover(text='This is how builders calculate tile sizes for flooring.') as tracker:
            self.play(FadeIn(grid))
        
        self.play(FadeOut(tile_group), FadeOut(t_steps), FadeOut(grid), FadeOut(new_tile_side), FadeOut(badge))

        # 7. SUMMARY
        badge = create_heading_badge("Summary")
        self.add(badge)
        summary = VGroup(
            Text("1. Formulas can be rearranged.", font_size=28, color=PURPLE),
            math("Rectangle: w = \\frac{P - 2l}{2}"),
            math("Square: s = \\frac{P}{4}")
        ).arrange(DOWN, buff=0.8, aligned_edge=LEFT).center()

        with self.voiceover(text='To summarize: rearrangement is a powerful tool to find missing dimensions in both rectangles and squares.') as tracker:
            self.play(FadeIn(summary, shift=UP))
            self.wait(2)
        
        self.play(FadeOut(summary), FadeOut(badge))