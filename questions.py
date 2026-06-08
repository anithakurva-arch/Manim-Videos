from manim import *
import numpy as np


class Q01(Scene):
    def construct(self):
        self.camera.background_color = WHITE
        s = 1.6
        A, B, C, D = ORIGIN, s*RIGHT, s*(RIGHT+UP), s*UP
        E, F = 2*s*UP, s*(UP - RIGHT)

        shaded = Polygon(A, C, E, F, stroke_color="#E65100", stroke_width=2.5,
                         fill_color="#FFB74D", fill_opacity=0.35)
        primary = Polygon(A, B, C, D, stroke_color="#1565C0", stroke_width=2.5,
                          fill_color="#90CAF9", fill_opacity=0.20)
        diag = DashedLine(A, C, color="#5D4037", stroke_width=2)
        u = s / 3
        grid = VGroup()
        for i in range(1, 3):
            grid.add(Line(i*u*UP, i*u*UP + s*RIGHT, stroke_width=0.8, color="#BBDEFB"))
            grid.add(Line(i*u*RIGHT, i*u*RIGHT + s*UP, stroke_width=0.8, color="#BBDEFB"))

        VGroup(shaded, primary, diag, grid).move_to(ORIGIN)
        self.add(shaded, grid, primary, diag)

        self.add(MathTex(r"9\;\text{sq units}", font_size=22, color=BLACK).move_to(primary))
        d = shaded.get_center() - primary.get_center()
        self.add(MathTex("?", font_size=44, color="#BF360C").move_to(
            shaded.get_center() + 0.38 * d / np.linalg.norm(d)))


class Q02(Scene):
    def construct(self):
        self.camera.background_color = WHITE
        s = 2.2
        A, B, C = ORIGIN, s*RIGHT, s*UP
        tri = Polygon(A, B, C, stroke_color="#1565C0", stroke_width=2.5,
                      fill_color="#BBDEFB", fill_opacity=0.15)
        ra = 0.2
        ram = VGroup(
            Line(A + ra*RIGHT, A + ra*(RIGHT + UP), stroke_width=1.5, color="#333"),
            Line(A + ra*UP, A + ra*(RIGHT + UP), stroke_width=1.5, color="#333"))
        VGroup(tri, ram).move_to(ORIGIN)
        self.add(tri, ram)

        v = tri.get_vertices()
        self.add(MathTex("a", font_size=28, color=BLACK).move_to(
            (v[0] + v[1]) / 2 + 0.28*DOWN))
        self.add(MathTex("a", font_size=28, color=BLACK).move_to(
            (v[0] + v[2]) / 2 + 0.28*LEFT))
        self.add(MathTex("c", font_size=28, color="#C62828").move_to(
            (v[1] + v[2]) / 2 + 0.3*(RIGHT + UP) / np.sqrt(2)))


class Q03(Scene):
    def construct(self):
        self.camera.background_color = WHITE
        s = 2.6
        A, B, C, D = ORIGIN, s*RIGHT, s*(RIGHT + UP), s*UP
        outer = Polygon(A, B, C, D, stroke_color="#333", stroke_width=2.5,
                        fill_color="#E8EAF6", fill_opacity=0.1)
        M1, M2, M3, M4 = (A+B)/2, (B+C)/2, (C+D)/2, (D+A)/2
        inner = Polygon(M1, M2, M3, M4, stroke_color="#E65100", stroke_width=2.5,
                        fill_color="#FFB74D", fill_opacity=0.30)
        ctr = s / 2 * (RIGHT + UP)
        folds = VGroup(*[DashedLine(v, ctr, color="#BDBDBD", stroke_width=1.2,
                         dash_length=0.08) for v in [A, B, C, D]])

        VGroup(outer, inner, folds).move_to(ORIGIN)
        self.add(outer, folds, inner)

        iv = inner.get_vertices()
        self.add(MathTex(r"40\;\text{sq cm}", font_size=20, color=BLACK).next_to(outer, DOWN, buff=0.15))
        self.add(MathTex("?", font_size=36, color="#BF360C").move_to(inner))

        for nm, pt, off in zip(["P", "Q", "R", "S"], iv,
                                [DOWN, RIGHT, UP, LEFT]):
            self.add(MathTex(nm, font_size=22, color="#E65100").move_to(pt + 0.25*off))


class Q04(Scene):
    def construct(self):
        self.camera.background_color = WHITE
        s = 2.4
        A, B, C, D = ORIGIN, s*RIGHT, s*(RIGHT + UP), s*UP
        sq = Polygon(A, B, C, D, stroke_color="#333", stroke_width=2.5, fill_opacity=0)
        diag = Line(A, C, color="#555", stroke_width=2)
        tri = Polygon(A, B, C, stroke_width=0, fill_color="#42A5F5", fill_opacity=0.25)

        VGroup(tri, sq, diag).move_to(ORIGIN)
        self.add(tri, sq, diag)

        v = sq.get_vertices()
        for i, d in enumerate([DOWN, RIGHT, UP, LEFT]):
            self.add(MathTex("1", font_size=24, color=BLACK).move_to(
                (v[i] + v[(i+1) % 4]) / 2 + 0.25*d))


class Q05(Scene):
    def construct(self):
        self.camera.background_color = WHITE
        s = 1.5
        A, B, C, D = ORIGIN, s*RIGHT, s*(RIGHT + UP), s*UP
        E, F = 2*s*UP, s*(UP - RIGHT)

        shaded = Polygon(A, C, E, F, stroke_color="#2E7D32", stroke_width=2.5,
                         fill_color="#A5D6A7", fill_opacity=0.30)
        primary = Polygon(A, B, C, D, stroke_color="#1565C0", stroke_width=2.5,
                          fill_color="#90CAF9", fill_opacity=0.15)
        diag = DashedLine(A, C, color="#5D4037", stroke_width=2)

        VGroup(shaded, primary, diag).move_to(ORIGIN)
        self.add(shaded, primary, diag)

        pv = primary.get_vertices()
        self.add(MathTex("4", font_size=26, color=BLACK).move_to(
            (pv[0] + pv[1]) / 2 + 0.25*DOWN))
        sc, pc = shaded.get_center(), primary.get_center()
        dd = sc - pc
        self.add(MathTex("?", font_size=42, color="#2E7D32").move_to(
            sc + 0.4 * dd / np.linalg.norm(dd)))


class Q06(Scene):
    def construct(self):
        self.camera.background_color = WHITE
        leg = 1.8
        O, P1, P2 = ORIGIN, leg*RIGHT, leg*UP
        tri = Polygon(O, P1, P2, stroke_color="#1565C0", stroke_width=2.5,
                      fill_color="#BBDEFB", fill_opacity=0.15)

        h = P2 - P1; hl = np.linalg.norm(h); hd = h / hl
        perp = np.array([hd[1], -hd[0], 0])
        S1, S2 = P1 + perp*hl, P2 + perp*hl
        sqr = Polygon(P1, P2, S2, S1, stroke_color="#E65100", stroke_width=2.5,
                      fill_color="#FFB74D", fill_opacity=0.25)

        ra = 0.18
        ram = VGroup(
            Line(O + ra*RIGHT, O + ra*(RIGHT + UP), stroke_width=1.5, color="#333"),
            Line(O + ra*UP, O + ra*(RIGHT + UP), stroke_width=1.5, color="#333"))

        VGroup(sqr, tri, ram).move_to(ORIGIN)
        self.add(sqr, tri, ram)

        tv, sv = tri.get_vertices(), sqr.get_vertices()
        self.add(MathTex(r"\sqrt{5}", font_size=22, color=BLACK).move_to(
            (tv[0] + tv[1]) / 2 + 0.28*DOWN))
        self.add(MathTex(r"\sqrt{5}", font_size=22, color=BLACK).move_to(
            (tv[0] + tv[2]) / 2 + 0.28*LEFT))
        for i, nm in enumerate(["R", "E", "S", "T"]):
            off = sv[i] - sqr.get_center()
            off = off / np.linalg.norm(off) * 0.28
            self.add(MathTex(nm, font_size=20, color="#E65100").move_to(sv[i] + off))


class Q07(Scene):
    def construct(self):
        self.camera.background_color = WHITE
        s = 2.6
        A, B, C, D = ORIGIN, s*RIGHT, s*(RIGHT + UP), s*UP
        outer = Polygon(A, B, C, D, stroke_color="#333", stroke_width=2.5,
                        fill_color="#E8EAF6", fill_opacity=0.08)
        M1, M2, M3, M4 = (A+B)/2, (B+C)/2, (C+D)/2, (D+A)/2
        inner = Polygon(M1, M2, M3, M4, stroke_color="#E65100", stroke_width=2.5,
                        fill_color="#FFB74D", fill_opacity=0.30)
        ctr = s / 2 * (RIGHT + UP)
        folds = VGroup(*[DashedLine(v, ctr, color="#BDBDBD", stroke_width=1,
                         dash_length=0.08) for v in [A, B, C, D]])

        VGroup(outer, folds, inner).move_to(ORIGIN)
        self.add(outer, folds, inner)

        self.add(MathTex(r"18\;\text{sq units}", font_size=20,
                         color="#BF360C").move_to(inner))
        self.add(MathTex("?", font_size=30, color=BLACK).next_to(outer, DOWN, buff=0.15))


class Q08(Scene):
    def construct(self):
        self.camera.background_color = WHITE
        sc = 0.7
        grid = VGroup()
        for i in range(5):
            grid.add(Line(i*sc*RIGHT, i*sc*RIGHT + 4*sc*UP,
                         stroke_width=0.5, color="#D0D0D0"))
            grid.add(Line(i*sc*UP, i*sc*UP + 4*sc*RIGHT,
                         stroke_width=0.5, color="#D0D0D0"))
        # extra lines to complete grid
        grid.add(Line(4*sc*RIGHT, 4*sc*RIGHT + 4*sc*UP, stroke_width=0.5, color="#D0D0D0"))
        grid.add(Line(4*sc*UP, 4*sc*RIGHT + 4*sc*UP, stroke_width=0.5, color="#D0D0D0"))

        A, B, C = ORIGIN, 3*sc*RIGHT, 3*sc*UP
        tri = Polygon(A, B, C, stroke_color="#1565C0", stroke_width=2.5,
                      fill_color="#BBDEFB", fill_opacity=0.15)
        ra = 0.15
        ram = VGroup(
            Line(A + ra*RIGHT, A + ra*(RIGHT + UP), stroke_width=1.5, color="#333"),
            Line(A + ra*UP, A + ra*(RIGHT + UP), stroke_width=1.5, color="#333"))
        dots = VGroup(*[Dot(p, radius=0.05, color="#333") for p in [A, B, C]])

        VGroup(grid, tri, ram, dots).move_to(ORIGIN)
        self.add(grid, tri, ram, dots)


class Q09(Scene):
    def construct(self):
        self.camera.background_color = WHITE
        sa = 1.1
        sb = sa * np.sqrt(2)
        sc = 2 * sa

        sqa = Square(side_length=sa, stroke_color="#1565C0", stroke_width=2.5,
                     fill_color="#90CAF9", fill_opacity=0.20)
        sqb = Square(side_length=sb, stroke_color="#2E7D32", stroke_width=2.5,
                     fill_color="#A5D6A7", fill_opacity=0.20)
        sqc = Square(side_length=sc, stroke_color="#E65100", stroke_width=2.5,
                     fill_color="#FFB74D", fill_opacity=0.20)

        sqa.move_to(3.2*LEFT)
        sqb.move_to(0.3*LEFT)
        sqc.move_to(2.8*RIGHT)
        for sq in [sqa, sqb]:
            sq.align_to(sqc, DOWN)
        self.add(sqa, sqb, sqc)

        self.add(MathTex("A", font_size=26, color="#0D47A1").move_to(sqa))
        self.add(MathTex("B", font_size=26, color="#1B5E20").move_to(sqb))
        self.add(MathTex("C", font_size=26, color="#BF360C").move_to(sqc))

        a1 = Arrow(sqa.get_right(), sqb.get_left(), buff=0.12,
                   color="#555", stroke_width=2, max_tip_length_to_length_ratio=0.15)
        a2 = Arrow(sqb.get_right(), sqc.get_left(), buff=0.12,
                   color="#555", stroke_width=2, max_tip_length_to_length_ratio=0.15)
        self.add(a1, a2)
        self.add(MathTex(r"\times 2", font_size=18, color="#555").next_to(a1, UP, buff=0.05))
        self.add(MathTex(r"\times 2", font_size=18, color="#555").next_to(a2, UP, buff=0.05))


class Q10(Scene):
    def construct(self):
        self.camera.background_color = WHITE
        s = 2.4
        A, B, C = ORIGIN, s*RIGHT, s*UP
        tri = Polygon(A, B, C, stroke_color="#1565C0", stroke_width=2.5,
                      fill_color="#BBDEFB", fill_opacity=0.15)
        ra = 0.2
        ram = VGroup(
            Line(A + ra*RIGHT, A + ra*(RIGHT + UP), stroke_width=1.5, color="#333"),
            Line(A + ra*UP, A + ra*(RIGHT + UP), stroke_width=1.5, color="#333"))

        VGroup(tri, ram).move_to(ORIGIN)
        self.add(tri, ram)

        v = tri.get_vertices()
        self.add(MathTex("10", font_size=26, color=BLACK).move_to(
            (v[0] + v[1]) / 2 + 0.3*DOWN))
        self.add(MathTex("10", font_size=26, color=BLACK).move_to(
            (v[0] + v[2]) / 2 + 0.3*LEFT))
        self.add(MathTex("?", font_size=30, color="#C62828").move_to(
            (v[1] + v[2]) / 2 + 0.3*(RIGHT + UP) / np.sqrt(2)))


class Q11(Scene):
    def construct(self):
        self.camera.background_color = WHITE
        s = 2.6
        A, B, C, D = ORIGIN, s*RIGHT, s*(RIGHT + UP), s*UP
        ctr = s / 2 * (RIGHT + UP)

        sq = Polygon(A, B, C, D, stroke_color="#333", stroke_width=2.5, fill_opacity=0)
        d1 = Line(A, C, color="#555", stroke_width=2)
        d2 = Line(B, D, color="#555", stroke_width=2)

        cols = ["#FFB74D", "#90CAF9", "#A5D6A7", "#CE93D8"]
        tris = [
            Polygon(A, B, ctr, fill_color=cols[0], fill_opacity=0.25, stroke_width=0),
            Polygon(B, C, ctr, fill_color=cols[1], fill_opacity=0.25, stroke_width=0),
            Polygon(C, D, ctr, fill_color=cols[2], fill_opacity=0.25, stroke_width=0),
            Polygon(D, A, ctr, fill_color=cols[3], fill_opacity=0.25, stroke_width=0),
        ]
        VGroup(*tris, sq, d1, d2).move_to(ORIGIN)
        self.add(*tris, sq, d1, d2)
        for i, t in enumerate(tris):
            self.add(MathTex(str(i + 1), font_size=28, color=BLACK).move_to(
                t.get_center()))


class Q12(Scene):
    def construct(self):
        self.camera.background_color = WHITE
        s = 2.4
        A, B, C, D = ORIGIN, s*RIGHT, s*(RIGHT + UP), s*UP
        sq = Polygon(A, B, C, D, stroke_color="#1565C0", stroke_width=2.5,
                     fill_color="#E3F2FD", fill_opacity=0.1)
        diag = Line(A, C, color="#C62828", stroke_width=3)

        VGroup(sq, diag).move_to(ORIGIN)
        self.add(sq, diag)

        v = sq.get_vertices()
        self.add(MathTex("1", font_size=26, color=BLACK).move_to(
            (v[0] + v[1]) / 2 + 0.28*DOWN))
        self.add(MathTex("1", font_size=26, color=BLACK).move_to(
            (v[0] + v[3]) / 2 + 0.28*LEFT))
        self.add(MathTex(r"\sqrt{2}", font_size=26, color="#C62828").move_to(
            (v[0] + v[2]) / 2 + 0.35*(LEFT + UP) / np.sqrt(2)))


class Q13(Scene):
    def construct(self):
        self.camera.background_color = WHITE
        leg = 1.8
        O, P1, P2 = ORIGIN, leg*RIGHT, leg*UP
        tri = Polygon(O, P1, P2, stroke_color="#1565C0", stroke_width=2.5,
                      fill_color="#BBDEFB", fill_opacity=0.15)

        h = P2 - P1; hl = np.linalg.norm(h); hd = h / hl
        perp = np.array([hd[1], -hd[0], 0])
        S1, S2 = P1 + perp*hl, P2 + perp*hl
        sqr = Polygon(P1, P2, S2, S1, stroke_color="#E65100", stroke_width=2.5,
                      fill_color="#FFB74D", fill_opacity=0.25)

        ra = 0.18
        ram = VGroup(
            Line(O + ra*RIGHT, O + ra*(RIGHT + UP), stroke_width=1.5, color="#333"),
            Line(O + ra*UP, O + ra*(RIGHT + UP), stroke_width=1.5, color="#333"))

        VGroup(sqr, tri, ram).move_to(ORIGIN)
        self.add(sqr, tri, ram)

        tv, sv = tri.get_vertices(), sqr.get_vertices()
        self.add(MathTex("a", font_size=24, color=BLACK).move_to(
            (tv[0] + tv[1]) / 2 + 0.25*DOWN))
        self.add(MathTex("a", font_size=24, color=BLACK).move_to(
            (tv[0] + tv[2]) / 2 + 0.25*LEFT))
        self.add(MathTex(r"50\;\text{sq units}", font_size=20,
                         color="#BF360C").move_to(sqr))
        for i, nm in enumerate(["R", "E", "S", "T"]):
            off = sv[i] - sqr.get_center()
            off = off / np.linalg.norm(off) * 0.28
            self.add(MathTex(nm, font_size=20, color="#E65100").move_to(sv[i] + off))


class Q14(Scene):
    def construct(self):
        self.camera.background_color = WHITE
        s1 = 1.8
        s2 = s1 * np.sqrt(2)

        sq1 = Square(side_length=s1, stroke_color="#1565C0", stroke_width=2.5,
                     fill_color="#90CAF9", fill_opacity=0.15)
        sq2 = Square(side_length=s2, stroke_color="#2E7D32", stroke_width=2.5,
                     fill_color="#A5D6A7", fill_opacity=0.15)

        sq1.move_to(2.5*LEFT)
        sq2.move_to(2.5*RIGHT)
        sq1.align_to(sq2, DOWN)
        self.add(sq1, sq2)

        self.add(MathTex(r"5\;\text{cm}", font_size=22, color=BLACK).next_to(
            sq1, DOWN, buff=0.12))
        self.add(MathTex("?", font_size=34, color="#2E7D32").next_to(
            sq2, DOWN, buff=0.12))

        arr = Arrow(sq1.get_right(), sq2.get_left(), buff=0.15,
                    color="#555", stroke_width=2, max_tip_length_to_length_ratio=0.15)
        self.add(arr)
        self.add(MathTex(r"2 \times \text{area}", font_size=18,
                         color="#555").next_to(arr, UP, buff=0.06))