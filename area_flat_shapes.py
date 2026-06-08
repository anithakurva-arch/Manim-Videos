from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.openai import OpenAIService

# Coschool Color Palette
LAVENDER_BG = "#E7E5F3"
PURPLE = "#7464CE"
ORANGE_HL = "#FF9302"
PALE_PURPLE = "#9495D7"


def create_heading_badge(text_str):
    text = Text(text_str, font="Poppins", font_size=28, color=WHITE, weight=BOLD)
    badge = RoundedRectangle(
        corner_radius=0.2,
        width=text.width + 0.6,
        height=text.height + 0.3,
        fill_color=PURPLE,
        fill_opacity=1,
        stroke_width=0,
    )
    badge.move_to(text)
    return VGroup(badge, text).to_corner(UL, buff=0.3)


class AreaOfRectanglesAndSquares(VoiceoverScene):
    def construct(self):
        self.camera.background_color = LAVENDER_BG
        self.set_speech_service(
            OpenAIService(
                voice="nova",
                model="tts-1-hd",
                transcription_model="medium",
            ),
            create_subcaption=False,
        )

        # ──────────────────────────────────────────────
        # --- SCENE 1: Title Slide ---
        # ──────────────────────────────────────────────
        title_bg = Rectangle(
            width=config.frame_width,
            height=config.frame_height,
            fill_color=PURPLE,
            fill_opacity=1,
            stroke_width=0,
        )
        title_text = Text(
            "Area of Rectangles\n& Squares",
            font="Poppins",
            font_size=72,
            color=WHITE,
            weight=BOLD,
            line_spacing=1.2,
        ).move_to(ORIGIN)

        with self.voiceover(
            text='<bookmark mark="show_title"/>Hello students! In this lesson, '
                 "we will understand how to measure the surface enclosed within "
                 "flat shapes like rectangles and squares."
        ) as tracker:
            self.wait_until_bookmark("show_title")
            self.play(FadeIn(title_bg), Write(title_text), run_time=1.2)
        self.wait(0.15)
        self.play(FadeOut(title_bg), FadeOut(title_text))

        # ──────────────────────────────────────────────
        # --- SCENE 2: Transition (no voiceover) ---
        # ──────────────────────────────────────────────
        intro_text = Text(
            "Let's understand how to measure\nthe surface enclosed within flat shapes",
            font="Poppins",
            font_size=32,
            color=PURPLE,
        ).move_to(ORIGIN)
        self.play(Write(intro_text), run_time=1.5)
        self.wait(0.15)
        self.play(FadeOut(intro_text))

        # ──────────────────────────────────────────────
        # --- SCENE 3: What Is Area? ---
        # ──────────────────────────────────────────────
        heading3 = create_heading_badge("What Is Area?")

        rect3 = Rectangle(width=4, height=2.5, color=PURPLE, stroke_width=2.5)
        rect3.move_to(ORIGIN + UP * 0.3)
        rect3_fill = rect3.copy().set_fill(PURPLE, opacity=0.12).set_stroke(width=0)

        arrows_in = VGroup()
        for d in [UP, DOWN, LEFT, RIGHT]:
            arr = Arrow(
                rect3.get_edge_center(d) + d * 0.6,
                rect3.get_edge_center(d) + d * 0.05,
                color=PURPLE,
                stroke_width=2,
                buff=0,
                max_tip_length_to_length_ratio=0.35,
            )
            arrows_in.add(arr)

        area_label3 = Text(
            "Area", font="Poppins", font_size=40, color=ORANGE_HL, weight=BOLD
        ).move_to(rect3.get_center())

        desc3 = Text(
            "The extent of a 2D surface",
            font="Poppins",
            font_size=24,
            color=PURPLE,
        ).next_to(rect3, DOWN, buff=0.7)

        with self.voiceover(
            text='<bookmark mark="h3"/>Area is the measure of '
                 '<bookmark mark="rect3"/>the extent of a '
                 '<bookmark mark="fill3"/>two-dimensional '
                 '<bookmark mark="arrows3"/>surface.'
                 '<bookmark mark="label3"/>'
        ) as tracker:
            self.wait_until_bookmark("h3")
            self.play(FadeIn(heading3), run_time=0.5)
            self.wait_until_bookmark("rect3")
            self.play(Create(rect3), run_time=0.8)
            self.wait_until_bookmark("fill3")
            self.play(FadeIn(rect3_fill), run_time=0.5)
            self.wait_until_bookmark("arrows3")
            self.play(*[GrowArrow(a) for a in arrows_in], run_time=0.6)
            self.wait_until_bookmark("label3")
            self.play(FadeIn(area_label3), FadeIn(desc3), run_time=0.6)
        self.wait(0.1)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.2)

        # ──────────────────────────────────────────────
        # --- SCENE 4: Unit Squares ---
        # ──────────────────────────────────────────────
        heading4 = create_heading_badge("Unit Squares")

        grid_rect4 = Rectangle(width=5, height=3, color=PURPLE, stroke_width=2.5)
        grid_rect4.move_to(ORIGIN + UP * 0.2)

        unit_squares4 = VGroup()
        for r in range(3):
            for c in range(5):
                sq = Square(side_length=1, color=PURPLE, stroke_width=1.2)
                sq.set_fill(LAVENDER_BG, opacity=0.5)
                sq.move_to(
                    grid_rect4.get_corner(UL) + RIGHT * (c + 0.5) + DOWN * (r + 0.5)
                )
                unit_squares4.add(sq)

        highlight_sq4 = unit_squares4[0].copy().set_stroke(ORANGE_HL, width=3)
        unit_label4 = Text("1 unit", font="Poppins", font_size=18, color=PURPLE)
        unit_label4.next_to(unit_squares4[0], LEFT, buff=0.3)

        with self.voiceover(
            text='<bookmark mark="h4"/>Area is determined by '
                 '<bookmark mark="grid4"/>counting the number of unit squares '
                 "that can fit within a given region "
                 '<bookmark mark="fill4"/>without overlapping. '
                 '<bookmark mark="ulabel4"/>These can also be fractions of a unit square.'
        ) as tracker:
            self.wait_until_bookmark("h4")
            self.play(FadeIn(heading4), run_time=0.5)
            self.wait_until_bookmark("grid4")
            self.play(Create(grid_rect4), run_time=0.8)
            self.wait_until_bookmark("fill4")
            self.play(
                LaggedStart(
                    *[FadeIn(sq) for sq in unit_squares4], lag_ratio=0.06
                ),
                run_time=2.0,
            )
            self.wait_until_bookmark("ulabel4")
            self.play(
                Create(highlight_sq4), FadeIn(unit_label4), run_time=0.6
            )
        self.wait(0.1)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.2)

        # ──────────────────────────────────────────────
        # --- SCENE 5: Unit Square ---
        # ──────────────────────────────────────────────
        heading5 = create_heading_badge("Unit Square")

        big_sq5 = Square(side_length=2.5, color=PURPLE, stroke_width=2.5)
        big_sq5.move_to(LEFT * 2 + UP * 0.2)

        b_arr5 = DoubleArrow(
            big_sq5.get_corner(DL) + DOWN * 0.3,
            big_sq5.get_corner(DR) + DOWN * 0.3,
            color=PURPLE, stroke_width=2, buff=0, tip_length=0.15,
        )
        b_lbl5 = Text("1 unit", font="Poppins", font_size=18, color=PURPLE)
        b_lbl5.next_to(b_arr5, DOWN, buff=0.1)

        l_arr5 = DoubleArrow(
            big_sq5.get_corner(UL) + LEFT * 0.3,
            big_sq5.get_corner(DL) + LEFT * 0.3,
            color=PURPLE, stroke_width=2, buff=0, tip_length=0.15,
        )
        l_lbl5 = Text("1 unit", font="Poppins", font_size=18, color=PURPLE)
        l_lbl5.next_to(l_arr5, LEFT, buff=0.1)

        sq_fill5 = big_sq5.copy().set_fill(ORANGE_HL, opacity=0.12).set_stroke(width=0)
        measure_txt5 = Text(
            "Used to measure area", font="Poppins", font_size=22, color=PURPLE
        ).next_to(big_sq5, DOWN, buff=1.0)

        units5 = (
            VGroup(
                MathTex(r"\text{cm}^2", color=PURPLE, font_size=32),
                MathTex(r"\text{m}^2", color=PURPLE, font_size=32),
                MathTex(r"\text{in}^2", color=PURPLE, font_size=32),
            )
            .arrange(DOWN, buff=0.3)
            .move_to(RIGHT * 3 + UP * 0.2)
        )

        with self.voiceover(
            text='<bookmark mark="h5"/>A unit square has a '
                 '<bookmark mark="sq5"/>side length of 1 unit and is '
                 '<bookmark mark="dims5"/>used to measure area. '
                 '<bookmark mark="fill5"/>Area is expressed as the number of such squares '
                 "covering a region, in square units like "
                 '<bookmark mark="units5"/>centimeter square, meter square, or inch square.'
        ) as tracker:
            self.wait_until_bookmark("h5")
            self.play(FadeIn(heading5), run_time=0.5)
            self.wait_until_bookmark("sq5")
            self.play(Create(big_sq5), run_time=0.8)
            self.wait_until_bookmark("dims5")
            self.play(
                GrowFromCenter(b_arr5), FadeIn(b_lbl5),
                GrowFromCenter(l_arr5), FadeIn(l_lbl5),
                run_time=0.6,
            )
            self.wait_until_bookmark("fill5")
            self.play(FadeIn(sq_fill5), FadeIn(measure_txt5), run_time=0.6)
            self.wait_until_bookmark("units5")
            self.play(
                LaggedStart(
                    *[FadeIn(u, shift=RIGHT * 0.3) for u in units5],
                    lag_ratio=0.2,
                ),
                run_time=0.8,
            )
        self.wait(0.1)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.2)

        # ──────────────────────────────────────────────
        # --- SCENE 6: Transition ---
        # ──────────────────────────────────────────────
        trans6 = Text(
            "How do unit squares connect\nto the area formula?",
            font="Poppins", font_size=32, color=PURPLE,
        ).move_to(ORIGIN)

        with self.voiceover(
            text='<bookmark mark="t6"/>Now let us see how unit squares '
                 "connect to the area formula for rectangles."
        ) as tracker:
            self.wait_until_bookmark("t6")
            self.play(Write(trans6), run_time=1.2)
        self.wait(0.15)
        self.play(FadeOut(trans6))

        # ──────────────────────────────────────────────
        # --- SCENE 7: Counting Squares  [FIX APPLIED]
        # ──────────────────────────────────────────────
        heading7 = create_heading_badge("Counting Squares")

        rect7 = Rectangle(width=5, height=3, color=PURPLE, stroke_width=2.5)
        rect7.move_to(ORIGIN + UP * 0.5)

        b_arr7 = DoubleArrow(
            rect7.get_corner(DL) + DOWN * 0.3,
            rect7.get_corner(DR) + DOWN * 0.3,
            color=PURPLE, stroke_width=2, buff=0, tip_length=0.15,
        )
        b_lbl7 = Text("5 units", font="Poppins", font_size=18, color=PURPLE)
        b_lbl7.next_to(b_arr7, DOWN, buff=0.1)

        l_arr7 = DoubleArrow(
            rect7.get_corner(UL) + LEFT * 0.3,
            rect7.get_corner(DL) + LEFT * 0.3,
            color=PURPLE, stroke_width=2, buff=0, tip_length=0.15,
        )
        l_lbl7 = Text("3 units", font="Poppins", font_size=18, color=PURPLE)
        l_lbl7.next_to(l_arr7, LEFT, buff=0.1)

        all_sqs7 = VGroup()
        for r in range(3):
            for c in range(5):
                sq = Square(side_length=1, color=PURPLE, stroke_width=1)
                sq.set_fill(LAVENDER_BG, opacity=0.3)
                sq.move_to(
                    rect7.get_corner(UL) + RIGHT * (c + 0.5) + DOWN * (r + 0.5)
                )
                all_sqs7.add(sq)

        with self.voiceover(
            text='<bookmark mark="h7"/>The number of unit squares contained '
                 "in a rectangle "
                 '<bookmark mark="r7"/>equals the '
                 '<bookmark mark="d7"/>product of its '
                 '<bookmark mark="row1"/>length and width.'
        ) as tracker:
            self.wait_until_bookmark("h7")
            self.play(FadeIn(heading7), run_time=0.5)
            self.wait_until_bookmark("r7")
            self.play(Create(rect7), run_time=0.8)
            self.wait_until_bookmark("d7")
            self.play(
                GrowFromCenter(b_arr7), FadeIn(b_lbl7),
                GrowFromCenter(l_arr7), FadeIn(l_lbl7),
                run_time=0.6,
            )
            self.wait_until_bookmark("row1")
            self.play(
                LaggedStart(
                    *[FadeIn(sq) for sq in all_sqs7], lag_ratio=0.04
                ),
                run_time=1.5,
            )
        self.wait(0.1)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.2)

        # ──────────────────────────────────────────────
        # --- SCENE 8: Rectangle Area ---
        # ──────────────────────────────────────────────
        heading8 = create_heading_badge("Rectangle Area")

        rect8 = Rectangle(width=4, height=2.5, color=PURPLE, stroke_width=2.5)
        rect8.move_to(ORIGIN + UP * 0.8)

        b_arr8 = DoubleArrow(
            rect8.get_corner(DL) + DOWN * 0.3,
            rect8.get_corner(DR) + DOWN * 0.3,
            color=PURPLE, stroke_width=2, buff=0, tip_length=0.15,
        )
        b_lbl8 = Text("length (l)", font="Poppins", font_size=18, color=PURPLE)
        b_lbl8.next_to(b_arr8, DOWN, buff=0.1)

        l_arr8 = DoubleArrow(
            rect8.get_corner(UL) + LEFT * 0.3,
            rect8.get_corner(DL) + LEFT * 0.3,
            color=PURPLE, stroke_width=2, buff=0, tip_length=0.15,
        )
        l_lbl8 = Text("width (w)", font="Poppins", font_size=18, color=PURPLE)
        l_lbl8.next_to(l_arr8, LEFT, buff=0.1)

        formula8 = MathTex(r"A = l \times w", color=PURPLE, font_size=40)
        formula8.next_to(rect8, DOWN, buff=1.2)
        fbox8 = SurroundingRectangle(
            formula8, color=ORANGE_HL, corner_radius=0.15, buff=0.25, stroke_width=3
        )

        with self.voiceover(
            text='<bookmark mark="h8"/>This gives us: '
                 '<bookmark mark="r8"/>Area of a rectangle equals '
                 '<bookmark mark="d8"/>length '
                 '<bookmark mark="f8"/>times width.'
        ) as tracker:
            self.wait_until_bookmark("h8")
            self.play(FadeIn(heading8), run_time=0.5)
            self.wait_until_bookmark("r8")
            self.play(Create(rect8), run_time=0.8)
            self.wait_until_bookmark("d8")
            self.play(
                GrowFromCenter(b_arr8), FadeIn(b_lbl8),
                GrowFromCenter(l_arr8), FadeIn(l_lbl8),
                run_time=0.6,
            )
            self.wait_until_bookmark("f8")
            self.play(Write(formula8), Create(fbox8), run_time=0.8)
        self.wait(0.1)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.2)

        # ──────────────────────────────────────────────
        # --- SCENE 9: Special Case ---
        # ──────────────────────────────────────────────
        heading9 = create_heading_badge("Special Case")

        rect9 = Rectangle(width=4, height=2.5, color=PURPLE, stroke_width=2.5)
        rect9.move_to(LEFT * 2 + UP * 0.3)

        sq9_target = Square(side_length=2.5, color=PURPLE, stroke_width=2.5)
        sq9_target.move_to(LEFT * 2 + UP * 0.3)

        s_labels9 = VGroup()
        for d in [DOWN, LEFT, UP, RIGHT]:
            lbl = Text("s", font="Poppins", font_size=20, color=PURPLE)
            lbl.next_to(sq9_target, d, buff=0.2)
            s_labels9.add(lbl)

        equal_txt9 = Text(
            "All sides equal",
            font="Poppins", font_size=24, color=ORANGE_HL, weight=BOLD,
        ).next_to(sq9_target, UP, buff=0.5)

        with self.voiceover(
            text='<bookmark mark="h9"/>Since a square is a '
                 '<bookmark mark="r9"/>special rectangle where '
                 '<bookmark mark="morph9"/>all sides are '
                 '<bookmark mark="lbl9"/>equal,'
        ) as tracker:
            self.wait_until_bookmark("h9")
            self.play(FadeIn(heading9), run_time=0.5)
            self.wait_until_bookmark("r9")
            self.play(Create(rect9), run_time=0.8)
            self.wait_until_bookmark("morph9")
            self.play(Transform(rect9, sq9_target), run_time=0.8)
            self.wait_until_bookmark("lbl9")
            self.play(
                *[FadeIn(lb) for lb in s_labels9],
                FadeIn(equal_txt9),
                run_time=0.6,
            )

        # ──────────────────────────────────────────────
        # --- SCENE 10: Square Area (continuation) ---
        # ──────────────────────────────────────────────
        heading10 = create_heading_badge("Square Area")

        formula10 = MathTex(r"A = s^2", color=PURPLE, font_size=40)
        formula10.move_to(RIGHT * 2.5 + UP * 0.8)
        fbox10 = SurroundingRectangle(
            formula10, color=ORANGE_HL, corner_radius=0.15, buff=0.25, stroke_width=3
        )
        expanded10 = MathTex(r"A = s \times s", color=PURPLE, font_size=32)
        expanded10.next_to(formula10, DOWN, buff=0.6)

        with self.voiceover(
            text='<bookmark mark="h10"/>Area of a square equals '
                 '<bookmark mark="f10"/>side length '
                 '<bookmark mark="exp10"/>squared.'
        ) as tracker:
            self.wait_until_bookmark("h10")
            self.play(FadeOut(heading9), FadeIn(heading10), run_time=0.5)
            self.wait_until_bookmark("f10")
            self.play(Write(formula10), Create(fbox10), run_time=0.8)
            self.wait_until_bookmark("exp10")
            self.play(FadeIn(expanded10), run_time=0.6)
        self.wait(0.1)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.2)

        # ──────────────────────────────────────────────
        # --- SCENE 11: Transition ---
        # ──────────────────────────────────────────────
        trans11 = Text(
            "What happens when we draw a\ndiagonal inside a rectangle?",
            font="Poppins", font_size=32, color=PURPLE,
        ).move_to(ORIGIN)

        with self.voiceover(
            text='<bookmark mark="t11"/>Let us explore what happens when we '
                 "draw a diagonal inside a rectangle."
        ) as tracker:
            self.wait_until_bookmark("t11")
            self.play(Write(trans11), run_time=1.2)
        self.wait(0.15)
        self.play(FadeOut(trans11))

        # ──────────────────────────────────────────────
        # --- SCENE 12: Diagonal Split ---
        # ──────────────────────────────────────────────
        heading12 = create_heading_badge("Diagonal Split")

        rect12 = Rectangle(width=4.5, height=3, color=PURPLE, stroke_width=2.5)
        rect12.move_to(ORIGIN + UP * 0.3)

        b_arr12 = DoubleArrow(
            rect12.get_corner(DL) + DOWN * 0.3,
            rect12.get_corner(DR) + DOWN * 0.3,
            color=PURPLE, stroke_width=2, buff=0, tip_length=0.15,
        )
        b_lbl12 = Text("length", font="Poppins", font_size=18, color=PURPLE)
        b_lbl12.next_to(b_arr12, DOWN, buff=0.1)

        l_arr12 = DoubleArrow(
            rect12.get_corner(UL) + LEFT * 0.3,
            rect12.get_corner(DL) + LEFT * 0.3,
            color=PURPLE, stroke_width=2, buff=0, tip_length=0.15,
        )
        l_lbl12 = Text("width", font="Poppins", font_size=18, color=PURPLE)
        l_lbl12.next_to(l_arr12, LEFT, buff=0.1)

        diag12 = Line(
            rect12.get_corner(UL), rect12.get_corner(DR),
            color=ORANGE_HL, stroke_width=3,
        )

        tri1_fill = Polygon(
            rect12.get_corner(UL), rect12.get_corner(UR), rect12.get_corner(DR),
            fill_color=PURPLE, fill_opacity=0.12, stroke_width=0,
        )
        tri2_fill = Polygon(
            rect12.get_corner(UL), rect12.get_corner(DL), rect12.get_corner(DR),
            fill_color=ORANGE_HL, fill_opacity=0.12, stroke_width=0,
        )

        tri1_lbl = Text("Triangle 1", font="Poppins", font_size=16, color=PURPLE)
        tri1_lbl.move_to(rect12.get_center() + UP * 0.5 + RIGHT * 0.4)
        tri2_lbl = Text("Triangle 2", font="Poppins", font_size=16, color=PURPLE)
        tri2_lbl.move_to(rect12.get_center() + DOWN * 0.5 + LEFT * 0.4)

        cong_sym = MathTex(r"\cong", color=ORANGE_HL, font_size=36)
        cong_sym.next_to(rect12, RIGHT, buff=0.6)

        with self.voiceover(
            text='<bookmark mark="h12"/>The diagonal of a rectangle '
                 '<bookmark mark="r12"/>divides it into '
                 '<bookmark mark="d12"/>two '
                 '<bookmark mark="diag12"/>congruent '
                 '<bookmark mark="fills12"/>triangles.'
                 '<bookmark mark="labels12"/>'
        ) as tracker:
            self.wait_until_bookmark("h12")
            self.play(FadeIn(heading12), run_time=0.5)
            self.wait_until_bookmark("r12")
            self.play(Create(rect12), run_time=0.8)
            self.wait_until_bookmark("d12")
            self.play(
                GrowFromCenter(b_arr12), FadeIn(b_lbl12),
                GrowFromCenter(l_arr12), FadeIn(l_lbl12),
                run_time=0.6,
            )
            self.wait_until_bookmark("diag12")
            self.play(Create(diag12), run_time=0.8)
            self.wait_until_bookmark("fills12")
            self.play(FadeIn(tri1_fill), FadeIn(tri2_fill), run_time=0.6)
            self.wait_until_bookmark("labels12")
            self.play(
                FadeIn(tri1_lbl), FadeIn(tri2_lbl), FadeIn(cong_sym),
                run_time=0.6,
            )

        # ──────────────────────────────────────────────
        # --- SCENE 13: Triangle Area (continuation) ---
        # ──────────────────────────────────────────────
        heading13 = create_heading_badge("Triangle Area")

        tri_formula = MathTex(
            r"A_{\triangle} = \frac{1}{2} \times l \times w",
            color=PURPLE, font_size=36,
        )
        tri_formula.next_to(rect12, DOWN, buff=1.0)
        tri_fbox = SurroundingRectangle(
            tri_formula, color=ORANGE_HL, corner_radius=0.15, buff=0.2, stroke_width=3
        )

        with self.voiceover(
            text='<bookmark mark="h13"/>Each triangle has an area equal to '
                 '<bookmark mark="hl13"/>half the area of the rectangle. '
                 '<bookmark mark="tf13"/>Area of each triangle equals one half '
                 "times length times width."
        ) as tracker:
            self.wait_until_bookmark("h13")
            self.play(FadeOut(heading12), FadeIn(heading13), run_time=0.5)
            self.wait_until_bookmark("hl13")
            self.play(
                tri2_fill.animate.set_fill(opacity=0.04),
                tri1_fill.animate.set_fill(ORANGE_HL, opacity=0.25),
                run_time=0.6,
            )
            self.wait_until_bookmark("tf13")
            self.play(Write(tri_formula), Create(tri_fbox), run_time=0.8)
        self.wait(0.1)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.2)

        # ──────────────────────────────────────────────
        # --- SCENE 14: Transition ---
        # ──────────────────────────────────────────────
        trans14 = Text(
            "Perimeter vs. Area:\nAn important distinction",
            font="Poppins", font_size=32, color=PURPLE,
        ).move_to(ORIGIN)

        with self.voiceover(
            text='<bookmark mark="t14"/>Let us now look into an important '
                 "distinction between perimeter and area."
        ) as tracker:
            self.wait_until_bookmark("t14")
            self.play(Write(trans14), run_time=1.2)
        self.wait(0.15)
        self.play(FadeOut(trans14))

        # ──────────────────────────────────────────────
        # --- SCENE 15: Perimeter ---
        # ──────────────────────────────────────────────
        heading15 = create_heading_badge("Perimeter")

        rect15 = Rectangle(width=4, height=2.5, color=PURPLE, stroke_width=2.5)
        rect15.move_to(ORIGIN + UP * 0.5)

        rect15_trace = rect15.copy().set_stroke(ORANGE_HL, width=4)

        boundary_txt = Text(
            "Boundary", font="Poppins", font_size=28, color=ORANGE_HL, weight=BOLD
        ).next_to(rect15, UP, buff=0.4)

        peri_desc = Text(
            "Total length of the boundary",
            font="Poppins", font_size=22, color=PURPLE,
        ).next_to(rect15, DOWN, buff=0.8)

        with self.voiceover(
            text='<bookmark mark="h15"/>Perimeter is the '
                 '<bookmark mark="r15"/>total length of '
                 '<bookmark mark="trace15"/>the '
                 '<bookmark mark="btxt15"/>boundary,'
        ) as tracker:
            self.wait_until_bookmark("h15")
            self.play(FadeIn(heading15), run_time=0.5)
            self.wait_until_bookmark("r15")
            self.play(Create(rect15), run_time=0.8)
            self.wait_until_bookmark("trace15")
            self.play(Create(rect15_trace), run_time=1.5)
            self.wait_until_bookmark("btxt15")
            self.play(FadeIn(boundary_txt), FadeIn(peri_desc), run_time=0.6)

        # ──────────────────────────────────────────────
        # --- SCENE 16: Area (continuation) ---
        # ──────────────────────────────────────────────
        heading16 = create_heading_badge("Area")

        rect15_fill = rect15.copy().set_fill(ORANGE_HL, opacity=0.2).set_stroke(width=0)

        surface_txt = Text(
            "Surface", font="Poppins", font_size=28, color=ORANGE_HL, weight=BOLD
        ).move_to(rect15.get_center())

        area_desc16 = Text(
            "Surface enclosed within",
            font="Poppins", font_size=22, color=PURPLE,
        ).next_to(rect15, DOWN, buff=0.8)

        with self.voiceover(
            text='<bookmark mark="h16"/>while area measures the '
                 '<bookmark mark="fade16"/>surface '
                 '<bookmark mark="fill16"/>enclosed '
                 '<bookmark mark="stxt16"/>within.'
        ) as tracker:
            self.wait_until_bookmark("h16")
            self.play(FadeOut(heading15), FadeIn(heading16), run_time=0.5)
            self.wait_until_bookmark("fade16")
            self.play(FadeOut(rect15_trace), FadeOut(boundary_txt), run_time=0.5)
            self.wait_until_bookmark("fill16")
            self.play(FadeIn(rect15_fill), run_time=0.6)
            self.wait_until_bookmark("stxt16")
            self.play(
                FadeIn(surface_txt),
                Transform(peri_desc, area_desc16),
                run_time=0.6,
            )
        self.wait(0.1)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.2)

        # ──────────────────────────────────────────────
        # --- SCENE 17: Key Insight ---
        # ──────────────────────────────────────────────
        heading17 = create_heading_badge("Key Insight")

        insight17 = Text(
            "Two regions can have the\nsame perimeter but different areas!",
            font="Poppins", font_size=28, color=PURPLE,
        ).move_to(ORIGIN)

        with self.voiceover(
            text='<bookmark mark="h17"/>Two regions can have the '
                 '<bookmark mark="ins17"/>same perimeter but different areas.'
        ) as tracker:
            self.wait_until_bookmark("h17")
            self.play(FadeIn(heading17), run_time=0.5)
            self.wait_until_bookmark("ins17")
            self.play(Write(insight17), run_time=1.0)
        self.wait(0.1)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.2)

        # ──────────────────────────────────────────────
        # --- SCENE 18: Example Rect 1 ---
        # ──────────────────────────────────────────────
        heading18 = create_heading_badge("Example: Rect 1")

        rect18 = Rectangle(width=3.5, height=1.5, color=PURPLE, stroke_width=2.5)
        rect18.move_to(LEFT * 3 + UP * 1.0)

        b_arr18 = DoubleArrow(
            rect18.get_corner(DL) + DOWN * 0.25,
            rect18.get_corner(DR) + DOWN * 0.25,
            color=PURPLE, stroke_width=2, buff=0, tip_length=0.12,
        )
        b_lbl18 = Text("7 cm", font="Poppins", font_size=16, color=PURPLE)
        b_lbl18.next_to(b_arr18, DOWN, buff=0.08)

        l_arr18 = DoubleArrow(
            rect18.get_corner(UL) + LEFT * 0.25,
            rect18.get_corner(DL) + LEFT * 0.25,
            color=PURPLE, stroke_width=2, buff=0, tip_length=0.12,
        )
        l_lbl18 = Text("3 cm", font="Poppins", font_size=16, color=PURPLE)
        l_lbl18.next_to(l_arr18, LEFT, buff=0.08)

        peri18 = MathTex(
            r"P = 2(7+3) = 20 \text{ cm}", color=PURPLE, font_size=28
        ).next_to(rect18, DOWN, buff=0.8)
        area18 = MathTex(
            r"A = 7 \times 3 = 21 \text{ cm}^2", color=ORANGE_HL, font_size=28
        ).next_to(peri18, DOWN, buff=0.3)

        with self.voiceover(
            text='<bookmark mark="h18"/>For instance, a rectangle of '
                 '<bookmark mark="r18"/>7 centimeters by 3 centimeters '
                 '<bookmark mark="d18"/>has a perimeter of '
                 '<bookmark mark="p18"/>20 centimeters and an area of '
                 '<bookmark mark="a18"/>21 centimeter square.'
        ) as tracker:
            self.wait_until_bookmark("h18")
            self.play(FadeIn(heading18), run_time=0.5)
            self.wait_until_bookmark("r18")
            self.play(Create(rect18), run_time=0.6)
            self.wait_until_bookmark("d18")
            self.play(
                GrowFromCenter(b_arr18), FadeIn(b_lbl18),
                GrowFromCenter(l_arr18), FadeIn(l_lbl18),
                run_time=0.5,
            )
            self.wait_until_bookmark("p18")
            self.play(Write(peri18), run_time=0.6)
            self.wait_until_bookmark("a18")
            self.play(Write(area18), run_time=0.6)

        # ──────────────────────────────────────────────
        # --- SCENE 19: Example Rect 2 (continuation) ---
        # ──────────────────────────────────────────────
        rect19 = Rectangle(width=4.5, height=0.5, color=PURPLE, stroke_width=2.5)
        rect19.move_to(RIGHT * 3 + UP * 1.0)

        b_arr19 = DoubleArrow(
            rect19.get_corner(DL) + DOWN * 0.25,
            rect19.get_corner(DR) + DOWN * 0.25,
            color=PURPLE, stroke_width=2, buff=0, tip_length=0.12,
        )
        b_lbl19 = Text("9 cm", font="Poppins", font_size=16, color=PURPLE)
        b_lbl19.next_to(b_arr19, DOWN, buff=0.08)

        l_arr19 = DoubleArrow(
            rect19.get_corner(UL) + LEFT * 0.25,
            rect19.get_corner(DL) + LEFT * 0.25,
            color=PURPLE, stroke_width=2, buff=0, tip_length=0.12,
        )
        l_lbl19 = Text("1 cm", font="Poppins", font_size=16, color=PURPLE)
        l_lbl19.next_to(l_arr19, LEFT, buff=0.08)

        peri19 = MathTex(
            r"P = 2(9+1) = 20 \text{ cm}", color=PURPLE, font_size=28
        ).next_to(rect19, DOWN, buff=0.8)
        area19 = MathTex(
            r"A = 9 \times 1 = 9 \text{ cm}^2", color=ORANGE_HL, font_size=28
        ).next_to(peri19, DOWN, buff=0.3)

        with self.voiceover(
            text='<bookmark mark="r19"/>And a rectangle of 9 centimeters '
                 "by 1 centimeter "
                 '<bookmark mark="d19"/>also has a perimeter of '
                 '<bookmark mark="p19"/>20 centimeters, yet its area is only '
                 '<bookmark mark="a19"/>9 centimeter square.'
        ) as tracker:
            self.wait_until_bookmark("r19")
            self.play(Create(rect19), run_time=0.6)
            self.wait_until_bookmark("d19")
            self.play(
                GrowFromCenter(b_arr19), FadeIn(b_lbl19),
                GrowFromCenter(l_arr19), FadeIn(l_lbl19),
                run_time=0.5,
            )
            self.wait_until_bookmark("p19")
            self.play(Write(peri19), run_time=0.6)
            self.wait_until_bookmark("a19")
            self.play(Write(area19), run_time=0.6)

        # ──────────────────────────────────────────────
        # --- SCENE 20: Conclusion (continuation) ---
        # ──────────────────────────────────────────────
        heading20 = create_heading_badge("Conclusion")

        conclusion_txt = Text(
            "Perimeter alone cannot determine area",
            font="Poppins", font_size=24, color=ORANGE_HL, weight=BOLD,
        ).to_edge(DOWN, buff=0.5)
        conclusion_box = SurroundingRectangle(
            conclusion_txt, color=ORANGE_HL, corner_radius=0.15,
            buff=0.2, stroke_width=3,
        )

        with self.voiceover(
            text='<bookmark mark="h20"/>Therefore, '
                 '<bookmark mark="conc20"/>perimeter alone cannot determine area.'
        ) as tracker:
            self.wait_until_bookmark("h20")
            self.play(FadeOut(heading18), FadeIn(heading20), run_time=0.5)
            self.wait_until_bookmark("conc20")
            self.play(
                Write(conclusion_txt), Create(conclusion_box), run_time=0.8
            )
        self.wait(0.15)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.2)

        # ──────────────────────────────────────────────
        # --- SCENE 21: Transition ---
        # ──────────────────────────────────────────────
        trans21 = Text(
            "Let's apply the rectangle area formula\nin a real-life path problem!",
            font="Poppins", font_size=32, color=PURPLE,
        ).move_to(ORIGIN)

        with self.voiceover(
            text='<bookmark mark="t21"/>Now let us apply the rectangle area '
                 "formula in a real-life path problem."
        ) as tracker:
            self.wait_until_bookmark("t21")
            self.play(Write(trans21), run_time=1.2)
        self.wait(0.15)
        self.play(FadeOut(trans21))

        # ──────────────────────────────────────────────
        # --- SCENE 22: Example 1 — Question  [FIX APPLIED]
        # ──────────────────────────────────────────────
        heading22 = create_heading_badge("Example 1")

        q22 = Text(
            "A rectangular field measures 40 m by 25 m.\n"
            "A path of width 5 m runs along the inside\n"
            "boundary. Find the area of the path.",
            font="Poppins", font_size=22, color=PURPLE, line_spacing=1.3,
        ).to_edge(UP, buff=1.0).shift(LEFT * 1.5)

        outer22 = Rectangle(width=4, height=2.5, color=PURPLE, stroke_width=2.5)
        outer22.move_to(RIGHT * 2.5 + DOWN * 0.5)

        inner22 = Rectangle(
            width=3, height=1.5, color=PURPLE, stroke_width=2,
            fill_color=LAVENDER_BG, fill_opacity=1,
        )
        inner22.move_to(outer22.get_center())

        ob_arr22 = DoubleArrow(
            outer22.get_corner(DL) + DOWN * 0.3,
            outer22.get_corner(DR) + DOWN * 0.3,
            color=PURPLE, stroke_width=2, buff=0, tip_length=0.12,
        )
        ob_lbl22 = Text("40 m", font="Poppins", font_size=16, color=PURPLE)
        ob_lbl22.next_to(ob_arr22, DOWN, buff=0.08)

        ol_arr22 = DoubleArrow(
            outer22.get_corner(UL) + LEFT * 0.3,
            outer22.get_corner(DL) + LEFT * 0.3,
            color=PURPLE, stroke_width=2, buff=0, tip_length=0.12,
        )
        ol_lbl22 = Text("25 m", font="Poppins", font_size=16, color=PURPLE)
        ol_lbl22.next_to(ol_arr22, LEFT, buff=0.08)

        pw_lbl22 = Text("5 m", font="Poppins", font_size=14, color=PURPLE)
        pw_lbl22.move_to(
            (outer22.get_edge_center(UP) + inner22.get_edge_center(UP)) / 2
        )

        qmark22 = Text(
            "Area of path = ?",
            font="Poppins", font_size=22, color=ORANGE_HL, weight=BOLD,
        ).next_to(outer22, DOWN, buff=1.0)

        with self.voiceover(
            text='<bookmark mark="h22"/>A rectangular field measures '
                 '<bookmark mark="q22"/>40 meters by 25 meters. '
                 '<bookmark mark="out22"/>A path of width 5 meters '
                 '<bookmark mark="fill22"/>runs along the '
                 '<bookmark mark="in22"/>inside boundary. '
                 '<bookmark mark="qm22"/>Find the area of the path.'
        ) as tracker:
            self.wait_until_bookmark("h22")
            self.play(FadeIn(heading22), run_time=0.5)
            self.wait_until_bookmark("q22")
            self.play(Write(q22), run_time=1.0)
            self.wait_until_bookmark("out22")
            self.play(
                Create(outer22),
                GrowFromCenter(ob_arr22), FadeIn(ob_lbl22),
                GrowFromCenter(ol_arr22), FadeIn(ol_lbl22),
                run_time=0.8,
            )
            self.wait_until_bookmark("fill22")
            self.play(
                outer22.animate.set_fill(ORANGE_HL, opacity=0.15),
                run_time=0.2,
            )
            self.wait_until_bookmark("in22")
            self.play(Create(inner22), FadeIn(pw_lbl22), run_time=0.6)
            self.wait_until_bookmark("qm22")
            self.play(FadeIn(qmark22), run_time=0.5)
        self.wait(0.1)
        self.play(FadeOut(q22), FadeOut(heading22), FadeOut(qmark22), run_time=0.4)

        # ──────────────────────────────────────────────
        # --- SCENE 23: Solution — Given ---
        # ──────────────────────────────────────────────
        heading23 = create_heading_badge("Solution")

        gvn_t23 = Text(
            "Given:", font="Poppins", font_size=24, color=PURPLE, weight=BOLD
        ).move_to(LEFT * 3.5 + UP * 2.5)
        gvn1_23 = Text(
            "Outer length = 40 m", font="Poppins", font_size=20, color=PURPLE
        ).next_to(gvn_t23, DOWN, buff=0.3, aligned_edge=LEFT)
        gvn2_23 = Text(
            "Outer width = 25 m", font="Poppins", font_size=20, color=PURPLE
        ).next_to(gvn1_23, DOWN, buff=0.2, aligned_edge=LEFT)
        gvn3_23 = Text(
            "Path width = 5 m", font="Poppins", font_size=20, color=PURPLE
        ).next_to(gvn2_23, DOWN, buff=0.2, aligned_edge=LEFT)

        with self.voiceover(
            text='<bookmark mark="h23"/>Solution. '
                 '<bookmark mark="gt23"/>Given: '
                 '<bookmark mark="g1_23"/>Outer length equals 40 meters, '
                 '<bookmark mark="g2_23"/>outer width equals 25 meters, '
                 '<bookmark mark="g3_23"/>path width equals 5 meters.'
        ) as tracker:
            self.wait_until_bookmark("h23")
            self.play(FadeIn(heading23), run_time=0.5)
            self.wait_until_bookmark("gt23")
            self.play(FadeIn(gvn_t23), run_time=0.4)
            self.wait_until_bookmark("g1_23")
            self.play(FadeIn(gvn1_23), run_time=0.4)
            self.wait_until_bookmark("g2_23")
            self.play(FadeIn(gvn2_23), run_time=0.4)
            self.wait_until_bookmark("g3_23")
            self.play(FadeIn(gvn3_23), run_time=0.4)

        # ──────────────────────────────────────────────
        # --- SCENE 24: Step 1 — Outer Area ---
        # ──────────────────────────────────────────────
        left_items_23 = VGroup(gvn_t23, gvn1_23, gvn2_23, gvn3_23)

        s1_t24 = Text(
            "Step 1:", font="Poppins", font_size=20, color=PURPLE, weight=BOLD
        ).next_to(gvn3_23, DOWN, buff=0.5, aligned_edge=LEFT)
        s1_calc24 = MathTex(
            r"A_{\text{outer}} = 40 \times 25", color=PURPLE, font_size=30
        ).next_to(s1_t24, DOWN, buff=0.2, aligned_edge=LEFT)
        s1_res24 = MathTex(
            r"= 1000 \text{ m}^2", color=ORANGE_HL, font_size=30
        ).next_to(s1_calc24, RIGHT, buff=0.2)

        with self.voiceover(
            text='<bookmark mark="s1t24"/>Area of the outer rectangle equals '
                 '<bookmark mark="s1c24"/>40 times 25, '
                 '<bookmark mark="s1r24"/>which equals 1000 meter square.'
        ) as tracker:
            self.wait_until_bookmark("s1t24")
            self.play(
                FadeIn(s1_t24),
                outer22.animate.set_stroke(ORANGE_HL, width=3),
                run_time=0.5,
            )
            self.wait_until_bookmark("s1c24")
            self.play(Write(s1_calc24), run_time=0.6)
            self.wait_until_bookmark("s1r24")
            self.play(Write(s1_res24), run_time=0.5)
        self.play(outer22.animate.set_stroke(PURPLE, width=2.5), run_time=0.3)

        # ──────────────────────────────────────────────
        # --- SCENE 25: Step 2 — Inner Length ---
        # ──────────────────────────────────────────────
        self.play(
            FadeOut(left_items_23), FadeOut(s1_t24),
            FadeOut(s1_calc24), FadeOut(s1_res24),
            run_time=0.2,
        )

        s2_t25 = Text(
            "Step 2:", font="Poppins", font_size=20, color=PURPLE, weight=BOLD
        ).move_to(LEFT * 3.5 + UP * 2.5)
        il_calc25 = MathTex(
            r"\text{Inner length} = 40 - (2 \times 5)",
            color=PURPLE, font_size=28,
        ).next_to(s2_t25, DOWN, buff=0.3, aligned_edge=LEFT)
        il_res25 = MathTex(
            r"= 40 - 10 = 30 \text{ m}", color=ORANGE_HL, font_size=28
        ).next_to(il_calc25, DOWN, buff=0.2, aligned_edge=LEFT)

        with self.voiceover(
            text='<bookmark mark="s2t25"/>Inner length equals '
                 '<bookmark mark="ilc25"/>40 minus 2 times 5, '
                 '<bookmark mark="ilr25"/>which equals 30 meters.'
        ) as tracker:
            self.wait_until_bookmark("s2t25")
            self.play(FadeIn(s2_t25), run_time=0.4)
            self.wait_until_bookmark("ilc25")
            self.play(Write(il_calc25), run_time=0.6)
            self.wait_until_bookmark("ilr25")
            self.play(Write(il_res25), run_time=0.5)

        # ──────────────────────────────────────────────
        # --- SCENE 26: Inner Width ---
        # ──────────────────────────────────────────────
        iw_calc26 = MathTex(
            r"\text{Inner width} = 25 - (2 \times 5)",
            color=PURPLE, font_size=28,
        ).next_to(il_res25, DOWN, buff=0.4, aligned_edge=LEFT)
        iw_res26 = MathTex(
            r"= 25 - 10 = 15 \text{ m}", color=ORANGE_HL, font_size=28
        ).next_to(iw_calc26, DOWN, buff=0.2, aligned_edge=LEFT)

        with self.voiceover(
            text='<bookmark mark="iwc26"/>Inner width equals 25 minus 2 times 5, '
                 '<bookmark mark="iwr26"/>which equals 15 meters.'
        ) as tracker:
            self.wait_until_bookmark("iwc26")
            self.play(Write(iw_calc26), run_time=0.6)
            self.wait_until_bookmark("iwr26")
            self.play(Write(iw_res26), run_time=0.5)

        # ──────────────────────────────────────────────
        # --- SCENE 27: Step 3 — Inner Area ---
        # ──────────────────────────────────────────────
        self.play(
            FadeOut(s2_t25), FadeOut(il_calc25), FadeOut(il_res25),
            FadeOut(iw_calc26), FadeOut(iw_res26),
            run_time=0.2,
        )

        s3_t27 = Text(
            "Step 3:", font="Poppins", font_size=20, color=PURPLE, weight=BOLD
        ).move_to(LEFT * 3.5 + UP * 2.5)
        ia_calc27 = MathTex(
            r"A_{\text{inner}} = 30 \times 15", color=PURPLE, font_size=30
        ).next_to(s3_t27, DOWN, buff=0.3, aligned_edge=LEFT)
        ia_res27 = MathTex(
            r"= 450 \text{ m}^2", color=ORANGE_HL, font_size=30
        ).next_to(ia_calc27, RIGHT, buff=0.2)

        with self.voiceover(
            text='<bookmark mark="s3t27"/>Area of the inner rectangle equals '
                 '<bookmark mark="iac27"/>30 times 15, '
                 '<bookmark mark="iar27"/>which equals 450 meter square.'
        ) as tracker:
            self.wait_until_bookmark("s3t27")
            self.play(
                FadeIn(s3_t27),
                inner22.animate.set_stroke(ORANGE_HL, width=3),
                run_time=0.5,
            )
            self.wait_until_bookmark("iac27")
            self.play(Write(ia_calc27), run_time=0.6)
            self.wait_until_bookmark("iar27")
            self.play(Write(ia_res27), run_time=0.5)
        self.play(inner22.animate.set_stroke(PURPLE, width=2), run_time=0.3)

        # ──────────────────────────────────────────────
        # --- SCENE 28: Step 4 — Path Area ---
        # ──────────────────────────────────────────────
        self.play(
            FadeOut(s3_t27), FadeOut(ia_calc27), FadeOut(ia_res27),
            run_time=0.2,
        )

        s4_t28 = Text(
            "Step 4:", font="Poppins", font_size=20, color=PURPLE, weight=BOLD
        ).move_to(LEFT * 3.5 + UP * 2.5)
        pa_calc28 = MathTex(
            r"A_{\text{path}} = 1000 - 450", color=PURPLE, font_size=30
        ).next_to(s4_t28, DOWN, buff=0.3, aligned_edge=LEFT)
        pa_res28 = MathTex(
            r"= 550 \text{ m}^2", color=ORANGE_HL, font_size=36
        ).next_to(pa_calc28, DOWN, buff=0.3, aligned_edge=LEFT)
        pa_box28 = SurroundingRectangle(
            pa_res28, color=ORANGE_HL, corner_radius=0.15,
            buff=0.2, stroke_width=3,
        )

        with self.voiceover(
            text='<bookmark mark="s4t28"/>Area of the path equals '
                 '<bookmark mark="pac28"/>1000 minus 450, '
                 '<bookmark mark="par28"/>which equals 550 meter square.'
        ) as tracker:
            self.wait_until_bookmark("s4t28")
            self.play(FadeIn(s4_t28), run_time=0.4)
            self.wait_until_bookmark("pac28")
            self.play(Write(pa_calc28), run_time=0.6)
            self.wait_until_bookmark("par28")
            self.play(Write(pa_res28), Create(pa_box28), run_time=0.8)
        self.wait(0.15)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.2)

        # ──────────────────────────────────────────────
        # --- SCENE 29: Transition ---
        # ──────────────────────────────────────────────
        trans29 = Text(
            "Let's explore another real-life\nsituation involving cross paths!",
            font="Poppins", font_size=32, color=PURPLE,
        ).move_to(ORIGIN)

        with self.voiceover(
            text='<bookmark mark="t29"/>Let us explore another real-life '
                 "situation involving cross paths."
        ) as tracker:
            self.wait_until_bookmark("t29")
            self.play(Write(trans29), run_time=1.2)
        self.wait(0.15)
        self.play(FadeOut(trans29))

        # ──────────────────────────────────────────────
        # --- SCENE 30: Example 2 — Question ---
        # ──────────────────────────────────────────────
        heading30 = create_heading_badge("Example 2")

        q30 = Text(
            "A rectangular plot measures 18 m by 10 m.\n"
            "Two paths, each 3 m wide, cross it — one\n"
            "parallel to the length, one parallel to the\n"
            "breadth. Find the area of the crosspath.",
            font="Poppins", font_size=20, color=PURPLE, line_spacing=1.2,
        ).to_edge(UP, buff=1.0).shift(LEFT * 2.5)

        plot30 = Rectangle(width=4.5, height=2.5, color=PURPLE, stroke_width=2.5)
        plot30.move_to(RIGHT * 2.5 + DOWN * 0.3)

        pb_arr30 = DoubleArrow(
            plot30.get_corner(DL) + DOWN * 0.3,
            plot30.get_corner(DR) + DOWN * 0.3,
            color=PURPLE, stroke_width=2, buff=0, tip_length=0.12,
        )
        pb_lbl30 = Text("18 m", font="Poppins", font_size=16, color=PURPLE)
        pb_lbl30.next_to(pb_arr30, DOWN, buff=0.08)

        pl_arr30 = DoubleArrow(
            plot30.get_corner(UL) + LEFT * 0.3,
            plot30.get_corner(DL) + LEFT * 0.3,
            color=PURPLE, stroke_width=2, buff=0, tip_length=0.12,
        )
        pl_lbl30 = Text("10 m", font="Poppins", font_size=16, color=PURPLE)
        pl_lbl30.next_to(pl_arr30, LEFT, buff=0.08)

        h_strip30 = Rectangle(
            width=4.5, height=0.75,
            color=ORANGE_HL, stroke_width=1,
            fill_color=ORANGE_HL, fill_opacity=0.15,
        ).move_to(plot30.get_center())

        v_strip30 = Rectangle(
            width=0.75, height=2.5,
            color=ORANGE_HL, stroke_width=1,
            fill_color=ORANGE_HL, fill_opacity=0.15,
        ).move_to(plot30.get_center())

        overlap30 = Rectangle(
            width=0.75, height=0.75,
            fill_color=ORANGE_HL, fill_opacity=0.35,
            stroke_width=1, stroke_color=ORANGE_HL,
        ).move_to(plot30.get_center())

        pw_lbl30 = Text("3 m", font="Poppins", font_size=14, color=PURPLE)
        pw_lbl30.next_to(h_strip30, RIGHT, buff=0.15)

        qm30 = Text(
            "Area of crosspath = ?",
            font="Poppins", font_size=20, color=ORANGE_HL, weight=BOLD,
        ).next_to(plot30, DOWN, buff=1.0)

        with self.voiceover(
            text='<bookmark mark="h30"/>A rectangular plot measures '
                 '<bookmark mark="q30"/>18 meters by 10 meters. Two paths, '
                 "each 3 meters wide, cross it — one parallel to the length, "
                 "one parallel to the breadth. "
                 '<bookmark mark="plt30"/>Find the area of '
                 '<bookmark mark="str30"/>the cross '
                 '<bookmark mark="olap30"/>path.'
                 '<bookmark mark="qm30"/>'
        ) as tracker:
            self.wait_until_bookmark("h30")
            self.play(FadeIn(heading30), run_time=0.5)
            self.wait_until_bookmark("q30")
            self.play(Write(q30), run_time=1.2)
            self.wait_until_bookmark("plt30")
            self.play(
                Create(plot30),
                GrowFromCenter(pb_arr30), FadeIn(pb_lbl30),
                GrowFromCenter(pl_arr30), FadeIn(pl_lbl30),
                run_time=0.8,
            )
            self.wait_until_bookmark("str30")
            self.play(
                FadeIn(h_strip30), FadeIn(v_strip30), FadeIn(pw_lbl30),
                run_time=0.6,
            )
            self.wait_until_bookmark("olap30")
            self.play(FadeIn(overlap30), run_time=0.4)
            self.wait_until_bookmark("qm30")
            self.play(FadeIn(qm30), run_time=0.4)
        self.wait(0.1)
        self.play(FadeOut(q30), FadeOut(heading30), FadeOut(qm30), run_time=0.4)

        # ──────────────────────────────────────────────
        # --- SCENE 31: Solution — Given ---
        # ──────────────────────────────────────────────
        heading31 = create_heading_badge("Solution")

        gt31 = Text(
            "Given:", font="Poppins", font_size=24, color=PURPLE, weight=BOLD
        ).move_to(LEFT * 3.5 + UP * 2.5)
        g1_31 = Text(
            "Plot length = 18 m", font="Poppins", font_size=20, color=PURPLE
        ).next_to(gt31, DOWN, buff=0.3, aligned_edge=LEFT)
        g2_31 = Text(
            "Plot breadth = 10 m", font="Poppins", font_size=20, color=PURPLE
        ).next_to(g1_31, DOWN, buff=0.2, aligned_edge=LEFT)
        g3_31 = Text(
            "Path width = 3 m", font="Poppins", font_size=20, color=PURPLE
        ).next_to(g2_31, DOWN, buff=0.2, aligned_edge=LEFT)

        with self.voiceover(
            text='<bookmark mark="h31"/>Solution. '
                 '<bookmark mark="gt31"/>Given: '
                 '<bookmark mark="g1_31"/>Plot length equals 18 meters, '
                 '<bookmark mark="g2_31"/>plot breadth equals 10 meters, '
                 '<bookmark mark="g3_31"/>path width equals 3 meters.'
        ) as tracker:
            self.wait_until_bookmark("h31")
            self.play(FadeIn(heading31), run_time=0.5)
            self.wait_until_bookmark("gt31")
            self.play(FadeIn(gt31), run_time=0.4)
            self.wait_until_bookmark("g1_31")
            self.play(FadeIn(g1_31), run_time=0.4)
            self.wait_until_bookmark("g2_31")
            self.play(FadeIn(g2_31), run_time=0.4)
            self.wait_until_bookmark("g3_31")
            self.play(FadeIn(g3_31), run_time=0.4)

        # ──────────────────────────────────────────────
        # --- SCENE 32: Horizontal Path Area ---
        # ──────────────────────────────────────────────
        self.play(
            FadeOut(gt31), FadeOut(g1_31), FadeOut(g2_31), FadeOut(g3_31),
            run_time=0.2,
        )

        s1_t32 = Text(
            "Step 1:", font="Poppins", font_size=20, color=PURPLE, weight=BOLD
        ).move_to(LEFT * 3.5 + UP * 2.5)
        hc32 = MathTex(
            r"A_{\text{horiz}} = 18 \times 3", color=PURPLE, font_size=28
        ).next_to(s1_t32, DOWN, buff=0.3, aligned_edge=LEFT)
        hr32 = MathTex(
            r"= 54 \text{ m}^2", color=ORANGE_HL, font_size=28
        ).next_to(hc32, RIGHT, buff=0.2)

        with self.voiceover(
            text='<bookmark mark="s1_32"/>Area of the horizontal path equals '
                 '<bookmark mark="hc32"/>18 times 3, '
                 '<bookmark mark="hr32"/>which equals 54 meter square.'
        ) as tracker:
            self.wait_until_bookmark("s1_32")
            self.play(
                FadeIn(s1_t32),
                h_strip30.animate.set_fill(ORANGE_HL, opacity=0.4),
                v_strip30.animate.set_fill(ORANGE_HL, opacity=0.08),
                overlap30.animate.set_fill(ORANGE_HL, opacity=0.08),
                run_time=0.5,
            )
            self.wait_until_bookmark("hc32")
            self.play(Write(hc32), run_time=0.6)
            self.wait_until_bookmark("hr32")
            self.play(Write(hr32), run_time=0.5)

        # ──────────────────────────────────────────────
        # --- SCENE 33: Vertical Path Area ---
        # ──────────────────────────────────────────────
        self.play(FadeOut(s1_t32), FadeOut(hc32), FadeOut(hr32), run_time=0.4)

        s2_t33 = Text(
            "Step 2:", font="Poppins", font_size=20, color=PURPLE, weight=BOLD
        ).move_to(LEFT * 3.5 + UP * 2.5)
        vc33 = MathTex(
            r"A_{\text{vert}} = 10 \times 3", color=PURPLE, font_size=28
        ).next_to(s2_t33, DOWN, buff=0.3, aligned_edge=LEFT)
        vr33 = MathTex(
            r"= 30 \text{ m}^2", color=ORANGE_HL, font_size=28
        ).next_to(vc33, RIGHT, buff=0.2)

        with self.voiceover(
            text='<bookmark mark="s2_33"/>Area of the vertical path equals '
                 '<bookmark mark="vc33"/>10 times 3, '
                 '<bookmark mark="vr33"/>which equals 30 meter square.'
        ) as tracker:
            self.wait_until_bookmark("s2_33")
            self.play(
                FadeIn(s2_t33),
                h_strip30.animate.set_fill(ORANGE_HL, opacity=0.08),
                v_strip30.animate.set_fill(ORANGE_HL, opacity=0.4),
                run_time=0.5,
            )
            self.wait_until_bookmark("vc33")
            self.play(Write(vc33), run_time=0.6)
            self.wait_until_bookmark("vr33")
            self.play(Write(vr33), run_time=0.5)

        # ──────────────────────────────────────────────
        # --- SCENE 34: Overlap Area ---
        # ──────────────────────────────────────────────
        self.play(FadeOut(s2_t33), FadeOut(vc33), FadeOut(vr33), run_time=0.4)

        s3_t34 = Text(
            "Step 3:", font="Poppins", font_size=20, color=PURPLE, weight=BOLD
        ).move_to(LEFT * 3.5 + UP * 2.5)
        oc34 = MathTex(
            r"A_{\text{overlap}} = 3 \times 3", color=PURPLE, font_size=28
        ).next_to(s3_t34, DOWN, buff=0.3, aligned_edge=LEFT)
        or34 = MathTex(
            r"= 9 \text{ m}^2", color=ORANGE_HL, font_size=28
        ).next_to(oc34, RIGHT, buff=0.2)

        with self.voiceover(
            text='<bookmark mark="s3_34"/>Area of the overlap equals '
                 '<bookmark mark="oc34"/>3 times 3, '
                 '<bookmark mark="or34"/>which equals 9 meter square.'
        ) as tracker:
            self.wait_until_bookmark("s3_34")
            self.play(
                FadeIn(s3_t34),
                h_strip30.animate.set_fill(ORANGE_HL, opacity=0.08),
                v_strip30.animate.set_fill(ORANGE_HL, opacity=0.08),
                overlap30.animate.set_fill(ORANGE_HL, opacity=0.5),
                run_time=0.5,
            )
            self.wait_until_bookmark("oc34")
            self.play(Write(oc34), run_time=0.6)
            self.wait_until_bookmark("or34")
            self.play(Write(or34), run_time=0.5)

        # ──────────────────────────────────────────────
        # --- SCENE 35: Crosspath Total ---
        # ──────────────────────────────────────────────
        self.play(FadeOut(s3_t34), FadeOut(oc34), FadeOut(or34), run_time=0.4)

        s4_t35 = Text(
            "Step 4:", font="Poppins", font_size=20, color=PURPLE, weight=BOLD
        ).move_to(LEFT * 3.5 + UP * 2.5)
        cpc35 = MathTex(
            r"A_{\text{crosspath}} = 54 + 30 - 9", color=PURPLE, font_size=28
        ).next_to(s4_t35, DOWN, buff=0.3, aligned_edge=LEFT)
        cpr35 = MathTex(
            r"= 75 \text{ m}^2", color=ORANGE_HL, font_size=36
        ).next_to(cpc35, DOWN, buff=0.3, aligned_edge=LEFT)
        cpb35 = SurroundingRectangle(
            cpr35, color=ORANGE_HL, corner_radius=0.15,
            buff=0.2, stroke_width=3,
        )

        with self.voiceover(
            text='<bookmark mark="s4_35"/>Area of the cross path equals '
                 '<bookmark mark="cpc35"/>54 plus 30 minus 9, '
                 '<bookmark mark="cpr35"/>which equals 75 meter square.'
        ) as tracker:
            self.wait_until_bookmark("s4_35")
            self.play(
                FadeIn(s4_t35),
                h_strip30.animate.set_fill(ORANGE_HL, opacity=0.3),
                v_strip30.animate.set_fill(ORANGE_HL, opacity=0.3),
                overlap30.animate.set_fill(ORANGE_HL, opacity=0.3),
                run_time=0.5,
            )
            self.wait_until_bookmark("cpc35")
            self.play(Write(cpc35), run_time=0.6)
            self.wait_until_bookmark("cpr35")
            self.play(Write(cpr35), Create(cpb35), run_time=0.8)
        self.wait(0.15)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.2)

        # ──────────────────────────────────────────────
        # --- SCENE 36: Transition ---
        # ──────────────────────────────────────────────
        trans36 = Text(
            "Now let's find the area of\na composite figure!",
            font="Poppins", font_size=32, color=PURPLE,
        ).move_to(ORIGIN)

        with self.voiceover(
            text='<bookmark mark="t36"/>Let us now look into finding '
                 "the area of a composite figure."
        ) as tracker:
            self.wait_until_bookmark("t36")
            self.play(Write(trans36), run_time=1.2)
        self.wait(0.15)
        self.play(FadeOut(trans36))

        # ──────────────────────────────────────────────
        # --- SCENE 37: Example 3 — Question ---
        # ──────────────────────────────────────────────
        heading37 = create_heading_badge("Example 3")

        q37 = Text(
            "An L-shaped figure is made of two rectangles:\n"
            "one measuring 9 cm by 4 cm and another\n"
            "measuring 6 cm by 3 cm. Find the total area.",
            font="Poppins", font_size=20, color=PURPLE, line_spacing=1.2,
        ).to_edge(UP, buff=1.0).shift(LEFT * 2)

        sc = 0.35
        r1_w, r1_h = 9 * sc, 4 * sc
        r2_w, r2_h = 6 * sc, 3 * sc

        rect1_37 = Rectangle(
            width=r1_w, height=r1_h, color=PURPLE, stroke_width=2.5
        )
        rect2_37 = Rectangle(
            width=r2_w, height=r2_h, color=PURPLE, stroke_width=2.5
        )

        l_shape_center = RIGHT * 2.5 + DOWN * 0.2
        rect1_37.move_to(l_shape_center + UP * r2_h / 2)
        rect2_37.next_to(rect1_37, DOWN, buff=0, aligned_edge=RIGHT)

        dash37 = DashedLine(
            rect2_37.get_corner(UL),
            rect1_37.get_corner(DR),
            color=PURPLE, stroke_width=1.5, dash_length=0.1,
        )

        r1_top_lbl = Text("9 cm", font="Poppins", font_size=14, color=PURPLE)
        r1_top_lbl.next_to(rect1_37, UP, buff=0.15)
        r1_left_lbl = Text("4 cm", font="Poppins", font_size=14, color=PURPLE)
        r1_left_lbl.next_to(rect1_37, LEFT, buff=0.15)

        r2_bot_lbl = Text("6 cm", font="Poppins", font_size=14, color=PURPLE)
        r2_bot_lbl.next_to(rect2_37, DOWN, buff=0.15)
        r2_right_lbl = Text("3 cm", font="Poppins", font_size=14, color=PURPLE)
        r2_right_lbl.next_to(rect2_37, RIGHT, buff=0.15)

        r1_ctr_lbl = Text("Rect 1", font="Poppins", font_size=14, color=PURPLE)
        r1_ctr_lbl.move_to(rect1_37.get_center())
        r2_ctr_lbl = Text("Rect 2", font="Poppins", font_size=14, color=PURPLE)
        r2_ctr_lbl.move_to(rect2_37.get_center())

        qm37 = Text(
            "Total Area = ?",
            font="Poppins", font_size=20, color=ORANGE_HL, weight=BOLD,
        ).next_to(VGroup(rect1_37, rect2_37), DOWN, buff=0.8)

        with self.voiceover(
            text='<bookmark mark="h37"/>An L-shaped figure is made of two rectangles: '
                 '<bookmark mark="q37"/>one measuring 9 centimeters by 4 centimeters and '
                 "another measuring 6 centimeters by 3 centimeters. "
                 '<bookmark mark="lshape37"/>Find the '
                 '<bookmark mark="lbls37"/>total '
                 '<bookmark mark="qm37"/>area.'
        ) as tracker:
            self.wait_until_bookmark("h37")
            self.play(FadeIn(heading37), run_time=0.5)
            self.wait_until_bookmark("q37")
            self.play(Write(q37), run_time=1.2)
            self.wait_until_bookmark("lshape37")
            self.play(
                Create(rect1_37), Create(rect2_37), Create(dash37),
                run_time=0.8,
            )
            self.wait_until_bookmark("lbls37")
            self.play(
                FadeIn(r1_top_lbl), FadeIn(r1_left_lbl),
                FadeIn(r2_bot_lbl), FadeIn(r2_right_lbl),
                FadeIn(r1_ctr_lbl), FadeIn(r2_ctr_lbl),
                run_time=0.6,
            )
            self.wait_until_bookmark("qm37")
            self.play(FadeIn(qm37), run_time=0.5)
        self.wait(0.1)
        self.play(FadeOut(q37), FadeOut(heading37), FadeOut(qm37), run_time=0.4)

        # ──────────────────────────────────────────────
        # --- SCENE 38: Solution — Given ---
        # ──────────────────────────────────────────────
        heading38 = create_heading_badge("Solution")

        gt38 = Text(
            "Given:", font="Poppins", font_size=24, color=PURPLE, weight=BOLD
        ).move_to(LEFT * 3.5 + UP * 2.5)
        g1_38 = Text(
            "Rectangle 1 = 9 cm × 4 cm",
            font="Poppins", font_size=20, color=PURPLE,
        ).next_to(gt38, DOWN, buff=0.3, aligned_edge=LEFT)
        g2_38 = Text(
            "Rectangle 2 = 6 cm × 3 cm",
            font="Poppins", font_size=20, color=PURPLE,
        ).next_to(g1_38, DOWN, buff=0.2, aligned_edge=LEFT)

        with self.voiceover(
            text='<bookmark mark="h38"/>Solution. '
                 '<bookmark mark="g38"/>Given: First rectangle is 9 centimeters '
                 "by 4 centimeters, "
                 '<bookmark mark="hl1_38"/>and the second rectangle is '
                 '<bookmark mark="hl2_38"/>6 centimeters by 3 centimeters.'
        ) as tracker:
            self.wait_until_bookmark("h38")
            self.play(FadeIn(heading38), run_time=0.5)
            self.wait_until_bookmark("g38")
            self.play(FadeIn(gt38), FadeIn(g1_38), run_time=0.5)
            self.wait_until_bookmark("hl1_38")
            self.play(
                rect1_37.animate.set_stroke(ORANGE_HL, width=3),
                FadeIn(g2_38),
                run_time=0.5,
            )
            self.wait_until_bookmark("hl2_38")
            self.play(
                rect1_37.animate.set_stroke(PURPLE, width=2.5),
                rect2_37.animate.set_stroke(ORANGE_HL, width=3),
                run_time=0.5,
            )
        self.play(rect2_37.animate.set_stroke(PURPLE, width=2.5), run_time=0.3)

        # ──────────────────────────────────────────────
        # --- SCENE 39: Area of Rectangle 1 ---
        # ──────────────────────────────────────────────
        self.play(FadeOut(gt38), FadeOut(g1_38), FadeOut(g2_38), run_time=0.4)

        s1_t39 = Text(
            "Step 1:", font="Poppins", font_size=20, color=PURPLE, weight=BOLD
        ).move_to(LEFT * 3.5 + UP * 2.5)
        a1c39 = MathTex(
            r"A_1 = 9 \times 4", color=PURPLE, font_size=30
        ).next_to(s1_t39, DOWN, buff=0.3, aligned_edge=LEFT)
        a1r39 = MathTex(
            r"= 36 \text{ cm}^2", color=ORANGE_HL, font_size=30
        ).next_to(a1c39, RIGHT, buff=0.2)

        with self.voiceover(
            text='<bookmark mark="s1_39"/>Area of the first rectangle equals '
                 '<bookmark mark="a1c39"/>9 times 4, '
                 '<bookmark mark="a1r39"/>which equals 36 centimeter square.'
        ) as tracker:
            self.wait_until_bookmark("s1_39")
            self.play(
                FadeIn(s1_t39),
                rect1_37.animate.set_fill(ORANGE_HL, opacity=0.2).set_stroke(
                    ORANGE_HL, width=3
                ),
                run_time=0.5,
            )
            self.wait_until_bookmark("a1c39")
            self.play(Write(a1c39), run_time=0.6)
            self.wait_until_bookmark("a1r39")
            self.play(Write(a1r39), run_time=0.5)

        # ──────────────────────────────────────────────
        # --- SCENE 40: Area of Rectangle 2 ---
        # ──────────────────────────────────────────────
        self.play(
            FadeOut(s1_t39), FadeOut(a1c39), FadeOut(a1r39),
            rect1_37.animate.set_fill(opacity=0).set_stroke(PURPLE, width=2.5),
            run_time=0.2,
        )

        s2_t40 = Text(
            "Step 2:", font="Poppins", font_size=20, color=PURPLE, weight=BOLD
        ).move_to(LEFT * 3.5 + UP * 2.5)
        a2c40 = MathTex(
            r"A_2 = 6 \times 3", color=PURPLE, font_size=30
        ).next_to(s2_t40, DOWN, buff=0.3, aligned_edge=LEFT)
        a2r40 = MathTex(
            r"= 18 \text{ cm}^2", color=ORANGE_HL, font_size=30
        ).next_to(a2c40, RIGHT, buff=0.2)

        with self.voiceover(
            text='<bookmark mark="s2_40"/>Area of the second rectangle equals '
                 '<bookmark mark="a2c40"/>6 times 3, '
                 '<bookmark mark="a2r40"/>which equals 18 centimeter square.'
        ) as tracker:
            self.wait_until_bookmark("s2_40")
            self.play(
                FadeIn(s2_t40),
                rect2_37.animate.set_fill(ORANGE_HL, opacity=0.2).set_stroke(
                    ORANGE_HL, width=3
                ),
                run_time=0.5,
            )
            self.wait_until_bookmark("a2c40")
            self.play(Write(a2c40), run_time=0.6)
            self.wait_until_bookmark("a2r40")
            self.play(Write(a2r40), run_time=0.5)

        # ──────────────────────────────────────────────
        # --- SCENE 41: Total Area ---
        # ──────────────────────────────────────────────
        self.play(
            FadeOut(s2_t40), FadeOut(a2c40), FadeOut(a2r40),
            run_time=0.2,
        )

        s3_t41 = Text(
            "Step 3:", font="Poppins", font_size=20, color=PURPLE, weight=BOLD
        ).move_to(LEFT * 3.5 + UP * 2.5)
        tc41 = MathTex(
            r"A_{\text{total}} = 36 + 18", color=PURPLE, font_size=30
        ).next_to(s3_t41, DOWN, buff=0.3, aligned_edge=LEFT)
        tr41 = MathTex(
            r"= 54 \text{ cm}^2", color=ORANGE_HL, font_size=36
        ).next_to(tc41, DOWN, buff=0.3, aligned_edge=LEFT)
        tb41 = SurroundingRectangle(
            tr41, color=ORANGE_HL, corner_radius=0.15,
            buff=0.2, stroke_width=3,
        )

        with self.voiceover(
            text='<bookmark mark="s3_41"/>Total area equals '
                 '<bookmark mark="tc41"/>36 plus 18, '
                 '<bookmark mark="tr41"/>which equals 54 centimeter square.'
        ) as tracker:
            self.wait_until_bookmark("s3_41")
            self.play(
                FadeIn(s3_t41),
                rect1_37.animate.set_fill(ORANGE_HL, opacity=0.2).set_stroke(
                    ORANGE_HL, width=3
                ),
                run_time=0.5,
            )
            self.wait_until_bookmark("tc41")
            self.play(Write(tc41), run_time=0.6)
            self.wait_until_bookmark("tr41")
            self.play(Write(tr41), Create(tb41), run_time=0.8)
        self.wait(0.15)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.2)

        # ──────────────────────────────────────────────
        # --- SCENE 42: Summary ---
        # ──────────────────────────────────────────────
        heading42 = create_heading_badge("Summary")

        s1_42 = Text(
            "• Area = number of unit squares covering a region",
            font="Poppins", font_size=22, color=PURPLE,
        )
        s2_42 = VGroup(
            Text("• ", font="Poppins", font_size=22, color=PURPLE),
            MathTex(r"A_{\text{rect}} = l \times w", color=PURPLE, font_size=28),
        ).arrange(RIGHT, buff=0.1)

        s3_42 = VGroup(
            Text("• ", font="Poppins", font_size=22, color=PURPLE),
            MathTex(r"A_{\text{square}} = s^2", color=PURPLE, font_size=28),
        ).arrange(RIGHT, buff=0.1)

        s4_42 = VGroup(
            Text("• ", font="Poppins", font_size=22, color=PURPLE),
            MathTex(
                r"A_{\triangle} = \frac{1}{2} \times l \times w",
                color=PURPLE, font_size=28,
            ),
        ).arrange(RIGHT, buff=0.1)

        s5_42 = Text(
            "• Perimeter ≠ Area",
            font="Poppins", font_size=22, color=ORANGE_HL, weight=BOLD,
        )
        s6_42 = Text(
            "• Composite areas = sum of individual areas",
            font="Poppins", font_size=22, color=PURPLE,
        )

        VGroup(
            s1_42, s2_42, s3_42, s4_42, s5_42, s6_42
        ).arrange(DOWN, buff=0.35, aligned_edge=LEFT).move_to(ORIGIN)

        with self.voiceover(
            text='<bookmark mark="h42"/>We have learned the concept of area '
                 '<bookmark mark="s1_42"/>and how to '
                 '<bookmark mark="s2_42"/>apply it '
                 '<bookmark mark="s3_42"/>to simple '
                 '<bookmark mark="s4_42"/>and '
                 '<bookmark mark="s5_42"/>complex '
                 '<bookmark mark="s6_42"/>shapes.'
        ) as tracker:
            self.wait_until_bookmark("h42")
            self.play(FadeIn(heading42), run_time=0.5)
            self.wait_until_bookmark("s1_42")
            self.play(FadeIn(s1_42, shift=UP * 0.2), run_time=0.5)
            self.wait_until_bookmark("s2_42")
            self.play(FadeIn(s2_42, shift=UP * 0.2), run_time=0.5)
            self.wait_until_bookmark("s3_42")
            self.play(FadeIn(s3_42, shift=UP * 0.2), run_time=0.5)
            self.wait_until_bookmark("s4_42")
            self.play(FadeIn(s4_42, shift=UP * 0.2), run_time=0.5)
            self.wait_until_bookmark("s5_42")
            self.play(FadeIn(s5_42, shift=UP * 0.2), run_time=0.5)
            self.wait_until_bookmark("s6_42")
            self.play(FadeIn(s6_42, shift=UP * 0.2), run_time=0.5)
        self.wait(0.15)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.2)