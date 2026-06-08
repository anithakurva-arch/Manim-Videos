import os
os.environ["OPENAI_API_KEY"] = "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"
from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.openai import OpenAIService

config.background_color = "#E7E5F3"
LAVENDER_BG = "#E7E5F3"
PURPLE = "#7464CE"
ORANGE_HL = "#FF9302"

class Script2Cc019457190Scene(VoiceoverScene):
    def construct(self):
        self.set_speech_service(
            OpenAIService(
                voice="shimmer",
                model="gpt-4o-mini-tts",
            )
        )
        
        # SEGMENT 1: Introduction/Hook
        with self.voiceover(text="<bookmark mark='intro'/> Hello students! Imagine you're helping organise a school event,,, where each table needs five chairs. <bookmark mark='scenario'/> The organiser tells you to prepare chairs, but won't confirm the final number of tables until tomorrow — it could be three, it could be eight, depending on registrations. <bookmark mark='question_hook'/> How can you write down a rule today that will work for any number of tables? And once they tell you the number, how do you quickly find the exact chair count? <bookmark mark='connection'/> This is exactly what we do when we evaluate algebraic expressions.") as tracker:
            
            # Title and simple icons
            title = Text("Evaluating Algebraic Expressions", font="Poppins", color=PURPLE, font_size=40)
            title.to_edge(UP)
            
            # Simple table icon (rectangle)
            table = Rectangle(width=1.5, height=1.0, color=PURPLE, fill_opacity=0.3, stroke_width=3)
            # Simple chair icons (small squares)
            chairs = VGroup(*[Square(side_length=0.3, color=ORANGE_HL, fill_opacity=0.5, stroke_width=2) for _ in range(5)])
            chairs.arrange(RIGHT, buff=0.2)
            
            scene_group = VGroup(table, chairs).arrange(DOWN, buff=0.5)
            scene_group.scale(0.8)
            

self.play(FadeIn(title))
            self.play(FadeIn(scene_group))
            

# Show uncertainty: 3 vs 8 tables
            tables_3 = VGroup(*[Rectangle(width=0.8, height=0.6, color=PURPLE, fill_opacity=0.3, stroke_width=2) for _ in range(3)])
            tables_3.arrange(RIGHT, buff=0.3)
            tables_8 = VGroup(*[Rectangle(width=0.8, height=0.6, color=PURPLE, fill_opacity=0.3, stroke_width=2) for _ in range(8)])
            tables_8.arrange_in_grid(rows=2, cols=4, buff=0.3)
            
            question_mark = Text("?", font="Poppins", color=ORANGE_HL, font_size=60)
            
            scenario_3 = VGroup(tables_3, Text("3 tables?", font="Poppins", color=PURPLE, font_size=24)).arrange(DOWN, buff=0.3)
            scenario_8 = VGroup(tables_8, Text("8 tables?", font="Poppins", color=PURPLE, font_size=24)).arrange(DOWN, buff=0.3)
            
            scenario_3.move_to(LEFT * 3)
            scenario_8.move_to(RIGHT * 3)
            question_mark.move_to(ORIGIN)
            
            self.play(FadeOut(scene_group))
            self.play(FadeIn(scenario_3), FadeIn(scenario_8), FadeIn(question_mark))
            

# Show formula emerging
            formula = MathTex("5", r"\times", "t", color=PURPLE, font_size=50)
            formula[2].set_color(ORANGE_HL)
            
            self.play(FadeOut(scenario_3), FadeOut(scenario_8), FadeOut(question_mark))
            self.play(Write(formula))
            

self.play(Indicate(formula, color=ORANGE_HL, scale_factor=1.2))
        
        # SEGMENT 2: Definition
        with self.voiceover(text="<bookmark mark='definition'/> An algebraic expression is a mathematical phrase that uses letters to stand for numbers we don't know yet. <bookmark mark='example_intro'/> For example, three times x plus seven. <bookmark mark='variable'/> Here, x is called a variable — it's a placeholder. <bookmark mark='evaluate_def'/> To evaluate the expression means to replace x with a specific number, then calculate the result.") as tracker:
            
            self.play(FadeOut(title), FadeOut(formula))
            

definition_box = Rectangle(width=11, height=2, color=PURPLE, stroke_width=3, fill_opacity=0.1)
            definition_text = Text(
                "Algebraic Expression: A mathematical phrase\nusing letters for unknown numbers",
                font="Poppins",
                color=PURPLE,
                font_size=28,
                line_spacing=1.2
            )
            definition_group = VGroup(definition_box, definition_text)
            definition_group.move_to(UP * 2)
            
            self.play(Create(definition_box), Write(definition_text))
            

example_expr = MathTex("3", "x", "+", "7", color=PURPLE, font_size=60)
            example_expr[1].set_color(ORANGE_HL)
            example_expr.move_to(ORIGIN)
            
            self.play(Write(example_expr[0]), run_time=0.4)
            self.play(Write(example_expr[1]), run_time=0.4)
            self.play(Write(example_expr[2]), run_time=0.4)
            self.play(Write(example_expr[3]), run_time=0.4)
            

variable_label = Text("variable = placeholder", font="Poppins", color=ORANGE_HL, font_size=24)
            variable_label.next_to(example_expr[1], DOWN, buff=0.5)
            arrow = Arrow(variable_label.get_top(), example_expr[1].get_bottom(), color=ORANGE_HL, buff=0.1, stroke_width=3)
            
            self.play(GrowArrow(arrow), Write(variable_label))
            self.play(Indicate(example_expr[1], color=ORANGE_HL, scale_factor=1.3))
            

eval_text = Text("Evaluate = Replace variable + Calculate", font="Poppins", color=PURPLE, font_size=28)
            eval_text.to_edge(DOWN, buff=1)
            self.play(Write(eval_text))
            
            # Show substitution visualization
            x_value = MathTex("x", "=", "5", color=PURPLE, font_size=40)
            x_value[0].set_color(ORANGE_HL)
            x_value[2].set_color(ORANGE_HL)
            x_value.next_to(example_expr, RIGHT, buff=1)
            
            self.play(Write(x_value))
            
            substituted = MathTex("3", r"\times", "5", "+", "7", color=PURPLE, font_size=50)
            substituted[2].set_color(ORANGE_HL)
            substituted.next_to(example_expr, DOWN, buff=1)
            
            self.play(TransformFromCopy(example_expr, substituted))
            
            result = MathTex("=", "22", color=PURPLE, font_size=50)
            result[1].set_color(ORANGE_HL)
            result.next_to(substituted, RIGHT, buff=0.3)
            self.play(Write(result))
        
        self.play(FadeOut(VGroup(*self.mobjects)))
        self.wait(0.5)
        
        # SEGMENT 3: Why Substitute
        with self.voiceover(text="<bookmark mark='why_substitute'/> We substitute because the expression itself is general — it works for any value. <bookmark mark='operations'/> Once we replace the variable with a specific number, we follow the order of operations to calculate the final answer.") as tracker:
            

general_title = Text("General Expression", font="Poppins", color=PURPLE, font_size=32)
            general_title.to_edge(UP, buff=1).shift(LEFT * 3)
            general_expr = MathTex("3x + 7", color=PURPLE, font_size=48)
            general_expr.next_to(general_title, DOWN, buff=0.5)
            
            specific_title = Text("Specific Value", font="Poppins", color=ORANGE_HL, font_size=32)
            specific_title.to_edge(UP, buff=1).shift(RIGHT * 3)
            specific_expr = MathTex("x = 5 \\rightarrow 22", color=PURPLE, font_size=48)
            specific_expr.next_to(specific_title, DOWN, buff=0.5)
            
            self.play(Write(general_title), Write(general_expr))
            self.play(Write(specific_title), Write(specific_expr))
            
            # Show it works for any value
            values = ["x=1→10", "x=2→13", "x=3→16"]
            value_mobs = VGroup()
            for i, val in enumerate(values):
                val_text = MathTex(val, color=PURPLE, font_size=28)
                val_text.next_to(specific_expr, DOWN, buff=0.3 + i*0.6)
                value_mobs.add(val_text)
            
            self.play(Write(value_mobs), run_time=2)
            

order_ops = Text("Order of Operations:\nPEMDAS/BODMAS", font="Poppins", color=PURPLE, font_size=28, line_spacing=1.2)
            order_ops.move_to(DOWN * 2)
            order_box = SurroundingRectangle(order_ops, color=ORANGE_HL, buff=0.2, stroke_width=3)
            
            self.play(Create(order_box), Write(order_ops))
        
        self.play(FadeOut(VGroup(*self.mobjects)))
        self.wait(0.5)
        
        # SEGMENT 4: Worked Example
        with self.voiceover(text="<bookmark mark='question'/> Question: Evaluate the expression two times a plus five,,, when a equals four. <bookmark mark='solution_start'/> Solution: Write the expression: two times a plus five. <bookmark mark='substitute'/> Substitute a equals four: two times four plus five. <bookmark mark='multiply'/> Multiply first: two times four equals eight. <bookmark mark='add'/> Add: eight plus five equals thirteen. <bookmark mark='final'/> Final answer: thirteen.") as tracker:
            

question_title = Text("Question:", font="Poppins", color=PURPLE, font_size=36)
            question_title.to_edge(UP, buff=0.8)
            
            question_text = Text(
                "Evaluate 2a + 5 when a = 4",
                font="Poppins",
                color=PURPLE,
                font_size=32
            )
            question_text.next_to(question_title, DOWN, buff=0.5)
            
            question_box = SurroundingRectangle(VGroup(question_title, question_text), color=ORANGE_HL, buff=0.3, stroke_width=3)
            
            self.play(Create(question_box), Write(question_title), Write(question_text))
            

solution_title = Text("Solution:", font="Poppins", color=PURPLE, font_size=32)
            solution_title.next_to(question_box, DOWN, buff=0.8).to_edge(LEFT, buff=1)
            self.play(Write(solution_title))
            
            # Step 1: Write expression
            step1_label = Text("Step 1: Write the expression", font="Poppins", color=PURPLE, font_size=24)
            step1_label.next_to(solution_title, DOWN, buff=0.4).to_edge(LEFT, buff=1)
            
            expression = MathTex("2", "a", "+", "5", color=PURPLE, font_size=50)
            expression[1].set_color(ORANGE_HL)
            expression.next_to(step1_label, DOWN, buff=0.3)
            
            self.play(Write(step1_label))
            self.play(Write(expression))
            

# Step 2: Substitute
            step2_label = Text("Step 2: Substitute a = 4", font="Poppins", color=PURPLE, font_size=24)
            step2_label.next_to(expression, DOWN, buff=0.6).to_edge(LEFT, buff=1)
            
            substituted_expr = MathTex("2", r"\times", "4", "+", "5", color=PURPLE, font_size=50)
            substituted_expr[2].set_color(ORANGE_HL)
            substituted_expr.next_to(step2_label, DOWN, buff=0.3)
            
            self.play(Write(step2_label))
            self.play(TransformFromCopy(expression, substituted_expr))
            self.play(Indicate(substituted_expr[2], color=ORANGE_HL, scale_factor=1.3))
            

# Step 3: Multiply
            step3_label = Text("Step 3: Multiply 2 × 4 = 8", font="Poppins", color=PURPLE, font_size=24)
            step3_label.next_to(substituted_expr, DOWN, buff=0.6).to_edge(LEFT, buff=1)
            
            multiply_highlight = SurroundingRectangle(VGroup(substituted_expr[0], substituted_expr[1], substituted_expr[2]), color=ORANGE_HL, buff=0.1, stroke_width=3)
            
            after_multiply = MathTex("8", "+", "5", color=PURPLE, font_size=50)
            after_multiply[0].set_color(ORANGE_HL)
            after_multiply.next_to(step3_label, DOWN, buff=0.3)
            
            self.play(Write(step3_label))
            self.play(Create(multiply_highlight))
            self.play(Transform(substituted_expr, after_multiply), FadeOut(multiply_highlight))
            

# Step 4: Add
            step4_label = Text("Step 4: Add 8 + 5 = 13", font="Poppins", color=PURPLE, font_size=24)
            step4_label.next_to(after_multiply, DOWN, buff=0.6).to_edge(LEFT, buff=1)
            
            final_calc = MathTex("13", color=PURPLE, font_size=50)
            final_calc.set_color(ORANGE_HL)
            final_calc.next_to(step4_label, DOWN, buff=0.3)
            
            self.play(Write(step4_label))
            self.play(Transform(substituted_expr, final_calc))
            

# Final answer box
            answer_box = SurroundingRectangle(substituted_expr, color=ORANGE_HL, buff=0.3, stroke_width=5)
            answer_label = Text("Final Answer", font="Poppins", color=ORANGE_HL, font_size=28)
            answer_label.next_to(answer_box, UP, buff=0.3)
            
            self.play(Create(answer_box), Write(answer_label))
            self.play(Flash(substituted_expr, color=ORANGE_HL, line_length=0.3, num_lines=12, flash_radius=0.5))
        
        self.play(FadeOut(VGroup(*self.mobjects)))
        self.wait(0.5)
        
        # SEGMENT 5: Summary
        with self.voiceover(text="<bookmark mark='summary'/> When you substitute a number for a variable and follow the order of operations, you turn a general rule into a specific answer — just like turning five times t into the exact number of chairs once you know t. <bookmark mark='closing'/> That's the power of evaluating expressions.") as tracker:
            

# Return to real-world example
            callback_title = Text("Real-World Connection", font="Poppins", color=PURPLE, font_size=36)
            callback_title.to_edge(UP, buff=0.8)
            
            self.play(Write(callback_title))
            
            # Show 5×t formula
            formula_general = MathTex("5", r"\times", "t", color=PURPLE, font_size=48)
            formula_general[2].set_color(ORANGE_HL)
            formula_general.move_to(UP * 1.5)
            
            self.play(Write(formula_general))
            
            # Show substitution t=6
            t_value = MathTex("t", "=", "6", color=PURPLE, font_size=40)
            t_value[0].set_color(ORANGE_HL)
            t_value[2].set_color(ORANGE_HL)
            t_value.next_to(formula_general, DOWN, buff=0.5)
            
            self.play(Write(t_value))
            
            # Show result
            calculation = MathTex("5", r"\times", "6", "=", "30", color=PURPLE, font_size=48)
            calculation[2].set_color(ORANGE_HL)
            calculation[4].set_color(ORANGE_HL)
            calculation.next_to(t_value, DOWN, buff=0.5)
            
            self.play(Write(calculation))
            
            # Show chairs
            chairs_text = Text("30 chairs needed!", font="Poppins", color=ORANGE_HL, font_size=32)
            chairs_text.next_to(calculation, DOWN, buff=0.8)
            
            self.play(Write(chairs_text))
            

# Closing message
            closing_text = Text(
                "The Power of\nEvaluating Expressions",
                font="Poppins",
                color=PURPLE,
                font_size=40,
                line_spacing=1.3
            )
            closing_text.move_to(DOWN * 1.5)
            
            closing_box = SurroundingRectangle(closing_text, color=ORANGE_HL, buff=0.4, stroke_width=4)
            
            self.play(FadeOut(VGroup(formula_general, t_value, calculation, chairs_text)))
            self.play(Create(closing_box), Write(closing_text))
            self.play(Indicate(closing_text, color=ORANGE_HL, scale_factor=1.1))
        
        self.wait(2)
        self.play(FadeOut(VGroup(*self.mobjects)))