import os
os.environ["OPENAI_API_KEY"] = "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"
from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.openai import OpenAIService

config.background_color = "#E7E5F3"
LAVENDER_BG = "#E7E5F3"
PURPLE = "#7464CE"
ORANGE_HL = "#FF9302"

class Script3Cc029457192Scene(VoiceoverScene):
    def construct(self):
        self.set_speech_service(OpenAIService(voice="shimmer", model="gpt-4o-mini-tts"))
        
        # Introduction
        with self.voiceover(text="""Hello students! <bookmark mark='intro'/> Imagine you're organising a school fair and need to calculate costs quickly. <bookmark mark='fair_setup'/> You have five pounds times the quantity three packs plus two packs plus four single items. <bookmark mark='first_expr'/> But then your friend says she's calculated it as five pounds times three packs, plus five pounds times two packs, plus five pounds times four items. <bookmark mark='second_expr'/> Are these the same calculation? <bookmark mark='question'/> How can you be sure you're getting the same total when expressions look so different? <bookmark mark='transition1'/>""") as tracker:
            title = Text("Algebraic Expressions", font="Poppins", color=PURPLE, font_size=48)
            self.play(FadeIn(title))
            self.wait_until_bookmark("intro")
            
            self.wait_until_bookmark("fair_setup")
            self.play(FadeOut(title))
            fair_icons = VGroup(
                Circle(radius=0.3, color=ORANGE_HL, fill_opacity=0.5),
                Square(side_length=0.6, color=PURPLE, fill_opacity=0.5),
                Triangle(color=ORANGE_HL, fill_opacity=0.5)
            ).arrange(RIGHT, buff=0.8).shift(UP*1.5)
            self.play(LaggedStartMap(FadeIn, fair_icons, lag_ratio=0.3))
            
            self.wait_until_bookmark("first_expr")
            expr1 = MathTex("5(3+2+4)", font_size=44, color=PURPLE)
            expr1.shift(UP*0.3)
            self.play(Write(expr1), FadeOut(fair_icons))
            
            self.wait_until_bookmark("second_expr")
            expr2 = MathTex("5\\cdot 3+5\\cdot 2+5\\cdot 4", font_size=44, color=ORANGE_HL)
            expr2.next_to(expr1, DOWN, buff=0.6)
            self.play(Write(expr2))
            
            self.wait_until_bookmark("question")
            question_mark = Text("?", font="Poppins", color=PURPLE, font_size=60)
            question_mark.move_to(ORIGIN).shift(DOWN*1.2)
            self.play(FadeIn(question_mark, scale=1.5))
            self.play(question_mark.animate.scale(1.2), rate_func=there_and_back, run_time=0.8)
            
            self.wait_until_bookmark("transition1")
            self.play(FadeOut(expr1), FadeOut(expr2), FadeOut(question_mark))
        
        # Definitions
        with self.voiceover(text="""Let's start with what an expression is. <bookmark mark='def_expression'/> An algebraic expression is a mathematical phrase built from numbers, variables, and operations. <bookmark mark='def_complete'/> Now, within any expression, a term is each individual part that we add together. <bookmark mark='def_term'/> For example, in the expression three x plus two y minus four, <bookmark mark='example_expr'/> we can rewrite this as three x plus two y plus negative four. <bookmark mark='rewrite'/> Now we see three separate terms being added: three x, two y, and negative four. <bookmark mark='highlight_terms'/> Here's the key insight: every expression can be written as a sum of terms. <bookmark mark='key_insight'/>""") as tracker:
            self.wait_until_bookmark("def_expression")
            expr_label = Text("Expression", font="Poppins", color=PURPLE, font_size=40)
            expr_label.to_edge(UP, buff=0.8)
            self.play(Write(expr_label))
            
            self.wait_until_bookmark("def_complete")
            definition = Text(
                "A mathematical phrase with\nnumbers, variables, and operations",
                font="Poppins", font_size=28, color=PURPLE
            )
            definition.next_to(expr_label, DOWN, buff=0.5)
            examples = VGroup(
                MathTex("3x+2", font_size=36, color=ORANGE_HL),
                MathTex("5y-7", font_size=36, color=ORANGE_HL)
            ).arrange(RIGHT, buff=1.5).next_to(definition, DOWN, buff=0.5)
            self.play(FadeIn(definition))
            self.play(LaggedStartMap(FadeIn, examples, lag_ratio=0.4))
            
            self.wait_until_bookmark("def_term")
            self.play(FadeOut(definition), FadeOut(examples))
            term_label = Text("Term", font="Poppins", color=ORANGE_HL, font_size=40)
            term_label.move_to(expr_label.get_center())
            self.play(Transform(expr_label, term_label))
            term_def = Text(
                "Each individual part\nthat we add together",
                font="Poppins", font_size=28, color=PURPLE
            )
            term_def.next_to(expr_label, DOWN, buff=0.5)
            self.play(FadeIn(term_def))
            
            self.wait_until_bookmark("example_expr")
            self.play(FadeOut(expr_label), FadeOut(term_def))
            example_expr = MathTex("3x+2y-4", font_size=48, color=PURPLE)
            example_expr.shift(UP*0.5)
            self.play(Write(example_expr))
            
            self.wait_until_bookmark("rewrite")
            rewritten = MathTex("3x+2y+(-4)", font_size=48, color=PURPLE)
            rewritten.move_to(example_expr.get_center())
            self.play(Transform(example_expr, rewritten))
            
            self.wait_until_bookmark("highlight_terms")
            term1_box = SurroundingRectangle(example_expr[0][0:2], color=PURPLE, buff=0.1)
            term2_box = SurroundingRectangle(example_expr[0][3:5], color=ORANGE_HL, buff=0.1)
            term3_box = SurroundingRectangle(example_expr[0][6:10], color=PURPLE, buff=0.1)
            self.play(Create(term1_box))
            self.play(Create(term2_box))
            self.play(Create(term3_box))
            
            self.wait_until_bookmark("key_insight")
            self.play(FadeOut(term1_box), FadeOut(term2_box), FadeOut(term3_box), FadeOut(example_expr))
            key_text = Text(
                "Every expression =\nSum of terms",
                font="Poppins", font_size=38, color=ORANGE_HL
            )
            self.play(Write(key_text))
            self.play(key_text.animate.scale(1.1), rate_func=there_and_back, run_time=1)
            self.play(FadeOut(key_text))
        
        # Properties
        with self.voiceover(text="""This leads us to three powerful tools we can use. <bookmark mark='tools_intro'/> Because addition is commutative, we can add terms in any order. <bookmark mark='commutative'/> This means three x plus two y equals two y plus three x—the sum stays the same. <bookmark mark='comm_example'/> We can also group terms using the associative property with brackets. <bookmark mark='associative'/> The distributive property lets us expand brackets. <bookmark mark='distributive'/> If we have five times, open bracket, x plus three, close bracket, <bookmark mark='dist_example'/> this equals five x plus fifteen, because we multiply five by each term inside the brackets. <bookmark mark='dist_result'/> Remember, these operations never change the expression's value, only its form. <bookmark mark='no_change'/>""") as tracker:
            self.wait_until_bookmark("tools_intro")
            tools_title = Text("Three Powerful Tools", font="Poppins", color=PURPLE, font_size=40)
            tools_title.to_edge(UP, buff=0.6)
            self.play(Write(tools_title))
            
            prop1 = Text("1. Commutative Property", font="Poppins", font_size=30, color=PURPLE)
            prop2 = Text("2. Associative Property", font="Poppins", font_size=30, color=PURPLE)
            prop3 = Text("3. Distributive Property", font="Poppins", font_size=30, color=PURPLE)
            props = VGroup(prop1, prop2, prop3).arrange(DOWN, buff=0.4, aligned_edge=LEFT)
            props.next_to(tools_title, DOWN, buff=0.7)
            self.play(LaggedStartMap(FadeIn, props, lag_ratio=0.3))
            
            self.wait_until_bookmark("commutative")
            self.play(prop1.animate.set_color(ORANGE_HL), run_time=0.5)
            
            self.wait_until_bookmark("comm_example")
            self.play(FadeOut(props), FadeOut(tools_title))
            comm_left = MathTex("3x+2y", font_size=44, color=PURPLE)
            equals = MathTex("=", font_size=44, color=PURPLE)
            comm_right = MathTex("2y+3x", font_size=44, color=PURPLE)
            comm_group = VGroup(comm_left, equals, comm_right).arrange(RIGHT, buff=0.4)
            self.play(Write(comm_left))
            self.play(Write(equals))
            self.play(Write(comm_right))
            self.wait(0.8)
            self.play(FadeOut(comm_group))
            
            self.wait_until_bookmark("associative")
            assoc_text = Text("Associative Property", font="Poppins", font_size=36, color=ORANGE_HL)
            self.play(Write(assoc_text))
            self.wait(0.8)
            self.play(FadeOut(assoc_text))
            
            self.wait_until_bookmark("distributive")
            dist_text = Text("Distributive Property", font="Poppins", font_size=36, color=ORANGE_HL)
            self.play(Write(dist_text))
            self.wait(0.5)
            self.play(FadeOut(dist_text))
            
            self.wait_until_bookmark("dist_example")
            dist_expr = MathTex("5(x+3)", font_size=48, color=PURPLE)
            dist_expr.shift(UP*0.8)
            self.play(Write(dist_expr))
            
            self.wait_until_bookmark("dist_result")
            arrow1 = Arrow(start=dist_expr.get_bottom() + LEFT*0.3, end=DOWN*0.5 + LEFT*0.8, color=ORANGE_HL, buff=0.1)
            arrow2 = Arrow(start=dist_expr.get_bottom() + RIGHT*0.3, end=DOWN*0.5 + RIGHT*0.8, color=ORANGE_HL, buff=0.1)
            self.play(Create(arrow1), Create(arrow2))
            
            dist_result = MathTex("5x+15", font_size=48, color=PURPLE)
            dist_result.shift(DOWN*1.2)
            self.play(Write(dist_result))
            
            self.wait_until_bookmark("no_change")
            reminder = Text("Same value, different form", font="Poppins", font_size=28, color=ORANGE_HL)
            reminder.shift(DOWN*2.2)
            self.play(FadeIn(reminder))
            self.play(reminder.animate.scale(1.1), rate_func=there_and_back, run_time=0.8)
            self.play(FadeOut(dist_expr), FadeOut(arrow1), FadeOut(arrow2), FadeOut(dist_result), FadeOut(reminder))
        
        # Worked Example
        with self.voiceover(text="""Question: Simplify the expression four times the quantity two a plus three minus five a plus seven by using the distributive property and combining like terms. <bookmark mark='question_start'/> Solution: First, apply the distributive property: four times two a plus four times three minus five a plus seven. <bookmark mark='apply_dist'/> This gives eight a plus twelve minus five a plus seven. <bookmark mark='result_dist'/> Now identify terms with the same variable: eight a and negative five a are like terms. <bookmark mark='identify_like'/>""") as tracker:
            self.wait_until_bookmark("question_start")
            question_text = Text("Question", font="Poppins", color=PURPLE, font_size=36)
            question_text.to_edge(UP, buff=0.5)
            self.play(Write(question_text))
            
            question_expr = MathTex("4(2a+3)-5a+7", font_size=44, color=PURPLE)
            question_expr.next_to(question_text, DOWN, buff=0.5)
            self.play(Write(question_expr))
            self.wait(1)
            
            self.wait_until_bookmark("apply_dist")
            self.play(FadeOut(question_text))
            sol_text = Text("Solution", font="Poppins", color=ORANGE_HL, font_size=36)
            sol_text.to_edge(UP, buff=0.5)
            self.play(Write(sol_text))
            
            step1 = MathTex("4\\cdot 2a+4\\cdot 3-5a+7", font_size=40, color=PURPLE)
            step1.next_to(question_expr, DOWN, buff=0.6)
            
            arrow_d1 = Arrow(start=question_expr.get_bottom() + LEFT*0.4, end=step1.get_top() + LEFT*1, color=ORANGE_HL, buff=0.1, stroke_width=3)
            arrow_d2 = Arrow(start=question_expr.get_bottom() + LEFT*0.1, end=step1.get_top() + LEFT*0.3, color=ORANGE_HL, buff=0.1, stroke_width=3)
            self.play(Create(arrow_d1), Create(arrow_d2))
            self.play(Write(step1))
            
            self.wait_until_bookmark("result_dist")
            self.play(FadeOut(arrow_d1), FadeOut(arrow_d2))
            step2 = MathTex("8a+12-5a+7", font_size=40, color=PURPLE)
            step2.next_to(step1, DOWN, buff=0.5)
            self.play(Write(step2))
            
            self.wait_until_bookmark("identify_like")
            box_8a = SurroundingRectangle(step2[0][0:2], color=PURPLE, buff=0.08)
            box_5a = SurroundingRectangle(step2[0][5:8], color=PURPLE, buff=0.08)
            self.play(Create(box_8a), Create(box_5a))
            self.wait(1)
            self.play(FadeOut(question_expr), FadeOut(step1), FadeOut(sol_text))
        
        with self.voiceover(text="""To combine like terms, we treat the variable part as one unit. <bookmark mark='unit_concept'/> Eight a means eight of something called 'a', and negative five a means we subtract five of that same thing. <bookmark mark='explain_units'/> Eight of something minus five of that something leaves three of it: three a. <bookmark mark='combine_a'/> Similarly, twelve and seven are both plain numbers with no variables, so we can add them directly: twelve plus seven equals nineteen. <bookmark mark='combine_nums'/> Final answer: three a plus nineteen. <bookmark mark='final_answer'/>""") as tracker:
            self.wait_until_bookmark("unit_concept")
            unit_text = Text("Treat variable as one unit", font="Poppins", font_size=30, color=ORANGE_HL)
            unit_text.to_edge(UP, buff=0.5)
            self.play(Write(unit_text))
            
            self.wait_until_bookmark("explain_units")
            blocks_8 = VGroup(*[Square(side_length=0.25, color=PURPLE, fill_opacity=0.6) for _ in range(8)])
            blocks_8.arrange(RIGHT, buff=0.05).shift(UP*0.3 + LEFT*2)
            label_8a = MathTex("8a", font_size=32, color=PURPLE).next_to(blocks_8, DOWN, buff=0.3)
            
            blocks_5 = VGroup(*[Square(side_length=0.25, color=ORANGE_HL, fill_opacity=0.6) for _ in range(5)])
            blocks_5.arrange(RIGHT, buff=0.05).shift(DOWN*0.5 + LEFT*2)
            label_5a = MathTex("-5a", font_size=32, color=ORANGE_HL).next_to(blocks_5, DOWN, buff=0.3)
            
            self.play(FadeOut(box_8a), FadeOut(box_5a))
            self.play(LaggedStartMap(FadeIn, blocks_8, lag_ratio=0.08))
            self.play(Write(label_8a))
            self.play(LaggedStartMap(FadeIn, blocks_5, lag_ratio=0.08))
            self.play(Write(label_5a))
            
            self.wait_until_bookmark("combine_a")
            self.play(
                FadeOut(blocks_5),
                FadeOut(label_5a),
                blocks_8[-5:].animate.set_opacity(0.2),
                run_time=1
            )
            result_3a = MathTex("3a", font_size=44, color=PURPLE)
            result_3a.move_to(blocks_8.get_center()).shift(RIGHT*1.5)
            self.play(Write(result_3a))
            self.play(FadeOut(blocks_8), FadeOut(label_8a), FadeOut(unit_text))
            
            self.wait_until_bookmark("combine_nums")
            self.play(result_3a.animate.shift(UP*1.2 + LEFT*1.5), step2.animate.shift(UP*1.2))
            
            box_12 = SurroundingRectangle(step2[0][3:5], color=ORANGE_HL, buff=0.08)
            box_7 = SurroundingRectangle(step2[0][8], color=ORANGE_HL, buff=0.08)
            self.play(Create(box_12), Create(box_7))
            
            nums_calc = MathTex("12+7=19", font_size=36, color=ORANGE_HL)
            nums_calc.shift(DOWN*0.3)
            self.play(Write(nums_calc))
            
            self.wait_until_bookmark("final_answer")
            self.play(FadeOut(step2), FadeOut(box_12), FadeOut(box_7), FadeOut(nums_calc))
            
            final_box = Rectangle(height=1.2, width=4, color=PURPLE, stroke_width=4)
            final_answer = MathTex("3a+19", font_size=52, color=PURPLE)
            final_answer.move_to(final_box.get_center())
            checkmark = Text("✓", font="Poppins", color="#00FF00", font_size=48)
            checkmark.next_to(final_box, RIGHT, buff=0.3)
            
            self.play(FadeOut(result_3a))
            self.play(Create(final_box))
            self.play(Write(final_answer))
            self.play(FadeIn(checkmark, scale=1.5))
            self.wait(1)
            self.play(FadeOut(final_box), FadeOut(final_answer), FadeOut(checkmark))
        
        # Summary
        with self.voiceover(text="""Summary: Expressions are sums of terms. <bookmark mark='sum1'/> Use commutative, associative, and distributive properties to simplify. <bookmark mark='sum2'/> Combine like terms by treating variable parts as units. <bookmark mark='sum3'/>""") as tracker:
            self.wait_until_bookmark("sum1")
            summary_title = Text("Summary", font="Poppins", color=PURPLE, font_size=40)
            summary_title.to_edge(UP, buff=0.6)
            self.play(Write(summary_title))
            
            bullet1 = Text("• Expressions are sums of terms", font="Poppins", font_size=30, color=PURPLE)
            bullet1.next_to(summary_title, DOWN, buff=0.6).to_edge(LEFT, buff=1)
            self.play(FadeIn(bullet1, shift=RIGHT*0.3))
            
            self.wait_until_bookmark("sum2")
            bullet2 = Text(
                "• Use commutative, associative, and\n  distributive properties to simplify",
                font="Poppins", font_size=30, color=PURPLE
            )
            bullet2.next_to(bullet1, DOWN, buff=0.4, aligned_edge=LEFT)
            self.play(FadeIn(bullet2, shift=RIGHT*0.3))
            
            self.wait_until_bookmark("sum3")
            bullet3 = Text(
                "• Combine like terms by treating\n  variable parts as units",
                font="Poppins", font_size=30, color=PURPLE
            )
            bullet3.next_to(bullet2, DOWN, buff=0.4, aligned_edge=LEFT)
            self.play(FadeIn(bullet3, shift=RIGHT*0.3))
            
            self.wait(1.5)
            self.play(
                FadeOut(summary_title),
                FadeOut(bullet1),
                FadeOut(bullet2),
                FadeOut(bullet3)
            )