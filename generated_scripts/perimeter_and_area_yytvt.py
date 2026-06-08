import os
os.environ["OPENAI_API_KEY"] = "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"
from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.openai import OpenAIService

config.background_color = "#E7E5F3"
PURPLE = "#7464CE"
ORANGE_HL = "#FF9302"
LAVENDER_BG = "#E7E5F3"

class PerimeterAndAreaScene(VoiceoverScene):
    def construct(self):
        self.set_speech_service(
            OpenAIService(
                voice="shimmer",
                model="gpt-4o-mini-tts"
            )
        )
        
        # Scene 1: Title and Introduction
        with self.voiceover(text=r"""<bookmark mark='bk_intro'/>Hello students! Imagine you are arranging chairs around a rectangular classroom table. <bookmark mark='bk_chairs'/>You know the total number of chairs that fit around it, and you know how many fit along one side. Could you figure out how many fit along the other side without counting again?""") as tracker:
            title = Text("Missing Dimensions\nfrom Perimeter", font="Poppins", weight=BOLD, color=PURPLE, font_size=48)
            title.to_edge(UP)
            
            self.wait_until_bookmark("bk_intro")
            self.play(FadeIn(title))
            self.wait(1)
            
            # Create table with chairs
            table = Rectangle(width=4, height=2.5, color=PURPLE, stroke_width=4)
            table.shift(DOWN*0.5)
            
            # Create chairs around table
            chair_positions = []
            # Top chairs
            for i in range(4):
                chair = Square(side_length=0.3, color=ORANGE_HL, fill_opacity=0.5)
                chair.move_to(table.get_top() + UP*0.3 + LEFT*1.5 + RIGHT*i)
                chair_positions.append(chair)
            # Bottom chairs
            for i in range(4):
                chair = Square(side_length=0.3, color=ORANGE_HL, fill_opacity=0.5)
                chair.move_to(table.get_bottom() + DOWN*0.3 + LEFT*1.5 + RIGHT*i)
                chair_positions.append(chair)
            # Left chairs
            for i in range(2):
                chair = Square(side_length=0.3, color=ORANGE_HL, fill_opacity=0.5)
                chair.move_to(table.get_left() + LEFT*0.3 + UP*0.7 + DOWN*i*1.4)
                chair_positions.append(chair)
            # Right chairs
            for i in range(2):
                chair = Square(side_length=0.3, color=ORANGE_HL, fill_opacity=0.5)
                chair.move_to(table.get_right() + RIGHT*0.3 + UP*0.7 + DOWN*i*1.4)
                chair_positions.append(chair)
            
            chairs = VGroup(*chair_positions)
            
            self.play(FadeOut(title))
            self.play(Create(table))
            self.play(LaggedStart(*[FadeIn(chair) for chair in chairs], lag_ratio=0.1))
            
            self.wait_until_bookmark("bk_chairs")
            
            # Highlight one side with known count
            top_label = Text("4 chairs", font="Poppins", color=PURPLE, font_size=24)
            top_label.next_to(table, UP, buff=0.8)
            
            side_label = Text("?", font="Poppins", color=ORANGE_HL, font_size=36)
            side_label.next_to(table, RIGHT, buff=0.8)
            
            self.play(Write(top_label), Write(side_label))
            self.play(side_label.animate.scale(1.2), rate_func=there_and_back)
            self.wait(1)
        
        # Scene 2: Perimeter Definition
        with self.voiceover(text=r"""<bookmark mark='bk_perimeter'/>The perimeter is the total length around a shape. <bookmark mark='bk_rect_formula'/>For a rectangle, the perimeter equals two times the sum of length and width. <bookmark mark='bk_square_formula'/>For a square, the perimeter equals four times the length of one side. <bookmark mark='bk_rearrange'/>So if we know the perimeter and one dimension, we can rearrange the formula and find the missing one. <bookmark mark='bk_tool'/>This means perimeter is not just for measuring—it is also a tool to work backwards.""") as tracker:
            
            self.play(FadeOut(table, chairs, top_label, side_label))
            
            self.wait_until_bookmark("bk_perimeter")
            
            # Create rectangle for perimeter demonstration
            rect = Rectangle(width=4, height=2, color=PURPLE, stroke_width=4)
            rect.move_to(ORIGIN)
            
            perimeter_def = Text("Perimeter = Total length\naround a shape", font="Poppins", color=PURPLE, font_size=28)
            perimeter_def.to_edge(UP)
            
            self.play(Write(perimeter_def))
            self.play(Create(rect))
            
            # Animate tracing perimeter
            perimeter_trace = rect.copy().set_color(ORANGE_HL)
            self.play(ShowPassingFlash(perimeter_trace, time_width=0.5, run_time=2))
            
            self.wait_until_bookmark("bk_rect_formula")
            
            # Add labels
            length_label = MathTex("l", color=PURPLE, font_size=36)
            length_label.next_to(rect, DOWN)
            width_label = MathTex("w", color=PURPLE, font_size=36)
            width_label.next_to(rect, LEFT)
            
            self.play(Write(length_label), Write(width_label))
            
            # Rectangle formula
            rect_formula = MathTex("P", "=", "2", "(", "l", "+", "w", ")", color=PURPLE, font_size=40)
            rect_formula.next_to(rect, DOWN, buff=1)
            
            self.play(Write(rect_formula))
            self.play(rect_formula.animate.set_color_by_tex("l", ORANGE_HL))
            self.play(rect_formula.animate.set_color_by_tex("w", ORANGE_HL))
            
            self.wait_until_bookmark("bk_square_formula")
            
            # Transform to square
            square = Square(side_length=2.5, color=PURPLE, stroke_width=4)
            square.move_to(ORIGIN)
            
            self.play(
                Transform(rect, square),
                FadeOut(length_label, width_label)
            )
            
            side_label_s = MathTex("s", color=PURPLE, font_size=36)
            side_label_s.next_to(square, DOWN)
            
            square_formula = MathTex("P", "=", "4", "s", color=PURPLE, font_size=40)
            square_formula.move_to(rect_formula.get_center())
            
            self.play(
                ReplacementTransform(rect_formula, square_formula),
                Write(side_label_s)
            )
            
            self.wait_until_bookmark("bk_rearrange")
            
            # Show rearrangement concept
            rearrange_text = Text("Rearrange to find\nmissing dimension", font="Poppins", color=ORANGE_HL, font_size=28)
            rearrange_text.next_to(square_formula, DOWN, buff=0.8)
            
            self.play(Write(rearrange_text))
            
            self.wait_until_bookmark("bk_tool")
            
            tool_text = Text("Work backwards!", font="Poppins", color=ORANGE_HL, font_size=32, weight=BOLD)
            tool_text.next_to(rearrange_text, DOWN, buff=0.3)
            
            self.play(Write(tool_text))
            self.wait(1)
        
        # Scene 3: Why it works
        with self.voiceover(text=r"""<bookmark mark='bk_why'/>Now, why does this work? <bookmark mark='bk_rect_sides'/>A rectangle has two equal lengths and two equal widths. <bookmark mark='bk_algebra'/>So once we know the perimeter and one of them, simple algebra gives us the other. <bookmark mark='bk_square_sides'/>A square has four equal sides, so its side is simply the perimeter divided by four.""") as tracker:
            
            self.play(FadeOut(rect, square, side_label_s, square_formula, perimeter_def, rearrange_text, tool_text))
            
            self.wait_until_bookmark("bk_why")
            
            why_title = Text("Why does this work?", font="Poppins", weight=BOLD, color=PURPLE, font_size=40)
            why_title.to_edge(UP)
            self.play(Write(why_title))
            
            self.wait_until_bookmark("bk_rect_sides")
            
            # Show rectangle with equal sides highlighted
            rect2 = Rectangle(width=4, height=2, color=PURPLE, stroke_width=4)
            rect2.shift(UP*0.5)
            
            self.play(Create(rect2))
            
            # Highlight pairs
            top_side = Line(rect2.get_corner(UL), rect2.get_corner(UR), color=ORANGE_HL, stroke_width=6)
            bottom_side = Line(rect2.get_corner(DL), rect2.get_corner(DR), color=ORANGE_HL, stroke_width=6)
            
            self.play(Create(top_side), Create(bottom_side))
            self.wait(0.5)
            
            left_side = Line(rect2.get_corner(UL), rect2.get_corner(DL), color=ORANGE_HL, stroke_width=6)
            right_side = Line(rect2.get_corner(UR), rect2.get_corner(DR), color=ORANGE_HL, stroke_width=6)
            
            self.play(
                top_side.animate.set_color(PURPLE),
                bottom_side.animate.set_color(PURPLE),
                Create(left_side),
                Create(right_side)
            )
            
            equal_text = Text("2 lengths + 2 widths", font="Poppins", color=PURPLE, font_size=28)
            equal_text.next_to(rect2, DOWN, buff=0.5)
            self.play(Write(equal_text))
            
            self.wait_until_bookmark("bk_algebra")
            
            algebra_text = Text("Simple algebra finds\nthe missing dimension", font="Poppins", color=ORANGE_HL, font_size=28)
            algebra_text.next_to(equal_text, DOWN, buff=0.3)
            self.play(Write(algebra_text))
            
            self.wait_until_bookmark("bk_square_sides")
            
            self.play(FadeOut(rect2, top_side, bottom_side, left_side, right_side, equal_text, algebra_text))
            
            square2 = Square(side_length=2.5, color=PURPLE, stroke_width=4)
            square2.shift(UP*0.5)
            self.play(Create(square2))
            
            # Highlight all four sides
            sides = []
            for i in range(4):
                if i == 0:
                    side = Line(square2.get_corner(UL), square2.get_corner(UR), color=ORANGE_HL, stroke_width=6)
                elif i == 1:
                    side = Line(square2.get_corner(UR), square2.get_corner(DR), color=ORANGE_HL, stroke_width=6)
                elif i == 2:
                    side = Line(square2.get_corner(DR), square2.get_corner(DL), color=ORANGE_HL, stroke_width=6)
                else:
                    side = Line(square2.get_corner(DL), square2.get_corner(UL), color=ORANGE_HL, stroke_width=6)
                sides.append(side)
            
            self.play(LaggedStart(*[Create(side) for side in sides], lag_ratio=0.2))
            
            square_text = Text("4 equal sides", font="Poppins", color=PURPLE, font_size=28)
            square_text.next_to(square2, DOWN, buff=0.5)
            
            divide_formula = MathTex("s", "=", "P", "\\div", "4", color=PURPLE, font_size=36)
            divide_formula.next_to(square_text, DOWN, buff=0.3)
            
            self.play(Write(square_text))
            self.play(Write(divide_formula))
            self.wait(1)
        
        # Scene 4: Problem Statement
        with self.voiceover(text=r"""<bookmark mark='bk_question'/>Question: <bookmark mark='bk_part1'/>Part one: The perimeter of a rectangular notebook is thirty-four centimetres. Its length is eleven centimetres. Find its width and check whether two such notebooks would fit along a twenty-four-centimetre shelf. <bookmark mark='bk_part2'/>Part two: A square tile has a perimeter of forty-eight centimetres. Find the length of one side.""") as tracker:
            
            self.play(FadeOut(why_title, square2, *sides, square_text, divide_formula))
            
            self.wait_until_bookmark("bk_question")
            
            question_title = Text("Question", font="Poppins", weight=BOLD, color=PURPLE, font_size=44)
            question_title.to_edge(UP)
            self.play(Write(question_title))
            
            self.wait_until_bookmark("bk_part1")
            
            # Part 1: Notebook problem
            part1_text = Text("Part 1: Rectangular Notebook", font="Poppins", color=PURPLE, font_size=32)
            part1_text.next_to(question_title, DOWN, buff=0.5)
            self.play(Write(part1_text))
            
            notebook = Rectangle(width=3, height=1.5, color=PURPLE, stroke_width=4)
            notebook.shift(UP*0.3)
            
            p_label = MathTex("P = 34", "\\text{ cm}", color=PURPLE, font_size=32)
            p_label.next_to(notebook, UP, buff=0.3)
            
            l_label = MathTex("l = 11", "\\text{ cm}", color=PURPLE, font_size=32)
            l_label.next_to(notebook, DOWN, buff=0.3)
            
            w_label = MathTex("w = ?", color=ORANGE_HL, font_size=32)
            w_label.next_to(notebook, LEFT, buff=0.3)
            
            self.play(Create(notebook))
            self.play(Write(p_label), Write(l_label), Write(w_label))
            
            shelf_question = Text("Fit on 24 cm shelf?", font="Poppins", color=ORANGE_HL, font_size=24)
            shelf_question.next_to(notebook, DOWN, buff=1.2)
            self.play(Write(shelf_question))
            
            self.wait_until_bookmark("bk_part2")
            
            self.play(FadeOut(part1_text, notebook, p_label, l_label, w_label, shelf_question))
            
            # Part 2: Square tile problem
            part2_text = Text("Part 2: Square Tile", font="Poppins", color=PURPLE, font_size=32)
            part2_text.next_to(question_title, DOWN, buff=0.5)
            self.play(Write(part2_text))
            
            tile = Square(side_length=2.5, color=PURPLE, stroke_width=4)
            tile.shift(DOWN*0.3)
            
            tile_p_label = MathTex("P = 48", "\\text{ cm}", color=PURPLE, font_size=32)
            tile_p_label.next_to(tile, UP, buff=0.3)
            
            tile_s_label = MathTex("s = ?", color=ORANGE_HL, font_size=32)
            tile_s_label.next_to(tile, DOWN, buff=0.3)
            
            self.play(Create(tile))
            self.play(Write(tile_p_label), Write(tile_s_label))
            self.wait(1)
        
        # Scene 5: Solution for Notebook
        with self.voiceover(text=r"""<bookmark mark='bk_solution'/>Solution: <bookmark mark='bk_notebook_start'/>For the notebook: <bookmark mark='bk_formula1'/>Two times the sum of length and width equals the perimeter. <bookmark mark='bk_substitute'/>Two times eleven plus width equals thirty-four. <bookmark mark='bk_divide'/>Eleven plus width equals seventeen. <bookmark mark='bk_width'/>So width equals six centimetres. <bookmark mark='bk_two_notebooks'/>Two notebooks placed side by side would need twelve centimetres, <bookmark mark='bk_fits'/>which fits well on the shelf.""") as tracker:
            
            self.play(FadeOut(question_title, part2_text, tile, tile_p_label, tile_s_label))
            
            self.wait_until_bookmark("bk_solution")
            
            solution_title = Text("Solution", font="Poppins", weight=BOLD, color=PURPLE, font_size=44)
            solution_title.to_edge(UP)
            self.play(Write(solution_title))
            
            self.wait_until_bookmark("bk_notebook_start")
            
            notebook_heading = Text("For the notebook:", font="Poppins", color=PURPLE, font_size=32)
            notebook_heading.next_to(solution_title, DOWN, buff=0.5)
            self.play(Write(notebook_heading))
            
            self.wait_until_bookmark("bk_formula1")
            
            # Step 1: Formula
            step1 = MathTex("2", "(", "l", "+", "w", ")", "=", "P", color=PURPLE, font_size=36)
            step1.next_to(notebook_heading, DOWN, buff=0.5)
            self.play(Write(step1))
            
            self.wait_until_bookmark("bk_substitute")
            
            # Step 2: Substitute values
            step2 = MathTex("2", "(", "11", "+", "w", ")", "=", "34", color=PURPLE, font_size=36)
            step2.next_to(step1, DOWN, buff=0.4)
            self.play(Write(step2))
            self.play(step2[2].animate.set_color(ORANGE_HL), step2[7].animate.set_color(ORANGE_HL))
            
            self.wait_until_bookmark("bk_divide")
            
            # Step 3: Divide both sides by 2
            step3 = MathTex("11", "+", "w", "=", "17", color=PURPLE, font_size=36)
            step3.next_to(step2, DOWN, buff=0.4)
            self.play(Write(step3))
            self.play(step3[4].animate.set_color(ORANGE_HL))
            
            self.wait_until_bookmark("bk_width")
            
            # Step 4: Solve for w
            step4 = MathTex("w", "=", "6", "\\text{ cm}", color=PURPLE, font_size=36)
            step4.next_to(step3, DOWN, buff=0.4)
            self.play(Write(step4))
            
            # Highlight answer
            answer_box = SurroundingRectangle(step4, color=ORANGE_HL, buff=0.2)
            self.play(Create(answer_box))
            
            self.wait_until_bookmark("bk_two_notebooks")
            
            self.play(FadeOut(step1, step2, step3, step4, answer_box, notebook_heading))
            
            # Show two notebooks
            notebook1 = Rectangle(width=2, height=1.2, color=PURPLE, stroke_width=3, fill_opacity=0.3, fill_color=PURPLE)
            notebook1.shift(LEFT*1.5 + UP*0.5)
            
            notebook2 = Rectangle(width=2, height=1.2, color=PURPLE, stroke_width=3, fill_opacity=0.3, fill_color=PURPLE)
            notebook2.shift(RIGHT*1.5 + UP*0.5)
            
            width1 = MathTex("6", "\\text{ cm}", color=ORANGE_HL, font_size=28)
            width1.next_to(notebook1, LEFT, buff=0.2)
            
            width2 = MathTex("6", "\\text{ cm}", color=ORANGE_HL, font_size=28)
            width2.next_to(notebook2, RIGHT, buff=0.2)
            
            self.play(Create(notebook1), Create(notebook2))
            self.play(Write(width1), Write(width2))
            
            total_width = MathTex("6 + 6 = 12", "\\text{ cm}", color=PURPLE, font_size=32)
            total_width.next_to(notebook1, DOWN, buff=1)
            self.play(Write(total_width))
            
            self.wait_until_bookmark("bk_fits")
            
            # Show shelf comparison
            shelf = Rectangle(width=5, height=0.3, color=PURPLE, stroke_width=3)
            shelf.next_to(total_width, DOWN, buff=0.5)
            
            shelf_label = MathTex("24", "\\text{ cm shelf}", color=PURPLE, font_size=28)
            shelf_label.next_to(shelf, DOWN, buff=0.2)
            
            self.play(Create(shelf), Write(shelf_label))
            
            checkmark = Text("✓ Fits!", font="Poppins", color="#00C853", font_size=36, weight=BOLD)
            checkmark.next_to(shelf, RIGHT, buff=0.5)
            self.play(Write(checkmark))
            self.wait(1)
        
        # Scene 6: Solution for Tile
        with self.voiceover(text=r"""<bookmark mark='bk_tile_start'/>For the tile: <bookmark mark='bk_tile_formula'/>The perimeter equals four times the side. <bookmark mark='bk_tile_substitute'/>Four times the side equals forty-eight. <bookmark mark='bk_tile_answer'/>So the side equals twelve centimetres. <bookmark mark='bk_builders'/>This is the same idea builders use when calculating tile sizes for a floor.""") as tracker:
            
            self.play(FadeOut(notebook1, notebook2, width1, width2, total_width, shelf, shelf_label, checkmark))
            
            self.wait_until_bookmark("bk_tile_start")
            
            tile_heading = Text("For the tile:", font="Poppins", color=PURPLE, font_size=32)
            tile_heading.next_to(solution_title, DOWN, buff=0.5)
            self.play(Write(tile_heading))
            
            self.wait_until_bookmark("bk_tile_formula")
            
            # Tile formula
            tile_step1 = MathTex("P", "=", "4", "s", color=PURPLE, font_size=36)
            tile_step1.next_to(tile_heading, DOWN, buff=0.5)
            self.play(Write(tile_step1))
            
            self.wait_until_bookmark("bk_tile_substitute")
            
            # Substitute
            tile_step2 = MathTex("4", "s", "=", "48", color=PURPLE, font_size=36)
            tile_step2.next_to(tile_step1, DOWN, buff=0.4)
            self.play(Write(tile_step2))
            self.play(tile_step2[3].animate.set_color(ORANGE_HL))
            
            self.wait_until_bookmark("bk_tile_answer")
            
            # Solve
            tile_step3 = MathTex("s", "=", "12", "\\text{ cm}", color=PURPLE, font_size=36)
            tile_step3.next_to(tile_step2, DOWN, buff=0.4)
            self.play(Write(tile_step3))
            
            tile_answer_box = SurroundingRectangle(tile_step3, color=ORANGE_HL, buff=0.2)
            self.play(Create(tile_answer_box))
            
            self.wait_until_bookmark("bk_builders")
            
            # Show builder illustration
            builder_text = Text("Real-world application:\nBuilders use this!", font="Poppins", color=ORANGE_HL, font_size=28)
            builder_text.next_to(tile_step3, DOWN, buff=0.8)
            self.play(Write(builder_text))
            
            # Simple floor grid
            floor_grid = VGroup()
            for i in range(3):
                for j in range(3):
                    tile_square = Square(side_length=0.5, color=PURPLE, stroke_width=2, fill_opacity=0.2, fill_color=PURPLE)
                    tile_square.shift(RIGHT*i*0.5 + DOWN*j*0.5)
                    floor_grid.add(tile_square)
            
            floor_grid.scale(0.8)
            floor_grid.next_to(builder_text, DOWN, buff=0.3)
            self.play(LaggedStart(*[FadeIn(tile) for tile in floor_grid], lag_ratio=0.05))
            self.wait(1)
        
        # Scene 7: Summary
        with self.voiceover(text=r"""<bookmark mark='bk_summary'/>Summary: <bookmark mark='bk_sum1'/>Perimeter formulas can be rearranged to find missing dimensions. <bookmark mark='bk_sum2'/>Rectangle: perimeter is two times the sum of length and width. <bookmark mark='bk_sum3'/>Square: side is the perimeter divided by four.""") as tracker:
            
            self.play(FadeOut(solution_title, tile_heading, tile_step1, tile_step2, tile_step3, tile_answer_box, builder_text, floor_grid))
            
            self.wait_until_bookmark("bk_summary")
            
            summary_title = Text("Summary", font="Poppins", weight=BOLD, color=PURPLE, font_size=48)
            summary_title.to_edge(UP)
            self.play(Write(summary_title))
            
            self.wait_until_bookmark("bk_sum1")
            
            bullet1 = Text("• Perimeter formulas can be\n  rearranged to find missing dimensions", font="Poppins", color=PURPLE, font_size=28)
            bullet1.next_to(summary_title, DOWN, buff=0.8)
            bullet1.to_edge(LEFT, buff=1)
            self.play(Write(bullet1))
            
            self.wait_until_bookmark("bk_sum2")
            
            bullet2 = VGroup(
                Text("• Rectangle:", font="Poppins", color=PURPLE, font_size=28),
                MathTex("P = 2(l + w)", color=PURPLE, font_size=32)
            )
            bullet2.arrange(RIGHT, buff=0.3)
            bullet2.next_to(bullet1, DOWN, buff=0.5, aligned_edge=LEFT)
            self.play(Write(bullet2))
            
            self.wait_until_bookmark("bk_sum3")
            
            bullet3 = VGroup(
                Text("• Square:", font="Poppins", color=PURPLE, font_size=28),
                MathTex("s = P \\div 4", color=PURPLE, font_size=32)
            )
            bullet3.arrange(RIGHT, buff=0.3)
            bullet3.next_to(bullet2, DOWN, buff=0.5, aligned_edge=LEFT)
            self.play(Write(bullet3))
            
            self.wait(2)
            
            # Final fade out
            self.play(FadeOut(summary_title, bullet1, bullet2, bullet3))