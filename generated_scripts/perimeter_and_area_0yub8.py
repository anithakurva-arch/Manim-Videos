import os
os.environ["OPENAI_API_KEY"] = "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"
from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.openai import OpenAIService

config.background_color = "#E7E5F3"

LAVENDER_BG = "#E7E5F3"
PURPLE = "#7464CE"
ORANGE_HL = "#FF9302"

class PerimeterAndAreaScene(VoiceoverScene):
    def construct(self):
        self.set_speech_service(
            OpenAIService(
                voice="shimmer",
                model="gpt-4o-mini-tts"
            )
        )

        # SEGMENT 1: Introduction and Hook
        with self.voiceover(
            text=r"""<bookmark mark='bk_intro'/>Hello students! Imagine you are arranging chairs... around a rectangular classroom table. <bookmark mark='bk_chairs'/>You know the total number of chairs that fit around it,... and you know how many fit along one side. <bookmark mark='bk_question'/>Could you figure out... how many fit along the other side... without counting again?"""
        ) as tracker:
            title = Text("Finding Missing Dimensions", font="Poppins", font_size=40, color=PURPLE, weight=BOLD)
            title.to_edge(UP)
            
            self.wait_until_bookmark("bk_intro")
            self.play(FadeIn(title))
            self.wait(1)
            self.play(FadeOut(title))
            
            # Create table with chairs
            table = Rectangle(width=4, height=2.5, color=PURPLE, stroke_width=4)
            
            # Chairs around the table
            chair_top = VGroup(*[Square(0.3, color=PURPLE, fill_opacity=0.5).move_to(table.get_top() + UP*0.4 + RIGHT*(i-2)*0.8) for i in range(5)])
            chair_bottom = VGroup(*[Square(0.3, color=PURPLE, fill_opacity=0.5).move_to(table.get_bottom() + DOWN*0.4 + RIGHT*(i-2)*0.8) for i in range(5)])
            chair_left = VGroup(*[Square(0.3, color=PURPLE, fill_opacity=0.5).move_to(table.get_left() + LEFT*0.4 + UP*(i-1)*0.8) for i in range(3)])
            chair_right = VGroup(*[Square(0.3, color=PURPLE, fill_opacity=0.5).move_to(table.get_right() + RIGHT*0.4 + UP*(i-1)*0.8) for i in range(3)])
            
            chairs = VGroup(chair_top, chair_bottom, chair_left, chair_right)
            table_setup = VGroup(table, chairs)
            
            self.play(FadeIn(table_setup))
            
            self.wait_until_bookmark("bk_chairs")
            # Highlight one side
            highlight_top = SurroundingRectangle(chair_top, color=ORANGE_HL, buff=0.1, stroke_width=5)
            label_known = Text("5 chairs", font="Poppins", font_size=24, color=ORANGE_HL).next_to(chair_top, UP)
            self.play(Create(highlight_top), FadeIn(label_known))
            
            self.wait_until_bookmark("bk_question")
            # Question mark on opposite side
            question = Text("?", font="Poppins", font_size=36, color=ORANGE_HL, weight=BOLD).next_to(chair_bottom, DOWN)
            self.play(FadeIn(question, scale=1.5))
            self.wait(1)
            
            self.play(FadeOut(table_setup), FadeOut(highlight_top), FadeOut(label_known), FadeOut(question))

        # SEGMENT 2: Concept Definition
        with self.voiceover(
            text=r"""<bookmark mark='bk_perimeter_def'/>The perimeter... is the total length around a shape. <bookmark mark='bk_rect_formula'/>For a rectangle,... the perimeter equals two times... the sum of length and width. <bookmark mark='bk_square_formula'/>For a square,... the perimeter equals four times... the length of one side. <bookmark mark='bk_rearrange'/>So if we know the perimeter and one dimension,... we can rearrange the formula... and find the missing one. <bookmark mark='bk_tool'/>This means perimeter is not just for measuring...— it is also a tool to work backwards."""
        ) as tracker:
            self.wait_until_bookmark("bk_perimeter_def")
            rect = Rectangle(width=4, height=2, color=PURPLE, stroke_width=4)
            self.play(Create(rect))
            
            # Trace perimeter
            dot = Dot(rect.get_corner(UL), color=ORANGE_HL)
            self.play(FadeIn(dot))
            self.play(MoveAlongPath(dot, rect), run_time=3, rate_func=linear)
            self.play(FadeOut(dot))
            
            self.wait_until_bookmark("bk_rect_formula")
            formula_rect = MathTex("P", "=", "2", "(", "l", "+", "w", ")", font_size=48, color=PURPLE)
            formula_rect.next_to(rect, DOWN, buff=0.5)
            self.play(Write(formula_rect))
            
            # Label dimensions
            length_label = MathTex("l", font_size=36, color=PURPLE).next_to(rect, RIGHT)
            width_label = MathTex("w", font_size=36, color=PURPLE).next_to(rect, UP)
            self.play(FadeIn(length_label), FadeIn(width_label))
            
            self.wait_until_bookmark("bk_square_formula")
            # Morph to square
            square = Square(2.5, color=PURPLE, stroke_width=4)
            formula_square = MathTex("P", "=", "4", "s", font_size=48, color=PURPLE)
            formula_square.next_to(square, DOWN, buff=0.5)
            side_label = MathTex("s", font_size=36, color=PURPLE).next_to(square, RIGHT)
            
            self.play(
                Transform(rect, square),
                Transform(formula_rect, formula_square),
                FadeOut(length_label),
                FadeOut(width_label)
            )
            self.play(FadeIn(side_label))
            
            self.wait_until_bookmark("bk_rearrange")
            # Show rearrangement concept
            arrow = Arrow(LEFT, RIGHT, color=ORANGE_HL).scale(0.8)
            rearrange_text = Text("Rearrange!", font="Poppins", font_size=28, color=ORANGE_HL).next_to(arrow, UP, buff=0.1)
            rearrange_group = VGroup(arrow, rearrange_text).next_to(formula_rect, DOWN, buff=0.5)
            self.play(GrowArrow(arrow), FadeIn(rearrange_text))
            
            self.wait_until_bookmark("bk_tool")
            tool_text = Text("Work Backwards!", font="Poppins", font_size=32, color=ORANGE_HL, weight=BOLD)
            tool_text.next_to(rearrange_group, DOWN, buff=0.3)
            self.play(FadeIn(tool_text, scale=1.2))
            self.wait(1)
            
            self.play(
                FadeOut(rect), FadeOut(formula_rect), FadeOut(side_label),
                FadeOut(rearrange_group), FadeOut(tool_text)
            )

        # SEGMENT 3: Why It Works
        with self.voiceover(
            text=r"""<bookmark mark='bk_why'/>Now, why does this work? <bookmark mark='bk_rect_sides'/>A rectangle has two equal lengths... and two equal widths. <bookmark mark='bk_algebra'/>So once we know the perimeter and one of them,... simple algebra gives us the other. <bookmark mark='bk_square_sides'/>A square has four equal sides,... so its side is simply... the perimeter divided by four."""
        ) as tracker:
            self.wait_until_bookmark("bk_why")
            why_title = Text("Why Does This Work?", font="Poppins", font_size=36, color=PURPLE, weight=BOLD)
            why_title.to_edge(UP)
            self.play(FadeIn(why_title))
            
            self.wait_until_bookmark("bk_rect_sides")
            rect2 = Rectangle(width=4, height=2, color=PURPLE, stroke_width=4).shift(UP*0.5)
            self.play(Create(rect2))
            
            # Label pairs
            top_label = MathTex("l", font_size=32, color=ORANGE_HL).next_to(rect2.get_top(), UP, buff=0.1)
            bottom_label = MathTex("l", font_size=32, color=ORANGE_HL).next_to(rect2.get_bottom(), DOWN, buff=0.1)
            left_label = MathTex("w", font_size=32, color=PURPLE).next_to(rect2.get_left(), LEFT, buff=0.1)
            right_label = MathTex("w", font_size=32, color=PURPLE).next_to(rect2.get_right(), RIGHT, buff=0.1)
            
            self.play(
                FadeIn(top_label), FadeIn(bottom_label),
                FadeIn(left_label), FadeIn(right_label)
            )
            
            # Show 2L + 2W
            sum_formula = MathTex("2l", "+", "2w", font_size=40, color=PURPLE).next_to(rect2, DOWN, buff=0.5)
            self.play(Write(sum_formula))
            
            self.wait_until_bookmark("bk_algebra")
            algebra_text = Text("Simple Algebra!", font="Poppins", font_size=30, color=ORANGE_HL, weight=BOLD)
            algebra_text.next_to(sum_formula, DOWN, buff=0.3)
            self.play(FadeIn(algebra_text, scale=1.2))
            
            self.wait_until_bookmark("bk_square_sides")
            # Transform to square explanation
            self.play(
                FadeOut(rect2), FadeOut(top_label), FadeOut(bottom_label),
                FadeOut(left_label), FadeOut(right_label), FadeOut(sum_formula), FadeOut(algebra_text)
            )
            
            square2 = Square(2.5, color=PURPLE, stroke_width=4)
            self.play(Create(square2))
            
            side_labels = VGroup(
                MathTex("s", font_size=32, color=ORANGE_HL).next_to(square2, UP, buff=0.1),
                MathTex("s", font_size=32, color=ORANGE_HL).next_to(square2, DOWN, buff=0.1),
                MathTex("s", font_size=32, color=ORANGE_HL).next_to(square2, LEFT, buff=0.1),
                MathTex("s", font_size=32, color=ORANGE_HL).next_to(square2, RIGHT, buff=0.1)
            )
            self.play(FadeIn(side_labels))
            
            div_formula = MathTex("s", "=", "P", "\\div", "4", font_size=40, color=PURPLE).next_to(square2, DOWN, buff=0.5)
            self.play(Write(div_formula))
            self.wait(1)
            
            self.play(
                FadeOut(why_title), FadeOut(square2), FadeOut(side_labels), FadeOut(div_formula)
            )

        # SEGMENT 4: Problem Statement
        with self.voiceover(
            text=r"""<bookmark mark='bk_problem1'/>Part 1: The perimeter of a rectangular notebook... is 34 centimeters. <bookmark mark='bk_length'/>Its length is 11 centimeters. <bookmark mark='bk_find_width'/>Find its width... and check whether two such notebooks... would fit along a 24 centimeter shelf."""
        ) as tracker:
            self.wait_until_bookmark("bk_problem1")
            problem1_title = Text("Problem 1: Notebook", font="Poppins", font_size=36, color=PURPLE, weight=BOLD)
            problem1_title.to_edge(UP)
            self.play(FadeIn(problem1_title))
            
            notebook = Rectangle(width=3, height=1.8, color=PURPLE, stroke_width=4, fill_opacity=0.1, fill_color=PURPLE)
            notebook.shift(UP*0.5)
            self.play(Create(notebook))
            
            perim_label = MathTex("P", "=", "34", "\\text{ cm}", font_size=36, color=ORANGE_HL)
            perim_label.next_to(notebook, LEFT, buff=0.5)
            self.play(Write(perim_label))
            
            self.wait_until_bookmark("bk_length")
            length_dim = MathTex("l", "=", "11", "\\text{ cm}", font_size=36, color=PURPLE)
            length_dim.next_to(notebook, DOWN, buff=0.3)
            length_brace = Brace(notebook, DOWN, color=PURPLE)
            self.play(GrowFromCenter(length_brace), Write(length_dim))
            
            self.wait_until_bookmark("bk_find_width")
            width_unknown = MathTex("w", "=", "?", font_size=36, color=ORANGE_HL)
            width_unknown.next_to(notebook, RIGHT, buff=0.5)
            width_brace = Brace(notebook, RIGHT, color=ORANGE_HL)
            self.play(GrowFromCenter(width_brace), Write(width_unknown))
            
            shelf_text = Text("Shelf = 24 cm", font="Poppins", font_size=28, color=PURPLE)
            shelf_text.next_to(length_dim, DOWN, buff=0.5)
            self.play(FadeIn(shelf_text))
            self.wait(1)
            
            self.play(
                FadeOut(problem1_title), FadeOut(notebook), FadeOut(perim_label),
                FadeOut(length_dim), FadeOut(length_brace), FadeOut(width_unknown),
                FadeOut(width_brace), FadeOut(shelf_text)
            )

        with self.voiceover(
            text=r"""<bookmark mark='bk_problem2'/>Part 2: A square tile... has a perimeter of 48 centimeters. <bookmark mark='bk_find_side'/>Find the length of one side."""
        ) as tracker:
            self.wait_until_bookmark("bk_problem2")
            problem2_title = Text("Problem 2: Tile", font="Poppins", font_size=36, color=PURPLE, weight=BOLD)
            problem2_title.to_edge(UP)
            self.play(FadeIn(problem2_title))
            
            tile = Square(2.5, color=PURPLE, stroke_width=4, fill_opacity=0.1, fill_color=PURPLE)
            self.play(Create(tile))
            
            tile_perim = MathTex("P", "=", "48", "\\text{ cm}", font_size=36, color=ORANGE_HL)
            tile_perim.next_to(tile, LEFT, buff=0.5)
            self.play(Write(tile_perim))
            
            self.wait_until_bookmark("bk_find_side")
            side_unknown = MathTex("s", "=", "?", font_size=36, color=ORANGE_HL)
            side_unknown.next_to(tile, RIGHT, buff=0.5)
            self.play(Write(side_unknown))
            self.wait(1)
            
            self.play(
                FadeOut(problem2_title), FadeOut(tile), FadeOut(tile_perim), FadeOut(side_unknown)
            )

        # SEGMENT 5: Solution Part 1
        with self.voiceover(
            text=r"""<bookmark mark='bk_solution1'/>For the notebook: Two times the sum of length and width... equals the perimeter. <bookmark mark='bk_eq1'/>Two times... eleven plus width... equals thirty-four. <bookmark mark='bk_eq2'/>Eleven plus width... equals seventeen. <bookmark mark='bk_width_answer'/>So width equals six centimeters. <bookmark mark='bk_shelf'/>Two notebooks placed side by side... would need twelve centimeters,... which fits well on the shelf."""
        ) as tracker:
            self.wait_until_bookmark("bk_solution1")
            sol1_title = Text("Solution 1", font="Poppins", font_size=36, color=PURPLE, weight=BOLD)
            sol1_title.to_edge(UP)
            self.play(FadeIn(sol1_title))
            
            eq1 = MathTex("2", "(", "l", "+", "w", ")", "=", "P", font_size=40, color=PURPLE)
            eq1.shift(UP*1.5)
            self.play(Write(eq1))
            
            self.wait_until_bookmark("bk_eq1")
            eq2 = MathTex("2", "(", "11", "+", "w", ")", "=", "34", font_size=40, color=PURPLE)
            eq2.next_to(eq1, DOWN, buff=0.4)
            self.play(TransformFromCopy(eq1, eq2))
            
            self.wait_until_bookmark("bk_eq2")
            eq3 = MathTex("11", "+", "w", "=", "17", font_size=40, color=PURPLE)
            eq3.next_to(eq2, DOWN, buff=0.4)
            self.play(TransformFromCopy(eq2, eq3))
            
            self.wait_until_bookmark("bk_width_answer")
            eq4 = MathTex("w", "=", "6", "\\text{ cm}", font_size=44, color=ORANGE_HL, weight=BOLD)
            eq4.next_to(eq3, DOWN, buff=0.4)
            self.play(Write(eq4))
            box_answer = SurroundingRectangle(eq4, color=ORANGE_HL, buff=0.15)
            self.play(Create(box_answer))
            
            self.wait_until_bookmark("bk_shelf")
            # Shelf visualization
            self.play(FadeOut(eq1), FadeOut(eq2), FadeOut(eq3), FadeOut(eq4), FadeOut(box_answer))
            
            shelf = Line(LEFT*4, RIGHT*4, color=PURPLE, stroke_width=6).shift(DOWN*1)
            shelf_label = Text("Shelf: 24 cm", font="Poppins", font_size=28, color=PURPLE).next_to(shelf, DOWN, buff=0.2)
            self.play(Create(shelf), FadeIn(shelf_label))
            
            notebook1 = Rectangle(width=1.5, height=1, color=ORANGE_HL, stroke_width=4, fill_opacity=0.3, fill_color=ORANGE_HL)
            notebook1.next_to(shelf, UP, buff=0.1).shift(LEFT*1.5)
            nb1_label = Text("6 cm", font="Poppins", font_size=20, color=WHITE).move_to(notebook1)
            
            notebook2 = Rectangle(width=1.5, height=1, color=ORANGE_HL, stroke_width=4, fill_opacity=0.3, fill_color=ORANGE_HL)
            notebook2.next_to(notebook1, RIGHT, buff=0)
            nb2_label = Text("6 cm", font="Poppins", font_size=20, color=WHITE).move_to(notebook2)
            
            self.play(FadeIn(notebook1), FadeIn(nb1_label))
            self.play(FadeIn(notebook2), FadeIn(nb2_label))
            
            total_brace = Brace(VGroup(notebook1, notebook2), UP, color=PURPLE)
            total_label = MathTex("12", "\\text{ cm}", font_size=32, color=PURPLE).next_to(total_brace, UP)
            self.play(GrowFromCenter(total_brace), FadeIn(total_label))
            
            checkmark = Text("✓ Fits!", font="Poppins", font_size=32, color="#00FF00", weight=BOLD)
            checkmark.next_to(shelf_label, DOWN, buff=0.3)
            self.play(FadeIn(checkmark, scale=1.5))
            self.wait(1)
            
            self.play(
                FadeOut(sol1_title), FadeOut(shelf), FadeOut(shelf_label),
                FadeOut(notebook1), FadeOut(nb1_label), FadeOut(notebook2), FadeOut(nb2_label),
                FadeOut(total_brace), FadeOut(total_label), FadeOut(checkmark)
            )

        # SEGMENT 6: Solution Part 2
        with self.voiceover(
            text=r"""<bookmark mark='bk_solution2'/>For the tile: The perimeter equals four times the side. <bookmark mark='bk_tile_eq'/>Four times the side... equals forty-eight. <bookmark mark='bk_side_answer'/>So the side equals twelve centimeters. <bookmark mark='bk_builders'/>This is the same idea builders use... when calculating tile sizes for a floor."""
        ) as tracker:
            self.wait_until_bookmark("bk_solution2")
            sol2_title = Text("Solution 2", font="Poppins", font_size=36, color=PURPLE, weight=BOLD)
            sol2_title.to_edge(UP)
            self.play(FadeIn(sol2_title))
            
            tile_eq1 = MathTex("P", "=", "4", "s", font_size=40, color=PURPLE)
            tile_eq1.shift(UP*1)
            self.play(Write(tile_eq1))
            
            self.wait_until_bookmark("bk_tile_eq")
            tile_eq2 = MathTex("4", "s", "=", "48", font_size=40, color=PURPLE)
            tile_eq2.next_to(tile_eq1, DOWN, buff=0.4)
            self.play(TransformFromCopy(tile_eq1, tile_eq2))
            
            self.wait_until_bookmark("bk_side_answer")
            tile_eq3 = MathTex("s", "=", "12", "\\text{ cm}", font_size=44, color=ORANGE_HL, weight=BOLD)
            tile_eq3.next_to(tile_eq2, DOWN, buff=0.4)
            self.play(Write(tile_eq3))
            box_answer2 = SurroundingRectangle(tile_eq3, color=ORANGE_HL, buff=0.15)
            self.play(Create(box_answer2))
            
            self.wait_until_bookmark("bk_builders")
            # Floor visualization
            self.play(FadeOut(tile_eq1), FadeOut(tile_eq2), FadeOut(tile_eq3), FadeOut(box_answer2))
            
            floor_tile = Square(1.5, color=PURPLE, stroke_width=4, fill_opacity=0.3, fill_color=PURPLE)
            floor_tile.shift(UP*0.5)
            tile_label = Text("12 cm", font="Poppins", font_size=24, color=WHITE).move_to(floor_tile)
            
            # Grid of tiles
            tile_grid = VGroup(
                floor_tile.copy().shift(LEFT*1.5 + UP*1.5),
                floor_tile.copy().shift(UP*1.5),
                floor_tile.copy().shift(RIGHT*1.5 + UP*1.5),
                floor_tile.copy().shift(LEFT*1.5),
                floor_tile.copy(),
                floor_tile.copy().shift(RIGHT*1.5)
            )
            
            self.play(FadeIn(tile_grid, lag_ratio=0.1))
            
            builder_text = Text("Builder's Tool!", font="Poppins", font_size=30, color=ORANGE_HL, weight=BOLD)
            builder_text.next_to(tile_grid, DOWN, buff=0.5)
            self.play(FadeIn(builder_text, scale=1.2))
            self.wait(1)
            
            self.play(FadeOut(sol2_title), FadeOut(tile_grid), FadeOut(builder_text))

        # SEGMENT 7: Summary
        with self.voiceover(
            text=r"""<bookmark mark='bk_summary'/>Summary: Perimeter formulas can be rearranged... to find missing dimensions. <bookmark mark='bk_rect_sum'/>Rectangle: perimeter is two times... the sum of length and width. <bookmark mark='bk_square_sum'/>Square: side is the perimeter... divided by four."""
        ) as tracker:
            self.wait_until_bookmark("bk_summary")
            summary_title = Text("Summary", font="Poppins", font_size=40, color=PURPLE, weight=BOLD)
            summary_title.to_edge(UP)
            self.play(FadeIn(summary_title))
            
            bullet1 = Text("• Rearrange formulas to find missing dimensions", font="Poppins", font_size=28, color=PURPLE)
            bullet1.shift(UP*1)
            self.play(FadeIn(bullet1, shift=RIGHT))
            
            self.wait_until_bookmark("bk_rect_sum")
            bullet2_text = Text("• Rectangle: ", font="Poppins", font_size=28, color=PURPLE)
            bullet2_formula = MathTex("P = 2(l + w)", font_size=32, color=PURPLE)
            bullet2 = VGroup(bullet2_text, bullet2_formula).arrange(RIGHT, buff=0.2)
            bullet2.next_to(bullet1, DOWN, buff=0.4, aligned_edge=LEFT)
            self.play(FadeIn(bullet2, shift=RIGHT))
            
            self.wait_until_bookmark("bk_square_sum")
            bullet3_text = Text("• Square: ", font="Poppins", font_size=28, color=PURPLE)
            bullet3_formula = MathTex("s = P \\div 4", font_size=32, color=PURPLE)
            bullet3 = VGroup(bullet3_text, bullet3_formula).arrange(RIGHT, buff=0.2)
            bullet3.next_to(bullet2, DOWN, buff=0.4, aligned_edge=LEFT)
            self.play(FadeIn(bullet3, shift=RIGHT))
            
            self.wait(2)
            self.play(FadeOut(VGroup(summary_title, bullet1, bullet2, bullet3)))