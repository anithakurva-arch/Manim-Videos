from manim import *
import numpy as np

# ---------- Colors ----------
BLACK_LINE = "#1A1A1A"
LIGHT_GRAY = "#E8E8E8"
BLUE_PRIMARY = "#4A90D9"
BLUE_DARK = "#2E5C8A"
BLUE_LIGHT_FILL = "#D6E8F5"
GRAY_DASH = "#B0B0B0"
GRAY_MED = "#808080"
DARK_GRAY = "#4A4A4A"
BLUE_VERY_LIGHT = "#A8C8E8"
TEXT_BUBBLE_GRAY = "#F0F0F0"


# ---------- Helpers ----------
def right_angle_marker(corner, size=0.3, dir_h=RIGHT, dir_v=UP):
    p1 = corner + dir_h * size
    p2 = corner + dir_h * size + dir_v * size
    p3 = corner + dir_v * size
    m = VMobject(stroke_color=BLACK_LINE, stroke_width=2, fill_opacity=0)
    m.set_points_as_corners([p1, p2, p3])
    return m


def single_tick(midpoint, perp_dir, length=0.25):
    return Line(midpoint - perp_dir * length / 2,
                midpoint + perp_dir * length / 2,
                color=BLACK_LINE, stroke_width=2)


def double_tick(midpoint, perp_dir, edge_dir, length=0.25, spacing=0.12):
    t1 = Line(midpoint + edge_dir * spacing / 2 - perp_dir * length / 2,
              midpoint + edge_dir * spacing / 2 + perp_dir * length / 2,
              color=BLACK_LINE, stroke_width=2)
    t2 = Line(midpoint - edge_dir * spacing / 2 - perp_dir * length / 2,
              midpoint - edge_dir * spacing / 2 + perp_dir * length / 2,
              color=BLACK_LINE, stroke_width=2)
    return VGroup(t1, t2)


def make_hatching(vertices, angle, color, spacing=0.35, stroke=1.0):
    """Generate parallel hatch lines clipped inside a convex polygon."""
    vertices = [np.array(v) for v in vertices]
    n = len(vertices)
    d = np.array([np.cos(angle), np.sin(angle), 0])
    nrm = np.array([-np.sin(angle), np.cos(angle), 0])
    projections = [float(np.dot(v, nrm)) for v in vertices]
    p_min, p_max = min(projections), max(projections)
    hatching = VGroup()
    p = p_min + spacing / 2
    while p < p_max:
        line_pt = p * nrm
        ints = []
        for i in range(n):
            v1 = vertices[i]
            v2 = vertices[(i + 1) % n]
            edge_d = v2 - v1
            A_mat = np.array([[edge_d[0], -d[0]], [edge_d[1], -d[1]]])
            b_vec = np.array([line_pt[0] - v1[0], line_pt[1] - v1[1]])
            try:
                t, s = np.linalg.solve(A_mat, b_vec)
                if -1e-9 <= t <= 1 + 1e-9:
                    ints.append(v1 + t * edge_d)
            except np.linalg.LinAlgError:
                pass
        if len(ints) >= 2:
            projs = [float(np.dot(pt, d)) for pt in ints]
            i_min = int(np.argmin(projs))
            i_max = int(np.argmax(projs))
            ln = Line(ints[i_min], ints[i_max], color=color, stroke_width=stroke)
            hatching.add(ln)
        p += spacing
    return hatching


# ===================== SCENE 1 =====================
class Scene01_IsoTriangleVars(Scene):
    def construct(self):
        self.camera.background_color = "#FFFFFF"
        leg = 4
        A = np.array([-leg/2, -leg/2, 0])
        B = np.array([leg/2, -leg/2, 0])
        C = np.array([-leg/2, leg/2, 0])
        triangle = Polygon(A, B, C, color=BLACK_LINE, stroke_width=2,
                           fill_color=LIGHT_GRAY, fill_opacity=0.2)
        ra = right_angle_marker(A)
        mh, mv = (A + B) / 2, (A + C) / 2
        th, tv = single_tick(mh, UP), single_tick(mv, RIGHT)
        lah = Text("a", font_size=28, color=BLACK_LINE).move_to(mh + DOWN * 0.45)
        lav = Text("a", font_size=28, color=BLACK_LINE).move_to(mv + LEFT * 0.45)
        mhyp = (B + C) / 2
        lc = Text("c", font_size=28, color=BLACK_LINE).move_to(mhyp + np.array([0.4, 0.4, 0]))
        self.add(triangle, ra, th, tv, lah, lav, lc)


# ===================== SCENE 2 =====================
class Scene02_MidpointSquarePQRS(Scene):
    def construct(self):
        self.camera.background_color = "#FAF8F5"
        s = 3
        BL = np.array([-s, -s, 0]); BR = np.array([s, -s, 0])
        TR = np.array([s, s, 0]);   TL = np.array([-s, s, 0])
        outer = Polygon(BL, BR, TR, TL, color=DARK_GRAY, stroke_width=2, fill_opacity=0)
        P = np.array([0, s, 0]); Q = np.array([s, 0, 0])
        R = np.array([0, -s, 0]); S = np.array([-s, 0, 0])
        inner_fill = Polygon(P, Q, R, S, fill_color=BLUE_PRIMARY, fill_opacity=0.25,
                             stroke_opacity=0)
        dashed = VGroup()
        for p1, p2 in [(P, Q), (Q, R), (R, S), (S, P)]:
            dashed.add(DashedLine(p1, p2, color=GRAY_DASH, stroke_width=1.5,
                                  dash_length=0.15))
        area = Text("Area = 40", font_size=26, color=BLACK_LINE).move_to(ORIGIN)
        Pl = Text("P", font_size=22, color=BLACK_LINE).move_to(P + UP * 0.3)
        Ql = Text("Q", font_size=22, color=BLACK_LINE).move_to(Q + RIGHT * 0.3)
        Rl = Text("R", font_size=22, color=BLACK_LINE).move_to(R + DOWN * 0.3)
        Sl = Text("S", font_size=22, color=BLACK_LINE).move_to(S + LEFT * 0.3)
        self.add(outer, inner_fill, dashed, area, Pl, Ql, Rl, Sl)


# ===================== SCENE 3 =====================
class Scene03_UnitSquareDiagonal(Scene):
    def construct(self):
        self.camera.background_color = "#FFFFFF"
        s = 2
        BL = np.array([-s, -s, 0]); BR = np.array([s, -s, 0])
        TR = np.array([s, s, 0]);   TL = np.array([-s, s, 0])
        sq = Polygon(BL, BR, TR, TL, color=BLACK_LINE, stroke_width=2, fill_opacity=0)
        diag = Line(BL, TR, color=BLACK_LINE, stroke_width=2)
        label = Text("1 unit", font_size=26, color=BLACK_LINE).move_to((BL + BR) / 2 + DOWN * 0.4)
        self.add(sq, diag, label)


# ===================== SCENE 4 =====================
class Scene04_DoublingConstruction4(Scene):
    def construct(self):
        self.camera.background_color = "#F5F5F0"
        side = 3
        A = np.array([-1, -2.5, 0])
        B = A + np.array([side, 0, 0])
        C = A + np.array([side, side, 0])
        D = A + np.array([0, side, 0])
        primary = Polygon(A, B, C, D, color=BLACK_LINE, stroke_width=2,
                          fill_color=BLUE_PRIMARY, fill_opacity=0.2)
        disp = np.array([-side, side, 0])
        E = C + disp; F = A + disp
        hatching = make_hatching([A, C, E, F], angle=45*DEGREES,
                                  color=BLUE_DARK, spacing=0.3, stroke=1.0)
        diagonal = Line(A, C, color=BLACK_LINE, stroke_width=2)
        second_outline = Polygon(A, C, E, F, color=BLACK_LINE, stroke_width=2,
                                 fill_opacity=0)
        label = Text("4", font_size=26, color=BLACK_LINE).move_to((A + B) / 2 + DOWN * 0.4)
        self.add(primary, hatching, second_outline, diagonal, label)


# ===================== SCENE 5 =====================
class Scene05_RESTsqrt5(Scene):
    def construct(self):
        self.camera.background_color = "#FFFFFF"
        leg = 2.5
        A = np.array([-2, -1.5, 0])
        B = A + np.array([leg, 0, 0])
        C = A + np.array([0, leg, 0])
        triangle = Polygon(A, B, C, color=BLACK_LINE, stroke_width=2,
                           fill_color=LIGHT_GRAY, fill_opacity=0.15)
        outward = np.array([leg, leg, 0])
        D_sq = C + outward; E_sq = B + outward
        sq = Polygon(B, C, D_sq, E_sq, color=BLACK_LINE, stroke_width=2,
                     fill_color=BLUE_LIGHT_FILL, fill_opacity=0.2)
        ra = right_angle_marker(A)
        mh, mv = (A + B) / 2, (A + C) / 2
        th, tv = single_tick(mh, UP), single_tick(mv, RIGHT)
        lh = Text("√5", font_size=26, color=BLACK_LINE).move_to(mh + DOWN * 0.45)
        lv = Text("√5", font_size=26, color=BLACK_LINE).move_to(mv + LEFT * 0.5)
        ctr = (B + C + D_sq + E_sq) / 4
        rest = Text("REST", font_size=24, color=BLACK_LINE).move_to(ctr)
        self.add(triangle, sq, ra, th, tv, lh, lv, rest)


# ===================== SCENE 6 =====================
class Scene06_DashedOuterInnerArea18(Scene):
    def construct(self):
        self.camera.background_color = "#FAF8F5"
        s = 3
        BL = np.array([-s, -s, 0]); BR = np.array([s, -s, 0])
        TR = np.array([s, s, 0]);   TL = np.array([-s, s, 0])
        outer = VGroup()
        for p1, p2 in [(BL, BR), (BR, TR), (TR, TL), (TL, BL)]:
            outer.add(DashedLine(p1, p2, color=GRAY_MED, stroke_width=2,
                                  dash_length=0.18))
        P = np.array([0, s, 0]); Q = np.array([s, 0, 0])
        R = np.array([0, -s, 0]); S = np.array([-s, 0, 0])
        inner = Polygon(P, Q, R, S, color=BLUE_PRIMARY, stroke_width=2,
                        fill_color=BLUE_PRIMARY, fill_opacity=0.3)
        label = Text("Area = 18", font_size=26, color=BLACK_LINE).move_to(ORIGIN)
        self.add(outer, inner, label)


# ===================== SCENE 7 =====================
class Scene07_DoubleTicks(Scene):
    def construct(self):
        self.camera.background_color = "#FFFFFF"
        leg = 4
        A = np.array([-leg/2, -leg/2, 0])
        B = np.array([leg/2, -leg/2, 0])
        C = np.array([-leg/2, leg/2, 0])
        triangle = Polygon(A, B, C, color=BLACK_LINE, stroke_width=2, fill_opacity=0)
        ra = right_angle_marker(A)
        mh, mv = (A + B) / 2, (A + C) / 2
        dth = double_tick(mh, UP, RIGHT)
        dtv = double_tick(mv, RIGHT, UP)
        self.add(triangle, ra, dth, dtv)


# ===================== SCENE 8 =====================
class Scene08_ThreeSquaresProgression(Scene):
    def construct(self):
        self.camera.background_color = "#F5F5F0"
        # Square A
        A_BL = np.array([-2.25, 0, 0]); A_BR = np.array([-0.75, 0, 0])
        A_TR = np.array([-0.75, 1.5, 0]); A_TL = np.array([-2.25, 1.5, 0])
        # Square B (diamond on A's diagonal)
        B_V1 = A_BL; B_V2 = A_TR
        B_V3 = A_TR + np.array([1.5, -1.5, 0])  # (0.75, 0)
        B_V4 = A_BL + np.array([1.5, -1.5, 0])  # (-0.75, -1.5)
        # Square C (on B's vertical diagonal)
        C_TL = B_V2; C_BL = B_V4
        C_BR = C_BL + np.array([3, 0, 0])
        C_TR = C_TL + np.array([3, 0, 0])

        C_poly = Polygon(C_BL, C_BR, C_TR, C_TL, color=BLACK_LINE, stroke_width=2,
                         fill_color=BLUE_DARK, fill_opacity=0.12)
        hatching_C = make_hatching([C_BL, C_BR, C_TR, C_TL],
                                    angle=60*DEGREES, color=BLUE_DARK, spacing=0.3)

        B_poly = Polygon(B_V1, B_V2, B_V3, B_V4, color=BLACK_LINE, stroke_width=2,
                         fill_color=BLUE_PRIMARY, fill_opacity=0.15)
        hatching_B = make_hatching([B_V1, B_V2, B_V3, B_V4],
                                    angle=30*DEGREES, color=BLUE_PRIMARY, spacing=0.3)

        A_poly = Polygon(A_BL, A_BR, A_TR, A_TL, color=BLACK_LINE, stroke_width=2,
                         fill_color=BLUE_VERY_LIGHT, fill_opacity=0.25)

        A_lbl = Text("A", font_size=28, color=BLACK_LINE).move_to(np.array([-1.5, 0.75, 0]))
        B_lbl = Text("B", font_size=28, color=BLACK_LINE).move_to(np.array([-1.5, -0.5, 0]))
        C_lbl = Text("C", font_size=28, color=BLACK_LINE).move_to(np.array([1.5, 0, 0]))

        self.add(C_poly, hatching_C, B_poly, hatching_B, A_poly,
                 A_lbl, B_lbl, C_lbl)


# ===================== SCENE 9 =====================
class Scene09_Triangle10c(Scene):
    def construct(self):
        self.camera.background_color = "#FFFFFF"
        leg = 4
        A = np.array([-leg/2, -leg/2, 0])
        B = np.array([leg/2, -leg/2, 0])
        C = np.array([-leg/2, leg/2, 0])
        triangle = Polygon(A, B, C, color=BLACK_LINE, stroke_width=2, fill_opacity=0)
        ra = right_angle_marker(A)
        mh, mv = (A + B) / 2, (A + C) / 2
        th, tv = single_tick(mh, UP), single_tick(mv, RIGHT)
        l10h = Text("10", font_size=26, color=BLACK_LINE).move_to(mh + DOWN * 0.45)
        l10v = Text("10", font_size=26, color=BLACK_LINE).move_to(mv + LEFT * 0.55)
        mhyp = (B + C) / 2
        lc = Text("c", font_size=28, color=BLACK_LINE).move_to(mhyp + np.array([0.4, 0.4, 0]))
        self.add(triangle, ra, th, tv, l10h, l10v, lc)


# ===================== SCENE 10 =====================
class Scene10_FourTriangles(Scene):
    def construct(self):
        self.camera.background_color = "#FFFFFF"
        s = 2.5
        BL = np.array([-s, -s, 0]); BR = np.array([s, -s, 0])
        TR = np.array([s, s, 0]);   TL = np.array([-s, s, 0])
        square = Polygon(BL, BR, TR, TL, color=BLACK_LINE, stroke_width=2, fill_opacity=0)
        d1 = Line(BL, TR, color=BLACK_LINE, stroke_width=2)
        d2 = Line(TL, BR, color=BLACK_LINE, stroke_width=2)
        ctr = np.array([0, 0, 0])
        c1 = (ctr + TL + TR) / 3
        c2 = (ctr + TR + BR) / 3
        c3 = (ctr + BR + BL) / 3
        c4 = (ctr + BL + TL) / 3
        l1 = Text("1", font_size=26, color=BLACK_LINE).move_to(c1)
        l2 = Text("2", font_size=26, color=BLACK_LINE).move_to(c2)
        l3 = Text("3", font_size=26, color=BLACK_LINE).move_to(c3)
        l4 = Text("4", font_size=26, color=BLACK_LINE).move_to(c4)
        self.add(square, d1, d2, l1, l2, l3, l4)


# ===================== SCENE 11 =====================
class Scene11_SqrtTwoBubble(Scene):
    def construct(self):
        self.camera.background_color = "#FFFFFF"
        s = 1.5
        cx = -2.5
        BL = np.array([cx - s, -s, 0]); BR = np.array([cx + s, -s, 0])
        TR = np.array([cx + s, s, 0]); TL = np.array([cx - s, s, 0])
        square = Polygon(BL, BR, TR, TL, color=BLACK_LINE, stroke_width=2, fill_opacity=0)
        diag = Line(BL, TR, color=BLACK_LINE, stroke_width=2)
        l1 = Text("1", font_size=26, color=BLACK_LINE).move_to((BL + BR) / 2 + DOWN * 0.4)
        # sqrt(2) label along diagonal
        mid_d = (BL + TR) / 2
        sqrt2 = Text("√2", font_size=26, color=BLACK_LINE)
        sqrt2.rotate(45 * DEGREES)
        sqrt2.move_to(mid_d + np.array([-0.35, 0.35, 0]))
        # Bubble
        mid_right = (BR + TR) / 2
        bubble_text = Text("Can this be m/n?", font_size=22, color=BLACK_LINE)
        bubble_text.move_to(mid_right + RIGHT * 3.0)
        bubble = RoundedRectangle(corner_radius=0.18,
                                   width=bubble_text.width + 0.5,
                                   height=bubble_text.height + 0.4,
                                   color=BLACK_LINE, stroke_width=1,
                                   fill_color=TEXT_BUBBLE_GRAY, fill_opacity=1)
        bubble.move_to(bubble_text.get_center())
        connector = Line(mid_right, bubble.get_left(), color=BLACK_LINE, stroke_width=1)
        self.add(square, diag, l1, sqrt2, connector, bubble, bubble_text)


# ===================== SCENE 12 =====================
class Scene12_RESTArea50(Scene):
    def construct(self):
        self.camera.background_color = "#FFFFFF"
        leg = 2.5
        A = np.array([-2, -1.5, 0])
        B = A + np.array([leg, 0, 0])
        C = A + np.array([0, leg, 0])
        triangle = Polygon(A, B, C, color=BLACK_LINE, stroke_width=2,
                           fill_color=LIGHT_GRAY, fill_opacity=0.15)
        outward = np.array([leg, leg, 0])
        D_sq = C + outward; E_sq = B + outward
        sq = Polygon(B, C, D_sq, E_sq, color=BLACK_LINE, stroke_width=2,
                     fill_color=BLUE_LIGHT_FILL, fill_opacity=0.25)
        ra = right_angle_marker(A)
        mh, mv = (A + B) / 2, (A + C) / 2
        th, tv = single_tick(mh, UP), single_tick(mv, RIGHT)
        lh = Text("a", font_size=26, color=BLACK_LINE).move_to(mh + DOWN * 0.4)
        lv = Text("a", font_size=26, color=BLACK_LINE).move_to(mv + LEFT * 0.4)
        ctr = (B + C + D_sq + E_sq) / 4
        area = Text("Area = 50", font_size=24, color=BLACK_LINE).move_to(ctr)
        rest = Text("REST", font_size=20, color=BLACK_LINE).move_to(ctr + np.array([0, 0.7, 0]))
        self.add(triangle, sq, ra, th, tv, lh, lv, area, rest)


# ===================== SCENE 13 =====================
class Scene13_PrimarySecondary5x(Scene):
    def construct(self):
        self.camera.background_color = "#F5F5F0"
        side = 3
        A = np.array([-1, -2.5, 0])
        B = A + np.array([side, 0, 0])
        C = A + np.array([side, side, 0])
        D = A + np.array([0, side, 0])
        primary = Polygon(A, B, C, D, color=BLACK_LINE, stroke_width=2,
                          fill_color=BLUE_PRIMARY, fill_opacity=0.25)
        disp = np.array([-side, side, 0])
        E = C + disp; F = A + disp
        hatching = make_hatching([A, C, E, F], angle=45*DEGREES,
                                  color=BLUE_DARK, spacing=0.3, stroke=1.0)
        diagonal = Line(A, C, color=BLACK_LINE, stroke_width=2)
        second_outline = Polygon(A, C, E, F, color=BLACK_LINE, stroke_width=2,
                                 fill_opacity=0)
        l5 = Text("5", font_size=26, color=BLACK_LINE).move_to((A + B) / 2 + DOWN * 0.4)
        sec_ctr = (A + C + E + F) / 4
        lx = Text("x", font_size=30, color=BLACK_LINE).move_to(sec_ctr)
        self.add(primary, hatching, second_outline, diagonal, l5, lx)