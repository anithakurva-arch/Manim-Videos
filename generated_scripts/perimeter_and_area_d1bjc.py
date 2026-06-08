import os
os.environ["OPENAI_API_KEY"] = "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"
from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.openai import OpenAIService

class PerimeterAndAreaScene(VoiceoverScene):
    def construct(self):
        self.camera.background_color = "#E7E5F3"
        service = OpenAIService(
            voice="shimmer",
            model="gpt-4o-mini-tts"
        )
        self.set_speech_service(service)
        
        # SEGMENT 1: Introduction with classroom metaphor
        with self.voiceover(text="""<bookmark mark='intro_start'/>Hello students! Imagine you are arranging chairs around a rectangular classroom table. <bookmark mark='chairs_context'/>You know the total number of chairs that fit around it, and you know how many fit along one side. <bookmark mark='question_pose'/>Could you figure out how many fit along the other side without counting again?""") as tracker:
            
            title = Text("Finding Missing Dimensions", font="Poppins", color="#7464CE", font_size=48)
            self.play(FadeIn(title))
            self.wait_until_bookmark("intro_start")
            
            self.play(FadeOut(title))
            
            # Draw table
            table = Rectangle(width=5, height=3, color="#7464CE", stroke_width=4)
            self.play(Create(table))
            
            self.wait_until_bookmark("chairs_context")
            
            # Add chairs around table
            chairs = VGroup()
            for i in range(5):
                chair_top = Square(side_length=0.3, color="#7464CE", fill_opacity=0.5)
                chair_top.move_to(table.get_top() + UP*0.4 + LEFT*2 + RIGHT*i)
                chairs.add(chair_top)
            
            for i in range(3):
                chair_right = Square(side_length=0.3, color="#7464CE", fill_opacity=0.5)
                chair_right.move_to(table.get_right() + RIGHT*0.4 + UP*1.2 + DOWN*i*0.8)
                chairs.add(chair_right)
            
            # Highlight one side
            side_label = Text("Known", font="Poppins", font_size=20, color="#7464CE")
            side_label.next_to(table.get_top(), UP, buff=0.8)
            
            self.play(Create(chairs), FadeIn(side_label))
            
            self.wait_until_bookmark("question_pose")
            
            question_mark = Text("?", font="Poppins", font_size=60, color="#FF9302")
            question_mark.move_to(table.get_right() + RIGHT*1.5)
            self.play(Write(question_mark))
            self.play(question_mark.animate.scale(1.2), rate_func=there_and_back)
            
            self.play(FadeOut(table, chairs, side_label, question_mark))
        
        # SEGMENT 2: Perimeter concepts and formulas
        with self.voiceover(text="""<bookmark mark='perimeter_def'/>The perimeter is the total length around a shape. <bookmark mark='rect_formula'/>For a rectangle, the perimeter equals 2 times the sum of length and width. <bookmark mark='square_formula'/>For a square, the perimeter equals 4 times the length of one side. <bookmark mark='rearrange'/>So if we know the perimeter and one dimension, we can rearrange the formula and find the missing one. <bookmark mark='tool'/>This means perimeter is not just for measuring — it is also a tool to work backwards.""") as tracker:
            
            self.wait_until_bookmark("perimeter_def")
            
            # Show rectangle with perimeter trace
            rect = Rectangle(width=4, height=2.5, color="#7464CE", stroke_width=4)
            rect.shift(LEFT*3)
            
            perimeter_label = Text("Perimeter", font="Poppins", font_size=28, color="#7464CE")
            perimeter_label.next_to(rect, UP)
            
            self.play(Create(rect), FadeIn(perimeter_label))
            
            # Trace perimeter
            trace = rect.copy().set_color("#FF9302").set_stroke(width=6)
            self.play(Create(trace), run_time=2)
            
            self.wait_until_bookmark("rect_formula")
            
            rect_formula = MathTex("P", "=", "2", "(", "l", "+", "w", ")", font_size=40)
            rect_formula.set_color_by_tex("P", "#7464CE")
            rect_formula.set_color_by_tex("l", "#7464CE")
            rect_formula.set_color_by_tex("w", "#7464CE")
            rect_formula.next_to(rect, DOWN, buff=0.5)
            
            self.play(Write(rect_formula))
            
            self.wait_until_bookmark("square_formula")
            
            # Show square
            square = Square(side_length=2.5, color="#7464CE", stroke_width=4)
            square.shift(RIGHT*3)
            
            square_trace = square.copy().set_color("#FF9302").set_stroke(width=6)
            
            square_formula = MathTex("P", "=", "4", "s", font_size=40)
            square_formula.set_color_by_tex("P", "#7464CE")
            square_formula.set_color_by_tex("s", "#7464CE")
            square_formula.next_to(square, DOWN, buff=0.5)
            
            self.play(Create(square), Create(square_trace), Write(square_formula))
            
            self.wait_until_bookmark("rearrange")
            
            # Show rearrangement
            rearranged = MathTex("w", "=", "\\frac{P}{2}", "-", "l", font_size=36)
            rearranged.set_color_by_tex("w", "#FF9302")
            rearranged.set_color_by_tex("P", "#7464CE")
            rearranged.set_color_by_tex("l", "#7464CE")
            rearranged.move_to(DOWN*2)
            
            arrow = Arrow(start=UP*0.5, end=DOWN*1, color="#FF9302", stroke_width=6)
            arrow.move_to(DOWN*0.5)
            
            self.play(GrowArrow(arrow), TransformFromCopy(rect_formula, rearranged))
            
            self.wait_until_bookmark("tool")
            self.wait(1)
            
            self.play(
                FadeOut(rect, trace, perimeter_label, rect_formula, square, square_trace, 
                       square_formula, rearranged, arrow)
            )
        
        # SEGMENT 3: Why it works
        with self.voiceover(text="""<bookmark mark='why'/>Now, why does this work? <bookmark mark='rect_explain'/>A rectangle has 2 equal lengths and 2 equal widths. <bookmark mark='algebra'/>So once we know the perimeter and one of them, simple algebra gives us the other. <bookmark mark='square_explain'/>A square has 4 equal sides, so its side is simply the perimeter divided by 4.""") as tracker:
            
            self.wait_until_bookmark("why")
            
            why_title = Text("Why Does This Work?", font="Poppins", font_size=36, color="#7464CE")
            why_title.to_edge(UP)
            self.play(FadeIn(why_title))
            
            self.wait_until_bookmark("rect_explain")
            
            # Show rectangle decomposition
            rect_whole = Rectangle(width=4, height=2, color="#7464CE", stroke_width=4)
            rect_whole.move_to(LEFT*2 + UP*0.5)
            
            self.play(Create(rect_whole))
            
            # Split into parts
            top_line = Line(rect_whole.get_corner(UL), rect_whole.get_corner(UR), color="#FF9302", stroke_width=5)
            bottom_line = Line(rect_whole.get_corner(DL), rect_whole.get_corner(DR), color="#FF9302", stroke_width=5)
            left_line = Line(rect_whole.get_corner(UL), rect_whole.get_corner(DL), color="#7464CE", stroke_width=5)
            right_line = Line(rect_whole.get_corner(UR), rect_whole.get_corner(DR), color="#7464CE", stroke_width=5)
            
            l_label1 = MathTex("l", font_size=32, color="#FF9302").next_to(top_line, UP, buff=0.2)
            l_label2 = MathTex("l", font_size=32, color="#FF9302").next_to(bottom_line, DOWN, buff=0.2)
            w_label1 = MathTex("w", font_size=32, color="#7464CE").next_to(left_line, LEFT, buff=0.2)
            w_label2 = MathTex("w", font_size=32, color="#7464CE").next_to(right_line, RIGHT, buff=0.2)
            
            self.play(
                Create(top_line), Create(bottom_line), Create(left_line), Create(right_line),
                FadeIn(l_label1, l_label2, w_label1, w_label2)
            )
            
            two_l = MathTex("2l", font_size=32, color="#FF9302").move_to(RIGHT*2 + UP*1)
            two_w = MathTex("2w", font_size=32, color="#7464CE").move_to(RIGHT*2 + UP*0.2)
            plus = MathTex("+", font_size=32).move_to(RIGHT*2 + UP*0.6)
            
            self.play(Write(two_l), Write(plus), Write(two_w))
            
            self.wait_until_bookmark("algebra")
            
            algebra_eq = MathTex("P", "=", "2l", "+", "2w", font_size=36)
            algebra_eq.set_color_by_tex("P", "#7464CE")
            algebra_eq.set_color_by_tex("2l", "#FF9302")
            algebra_eq.set_color_by_tex("2w", "#7464CE")
            algebra_eq.move_to(RIGHT*2 + DOWN*0.8)
            
            self.play(Write(algebra_eq))
            
            self.wait_until_bookmark("square_explain")
            
            self.play(
                FadeOut(rect_whole, top_line, bottom_line, left_line, right_line,
                       l_label1, l_label2, w_label1, w_label2, two_l, two_w, plus, algebra_eq)
            )
            
            # Show square with 4 sides
            sq = Square(side_length=2.5, color="#7464CE", stroke_width=4)
            sq.move_to(LEFT*2)
            
            self.play(Create(sq))
            
            sides = VGroup(
                Line(sq.get_corner(UL), sq.get_corner(UR), color="#FF9302", stroke_width=5),
                Line(sq.get_corner(UR), sq.get_corner(DR), color="#FF9302", stroke_width=5),
                Line(sq.get_corner(DR), sq.get_corner(DL), color="#FF9302", stroke_width=5),
                Line(sq.get_corner(DL), sq.get_corner(UL), color="#FF9302", stroke_width=5)
            )
            
            self.play(Create(sides), run_time=2)
            
            four_s = MathTex("4s", font_size=36, color="#FF9302").move_to(RIGHT*2)
            division = MathTex("s", "=", "\\frac{P}{4}", font_size=36)
            division.set_color_by_tex("s", "#FF9302")
            division.set_color_by_tex("P", "#7464CE")
            division.next_to(four_s, DOWN, buff=0.8)
            
            self.play(Write(four_s), Write(division))
            self.wait(1)
            
            self.play(FadeOut(why_title, sq, sides, four_s, division))
        
        # SEGMENT 4: Problem statement
        with self.voiceover(text="""<bookmark mark='problem_intro'/>Question: Part 1: The perimeter of a rectangular notebook is 34 centimeters. Its length is 11 centimeters. <bookmark mark='problem_task'/>Find its width and check whether 2 such notebooks would fit along a 24 centimeter shelf. <bookmark mark='part2'/>Part 2: A square tile has a perimeter of 48 centimeters. Find the length of one side.""") as tracker:
            
            self.wait_until_bookmark("problem_intro")
            
            problem_title = Text("Question", font="Poppins", font_size=40, color="#7464CE")
            problem_title.to_edge(UP)
            self.play(FadeIn(problem_title))
            
            # Part 1 setup
            notebook = Rectangle(width=3, height=1.8, color="#7464CE", stroke_width=4)
            notebook.shift(LEFT*3 + UP*0.5)
            
            p_label = MathTex("P", "=", "34", "\\text{ cm}", font_size=32)
            p_label.set_color_by_tex("P", "#7464CE")
            p_label.set_color_by_tex("34", "#FF9302")
            p_label.next_to(notebook, UP, buff=0.3)
            
            l_label = MathTex("l", "=", "11", "\\text{ cm}", font_size=32)
            l_label.set_color_by_tex("l", "#7464CE")
            l_label.set_color_by_tex("11", "#7464CE")
            l_label.next_to(notebook, DOWN, buff=0.3)
            
            w_question = MathTex("w", "=", "?", font_size=32)
            w_question.set_color_by_tex("w", "#FF9302")
            w_question.set_color_by_tex("?", "#FF9302")
            w_question.next_to(notebook, RIGHT, buff=0.5)
            
            self.play(
                Create(notebook),
                Write(p_label),
                Write(l_label),
                Write(w_question)
            )
            
            self.wait_until_bookmark("problem_task")
            
            shelf = Line(LEFT*2, RIGHT*2, color="#7464CE", stroke_width=6)
            shelf.shift(DOWN*2)
            shelf_label = MathTex("24", "\\text{ cm}", font_size=28, color="#7464CE")
            shelf_label.next_to(shelf, DOWN, buff=0.2)
            
            self.play(Create(shelf), Write(shelf_label))
            
            self.wait_until_bookmark("part2")
            
            # Part 2 setup
            tile = Square(side_length=2, color="#7464CE", stroke_width=4)
            tile.shift(RIGHT*3 + UP*0.5)
            
            tile_p = MathTex("P", "=", "48", "\\text{ cm}", font_size=32)
            tile_p.set_color_by_tex("P", "#7464CE")
            tile_p.set_color_by_tex("48", "#FF9302")
            tile_p.next_to(tile, UP, buff=0.3)
            
            tile_s = MathTex("s", "=", "?", font_size=32)
            tile_s.set_color_by_tex("s", "#FF9302")
            tile_s.set_color_by_tex("?", "#FF9302")
            tile_s.next_to(tile, DOWN, buff=0.3)
            
            self.play(
                Create(tile),
                Write(tile_p),
                Write(tile_s)
            )
            
            self.wait(1)
            self.play(
                FadeOut(problem_title, notebook, p_label, l_label, w_question, 
                       shelf, shelf_label, tile, tile_p, tile_s)
            )
        
        # SEGMENT 5: Solutions
        with self.voiceover(text="""<bookmark mark='solution_start'/>Solution: For the notebook: <bookmark mark='eq1'/>2 times the sum of length and width equals the perimeter. <bookmark mark='eq2'/>2 times 11 plus width equals 34. <bookmark mark='eq3'/>11 plus width equals 17. <bookmark mark='answer1'/>So width equals 6 centimeters. <bookmark mark='shelf_check'/>Two notebooks placed side by side would need 12 centimeters, which fits well on the shelf.""") as tracker:
            
            self.wait_until_bookmark("solution_start")
            
            solution_title = Text("Solution", font="Poppins", font_size=40, color="#7464CE")
            solution_title.to_edge(UP)
            self.play(FadeIn(solution_title))
            
            part1_label = Text("Part 1: Notebook", font="Poppins", font_size=28, color="#7464CE")
            part1_label.next_to(solution_title, DOWN, buff=0.5)
            self.play(FadeIn(part1_label))
            
            self.wait_until_bookmark("eq1")
            
            eq1 = MathTex("2", "(", "l", "+", "w", ")", "=", "P", font_size=36)
            eq1.set_color_by_tex("l", "#7464CE")
            eq1.set_color_by_tex("w", "#FF9302")
            eq1.set_color_by_tex("P", "#7464CE")
            eq1.move_to(UP*1.2)
            
            self.play(Write(eq1))
            
            self.wait_until_bookmark("eq2")
            
            eq2 = MathTex("2", "(", "11", "+", "w", ")", "=", "34", font_size=36)
            eq2.set_color_by_tex("11", "#7464CE")
            eq2.set_color_by_tex("w", "#FF9302")
            eq2.set_color_by_tex("34", "#7464CE")
            eq2.move_to(UP*0.4)
            
            self.play(TransformFromCopy(eq1, eq2))
            
            self.wait_until_bookmark("eq3")
            
            eq3 = MathTex("11", "+", "w", "=", "17", font_size=36)
            eq3.set_color_by_tex("11", "#7464CE")
            eq3.set_color_by_tex("w", "#FF9302")
            eq3.set_color_by_tex("17", "#7464CE")
            eq3.move_to(DOWN*0.4)
            
            self.play(TransformFromCopy(eq2, eq3))
            
            self.wait_until_bookmark("answer1")
            
            eq4 = MathTex("w", "=", "6", "\\text{ cm}", font_size=36)
            eq4.set_color_by_tex("w", "#FF9302")
            eq4.set_color_by_tex("6", "#FF9302")
            eq4.move_to(DOWN*1.2)
            
            self.play(TransformFromCopy(eq3, eq4))
            
            # Highlight answer
            answer_box = SurroundingRectangle(eq4, color="#FF9302", buff=0.15, stroke_width=3)
            self.play(Create(answer_box))
            
            self.wait_until_bookmark("shelf_check")
            
            self.play(FadeOut(eq1, eq2, eq3, eq4, answer_box, part1_label))
            
            # Shelf visualization
            shelf_viz = Line(LEFT*4, RIGHT*4, color="#7464CE", stroke_width=8)
            shelf_viz.shift(DOWN*1.5)
            
            shelf_measurement = MathTex("24", "\\text{ cm}", font_size=32, color="#7464CE")
            shelf_measurement.next_to(shelf_viz, DOWN, buff=0.3)
            
            self.play(Create(shelf_viz), Write(shelf_measurement))
            
            notebook1 = Rectangle(width=2.2, height=1.2, color="#7464CE", stroke_width=3, fill_opacity=0.3, fill_color="#7464CE")
            notebook1.move_to(shelf_viz.get_left() + RIGHT*1.1 + UP*0.8)
            
            notebook2 = Rectangle(width=2.2, height=1.2, color="#7464CE", stroke_width=3, fill_opacity=0.3, fill_color="#7464CE")
            notebook2.move_to(notebook1.get_right() + RIGHT*1.1)
            
            w1_label = MathTex("6", "\\text{ cm}", font_size=24, color="#FF9302")
            w1_label.move_to(notebook1)
            
            w2_label = MathTex("6", "\\text{ cm}", font_size=24, color="#FF9302")
            w2_label.move_to(notebook2)
            
            self.play(
                FadeIn(notebook1, notebook2),
                Write(w1_label), Write(w2_label)
            )
            
            total_label = MathTex("12", "\\text{ cm}", font_size=32, color="#FF9302")
            total_label.move_to(UP*1.5)
            
            checkmark = Text("✓", font="Poppins", font_size=48, color="#7464CE")
            checkmark.next_to(total_label, RIGHT, buff=0.5)
            
            self.play(Write(total_label), FadeIn(checkmark, scale=1.5))
            self.wait(1)
            
            self.play(
                FadeOut(shelf_viz, shelf_measurement, notebook1, notebook2, 
                       w1_label, w2_label, total_label, checkmark)
            )
        
        with self.voiceover(text="""<bookmark mark='tile_start'/>For the tile: The perimeter equals 4 times the side. <bookmark mark='tile_eq1'/>4 times the side equals 48. <bookmark mark='tile_answer'/>So the side equals 12 centimeters. <bookmark mark='real_world'/>This is the same idea builders use when calculating tile sizes for a floor.""") as tracker:
            
            self.wait_until_bookmark("tile_start")
            
            part2_label = Text("Part 2: Square Tile", font="Poppins", font_size=28, color="#7464CE")
            part2_label.next_to(solution_title, DOWN, buff=0.5)
            self.play(FadeIn(part2_label))
            
            tile_eq1 = MathTex("P", "=", "4", "s", font_size=36)
            tile_eq1.set_color_by_tex("P", "#7464CE")
            tile_eq1.set_color_by_tex("s", "#FF9302")
            tile_eq1.move_to(UP*1)
            
            self.play(Write(tile_eq1))
            
            self.wait_until_bookmark("tile_eq1")
            
            tile_eq2 = MathTex("4", "s", "=", "48", font_size=36)
            tile_eq2.set_color_by_tex("s", "#FF9302")
            tile_eq2.set_color_by_tex("48", "#7464CE")
            tile_eq2.move_to(UP*0.2)
            
            self.play(TransformFromCopy(tile_eq1, tile_eq2))
            
            self.wait_until_bookmark("tile_answer")
            
            tile_eq3 = MathTex("s", "=", "12", "\\text{ cm}", font_size=36)
            tile_eq3.set_color_by_tex("s", "#FF9302")
            tile_eq3.set_color_by_tex("12", "#FF9302")
            tile_eq3.move_to(DOWN*0.6)
            
            self.play(TransformFromCopy(tile_eq2, tile_eq3))
            
            tile_box = SurroundingRectangle(tile_eq3, color="#FF9302", buff=0.15, stroke_width=3)
            self.play(Create(tile_box))
            
            self.wait_until_bookmark("real_world")
            
            self.play(FadeOut(tile_eq1, tile_eq2, tile_eq3, tile_box, part2_label))
            
            # Floor tile visualization
            floor_grid = VGroup()
            for i in range(4):
                for j in range(3):
                    tile_square = Square(side_length=0.8, color="#7464CE", stroke_width=2, fill_opacity=0.2, fill_color="#7464CE")
                    tile_square.move_to(LEFT*1.5 + UP*0.8 + RIGHT*i*0.85 + DOWN*j*0.85)
                    floor_grid.add(tile_square)
            
            floor_label = Text("Builder's floor tiles", font="Poppins", font_size=24, color="#7464CE")
            floor_label.move_to(DOWN*2.2)
            
            self.play(FadeIn(floor_grid), Write(floor_label))
            self.wait(1)
            
            self.play(FadeOut(solution_title, floor_grid, floor_label))
        
        # SEGMENT 6: Summary
        with self.voiceover(text="""<bookmark mark='summary_start'/>Summary: Perimeter formulas can be rearranged to find missing dimensions. <bookmark mark='summary_rect'/>Rectangle: perimeter is 2 times the sum of length and width. <bookmark mark='summary_square'/>Square: side is the perimeter divided by 4.""") as tracker:
            
            self.wait_until_bookmark("summary_start")
            
            summary_title = Text("Summary", font="Poppins", font_size=44, color="#7464CE")
            summary_title.to_edge(UP)
            self.play(FadeIn(summary_title))
            
            bullet1 = Text("• Perimeter formulas can be rearranged\n  to find missing dimensions", 
                          font="Poppins", font_size=28, color="#7464CE", line_spacing=1.2)
            bullet1.move_to(UP*1.2)
            bullet1.align_to(LEFT*5, LEFT)
            
            self.play(FadeIn(bullet1, shift=RIGHT*0.5))
            
            self.wait_until_bookmark("summary_rect")
            
            rect_icon = Rectangle(width=1.5, height=1, color="#7464CE", stroke_width=3)
            rect_icon.move_to(LEFT*4 + DOWN*0.5)
            
            bullet2 = Text("• Rectangle:", font="Poppins", font_size=28, color="#7464CE")
            bullet2.next_to(rect_icon, RIGHT, buff=0.5)
            bullet2.align_to(bullet1, LEFT)
            
            rect_formula_final = MathTex("P", "=", "2", "(", "l", "+", "w", ")", font_size=32)
            rect_formula_final.set_color_by_tex("P", "#7464CE")
            rect_formula_final.next_to(bullet2, RIGHT, buff=0.3)
            
            self.play(
                Create(rect_icon),
                FadeIn(bullet2, shift=RIGHT*0.5),
                Write(rect_formula_final)
            )
            
            self.wait_until_bookmark("summary_square")
            
            square_icon = Square(side_length=1, color="#7464CE", stroke_width=3)
            square_icon.move_to(LEFT*4 + DOWN*1.8)
            
            bullet3 = Text("• Square:", font="Poppins", font_size=28, color="#7464CE")
            bullet3.next_to(square_icon, RIGHT, buff=0.5)
            bullet3.align_to(bullet1, LEFT)
            
            square_formula_final = MathTex("s", "=", "\\frac{P}{4}", font_size=32)
            square_formula_final.set_color_by_tex("s", "#FF9302")
            square_formula_final.set_color_by_tex("P", "#7464CE")
            square_formula_final.next_to(bullet3, RIGHT, buff=0.3)
            
            self.play(
                Create(square_icon),
                FadeIn(bullet3, shift=RIGHT*0.5),
                Write(square_formula_final)
            )
            
            self.wait(2)
            
            self.play(
                FadeOut(summary_title, bullet1, bullet2, bullet3, 
                       rect_icon, rect_formula_final, square_icon, square_formula_final)
            )