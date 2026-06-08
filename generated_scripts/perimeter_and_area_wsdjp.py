import os
os.environ["OPENAI_API_KEY"] = "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"

from manim import *
import math

config.background_color = "#E7E5F3"
LAVENDER_BG = "#E7E5F3"
PURPLE = "#7464CE"
ORANGE = "#FF9302"

class PerimeterAndAreaScene(Scene):
    def construct(self):
        self.camera.background_color = LAVENDER_BG
        
        # Audio setup
        audio_script = """<bookmark mark='intro_start'/>Hello students! Imagine you are arranging chairs around a rectangular classroom table.<break time='0.4s'/> You know the total number of chairs that fit around it, and you know how many fit along one side.<break time='0.4s'/> Could you figure out how many fit along the other side without counting again?<break time='0.6s'/><bookmark mark='concept_start'/> The perimeter is the total length around a shape.<break time='0.4s'/> For a rectangle, the perimeter equals two times the sum of length and width.<break time='0.4s'/> For a square, the perimeter equals four times the length of one side.<break time='0.4s'/> So if we know the perimeter and one dimension, we can rearrange the formula and find the missing one.<break time='0.4s'/> This means perimeter is not just for measuring, it is also a tool to work backwards.<break time='0.6s'/><bookmark mark='reasoning_start'/> Now, why does this work?<break time='0.3s'/> A rectangle has two equal lengths and two equal widths.<break time='0.4s'/> So once we know the perimeter and one of them, simple algebra gives us the other.<break time='0.4s'/> A square has four equal sides, so its side is simply the perimeter divided by four.<break time='0.6s'/><bookmark mark='problem_start'/> Question: Part 1: The perimeter of a rectangular notebook is 34 centimeters.<break time='0.3s'/> Its length is 11 centimeters.<break time='0.3s'/> Find its width and check whether two such notebooks would fit along a 24 centimeter shelf.<break time='0.5s'/> Part 2: A square tile has a perimeter of 48 centimeters.<break time='0.3s'/> Find the length of one side.<break time='0.6s'/><bookmark mark='solution1_start'/> Solution: For the notebook:<break time='0.3s'/> Two times the sum of length and width equals the perimeter.<break time='0.3s'/> Two times, eleven plus width, equals thirty four.<break time='0.3s'/> Eleven plus width equals seventeen.<break time='0.3s'/> So width equals six centimeters.<break time='0.4s'/> Two notebooks placed side by side would need twelve centimeters, which fits well on the shelf.<break time='0.6s'/><bookmark mark='solution2_start'/> For the tile:<break time='0.3s'/> The perimeter equals four times the side.<break time='0.3s'/> Four times the side equals forty eight.<break time='0.3s'/> So the side equals twelve centimeters.<break time='0.4s'/> This is the same idea builders use when calculating tile sizes for a floor.<break time='0.6s'/><bookmark mark='summary_start'/> Summary: Perimeter formulas can be rearranged to find missing dimensions.<break time='0.4s'/> Rectangle: perimeter is two times the sum of length and width.<break time='0.4s'/> Square: side is the perimeter divided by four."""
        
        # SEGMENT 1: INTRODUCTION (0:00-0:12)
        table = Rectangle(width=4, height=2.5, stroke_color=PURPLE, stroke_width=4, fill_opacity=0)
        
        # Create chairs around table
        chair_size = 0.3
        chairs = VGroup()
        # Top side - 5 chairs
        for i in range(5):
            chair = Square(side_length=chair_size, fill_color=PURPLE, fill_opacity=0.7, stroke_width=2)
            chair.move_to(table.get_top() + UP*0.4 + RIGHT*(i-2)*0.9)
            chairs.add(chair)
        # Bottom side - 5 chairs
        for i in range(5):
            chair = Square(side_length=chair_size, fill_color=PURPLE, fill_opacity=0.7, stroke_width=2)
            chair.move_to(table.get_bottom() + DOWN*0.4 + RIGHT*(i-2)*0.9)
            chairs.add(chair)
        # Left side - 3 chairs
        for i in range(3):
            chair = Square(side_length=chair_size, fill_color=PURPLE, fill_opacity=0.7, stroke_width=2)
            chair.move_to(table.get_left() + LEFT*0.4 + UP*(i-1)*0.9)
            chairs.add(chair)
        # Right side - 3 chairs (unknown)
        for i in range(3):
            chair = Square(side_length=chair_size, fill_color=PURPLE, fill_opacity=0.3, stroke_width=2, stroke_color=PURPLE)
            chair.move_to(table.get_right() + RIGHT*0.4 + UP*(i-1)*0.9)
            chairs.add(chair)
        
        intro_group = VGroup(table, chairs).scale(0.7)
        
        # Label one side
        left_label = Text("5 chairs", font_size=24, color=ORANGE).next_to(table.get_left(), LEFT, buff=0.6)
        right_label = Text("?", font_size=36, color=PURPLE).next_to(table.get_right(), RIGHT, buff=0.6)
        
        self.play(FadeIn(table))
        self.wait(0.5)
        self.play(LaggedStart(*[FadeIn(chair) for chair in chairs[:13]], lag_ratio=0.05))
        self.play(Write(left_label))
        self.wait(0.5)
        self.play(LaggedStart(*[FadeIn(chair) for chair in chairs[13:]], lag_ratio=0.1))
        self.play(Write(right_label))
        self.wait(1)
        
        self.play(FadeOut(intro_group), FadeOut(left_label), FadeOut(right_label))
        
        # SEGMENT 2: CONCEPT (0:12-0:30)
        rect = Rectangle(width=3.5, height=2, stroke_color=PURPLE, stroke_width=4, fill_opacity=0)
        rect.shift(UP*1.5)
        
        # Trace perimeter
        trace_line = rect.copy().set_stroke(ORANGE, width=6)
        
        self.play(Create(rect))
        self.play(Create(trace_line), run_time=2, rate_func=linear)
        self.wait(0.3)
        
        # Rectangle formula
        rect_formula = MathTex("P", "=", "2", "(", "l", "+", "w", ")", color=PURPLE, font_size=42)
        rect_formula.next_to(rect, DOWN, buff=0.5)
        
        self.play(Write(rect_formula))
        self.wait(0.5)
        
        # Square
        square = Square(side_length=2, stroke_color=PURPLE, stroke_width=4, fill_opacity=0)
        square.next_to(rect_formula, DOWN, buff=1)
        
        trace_square = square.copy().set_stroke(ORANGE, width=6)
        
        self.play(Create(square))
        self.play(Create(trace_square), run_time=2, rate_func=linear)
        self.wait(0.3)
        
        # Square formula
        square_formula = MathTex("P", "=", "4", "s", color=PURPLE, font_size=42)
        square_formula.next_to(square, DOWN, buff=0.3)
        
        self.play(Write(square_formula))
        self.wait(0.5)
        
        # Rearrangement concept
        arrow = Arrow(rect_formula.get_right(), rect_formula.get_right() + RIGHT*1.5, color=ORANGE, stroke_width=4)
        rearrange_text = Text("Solve for\nunknown", font_size=24, color=PURPLE).next_to(arrow, RIGHT, buff=0.2)
        
        self.play(GrowArrow(arrow), FadeIn(rearrange_text))
        self.wait(1.5)
        
        self.play(FadeOut(VGroup(rect, trace_line, rect_formula, square, trace_square, square_formula, arrow, rearrange_text)))
        
        # SEGMENT 3: REASONING (0:30-0:48)
        reasoning_rect = Rectangle(width=4, height=2.5, stroke_color=PURPLE, stroke_width=4, fill_opacity=0)
        
        # Labels for sides
        l1 = MathTex("l", color=ORANGE, font_size=36).next_to(reasoning_rect.get_top(), UP, buff=0.2)
        l2 = MathTex("l", color=ORANGE, font_size=36).next_to(reasoning_rect.get_bottom(), DOWN, buff=0.2)
        w1 = MathTex("w", color=PURPLE, font_size=36).next_to(reasoning_rect.get_left(), LEFT, buff=0.2)
        w2 = MathTex("w", color=PURPLE, font_size=36).next_to(reasoning_rect.get_right(), RIGHT, buff=0.2)
        
        self.play(Create(reasoning_rect))
        self.play(Write(l1), Write(l2))
        self.wait(0.5)
        
        # Pulse equal lengths
        self.play(
            reasoning_rect.get_top().animate.set_stroke(ORANGE, width=8),
            reasoning_rect.get_bottom().animate.set_stroke(ORANGE, width=8),
            rate_func=there_and_back,
            run_time=1
        )
        self.wait(0.5)
        
        self.play(Write(w1), Write(w2))
        self.wait(0.5)
        
        # Show formula transformation
        transform_formula1 = MathTex("P", "=", "2", "(", "l", "+", "w", ")", color=PURPLE, font_size=36)
        transform_formula1.next_to(reasoning_rect, DOWN, buff=0.8)
        
        self.play(Write(transform_formula1))
        self.wait(0.5)
        
        transform_formula2 = MathTex("w", "=", "{P - 2l", "\\over", "2}", color=PURPLE, font_size=36)
        transform_formula2.move_to(transform_formula1.get_center())
        
        self.play(Transform(transform_formula1, transform_formula2))
        self.wait(1)
        
        self.play(FadeOut(VGroup(reasoning_rect, l1, l2, w1, w2, transform_formula1)))
        
        # Square reasoning
        reasoning_square = Square(side_length=2.5, stroke_color=PURPLE, stroke_width=4, fill_opacity=0)
        
        s_labels = VGroup(
            MathTex("s", color=PURPLE, font_size=32).next_to(reasoning_square.get_top(), UP, buff=0.15),
            MathTex("s", color=PURPLE, font_size=32).next_to(reasoning_square.get_right(), RIGHT, buff=0.15),
            MathTex("s", color=PURPLE, font_size=32).next_to(reasoning_square.get_bottom(), DOWN, buff=0.15),
            MathTex("s", color=PURPLE, font_size=32).next_to(reasoning_square.get_left(), LEFT, buff=0.15)
        )
        
        self.play(Create(reasoning_square))
        self.play(Write(s_labels))
        self.wait(0.5)
        
        # Pulse all sides
        for _ in range(2):
            self.play(
                reasoning_square.animate.set_stroke(ORANGE, width=8),
                rate_func=there_and_back,
                run_time=0.6
            )
        
        square_transform1 = MathTex("P", "=", "4", "s", color=PURPLE, font_size=36)
        square_transform1.next_to(reasoning_square, DOWN, buff=0.6)
        
        self.play(Write(square_transform1))
        self.wait(0.3)
        
        square_transform2 = MathTex("s", "=", "{P", "\\over", "4}", color=PURPLE, font_size=36)
        square_transform2.move_to(square_transform1.get_center())
        
        self.play(Transform(square_transform1, square_transform2))
        self.wait(1)
        
        self.play(FadeOut(VGroup(reasoning_square, s_labels, square_transform1)))
        
        # SEGMENT 4: PROBLEM (0:48-1:04)
        problem_title = Text("Question:", font_size=36, color=PURPLE, weight=BOLD).to_edge(UP, buff=0.3)
        self.play(Write(problem_title))
        
        # Part 1: Notebook
        notebook = Rectangle(width=2.2, height=1.4, stroke_color=PURPLE, stroke_width=4, fill_opacity=0)
        notebook.shift(UP*0.8 + LEFT*2)
        
        p_label = MathTex("P = 34", "\\text{ cm}", color=PURPLE, font_size=28).next_to(notebook, UP, buff=0.3)
        l_label = MathTex("l = 11", "\\text{ cm}", color=ORANGE, font_size=28).next_to(notebook.get_top(), DOWN, buff=0.1)
        w_label = MathTex("w = ?", color=PURPLE, font_size=28).next_to(notebook.get_left(), RIGHT, buff=0.1)
        
        self.play(Create(notebook))
        self.play(Write(p_label))
        self.wait(0.3)
        self.play(Write(l_label))
        self.wait(0.3)
        self.play(Write(w_label))
        self.wait(0.5)
        
        # Shelf
        shelf = Line(LEFT*3, RIGHT*3, color=PURPLE, stroke_width=6)
        shelf.shift(DOWN*1.5)
        shelf_label = MathTex("24", "\\text{ cm}", color=PURPLE, font_size=28).next_to(shelf, DOWN, buff=0.2)
        
        self.play(Create(shelf), Write(shelf_label))
        self.wait(0.8)
        
        # Part 2: Tile
        tile = Square(side_length=1.8, stroke_color=PURPLE, stroke_width=4, fill_opacity=0)
        tile.shift(UP*0.8 + RIGHT*3)
        
        tile_p_label = MathTex("P = 48", "\\text{ cm}", color=PURPLE, font_size=28).next_to(tile, UP, buff=0.3)
        tile_s_label = MathTex("s = ?", color=PURPLE, font_size=28).next_to(tile.get_top(), DOWN, buff=0.3)
        
        self.play(Create(tile))
        self.play(Write(tile_p_label))
        self.wait(0.3)
        self.play(Write(tile_s_label))
        self.wait(1)
        
        self.play(FadeOut(VGroup(problem_title, notebook, p_label, l_label, w_label, shelf, shelf_label, tile, tile_p_label, tile_s_label)))
        
        # SEGMENT 5: SOLUTION PART 1 (1:04-1:25)
        solution_title = Text("Solution: Notebook", font_size=32, color=PURPLE, weight=BOLD).to_edge(UP, buff=0.3)
        self.play(Write(solution_title))
        
        # Equation sequence
        eq1 = MathTex("2", "(", "l", "+", "w", ")", "=", "P", color=PURPLE, font_size=38)
        eq1.shift(UP*1.5)
        self.play(Write(eq1))
        self.wait(0.4)
        
        eq2 = MathTex("2", "(", "11", "+", "w", ")", "=", "34", color=PURPLE, font_size=38)
        eq2[2].set_color(ORANGE)
        eq2[7].set_color(ORANGE)
        eq2.move_to(eq1.get_center())
        self.play(TransformMatchingTex(eq1, eq2))
        self.wait(0.4)
        
        eq3 = MathTex("11", "+", "w", "=", "17", color=PURPLE, font_size=38)
        eq3[0].set_color(ORANGE)
        eq3[4].set_color(ORANGE)
        eq3.next_to(eq2, DOWN, buff=0.5)
        self.play(Write(eq3))
        self.wait(0.4)
        
        eq4 = MathTex("w", "=", "6", "\\text{ cm}", color=PURPLE, font_size=38)
        eq4[2].set_color(ORANGE)
        eq4.next_to(eq3, DOWN, buff=0.5)
        self.play(Write(eq4))
        self.wait(0.5)
        
        # Show notebook with dimensions
        solved_notebook = Rectangle(width=2.2, height=1.2, stroke_color=PURPLE, stroke_width=4, fill_opacity=0.1, fill_color=PURPLE)
        solved_notebook.shift(DOWN*1.5 + LEFT*1.5)
        solved_l = MathTex("11", color=ORANGE, font_size=28).next_to(solved_notebook.get_top(), UP, buff=0.15)
        solved_w = MathTex("6", color=ORANGE, font_size=28).next_to(solved_notebook.get_left(), LEFT, buff=0.15)
        
        self.play(Create(solved_notebook), Write(solved_l), Write(solved_w))
        self.wait(0.5)
        
        # Two notebooks on shelf
        notebook2 = solved_notebook.copy().shift(RIGHT*1.4)
        shelf2 = Line(LEFT*3.5, RIGHT*3.5, color=PURPLE, stroke_width=6).shift(DOWN*2.2)
        
        brace1 = Brace(VGroup(solved_notebook, notebook2), DOWN, color=ORANGE)
        brace_label = MathTex("12", "\\text{ cm}", color=ORANGE, font_size=28).next_to(brace1, DOWN, buff=0.1)
        
        shelf_brace = Brace(shelf2, DOWN, color=PURPLE)
        shelf_brace_label = MathTex("24", "\\text{ cm}", color=PURPLE, font_size=28).next_to(shelf_brace, DOWN, buff=0.1)
        
        self.play(Create(notebook2))
        self.play(Create(shelf2))
        self.play(GrowFromCenter(brace1), Write(brace_label))
        self.play(GrowFromCenter(shelf_brace), Write(shelf_brace_label))
        
        checkmark = Text("✓ Fits!", font_size=32, color=ORANGE, weight=BOLD).next_to(shelf2, RIGHT, buff=0.8)
        self.play(Write(checkmark))
        self.wait(1.5)
        
        self.play(FadeOut(VGroup(solution_title, eq2, eq3, eq4, solved_notebook, solved_l, solved_w, notebook2, shelf2, brace1, brace_label, shelf_brace, shelf_brace_label, checkmark)))
        
        # SEGMENT 6: SOLUTION PART 2 (1:25-1:40)
        solution_title2 = Text("Solution: Tile", font_size=32, color=PURPLE, weight=BOLD).to_edge(UP, buff=0.3)
        self.play(Write(solution_title2))
        
        # Equation sequence for tile
        tile_eq1 = MathTex("P", "=", "4", "s", color=PURPLE, font_size=38)
        tile_eq1.shift(UP*1.2)
        self.play(Write(tile_eq1))
        self.wait(0.4)
        
        tile_eq2 = MathTex("4", "s", "=", "48", color=PURPLE, font_size=38)
        tile_eq2[3].set_color(ORANGE)
        tile_eq2.move_to(tile_eq1.get_center())
        self.play(TransformMatchingTex(tile_eq1, tile_eq2))
        self.wait(0.4)
        
        tile_eq3 = MathTex("s", "=", "12", "\\text{ cm}", color=PURPLE, font_size=38)
        tile_eq3[2].set_color(ORANGE)
        tile_eq3.next_to(tile_eq2, DOWN, buff=0.5)
        self.play(Write(tile_eq3))
        self.wait(0.5)
        
        # Show solved tile
        solved_tile = Square(side_length=1.8, stroke_color=PURPLE, stroke_width=4, fill_opacity=0.1, fill_color=PURPLE)
        solved_tile.shift(DOWN*0.5)
        tile_side_label = MathTex("12", "\\text{ cm}", color=ORANGE, font_size=28).next_to(solved_tile.get_top(), UP, buff=0.15)
        
        self.play(Create(solved_tile), Write(tile_side_label))
        self.wait(0.5)
        
        # Builder application - floor with tiles
        floor_grid = VGroup()
        for i in range(3):
            for j in range(3):
                small_tile = Square(side_length=0.5, stroke_color=PURPLE, stroke_width=2, fill_opacity=0.15, fill_color=PURPLE)
                small_tile.move_to(DOWN*2 + LEFT*0.8 + RIGHT*i*0.55 + UP*j*0.55)
                floor_grid.add(small_tile)
        
        builder = SVGMobject("assets/builder.svg").scale(0.4) if os.path.exists("assets/builder.svg") else Text("Builder", font_size=20, color=PURPLE)
        builder.next_to(floor_grid, RIGHT, buff=0.3)
        
        self.play(LaggedStart(*[FadeIn(tile) for tile in floor_grid], lag_ratio=0.05))
        self.play(FadeIn(builder))
        self.wait(1.5)
        
        self.play(FadeOut(VGroup(solution_title2, tile_eq2, tile_eq3, solved_tile, tile_side_label, floor_grid, builder)))
        
        # SEGMENT 7: SUMMARY (1:40-1:55)
        summary_title = Text("Summary", font_size=40, color=PURPLE, weight=BOLD).to_edge(UP, buff=0.4)
        self.play(Write(summary_title))
        self.wait(0.3)
        
        # Three bullet points
        bullet1_icon = Text("⟲", font_size=40, color=ORANGE).shift(UP*1 + LEFT*5)
        bullet1_text = Text("Perimeter formulas can be\nrearranged to find missing dimensions", font_size=24, color=PURPLE, line_spacing=1.2)
        bullet1_text.next_to(bullet1_icon, RIGHT, buff=0.3, aligned_edge=UP)
        
        self.play(FadeIn(bullet1_icon), Write(bullet1_text))
        self.wait(0.5)
        
        bullet2_rect = Rectangle(width=1, height=0.6, stroke_color=PURPLE, stroke_width=3, fill_opacity=0).shift(DOWN*0.2 + LEFT*5.5)
        bullet2_formula = MathTex("P = 2(l+w)", color=PURPLE, font_size=28).next_to(bullet2_rect, RIGHT, buff=0.3)
        bullet2_text = Text("Rectangle", font_size=24, color=PURPLE).next_to(bullet2_formula, RIGHT, buff=0.3)
        
        self.play(Create(bullet2_rect), Write(bullet2_formula), Write(bullet2_text))
        self.wait(0.5)
        
        bullet3_square = Square(side_length=0.6, stroke_color=PURPLE, stroke_width=3, fill_opacity=0).shift(DOWN*1.4 + LEFT*5.5)
        bullet3_formula = MathTex("s = {P \\over 4}", color=PURPLE, font_size=28).next_to(bullet3_square, RIGHT, buff=0.3)
        bullet3_text = Text("Square", font_size=24, color=PURPLE).next_to(bullet3_formula, RIGHT, buff=0.3)
        
        self.play(Create(bullet3_square), Write(bullet3_formula), Write(bullet3_text))
        self.wait(2)
        
        self.play(FadeOut(VGroup(summary_title, bullet1_icon, bullet1_text, bullet2_rect, bullet2_formula, bullet2_text, bullet3_square, bullet3_formula, bullet3_text)))
        
        self.wait(0.5)