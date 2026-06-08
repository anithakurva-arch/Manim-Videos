import os
os.environ["OPENAI_API_KEY"] = "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"
from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.openai import OpenAIService

class PerimeterAndAreaScene(VoiceoverScene):
    def construct(self):
        self.camera.background_color = "#E7E5F3"
        self.set_speech_service(OpenAIService(voice="shimmer", model="gpt-4o-mini-tts"))

        # Colors
        PURPLE = "#7464CE"
        ORANGE_HL = "#FF9302"
        LAVENDER_BG = "#E7E5F3"

        # Title Card
        with self.voiceover(text="<bookmark mark='intro'/>Hello students! Imagine you are arranging chairs around a rectangular classroom table. <bookmark mark='chairs_context'/>You know the total number of chairs that fit around it, and you know how many fit along one side. <bookmark mark='question_hook'/>Could you figure out how many fit along the other side without counting again?") as tracker:
            title = Text("Finding Missing Dimensions", font="Poppins", color=PURPLE, font_size=48)
            subtitle = Text("Using Perimeter", font="Poppins", color=PURPLE, font_size=32)
            subtitle.next_to(title, DOWN)
            
            self.play(FadeIn(title))
            self.play(Write(subtitle))
            self.wait(1)
            
            self.wait_until_bookmark("intro")
            self.play(FadeOut(title), FadeOut(subtitle))
            
            # Table with chairs
            table = Rectangle(width=5, height=3, color=PURPLE, stroke_width=4)
            chairs = VGroup()
            for i in range(6):
                chair = Circle(radius=0.2, color=PURPLE, fill_opacity=0.5)
                chair.move_to(table.get_top() + DOWN*0.3 + RIGHT*(i-2.5)*0.8)
                chairs.add(chair)
            for i in range(6):
                chair = Circle(radius=0.2, color=PURPLE, fill_opacity=0.5)
                chair.move_to(table.get_bottom() + UP*0.3 + RIGHT*(i-2.5)*0.8)
                chairs.add(chair)
            for i in range(3):
                chair = Circle(radius=0.2, color=PURPLE, fill_opacity=0.5)
                chair.move_to(table.get_left() + RIGHT*0.3 + UP*(i-1)*1.2)
                chairs.add(chair)
            for i in range(3):
                chair = Circle(radius=0.2, color=PURPLE, fill_opacity=0.5)
                chair.move_to(table.get_right() + LEFT*0.3 + UP*(i-1)*1.2)
                chairs.add(chair)
            
            self.play(Create(table))
            self.play(LaggedStart(*[FadeIn(chair) for chair in chairs], lag_ratio=0.05))
            
            self.wait_until_bookmark("chairs_context")
            # Highlight one side
            top_side = Line(table.get_corner(UL), table.get_corner(UR), color=ORANGE_HL, stroke_width=6)
            known_label = Text("Known", font="Poppins", color=ORANGE_HL, font_size=24)
            known_label.next_to(top_side, UP, buff=0.3)
            self.play(Create(top_side), Write(known_label))
            
            # Question marks on other sides
            qm_left = Text("?", font="Poppins", color=WHITE, font_size=32)
            qm_left.next_to(table.get_left(), LEFT)
            qm_right = Text("?", font="Poppins", color=WHITE, font_size=32)
            qm_right.next_to(table.get_right(), RIGHT)
            self.play(Write(qm_left), Write(qm_right))
            
            self.wait_until_bookmark("question_hook")
            self.play(Indicate(qm_right, scale_factor=1.5))
            self.play(Transform(qm_right, known_label.copy().next_to(table.get_right(), RIGHT)))
            self.wait(1)
            
            self.play(FadeOut(VGroup(table, chairs, top_side, known_label, qm_left, qm_right)))

        # Core concept - Perimeter definition
        with self.voiceover(text="<bookmark mark='perimeter_definition'/>The perimeter is the total length around a shape. <bookmark mark='rectangle_formula'/>For a rectangle, the perimeter equals 2 times the sum of length and width. <bookmark mark='square_formula'/>For a square, the perimeter equals 4 times the length of one side. <bookmark mark='rearrange'/>So if we know the perimeter and one dimension, we can rearrange the formula and find the missing one. <bookmark mark='backwards_tool'/>This means perimeter is not just for measuring — it is also a tool to work backwards.") as tracker:
            
            self.wait_until_bookmark("perimeter_definition")
            rect1 = Rectangle(width=4, height=2.5, color=PURPLE, stroke_width=4)
            
            # Trace perimeter
            perimeter_trace = rect1.copy().set_color(ORANGE_HL).set_stroke(width=6)
            self.play(Create(rect1))
            self.play(Create(perimeter_trace, run_time=2))
            self.wait(0.5)
            
            self.wait_until_bookmark("rectangle_formula")
            # Labels for rectangle
            l_label = MathTex("L", color=PURPLE, font_size=36)
            l_label.next_to(rect1.get_top(), UP, buff=0.2)
            w_label = MathTex("W", color=PURPLE, font_size=36)
            w_label.next_to(rect1.get_right(), RIGHT, buff=0.2)
            
            rect_formula = MathTex("P", "=", "2", "(", "L", "+", "W", ")", color=PURPLE, font_size=40)
            rect_formula.next_to(rect1, DOWN, buff=0.8)
            
            self.play(Write(l_label), Write(w_label))
            self.play(Write(rect_formula))
            self.wait(1)
            
            self.wait_until_bookmark("square_formula")
            # Move rectangle to left
            rect_group = VGroup(rect1, perimeter_trace, l_label, w_label, rect_formula)
            self.play(rect_group.animate.shift(LEFT*3))
            
            # Square
            square1 = Square(side_length=2.5, color=PURPLE, stroke_width=4)
            square1.shift(RIGHT*3)
            s_labels = VGroup()
            for direction, pos in [(UP, square1.get_top()), (RIGHT, square1.get_right())]:
                s_label = MathTex("S", color=PURPLE, font_size=36)
                s_label.next_to(pos, direction, buff=0.2)
                s_labels.add(s_label)
            
            square_formula = MathTex("P", "=", "4", "S", color=PURPLE, font_size=40)
            square_formula.next_to(square1, DOWN, buff=0.8)
            
            self.play(Create(square1))
            self.play(Write(s_labels))
            self.play(Write(square_formula))
            self.wait(1)
            
            self.wait_until_bookmark("rearrange")
            # Highlight known values
            rect_formula_highlight = MathTex("P", "=", "2", "(", "L", "+", "W", ")", color=PURPLE, font_size=40)
            rect_formula_highlight.move_to(rect_formula)
            rect_formula_highlight[0].set_color(ORANGE_HL)
            rect_formula_highlight[4].set_color(ORANGE_HL)
            
            rearranged = MathTex("W", "=", "\\frac{P}{2}", "-", "L", color=PURPLE, font_size=40)
            rearranged.next_to(rect_formula, DOWN, buff=0.5)
            
            self.play(Transform(rect_formula, rect_formula_highlight))
            self.play(Write(rearranged))
            
            self.wait_until_bookmark("backwards_tool")
            arrow_back = Arrow(rearranged.get_right(), rearranged.get_right() + RIGHT*1.5, color=ORANGE_HL)
            back_text = Text("Work Backwards", font="Poppins", color=ORANGE_HL, font_size=24)
            back_text.next_to(arrow_back, RIGHT)
            self.play(GrowArrow(arrow_back), Write(back_text))
            self.play(Indicate(back_text))
            self.wait(1)
            
            self.play(FadeOut(VGroup(rect_group, square1, s_labels, square_formula, rearranged, arrow_back, back_text)))

        # Explanation - Why it works
        with self.voiceover(text="<bookmark mark='why_works'/>Now, why does this work? <bookmark mark='rectangle_structure'/>A rectangle has 2 equal lengths and 2 equal widths. <bookmark mark='algebra_gives'/>So once we know the perimeter and one of them, simple algebra gives us the other. <bookmark mark='square_structure'/>A square has 4 equal sides, so its side is simply the perimeter divided by 4.") as tracker:
            
            self.wait_until_bookmark("why_works")
            why_text = Text("Why?", font="Poppins", color=PURPLE, font_size=60)
            self.play(Write(why_text))
            self.wait(0.5)
            self.play(FadeOut(why_text))
            
            self.wait_until_bookmark("rectangle_structure")
            rect2 = Rectangle(width=4, height=2.5, color=PURPLE, stroke_width=4)
            self.play(Create(rect2))
            
            # Highlight pairs
            top_bottom = VGroup(
                Line(rect2.get_corner(UL), rect2.get_corner(UR), color=ORANGE_HL, stroke_width=6),
                Line(rect2.get_corner(DL), rect2.get_corner(DR), color=ORANGE_HL, stroke_width=6)
            )
            left_right = VGroup(
                Line(rect2.get_corner(UL), rect2.get_corner(DL), color="#00FF00", stroke_width=6),
                Line(rect2.get_corner(UR), rect2.get_corner(DR), color="#00FF00", stroke_width=6)
            )
            
            self.play(Create(top_bottom))
            self.wait(0.3)
            self.play(Create(left_right))
            self.wait(1)
            
            self.wait_until_bookmark("algebra_gives")
            # Show algebraic steps
            algebra_steps = VGroup(
                MathTex("P", "=", "2", "(", "L", "+", "W", ")", color=PURPLE, font_size=36),
                MathTex("\\frac{P}{2}", "=", "L", "+", "W", color=PURPLE, font_size=36),
                MathTex("W", "=", "\\frac{P}{2}", "-", "L", color=PURPLE, font_size=36)
            ).arrange(DOWN, buff=0.4)
            algebra_steps.next_to(rect2, DOWN, buff=0.8)
            
            # Highlight known
            algebra_steps[0][0].set_color(ORANGE_HL)
            algebra_steps[0][4].set_color(ORANGE_HL)
            
            for step in algebra_steps:
                self.play(Write(step))
                self.wait(0.5)
            
            self.wait(1)
            self.play(FadeOut(VGroup(rect2, top_bottom, left_right, algebra_steps)))
            
            self.wait_until_bookmark("square_structure")
            square2 = Square(side_length=2.5, color=PURPLE, stroke_width=4)
            self.play(Create(square2))
            
            # Highlight all 4 sides
            four_sides = VGroup(
                Line(square2.get_corner(UL), square2.get_corner(UR), color=ORANGE_HL, stroke_width=6),
                Line(square2.get_corner(UR), square2.get_corner(DR), color=ORANGE_HL, stroke_width=6),
                Line(square2.get_corner(DR), square2.get_corner(DL), color=ORANGE_HL, stroke_width=6),
                Line(square2.get_corner(DL), square2.get_corner(UL), color=ORANGE_HL, stroke_width=6)
            )
            self.play(LaggedStart(*[Create(side) for side in four_sides], lag_ratio=0.2))
            
            square_derivation = VGroup(
                MathTex("P", "=", "4", "S", color=PURPLE, font_size=36),
                MathTex("S", "=", "\\frac{P}{4}", color=PURPLE, font_size=36)
            ).arrange(DOWN, buff=0.4)
            square_derivation.next_to(square2, DOWN, buff=0.8)
            
            for step in square_derivation:
                self.play(Write(step))
                self.wait(0.5)
            
            self.wait(1)
            self.play(FadeOut(VGroup(square2, four_sides, square_derivation)))

        # Question setup
        with self.voiceover(text="<bookmark mark='question_part1'/>Part 1: The perimeter of a rectangular notebook is 34 centimeters. <bookmark mark='given_length'/>Its length is 11 centimeters. <bookmark mark='find_width'/>Find its width and check whether 2 such notebooks would fit along a 24 centimeter shelf.") as tracker:
            
            self.wait_until_bookmark("question_part1")
            # Notebook
            notebook = Rectangle(width=3.5, height=2, color=PURPLE, stroke_width=4)
            notebook.shift(UP*1)
            
            p_label = Text("P = 34 cm", font="Poppins", color=ORANGE_HL, font_size=32)
            p_label.next_to(notebook, UP, buff=0.3)
            
            self.play(Create(notebook))
            self.play(Write(p_label))
            
            self.wait_until_bookmark("given_length")
            l_value = Text("L = 11 cm", font="Poppins", color=ORANGE_HL, font_size=28)
            l_value.next_to(notebook.get_top(), DOWN, buff=0.1)
            self.play(Write(l_value))
            
            self.wait_until_bookmark("find_width")
            w_unknown = Text("W = ?", font="Poppins", color=WHITE, font_size=28)
            w_unknown.next_to(notebook.get_right(), RIGHT, buff=0.2)
            self.play(Write(w_unknown))
            
            # Shelf
            shelf = Line(LEFT*3, RIGHT*3, color=PURPLE, stroke_width=6)
            shelf.shift(DOWN*2)
            shelf_label = Text("Shelf: 24 cm", font="Poppins", color=PURPLE, font_size=28)
            shelf_label.next_to(shelf, DOWN, buff=0.2)
            self.play(Create(shelf), Write(shelf_label))
            self.wait(1)
            
            question1_group = VGroup(notebook, p_label, l_value, w_unknown, shelf, shelf_label)

        with self.voiceover(text="<bookmark mark='question_part2'/>Part 2: A square tile has a perimeter of 48 centimeters. <bookmark mark='find_side'/>Find the length of one side.") as tracker:
            
            self.wait_until_bookmark("question_part2")
            self.play(question1_group.animate.shift(LEFT*4).scale(0.7))
            
            # Tile
            tile = Square(side_length=2.5, color=PURPLE, stroke_width=4)
            tile.shift(RIGHT*3 + UP*1)
            
            tile_p_label = Text("P = 48 cm", font="Poppins", color=ORANGE_HL, font_size=32)
            tile_p_label.next_to(tile, UP, buff=0.3)
            
            self.play(Create(tile))
            self.play(Write(tile_p_label))
            
            self.wait_until_bookmark("find_side")
            s_unknown = Text("S = ?", font="Poppins", color=WHITE, font_size=28)
            s_unknown.next_to(tile, RIGHT, buff=0.3)
            self.play(Write(s_unknown))
            self.wait(1)
            
            question2_group = VGroup(tile, tile_p_label, s_unknown)
            self.play(FadeOut(question1_group), FadeOut(question2_group))

        # Solution Part 1
        with self.voiceover(text="<bookmark mark='solution_notebook'/>For the notebook: <bookmark mark='formula_statement'/>2 times the sum of length and width equals the perimeter. <bookmark mark='substitute'/>2 times, 11 plus width, equals 34. <bookmark mark='simplify'/>11 plus width equals 17. <bookmark mark='width_result'/>So width equals 6 centimeters. <bookmark mark='shelf_check'/>2 notebooks placed side by side would need 12 centimeters, which fits well on the shelf.") as tracker:
            
            self.wait_until_bookmark("solution_notebook")
            solution_header = Text("Solution - Part 1", font="Poppins", color=PURPLE, font_size=40)
            solution_header.to_edge(UP)
            self.play(Write(solution_header))
            
            # Recreate notebook
            notebook2 = Rectangle(width=3.5, height=2, color=PURPLE, stroke_width=4)
            notebook2.shift(UP*0.5)
            self.play(Create(notebook2))
            
            self.wait_until_bookmark("formula_statement")
            step1 = MathTex("2", "(", "L", "+", "W", ")", "=", "P", color=PURPLE, font_size=38)
            step1.next_to(notebook2, DOWN, buff=0.8)
            self.play(Write(step1))
            
            self.wait_until_bookmark("substitute")
            step2 = MathTex("2", "(", "11", "+", "W", ")", "=", "34", color=PURPLE, font_size=38)
            step2.move_to(step1)
            step2[2].set_color(ORANGE_HL)
            step2[7].set_color(ORANGE_HL)
            self.play(Transform(step1, step2))
            
            self.wait_until_bookmark("simplify")
            step3 = MathTex("11", "+", "W", "=", "17", color=PURPLE, font_size=38)
            step3.next_to(step1, DOWN, buff=0.4)
            self.play(Write(step3))
            
            self.wait_until_bookmark("width_result")
            step4 = MathTex("W", "=", "6", "\\text{ cm}", color=PURPLE, font_size=38)
            step4.next_to(step3, DOWN, buff=0.4)
            step4[2].set_color(ORANGE_HL)
            self.play(Write(step4))
            
            # Update notebook with width
            w_value_final = Text("W = 6 cm", font="Poppins", color=ORANGE_HL, font_size=28)
            w_value_final.next_to(notebook2.get_right(), RIGHT, buff=0.2)
            self.play(Write(w_value_final))
            
            self.wait_until_bookmark("shelf_check")
            self.play(FadeOut(VGroup(step1, step3, step4)))
            
            # Two notebooks
            nb1 = Rectangle(width=1.5, height=2, color=PURPLE, stroke_width=4)
            nb2 = Rectangle(width=1.5, height=2, color=PURPLE, stroke_width=4)
            nb1.next_to(ORIGIN, LEFT, buff=0)
            nb2.next_to(ORIGIN, RIGHT, buff=0)
            notebooks_group = VGroup(nb1, nb2)
            notebooks_group.shift(DOWN*1.5)
            
            width_calc = MathTex("6", "+", "6", "=", "12", "\\text{ cm}", color=PURPLE, font_size=32)
            width_calc.next_to(notebooks_group, DOWN, buff=0.5)
            width_calc[4].set_color(ORANGE_HL)
            
            self.play(FadeOut(notebook2), FadeOut(w_value_final))
            self.play(Create(notebooks_group))
            self.play(Write(width_calc))
            
            # Shelf comparison
            shelf2 = Line(LEFT*3, RIGHT*3, color=PURPLE, stroke_width=6)
            shelf2.next_to(width_calc, DOWN, buff=0.5)
            shelf_label2 = Text("Shelf: 24 cm ✓", font="Poppins", color="#00FF00", font_size=28)
            shelf_label2.next_to(shelf2, DOWN, buff=0.2)
            
            self.play(Create(shelf2), Write(shelf_label2))
            self.wait(1)
            
            self.play(FadeOut(VGroup(solution_header, notebooks_group, width_calc, shelf2, shelf_label2)))

        # Solution Part 2
        with self.voiceover(text="<bookmark mark='solution_tile'/>For the tile: <bookmark mark='tile_formula'/>The perimeter equals 4 times the side. <bookmark mark='tile_substitute'/>4 times the side equals 48. <bookmark mark='tile_result'/>So the side equals 12 centimeters. <bookmark mark='real_world'/>This is the same idea builders use when calculating tile sizes for a floor.") as tracker:
            
            self.wait_until_bookmark("solution_tile")
            solution_header2 = Text("Solution - Part 2", font="Poppins", color=PURPLE, font_size=40)
            solution_header2.to_edge(UP)
            self.play(Write(solution_header2))
            
            # Recreate tile
            tile2 = Square(side_length=2.5, color=PURPLE, stroke_width=4)
            tile2.shift(UP*0.5)
            self.play(Create(tile2))
            
            self.wait_until_bookmark("tile_formula")
            tile_step1 = MathTex("P", "=", "4", "S", color=PURPLE, font_size=38)
            tile_step1.next_to(tile2, DOWN, buff=0.8)
            self.play(Write(tile_step1))
            
            self.wait_until_bookmark("tile_substitute")
            tile_step2 = MathTex("4", "S", "=", "48", color=PURPLE, font_size=38)
            tile_step2.next_to(tile_step1, DOWN, buff=0.4)
            tile_step2[3].set_color(ORANGE_HL)
            self.play(Write(tile_step2))
            
            self.wait_until_bookmark("tile_result")
            tile_step3 = MathTex("S", "=", "12", "\\text{ cm}", color=PURPLE, font_size=38)
            tile_step3.next_to(tile_step2, DOWN, buff=0.4)
            tile_step3[2].set_color(ORANGE_HL)
            self.play(Write(tile_step3))
            
            # Update tile
            s_labels_final = VGroup()
            for direction, pos in [(UP, tile2.get_top()), (RIGHT, tile2.get_right()), 
                                   (DOWN, tile2.get_bottom()), (LEFT, tile2.get_left())]:
                s_final = Text("12 cm", font="Poppins", color=ORANGE_HL, font_size=20)
                s_final.next_to(pos, direction, buff=0.15)
                s_labels_final.add(s_final)
            self.play(Write(s_labels_final))
            
            self.wait_until_bookmark("real_world")
            # Builder context
            builder_icon = Text("🏗️", font="Poppins", font_size=48)
            builder_icon.to_edge(LEFT).shift(DOWN*1.5)
            
            floor_tiles = VGroup()
            for i in range(3):
                for j in range(3):
                    small_tile = Square(side_length=0.5, color=PURPLE, stroke_width=2)
                    small_tile.move_to(RIGHT*2 + DOWN*1.5 + RIGHT*i*0.5 + UP*j*0.5)
                    floor_tiles.add(small_tile)
            
            self.play(FadeIn(builder_icon))
            self.play(LaggedStart(*[Create(t) for t in floor_tiles], lag_ratio=0.05))
            self.wait(1.5)
            
            self.play(FadeOut(VGroup(solution_header2, tile2, tile_step1, tile_step2, tile_step3, 
                                     s_labels_final, builder_icon, floor_tiles)))

        # Summary
        with self.voiceover(text="<bookmark mark='summary'/>Perimeter formulas can be rearranged to find missing dimensions. <bookmark mark='summary_rectangle'/>Rectangle: perimeter is 2 times the sum of length and width. <bookmark mark='summary_square'/>Square: side is the perimeter divided by 4.") as tracker:
            
            self.wait_until_bookmark("summary")
            summary_title = Text("Summary", font="Poppins", color=PURPLE, font_size=48)
            summary_title.to_edge(UP)
            self.play(Write(summary_title))
            
            bullet1 = Text("• Perimeter formulas can be rearranged\n  to find missing dimensions", 
                          font="Poppins", color=PURPLE, font_size=28, line_spacing=1.2)
            bullet1.next_to(summary_title, DOWN, buff=0.8)
            bullet1.to_edge(LEFT, buff=1)
            self.play(Write(bullet1))
            
            self.wait_until_bookmark("summary_rectangle")
            bullet2 = MathTex("\\text{• Rectangle: } P = 2(L + W)", color=PURPLE, font_size=32)
            bullet2.next_to(bullet1, DOWN, buff=0.5, aligned_edge=LEFT)
            self.play(Write(bullet2))
            
            self.wait_until_bookmark("summary_square")
            bullet3 = MathTex("\\text{• Square: } S = \\frac{P}{4}", color=PURPLE, font_size=32)
            bullet3.next_to(bullet2, DOWN, buff=0.5, aligned_edge=LEFT)
            self.play(Write(bullet3))
            
            self.wait(2)
            self.play(FadeOut(VGroup(summary_title, bullet1, bullet2, bullet3)))

        # Outro
        logo = Text("Coschool", font="Poppins", color=PURPLE, font_size=60)
        self.play(FadeIn(logo))
        self.wait(2)
        self.play(FadeOut(logo))