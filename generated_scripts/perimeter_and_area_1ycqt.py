import os
os.environ["OPENAI_API_KEY"] = "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"
from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.openai import OpenAIService

config.background_color = "#E7E5F3"
PURPLE = "#7464CE"
ORANGE_HL = "#FF9302"

class PerimeterAndAreaScene(VoiceoverScene):
    def construct(self):
        self.set_speech_service(OpenAIService(voice="shimmer", model="gpt-4o-mini-tts"))
        
        # SEGMENT 1: HOOK - Classroom table with chairs
        with self.voiceover(text="""<bookmark mark='hook_start'/>Imagine you are arranging chairs around a rectangular classroom table. <break time='0.3s'/> You know the total number of chairs that fit around it, and you know how many fit along one side. <break time='0.4s'/> Could you figure out how many fit along the other side without counting again?<bookmark mark='hook_end'/>""") as tracker:
            
            table = Rectangle(width=5, height=3, color=PURPLE, fill_opacity=0.2, stroke_width=4)
            self.play(FadeIn(table))
            self.wait_until_bookmark("hook_start")
            
            # Create chair icons (small squares)
            chairs = VGroup()
            # Top side: 5 chairs
            for i in range(5):
                chair = Square(side_length=0.2, color=ORANGE_HL, fill_opacity=0.8)
                chair.move_to(table.get_top() + DOWN*0.3 + LEFT*2 + RIGHT*i)
                chairs.add(chair)
            
            # Bottom side: 5 chairs
            for i in range(5):
                chair = Square(side_length=0.2, color=ORANGE_HL, fill_opacity=0.8)
                chair.move_to(table.get_bottom() + UP*0.3 + LEFT*2 + RIGHT*i)
                chairs.add(chair)
            
            # Left side: 3 chairs
            for i in range(3):
                chair = Square(side_length=0.2, color=ORANGE_HL, fill_opacity=0.8)
                chair.move_to(table.get_left() + RIGHT*0.3 + UP*1 + DOWN*i)
                chairs.add(chair)
            
            # Right side: question marks
            question_marks = VGroup()
            for i in range(3):
                qm = Text("?", font="Poppins", color=ORANGE_HL, font_size=24)
                qm.move_to(table.get_right() + LEFT*0.3 + UP*1 + DOWN*i)
                question_marks.add(qm)
            
            self.play(LaggedStart(*[FadeIn(chair) for chair in chairs], lag_ratio=0.1))
            self.play(FadeIn(question_marks))
            
            # Label for known side
            top_label = Text("5 chairs", font="Poppins", color=PURPLE, font_size=28)
            top_label.next_to(table, UP, buff=0.3)
            self.play(Write(top_label))
            
            self.wait_until_bookmark("hook_end")
            self.play(FadeOut(VGroup(table, chairs, question_marks, top_label)))
        
        self.wait(0.3)
        
        # SEGMENT 2: CONCEPT INTRODUCTION
        with self.voiceover(text="""<bookmark mark='concept_start'/>The perimeter is the total length around a shape. <break time='0.3s'/> For a rectangle, the perimeter equals two times the sum of length and width. <break time='0.3s'/> For a square, the perimeter equals four times the length of one side. <break time='0.4s'/> So if we know the perimeter and one dimension, we can rearrange the formula and find the missing one. <break time='0.3s'/> This means perimeter is not just for measuring — it is also a tool to work backwards.<bookmark mark='concept_end'/>""") as tracker:
            
            rect = Rectangle(width=4, height=2.5, color=PURPLE, stroke_width=4)
            self.play(Create(rect))
            self.wait_until_bookmark("concept_start")
            
            # Trace perimeter
            perimeter_line = rect.copy().set_color(ORANGE_HL).set_stroke(width=6)
            self.play(Create(perimeter_line), run_time=2)
            
            # Rectangle formula
            rect_formula = MathTex("P", "=", "2", "(", "l", "+", "w", ")", color=PURPLE, font_size=40)
            rect_formula.move_to(UP*1.5)
            self.play(Write(rect_formula))
            
            # Highlight formula
            self.play(rect_formula.animate.set_color(ORANGE_HL), run_time=0.5)
            self.play(rect_formula.animate.set_color(PURPLE), run_time=0.5)
            
            self.play(FadeOut(rect), FadeOut(perimeter_line))
            
            # Square
            square = Square(side_length=2.5, color=PURPLE, stroke_width=4)
            square.shift(DOWN*0.5)
            self.play(Create(square))
            
            square_perimeter = square.copy().set_color(ORANGE_HL).set_stroke(width=6)
            self.play(Create(square_perimeter), run_time=1.5)
            
            # Square formula
            square_formula = MathTex("P", "=", "4", "s", color=PURPLE, font_size=40)
            square_formula.move_to(DOWN*2)
            self.play(Write(square_formula))
            
            self.play(square_formula.animate.set_color(ORANGE_HL), run_time=0.5)
            self.play(square_formula.animate.set_color(PURPLE), run_time=0.5)
            
            self.wait_until_bookmark("concept_end")
            self.play(FadeOut(VGroup(square, square_perimeter, rect_formula, square_formula)))
        
        self.wait(0.3)
        
        # SEGMENT 3: WHY IT WORKS
        with self.voiceover(text="""<bookmark mark='why_start'/>A rectangle has two equal lengths and two equal widths. <break time='0.3s'/> So once we know the perimeter and one of them, simple algebra gives us the other. <break time='0.3s'/> A square has four equal sides, so its side is simply the perimeter divided by four.<bookmark mark='why_end'/>""") as tracker:
            
            rect2 = Rectangle(width=4, height=2.5, color=PURPLE, stroke_width=4)
            self.play(Create(rect2))
            self.wait_until_bookmark("why_start")
            
            # Highlight paired sides
            top_line = Line(rect2.get_corner(UL), rect2.get_corner(UR), color=PURPLE, stroke_width=8)
            bottom_line = Line(rect2.get_corner(DL), rect2.get_corner(DR), color=PURPLE, stroke_width=8)
            self.play(Create(top_line), Create(bottom_line))
            
            length_label1 = Text("l", font="Poppins", color=PURPLE, font_size=32)
            length_label1.next_to(top_line, UP, buff=0.2)
            length_label2 = Text("l", font="Poppins", color=PURPLE, font_size=32)
            length_label2.next_to(bottom_line, DOWN, buff=0.2)
            self.play(Write(length_label1), Write(length_label2))
            
            left_line = Line(rect2.get_corner(UL), rect2.get_corner(DL), color=ORANGE_HL, stroke_width=8)
            right_line = Line(rect2.get_corner(UR), rect2.get_corner(DR), color=ORANGE_HL, stroke_width=8)
            self.play(Create(left_line), Create(right_line))
            
            width_label1 = Text("w", font="Poppins", color=ORANGE_HL, font_size=32)
            width_label1.next_to(left_line, LEFT, buff=0.2)
            width_label2 = Text("w", font="Poppins", color=ORANGE_HL, font_size=32)
            width_label2.next_to(right_line, RIGHT, buff=0.2)
            self.play(Write(width_label1), Write(width_label2))
            
            self.play(FadeOut(VGroup(rect2, top_line, bottom_line, left_line, right_line, length_label1, length_label2, width_label1, width_label2)))
            
            # Square with equal sides
            square2 = Square(side_length=2.5, color=PURPLE, stroke_width=4)
            self.play(Create(square2))
            
            side_labels = VGroup()
            for direction in [UP, DOWN, LEFT, RIGHT]:
                label = Text("s", font="Poppins", color=PURPLE, font_size=32)
                if direction == UP:
                    label.next_to(square2, UP, buff=0.2)
                elif direction == DOWN:
                    label.next_to(square2, DOWN, buff=0.2)
                elif direction == LEFT:
                    label.next_to(square2, LEFT, buff=0.2)
                else:
                    label.next_to(square2, RIGHT, buff=0.2)
                side_labels.add(label)
            
            self.play(LaggedStart(*[Write(label) for label in side_labels], lag_ratio=0.2))
            
            self.wait_until_bookmark("why_end")
            self.play(FadeOut(VGroup(square2, side_labels)))
        
        self.wait(0.3)
        
        # SEGMENT 4: PROBLEM STATEMENT
        with self.voiceover(text="""<bookmark mark='problem_start'/>Part 1: The perimeter of a rectangular notebook is 34 centimetres. <break time='0.3s'/> Its length is 11 centimetres. <break time='0.3s'/> Find its width and check whether two such notebooks would fit along a 24-centimetre shelf. <break time='0.4s'/> Part 2: A square tile has a perimeter of 48 centimetres. <break time='0.3s'/> Find the length of one side.<bookmark mark='problem_end'/>""") as tracker:
            
            # Notebook rectangle
            notebook = Rectangle(width=3.5, height=2, color=PURPLE, stroke_width=4, fill_opacity=0.1)
            notebook.shift(UP*1.5 + LEFT*0.5)
            
            perimeter_label = Text("P = 34 cm", font="Poppins", color=PURPLE, font_size=28)
            perimeter_label.next_to(notebook, UP, buff=0.3)
            
            length_label = Text("l = 11 cm", font="Poppins", color=PURPLE, font_size=28)
            length_label.next_to(notebook, DOWN, buff=0.2)
            
            width_label = Text("w = ?", font="Poppins", color=ORANGE_HL, font_size=28)
            width_label.next_to(notebook, LEFT, buff=0.2)
            
            self.play(Create(notebook))
            self.wait_until_bookmark("problem_start")
            self.play(Write(perimeter_label))
            self.play(Write(length_label))
            self.play(Write(width_label))
            
            # Square tile
            tile = Square(side_length=2.5, color=PURPLE, stroke_width=4, fill_opacity=0.1)
            tile.shift(DOWN*1.8)
            
            tile_perimeter = Text("P = 48 cm", font="Poppins", color=PURPLE, font_size=28)
            tile_perimeter.next_to(tile, UP, buff=0.3)
            
            tile_side = Text("s = ?", font="Poppins", color=ORANGE_HL, font_size=28)
            tile_side.next_to(tile, DOWN, buff=0.2)
            
            self.play(Create(tile))
            self.play(Write(tile_perimeter))
            self.play(Write(tile_side))
            
            # Pulse unknowns
            self.play(width_label.animate.scale(1.2).set_color(ORANGE_HL), run_time=0.3)
            self.play(width_label.animate.scale(1/1.2), run_time=0.3)
            self.play(tile_side.animate.scale(1.2).set_color(ORANGE_HL), run_time=0.3)
            self.play(tile_side.animate.scale(1/1.2), run_time=0.3)
            
            self.wait_until_bookmark("problem_end")
            self.play(FadeOut(VGroup(notebook, perimeter_label, length_label, width_label, tile, tile_perimeter, tile_side)))
        
        self.wait(0.3)
        
        # SEGMENT 5: SOLUTION NOTEBOOK
        with self.voiceover(text="""<bookmark mark='solution_notebook_start'/>For the notebook: <break time='0.2s'/> Two times the sum of length and width equals the perimeter. <break time='0.3s'/> Two times eleven plus width equals thirty-four. <break time='0.3s'/> Eleven plus width equals seventeen. <break time='0.3s'/> So width equals six centimetres. <break time='0.4s'/> Two notebooks placed side by side would need twelve centimetres, which fits well on the shelf.<bookmark mark='solution_notebook_end'/>""") as tracker:
            
            # Left side: algebra
            step1 = MathTex("2", "(", "l", "+", "w", ")", "=", "P", color=PURPLE, font_size=36)
            step1.shift(LEFT*3.5 + UP*2.5)
            
            step2 = MathTex("2", "(", "11", "+", "w", ")", "=", "34", color=PURPLE, font_size=36)
            step2.next_to(step1, DOWN, buff=0.4, aligned_edge=LEFT)
            
            step3 = MathTex("11", "+", "w", "=", "17", color=PURPLE, font_size=36)
            step3.next_to(step2, DOWN, buff=0.4, aligned_edge=LEFT)
            
            step4 = MathTex("w", "=", "6", "\\text{ cm}", color=PURPLE, font_size=36)
            step4.next_to(step3, DOWN, buff=0.4, aligned_edge=LEFT)
            
            self.wait_until_bookmark("solution_notebook_start")
            self.play(Write(step1))
            self.play(step1[4].animate.set_color(ORANGE_HL))
            
            self.play(Write(step2))
            self.play(step2[4].animate.set_color(ORANGE_HL))
            
            self.play(Write(step3))
            self.play(step3[2].animate.set_color(ORANGE_HL))
            
            self.play(Write(step4))
            self.play(step4[0].animate.set_color(ORANGE_HL), step4[2].animate.set_color(ORANGE_HL))
            
            # Right side: notebook visual
            notebook_solved = Rectangle(width=3.5, height=2, color=PURPLE, stroke_width=4, fill_opacity=0.15)
            notebook_solved.shift(RIGHT*3 + UP*1.5)
            
            length_dim = Text("11 cm", font="Poppins", color=PURPLE, font_size=24)
            length_dim.next_to(notebook_solved, DOWN, buff=0.15)
            
            width_dim = Text("6 cm", font="Poppins", color=ORANGE_HL, font_size=24)
            width_dim.next_to(notebook_solved, LEFT, buff=0.15)
            
            self.play(Create(notebook_solved))
            self.play(Write(length_dim))
            self.play(Write(width_dim))
            
            # Shelf visualization
            shelf = Line(LEFT*3, RIGHT*3, color=PURPLE, stroke_width=6)
            shelf.shift(DOWN*2)
            shelf_label = Text("24 cm shelf", font="Poppins", color=PURPLE, font_size=24)
            shelf_label.next_to(shelf, DOWN, buff=0.2)
            
            self.play(Create(shelf), Write(shelf_label))
            
            # Two notebooks on shelf
            notebook1 = Rectangle(width=1.5, height=0.8, color=PURPLE, stroke_width=3, fill_opacity=0.3)
            notebook1.move_to(shelf.get_start() + RIGHT*0.75 + UP*0.5)
            
            notebook2 = Rectangle(width=1.5, height=0.8, color=PURPLE, stroke_width=3, fill_opacity=0.3)
            notebook2.move_to(notebook1.get_right() + RIGHT*0.75)
            
            self.play(FadeIn(notebook1), FadeIn(notebook2))
            
            total_width = Text("12 cm", font="Poppins", color=ORANGE_HL, font_size=24)
            total_width.next_to(VGroup(notebook1, notebook2), UP, buff=0.2)
            self.play(Write(total_width))
            
            checkmark = Text("✓", font="Poppins", color="#00FF00", font_size=48)
            checkmark.next_to(total_width, RIGHT, buff=0.3)
            self.play(FadeIn(checkmark, scale=1.5))
            
            self.wait_until_bookmark("solution_notebook_end")
            self.play(FadeOut(VGroup(step1, step2, step3, step4, notebook_solved, length_dim, width_dim, shelf, shelf_label, notebook1, notebook2, total_width, checkmark)))
        
        self.wait(0.3)
        
        # SEGMENT 6: SOLUTION TILE
        with self.voiceover(text="""<bookmark mark='solution_tile_start'/>For the tile: <break time='0.2s'/> The perimeter equals four times the side. <break time='0.3s'/> Four times the side equals forty-eight. <break time='0.3s'/> So the side equals twelve centimetres. <break time='0.3s'/> This is the same idea builders use when calculating tile sizes for a floor.<bookmark mark='solution_tile_end'/>""") as tracker:
            
            tile_step1 = MathTex("P", "=", "4", "s", color=PURPLE, font_size=40)
            tile_step1.shift(UP*2)
            
            tile_step2 = MathTex("48", "=", "4", "s", color=PURPLE, font_size=40)
            tile_step2.next_to(tile_step1, DOWN, buff=0.5)
            
            tile_step3 = MathTex("s", "=", "12", "\\text{ cm}", color=PURPLE, font_size=40)
            tile_step3.next_to(tile_step2, DOWN, buff=0.5)
            
            self.wait_until_bookmark("solution_tile_start")
            self.play(Write(tile_step1))
            self.play(tile_step1[3].animate.set_color(ORANGE_HL))
            
            self.play(Write(tile_step2))
            self.play(tile_step2[3].animate.set_color(ORANGE_HL))
            
            self.play(Write(tile_step3))
            self.play(tile_step3[0].animate.set_color(ORANGE_HL), tile_step3[2].animate.set_color(ORANGE_HL))
            
            # Tile visual
            tile_visual = Square(side_length=2.5, color=PURPLE, stroke_width=4, fill_opacity=0.15)
            tile_visual.shift(DOWN*1.2)
            self.play(Create(tile_visual))
            
            # Label all sides
            side_label_top = Text("12 cm", font="Poppins", color=ORANGE_HL, font_size=24)
            side_label_top.next_to(tile_visual, UP, buff=0.15)
            
            side_label_bottom = Text("12 cm", font="Poppins", color=ORANGE_HL, font_size=24)
            side_label_bottom.next_to(tile_visual, DOWN, buff=0.15)
            
            side_label_left = Text("12 cm", font="Poppins", color=ORANGE_HL, font_size=24)
            side_label_left.next_to(tile_visual, LEFT, buff=0.15)
            
            side_label_right = Text("12 cm", font="Poppins", color=ORANGE_HL, font_size=24)
            side_label_right.next_to(tile_visual, RIGHT, buff=0.15)
            
            self.play(
                Write(side_label_top),
                Write(side_label_bottom),
                Write(side_label_left),
                Write(side_label_right)
            )
            
            # Builder icon (simple hard hat)
            builder_hat = Polygon(
                [-0.3, 0, 0], [0.3, 0, 0], [0.4, 0.3, 0], [-0.4, 0.3, 0],
                color=ORANGE_HL, fill_opacity=0.7, stroke_width=2
            )
            builder_hat.scale(0.5).shift(RIGHT*4 + DOWN*2)
            self.play(FadeIn(builder_hat, scale=0.5))
            
            self.wait_until_bookmark("solution_tile_end")
            self.play(FadeOut(VGroup(tile_step1, tile_step2, tile_step3, tile_visual, side_label_top, side_label_bottom, side_label_left, side_label_right, builder_hat)))
        
        self.wait(0.3)
        
        # SEGMENT 7: SUMMARY
        with self.voiceover(text="""<bookmark mark='summary_start'/>Perimeter formulas can be rearranged to find missing dimensions. <break time='0.3s'/> Rectangle: perimeter is two times the sum of length and width. <break time='0.3s'/> Square: side is the perimeter divided by four.<bookmark mark='summary_end'/>""") as tracker:
            
            title = Text("Summary", font="Poppins", color=PURPLE, font_size=44)
            title.to_edge(UP, buff=0.5)
            self.play(Write(title))
            self.wait_until_bookmark("summary_start")
            
            # Left: Rectangle
            rect_summary = Rectangle(width=3, height=2, color=PURPLE, stroke_width=4, fill_opacity=0.1)
            rect_summary.shift(LEFT*3.5 + DOWN*0.5)
            
            rect_formula_summary = MathTex("P", "=", "2", "(", "l", "+", "w", ")", color=PURPLE, font_size=32)
            rect_formula_summary.next_to(rect_summary, DOWN, buff=0.4)
            
            rect_rearranged = MathTex("w", "=", "\\frac{P}{2}", "-", "l", color=PURPLE, font_size=28)
            rect_rearranged.next_to(rect_formula_summary, DOWN, buff=0.3)
            
            self.play(Create(rect_summary))
            self.play(Write(rect_formula_summary))
            self.play(rect_formula_summary[4].animate.set_color(ORANGE_HL), rect_formula_summary[6].animate.set_color(ORANGE_HL))
            self.play(Write(rect_rearranged))
            self.play(rect_rearranged[0].animate.set_color(ORANGE_HL))
            
            # Right: Square
            square_summary = Square(side_length=2.5, color=PURPLE, stroke_width=4, fill_opacity=0.1)
            square_summary.shift(RIGHT*3.5 + DOWN*0.5)
            
            square_formula_summary = MathTex("P", "=", "4", "s", color=PURPLE, font_size=32)
            square_formula_summary.next_to(square_summary, DOWN, buff=0.4)
            
            square_rearranged = MathTex("s", "=", "\\frac{P}{4}", color=PURPLE, font_size=28)
            square_rearranged.next_to(square_formula_summary, DOWN, buff=0.3)
            
            self.play(Create(square_summary))
            self.play(Write(square_formula_summary))
            self.play(square_formula_summary[3].animate.set_color(ORANGE_HL))
            self.play(Write(square_rearranged))
            self.play(square_rearranged[0].animate.set_color(ORANGE_HL))
            
            # Arrows showing solution path
            arrow_rect = Arrow(
                rect_formula_summary.get_bottom(),
                rect_rearranged.get_top(),
                color=ORANGE_HL,
                buff=0.1,
                stroke_width=3
            )
            
            arrow_square = Arrow(
                square_formula_summary.get_bottom(),
                square_rearranged.get_top(),
                color=ORANGE_HL,
                buff=0.1,
                stroke_width=3
            )
            
            self.play(GrowArrow(arrow_rect), GrowArrow(arrow_square))
            
            self.wait_until_bookmark("summary_end")
            self.wait(1)
            
            self.play(FadeOut(VGroup(title, rect_summary, rect_formula_summary, rect_rearranged, square_summary, square_formula_summary, square_rearranged, arrow_rect, arrow_square)))
        
        self.wait(0.5)