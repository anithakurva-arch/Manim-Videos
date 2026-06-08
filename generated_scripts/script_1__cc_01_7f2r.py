import os
os.environ["OPENAI_API_KEY"] = "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"
from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.openai import OpenAIService

class Script1Cc01Scene(VoiceoverScene):
    def construct(self):
        self.camera.background_color = "#E7E5F3"
        self.set_speech_service(OpenAIService(voice="shimmer", model="gpt-4o-mini-tts"))
        
        # Title Card
        title = Text("Sets", font="Poppins", font_size=60, color="#7464CE")
        subtitle = Text("Revisiting the Idea of Sets", font="Poppins", font_size=32, color="#FF9302")
        subtitle.next_to(title, DOWN, buff=0.3)
        title_group = VGroup(title, subtitle)
        
        with self.voiceover(text="<bookmark mark='intro'/>Hello students! <break time='0.5s'/> Imagine your teacher asks you to form a group of \"all tall students\" in your class.") as tracker:
            self.play(FadeIn(title_group))

self.wait(1)
            self.play(FadeOut(title_group))
            
            # Classroom scene with stick figures
            figures = VGroup()
            heights = [1.5, 2.2, 1.8, 2.5, 1.6, 2.0]
            for i, h in enumerate(heights):
                stick = VGroup(
                    Circle(radius=0.15, color="#7464CE", fill_opacity=1),
                    Line(ORIGIN, DOWN*h*0.5, color="#7464CE", stroke_width=4),
                    Line(ORIGIN, DL*0.3, color="#7464CE", stroke_width=4),
                    Line(ORIGIN, DR*0.3, color="#7464CE", stroke_width=4)
                )
                stick.arrange(DOWN, buff=0.05, center=False)
                stick.scale(0.5)
                figures.add(stick)
            
            figures.arrange(RIGHT, buff=0.5)
            self.play(LaggedStartMap(FadeIn, figures, lag_ratio=0.2))
        
        with self.voiceover(text="<bookmark mark='hesitate'/>You'd probably hesitate <break time='0.3s'/> — who counts as tall? <break time='0.4s'/> Is someone one hundred fifty centimeters tall enough, <break time='0.2s'/> or must they be taller?") as tracker:

question_marks = VGroup(*[Text("?", font="Poppins", color="#FF9302", font_size=36).next_to(fig, UP, buff=0.2) for fig in figures])
            self.play(LaggedStartMap(FadeIn, question_marks, lag_ratio=0.15))
            
            # Height ruler
            ruler = VGroup(
                Line(UP*1.5, DOWN*1.5, color="#7464CE", stroke_width=3),
                Text("150cm", font="Poppins", font_size=20, color="#7464CE").shift(RIGHT*0.5)
            )
            ruler.to_edge(RIGHT)
            self.play(ruler.animate.shift(LEFT*0.5), run_time=0.8)
            
            # Highlight uncertain figures
            uncertain_highlights = VGroup(*[SurroundingRectangle(figures[i], color=GRAY, buff=0.1) for i in [0, 2, 4]])
            self.play(Create(uncertain_highlights))
        
        with self.voiceover(text="<bookmark mark='no_rule'/>Without a clear rule, <break time='0.2s'/> you cannot decide who belongs in the group and who does not. <break time='0.5s'/> This problem brings us to an important idea in mathematics.") as tracker:

self.play(FadeOut(figures, question_marks, ruler, uncertain_highlights))
            
            # Confusion visualization
            blur_circle = Circle(radius=1.5, color=GRAY, fill_opacity=0.3, stroke_width=2)
            blur_circle.set_stroke(color=GRAY, width=2, opacity=0.5)
            self.play(FadeIn(blur_circle))
            
            x_mark = VGroup(
                Line(UL*0.5, DR*0.5, color=RED, stroke_width=8),
                Line(UR*0.5, DL*0.5, color=RED, stroke_width=8)
            )
            self.play(Create(x_mark), blur_circle.animate.set_opacity(0.2))
            self.wait(0.5)
            self.play(FadeOut(blur_circle, x_mark))
        
        with self.voiceover(text="<bookmark mark='definition'/>A set is defined as a well-defined collection of objects. <break time='0.6s'/> Well-defined means there must be a clear rule or property <break time='0.3s'/> that tells us exactly whether any object belongs to the collection or not <break time='0.3s'/> — no confusion, no doubt.") as tracker:

# Definition box
            def_title = Text("SET", font="Poppins", font_size=48, color="#7464CE")
            def_text = Text("Well-defined collection\nof objects", font="Poppins", font_size=32, color="#7464CE")
            def_text.next_to(def_title, DOWN, buff=0.3)
            def_group = VGroup(def_title, def_text)
            def_box = SurroundingRectangle(def_group, color="#7464CE", buff=0.4, corner_radius=0.2)
            definition = VGroup(def_box, def_group)
            
            self.play(Create(def_box))
            self.play(Write(def_title))
            self.play(Write(def_text))
            
            # Highlight "Well-defined"
            well_defined_highlight = SurroundingRectangle(def_text[0:12], color="#FF9302", buff=0.05)
            self.play(Create(well_defined_highlight))
            self.wait(2)
            self.play(FadeOut(well_defined_highlight))
            self.play(definition.animate.scale(0.7).to_edge(UP))
        
        with self.voiceover(text="<bookmark mark='even_example'/>For example, <break time='0.2s'/> \"all even numbers less than ten\" forms a set <break time='0.3s'/> because we can clearly list them: <break time='0.3s'/> <bookmark mark='two'/>two, <break time='0.2s'/> <bookmark mark='four'/>four, <break time='0.2s'/> <bookmark mark='six'/>six, <break time='0.2s'/> <bookmark mark='eight'/>and eight.") as tracker:

even_label = Text("Even numbers < 10", font="Poppins", font_size=28, color="#7464CE")
            even_label.shift(UP*1.5 + LEFT*3)
            even_circle = Circle(radius=1.3, color="#7464CE", stroke_width=3)
            even_circle.next_to(even_label, DOWN, buff=0.3)
            
            self.play(Write(even_label))
            self.play(Create(even_circle))
            
            numbers = []
            positions = [UP*0.4+LEFT*0.4, UP*0.4+RIGHT*0.4, DOWN*0.4+LEFT*0.4, DOWN*0.4+RIGHT*0.4]
            

num2 = Text("2", font="Poppins", font_size=36, color="#FF9302").move_to(even_circle.get_center() + positions[0])
            self.play(FadeIn(num2, scale=0.5))
            numbers.append(num2)
            

num4 = Text("4", font="Poppins", font_size=36, color="#FF9302").move_to(even_circle.get_center() + positions[1])
            self.play(FadeIn(num4, scale=0.5))
            numbers.append(num4)
            

num6 = Text("6", font="Poppins", font_size=36, color="#FF9302").move_to(even_circle.get_center() + positions[2])
            self.play(FadeIn(num6, scale=0.5))
            numbers.append(num6)
            

num8 = Text("8", font="Poppins", font_size=36, color="#FF9302").move_to(even_circle.get_center() + positions[3])
            self.play(FadeIn(num8, scale=0.5))
            numbers.append(num8)
            
            checkmark = VGroup(
                Line(ORIGIN, RIGHT*0.2+DOWN*0.2, color=GREEN, stroke_width=6),
                Line(RIGHT*0.2+DOWN*0.2, RIGHT*0.5+UP*0.4, color=GREEN, stroke_width=6)
            ).next_to(even_circle, RIGHT, buff=0.3)
            self.play(Create(checkmark))
            
            even_group = VGroup(even_label, even_circle, *numbers, checkmark)
        
        with self.voiceover(text="<bookmark mark='flowers_example'/>But \"beautiful flowers\" does not form a set <break time='0.3s'/> because beauty is subjective <break time='0.3s'/> — different people will disagree on which flowers belong.") as tracker:

flower_label = Text("Beautiful flowers", font="Poppins", font_size=28, color="#7464CE")
            flower_label.shift(UP*1.5 + RIGHT*3)
            flower_blob = Circle(radius=1.3, color=GRAY, stroke_width=3, fill_opacity=0.2)
            flower_blob.next_to(flower_label, DOWN, buff=0.3)
            
            self.play(Write(flower_label))
            self.play(Create(flower_blob))
            
            # Simple flower representations
            flower1 = Text("🌸", font="Poppins", font_size=32).move_to(flower_blob.get_center() + UP*0.3)
            flower2 = Text("🌻", font="Poppins", font_size=32).move_to(flower_blob.get_center() + DOWN*0.3)
            self.play(FadeIn(flower1, flower2))
            
            # People with opinions
            person1 = Text("👍", font="Poppins", font_size=28, color=GREEN).next_to(flower_blob, LEFT, buff=0.2)
            person2 = Text("👎", font="Poppins", font_size=28, color=RED).next_to(flower_blob, RIGHT, buff=0.2)
            self.play(FadeIn(person1, person2))
            
            x_mark2 = VGroup(
                Line(UL*0.3, DR*0.3, color=RED, stroke_width=6),
                Line(UR*0.3, DL*0.3, color=RED, stroke_width=6)
            ).next_to(flower_blob, DOWN, buff=0.2)
            self.play(Create(x_mark2))
            
            flower_group = VGroup(flower_label, flower_blob, flower1, flower2, person1, person2, x_mark2)
            
            self.wait(1)
            self.play(FadeOut(even_group, flower_group))
        
        with self.voiceover(text="<bookmark mark='cardinality'/>A set can contain many objects, <break time='0.2s'/> just one object, <break time='0.2s'/> or even no objects at all <break time='0.3s'/> — as long as the membership rule is clear. <break time='0.5s'/> Any ambiguity about membership means it is not a set.") as tracker:

# Three circles for cardinality
            many_circle = Circle(radius=0.8, color="#7464CE", stroke_width=3).shift(LEFT*3)
            many_dots = VGroup(*[Dot(color="#FF9302", radius=0.06).move_to(many_circle.get_center() + [np.cos(i*2*PI/6), np.sin(i*2*PI/6), 0]*0.4) for i in range(6)])
            many_label = Text("Many", font="Poppins", font_size=24, color="#7464CE").next_to(many_circle, DOWN, buff=0.2)
            
            one_circle = Circle(radius=0.8, color="#7464CE", stroke_width=3)
            one_dot = Dot(color="#FF9302", radius=0.08).move_to(one_circle.get_center())
            one_label = Text("One", font="Poppins", font_size=24, color="#7464CE").next_to(one_circle, DOWN, buff=0.2)
            
            empty_circle = Circle(radius=0.8, color="#7464CE", stroke_width=3).shift(RIGHT*3)
            empty_label = Text("None", font="Poppins", font_size=24, color="#7464CE").next_to(empty_circle, DOWN, buff=0.2)
            
            self.play(Create(many_circle), FadeIn(many_dots), Write(many_label))
            self.wait(0.5)
            self.play(Create(one_circle), FadeIn(one_dot), Write(one_label))
            self.wait(0.5)
            self.play(Create(empty_circle), Write(empty_label))
            
            # Checkmarks for all three
            check1 = Text("✓", font="Poppins", font_size=32, color=GREEN).next_to(many_circle, UP, buff=0.1)
            check2 = Text("✓", font="Poppins", font_size=32, color=GREEN).next_to(one_circle, UP, buff=0.1)
            check3 = Text("✓", font="Poppins", font_size=32, color=GREEN).next_to(empty_circle, UP, buff=0.1)
            self.play(FadeIn(check1, check2, check3))
            
            self.wait(1.5)
            self.play(FadeOut(many_circle, many_dots, many_label, one_circle, one_dot, one_label, 
                            empty_circle, empty_label, check1, check2, check3, definition))
        
        with self.voiceover(text="<bookmark mark='elements'/>The objects in a set are called its elements or members.") as tracker:

elements_title = Text("Elements / Members", font="Poppins", font_size=40, color="#FF9302")
            self.play(Write(elements_title))
            
            set_visual = Circle(radius=1.5, color="#7464CE", stroke_width=3).shift(DOWN*0.5)
            dots_in_set = VGroup(*[Dot(color="#FF9302", radius=0.1).move_to(set_visual.get_center() + [np.cos(i*2*PI/5), np.sin(i*2*PI/5), 0]*0.8) for i in range(5)])
            
            self.play(Create(set_visual), FadeIn(dots_in_set))
            self.wait(1)
            self.play(FadeOut(elements_title, set_visual, dots_in_set))
        
        with self.voiceover(text="<bookmark mark='notation'/>We use capital letters for sets, <break time='0.2s'/> like A or B, <break time='0.3s'/> and small letters for elements, <break time='0.2s'/> like x or y.") as tracker:

notation_title = Text("Notation Convention", font="Poppins", font_size=40, color="#7464CE")
            notation_title.to_edge(UP)
            self.play(Write(notation_title))
            
            sets_label = Text("Sets:", font="Poppins", font_size=32, color="#7464CE").shift(UP*0.8 + LEFT*2)
            set_A = Text("A", font="Poppins", font_size=48, color="#7464CE").next_to(sets_label, RIGHT, buff=0.5)
            set_B = Text("B", font="Poppins", font_size=48, color="#7464CE").next_to(set_A, RIGHT, buff=0.5)
            
            elements_label = Text("Elements:", font="Poppins", font_size=32, color="#FF9302").shift(DOWN*0.8 + LEFT*2)
            elem_x = Text("x", font="Poppins", font_size=48, color="#FF9302").next_to(elements_label, RIGHT, buff=0.5)
            elem_y = Text("y", font="Poppins", font_size=48, color="#FF9302").next_to(elem_x, RIGHT, buff=0.5)
            
            self.play(Write(sets_label))
            self.play(Write(set_A), run_time=0.5)
            self.play(Write(set_B), run_time=0.5)
            self.wait(0.5)
            self.play(Write(elements_label))
            self.play(Write(elem_x), run_time=0.5)
            self.play(Write(elem_y), run_time=0.5)
            
            self.wait(1)
            self.play(FadeOut(notation_title, sets_label, set_A, set_B, elements_label, elem_x, elem_y))
        
        with self.voiceover(text="<bookmark mark='epsilon'/>If an element belongs to a set, <break time='0.2s'/> we use the symbol epsilon, <break time='0.2s'/> written as a curved E, <break time='0.2s'/> which we read as \"belongs to\".") as tracker:

# Draw epsilon symbol stroke by stroke
            epsilon_path = VMobject()
            epsilon_path.set_points_as_corners([
                UP*0.5 + RIGHT*0.3,
                UP*0.5 + LEFT*0.3,
                LEFT*0.3,
                UP*0.5 + LEFT*0.3,
                DOWN*0.5 + LEFT*0.3,
                LEFT*0.3,
                DOWN*0.5 + LEFT*0.3,
                DOWN*0.5 + RIGHT*0.3
            ])
            epsilon_symbol = MathTex(r"\in", font_size=96, color="#7464CE")
            
            self.play(Create(epsilon_symbol), run_time=1.5)
            self.play(epsilon_symbol.animate.set_color("#FF9302"), run_time=0.5)
            
            belongs_label = Text("\"belongs to\"", font="Poppins", font_size=32, color="#7464CE").next_to(epsilon_symbol, DOWN, buff=0.5)
            self.play(Write(belongs_label))
            
            # Example usage
            example1 = MathTex("x", r"\in", "A", font_size=56, color="#7464CE")
            example1[0].set_color("#FF9302")
            example1[1].set_color("#7464CE")
            example1[2].set_color("#7464CE")
            example1.next_to(belongs_label, DOWN, buff=0.5)
            self.play(Write(example1))
            
            epsilon_group = VGroup(epsilon_symbol, belongs_label, example1)
            self.wait(1)
            self.play(epsilon_group.animate.shift(LEFT*3))
        
        with self.voiceover(text="<bookmark mark='not_epsilon'/>If it does not belong, <break time='0.2s'/> we use epsilon with a slash through it, <break time='0.2s'/> read as \"does not belong to\".") as tracker:

not_epsilon = MathTex(r"\notin", font_size=96, color="#7464CE").shift(RIGHT*3)
            self.play(Create(not_epsilon), run_time=1.5)
            self.play(not_epsilon.animate.set_color("#FF9302"), run_time=0.5)
            
            not_belongs_label = Text("\"does not belong to\"", font="Poppins", font_size=32, color="#7464CE").next_to(not_epsilon, DOWN, buff=0.5)
            self.play(Write(not_belongs_label))
            
            example2 = MathTex("y", r"\notin", "A", font_size=56, color="#7464CE")
            example2[0].set_color("#FF9302")
            example2[1].set_color("#7464CE")
            example2[2].set_color("#7464CE")
            example2.next_to(not_belongs_label, DOWN, buff=0.5)
            self.play(Write(example2))
            
            self.wait(2)
            self.play(FadeOut(epsilon_group, not_epsilon, not_belongs_label, example2))
        
        with self.voiceover(text="<bookmark mark='question'/>Question: <break time='0.4s'/> Consider the collection P <break time='0.2s'/> containing all prime numbers less than ten. <break time='0.5s'/> Does the number seven belong to set P? <break time='0.5s'/> Does the number nine belong to set P?") as tracker:

question_box = Rectangle(width=11, height=3.5, color="#7464CE", stroke_width=3, fill_opacity=0.1, fill_color="#7464CE")
            question_box.shift(UP*0.5)
            
            q_title = Text("Question", font="Poppins", font_size=36, color="#FF9302")
            q_title.next_to(question_box.get_top(), DOWN, buff=0.3)
            
            set_def = MathTex("P = \\{", "\\text{prime numbers} < 10", "\\}", font_size=40, color="#7464CE")
            set_def.next_to(q_title, DOWN, buff=0.4)
            
            q1 = MathTex("7", r"\in", "P", "?", font_size=40, color="#7464CE")
            q1[0].set_color("#FF9302")
            q1.next_to(set_def, DOWN, buff=0.5).shift(LEFT*2)
            
            q2 = MathTex("9", r"\in", "P", "?", font_size=40, color="#7464CE")
            q2[0].set_color("#FF9302")
            q2.next_to(set_def, DOWN, buff=0.5).shift(RIGHT*2)
            
            self.play(Create(question_box))
            self.play(Write(q_title))
            self.play(Write(set_def))
            self.wait(0.5)
            self.play(Write(q1))
            self.wait(0.5)
            self.play(Write(q2))
            
            self.wait(1)
            self.play(FadeOut(question_box, q_title, set_def, q1, q2))
        
        with self.voiceover(text="<bookmark mark='solution_start'/>Solution: <break time='0.4s'/> First, list the prime numbers less than ten: <break time='0.3s'/> two, <break time='0.2s'/> three, <break time='0.2s'/> five, <break time='0.2s'/> and seven.") as tracker:

sol_title = Text("Solution", font="Poppins", font_size=36, color="#FF9302")
            sol_title.to_edge(UP)
            self.play(Write(sol_title))
            
            prime_list = MathTex("P = \\{", "2,", "3,", "5,", "7", "\\}", font_size=48, color="#7464CE")
            prime_list.shift(UP*1.5)
            
            self.play(Write(prime_list[0]))
            self.play(Write(prime_list[1]), run_time=0.4)
            self.wait(0.2)
            self.play(Write(prime_list[2]), run_time=0.4)
            self.wait(0.2)
            self.play(Write(prime_list[3]), run_time=0.4)
            self.wait(0.2)
            self.play(Write(prime_list[4]), run_time=0.4)
            self.play(Write(prime_list[5]))
        
        with self.voiceover(text="<bookmark mark='seven_belongs'/>Seven is prime, <break time='0.2s'/> so seven belongs to P <break time='0.3s'/> — we write this as: <break time='0.2s'/> seven epsilon P.") as tracker:

seven_highlight = SurroundingRectangle(prime_list[4], color="#FF9302", buff=0.1, corner_radius=0.1)
            self.play(Create(seven_highlight))
            
            seven_check = Text("7 is prime ✓", font="Poppins", font_size=32, color=GREEN).shift(UP*0.3)
            self.play(Write(seven_check))
            
            seven_notation = MathTex("7", r"\in", "P", font_size=56, color="#7464CE")
            seven_notation[0].set_color("#FF9302")
            seven_notation.shift(DOWN*0.8)
            self.play(Write(seven_notation))
            
            self.wait(1)
        
        with self.voiceover(text="<bookmark mark='nine_check'/>Nine equals three times three, <break time='0.2s'/> so it is not prime.") as tracker:

nine_calc = MathTex("9 = 3 \\times 3", font_size=40, color="#7464CE").shift(DOWN*2)
            self.play(Write(nine_calc))
            
            not_prime = Text("not prime ✗", font="Poppins", font_size=32, color=RED).next_to(nine_calc, RIGHT, buff=0.5)
            self.play(Write(not_prime))
        
        with self.voiceover(text="<bookmark mark='nine_not_belongs'/>Therefore, nine does not belong to P <break time='0.3s'/> — we write this as: <break time='0.2s'/> nine epsilon with slash P.") as tracker:

nine_notation = MathTex("9", r"\notin", "P", font_size=56, color="#7464CE")
            nine_notation[0].set_color("#FF9302")
            nine_notation.next_to(nine_calc, DOWN, buff=0.5)
            self.play(Write(nine_notation))
            
            self.wait(2)
            self.play(FadeOut(sol_title, prime_list, seven_highlight, seven_check, seven_notation, 
                            nine_calc, not_prime, nine_notation))
        
        with self.voiceover(text="<bookmark mark='summary'/>Summary: <break time='0.4s'/> A set is a well-defined collection with a clear membership rule. <break time='0.5s'/> Elements are denoted by small letters; <break time='0.2s'/> sets by capital letters. <break time='0.5s'/> Use epsilon for membership, <break time='0.2s'/> epsilon with slash for non-membership.") as tracker:

summary_title = Text("Summary", font="Poppins", font_size=48, color="#FF9302")
            summary_title.to_edge(UP)
            self.play(Write(summary_title))
            
            bullet1 = Text("• Set = well-defined collection with clear rule", font="Poppins", font_size=28, color="#7464CE")
            bullet1.shift(UP*0.8 + LEFT*0.5)
            
            bullet2 = Text("• Elements (lowercase)  /  Sets (UPPERCASE)", font="Poppins", font_size=28, color="#7464CE")
            bullet2.next_to(bullet1, DOWN, buff=0.4, aligned_edge=LEFT)
            
            bullet3 = MathTex(r"\text{• Use } \in \text{ for membership, } \notin \text{ for non-membership}", font_size=28, color="#7464CE")
            bullet3.next_to(bullet2, DOWN, buff=0.4, aligned_edge=LEFT)
            
            self.play(Write(bullet1), run_time=1)
            self.wait(0.5)
            self.play(Write(bullet2), run_time=1)
            self.wait(0.5)
            self.play(Write(bullet3), run_time=1)
            
            self.wait(2)
            self.play(FadeOut(summary_title, bullet1, bullet2, bullet3))
        
        # End card
        end_text = Text("Thank you!", font="Poppins", font_size=56, color="#7464CE")
        self.play(FadeIn(end_text))
        self.wait(2)
        self.play(FadeOut(end_text))