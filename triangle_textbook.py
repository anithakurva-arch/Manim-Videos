from manim import *

# Color palette matching the image
CREAM_BG = "#FAF7F0"
NAVY = "#1A1A2E"
BLUE = "#1F4FE0"
RED = "#E03020"


class TextbookTriangle(Scene):
    def construct(self):
        self.camera.background_color = CREAM_BG

        # --- TITLE & QUESTION TEXT ---
        title = Text(
            "Section 2: Find the Area of the Following Triangles",
            font="Cambria", weight=BOLD, color=NAVY, font_size=30,
        )
        question = Text(
            "1. Calculate the area of the triangle shown below.",
            font="Cambria", weight=BOLD, color=NAVY, font_size=28,
        )
        header = VGroup(title, question).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        header.to_corner(UL, buff=0.5)

        # --- TRIANGLE VERTICES ---
        # A = bottom-left (right angle), B = bottom-right, C = top-left
        scale = 0.4  # 1 cm = 0.4 units
        A = np.array([-2.0, -2.0, 0])
        B = A + RIGHT * 12 * scale       # 12 cm to the right
        C = A + UP * 9 * scale            # 9 cm up

        # Triangle as 3 lines (so we can style each side independently)
        side_AC = Line(A, C, color=BLUE, stroke_width=3)
        side_AB = Line(A, B, color=BLUE, stroke_width=3)
        side_BC = Line(B, C, color=BLUE, stroke_width=3)
        triangle = VGroup(side_AC, side_AB, side_BC)

        # --- VERTEX DOTS ---
        dot_A = Dot(A, color=NAVY, radius=0.04)
        dot_B = Dot(B, color=NAVY, radius=0.04)
        dot_C = Dot(C, color=NAVY, radius=0.04)

        # --- VERTEX LABELS ---
        label_C = Text("C", font="Cambria", color=NAVY, font_size=24).next_to(C, UL, buff=0.08)
        label_A = Text("A", font="Cambria", color=NAVY, font_size=24).next_to(A, DL, buff=0.08)
        label_B = Text("B", font="Cambria", color=NAVY, font_size=24).next_to(B, DR, buff=0.08)

        # --- RIGHT-ANGLE INDICATOR (small square at A) ---
        right_angle = Square(side_length=0.25, color=NAVY, stroke_width=1.5)
        right_angle.move_to(A + UR * 0.15)

        # --- DIMENSION LABELS (no arrows, textbook style) ---
        label_9cm = Text("9 cm", font="Cambria", color=RED, font_size=22)
        label_9cm.rotate(PI / 2)  # vertical orientation
        label_9cm.next_to(side_AC, LEFT, buff=0.15)

        label_12cm = Text("12 cm", font="Cambria", color=NAVY, font_size=22)
        label_12cm.next_to(side_AB, DOWN, buff=0.2)

        # --- ASSEMBLE & DISPLAY ---
        figure = VGroup(
            triangle, dot_A, dot_B, dot_C,
            label_A, label_B, label_C,
            right_angle, label_9cm, label_12cm,
        ).shift(DOWN * 0.5)

        self.add(header, figure)
        self.wait(2)