import os
os.environ["OPENAI_API_KEY"] = "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"

from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.openai import OpenAIService

config.background_color = "#E7E5F3"
LAVENDER_BG = "#E7E5F3"
PURPLE = "#7464CE"
ORANGE_HL = "#FF9302"

class Script3Cc01Scene(VoiceoverScene):
    def construct(self):
        self.set_speech_service(OpenAIService(voice="shimmer", model="gpt-4o-mini-tts"))
        
        # Title card
        title = Text("Classifying Sets", font="Poppins", font_size=56, color=PURPLE)
        library_icon = SVGMobject("library").scale(0.8).set_color(PURPLE)
        library_icon.next_to(title, DOWN, buff=0.5)
        
        with self.voiceover(text="""<bookmark mark='hook_start'/>Hello students! Imagine you're designing an automated library system <break time='0.3s'/> that must handle different types of collections.""") as tracker:
            self.play(FadeIn(title))
            self.wait_until_bookmark("hook_start")
            self.play(DrawBorderThenFill(library_icon))
            self.wait(1)
        
        self.play(FadeOut(title), FadeOut(library_icon))
        
        # Three shelves for collections
        shelf1 = Rectangle(width=3, height=2, color=PURPLE, stroke_width=3)
        shelf2 = Rectangle(width=3, height=2, color=PURPLE, stroke_width=3)
        shelf3 = Rectangle(width=3, height=2, color=PURPLE, stroke_width=3)
        
        shelf1.shift(LEFT * 4)
        shelf2.shift(ORIGIN)
        shelf3.shift(RIGHT * 4)
        
        label1 = Text("This Year", font="Poppins", font_size=20, color=PURPLE).next_to(shelf1, UP, buff=0.2)
        label2 = Text("All Time", font="Poppins", font_size=20, color=PURPLE).next_to(shelf2, UP, buff=0.2)
        label3 = Text("Non-existent\nLanguage", font="Poppins", font_size=18, color=PURPLE).next_to(shelf3, UP, buff=0.2)
        
        with self.voiceover(text="""<bookmark mark='collection1'/> One collection contains all books published this year. <bookmark mark='collection2'/> Another contains all books that will ever be published. <bookmark mark='collection3'/> A third contains books written in a language that doesn't exist yet.""") as tracker:
            self.wait_until_bookmark("collection1")
            self.play(Create(shelf1), FadeIn(label1))
            
            self.wait_until_bookmark("collection2")
            self.play(Create(shelf2), FadeIn(label2))
            
            self.wait_until_bookmark("collection3")
            self.play(Create(shelf3), FadeIn(label3))
        
        # Populate shelves
        books1 = VGroup(*[Rectangle(width=0.2, height=0.8, color=ORANGE_HL, fill_opacity=0.7).move_to(shelf1.get_center() + LEFT * 1.2 + RIGHT * i * 0.25) for i in range(12)])
        
        # Infinite shelf visualization
        books2_base = VGroup(*[Rectangle(width=0.2, height=0.8, color=ORANGE_HL, fill_opacity=0.7).move_to(shelf2.get_center() + LEFT * 1.2 + RIGHT * i * 0.25) for i in range(8)])
        ellipsis2 = Text("...", font="Poppins", font_size=32, color=PURPLE).move_to(shelf2.get_center() + RIGHT * 1.2)
        
        with self.voiceover(text="""<bookmark mark='system_rules'/> Your system needs different rules for each collection type. <bookmark mark='question_hook'/> How would you classify collections based on whether they're bounded or unbounded?""") as tracker:
            self.play(LaggedStart(*[FadeIn(b) for b in books1], lag_ratio=0.05))
            self.play(LaggedStart(*[FadeIn(b) for b in books2_base], lag_ratio=0.05))
            self.play(Write(ellipsis2))
            self.wait_until_bookmark("question_hook")
            
            new_label1 = Text("Bounded?", font="Poppins", font_size=20, color=ORANGE_HL).move_to(label1)
            new_label2 = Text("Unbounded?", font="Poppins", font_size=20, color=ORANGE_HL).move_to(label2)
            new_label3 = Text("Empty?", font="Poppins", font_size=20, color=ORANGE_HL).move_to(label3)
            
            self.play(
                Transform(label1, new_label1),
                Transform(label2, new_label2),
                Transform(label3, new_label3)
            )
            self.wait(1)
        
        self.play(*[FadeOut(mob) for mob in self.mobjects])
        
        # FINITE SET section
        finite_title = Text("FINITE SET", font="Poppins", font_size=44, color=PURPLE)
        finite_title.to_edge(UP, buff=0.5)
        
        with self.voiceover(text="""<bookmark mark='finite_def'/> A finite set contains a specific, limited number of elements. <bookmark mark='finite_example'/> We can, in principle, count all its elements and reach a definite total, <break time='0.2s'/> like the seven days of the week.""") as tracker:
            self.wait_until_bookmark("finite_def")
            self.play(Write(finite_title))
            
            boundary = Rectangle(width=8, height=3, color=PURPLE, stroke_width=3)
            self.play(Create(boundary))
            
            self.wait_until_bookmark("finite_example")
            
            days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            day_elements = VGroup()
            
            for i, day in enumerate(days):
                day_text = Text(day, font="Poppins", font_size=20, color=PURPLE)
                if i < 4:
                    day_text.move_to(boundary.get_center() + LEFT * 3 + RIGHT * i * 1.5 + UP * 0.5)
                else:
                    day_text.move_to(boundary.get_center() + LEFT * 3 + RIGHT * (i-4) * 1.5 + DOWN * 0.5)
                day_elements.add(day_text)
            
            counter = Integer(0, font_size=36, color=ORANGE_HL)
            counter.next_to(boundary, DOWN, buff=0.5)
            
            self.play(FadeIn(counter))
            
            for i, day_elem in enumerate(day_elements):
                self.play(
                    FadeIn(day_elem),
                    counter.animate.set_value(i + 1),
                    run_time=0.3
                )
            
            final_count = Text("Total: 7", font="Poppins", font_size=32, color=ORANGE_HL).move_to(counter)
            self.play(Transform(counter, final_count))
            self.wait(1)
        
        self.play(*[FadeOut(mob) for mob in self.mobjects])
        
        # SINGLETON SET section
        singleton_title = Text("SINGLETON SET", font="Poppins", font_size=44, color=PURPLE)
        singleton_title.to_edge(UP, buff=0.5)
        
        with self.voiceover(text="""<bookmark mark='singleton_def'/> A singleton set is a special finite set containing exactly one element, <bookmark mark='singleton_example'/> like the set containing only the number five.""") as tracker:
            self.wait_until_bookmark("singleton_def")
            self.play(Write(singleton_title))
            
            circle = Circle(radius=1.5, color=PURPLE, stroke_width=3)
            element = Text("5", font="Poppins", font_size=72, color=ORANGE_HL)
            
            self.wait_until_bookmark("singleton_example")
            self.play(Create(circle))
            self.play(FadeIn(element, scale=1.5))
            
            badge = Star(n=5, outer_radius=0.5, color=ORANGE_HL, fill_opacity=0.8)
            badge.next_to(circle, UR, buff=0.1)
            self.play(DrawBorderThenFill(badge))
            self.wait(1)
        
        self.play(*[FadeOut(mob) for mob in self.mobjects])
        
        # INFINITE SET section
        infinite_title = Text("INFINITE SET", font="Poppins", font_size=44, color=PURPLE)
        infinite_title.to_edge(UP, buff=0.5)
        
        with self.voiceover(text="""<bookmark mark='infinite_def'/> An infinite set has no end to its elements <break time='0.2s'/> — no matter how many you count, there are always more. <bookmark mark='infinite_example'/> The set of all natural numbers is infinite because after any number, <break time='0.2s'/> there is always a next number.""") as tracker:
            self.wait_until_bookmark("infinite_def")
            self.play(Write(infinite_title))
            
            # Boundary that tries to contain but fails
            expanding_boundary = Rectangle(width=6, height=2, color=PURPLE, stroke_width=3)
            self.play(Create(expanding_boundary))
            
            # Elements appearing continuously
            dots = VGroup(*[Dot(color=ORANGE_HL, radius=0.08).move_to(LEFT * 2.5 + RIGHT * i * 0.4) for i in range(15)])
            
            for i in range(8):
                self.add(dots[i])
                self.wait(0.15)
            
            # Boundary expands
            self.play(expanding_boundary.animate.set_width(10), run_time=0.8)
            
            for i in range(8, 15):
                self.add(dots[i])
                self.wait(0.15)
            
            ellipsis_inf = Text("...", font="Poppins", font_size=48, color=ORANGE_HL)
            ellipsis_inf.next_to(dots[-1], RIGHT, buff=0.2)
            self.play(Write(ellipsis_inf))
            
            self.wait_until_bookmark("infinite_example")
            self.play(*[FadeOut(mob) for mob in [expanding_boundary, dots, ellipsis_inf]])
            
            # Natural numbers with arrows
            nat_nums = VGroup()
            for i in range(1, 6):
                num = Text(str(i), font="Poppins", font_size=32, color=PURPLE)
                num.move_to(LEFT * 4 + RIGHT * i * 1.5)
                nat_nums.add(num)
            
            ellipsis_nat = Text("...", font="Poppins", font_size=32, color=PURPLE)
            ellipsis_nat.next_to(nat_nums[-1], RIGHT, buff=0.3)
            
            arrows = VGroup()
            for i in range(4):
                arrow = Arrow(nat_nums[i].get_right(), nat_nums[i+1].get_left(), buff=0.1, color=ORANGE_HL, stroke_width=3)
                arrows.add(arrow)
            
            for num in nat_nums:
                self.play(FadeIn(num), run_time=0.3)
            
            self.play(LaggedStart(*[GrowArrow(arr) for arr in arrows], lag_ratio=0.2))
            self.play(Write(ellipsis_nat))
            self.wait(1)
        
        self.play(*[FadeOut(mob) for mob in self.mobjects])
        
        # EMPTY SET section
        empty_title = Text("EMPTY SET", font="Poppins", font_size=44, color=PURPLE)
        empty_title.to_edge(UP, buff=0.5)
        
        with self.voiceover(text="""<bookmark mark='empty_def'/> An empty set has no elements at all. <bookmark mark='empty_notation'/> We call it the empty set or phi, <break time='0.2s'/> and write it as a pair of curly brackets with nothing between them.""") as tracker:
            self.wait_until_bookmark("empty_def")
            self.play(Write(empty_title))
            
            empty_container = Rectangle(width=4, height=2, color=PURPLE, stroke_width=3)
            self.play(Create(empty_container))
            
            # Emphasize emptiness
            cross = VGroup(
                Line(empty_container.get_corner(UL), empty_container.get_corner(DR), color=RED, stroke_width=2),
                Line(empty_container.get_corner(UR), empty_container.get_corner(DL), color=RED, stroke_width=2)
            )
            self.play(Create(cross), run_time=0.5)
            self.play(FadeOut(cross))
            
            self.wait_until_bookmark("empty_notation")
            self.play(FadeOut(empty_container))
            
            brackets = Text("{ }", font="Poppins", font_size=64, color=PURPLE)
            brackets.shift(LEFT * 2)
            
            phi = MathTex(r"\varnothing", font_size=64, color=PURPLE)
            phi.shift(RIGHT * 2)
            
            self.play(Write(brackets), Write(phi))
            
            equals = MathTex("=", font_size=48, color=ORANGE_HL)
            equals.move_to(ORIGIN)
            self.play(Write(equals))
            
            self.play(
                brackets.animate.set_color(ORANGE_HL),
                phi.animate.set_color(ORANGE_HL)
            )
            self.wait(1)
        
        self.play(*[FadeOut(mob) for mob in self.mobjects])
        
        # UNIVERSAL SET section
        universal_title = Text("UNIVERSAL SET", font="Poppins", font_size=44, color=PURPLE)
        universal_title.to_edge(UP, buff=0.5)
        
        with self.voiceover(text="""<bookmark mark='universal_def'/> The universal set contains all elements under consideration for a particular problem. <bookmark mark='universal_context'/> It changes depending on context.""") as tracker:
            self.wait_until_bookmark("universal_def")
            self.play(Write(universal_title))
            
            # Large rectangle labeled U
            universal_rect = Rectangle(width=8, height=4, color=PURPLE, stroke_width=4)
            u_label = Text("U", font="Poppins", font_size=36, color=PURPLE)
            u_label.next_to(universal_rect, UL, buff=0.2)
            
            # Smaller sets inside
            set1 = Circle(radius=0.6, color=ORANGE_HL, stroke_width=2).shift(LEFT * 2 + UP * 0.5)
            set2 = Circle(radius=0.6, color=ORANGE_HL, stroke_width=2).shift(RIGHT * 1 + DOWN * 0.3)
            
            self.play(Create(universal_rect), Write(u_label))
            self.play(Create(set1), Create(set2))
            
            self.wait_until_bookmark("universal_context")
            
            # Morph to different context
            new_universal = Rectangle(width=6, height=3, color=PURPLE, stroke_width=4)
            self.play(Transform(universal_rect, new_universal), run_time=1)
            self.wait(0.5)
        
        with self.voiceover(text="""<bookmark mark='universal_example'/> If you're solving a problem about even numbers less than twenty, <break time='0.2s'/> your universal set would be all natural numbers less than twenty.""") as tracker:
            self.wait_until_bookmark("universal_example")
            self.play(FadeOut(set1), FadeOut(set2))
            
            u_example = Text("U = {1, 2, 3, ..., 19}", font="Poppins", font_size=28, color=PURPLE)
            u_example.move_to(universal_rect.get_top() + DOWN * 0.5)
            
            evens = Text("Evens = {2, 4, 6, ..., 18}", font="Poppins", font_size=24, color=ORANGE_HL)
            evens.move_to(universal_rect.get_center())
            
            self.play(Write(u_example))
            self.wait(0.5)
            self.play(Write(evens))
            self.wait(1)
        
        self.play(*[FadeOut(mob) for mob in self.mobjects])
        
        # WORKED PROBLEM
        question_title = Text("Classify These Sets", font="Poppins", font_size=40, color=PURPLE)
        question_title.to_edge(UP, buff=0.3)
        
        with self.voiceover(text="""<bookmark mark='question_intro'/> Classify these sets and identify suitable universal sets: <bookmark mark='question_a'/> Set A contains the prime numbers between ten and twenty. <bookmark mark='question_b'/> Set B contains all natural numbers.""") as tracker:
            self.wait_until_bookmark("question_intro")
            self.play(Write(question_title))
            
            # Split screen
            divider = Line(UP * 3, DOWN * 3, color=PURPLE, stroke_width=2)
            
            self.wait_until_bookmark("question_a")
            set_a_label = Text("Set A", font="Poppins", font_size=32, color=PURPLE)
            set_a_label.move_to(LEFT * 3 + UP * 2)
            set_a_desc = Text("Prime numbers\nbetween 10 and 20", font="Poppins", font_size=20, color=PURPLE)
            set_a_desc.next_to(set_a_label, DOWN, buff=0.3)
            
            self.play(Create(divider))
            self.play(Write(set_a_label), Write(set_a_desc))
            
            self.wait_until_bookmark("question_b")
            set_b_label = Text("Set B", font="Poppins", font_size=32, color=PURPLE)
            set_b_label.move_to(RIGHT * 3 + UP * 2)
            set_b_desc = Text("All natural\nnumbers", font="Poppins", font_size=20, color=PURPLE)
            set_b_desc.next_to(set_b_label, DOWN, buff=0.3)
            
            self.play(Write(set_b_label), Write(set_b_desc))
        
        # Solution for Set A
        with self.voiceover(text="""<bookmark mark='solution_a_list'/> Set A contains eleven, thirteen, seventeen, and nineteen. <bookmark mark='solution_a_count'/> We can list them completely and count four elements, <bookmark mark='solution_a_classify'/> so Set A is finite. <bookmark mark='solution_a_universal'/> For Set A, a suitable universal set is all natural numbers between ten and twenty.""") as tracker:
            self.wait_until_bookmark("solution_a_list")
            
            primes = [11, 13, 17, 19]
            prime_elements = VGroup()
            
            for i, p in enumerate(primes):
                prime_text = Text(str(p), font="Poppins", font_size=28, color=ORANGE_HL)
                prime_text.move_to(LEFT * 3 + UP * 0.5 + DOWN * i * 0.6)
                prime_elements.add(prime_text)
                
                checkmark = Text("✓", font="Poppins", font_size=24, color=GREEN)
                checkmark.next_to(prime_text, LEFT, buff=0.2)
                
                self.play(Write(prime_text), FadeIn(checkmark), run_time=0.4)
            
            self.wait_until_bookmark("solution_a_count")
            
            count_label = Text("Count: 4", font="Poppins", font_size=24, color=PURPLE)
            count_label.move_to(LEFT * 3 + DOWN * 1.5)
            self.play(Write(count_label))
            
            self.wait_until_bookmark("solution_a_classify")
            
            finite_badge = Text("FINITE", font="Poppins", font_size=28, color=WHITE, background_stroke_width=0)
            finite_bg = Rectangle(width=2, height=0.6, color=ORANGE_HL, fill_opacity=1)
            finite_bg.move_to(LEFT * 3 + DOWN * 2.3)
            finite_badge.move_to(finite_bg)
            
            self.play(FadeIn(finite_bg), Write(finite_badge))
            
            self.wait_until_bookmark("solution_a_universal")
            
            u_a = Text("U = {10, 11, ..., 20}", font="Poppins", font_size=20, color=PURPLE)
            u_a.move_to(LEFT * 3 + DOWN * 3)
            self.play(Write(u_a))
        
        # Solution for Set B
        with self.voiceover(text="""<bookmark mark='solution_b_start'/> Set B contains one, two, three, <bookmark mark='solution_b_continue'/> and continues without ever stopping <break time='0.2s'/> — there is no final element, <bookmark mark='solution_b_classify'/> so Set B is infinite.""") as tracker:
            self.wait_until_bookmark("solution_b_start")
            
            nat_elements = VGroup()
            for i in range(1, 6):
                nat_text = Text(str(i), font="Poppins", font_size=24, color=ORANGE_HL)
                nat_text.move_to(RIGHT * 3 + UP * 0.5 + DOWN * (i-1) * 0.5)
                nat_elements.add(nat_text)
                self.play(FadeIn(nat_text), run_time=0.25)
            
            self.wait_until_bookmark("solution_b_continue")
            
            ellipsis_b = Text("...", font="Poppins", font_size=32, color=ORANGE_HL)
            ellipsis_b.move_to(RIGHT * 3 + DOWN * 1.5)
            self.play(Write(ellipsis_b))
            
            self.wait_until_bookmark("solution_b_classify")
            
            infinite_badge = Text("INFINITE", font="Poppins", font_size=28, color=WHITE, background_stroke_width=0)
            infinite_bg = Rectangle(width=2.2, height=0.6, color=PURPLE, fill_opacity=1)
            infinite_bg.move_to(RIGHT * 3 + DOWN * 2.3)
            infinite_badge.move_to(infinite_bg)
            
            infinity_symbol = MathTex(r"\infty", font_size=32, color=ORANGE_HL)
            infinity_symbol.next_to(infinite_bg, RIGHT, buff=0.2)
            
            self.play(FadeIn(infinite_bg), Write(infinite_badge), FadeIn(infinity_symbol))
            self.wait(1.5)
        
        self.play(*[FadeOut(mob) for mob in self.mobjects])
        
        # SUMMARY
        summary_title = Text("Summary", font="Poppins", font_size=48, color=PURPLE)
        summary_title.to_edge(UP, buff=0.5)
        
        with self.voiceover(text="""<bookmark mark='summary_start'/> Sets are finite if we can count all elements and reach a total; <bookmark mark='summary_infinite'/> they're infinite if elements continue without end. <bookmark mark='summary_special'/> Singleton has one element; empty set has none. <bookmark mark='summary_universal'/> Universal set changes based on problem context.""") as tracker:
            self.wait_until_bookmark("summary_start")
            self.play(Write(summary_title))
            
            # Four summary icons
            finite_icon = VGroup(
                Rectangle(width=1.5, height=1, color=PURPLE, stroke_width=3),
                Text("Finite", font="Poppins", font_size=18, color=PURPLE)
            ).arrange(DOWN, buff=0.2)
            finite_icon.shift(LEFT * 4.5 + UP * 0.5)
            
            self.play(FadeIn(finite_icon))
            
            self.wait_until_bookmark("summary_infinite")
            
            infinite_icon = VGroup(
                Arrow(LEFT * 0.5, RIGHT * 0.5, color=PURPLE, stroke_width=3, buff=0),
                Text("...", font="Poppins", font_size=24, color=ORANGE_HL),
                Text("Infinite", font="Poppins", font_size=18, color=PURPLE)
            ).arrange(DOWN, buff=0.1)
            infinite_icon.shift(LEFT * 1.5 + UP * 0.5)
            
            self.play(FadeIn(infinite_icon))
            
            self.wait_until_bookmark("summary_special")
            
            singleton_icon = VGroup(
                Circle(radius=0.4, color=PURPLE, stroke_width=3),
                Dot(color=ORANGE_HL, radius=0.08),
                Text("Singleton", font="Poppins", font_size=18, color=PURPLE)
            ).arrange(DOWN, buff=0.2)
            singleton_icon.shift(RIGHT * 1.5 + UP * 0.5)
            
            empty_icon = VGroup(
                Text("{ }", font="Poppins", font_size=28, color=PURPLE),
                Text("Empty", font="Poppins", font_size=18, color=PURPLE)
            ).arrange(DOWN, buff=0.2)
            empty_icon.shift(RIGHT * 4.5 + UP * 0.5)
            
            self.play(FadeIn(singleton_icon), FadeIn(empty_icon))
            
            self.wait_until_bookmark("summary_universal")
            
            # Universal set morphing
            u_morph = VGroup(
                Rectangle(width=2, height=1.2, color=PURPLE, stroke_width=2),
                Text("U", font="Poppins", font_size=20, color=PURPLE)
            )
            u_morph[1].move_to(u_morph[0].get_corner(UL) + DR * 0.3)
            u_morph.shift(DOWN * 1.5)
            
            context1 = Text("{numbers}", font="Poppins", font_size=16, color=ORANGE_HL).move_to(u_morph[0])
            self.play(FadeIn(u_morph), Write(context1))
            self.wait(0.5)
            
            context2 = Text("{letters}", font="Poppins", font_size=16, color=ORANGE_HL).move_to(u_morph[0])
            self.play(Transform(context1, context2))
            self.wait(0.5)
            
            context3 = Text("{shapes}", font="Poppins", font_size=16, color=ORANGE_HL).move_to(u_morph[0])
            self.play(Transform(context1, context3))
            self.wait(1)
        
        self.play(*[FadeOut(mob) for mob in self.mobjects])
        
        # End card
        end_text = Text("Keep Classifying!", font="Poppins", font_size=48, color=PURPLE)
        self.play(FadeIn(end_text, scale=1.2))
        self.wait(2)
        self.play(FadeOut(end_text))