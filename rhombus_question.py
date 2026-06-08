from manim import *

# Color palette
CREAM_BG = "#FAF7F0"
NAVY     = "#1A1A2E"
BLUE     = "#1F4FE0"
RED      = "#E03020"
ORANGE   = "#FF9302"


class RhombusQuestion(Scene):
    def construct(self):
        self.camera.background_color = CREAM_BG

        # --- QUESTION TEXT (top of frame) ---
        q_title = Text(
            "Question:",
            font="Cambria", weight=BOLD, color=NAVY, font_size=32,
        )
        q_body = Text(
            "Find the area of a rhombus with diagonals 16 cm and 12 cm.",
            font="Cambria", weight=BOLD, color=NAVY, font_size=28,
        )
        header = VGroup(q_title, q_body).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        header.to_corner(UL, buff=0.6)

        # --- RHOMBUS GEOMETRY ---
        # Scale factor: 1 cm = 0.25 units
        scale = 0.25
        center = np.array([0, -1.0, 0])  # center of rhombus

        # Vertices (diamond orientation)
        top    = center + UP    * (16 / 2) * scale   # 8 * 0.25 = 2.0 up
        bottom = center + DOWN  * (16 / 2) * scale
        left   = center + LEFT  * (12 / 2) * scale   # 6 * 0.25 = 1.5 left
        right  = center + RIGHT * (12 / 2) * scale

        # --- RHOMBUS OUTLINE ---
        rhombus = Polygon(
            top, right, bottom, left,
            color=BLUE, stroke_width=3,
            fill_color=BLUE, fill_opacity=0.05,
        )

        # --- DIAGONALS (dashed) ---
        diag_vertical = DashedLine(
            top, bottom, color=NAVY, stroke_width=2,
            dash_length=0.12, dashed_ratio=0.6,
        )
        diag_horizontal = DashedLine(
            left, right, color=NAVY, stroke_width=2,
            dash_length=0.12, dashed_ratio=0.6,
        )

        # --- RIGHT-ANGLE INDICATOR AT CENTER ---
        right_angle = Square(side_length=0.22, color=NAVY, stroke_width=1.5)
        right_angle.move_to(center + UR * 0.13)

        # --- VERTEX DOTS (optional, for polish) ---
        vertex_dots = VGroup(*[
            Dot(v, color=NAVY, radius=0.05)
            for v in [top, right, bottom, left]
        ])

        # --- DIMENSION LABELS ---
        # "16 cm" on the vertical diagonal (placed to the RIGHT of upper half)
        label_16 = Text(
            "16 cm", font="Cambria", color=RED, font_size=24,
        )
        label_16.next_to(diag_vertical.get_center(), RIGHT, buff=0.25)

        # "12 cm" on the horizontal diagonal (placed BELOW the lower half)
        label_12 = Text(
            "12 cm", font="Cambria", color=RED, font_size=24,
        )
        label_12.next_to(diag_horizontal.get_center(), DOWN, buff=0.25)

        # --- UNKNOWN "?" MARKER ---
        unknown = Text(
            "?", font="Cambria", weight=BOLD,
            color=ORANGE, font_size=44,
        )
        unknown.move_to(center + UP * 0.6 + LEFT * 0.5)

        # --- ASSEMBLE FIGURE ---
        figure = VGroup(
            rhombus, diag_vertical, diag_horizontal,
            right_angle, vertex_dots,
            label_16, label_12, unknown,
        )

        # --- DISPLAY ---
        self.add(header, figure)
        self.wait(1)