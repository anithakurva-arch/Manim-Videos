from manim import *
import numpy as np

# Global defaults — keeps everything clean and centered
config.background_color = "#0f1419"

class Segment1(Scene):
    def construct(self):
        # --- Centered sale board ---
        board = RoundedRectangle(width=5, height=2.8, corner_radius=0.2,
                                 color=RED, fill_opacity=0.15, stroke_width=5)
        sale = Text("50% OFF", color=RED, weight=BOLD).scale(1.4).move_to(board)
        sale_grp = VGroup(board, sale)
        self.play(FadeIn(sale_grp, scale=0.8))
        self.wait(3)
        self.play(FadeOut(sale_grp))

        # --- Centered report card ---
        card = RoundedRectangle(width=5, height=3, corner_radius=0.2,
                                color=BLUE, fill_opacity=0.12, stroke_width=4)
        title = Text("Report Card", color=BLUE_B).scale(0.5)\
                    .next_to(card.get_top(), DOWN, 0.3)
        total = Text("Total: 83%", color=YELLOW, weight=BOLD).scale(0.9)
        hl = SurroundingRectangle(total, color=YELLOW, buff=0.15)
        card_grp = VGroup(card, title, total, hl)
        self.play(FadeIn(card_grp, scale=0.9))
        self.wait(3)
        self.play(FadeOut(card_grp))

        # --- Centered question ---
        q = Text("% = ?", color=WHITE, weight=BOLD).scale(2.5)
        self.play(Write(q))
        self.play(q.animate.scale(1.1), rate_func=there_and_back, run_time=1.2)
        self.wait(3)
        self.play(FadeOut(q))


class Segment2(Scene):
    def construct(self):
        # --- Centered 10x10 grid ---
        grid = VGroup()
        for r in range(10):
            for c in range(10):
                sq = Square(side_length=0.42, stroke_width=1.5, color=GREY_B)
                sq.move_to([c*0.42, -r*0.42, 0])
                grid.add(sq)
        grid.move_to(ORIGIN).shift(UP*0.3)

        self.play(Create(grid), run_time=2)
        self.wait(2)

        etym = Text("per centum  =  out of a hundred", color=BLUE_B)\
                  .scale(0.55).next_to(grid, DOWN, buff=0.5)
        self.play(Write(etym))
        self.wait(3)

        # Fill 25 squares
        fills = [grid[i].animate.set_fill(BLUE, opacity=0.9) for i in range(25)]
        self.play(LaggedStart(*fills, lag_ratio=0.04), run_time=3)
        self.wait(2)

        # Replace etymology with equation
        eq = MathTex("25\\%", "=", "\\frac{25}{100}", color=YELLOW).scale(1.3)
        eq.next_to(grid, DOWN, buff=0.5)
        self.play(ReplacementTransform(etym, eq))
        self.wait(4)
        self.play(FadeOut(VGroup(grid, eq)))


class Segment3(Scene):
    def construct(self):
        # --- Top bar: fraction 3/4 ---
        top_bar = VGroup()
        for i in range(4):
            sq = Rectangle(width=1.6, height=0.8, stroke_width=2, color=WHITE)
            sq.move_to([i*1.6 - 2.4, 1.4, 0])
            if i < 3: sq.set_fill(GREEN, opacity=0.85)
            top_bar.add(sq)
        frac = MathTex("\\frac{3}{4}", color=GREEN).scale(1.1)\
                  .next_to(top_bar, LEFT, buff=0.4)

        self.play(Create(top_bar), Write(frac))
        self.wait(3)

        # --- Bottom bar: scale of 100 ---
        bottom = Rectangle(width=6.4, height=0.8, stroke_width=2, color=WHITE)\
                    .move_to([0, -0.3, 0])
        ticks = VGroup()
        for i, t in enumerate(["0%", "25%", "50%", "75%", "100%"]):
            ticks.add(Text(t, color=WHITE).scale(0.4)
                       .move_to([i*1.6 - 3.2, -0.95, 0]))
        scale_lbl = Text("Scale of 100", color=BLUE_B).scale(0.45)\
                       .next_to(bottom, LEFT, buff=0.4)

        self.play(Create(bottom), Write(scale_lbl))
        self.play(Write(ticks))
        self.wait(2)

        # --- Dashed alignment ---
        dashed = DashedLine([3*1.6 - 2.4 - 0.8 + 0.8, 1.0, 0],
                            [3*1.6 - 2.4 - 0.8 + 0.8, -0.7, 0],
                            color=YELLOW, stroke_width=4)
        # Correct x: end of 3rd block = 3*1.6 - 2.4 = 2.4
        dashed = DashedLine([2.4, 1.0, 0], [2.4, -0.7, 0],
                            color=YELLOW, stroke_width=4)
        pulse = Circle(radius=0.25, color=YELLOW, stroke_width=4)\
                    .move_to([2.4, -0.95, 0])
        self.play(Create(dashed), Create(pulse))
        self.wait(2)

        # --- Equation below ---
        eq = MathTex("\\frac{3}{4}", "=", "\\frac{75}{100}", "=", "75\\%",
                     color=YELLOW).scale(1.1).to_edge(DOWN, buff=0.7)
        self.play(Write(eq))
        self.wait(4)
        self.play(FadeOut(VGroup(top_bar, frac, bottom, ticks,
                                  scale_lbl, dashed, pulse, eq)))


class Segment4(Scene):
    def construct(self):
        # --- LEFT GROUP: 50% of 20 ---
        left_coins = VGroup()
        for i in range(20):
            c = Circle(radius=0.16, color=GOLD, stroke_width=2)
            c.move_to([(i%5)*0.38, -(i//5)*0.38, 0])
            if i < 10: c.set_fill(GOLD, opacity=0.95)
            left_coins.add(c)
        left_coins.move_to(LEFT*3.2 + DOWN*0.2)
        left_lbl = Text("50% of 20 = 10", color=WHITE, weight=BOLD)\
                       .scale(0.55).next_to(left_coins, UP, buff=0.4)

        # --- RIGHT GROUP: 25% of 80 ---
        right_coins = VGroup()
        for i in range(80):
            c = Circle(radius=0.10, color=GOLD, stroke_width=1.5)
            c.move_to([(i%10)*0.24, -(i//10)*0.24, 0])
            if i < 20: c.set_fill(GOLD, opacity=0.95)
            right_coins.add(c)
        right_coins.move_to(RIGHT*3 + DOWN*0.2)
        right_lbl = Text("25% of 80 = 20", color=WHITE, weight=BOLD)\
                        .scale(0.55).next_to(right_coins, UP, buff=0.4)

        self.play(FadeIn(left_coins), Write(left_lbl))
        self.play(FadeIn(right_coins), Write(right_lbl))
        self.wait(3)

        # --- Misconception bubble (centered, top) ---
        bubble = RoundedRectangle(width=6.5, height=1.0, corner_radius=0.5,
                                  color=WHITE, fill_opacity=0.08).to_edge(UP, 0.4)
        btxt = Text('"50% > 25%, so 50% gives more"', color=WHITE)\
                  .scale(0.5).move_to(bubble)
        self.play(Create(bubble), Write(btxt))
        cross = Cross(bubble, color=RED, stroke_width=8)
        self.play(Create(cross))
        self.wait(2)

        # --- Rule (centered bottom) ---
        rule = Text("% always depends on the WHOLE",
                    color=YELLOW, weight=BOLD).scale(0.7).to_edge(DOWN, 0.5)
        self.play(Write(rule))
        self.wait(3)
        self.play(FadeOut(VGroup(left_coins, right_coins, left_lbl, right_lbl,
                                  bubble, btxt, cross, rule)))


class Segment5(Scene):
    def construct(self):
        # --- Problem at top ---
        problem = Text(
            "A cyclist has cycled 75% of a 240 km journey.\n"
            "How many kilometres has he cycled?",
            color=WHITE, line_spacing=1.0
        ).scale(0.5)
        box = SurroundingRectangle(problem, color=BLUE_B, buff=0.25, corner_radius=0.15)
        prob = VGroup(box, problem).to_edge(UP, buff=0.4)
        self.play(FadeIn(prob))
        self.wait(2)

        # --- Bar model (centered) ---
        full = Rectangle(width=6.5, height=0.7, color=WHITE, stroke_width=2.5)
        shaded = Rectangle(width=4.875, height=0.7, color=GREEN, fill_opacity=0.85)
        shaded.align_to(full, LEFT)
        bars = VGroup(full, shaded).move_to(UP*0.6)
        total_lbl = Text("Total = 240 km").scale(0.45).next_to(bars, UP, 0.2)
        cyc_lbl = Text("75% = ?", color=WHITE).scale(0.42).move_to(shaded)
        rem_lbl = Text("25%", color=GREY_B).scale(0.4)\
                     .move_to(full.get_right()+LEFT*0.55)
        self.play(Create(full), FadeIn(shaded),
                  Write(total_lbl), Write(cyc_lbl), Write(rem_lbl))
        self.wait(2)

        # --- Five steps, vertically stacked (compact) ---
        steps = VGroup(
            Text("Given:  Total = 240 km,  Percentage = 75%", color=WHITE).scale(0.42),
            Text("To Find:  Distance cycled (km)", color=WHITE).scale(0.42),
            MathTex("\\text{Strategy: } \\text{Distance} = \\tfrac{75}{100} \\times \\text{Total}",
                    color=WHITE).scale(0.55),
            MathTex("\\tfrac{75}{100} \\times 240 = \\tfrac{3}{4} \\times 240 = 180 \\text{ km}",
                    color=WHITE).scale(0.6),
        ).arrange(DOWN, buff=0.25, aligned_edge=LEFT).next_to(bars, DOWN, buff=0.5)

        for s in steps:
            self.play(FadeIn(s, shift=UP*0.1))
            self.wait(2)

        # Final answer
        ans = Text("Answer: 180 km", color=YELLOW, weight=BOLD).scale(0.6)
        ans_box = SurroundingRectangle(ans, color=YELLOW, buff=0.2, corner_radius=0.1)
        ans_grp = VGroup(ans_box, ans).next_to(steps, DOWN, buff=0.3)
        self.play(FadeIn(ans_grp, scale=0.9))
        self.wait(4)
        self.play(FadeOut(VGroup(prob, bars, total_lbl, cyc_lbl, rem_lbl, steps, ans_grp)))


class Segment6(Scene):
    def construct(self):
        # --- Three icons centered horizontally ---
        # Icon 1: mini grid
        mini = VGroup()
        for r in range(10):
            for c in range(10):
                mini.add(Square(side_length=0.13, stroke_width=0.6, color=GREY_B)
                         .move_to([c*0.13, -r*0.13, 0]))
        for i in range(50):
            mini[i].set_fill(BLUE, opacity=0.7)
        mini.move_to(LEFT*4 + UP*0.4)
        l1 = Text("% = out of 100", color=WHITE).scale(0.4)\
                 .next_to(mini, DOWN, 0.4)

        # Icon 2: two bars
        bar_a = Rectangle(width=1.6, height=0.35, color=GREEN, fill_opacity=0.9)
        bar_b = Rectangle(width=1.6, height=0.35, color=BLUE, fill_opacity=0.9)
        two = VGroup(bar_a, bar_b).arrange(DOWN, buff=0.2).move_to(UP*0.4)
        l2 = Text("Fraction → %", color=WHITE).scale(0.4)\
                 .next_to(two, DOWN, 0.4)

        # Icon 3: cyclist
        w1 = Circle(radius=0.28, color=WHITE, stroke_width=3)
        w2 = Circle(radius=0.28, color=WHITE, stroke_width=3).shift(RIGHT*0.85)
        frame = Line(w1.get_center()+UP*0.28, w2.get_center()+UP*0.28, color=WHITE)
        rider = Circle(radius=0.14, color=WHITE, fill_opacity=1)\
                    .move_to(frame.get_center()+UP*0.35)
        cyclist = VGroup(w1, w2, frame, rider).move_to(RIGHT*4 + UP*0.4)
        l3 = Text("% of a quantity", color=WHITE).scale(0.4)\
                 .next_to(cyclist, DOWN, 0.4)

        self.play(FadeIn(mini), FadeIn(two), FadeIn(cyclist))
        self.play(Write(l1), Write(l2), Write(l3))
        self.wait(4)

        # Reflective prompt (centered bottom)
        prompt = Text("Where did you see a percentage today?",
                      color=YELLOW, weight=BOLD).scale(0.6).to_edge(DOWN, 0.7)
        self.play(FadeIn(prompt, shift=UP*0.2))
        self.wait(4)