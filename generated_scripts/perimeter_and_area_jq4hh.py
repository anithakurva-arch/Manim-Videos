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
        
        # SEGMENT 1: INTRODUCTION
        with self.voiceover(text=r"""<bookmark mark='bk_intro'/>Hello students! Imagine you are arranging chairs around a rectangular classroom table. You know the total number of chairs that fit around it, and you know how many fit along one side. Could you figure out how many fit along the other side without counting again?""") as tracker:
            title = Text("Finding Missing Dimensions", font="Poppins", color=PURPLE, font_size=40)
            self.wait_until_bookmark("bk_intro")
            self.play(FadeIn(title))
            self.wait(1.5)
            self.play(FadeOut(title))
            
            # Draw table with chairs
            table = Rectangle(width=4, height=2.5, color=PURPLE, stroke_width=3)
            table.shift(UP*0.5)
            
            # Chairs as small squares around perimeter
            chair_size = 0.3
            top_chairs = VGroup(*[Square(side_length=chair_size, color=ORANGE_HL, fill_opacity=0.5) for _ in range(5)])
            top_chairs.arrange(RIGHT, buff=0.5)
            top_chairs.next_to(table, UP, buff=0.2)
            
            bottom_chairs = VGroup(*[Square(side_length=chair_size, color=ORANGE_HL, fill_opacity=0.5) for _ in range(5)])
            bottom_chairs.arrange(RIGHT, buff=0.5)
            bottom_chairs.next_to(table, DOWN, buff=0.2)
            
            left_chairs = VGroup(*[Square(side_length=chair_size, color=ORANGE_HL, fill_opacity=0.5) for _ in range(3)])
            left_chairs.arrange(DOWN, buff=0.5)
            left_chairs.next_to(table, LEFT, buff=0.2)
            
            right_chairs = VGroup(*[Square(side_length=chair_size, color=PURPLE, fill_opacity=0.3) for _ in range(3)])
            right_chairs.arrange(DOWN, buff=0.5)
            right_chairs.next_to(table, RIGHT, buff=0.2)
            right_label = Text("?", font="Poppins", color=ORANGE_HL, font_size=30).next_to(right_chairs, RIGHT, buff=0.3)
            
            self.play(Create(table))
            self.play(FadeIn(top_chairs), FadeIn(bottom_chairs), FadeIn(left_chairs))
            self.play(FadeIn(right_chairs), Write(right_label))
            self.wait(2)
            
            self.play(FadeOut(VGroup(table, top_chairs, bottom_chairs, left_chairs, right_chairs, right_label)))
        
        # SEGMENT 2: CONCEPT
        with self.voiceover(text=r"""<bookmark mark='bk_perim_def'/>The perimeter is the total length around a shape. <bookmark mark='bk_rect_formula'/>For a rectangle, the perimeter equals two times the sum of length and width. <bookmark mark='bk_square_formula'/>For a square, the perimeter equals four times the length of one side. <bookmark mark='bk_rearrange'/>So if we know the perimeter and one dimension, we can rearrange the formula and find the missing one. This means perimeter is not just for measuring—it is also a tool to work backwards.""") as tracker:
            rect = Rectangle(width=3, height=2, color=PURPLE, stroke_width=3)
            rect.shift(LEFT*3 + UP*1)
            
            self.wait_until_bookmark("bk_perim_def")
            self.play(Create(rect))
            
            # Perimeter arrow tracing
            perimeter_path = VMobject(color=ORANGE_HL, stroke_width=4)
            perimeter_path.set_points_as_corners([
                rect.get_corner(UL),
                rect.get_corner(UR),
                rect.get_corner(DR),
                rect.get_corner(DL),
                rect.get_corner(UL)
            ])
            self.play(Create(perimeter_path), run_time=2)
            
            self.wait_until_bookmark("bk_rect_formula")
            rect_formula = MathTex(r"P = 2(l + w)", color=PURPLE, font_size=36)
            rect_formula.next_to(rect, DOWN, buff=0.5)
            self.play(Write(rect_formula))
            
            self.wait_until_bookmark("bk_square_formula")
            square = Square(side_length=2, color=PURPLE, stroke_width=3)
            square.shift(RIGHT*3 + UP*1)
            square_formula = MathTex(r"P = 4s", color=PURPLE, font_size=36)
            square_formula.next_to(square, DOWN, buff=0.5)
            self.play(Create(square), Write(square_formula))
            
            self.wait_until_bookmark("bk_rearrange")
            # Show rearrangement
            rearranged = MathTex(r"w = \frac{P}{2} - l", color=ORANGE_HL, font_size=36)
            rearranged.next_to(rect_formula, DOWN, buff=0.3)
            arrow = Arrow(rect_formula.get_bottom(), rearranged.get_top(), color=ORANGE_HL, buff=0.1, stroke_width=3)
            self.play(GrowArrow(arrow), Write(rearranged))
            self.wait(2)
            
            self.play(FadeOut(VGroup(rect, perimeter_path, rect_formula, square, square_formula, rearranged, arrow)))
        
        with self.voiceover(text=r"""<bookmark mark='bk_why'/>Now, why does this work? <bookmark mark='bk_rect_explain'/>A rectangle has two equal lengths and two equal widths. So once we know the perimeter and one of them, simple algebra gives us the other. <bookmark mark='bk_square_explain'/>A square has four equal sides, so its side is simply the perimeter divided by four.""") as tracker:
            self.wait_until_bookmark("bk_why")
            why_text = Text("Why does this work?", font="Poppins", color=PURPLE, font_size=34)
            why_text.to_edge(UP)
            self.play(Write(why_text))
            
            self.wait_until_bookmark("bk_rect_explain")
            explain_rect = Rectangle(width=3.5, height=2, color=PURPLE, stroke_width=3)
            explain_rect.shift(LEFT*2.5)
            
            l_label1 = MathTex("l", color=PURPLE, font_size=28).next_to(explain_rect, UP, buff=0.2)
            l_label2 = MathTex("l", color=PURPLE, font_size=28).next_to(explain_rect, DOWN, buff=0.2)
            w_label1 = MathTex("w", color=ORANGE_HL, font_size=28).next_to(explain_rect, LEFT, buff=0.2)
            w_label2 = MathTex("w", color=ORANGE_HL, font_size=28).next_to(explain_rect, RIGHT, buff=0.2)
            
            brace_top = Brace(explain_rect, UP, color=PURPLE)
            brace_left = Brace(explain_rect, LEFT, color=ORANGE_HL)
            text_2l = Text("2 lengths", font="Poppins", color=PURPLE, font_size=22).next_to(brace_top, UP, buff=0.1)
            text_2w = Text("2 widths", font="Poppins", color=ORANGE_HL, font_size=22).next_to(brace_left, LEFT, buff=0.1)
            
            self.play(Create(explain_rect))
            self.play(Write(l_label1), Write(l_label2), Write(w_label1), Write(w_label2))
            self.play(GrowFromCenter(brace_top), Write(text_2l))
            self.play(GrowFromCenter(brace_left), Write(text_2w))
            
            self.wait_until_bookmark("bk_square_explain")
            explain_square = Square(side_length=2, color=PURPLE, stroke_width=3)
            explain_square.shift(RIGHT*2.5)
            
            s_labels = VGroup(
                MathTex("s", color=PURPLE, font_size=28).next_to(explain_square, UP, buff=0.2),
                MathTex("s", color=PURPLE, font_size=28).next_to(explain_square, DOWN, buff=0.2),
                MathTex("s", color=PURPLE, font_size=28).next_to(explain_square, LEFT, buff=0.2),
                MathTex("s", color=PURPLE, font_size=28).next_to(explain_square, RIGHT, buff=0.2)
            )
            text_4s = Text("4 equal sides", font="Poppins", color=PURPLE, font_size=22)
            text_4s.next_to(explain_square, DOWN, buff=0.8)
            
            self.play(Create(explain_square), Write(s_labels))
            self.play(Write(text_4s))
            self.wait(2)
            
            self.play(FadeOut(VGroup(why_text, explain_rect, l_label1, l_label2, w_label1, w_label2, brace_top, brace_left, text_2l, text_2w, explain_square, s_labels, text_4s)))
        
        # SEGMENT 3: QUESTION
        with self.voiceover(text=r"""<bookmark mark='bk_question'/>Question: Part 1: The perimeter of a rectangular notebook is thirty-four centimetres. Its length is eleven centimetres. Find its width and check whether two such notebooks would fit along a twenty-four-centimetre shelf. Part 2: A square tile has a perimeter of forty-eight centimetres. Find the length of one side.""") as tracker:
            self.wait_until_bookmark("bk_question")
            question_title = Text("Question", font="Poppins", color=PURPLE, font_size=36)
            question_title.to_edge(UP)
            self.play(Write(question_title))
            
            part1 = Text("Part 1: Notebook P=34cm, l=11cm.\nFind w. Check if 2 fit on 24cm shelf.", font="Poppins", color=PURPLE, font_size=24, line_spacing=1.2)
            part1.shift(UP*1)
            
            part2 = Text("Part 2: Square tile P=48cm.\nFind side length.", font="Poppins", color=PURPLE, font_size=24, line_spacing=1.2)
            part2.shift(DOWN*1)
            
            self.play(Write(part1))
            self.play(Write(part2))
            self.wait(2)
            
            self.play(FadeOut(VGroup(question_title, part1, part2)))
        
        # SEGMENT 4: SOLUTION PART 1
        with self.voiceover(text=r"""<bookmark mark='bk_solution1'/>For the notebook: <bookmark mark='bk_formula1'/>Two times the sum of length and width equals the perimeter. <bookmark mark='bk_sub1'/>Two times eleven plus width equals thirty-four. <bookmark mark='bk_divide1'/>Eleven plus width equals seventeen. <bookmark mark='bk_width1'/>So width equals six centimetres. <bookmark mark='bk_shelf'/>Two notebooks placed side by side would need twelve centimetres, which fits well on the shelf.""") as tracker:
            self.wait_until_bookmark("bk_solution1")
            sol1_title = Text("Solution Part 1: Notebook", font="Poppins", color=PURPLE, font_size=32)
            sol1_title.to_edge(UP)
            self.play(Write(sol1_title))
            
            self.wait_until_bookmark("bk_formula1")
            formula1 = MathTex(r"P = 2(l + w)", color=PURPLE, font_size=36)
            formula1.shift(UP*1.5)
            self.play(Write(formula1))
            
            self.wait_until_bookmark("bk_sub1")
            step1 = MathTex(r"34 = 2(11 + w)", color=PURPLE, font_size=36)
            step1.shift(UP*0.5)
            self.play(TransformMatchingTex(formula1.copy(), step1))
            
            self.wait_until_bookmark("bk_divide1")
            step2 = MathTex(r"17 = 11 + w", color=PURPLE, font_size=36)
            step2.shift(DOWN*0.5)
            self.play(TransformMatchingTex(step1.copy(), step2))
            
            self.wait_until_bookmark("bk_width1")
            step3 = MathTex(r"w = 6 \text{ cm}", color=ORANGE_HL, font_size=36)
            step3.shift(DOWN*1.5)
            self.play(TransformMatchingTex(step2.copy(), step3))
            self.play(Indicate(step3, color=ORANGE_HL, scale_factor=1.2))
            
            self.wait_until_bookmark("bk_shelf")
            self.play(FadeOut(VGroup(formula1, step1, step2, step3, sol1_title)))
            
            # Shelf visualization
            shelf = Line(LEFT*4, RIGHT*4, color=PURPLE, stroke_width=5)
            shelf.shift(DOWN*1)
            shelf_label = MathTex(r"24 \text{ cm}", color=PURPLE, font_size=28).next_to(shelf, DOWN, buff=0.3)
            
            notebook1 = Rectangle(width=1.2, height=2.2, color=ORANGE_HL, stroke_width=3)
            notebook1.next_to(shelf, UP, buff=0.1, aligned_edge=LEFT).shift(RIGHT*0.5)
            w1_label = MathTex(r"6 \text{ cm}", color=ORANGE_HL, font_size=24).next_to(notebook1, UP, buff=0.2)
            
            notebook2 = Rectangle(width=1.2, height=2.2, color=ORANGE_HL, stroke_width=3)
            notebook2.next_to(notebook1, RIGHT, buff=0.1)
            w2_label = MathTex(r"6 \text{ cm}", color=ORANGE_HL, font_size=24).next_to(notebook2, UP, buff=0.2)
            
            total_brace = Brace(VGroup(notebook1, notebook2), UP, color=PURPLE)
            total_text = MathTex(r"12 \text{ cm}", color=PURPLE, font_size=28).next_to(total_brace, UP, buff=0.1)
            
            check_text = Text("✓ Fits on shelf!", font="Poppins", color=PURPLE, font_size=28)
            check_text.shift(DOWN*2.5)
            
            self.play(Create(shelf), Write(shelf_label))
            self.play(Create(notebook1), Write(w1_label))
            self.play(Create(notebook2), Write(w2_label))
            self.play(GrowFromCenter(total_brace), Write(total_text))
            self.play(Write(check_text))
            self.wait(2)
            
            self.play(FadeOut(VGroup(shelf, shelf_label, notebook1, notebook2, w1_label, w2_label, total_brace, total_text, check_text)))
        
        # SEGMENT 5: SOLUTION PART 2
        with self.voiceover(text=r"""<bookmark mark='bk_solution2'/>For the tile: <bookmark mark='bk_formula2'/>The perimeter equals four times the side. <bookmark mark='bk_sub2'/>Four times the side equals forty-eight. <bookmark mark='bk_side2'/>So the side equals twelve centimetres. <bookmark mark='bk_builders'/>This is the same idea builders use when calculating tile sizes for a floor.""") as tracker:
            self.wait_until_bookmark("bk_solution2")
            sol2_title = Text("Solution Part 2: Tile", font="Poppins", color=PURPLE, font_size=32)
            sol2_title.to_edge(UP)
            self.play(Write(sol2_title))
            
            self.wait_until_bookmark("bk_formula2")
            formula2 = MathTex(r"P = 4s", color=PURPLE, font_size=36)
            formula2.shift(UP*1)
            self.play(Write(formula2))
            
            self.wait_until_bookmark("bk_sub2")
            step2_1 = MathTex(r"48 = 4s", color=PURPLE, font_size=36)
            step2_1.shift(UP*0)
            self.play(TransformMatchingTex(formula2.copy(), step2_1))
            
            self.wait_until_bookmark("bk_side2")
            step2_2 = MathTex(r"s = 12 \text{ cm}", color=ORANGE_HL, font_size=36)
            step2_2.shift(DOWN*1)
            self.play(TransformMatchingTex(step2_1.copy(), step2_2))
            self.play(Indicate(step2_2, color=ORANGE_HL, scale_factor=1.2))
            
            self.wait_until_bookmark("bk_builders")
            self.play(FadeOut(VGroup(formula2, step2_1, step2_2, sol2_title)))
            
            # Floor tile visualization
            floor_text = Text("Builder's floor:", font="Poppins", color=PURPLE, font_size=28)
            floor_text.to_edge(UP)
            self.play(Write(floor_text))
            
            tile_size = 0.8
            tiles = VGroup(*[
                Square(side_length=tile_size, color=PURPLE, stroke_width=2, fill_opacity=0.2)
                for _ in range(12)
            ])
            tiles.arrange_in_grid(rows=3, cols=4, buff=0.05)
            tiles.shift(DOWN*0.5)
            
            tile_label = MathTex(r"12 \text{ cm}", color=ORANGE_HL, font_size=24)
            tile_label.next_to(tiles[0], UP, buff=0.2)
            
            self.play(Create(tiles), run_time=2)
            self.play(Write(tile_label))
            self.wait(2)
            
            self.play(FadeOut(VGroup(floor_text, tiles, tile_label)))
        
        # SEGMENT 6: SUMMARY
        with self.voiceover(text=r"""<bookmark mark='bk_summary'/>Summary: Perimeter formulas can be rearranged to find missing dimensions. Rectangle: perimeter is two times the sum of length and width. Square: side is the perimeter divided by four.""") as tracker:
            self.wait_until_bookmark("bk_summary")
            summary_title = Text("Summary", font="Poppins", color=PURPLE, font_size=38)
            summary_title.to_edge(UP)
            self.play(Write(summary_title))
            
            bullet1 = Text("• Rearrange formulas to find missing dimensions", font="Poppins", color=PURPLE, font_size=26)
            bullet1.shift(UP*0.8)
            
            bullet2 = MathTex(r"\text{• Rectangle: } P = 2(l + w)", color=PURPLE, font_size=28)
            bullet2.shift(DOWN*0)
            
            bullet3 = MathTex(r"\text{• Square: } s = \frac{P}{4}", color=PURPLE, font_size=28)
            bullet3.shift(DOWN*1)
            
            self.play(Write(bullet1))
            self.wait(0.5)
            self.play(Write(bullet2))
            self.wait(0.5)
            self.play(Write(bullet3))
            self.wait(3)
            
            self.play(FadeOut(VGroup(summary_title, bullet1, bullet2, bullet3)))