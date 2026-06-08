from manim import *
import numpy as np


class Q01(Scene):
    def construct(self):
        self.camera.background_color = "#F5F5F0"

        s = 2.0

        # ── Primary square vertices ─────────────────────
        A = np.array([0.0, 0.0, 0.0])
        B = np.array([s, 0.0, 0.0])
        C = np.array([s, s, 0.0])
        D = np.array([0.0, s, 0.0])

        # ── Diamond (second square) on diagonal A→C ─────
        E = np.array([0.0, 2 * s, 0.0])
        F = np.array([-s, s, 0.0])

        # ── Primary square: medium blue, 30 % fill ──────
        primary = Polygon(
            A, B, C, D,
            stroke_color="#1A1A1A",
            stroke_width=2,
            fill_color="#4A90D9",
            fill_opacity=0.30,
        )

        # ── Diamond outline only (hatching provides fill) ─
        diamond = Polygon(
            A, C, E, F,
            stroke_color="#1A1A1A",
            stroke_width=2,
            fill_opacity=0,
        )

        # ── Diagonal shared edge ─────────────────────────
        diag = Line(A, C, stroke_color="#1A1A1A", stroke_width=2)

        # ── 45° hatching inside the diamond ──────────────
        #    Analytically clipped: for line y = x + c the
        #    diamond edges FA and CE give entry/exit points.
        #    c runs from 0 (edge AC) to 4 (edge EF).
        dc = 0.08  # perpendicular gap ≈ dc/√2 ≈ 7–8 px at 1080p
        hatching = VGroup()
        c_val = dc
        while c_val < 4.0:
            p1 = np.array([-c_val / 2, c_val / 2, 0.0])
            p2 = np.array([2.0 - c_val / 2, 2.0 + c_val / 2, 0.0])
            hatching.add(
                Line(p1, p2, stroke_color="#2E5C8A", stroke_width=1)
            )
            c_val += dc

        # ── Centre the whole figure on screen ────────────
        VGroup(hatching, diamond, primary, diag).move_to(ORIGIN)

        # ── Render back-to-front ─────────────────────────
        self.add(hatching)   # hatching behind everything
        self.add(diamond)    # diamond outline
        self.add(primary)    # primary square (semi-transparent fill)
        self.add(diag)       # diagonal on top

        # ── Label inside primary square ──────────────────
        label = Text(
            "Area = 9 sq units",
            font_size=20,
            color="#1A1A1A",
        )
        label.move_to(primary.get_center())
        self.add(label)
