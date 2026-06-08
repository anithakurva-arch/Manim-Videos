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
        self.set_speech_service(OpenAIService(voice="shimmer", model="gpt-4o-mini-tts"))
        
        # Segment 1: Introduction with table and chairs
        with self.voiceover(text="<bookmark mark='intro'/>Hello students! Imagine you are arranging chairs around a rectangular classroom table. <break time='0.3s'/> You know the total number of chairs that fit around it, and you know how many fit along one side. <break time='0.3s'/> Could you figure out how many fit along the other side without counting again?<break time='0.5s'/>") as tracker:
            table = Rectangle(width=4, height=2.5, color=PURPLE, fill_opacity=0.2, stroke_width=3)
            self.play(FadeIn(table))
            self.wait_until_bookmark("intro")
            
            # Create chairs around perimeter
            chairs = VGroup()
            # Top side - 5 chairs
            for i in range(5):
                chair = Square(side_length=0.3, color=ORANGE_HL, fill_opacity=0.6).move_to(table.get_top() + DOWN*0.3 + LEFT*1.5 + RIGHT*i*0.8)
                chairs.add(chair)
            # Bottom side - 5 chairs
            for i in range(5):
                chair = Square(side_length=0.3, color=ORANGE_HL, fill_opacity=0.6).move_to(table.get_bottom() + UP*0.3 + LEFT*1.5 + RIGHT*i*0.8)
                chairs.add(chair)
            # Left side - 3 chairs
            for i in range(3):
                chair = Square(side_length=0.3, color=ORANGE_HL, fill_opacity=0.6).move_to(table.get_left() + RIGHT*0.3 + UP*0.8 + DOWN*i*0.8)
                chairs.add(chair)
            # Right side - 3 chairs
            for i in range(3):
                chair = Square(side_length=0.3, color=ORANGE_HL, fill_opacity=0.6).move_to(table.get_right() + LEFT*0.3 + UP*0.8 + DOWN*i*0.8)
                chairs.add(chair)
            
            self.play(LaggedStart(*[FadeIn(chair) for chair in chairs], lag_ratio=0.1))
            
            # Highlight one side with count
            top_bracket = BraceBetweenPoints(table.get_corner(UL) + UP*0.6, table.get_corner(UR) + UP*0.6, direction=UP, color=PURPLE)
            top_label = Text("5", font="Poppins", color=PURPLE, font_size=28).next_to(top_bracket, UP, buff=0.1)
            self.play(Create(top_bracket), Write(top_label))
            
            # Question mark on adjacent side
            right_bracket = BraceBetweenPoints(table.get_corner(UR) + RIGHT*0.6, table.get_corner(DR) + RIGHT*0.6, direction=RIGHT, color=ORANGE_HL)
            question = Text("?", font="Poppins", color=ORANGE_HL, font_size=32).next_to(right_bracket, RIGHT, buff=0.1)
            self.play(Create(right_bracket), Write(question))
            self.play(question.animate.scale(1.3), rate_func=there_and_back, run_time=0.5)
        
        self.play(FadeOut(VGroup(table, chairs, top_bracket, top_label, right_bracket, question)))
        
        # Segment 2: Concept explanation with formulas
        with self.voiceover(text="<bookmark mark='concept_start'/>The perimeter is the total length around a shape. <break time='0.3s'/> For a rectangle, the perimeter equals two times the sum of length and width. <break time='0.3s'/> For a square, the perimeter equals four times the length of one side. <break time='0.4s'/> So if we know the perimeter and one dimension, we can rearrange the formula and find the missing one. <break time='0.3s'/> This means perimeter is not just for measuring — it is also a tool to work backwards.<break time='0.5s'/>") as tracker:
            self.wait_until_bookmark("concept_start")
            
            # Rectangle with perimeter
            rect = Rectangle(width=3, height=2, color=PURPLE, stroke_width=4).shift(LEFT*3 + UP*0.5)
            self.play(Create(rect))
            
            # Trace perimeter
            perimeter_line = rect.copy().set_color(ORANGE_HL).set_stroke(width=6)
            self.play(Create(perimeter_line), run_time=2)
            
            # Rectangle formula
            rect_formula = MathTex("P", "=", "2", "(", "l", "+", "w", ")", font_size=36, color=PURPLE).next_to(rect, DOWN, buff=0.5)
            rect_formula[0].set_color(ORANGE_HL)
            self.play(Write(rect_formula))
            self.wait(0.5)
            
            # Square with formula
            square = Square(side_length=2, color=PURPLE, stroke_width=4).shift(RIGHT*3 + UP*0.5)
            self.play(Create(square))
            
            square_perimeter = square.copy().set_color(ORANGE_HL).set_stroke(width=6)
            self.play(Create(square_perimeter), run_time=1.5)
            
            square_formula = MathTex("P", "=", "4", "s", font_size=36, color=PURPLE).next_to(square, DOWN, buff=0.5)
            square_formula[0].set_color(ORANGE_HL)
            self.play(Write(square_formula))
            
            # Bidirectional arrow
            arrow = DoubleArrow(LEFT*1, RIGHT*1, color=ORANGE_HL, buff=0.2).shift(DOWN*2.5)
            arrow_label = Text("Work Backwards", font="Poppins", font_size=24, color=PURPLE).next_to(arrow, DOWN, buff=0.2)
            self.play(Create(arrow), Write(arrow_label))
        
        self.play(FadeOut(VGroup(rect, perimeter_line, rect_formula, square, square_perimeter, square_formula, arrow, arrow_label)))
        
        # Segment 3: Why it works
        with self.voiceover(text="<bookmark mark='why_works'/>Now, why does this work? <break time='0.3s'/> A rectangle has two equal lengths and two equal widths. <break time='0.3s'/> So once we know the perimeter and one of them, simple algebra gives us the other. <break time='0.3s'/> A square has four equal sides, so its side is simply the perimeter divided by four.<break time='0.5s'/>") as tracker:
            self.wait_until_bookmark("why_works")
            
            # Rectangle with labeled sides
            rect2 = Rectangle(width=3, height=1.8, color=PURPLE, stroke_width=3).shift(UP*1)
            self.play(Create(rect2))
            
            # Label sides
            top_side = Line(rect2.get_corner(UL), rect2.get_corner(UR), color=ORANGE_HL, stroke_width=5)
            bottom_side = Line(rect2.get_corner(DL), rect2.get_corner(DR), color=ORANGE_HL, stroke_width=5)
            left_side = Line(rect2.get_corner(UL), rect2.get_corner(DL), color=PURPLE, stroke_width=5)
            right_side = Line(rect2.get_corner(UR), rect2.get_corner(DR), color=PURPLE, stroke_width=5)
            
            l_label1 = MathTex("l", font_size=28, color=ORANGE_HL).next_to(top_side, UP, buff=0.1)
            l_label2 = MathTex("l", font_size=28, color=ORANGE_HL).next_to(bottom_side, DOWN, buff=0.1)
            w_label1 = MathTex("w", font_size=28, color=PURPLE).next_to(left_side, LEFT, buff=0.1)
            w_label2 = MathTex("w", font_size=28, color=PURPLE).next_to(right_side, RIGHT, buff=0.1)
            
            self.play(
                Create(top_side), Create(bottom_side),
                Create(left_side), Create(right_side),
                Write(l_label1), Write(l_label2),
                Write(w_label1), Write(w_label2)
            )
            
            # Show algebra
            algebra = VGroup(
                MathTex("P", "=", "l", "+", "w", "+", "l", "+", "w", font_size=30, color=PURPLE),
                MathTex("P", "=", "2l", "+", "2w", font_size=30, color=PURPLE),
                MathTex("P", "=", "2", "(", "l", "+", "w", ")", font_size=30, color=PURPLE)
            ).arrange(DOWN, buff=0.3).shift(DOWN*1.5)
            
            for eq in algebra:
                eq[0].set_color(ORANGE_HL)
            
            self.play(Write(algebra[0]))
            self.wait(0.3)
            self.play(TransformMatchingTex(algebra[0].copy(), algebra[1]))
            self.wait(0.3)
            self.play(TransformMatchingTex(algebra[1].copy(), algebra[2]))
        
        self.play(FadeOut(VGroup(rect2, top_side, bottom_side, left_side, right_side, l_label1, l_label2, w_label1, w_label2, algebra)))
        
        # Segment 4: Problem statement
        with self.voiceover(text="<bookmark mark='question'/>Question: Part 1: The perimeter of a rectangular notebook is 34 centimetres. <break time='0.3s'/> Its length is 11 centimetres. <break time='0.3s'/> Find its width and check whether two such notebooks would fit along a 24-centimetre shelf. <break time='0.4s'/> Part 2: A square tile has a perimeter of 48 centimetres. <break time='0.3s'/> Find the length of one side.<break time='0.5s'/>") as tracker:
            self.wait_until_bookmark("question")
            
            # Notebook
            notebook = Rectangle(width=2.2, height=1.2, color=PURPLE, fill_opacity=0.15, stroke_width=3).shift(LEFT*3.5 + UP*1)
            
            # Perimeter label around notebook
            perim_label = Text("P = 34 cm", font="Poppins", font_size=24, color=ORANGE_HL).next_to(notebook, UP, buff=0.3)
            length_brace = BraceBetweenPoints(notebook.get_corner(DL), notebook.get_corner(DR), direction=DOWN, color=PURPLE)
            length_label = MathTex("l = 11", "\\text{ cm}", font_size=24, color=PURPLE).next_to(length_brace, DOWN, buff=0.1)
            width_brace = BraceBetweenPoints(notebook.get_corner(DR), notebook.get_corner(UR), direction=RIGHT, color=ORANGE_HL)
            width_label = MathTex("w = ?", font_size=24, color=ORANGE_HL).next_to(width_brace, RIGHT, buff=0.1)
            
            self.play(Create(notebook), Write(perim_label))
            self.play(Create(length_brace), Write(length_label))
            self.play(Create(width_brace), Write(width_label))
            
            # Shelf
            shelf = Line(LEFT*2, RIGHT*2, color=PURPLE, stroke_width=4).shift(DOWN*1)
            shelf_brace = BraceBetweenPoints(shelf.get_start(), shelf.get_end(), direction=DOWN, color=PURPLE)
            shelf_label = Text("24 cm", font="Poppins", font_size=22, color=PURPLE).next_to(shelf_brace, DOWN, buff=0.1)
            self.play(Create(shelf), Create(shelf_brace), Write(shelf_label))
            
            # Tile
            tile = Square(side_length=1.5, color=PURPLE, fill_opacity=0.15, stroke_width=3).shift(RIGHT*3.5 + UP*1)
            tile_perim = Text("P = 48 cm", font="Poppins", font_size=24, color=ORANGE_HL).next_to(tile, UP, buff=0.3)
            tile_side_brace = BraceBetweenPoints(tile.get_corner(DL), tile.get_corner(DR), direction=DOWN, color=PURPLE)
            tile_side_label = MathTex("s = ?", font_size=24, color=ORANGE_HL).next_to(tile_side_brace, DOWN, buff=0.1)
            
            self.play(Create(tile), Write(tile_perim))
            self.play(Create(tile_side_brace), Write(tile_side_label))
        
        self.play(FadeOut(VGroup(notebook, perim_label, length_brace, length_label, width_brace, width_label, shelf, shelf_brace, shelf_label, tile, tile_perim, tile_side_brace, tile_side_label)))
        
        # Segment 5: Solution Part 1 - Notebook
        with self.voiceover(text="<bookmark mark='solution_notebook'/>Solution: For the notebook: Two times the sum of length and width equals the perimeter. <break time='0.3s'/> Two times eleven plus width equals thirty-four. <break time='0.3s'/> Eleven plus width equals seventeen. <break time='0.3s'/> So width equals six centimetres. <break time='0.3s'/> Two notebooks placed side by side would need twelve centimetres, which fits well on the shelf.<break time='0.5s'/>") as tracker:
            self.wait_until_bookmark("solution_notebook")
            
            title = Text("Notebook Solution", font="Poppins", font_size=32, color=PURPLE).to_edge(UP, buff=0.3)
            self.play(Write(title))
            
            # Equation steps
            eq1 = MathTex("2", "(", "l", "+", "w", ")", "=", "P", font_size=36, color=PURPLE).shift(UP*1.5)
            eq1[7].set_color(ORANGE_HL)
            self.play(Write(eq1))
            self.wait(0.5)
            
            eq2 = MathTex("2", "(", "11", "+", "w", ")", "=", "34", font_size=36, color=PURPLE).shift(UP*0.5)
            eq2[2].set_color(ORANGE_HL)
            eq2[7].set_color(ORANGE_HL)
            self.play(TransformMatchingTex(eq1.copy(), eq2))
            self.wait(0.5)
            
            eq3 = MathTex("11", "+", "w", "=", "17", font_size=36, color=PURPLE).shift(DOWN*0.5)
            eq3[4].set_color(ORANGE_HL)
            self.play(TransformMatchingTex(eq2.copy(), eq3))
            self.wait(0.5)
            
            eq4 = MathTex("w", "=", "6", "\\text{ cm}", font_size=36, color=PURPLE).shift(DOWN*1.5)
            eq4[2].set_color(ORANGE_HL)
            self.play(TransformMatchingTex(eq3.copy(), eq4))
            
            # Box the answer
            answer_box = SurroundingRectangle(eq4, color=ORANGE_HL, buff=0.2, corner_radius=0.1)
            self.play(Create(answer_box))
            self.wait(0.5)
        
        self.play(FadeOut(VGroup(title, eq1, eq2, eq3, eq4, answer_box)))
        
        # Show two notebooks on shelf
        with self.voiceover(text="") as tracker:
            shelf2 = Line(LEFT*3, RIGHT*3, color=PURPLE, stroke_width=4).shift(DOWN*0.5)
            shelf_brace2 = BraceBetweenPoints(shelf2.get_start(), shelf2.get_end(), direction=DOWN, color=PURPLE)
            shelf_label2 = Text("24 cm", font="Poppins", font_size=24, color=PURPLE).next_to(shelf_brace2, DOWN, buff=0.1)
            
            self.play(Create(shelf2), Create(shelf_brace2), Write(shelf_label2))
            
            notebook1 = Rectangle(width=1.1, height=0.6, color=PURPLE, fill_opacity=0.2, stroke_width=3).move_to(shelf2.get_center() + LEFT*0.55)
            notebook2 = Rectangle(width=1.1, height=0.6, color=PURPLE, fill_opacity=0.2, stroke_width=3).move_to(shelf2.get_center() + RIGHT*0.55)
            
            nb1_brace = BraceBetweenPoints(notebook1.get_corner(DL) + DOWN*0.1, notebook1.get_corner(DR) + DOWN*0.1, direction=DOWN, color=ORANGE_HL)
            nb1_label = Text("6 cm", font="Poppins", font_size=20, color=ORANGE_HL).next_to(nb1_brace, DOWN, buff=0.05)
            
            nb2_brace = BraceBetweenPoints(notebook2.get_corner(DL) + DOWN*0.1, notebook2.get_corner(DR) + DOWN*0.1, direction=DOWN, color=ORANGE_HL)
            nb2_label = Text("6 cm", font="Poppins", font_size=20, color=ORANGE_HL).next_to(nb2_brace, DOWN, buff=0.05)
            
            self.play(FadeIn(notebook1), FadeIn(notebook2))
            self.play(Create(nb1_brace), Write(nb1_label), Create(nb2_brace), Write(nb2_label))
            
            total_brace = BraceBetweenPoints(
                notebook1.get_corner(DL) + LEFT*0.1,
                notebook2.get_corner(DR) + RIGHT*0.1,
                direction=UP, color=ORANGE_HL
            ).shift(UP*0.8)
            total_label = Text("12 cm < 24 cm ✓", font="Poppins", font_size=24, color=ORANGE_HL).next_to(total_brace, UP, buff=0.1)
            self.play(Create(total_brace), Write(total_label))
            self.wait(1)
        
        self.play(FadeOut(VGroup(shelf2, shelf_brace2, shelf_label2, notebook1, notebook2, nb1_brace, nb1_label, nb2_brace, nb2_label, total_brace, total_label)))
        
        # Segment 6: Solution Part 2 - Tile
        with self.voiceover(text="<bookmark mark='solution_tile'/>For the tile: The perimeter equals four times the side. <break time='0.3s'/> Four times the side equals forty-eight. <break time='0.3s'/> So the side equals twelve centimetres. <break time='0.3s'/> This is the same idea builders use when calculating tile sizes for a floor.<break time='0.5s'/>") as tracker:
            self.wait_until_bookmark("solution_tile")
            
            title2 = Text("Tile Solution", font="Poppins", font_size=32, color=PURPLE).to_edge(UP, buff=0.3)
            self.play(Write(title2))
            
            # Tile equations
            tile_eq1 = MathTex("P", "=", "4", "s", font_size=36, color=PURPLE).shift(UP*1)
            tile_eq1[0].set_color(ORANGE_HL)
            self.play(Write(tile_eq1))
            self.wait(0.5)
            
            tile_eq2 = MathTex("4", "s", "=", "48", font_size=36, color=PURPLE).shift(UP*0)
            tile_eq2[3].set_color(ORANGE_HL)
            self.play(TransformMatchingTex(tile_eq1.copy(), tile_eq2))
            self.wait(0.5)
            
            tile_eq3 = MathTex("s", "=", "12", "\\text{ cm}", font_size=36, color=PURPLE).shift(DOWN*1)
            tile_eq3[2].set_color(ORANGE_HL)
            self.play(TransformMatchingTex(tile_eq2.copy(), tile_eq3))
            
            tile_answer_box = SurroundingRectangle(tile_eq3, color=ORANGE_HL, buff=0.2, corner_radius=0.1)
            self.play(Create(tile_answer_box))
            self.wait(0.5)
        
        self.play(FadeOut(VGroup(title2, tile_eq1, tile_eq2, tile_eq3, tile_answer_box)))
        
        # Builder scene with tiles
        with self.voiceover(text="") as tracker:
            floor_grid = VGroup()
            for i in range(4):
                for j in range(3):
                    tile_square = Square(side_length=0.8, color=PURPLE, stroke_width=2, fill_opacity=0.1).move_to(
                        LEFT*2.4 + UP*1.2 + RIGHT*i*0.8 + DOWN*j*0.8
                    )
                    floor_grid.add(tile_square)
            
            builder_text = Text("Builder's Application", font="Poppins", font_size=28, color=PURPLE).to_edge(UP, buff=0.3)
            self.play(Write(builder_text))
            self.play(LaggedStart(*[FadeIn(tile) for tile in floor_grid], lag_ratio=0.05))
            
            sample_tile = floor_grid[0].copy().set_color(ORANGE_HL).set_stroke(width=4)
            tile_dim = Text("12 cm", font="Poppins", font_size=20, color=ORANGE_HL).next_to(sample_tile, DOWN, buff=0.2)
            self.play(sample_tile.animate.scale(1.2), Write(tile_dim))
            self.wait(1)
        
        self.play(FadeOut(VGroup(floor_grid, builder_text, sample_tile, tile_dim)))
        
        # Segment 7: Summary
        with self.voiceover(text="<bookmark mark='summary'/>Summary: Perimeter formulas can be rearranged to find missing dimensions. <break time='0.3s'/> Rectangle: perimeter is two times the sum of length and width. <break time='0.3s'/> Square: side is the perimeter divided by four.") as tracker:
            self.wait_until_bookmark("summary")
            
            summary_title = Text("Summary", font="Poppins", font_size=38, color=PURPLE).to_edge(UP, buff=0.5)
            self.play(Write(summary_title))
            
            # Summary points with icons
            rect_icon = Rectangle(width=1.2, height=0.7, color=PURPLE, stroke_width=3).shift(LEFT*4 + UP*0.5)
            rect_formula_sum = MathTex("P", "=", "2", "(", "l", "+", "w", ")", font_size=30, color=PURPLE).next_to(rect_icon, RIGHT, buff=0.3)
            rect_formula_sum[0].set_color(ORANGE_HL)
            
            square_icon = Square(side_length=0.8, color=PURPLE, stroke_width=3).shift(LEFT*4 + DOWN*1.2)
            square_formula_sum = MathTex("s", "=", "\\frac{P}{4}", font_size=30, color=PURPLE).next_to(square_icon, RIGHT, buff=0.3)
            square_formula_sum[2].set_color(ORANGE_HL)
            
            self.play(Create(rect_icon), Write(rect_formula_sum))
            self.wait(0.5)
            self.play(Create(square_icon), Write(square_formula_sum))
            self.wait(0.5)
            
            # Pulse emphasis
            self.play(
                rect_formula_sum.animate.scale(1.1).set_color(ORANGE_HL),
                rate_func=there_and_back,
                run_time=0.8
            )
            self.play(
                square_formula_sum.animate.scale(1.1).set_color(ORANGE_HL),
                rate_func=there_and_back,
                run_time=0.8
            )
            
            self.wait(2)