from manim import *
import numpy as np

class DoubledSquare(Scene):
    def construct(self):
        self.camera.background_color = "#F5F5F0"
        
        BLUE_PRIMARY = "#4A90D9"
        BLUE_SECONDARY = "#2E5C8A"
        BLACK_LINE = "#1A1A1A"
        
        # Primary square corners (side = 3, area = 9)
        A = np.array([-1, -3, 0])   # bottom-left
        B = np.array([ 2, -3, 0])   # bottom-right
        C = np.array([ 2,  0, 0])   # top-right
        D = np.array([-1,  0, 0])   # top-left
        
        primary = Polygon(
            A, B, C, D,
            color=BLACK_LINE,
            stroke_width=2,
            fill_color=BLUE_PRIMARY,
            fill_opacity=0.30,
        )
        
        # Second square: built on diagonal AC, rotated 45° (diamond)
        # Perpendicular displacement (-3, 3) puts it above primary square
        E = np.array([-1,  3, 0])   # C + (-3, 3)
        F = np.array([-4,  0, 0])   # A + (-3, 3)
        
        second = Polygon(
            A, C, E, F,
            color=BLACK_LINE,
            stroke_width=2,
            fill_color=BLUE_SECONDARY,
            fill_opacity=0.15,
        )
        
        # Diagonal hatching at 45 degrees (lines parallel to AC: y = x + c)
        hatching = VGroup()
        spacing = 0.35
        c = -2 + spacing
        while c < 4:
            # Endpoints on edges FA (y=-x-4) and CE (y=-x+2)
            x1 = (-4 - c) / 2
            y1 = x1 + c
            x2 = ( 2 - c) / 2
            y2 = x2 + c
            hatch_line = Line(
                np.array([x1, y1, 0]),
                np.array([x2, y2, 0]),
                color=BLUE_SECONDARY,
                stroke_width=1.2,
            )
            hatching.add(hatch_line)
            c += spacing
        
        # Diagonal line (shared edge) - drawn on top
        diagonal = Line(A, C, color=BLACK_LINE, stroke_width=2)
        
        # Outline of second square redrawn on top of hatching
        second_outline = Polygon(
            A, C, E, F,
            color=BLACK_LINE,
            stroke_width=2,
            fill_opacity=0,
        )
        
        # Text label centered inside primary square
        center_primary = np.array([(A[0] + C[0]) / 2, (A[1] + C[1]) / 2, 0])
        label = Text(
            "Area = 9 sq units",
            font="sans-serif",
            font_size=22,
            color=BLACK_LINE,
        )
        label.move_to(center_primary)
        
        # Layering: fills -> hatching -> outlines -> diagonal -> label
        self.add(primary, second, hatching, second_outline, diagonal, label)