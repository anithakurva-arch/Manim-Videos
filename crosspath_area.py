from manim import *
from manim_fonts import RegisterFont

class CrossPathArea(Scene):
    def construct(self):
        with RegisterFont("Poppins") as fonts:
            FONT = fonts[0]

            # Colors
            garden_fill = "#CFECC7"
            garden_stroke = "#2E7D32"
            path_fill = "#D9D2C3"
            overlap_fill = "#B8B0A3"
            length_color = "#1565C0"
            width_color = "#2E7D32"
            area_color = "#F9A825"
            path_width_color = "#8E24AA"

            # Title
            title = Text(
                "Area of the Cross Path",
                font=FONT,
                font_size=40,
                weight=BOLD,
            ).to_edge(UP)

            self.play(Write(title))

            # Garden rectangle
            garden = Rectangle(
                width=8,
                height=6,
                stroke_color=garden_stroke,
                stroke_width=4
            )
            garden.set_fill(garden_fill, opacity=1)
            garden.shift(LEFT * 3)

            garden_label = Text(
                "Garden",
                font=FONT,
                font_size=28,
                weight=BOLD,
                color=BLACK
            ).move_to(garden.get_center())

            self.play(Create(garden), FadeIn(garden_label))
            self.wait(0.4)

            # Braces and dimension labels
            top_brace = Brace(garden, UP)
            top_text = Text(
                "20 m",
                font=FONT,
                font_size=24,
                color=length_color
            ).next_to(top_brace, UP, buff=0.1)

            left_brace = Brace(garden, LEFT)
            left_text = Text(
                "15 m",
                font=FONT,
                font_size=24,
                color=width_color
            ).next_to(left_brace, LEFT, buff=0.1)

            self.play(GrowFromCenter(top_brace), FadeIn(top_text))
            self.play(GrowFromCenter(left_brace), FadeIn(left_text))
            self.wait(0.4)

            # Paths
            vertical_path = Rectangle(width=0.8, height=6, stroke_width=0)
            vertical_path.set_fill(path_fill, opacity=0.95)
            vertical_path.move_to(garden.get_center())

            horizontal_path = Rectangle(width=8, height=0.8, stroke_width=0)
            horizontal_path.set_fill(path_fill, opacity=0.95)
            horizontal_path.move_to(garden.get_center())

            overlap = Square(side_length=0.8, stroke_width=0)
            overlap.set_fill(overlap_fill, opacity=1)
            overlap.move_to(garden.get_center())

            self.play(FadeIn(vertical_path), run_time=1.0)
            self.play(FadeIn(horizontal_path), run_time=1.0)
            self.play(FadeIn(overlap), run_time=0.4)
            self.wait(0.4)

            # Width labels on paths
            v_width = Text(
                "2 m",
                font=FONT,
                font_size=22,
                color=path_width_color
            ).next_to(vertical_path, RIGHT, buff=0.12)

            h_width = Text(
                "2 m",
                font=FONT,
                font_size=22,
                color=path_width_color
            ).next_to(horizontal_path, DOWN, buff=0.1)

            self.play(FadeIn(v_width), FadeIn(h_width))
            self.wait(0.4)

            # Right-side explanation labels
            path_label_1 = Text(
                "Path parallel to length",
                font=FONT,
                font_size=24,
                color=WHITE
            ).next_to(garden, RIGHT, buff=1.0).shift(UP * 1.9)

            eq1 = MathTex(
                r"\text{Area} = 20 \times 2 = 40\text{ m}^2",
                color=WHITE
            ).scale(0.78).next_to(path_label_1, DOWN, aligned_edge=LEFT, buff=0.2)
            eq1.set_color_by_tex("20", length_color)
            eq1.set_color_by_tex("2", path_width_color)
            eq1.set_color_by_tex("40", area_color)

            path_label_2 = Text(
                "Path parallel to width",
                font=FONT,
                font_size=24,
                color=WHITE
            ).next_to(eq1, DOWN, aligned_edge=LEFT, buff=0.5)

            eq2 = MathTex(
                r"\text{Area} = 15 \times 2 = 30\text{ m}^2",
                color=WHITE
            ).scale(0.78).next_to(path_label_2, DOWN, aligned_edge=LEFT, buff=0.2)
            eq2.set_color_by_tex("15", width_color)
            eq2.set_color_by_tex("2", path_width_color)
            eq2.set_color_by_tex("30", area_color)

            overlap_label = Text(
                "Overlap square",
                font=FONT,
                font_size=24,
                color=WHITE
            ).next_to(eq2, DOWN, aligned_edge=LEFT, buff=0.5)

            eq3 = MathTex(
                r"\text{Area} = 2 \times 2 = 4\text{ m}^2",
                color=WHITE
            ).scale(0.78).next_to(overlap_label, DOWN, aligned_edge=LEFT, buff=0.2)
            eq3.set_color_by_tex("2", path_width_color)
            eq3.set_color_by_tex("4", area_color)

            eq4 = MathTex(
                r"\text{Crosspath area} = 40 + 30 - 4 = 66\text{ m}^2",
                color=WHITE
            ).scale(0.84).next_to(eq3, DOWN, aligned_edge=LEFT, buff=0.7)
            eq4.set_color_by_tex("40", area_color)
            eq4.set_color_by_tex("30", area_color)
            eq4.set_color_by_tex("4", RED_C)
            eq4.set_color_by_tex("66", YELLOW)

            final_box = SurroundingRectangle(eq4, color=YELLOW, buff=0.22, stroke_width=3)

            final_text = Text(
                "Crosspath covers 66 m²",
                font=FONT,
                font_size=30,
                weight=BOLD,
                color=YELLOW
            ).next_to(final_box, DOWN, buff=0.25)

            # Animations for explanation
            self.play(Write(path_label_1))
            self.play(Indicate(vertical_path, color=length_color), Write(eq1))
            self.wait(0.3)

            self.play(Write(path_label_2))
            self.play(Indicate(horizontal_path, color=width_color), Write(eq2))
            self.wait(0.3)

            self.play(Write(overlap_label))
            self.play(Indicate(overlap, color=YELLOW), Write(eq3))
            self.wait(0.5)

            self.play(Write(eq4))
            self.play(Create(final_box), FadeIn(final_text))
            self.wait(2)