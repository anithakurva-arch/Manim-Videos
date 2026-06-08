from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.openai import OpenAIService


class Recs(VoiceoverScene):
    def construct(self):
        self.camera.background_color = "#1e1e2e"
        self.set_speech_service(
            OpenAIService(voice="nova", model="tts-1", transcription_model=None),
            create_subcaption=False,
        )

        def dima(s, e, lab, d, c=WHITE, fs=16):
            a = DoubleArrow(s, e, color=c, tip_length=0.1, stroke_width=2, buff=0)
            t = Text(lab, font_size=fs, color=c).next_to(a, d, buff=0.1)
            return VGroup(a, t)

        def heading(txt):
            return Text(txt, font_size=36, weight=BOLD, color=BLUE_C).to_corner(UL, buff=0.4)

        def bottom(txt):
            return Text(txt, font_size=22, color=YELLOW).to_edge(DOWN, buff=0.3)

        def clear(*args):
            self.play(FadeOut(VGroup(*args)))

        t1 = Text("Rectangles & Squares", font_size=58, weight=BOLD, color=BLUE_C)
        with self.voiceover(text="Hello students! In this lesson, we will understand how to measure the surface enclosed within flat shapes like rectangles and squares.") as tk:
            self.play(FadeIn(t1, shift=UP), run_time=tk.duration)
        self.wait(0.3)
        self.play(FadeOut(t1))

        h = heading("What is Area?")
        b = bottom("Measure of a 2D surface")
        r = Rectangle(width=4, height=3, color=BLUE_C, stroke_width=3).move_to(LEFT * 2.5)
        sq = VGroup(*[Square(side_length=1, color=YELLOW, fill_opacity=0.2, stroke_width=1).move_to(r.get_corner(DL) + RIGHT * (i + .5) + UP * (j + .5)) for i in range(4) for j in range(3)])
        d = Text("Area is the measure of the\nextent of a 2D surface,\ndetermined by counting unit\nsquares that fit within a\nregion without overlapping.", font_size=18, color=WHITE, line_spacing=1.3).next_to(r, RIGHT, buff=0.6)
        with self.voiceover(text="Area is the measure of the extent of a two-dimensional surface, determined by counting the number of unit squares which can also be a fraction that can fit within a given region without overlapping.") as tk:
            self.play(FadeIn(h), FadeIn(b), run_time=0.5)
            self.play(Create(r), run_time=0.5)
            self.play(FadeIn(sq, lag_ratio=0.04), run_time=1.5)
            self.play(FadeIn(d), run_time=max(0.5, tk.duration - 2.5))
        self.wait(0.3)
        clear(h, b, r, sq, d)

        h = heading("Unit Square")
        b = bottom("cm squared, m squared, in squared")
        u = Square(side_length=2, color=BLUE_C, fill_opacity=0.15, stroke_width=3).move_to(LEFT * 2.5)
        ab = dima(u.get_corner(DL) + DOWN * .3, u.get_corner(DR) + DOWN * .3, "1 unit", DOWN)
        ar = dima(u.get_corner(DR) + RIGHT * .3, u.get_corner(UR) + RIGHT * .3, "1 unit", RIGHT)
        ul = VGroup(Text("cm squared", font_size=24, color=GREEN_C), Text("m squared", font_size=24, color=GREEN_C), Text("in squared", font_size=24, color=GREEN_C)).arrange(DOWN, buff=0.35, aligned_edge=LEFT).move_to(RIGHT * 3)
        with self.voiceover(text="A unit square has a sidelength of 1 unit and is used to measure area, which is expressed as the number of such squares covering a region, in square units like cm squared, m squared, or in squared.") as tk:
            self.play(FadeIn(h), FadeIn(b), run_time=0.5)
            self.play(Create(u), run_time=0.5)
            self.play(FadeIn(ab), FadeIn(ar), run_time=0.7)
            self.play(FadeIn(ul, lag_ratio=0.3), run_time=max(0.5, tk.duration - 1.7))
        self.wait(0.3)
        clear(h, b, u, ab, ar, ul)

        tr = Text("How Unit Squares\nConnect to Area", font_size=38, weight=BOLD, color=BLUE_C)
        with self.voiceover(text="Now let us see how unit squares connect to the area formula for rectangles.") as tk:
            self.play(FadeIn(tr, shift=UP), run_time=1.0)
            self.wait(max(0.3, tk.duration - 1.0))
        self.wait(0.3)
        self.play(FadeOut(tr))

        h = heading("Area of Rectangle")
        b = bottom("Area = length times width")
        r5 = Rectangle(width=5, height=3, color=BLUE_C, stroke_width=3).move_to(LEFT * 1.5 + UP * 0.2)
        g5 = VGroup(*[Square(side_length=1, color=YELLOW, fill_opacity=0.12, stroke_width=0.8).move_to(r5.get_corner(DL) + RIGHT * (i + .5) + UP * (j + .5)) for i in range(5) for j in range(3)])
        dl = dima(r5.get_corner(DL) + DOWN * .35, r5.get_corner(DR) + DOWN * .35, "length = 5", DOWN)
        dw = dima(r5.get_corner(DL) + LEFT * .35, r5.get_corner(UL) + LEFT * .35, "width = 3", LEFT)
        f5 = MathTex(r"\text{Area} = l \times w", font_size=34, color=YELLOW).move_to(RIGHT * 4.5 + UP * 1)
        e5 = MathTex(r"= 5 \times 3 = 15\;\text{sq.units}", font_size=28, color=GREEN_C).next_to(f5, DOWN, buff=0.3)
        with self.voiceover(text="The number of unit squares contained in a rectangle equals the product of its length and width. This gives us: Area of a rectangle = length times width.") as tk:
            self.play(FadeIn(h), FadeIn(b), run_time=0.5)
            self.play(Create(r5), run_time=0.5)
            self.play(FadeIn(g5, lag_ratio=0.02), run_time=1.0)
            self.play(FadeIn(dl), FadeIn(dw), run_time=0.6)
            self.play(Write(f5), run_time=0.8)
            self.play(FadeIn(e5), run_time=max(0.5, tk.duration - 3.4))
        self.wait(0.3)
        clear(h, b, r5, g5, dl, dw, f5, e5)

        h = heading("Area of Square")
        b = bottom("Area = s squared")
        s6 = Square(side_length=2.5, color=GREEN_C, fill_opacity=0.15, stroke_width=3).move_to(LEFT * 2)
        a6 = VGroup(
            dima(s6.get_corner(DL) + DOWN * .3, s6.get_corner(DR) + DOWN * .3, "s", DOWN),
            dima(s6.get_corner(DR) + RIGHT * .3, s6.get_corner(UR) + RIGHT * .3, "s", RIGHT),
            dima(s6.get_corner(UL) + UP * .3, s6.get_corner(UR) + UP * .3, "s", UP),
            dima(s6.get_corner(DL) + LEFT * .3, s6.get_corner(UL) + LEFT * .3, "s", LEFT),
        )
        f6 = MathTex(r"\text{Area} = s^{2}", font_size=40, color=YELLOW).move_to(RIGHT * 3)
        with self.voiceover(text="Since a square is a special rectangle where all sides are equal: Area of a square = sidelength squared.") as tk:
            self.play(FadeIn(h), FadeIn(b), run_time=0.5)
            self.play(Create(s6), run_time=0.5)
            self.play(FadeIn(a6), run_time=0.6)
            self.play(Indicate(s6, color=YELLOW, scale_factor=1.05), run_time=0.5)
            self.play(Write(f6), run_time=max(0.5, tk.duration - 2.1))
        self.wait(0.3)
        clear(h, b, s6, a6, f6)

        h7 = heading("Diagonal Property")
        b7 = bottom("Diagonal creates Two Triangles")
        r7 = Rectangle(width=5, height=3, color=BLUE_C, stroke_width=3).move_to(LEFT * 1 + UP * 0.2)
        dg = Line(r7.get_corner(DL), r7.get_corner(UR), color=RED_C, stroke_width=3)
        with self.voiceover(text="Let us explore what happens when we draw a diagonal inside a rectangle.") as tk:
            self.play(FadeIn(h7), FadeIn(b7), run_time=0.5)
            self.play(Create(r7), run_time=0.5)
            self.play(Create(dg), run_time=max(0.5, tk.duration - 1.0))
        self.wait(0.3)

        b8 = bottom("Triangle = half l times w")
        tu = Polygon(r7.get_corner(DL), r7.get_corner(UR), r7.get_corner(UL), color=BLUE_C, fill_opacity=0.3, stroke_width=0)
        td = Polygon(r7.get_corner(DL), r7.get_corner(UR), r7.get_corner(DR), color=GREEN_C, fill_opacity=0.3, stroke_width=0)
        l1 = Text("T1", font_size=20, color=BLUE_C).move_to(r7.get_center() + UL * 0.6)
        l2 = Text("T2", font_size=20, color=GREEN_C).move_to(r7.get_center() + DR * 0.6)
        tf = MathTex(r"\text{Area of }\triangle = \frac{1}{2} \times l \times w", font_size=30, color=YELLOW).move_to(RIGHT * 4 + UP * 0.2)
        with self.voiceover(text="The diagonal of a rectangle divides it into two congruent triangles. Each triangle has an area equal to half the area of the rectangle: Area of each triangle = one half times length times width.") as tk:
            self.play(Transform(b7, b8), run_time=0.3)
            self.play(FadeIn(tu), FadeIn(l1), run_time=0.6)
            self.play(FadeIn(td), FadeIn(l2), run_time=0.6)
            self.play(Write(tf), run_time=1.0)
            self.wait(max(2.0, tk.duration - 2.5))
        self.wait(0.3)
        clear(h7, b7, r7, dg, tu, td, l1, l2, tf)

        tr = Text("Perimeter vs Area", font_size=42, weight=BOLD, color=BLUE_C)
        with self.voiceover(text="Let us now look into an important distinction between perimeter and area.") as tk:
            self.play(FadeIn(tr, scale=1.2), run_time=1.0)
            self.wait(max(0.3, tk.duration - 1.0))
        self.wait(0.3)
        self.play(FadeOut(tr))

        h10 = heading("Perimeter vs Area")
        b10 = bottom("Same Perimeter not equal Same Area")
        dn = VGroup(
            Text("Perimeter = total boundary length", font_size=22, color=RED_C),
            Text("Area = surface enclosed within", font_size=22, color=GREEN_C),
        ).arrange(DOWN, buff=0.25).move_to(UP * 2.2)
        rx = Rectangle(width=4, height=2.5, color=WHITE, stroke_width=2).move_to(DOWN * 0.2)
        pt = rx.copy().set_stroke(RED_C, width=5)
        af = rx.copy().set_fill(BLUE_C, opacity=0.3).set_stroke(width=0)
        with self.voiceover(text="Perimeter is the total length of the boundary, while area measures the surface enclosed within. Two regions can have the same perimeter but different areas.") as tk:
            self.play(FadeIn(h10), FadeIn(b10), run_time=0.5)
            self.play(FadeIn(dn), run_time=0.6)
            self.play(Create(rx), run_time=0.4)
            self.play(Create(pt), run_time=0.8)
            self.play(FadeIn(af), run_time=0.6)
            self.wait(max(0.3, tk.duration - 2.9))
        self.wait(0.3)
        clear(dn, rx, pt, af)

        b11 = bottom("P=20cm but Areas differ")
        ra = Rectangle(width=3.5, height=1.5, color=BLUE_C, fill_opacity=0.2, stroke_width=3).move_to(LEFT * 3.5)
        daa = VGroup(
            dima(ra.get_corner(DL) + DOWN * .25, ra.get_corner(DR) + DOWN * .25, "7 cm", DOWN),
            dima(ra.get_corner(DL) + LEFT * .25, ra.get_corner(UL) + LEFT * .25, "3 cm", LEFT),
        )
        pa = Text("P = 20 cm", font_size=18, color=YELLOW).next_to(ra, UP, buff=0.25)
        aa = Text("Area = 21 sq cm", font_size=18, color=GREEN_C).move_to(ra)
        rb = Rectangle(width=4.5, height=0.5, color=RED_C, fill_opacity=0.2, stroke_width=3).move_to(RIGHT * 3.5)
        dab = VGroup(
            dima(rb.get_corner(DL) + DOWN * .25, rb.get_corner(DR) + DOWN * .25, "9 cm", DOWN),
            dima(rb.get_corner(DL) + LEFT * .3, rb.get_corner(UL) + LEFT * .3, "1 cm", LEFT),
        )
        pb = Text("P = 20 cm", font_size=18, color=YELLOW).next_to(rb, UP, buff=0.25)
        abx = Text("Area = 9 sq cm", font_size=18, color=GREEN_C).move_to(rb)
        cc = Text("Perimeter alone cannot determine area!", font_size=24, color=RED_C).move_to(UP * 2.8)
        with self.voiceover(text="For instance, a rectangle of 7 cm by 3 cm and one of 9 cm by 1 cm both have a perimeter of 20 cm, yet their areas are 21 cm squared and 9 cm squared respectively. Therefore, perimeter alone cannot determine area.") as tk:
            self.play(Transform(b10, b11), run_time=0.3)
            self.play(Create(ra), FadeIn(daa), FadeIn(pa), run_time=1.0)
            self.play(Create(rb), FadeIn(dab), FadeIn(pb), run_time=1.0)
            self.play(Indicate(ra, color=YELLOW, scale_factor=1.05), FadeIn(aa), run_time=0.8)
            self.play(Indicate(rb, color=YELLOW, scale_factor=1.05), FadeIn(abx), run_time=0.8)
            self.play(FadeIn(cc), run_time=max(0.5, tk.duration - 3.9))
        self.wait(0.3)
        clear(h10, b10, ra, daa, pa, aa, rb, dab, pb, abx, cc)

        tr = Text("Path Around a Field", font_size=38, weight=BOLD, color=BLUE_C)
        with self.voiceover(text="Now let us apply the rectangle area formula in a real-life path problem.") as tk:
            self.play(FadeIn(tr, shift=UP), run_time=1.0)
            self.wait(max(0.3, tk.duration - 1.0))
        self.wait(0.3)
        self.play(FadeOut(tr))

        h13 = heading("Path Problem")
        b13 = bottom("Find area of the path")
        ou = Rectangle(width=5, height=3.125, color=BLUE_C, stroke_width=3)
        ou.set_fill(YELLOW, opacity=0.2)
        inn = Rectangle(width=3.75, height=1.875, color=GREEN_C, stroke_width=2)
        inn.set_fill("#1e1e2e", opacity=1)
        inn.move_to(ou.get_center())
        d13b = dima(ou.get_corner(DL) + DOWN * .3, ou.get_corner(DR) + DOWN * .3, "40 m", DOWN)
        d13l = dima(ou.get_corner(DL) + LEFT * .3, ou.get_corner(UL) + LEFT * .3, "25 m", LEFT)
        d13p = dima(inn.get_right(), ou.get_right(), "5 m", UP, c=RED_C, fs=14)
        q13 = Text("Find the area of the path.", font_size=20, color=WHITE).next_to(ou, UP, buff=0.4)
        dia13 = VGroup(ou, inn, d13b, d13l, d13p, q13)
        with self.voiceover(text="A rectangular field measures 40 m by 25 m. A path of width 5 m runs along the inside boundary. Find the area of the path.") as tk:
            self.play(FadeIn(h13), FadeIn(b13), run_time=0.5)
            self.play(Create(ou), run_time=0.5)
            self.play(FadeIn(d13b), FadeIn(d13l), run_time=0.5)
            self.play(Create(inn), run_time=0.4)
            self.play(FadeIn(d13p), run_time=0.4)
            self.play(FadeIn(q13), run_time=max(0.3, tk.duration - 2.3))
        self.wait(0.3)

        b14 = bottom("Path Area = 550 sq m")
        with self.voiceover(text="Solution: Given: Outer length = 40 m, outer width = 25 m, path width = 5 m. Area of outer rectangle = 40 times 25 = 1000 m squared. Inner length = 40 minus 2 times 5 = 30 m. Inner width = 25 minus 2 times 5 = 15 m. Area of inner rectangle = 30 times 15 = 450 m squared. Area of path = 1000 minus 450 = 550 m squared.") as tk:
            self.play(Transform(b13, b14), run_time=0.3)
            self.play(dia13.animate.scale(0.65).shift(LEFT * 3.5), run_time=0.8)
            s14 = VGroup(
                MathTex(r"\text{Outer}=40 \times 25=1000\;\text{m}^2", font_size=24, color=WHITE),
                MathTex(r"\text{Inner }l=40-2(5)=30\;\text{m}", font_size=24, color=WHITE),
                MathTex(r"\text{Inner }w=25-2(5)=15\;\text{m}", font_size=24, color=WHITE),
                MathTex(r"\text{Inner}=30 \times 15=450\;\text{m}^2", font_size=24, color=WHITE),
                MathTex(r"\text{Path}=1000-450=\mathbf{550\;\text{m}^2}", font_size=26, color=GREEN_C),
            ).arrange(DOWN, buff=0.22, aligned_edge=LEFT).move_to(RIGHT * 2.8)
            rm = max(1, tk.duration - 1.1)
            st = rm / 5
            self.play(Indicate(ou, color=YELLOW, scale_factor=1.05), FadeIn(s14[0], shift=RIGHT * .2), run_time=st)
            self.play(FadeIn(s14[1], shift=RIGHT * .2), run_time=st)
            self.play(FadeIn(s14[2], shift=RIGHT * .2), run_time=st)
            self.play(Indicate(inn, color=GREEN_C, scale_factor=1.05), FadeIn(s14[3], shift=RIGHT * .2), run_time=st)
            self.play(Indicate(ou, color=RED_C, scale_factor=1.03), FadeIn(s14[4], shift=RIGHT * .2), run_time=st)
        self.wait(0.3)
        clear(h13, b13, dia13, s14)

        tr = Text("Crosspath Problem", font_size=38, weight=BOLD, color=BLUE_C)
        with self.voiceover(text="Let us explore another real-life situation involving crosspaths.") as tk:
            self.play(FadeIn(tr, shift=UP), run_time=1.0)
            self.wait(max(0.3, tk.duration - 1.0))
        self.wait(0.3)
        self.play(FadeOut(tr))

        h16 = heading("Crosspath Problem")
        b16 = bottom("Find crosspath area")
        pl = Rectangle(width=5.4, height=3, color=BLUE_C, stroke_width=3)
        hp = Rectangle(width=5.4, height=0.9, color=YELLOW, fill_opacity=0.3, stroke_width=1).move_to(pl.get_center())
        vp = Rectangle(width=0.9, height=3, color=GREEN_C, fill_opacity=0.3, stroke_width=1).move_to(pl.get_center())
        ov = Square(side_length=0.9, color=RED_C, fill_opacity=0.5, stroke_width=1).move_to(pl.get_center())
        d16b = dima(pl.get_corner(DL) + DOWN * .3, pl.get_corner(DR) + DOWN * .3, "18 m", DOWN)
        d16l = dima(pl.get_corner(DL) + LEFT * .3, pl.get_corner(UL) + LEFT * .3, "10 m", LEFT)
        pw16 = Text("3 m wide paths", font_size=16, color=RED_C).next_to(pl, RIGHT, buff=0.3)
        q16 = Text("Find the area of the crosspath.", font_size=20, color=WHITE).next_to(pl, UP, buff=0.35)
        dia16 = VGroup(pl, hp, vp, ov, d16b, d16l, pw16, q16)
        with self.voiceover(text="A rectangular plot measures 18 m by 10 m. Two paths, each 3 m wide, cross it, one parallel to the length, one parallel to the breadth. Find the area of the crosspath.") as tk:
            self.play(FadeIn(h16), FadeIn(b16), run_time=0.5)
            self.play(Create(pl), run_time=0.5)
            self.play(FadeIn(d16b), FadeIn(d16l), run_time=0.5)
            self.play(FadeIn(hp), run_time=0.4)
            self.play(FadeIn(vp), run_time=0.4)
            self.play(FadeIn(ov), FadeIn(pw16), run_time=0.3)
            self.play(FadeIn(q16), run_time=max(0.3, tk.duration - 2.6))
        self.wait(0.3)

        b17 = bottom("Crosspath = 75 sq m")
        with self.voiceover(text="Solution: Given: Plot length = 18 m, plot breadth = 10 m, path width = 3 m. Area of horizontal path = 18 times 3 = 54 m squared. Area of vertical path = 10 times 3 = 30 m squared. Area of overlap = 3 times 3 = 9 m squared. Area of crosspath = 54 plus 30 minus 9 = 75 m squared.") as tk:
            self.play(Transform(b16, b17), run_time=0.3)
            self.play(dia16.animate.scale(0.6).shift(LEFT * 3.5), run_time=0.8)
            s17 = VGroup(
                MathTex(r"\text{Horiz}=18 \times 3=54\;\text{m}^2", font_size=24, color=YELLOW),
                MathTex(r"\text{Vert}=10 \times 3=30\;\text{m}^2", font_size=24, color=GREEN_C),
                MathTex(r"\text{Overlap}=3 \times 3=9\;\text{m}^2", font_size=24, color=RED_C),
                MathTex(r"\text{Cross}=54+30-9=\mathbf{75\;\text{m}^2}", font_size=26, color=BLUE_C),
            ).arrange(DOWN, buff=0.3, aligned_edge=LEFT).move_to(RIGHT * 2.8)
            rm = max(1, tk.duration - 1.1)
            st = rm / 4
            self.play(Indicate(hp, color=YELLOW, scale_factor=1.05), FadeIn(s17[0], shift=RIGHT * .2), run_time=st)
            self.play(Indicate(vp, color=GREEN_C, scale_factor=1.05), FadeIn(s17[1], shift=RIGHT * .2), run_time=st)
            self.play(Indicate(ov, color=RED_C, scale_factor=1.1), FadeIn(s17[2], shift=RIGHT * .2), run_time=st)
            self.play(FadeIn(s17[3], shift=RIGHT * .2), run_time=st)
        self.wait(0.3)
        clear(h16, b16, dia16, s17)

        tr = Text("Composite Figure", font_size=38, weight=BOLD, color=BLUE_C)
        with self.voiceover(text="Let us now look into finding the area of a composite figure.") as tk:
            self.play(FadeIn(tr, shift=UP), run_time=1.0)
            self.wait(max(0.3, tk.duration - 1.0))
        self.wait(0.3)
        self.play(FadeOut(tr))

        h19 = heading("Composite Figure")
        b19 = bottom("Find total area")
        ra19 = Rectangle(width=1.6, height=3.6, color=BLUE_C, fill_opacity=0.2, stroke_width=3)
        rb19 = Rectangle(width=2.4, height=1.2, color=GREEN_C, fill_opacity=0.2, stroke_width=3)
        rb19.next_to(ra19, RIGHT, buff=0, aligned_edge=DOWN)
        ls = VGroup(ra19, rb19).move_to(ORIGIN)
        d19 = VGroup(
            dima(ra19.get_corner(DL) + LEFT * .3, ra19.get_corner(UL) + LEFT * .3, "9 cm", LEFT),
            dima(ra19.get_corner(DL) + DOWN * .3, ra19.get_corner(DR) + DOWN * .3, "4 cm", DOWN),
            dima(rb19.get_corner(DL) + DOWN * .3, rb19.get_corner(DR) + DOWN * .3, "6 cm", DOWN),
            dima(rb19.get_corner(DR) + RIGHT * .3, rb19.get_corner(UR) + RIGHT * .3, "3 cm", RIGHT),
        )
        q19 = Text("Find the total area.", font_size=20, color=WHITE).next_to(ls, UP, buff=0.5)
        dia19 = VGroup(ls, d19, q19)
        with self.voiceover(text="Question: An L-shaped figure is made of two rectangles: one measuring 9 cm by 4 cm and another measuring 6 cm by 3 cm. Find the total area.") as tk:
            self.play(FadeIn(h19), FadeIn(b19), run_time=0.5)
            self.play(Create(ra19), Create(rb19), run_time=0.8)
            self.play(FadeIn(d19), run_time=0.6)
            self.play(FadeIn(q19), run_time=max(0.3, tk.duration - 1.9))
        self.wait(0.3)

        b20 = bottom("Total = 54 sq cm")
        with self.voiceover(text="Solution: Given: First rectangle = 9 cm times 4 cm, second rectangle = 6 cm times 3 cm. Area of first rectangle = 9 times 4 = 36 cm squared. Area of second rectangle = 6 times 3 = 18 cm squared. Total area = 36 plus 18 = 54 cm squared.") as tk:
            self.play(Transform(b19, b20), run_time=0.3)
            self.play(dia19.animate.scale(0.85).shift(LEFT * 3.5), run_time=0.8)
            s20 = VGroup(
                MathTex(r"\text{Area}_1=9 \times 4=36\;\text{cm}^2", font_size=26, color=BLUE_C),
                MathTex(r"\text{Area}_2=6 \times 3=18\;\text{cm}^2", font_size=26, color=GREEN_C),
                MathTex(r"\text{Total}=36+18=\mathbf{54\;\text{cm}^2}", font_size=28, color=YELLOW),
            ).arrange(DOWN, buff=0.4, aligned_edge=LEFT).move_to(RIGHT * 2.8)
            rm = max(1, tk.duration - 1.1)
            st = rm / 3
            self.play(Indicate(ra19, color=BLUE_C, scale_factor=1.08), FadeIn(s20[0], shift=RIGHT * .2), run_time=st)
            self.play(Indicate(rb19, color=GREEN_C, scale_factor=1.08), FadeIn(s20[1], shift=RIGHT * .2), run_time=st)
            self.play(FadeIn(s20[2], shift=RIGHT * .2), run_time=st)
        self.wait(0.3)
        clear(h19, b19, dia19, s20)

        h21 = heading("Summary")
        b21 = bottom("Key Concepts Learned")
        bu = VGroup(
            Text("Area = count of unit squares", font_size=24, color=WHITE),
            Text("Rectangle: Area = l x w", font_size=24, color=WHITE),
            Text("Square: Area = s squared", font_size=24, color=WHITE),
            Text("Triangle: Area = half l x w", font_size=24, color=WHITE),
            Text("Perimeter is not equal to Area", font_size=24, color=WHITE),
            Text("Composite = sum of parts", font_size=24, color=WHITE),
        ).arrange(DOWN, buff=0.3, aligned_edge=LEFT).move_to(ORIGIN)
        with self.voiceover(text="Summary: We have learned the concept of area and how to apply it to simple and complex shapes.") as tk:
            self.play(FadeIn(h21), FadeIn(b21), run_time=0.5)
            self.play(FadeIn(bu, lag_ratio=0.15), run_time=max(0.5, tk.duration - 0.5))
        self.wait(1.0)
        clear(h21, b21, bu)
        self.wait(0.5)