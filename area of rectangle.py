from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.openai import OpenAIService

# ─── Storyboard Color Palette ──────────────────────────────
SOFT_GREEN     = "#E8F5E9"
LIGHT_GREEN    = "#C8E6C9"
MED_GREEN      = "#A5D6A7"
DARK_GREEN     = "#2E7D32"
DARK_NAVY      = "#0D2540"
TAN            = "#D7CCC8"
BROWN          = "#795548"
BLUE_C         = "#1565C0"
PALE_BLUE      = "#BBDEFB"
VERY_PALE_BLUE = "#E3F2FD"
YELLOW_C       = "#FFC107"
PALE_YELLOW    = "#FFF9C4"
RED_C          = "#C62828"
PALE_RED       = "#FFCDD2"
ORANGE_FILL    = "#FFE0B2"
BURNT_ORANGE   = "#D84315"
LAV            = "#E1BEE7"
PINK           = "#F8BBD0"
DARK_GREY      = "#424242"
LIGHT_GREY     = "#BDBDBD"

TTS_INSTRUCTIONS = """
Voice & Personality:
You are a warm, patient, and encouraging math teacher speaking to a 
middle-school student. Your tone is friendly, calm, and confident.

Pacing:
Speak at a MODERATE-TO-SLOW pace. Prioritize clarity over speed.

Variables and Math Terms:
When pronouncing single-letter variables, slow down and articulate 
each letter clearly with a brief micro-pause.

Formulas:
When reading a formula, slow further. Pause briefly between each 
component so the student can match spoken word to symbol on screen.

Numbers and Units:
Pronounce numbers clearly. For units like "centimeter square" or 
"meter square," say them with a confident, deliberate cadence.

Emphasis:
Naturally emphasize key terms: shape names, formulas, final answers.

Pauses:
Add a natural beat at commas, a slightly longer pause at periods.

Mood:
Encouraging, curious, and warm.

Do NOT rush, flatten into monotone, add filler, or paraphrase.
"""


# ─── Helper Functions ──────────────────────────────────────
def poppins(text, size=22, color=DARK_GREY, weight=NORMAL):
    return Text(text, font="Poppins", font_size=size,
                color=color, weight=weight)

def title_text(s, color=DARK_NAVY, size=32):
    return poppins(s, size=size, color=color, weight=BOLD).to_edge(UP, buff=0.5)

def make_card(content, fill=WHITE, border=DARK_NAVY, pad=0.3,
              border_width=2, radius=0.15):
    bg = SurroundingRectangle(
        content, color=border, stroke_width=border_width,
        corner_radius=radius, buff=pad, fill_color=fill, fill_opacity=1,
    )
    return VGroup(bg, content)

def make_garden(scale=1.0, show_labels=True):
    inner = Rectangle(width=4.4*scale, height=3.2*scale,
                      color=DARK_NAVY, stroke_width=3,
                      fill_color=LIGHT_GREEN, fill_opacity=1)
    outer = Rectangle(width=5.6*scale, height=4.4*scale,
                      color=DARK_NAVY, stroke_width=2,
                      fill_color=TAN, fill_opacity=1)
    outer.move_to(inner.get_center())
    inner.set_z_index(1)
    grp = VGroup(outer, inner)
    if show_labels:
        l14 = poppins("14 m", 20, DARK_GREY).next_to(inner, UP, buff=0.1)
        l12 = poppins("12 m", 20, DARK_GREY).next_to(inner, RIGHT, buff=0.1)
        arrow2 = Arrow(outer.get_left()+RIGHT*0.05,
                       inner.get_left()+LEFT*0.05,
                       color=DARK_GREY, stroke_width=2,
                       buff=0, max_tip_length_to_length_ratio=0.3)
        l2 = poppins("2 m", 16, DARK_GREY).next_to(arrow2, DOWN, buff=0.05)
        grp.add(l14, l12, arrow2, l2)
    return grp

def grid_rect(cols, rows, cell=0.5, fill=WHITE, fill_op=0,
              line_color=LIGHT_GREY, outline=DARK_NAVY, numbers=False,
              num_color=DARK_GREY):
    w, h = cols*cell, rows*cell
    rect = Rectangle(width=w, height=h, color=outline, stroke_width=3,
                     fill_color=fill, fill_opacity=fill_op)
    lines = VGroup()
    for i in range(1, cols):
        x = -w/2 + i*cell
        lines.add(Line([x,-h/2,0],[x,h/2,0],
                       color=line_color, stroke_width=1))
    for j in range(1, rows):
        y = -h/2 + j*cell
        lines.add(Line([-w/2,y,0],[w/2,y,0],
                       color=line_color, stroke_width=1))
    grp = VGroup(rect, lines)
    if numbers:
        nums = VGroup()
        n = 1
        for r in range(rows):
            for c in range(cols):
                cx = -w/2 + (c+0.5)*cell
                cy = h/2 - (r+0.5)*cell
                nums.add(poppins(str(n), 10, num_color).move_to([cx,cy,0]))
                n += 1
        grp.add(nums)
    return grp

def fill_cells(cols, rows, cell, indices_colors, base_pos=ORIGIN):
    """Return VGroup of small filled squares at cell indices."""
    w, h = cols*cell, rows*cell
    squares = VGroup()
    for (r, c, color) in indices_colors:
        cx = base_pos[0] - w/2 + (c+0.5)*cell
        cy = base_pos[1] + h/2 - (r+0.5)*cell
        sq = Square(side_length=cell*0.96, color=DARK_NAVY,
                    stroke_width=1, fill_color=color, fill_opacity=1)
        sq.move_to([cx, cy, 0])
        squares.add(sq)
    return squares

def check_icon(color=DARK_GREEN, size=0.3):
    return poppins("✓", size*100, color, BOLD)

def cross_icon(color=RED_C, size=0.3):
    return poppins("✗", size*100, color, BOLD)


# ─── Main Scene ────────────────────────────────────────────
class GardenAreaExplainer(VoiceoverScene):
    def construct(self):
        self.camera.background_color = WHITE
        self.set_speech_service(
            OpenAIService(
                voice="nova",
                model="gpt-4o-mini-tts",
                transcription_model="medium",
                instructions=TTS_INSTRUCTIONS,
            ),
            create_subcaption=False,
        )

        # Utility to clear everything
        def clear_all(rt=0.6):
            mobs = [m for m in self.mobjects]
            if mobs:
                self.play(*[FadeOut(m) for m in mobs], run_time=rt)

        # ========================================================
        # ROW 1 — Garden Problem Intro
        # ========================================================
        self.camera.background_color = SOFT_GREEN
        title1 = title_text("The Garden Problem")
        bush_l = Circle(radius=0.25, color=DARK_GREEN,
                        fill_color=DARK_GREEN, fill_opacity=1)
        bush_l.to_corner(DL, buff=0.4)
        bush_r = bush_l.copy().to_corner(DR, buff=0.4)
        fence = Line(LEFT*7, RIGHT*7, color=BROWN, stroke_width=4)
        fence.to_edge(DOWN, buff=0.15)
        garden = make_garden(scale=1.0).shift(UP*0.1)
        banner_bg = RoundedRectangle(width=5.5, height=0.7,
                                     corner_radius=0.1,
                                     fill_color=BLUE_C, fill_opacity=1,
                                     stroke_width=0)
        banner_text = poppins("How many square metres of tiles?",
                              20, WHITE, BOLD)
        banner = VGroup(banner_bg, banner_text)
        banner.next_to(garden, DOWN, buff=0.4)

        with self.voiceover(
            text='<bookmark mark="b1"/>Imagine you are helping your family '
                 'tile a courtyard. <bookmark mark="b2"/>It is a rectangular '
                 'vegetable patch, fourteen metres by twelve metres. '
                 '<bookmark mark="b3"/>You want to build a two-metre-wide '
                 'walking path all around it, paved with tiles. '
                 '<bookmark mark="b4"/>How many square metres of tiles '
                 'do you need to buy?'
        ) as t:
            self.wait_until_bookmark("b1")
            self.play(FadeIn(title1), FadeIn(bush_l), FadeIn(bush_r),
                      Create(fence), run_time=0.8)
            self.wait_until_bookmark("b2")
            self.play(Create(garden[1]), run_time=1.0)
            self.play(FadeIn(garden[2]), FadeIn(garden[3]), run_time=0.6)
            self.wait_until_bookmark("b3")
            self.play(FadeIn(garden[0]), run_time=0.8)
            self.play(Create(garden[4]), FadeIn(garden[5]), run_time=0.6)
            self.wait_until_bookmark("b4")
            self.play(FadeIn(banner), run_time=0.7)
        self.wait(0.5)
        clear_all()

        # ========================================================
        # ROW 2 — Trap warning
        # ========================================================
        self.camera.background_color = WHITE
        mini_garden = make_garden(scale=0.55, show_labels=False).set_opacity(0.7)
        mini_garden.move_to(UP*0.5)
        warn_tri = Triangle(color=BLACK, stroke_width=2,
                            fill_color=YELLOW_C, fill_opacity=1).scale(0.7)
        warn_tri.move_to(mini_garden.get_center())
        warn_excl = poppins("!", 40, BLACK, BOLD).move_to(warn_tri.get_center())
        line1 = poppins("This question hides a trap.", 22, DARK_GREY)
        trap_word = poppins("trap", 22, RED_C, BOLD)
        line1_grp = VGroup(line1).next_to(mini_garden, DOWN, buff=0.6)
        line2 = poppins("Today we will learn to decode it.", 22, DARK_GREY)
        line2.next_to(line1_grp, DOWN, buff=0.2)

        with self.voiceover(
            text='<bookmark mark="b1"/>This question appears straightforward, '
                 'but it <bookmark mark="b2"/>hides a trap that has misled '
                 'many learners. <bookmark mark="b3"/>Today we will learn '
                 'to decode it.'
        ) as t:
            self.wait_until_bookmark("b1")
            self.play(FadeIn(mini_garden), run_time=0.7)
            self.wait_until_bookmark("b2")
            self.play(FadeIn(warn_tri), FadeIn(warn_excl), run_time=0.7)
            self.play(FadeIn(line1_grp), run_time=0.6)
            self.wait_until_bookmark("b3")
            self.play(FadeIn(line2), run_time=0.6)
        self.wait(0.4)
        clear_all()

        # ========================================================
        # ROW 3 — Learning Objectives
        # ========================================================
        t3 = title_text("Learning Objectives")
        def obj_card(text_str, icon_str):
            chk = poppins("✓", 24, DARK_GREEN, BOLD)
            txt = poppins(text_str, 18, DARK_GREY)
            rect_icon = Rectangle(width=0.5, height=0.3,
                                  color=DARK_NAVY, stroke_width=2)
            if icon_str == "nested":
                inner_i = Rectangle(width=0.3, height=0.18,
                                    color=DARK_NAVY, stroke_width=1.5)
                inner_i.move_to(rect_icon.get_center())
                rect_icon = VGroup(rect_icon, inner_i)
            row = VGroup(chk, txt, rect_icon).arrange(RIGHT, buff=0.3)
            return make_card(row, fill=WHITE, border=DARK_GREEN,
                             border_width=2, pad=0.25, radius=0.15)
        c1 = obj_card("Find the area of any rectangular region", "single")
        c2 = obj_card("Read composite figures before you compute", "nested")
        cards = VGroup(c1, c2).arrange(DOWN, buff=0.4).move_to(ORIGIN)

        with self.voiceover(
            text='<bookmark mark="b1"/>By the end of this video, you will be '
                 'able to <bookmark mark="b2"/>find the area of any '
                 'rectangular region. <bookmark mark="b3"/>You will also know '
                 'how to read composite figures like this path before '
                 'you compute.'
        ) as t:
            self.wait_until_bookmark("b1")
            self.play(FadeIn(t3), run_time=0.6)
            self.wait_until_bookmark("b2")
            self.play(FadeIn(c1), run_time=0.7)
            self.wait_until_bookmark("b3")
            self.play(FadeIn(c2), run_time=0.7)
        self.wait(0.4)
        clear_all()

        # ========================================================
        # ROW 4 — Roadmap
        # ========================================================
        t4 = title_text("Today's Roadmap")
        labels4 = ["What Area Means", "Build the Formula",
                   "Confront Misconception", "Solve the Garden Problem"]
        colors4 = [LIGHT_GREEN, PALE_BLUE, PALE_RED, TAN]
        nodes = VGroup()
        for i, (lab, col) in enumerate(zip(labels4, colors4)):
            node = Circle(radius=0.4, color=DARK_NAVY,
                          stroke_width=2,
                          fill_color=col, fill_opacity=1)
            num = poppins(str(i+1), 18, DARK_NAVY, BOLD).move_to(node.get_center())
            label = poppins(lab, 14, DARK_GREY).next_to(node, DOWN, buff=0.3)
            nodes.add(VGroup(node, num, label))
        nodes.arrange(RIGHT, buff=1.0).move_to(ORIGIN)
        arrows4 = VGroup()
        for i in range(3):
            a = Arrow(nodes[i][0].get_right(), nodes[i+1][0].get_left(),
                      color=DARK_GREY, stroke_width=2,
                      buff=0.05, max_tip_length_to_length_ratio=0.2)
            arrows4.add(a)

        with self.voiceover(
            text='<bookmark mark="b1"/>We will begin by revisiting what area '
                 'truly means. <bookmark mark="b2"/>Then we will build the '
                 'rectangle formula from intuition, <bookmark mark="b3"/>'
                 'confront a common misconception, <bookmark mark="b4"/>and '
                 'solve this garden problem step by step.'
        ) as t:
            self.play(FadeIn(t4), run_time=0.5)
            self.wait_until_bookmark("b1")
            self.play(FadeIn(nodes[0]), run_time=0.6)
            self.wait_until_bookmark("b2")
            self.play(Create(arrows4[0]), FadeIn(nodes[1]), run_time=0.6)
            self.wait_until_bookmark("b3")
            self.play(Create(arrows4[1]), FadeIn(nodes[2]), run_time=0.6)
            self.wait_until_bookmark("b4")
            self.play(Create(arrows4[2]), FadeIn(nodes[3]), run_time=0.6)
        self.wait(0.4)
        clear_all()

        # ========================================================
        # ROW 5 — Rectangle Properties
        # ========================================================
        t5 = title_text("Rectangle Properties")
        rect5 = Rectangle(width=3.2, height=2.0, color=DARK_NAVY,
                          stroke_width=3, fill_color=WHITE, fill_opacity=1)
        rect5.shift(LEFT*1.2)
        # right-angle markers
        rams = VGroup()
        for corner, off in [(rect5.get_corner(UL), DR), (rect5.get_corner(UR), DL),
                            (rect5.get_corner(DL), UR), (rect5.get_corner(DR), UL)]:
            sq = Square(side_length=0.15, color=DARK_NAVY, stroke_width=2)
            sq.move_to(corner + np.array([off[0]*0.075, off[1]*0.075, 0]))
            rams.add(sq)
       a_top = poppins("a", 18, DARK_GREY).next_to(rect5, UP, buff=0.15)
        a_bot = poppins("a", 18, DARK_GREY).next_to(rect5, DOWN, buff=0.15)
        b_left = poppins("b", 18, DARK_GREY).next_to(rect5, LEFT, buff=0.15)
        b_right = poppins("b", 18, DARK_GREY).next_to(rect5, RIGHT, buff=0.15)
        ann1 = poppins("• 4 right angles", 16, DARK_GREY)
        ann2 = poppins("• Opposite sides equal", 16, DARK_GREY)
        anns = VGroup(ann1, ann2).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        anns.next_to(rect5, RIGHT, buff=1.2)

        with self.voiceover(
            text='<bookmark mark="b1"/>Before we move forward, let us revisit '
                 'something you have worked with before. <bookmark mark="b2"/>'
                 'A rectangle has four right angles, <bookmark mark="b3"/>and '
                 'its opposite sides are equal.'
        ) as t:
            self.play(FadeIn(t5), run_time=0.5)
            self.wait_until_bookmark("b1")
            self.play(Create(rect5), run_time=1.0)
            self.play(FadeIn(a_top), FadeIn(a_bot),
                      FadeIn(b_left), FadeIn(b_right), run_time=0.6)
            self.wait_until_bookmark("b2")
            self.play(FadeIn(rams), FadeIn(ann1), run_time=0.7)
            self.wait_until_bookmark("b3")
            self.play(FadeIn(ann2), run_time=0.6)
        self.wait(0.4)
        clear_all()

        # ========================================================
        # ROW 6 — Unit squares
        # ========================================================
        grid6 = grid_rect(5, 3, cell=0.6, numbers=True).move_to(LEFT*1.5)
        callout_sq = Square(side_length=0.6, color=DARK_NAVY, stroke_width=2,
                            fill_color=LIGHT_GREY, fill_opacity=0.5)
        callout_sq.move_to(RIGHT*3 + UP*0.5)
        callout_lbl = poppins("1 unit square", 14, DARK_GREY)
        callout_lbl.next_to(callout_sq, DOWN, buff=0.15)
        caption6 = poppins("Area = count of unit squares that fit inside",
                           18, DARK_GREY)
        caption6.next_to(grid6, DOWN, buff=0.6)

        with self.voiceover(
            text='<bookmark mark="b1"/>You also know that we measure a surface '
                 'by <bookmark mark="b2"/>counting how many unit squares fit '
                 'inside it.'
        ) as t:
            self.wait_until_bookmark("b1")
            self.play(Create(grid6[0]), Create(grid6[1]), run_time=1.0)
            self.play(FadeIn(grid6[2]), run_time=0.6)
            self.wait_until_bookmark("b2")
            self.play(FadeIn(callout_sq), FadeIn(callout_lbl),
                      FadeIn(caption6), run_time=0.7)
        self.wait(0.5)
        clear_all()

        # ========================================================
        # ROW 7 — From counting to a shortcut
        # ========================================================
        t7 = title_text("From Counting to a Shortcut")
        left_g = grid_rect(5, 3, cell=0.45, numbers=True).move_to(LEFT*3.5)
        cap_l = poppins("Counting one by one", 16, DARK_GREY).next_to(left_g, DOWN, buff=0.3)
        x_l = cross_icon().scale(0.7).next_to(cap_l, RIGHT, buff=0.2)
        right_r = Rectangle(width=2.25, height=1.35, color=DARK_NAVY,
                            stroke_width=3, fill_color=WHITE, fill_opacity=1)
        right_r.move_to(RIGHT*3.5)
        bolt = poppins("⚡", 30, YELLOW_C, BOLD).move_to(right_r.get_center())
        cap_r = poppins("Powerful shortcut", 16, DARK_NAVY, BOLD).next_to(right_r, DOWN, buff=0.3)
        v_r = check_icon().scale(0.7).next_to(cap_r, RIGHT, buff=0.2)
        arr7 = Arrow(LEFT*1.4, RIGHT*1.4, color=DARK_GREY, stroke_width=3)
        arr7_lbl = poppins("Next step", 14, DARK_GREY).next_to(arr7, UP, buff=0.15)

        with self.voiceover(
            text='<bookmark mark="b1"/>These ideas form the foundation we need. '
                 'You already know that a rectangle is made of right angles '
                 'and equal opposite sides. <bookmark mark="b2"/>Now we will '
                 'use those properties to discover a powerful shortcut — '
                 '<bookmark mark="b3"/>so you never have to count squares '
                 'one by one again.'
        ) as t:
            self.play(FadeIn(t7), run_time=0.5)
            self.wait_until_bookmark("b1")
            self.play(FadeIn(left_g), FadeIn(cap_l), FadeIn(x_l), run_time=0.8)
            self.wait_until_bookmark("b2")
            self.play(Create(right_r), FadeIn(bolt),
                      FadeIn(cap_r), FadeIn(v_r), run_time=0.8)
            self.wait_until_bookmark("b3")
            self.play(Create(arr7), FadeIn(arr7_lbl), run_time=0.6)
        self.wait(0.4)
        clear_all()

        # ========================================================
        # ROW 8 — Self check thought bubble
        # ========================================================
        bubble = Ellipse(width=4.5, height=2.2, color=DARK_GREY, stroke_width=2)
        bubble.shift(UP*1.5)
        mini_r = Rectangle(width=1.2, height=0.8, color=DARK_NAVY, stroke_width=2)
        mini_grid = grid_rect(4, 3, cell=0.2).move_to(bubble.get_center())
        head = Circle(radius=0.25, color=DARK_GREY, stroke_width=2,
                      fill_color=LIGHT_GREY, fill_opacity=1).shift(DOWN*0.5)
        shoulders = Arc(radius=0.5, angle=PI,
                        start_angle=PI, color=DARK_GREY, stroke_width=2)
        shoulders.next_to(head, DOWN, buff=-0.1)
        tail_dots = VGroup(*[Dot(point=bubble.get_bottom()+DOWN*i*0.15,
                                 radius=0.05, color=DARK_GREY) for i in range(1,4)])
        question8 = poppins("Can you picture a rectangle and count the unit\n"
                            "squares inside it?", 18, DARK_GREY, italic=NORMAL)
        question8 = poppins("Can you picture a rectangle and count squares inside?",
                            18, DARK_GREY).next_to(head, DOWN, buff=0.7)
        banner8_bg = RoundedRectangle(width=4.5, height=0.7,
                                      corner_radius=0.15,
                                      fill_color=DARK_GREEN, fill_opacity=1,
                                      stroke_width=0)
        banner8_txt = poppins("If yes — you are prepared!", 16, WHITE, BOLD)
        banner8 = VGroup(banner8_bg, banner8_txt).next_to(question8, DOWN, buff=0.4)

        with self.voiceover(
            text='<bookmark mark="b1"/>Take a moment to ask yourself: '
                 '<bookmark mark="b2"/>can you picture a rectangle and count '
                 'the unit squares inside it? <bookmark mark="b3"/>If you can, '
                 'you are fully prepared for what comes next.'
        ) as t:
            self.wait_until_bookmark("b1")
            self.play(Create(bubble), FadeIn(mini_grid),
                      FadeIn(head), Create(shoulders),
                      FadeIn(tail_dots), run_time=1.0)
            self.wait_until_bookmark("b2")
            self.play(FadeIn(question8), run_time=0.7)
            self.wait_until_bookmark("b3")
            self.play(FadeIn(banner8), run_time=0.7)
        self.wait(0.4)
        clear_all()

        # ========================================================
        # ROW 9 — Rangoli
        # ========================================================
        self.camera.background_color = SOFT_GREEN
        t9 = title_text("Real-World Connection")
        grid9 = grid_rect(6, 4, cell=0.55).move_to(ORIGIN)
        colors9 = [PINK, PALE_YELLOW, ORANGE_FILL, LAV, PALE_BLUE, LIGHT_GREEN]
        positions9 = [(0,1),(1,3),(2,0),(2,4),(3,2),(3,5)]
        filled9 = fill_cells(6, 4, 0.55,
                             [(r,c,colors9[i]) for i,(r,c) in enumerate(positions9)],
                             base_pos=ORIGIN)
        hand9 = poppins("✋", 30, DARK_GREY).next_to(grid9, LEFT, buff=0.5)
        cap9 = poppins("Rangoli artists count unit squares to know how much powder they need.",
                       16, DARK_GREY).next_to(grid9, DOWN, buff=0.5)

        with self.voiceover(
            text='<bookmark mark="b1"/>Consider rangoli artists filling '
                 'rectangular regions with coloured powder. '
                 '<bookmark mark="b2"/>To know how much powder they need, '
                 'they count unit squares.'
        ) as t:
            self.play(FadeIn(t9), run_time=0.5)
            self.wait_until_bookmark("b1")
            self.play(Create(grid9), FadeIn(hand9), run_time=1.0)
            self.play(FadeIn(filled9), run_time=0.7)
            self.wait_until_bookmark("b2")
            self.play(FadeIn(cap9), run_time=0.6)
        self.wait(0.5)
        clear_all()
        self.camera.background_color = WHITE

        # ========================================================
        # ROW 10 — 7x4 grid intro
        # ========================================================
        cell10 = 0.5
        grid10 = grid_rect(4, 7, cell=cell10).move_to(LEFT*0.5)
        lbl_7 = poppins("7 cm", 18, DARK_GREY).next_to(grid10, LEFT, buff=0.2)
        lbl_4 = poppins("4 cm", 18, DARK_GREY).next_to(grid10, UP, buff=0.2)
        # highlight top row
        top_row_sqs = fill_cells(4, 7, cell10,
                                 [(0,c,PALE_BLUE) for c in range(4)],
                                 base_pos=grid10.get_center())
        br_label = poppins("Row 1 : 4 squares", 14, DARK_GREY)
        br_label.next_to(grid10, RIGHT, buff=0.3).align_to(grid10.get_top(), UP)
        rows_info = VGroup(
            poppins("Row 2 : 4 squares", 13, DARK_GREY),
            poppins("⋮", 16, DARK_GREY),
            poppins("Row 7 : 4 squares", 13, DARK_GREY),
        ).arrange(DOWN, buff=0.25).next_to(br_label, DOWN, buff=0.2, aligned_edge=LEFT)
        q10 = poppins("What is the relationship between the rows and the total count?",
                      16, DARK_GREY).next_to(grid10, DOWN, buff=0.5)

        with self.voiceover(
            text='<bookmark mark="b1"/>Look at a rectangle seven centimetres '
                 'by four centimetres. <bookmark mark="b2"/>You see seven '
                 'rows, and each row has four squares. <bookmark mark="b3"/>'
                 'What do you notice about the relationship between the '
                 'number of rows and the total count?'
        ) as t:
            self.wait_until_bookmark("b1")
            self.play(Create(grid10), FadeIn(lbl_7), FadeIn(lbl_4), run_time=1.0)
            self.wait_until_bookmark("b2")
            self.play(FadeIn(top_row_sqs), FadeIn(br_label), run_time=0.7)
            self.play(FadeIn(rows_info), run_time=0.7)
            self.wait_until_bookmark("b3")
            self.play(FadeIn(q10), run_time=0.6)
        self.wait(0.4)
        # Don't clear yet — Row 11 builds on this
        # but we need to also keep refs. Let's just clear for simplicity:
        clear_all()

        # ========================================================
        # ROW 11 — 7 × 4 = 28
        # ========================================================
        grid11 = grid_rect(4, 7, cell=cell10).move_to(LEFT*1.5)
        all_filled = fill_cells(4, 7, cell10,
                                [(r,c,PALE_BLUE) for r in range(7) for c in range(4)],
                                base_pos=grid11.get_center())
        # numbers 1-28
        nums11 = VGroup()
        n = 1
        for r in range(7):
            for c in range(4):
                cx = grid11.get_center()[0] - (4*cell10)/2 + (c+0.5)*cell10
                cy = grid11.get_center()[1] + (7*cell10)/2 - (r+0.5)*cell10
                nums11.add(poppins(str(n), 10, DARK_GREY).move_to([cx,cy,0]))
                n += 1
        lbl_7b = poppins("7 cm", 18, DARK_GREY).next_to(grid11, LEFT, buff=0.2)
        lbl_4b = poppins("4 cm", 18, DARK_GREY).next_to(grid11, UP, buff=0.2)
        eq11 = MathTex("7", r"\times", "4", "=", "28",
                       color=DARK_NAVY, font_size=42)
        eq11[1].set_color(BURNT_ORANGE)
        eq11.next_to(grid11, RIGHT, buff=1.2)
        cap11 = poppins("This is the heart of the formula.",
                        18, DARK_GREY).next_to(grid11, DOWN, buff=0.6)
        heart_word = poppins("heart of the formula", 18, DARK_NAVY, BOLD)

        with self.voiceover(
            text='<bookmark mark="b1"/>Seven times four <bookmark mark="b2"/>'
                 'gives twenty-eight. <bookmark mark="b3"/>This is the heart '
                 'of the formula.'
        ) as t:
            self.play(Create(grid11), FadeIn(lbl_7b), FadeIn(lbl_4b),
                      run_time=0.8)
            self.play(FadeIn(all_filled), FadeIn(nums11), run_time=0.8)
            self.wait_until_bookmark("b1")
            self.play(FadeIn(eq11[0]), FadeIn(eq11[1]), FadeIn(eq11[2]), run_time=0.6)
            self.wait_until_bookmark("b2")
            self.play(FadeIn(eq11[3]), FadeIn(eq11[4]), run_time=0.6)
            self.wait_until_bookmark("b3")
            self.play(FadeIn(cap11), run_time=0.6)
        self.wait(0.4)
        clear_all()

        # ========================================================
        # ROW 12 — Formula card
        # ========================================================
        formula12 = MathTex(r"\text{Area of Rectangle} = \text{Length} ",
                            r"\times", r" \text{Breadth}",
                            color=DARK_NAVY, font_size=36)
        formula12[1].set_color(BURNT_ORANGE)
        card12 = make_card(formula12, fill=VERY_PALE_BLUE, border=DARK_NAVY,
                           border_width=2, pad=0.4, radius=0.2)
        card12.move_to(ORIGIN)
        mini12 = grid_rect(4, 7, cell=0.2).scale(0.8).next_to(card12, UP, buff=0.5)
        arr12 = Arrow(mini12.get_bottom(), card12.get_top(),
                      color=DARK_GREY, stroke_width=2, buff=0.1)
        cap12 = poppins("This is the general rule for all rectangles.",
                        16, DARK_GREY).next_to(card12, DOWN, buff=0.4)

        with self.voiceover(
            text='<bookmark mark="b1"/>The area of a rectangle '
                 '<bookmark mark="b2"/>equals length multiplied by breadth.'
        ) as t:
            self.play(FadeIn(mini12), Create(arr12), run_time=0.7)
            self.wait_until_bookmark("b1")
            self.play(FadeIn(card12), run_time=0.8)
            self.wait_until_bookmark("b2")
            self.play(FadeIn(cap12), run_time=0.6)
        self.wait(0.4)
        clear_all()

        # ========================================================
        # ROW 13 — Works for every rectangle
        # ========================================================
        t13 = title_text("Works for Every Rectangle")
        formula13 = MathTex(r"\text{Area} = \text{Length} \times \text{Breadth}",
                            color=DARK_NAVY, font_size=28).next_to(t13, DOWN, buff=0.4)
        rA = Rectangle(width=3.2, height=0.8, color=DARK_NAVY, stroke_width=3)
        rB = Rectangle(width=2.0, height=1.6, color=DARK_NAVY, stroke_width=3)
        rC = Rectangle(width=1.4, height=1.4, color=DARK_NAVY, stroke_width=3)
        for r in (rA, rB, rC):
            lb = MathTex(r"L \times B", color=DARK_GREY, font_size=22).move_to(r.get_center())
            r.add(lb)
        row13 = VGroup(rA, rB, rC).arrange(RIGHT, buff=1.0).move_to(ORIGIN)
        names = ["Long and thin", "Short and wide", "Square"]
        labels13 = VGroup()
        ticks13 = VGroup()
        for r, name in zip(row13, names):
            lbl = poppins(name, 14, DARK_GREY).next_to(r, DOWN, buff=0.3)
            tk = check_icon().scale(0.5).next_to(r, UP, buff=0.2)
            labels13.add(lbl)
            ticks13.add(tk)

        with self.voiceover(
            text='<bookmark mark="b1"/>This works for every rectangle — '
                 '<bookmark mark="b2"/>whether it is long and thin, '
                 '<bookmark mark="b3"/>short and wide, '
                 '<bookmark mark="b4"/>or a square.'
        ) as t:
            self.play(FadeIn(t13), FadeIn(formula13), run_time=0.6)
            self.wait_until_bookmark("b1")
            self.play(Create(rA), FadeIn(labels13[0]), FadeIn(ticks13[0]), run_time=0.6)
            self.wait_until_bookmark("b2")
            self.play(Create(rB), FadeIn(labels13[1]), FadeIn(ticks13[1]), run_time=0.6)
            self.wait_until_bookmark("b3")
            # already covered above; small wait
            self.wait(0.2)
            self.wait_until_bookmark("b4")
            self.play(Create(rC), FadeIn(labels13[2]), FadeIn(ticks13[2]), run_time=0.6)
        self.wait(0.4)
        clear_all()

        # ========================================================
        # ROW 14 — Units notation
        # ========================================================
        grid14 = grid_rect(4, 7, cell=0.35).move_to(LEFT*3.5)
        all14 = fill_cells(4, 7, 0.35,
                           [(r,c,PALE_BLUE) for r in range(7) for c in range(4)],
                           base_pos=grid14.get_center())
        c1_14 = poppins("28 square centimetres", 18, DARK_GREY)
        c1_14 = make_card(c1_14, fill=WHITE, border=LIGHT_GREY,
                          border_width=1, pad=0.2, radius=0.1)
        c2_14 = poppins("28 centimetre squared", 18, DARK_GREY)
        c2_14 = make_card(c2_14, fill=WHITE, border=LIGHT_GREY,
                          border_width=1, pad=0.2, radius=0.1)
        c3_14_text = MathTex(r"28\,\text{cm}^2", color=DARK_NAVY, font_size=32)
        c3_14 = make_card(c3_14_text, fill=WHITE, border=DARK_NAVY,
                          border_width=2.5, pad=0.25, radius=0.12)
        cards14 = VGroup(c1_14, c2_14, c3_14).arrange(DOWN, buff=0.35)
        cards14.move_to(RIGHT*2.8)
        circle_sup = Circle(radius=0.18, color=RED_C, stroke_width=2)
        # try to position around the "2" superscript
        circle_sup.move_to(c3_14_text[0][-1].get_center())
        callout14 = poppins("means square units", 12, RED_C)
        callout14.next_to(circle_sup, RIGHT, buff=0.3)
        arrow14 = Arrow(grid14.get_right(), cards14[0].get_left(),
                        color=DARK_GREY, stroke_width=2, buff=0.2)
        arr_lbl = poppins("= unit squares that fill", 12, DARK_GREY).next_to(arrow14, UP, buff=0.1)

        with self.voiceover(
            text='<bookmark mark="b1"/>In other words, the area tells us how '
                 'many unit squares fill the space completely. '
                 '<bookmark mark="b2"/>We write this as twenty-eight square '
                 'centimetres, or <bookmark mark="b3"/>twenty-eight '
                 'centimetre squared. <bookmark mark="b4"/>On screen, we show '
                 'it as twenty-eight cm squared — <bookmark mark="b5"/>the '
                 'small two means square units.'
        ) as t:
            self.wait_until_bookmark("b1")
            self.play(Create(grid14), FadeIn(all14), run_time=0.8)
            self.play(Create(arrow14), FadeIn(arr_lbl), run_time=0.5)
            self.wait_until_bookmark("b2")
            self.play(FadeIn(c1_14), run_time=0.6)
            self.wait_until_bookmark("b3")
            self.play(FadeIn(c2_14), run_time=0.6)
            self.wait_until_bookmark("b4")
            self.play(FadeIn(c3_14), run_time=0.7)
            self.wait_until_bookmark("b5")
            self.play(Create(circle_sup), FadeIn(callout14), run_time=0.6)
        self.wait(0.4)
        clear_all()

        # ========================================================
        # ROW 15 — Square as special rectangle
        # ========================================================
        t15 = title_text("Square: A Special Rectangle")
        sq15 = Square(side_length=2.0, color=DARK_NAVY, stroke_width=3,
                      fill_color=VERY_PALE_BLUE, fill_opacity=1).move_to(ORIGIN)
        # corner markers
        cms = VGroup(*[Square(side_length=0.13, color=DARK_NAVY, stroke_width=2)
                       .move_to(sq15.get_corner(d) + np.array([-d[0]*0.065,-d[1]*0.065,0]))
                       for d in [UL,UR,DL,DR]])
        s_top = MathTex("s", color=DARK_GREY, font_size=26).next_to(sq15, UP, buff=0.15)
        s_right = MathTex("s", color=DARK_GREY, font_size=26).next_to(sq15, RIGHT, buff=0.15)
        eq_arrow = MathTex("=", color=DARK_NAVY, font_size=28).next_to(sq15, UR, buff=0.3)
        left_ann = poppins("Length = Breadth = s", 16, DARK_GREY).next_to(sq15, LEFT, buff=0.5)
        formula15 = MathTex(r"\text{Area of Square} = s \times s",
                            color=DARK_NAVY, font_size=28)
        formula15[0][-3].set_color(BURNT_ORANGE)  # the × in s × s (approx)
        card15 = make_card(formula15, fill=VERY_PALE_BLUE, border=DARK_NAVY,
                           border_width=2, pad=0.3, radius=0.15)
        card15.next_to(sq15, DOWN, buff=0.6)

        with self.voiceover(
            text='<bookmark mark="b1"/>A square is simply a rectangle whose '
                 'length and breadth are identical. <bookmark mark="b2"/>'
                 'So its area is side multiplied by side.'
        ) as t:
            self.play(FadeIn(t15), run_time=0.5)
            self.wait_until_bookmark("b1")
            self.play(Create(sq15), FadeIn(cms), FadeIn(s_top),
                      FadeIn(s_right), FadeIn(eq_arrow),
                      FadeIn(left_ann), run_time=1.0)
            self.wait_until_bookmark("b2")
            self.play(FadeIn(card15), run_time=0.7)
        self.wait(0.4)
        clear_all()

        # ========================================================
        # ROW 16 — Why multiplication works
        # ========================================================
        t16 = title_text("Why Multiplication Works")
        people = VGroup()
        for r in range(4):
            for c in range(5):
                d = Dot(radius=0.18, color=PALE_BLUE)
                d.set_stroke(DARK_GREY, width=1)
                d.move_to([-1.2 + c*0.45, 0.8 - r*0.45, 0])
                people.add(d)
        people.move_to(LEFT*2.5)
        br_top = Brace(people, UP)
        br_top_lbl = poppins("5 seats per row", 14, DARK_GREY).next_to(br_top, UP, buff=0.1)
        br_left = Brace(people, LEFT)
        br_left_lbl = poppins("4 rows", 14, DARK_GREY).next_to(br_left, LEFT, buff=0.1)
        eq16 = MathTex(r"4\;\text{rows} \times 5\;\text{seats} = 20\;\text{people}",
                       color=DARK_NAVY, font_size=28)
        eq16.next_to(people, DOWN, buff=0.7)
        equals16 = MathTex("=", color=DARK_NAVY, font_size=36).move_to(RIGHT*0.5)
        grid16 = grid_rect(5, 4, cell=0.4).move_to(RIGHT*2.5)
        fill16 = fill_cells(5, 4, 0.4,
                            [(r,c,PALE_BLUE) for r in range(4) for c in range(5)],
                            base_pos=grid16.get_center())
        cap16 = poppins("Same as unit squares!", 14, DARK_GREY).next_to(grid16, DOWN, buff=0.3)

        with self.voiceover(
            text='<bookmark mark="b1"/>But why does multiplication work? '
                 '<bookmark mark="b2"/>Think of area like a crowd seated in '
                 'rows. <bookmark mark="b3"/>If each row has a certain number '
                 'of seats, and you know how many rows there are, '
                 '<bookmark mark="b4"/>multiplication gives you the total '
                 'number of people.'
        ) as t:
            self.play(FadeIn(t16), run_time=0.5)
            self.wait_until_bookmark("b1")
            self.play(FadeIn(people), run_time=0.8)
            self.wait_until_bookmark("b2")
            self.play(FadeIn(br_top), FadeIn(br_top_lbl),
                      FadeIn(br_left), FadeIn(br_left_lbl), run_time=0.7)
            self.wait_until_bookmark("b3")
            self.play(FadeIn(eq16), run_time=0.6)
            self.wait_until_bookmark("b4")
            self.play(FadeIn(equals16), Create(grid16), FadeIn(fill16),
                      FadeIn(cap16), run_time=0.9)
        self.wait(0.4)
        clear_all()

        # ========================================================
        # ROW 17 — Add vs Multiply
        # ========================================================
        t17 = title_text("Add vs. Multiply")
        left_bg = Rectangle(width=6.0, height=4.5, color=PALE_RED,
                            fill_color=PALE_RED, fill_opacity=1, stroke_width=0)
        left_bg.move_to(LEFT*3.3 + DOWN*0.3)
        right_bg = Rectangle(width=6.0, height=4.5, color=SOFT_GREEN,
                             fill_color=SOFT_GREEN, fill_opacity=1, stroke_width=0)
        right_bg.move_to(RIGHT*3.3 + DOWN*0.3)
        eq17L = MathTex("4 + 5 = 9", color=DARK_GREY, font_size=32).move_to(left_bg.get_center()+UP*1.2)
        x17 = cross_icon().scale(0.8).next_to(eq17L, RIGHT, buff=0.3)
        rect17L = Rectangle(width=2.5, height=1.5, color=RED_C, stroke_width=5,
                            fill_opacity=0).move_to(left_bg.get_center()+DOWN*0.2)
        lblL = poppins("Perimeter (boundary)", 14, RED_C).next_to(rect17L, DOWN, buff=0.2)
        notArea = poppins("NOT the area", 14, RED_C, BOLD).next_to(lblL, DOWN, buff=0.15)
        eq17R = MathTex("4 \\times 5 = 20", color=DARK_GREY, font_size=32).move_to(right_bg.get_center()+UP*1.2)
        v17 = check_icon().scale(0.8).next_to(eq17R, RIGHT, buff=0.3)
        rect17R = Rectangle(width=2.5, height=1.5, color=DARK_NAVY, stroke_width=2,
                            fill_color=PALE_BLUE, fill_opacity=1).move_to(right_bg.get_center()+DOWN*0.2)
        lblR = poppins("Area (space inside)", 14, DARK_GREEN).next_to(rect17R, DOWN, buff=0.2)

        with self.voiceover(
            text='<bookmark mark="b1"/>You would never add the row count to '
                 'the seat count — <bookmark mark="b2"/>that would only tell '
                 'you the boundary.'
        ) as t:
            self.play(FadeIn(t17), run_time=0.5)
            self.wait_until_bookmark("b1")
            self.play(FadeIn(left_bg), FadeIn(eq17L), FadeIn(x17),
                      Create(rect17L), FadeIn(lblL), run_time=1.0)
            self.wait_until_bookmark("b2")
            self.play(FadeIn(notArea),
                      FadeIn(right_bg), FadeIn(eq17R), FadeIn(v17),
                      Create(rect17R), FadeIn(lblR), run_time=1.0)
        self.wait(0.4)
        clear_all()

        # ========================================================
        # ROW 18 — Does order matter
        # ========================================================
        t18 = title_text("Does Order Matter?")
        gA = grid_rect(4, 7, cell=0.3).move_to(LEFT*3)
        fA = fill_cells(4, 7, 0.3,
                        [(r,c,PALE_BLUE) for r in range(7) for c in range(4)],
                        base_pos=gA.get_center())
        gA_top = poppins("4 cm", 14, DARK_GREY).next_to(gA, UP, buff=0.15)
        gA_left = poppins("7 cm", 14, DARK_GREY).next_to(gA, LEFT, buff=0.15)
        eqA = MathTex(r"7 \times 4 = 28", color=DARK_NAVY, font_size=24)
        eqA.next_to(gA, DOWN, buff=0.3)
        vA = check_icon().scale(0.5).next_to(eqA, RIGHT, buff=0.2)
        eq_mid = MathTex("=", color=DARK_NAVY, font_size=42).move_to(ORIGIN)
        gB = grid_rect(7, 4, cell=0.3).move_to(RIGHT*3)
        fB = fill_cells(7, 4, 0.3,
                        [(r,c,PALE_BLUE) for r in range(4) for c in range(7)],
                        base_pos=gB.get_center())
        gB_top = poppins("7 cm", 14, DARK_GREY).next_to(gB, UP, buff=0.15)
        gB_left = poppins("4 cm", 14, DARK_GREY).next_to(gB, LEFT, buff=0.15)
        eqB = MathTex(r"4 \times 7 = 28", color=DARK_NAVY, font_size=24)
        eqB.next_to(gB, DOWN, buff=0.3)
        vB = check_icon().scale(0.5).next_to(eqB, RIGHT, buff=0.2)
        cap18 = poppins("Multiplication does not care about order.",
                        18, DARK_NAVY, BOLD).to_edge(DOWN, buff=0.6)

        with self.voiceover(
            text='<bookmark mark="b1"/>Here is a question many students ask: '
                 'does it matter which side I call length? '
                 '<bookmark mark="b2"/>Could I write breadth times length '
                 'instead? <bookmark mark="b3"/>Think about it — '
                 'multiplication does not care about order. '
                 '<bookmark mark="b4"/>Seven times four and four times seven '
                 'both give twenty-eight. <bookmark mark="b5"/>So the area '
                 'is the same either way.'
        ) as t:
            self.play(FadeIn(t18), run_time=0.5)
            self.wait_until_bookmark("b1")
            self.play(Create(gA), FadeIn(fA),
                      FadeIn(gA_top), FadeIn(gA_left), run_time=0.9)
            self.wait_until_bookmark("b2")
            self.play(Create(gB), FadeIn(fB),
                      FadeIn(gB_top), FadeIn(gB_left), run_time=0.9)
            self.wait_until_bookmark("b3")
            self.play(FadeIn(eq_mid), FadeIn(cap18), run_time=0.6)
            self.wait_until_bookmark("b4")
            self.play(FadeIn(eqA), FadeIn(vA),
                      FadeIn(eqB), FadeIn(vB), run_time=0.8)
            self.wait_until_bookmark("b5")
            self.wait(0.3)
        self.wait(0.4)
        clear_all()

        # ========================================================
        # ROW 19 — Same perimeter ≠ same area
        # ========================================================
        t19 = title_text("Same Perimeter \u2260 Same Area")
        rA19 = grid_rect(4, 1, cell=0.45).move_to(LEFT*3 + UP*0.5)
        fA19 = fill_cells(4, 1, 0.45,
                          [(0,c,PALE_RED) for c in range(4)],
                          base_pos=rA19.get_center())
        lblA_t = poppins("4", 14, DARK_GREY).next_to(rA19, UP, buff=0.1)
        lblA_l = poppins("1", 14, DARK_GREY).next_to(rA19, LEFT, buff=0.1)
        cardA = VGroup(
            poppins("P = 2(4+1) = 10", 14, DARK_GREY),
            poppins("A = 4 × 1 = 4", 14, DARK_GREY),
        ).arrange(DOWN, buff=0.15).next_to(rA19, DOWN, buff=0.4)
        rB19 = grid_rect(3, 2, cell=0.45).move_to(RIGHT*3 + UP*0.5)
        fB19 = fill_cells(3, 2, 0.45,
                          [(r,c,PALE_BLUE) for r in range(2) for c in range(3)],
                          base_pos=rB19.get_center())
        lblB_t = poppins("3", 14, DARK_GREY).next_to(rB19, UP, buff=0.1)
        lblB_l = poppins("2", 14, DARK_GREY).next_to(rB19, LEFT, buff=0.1)
        cardB = VGroup(
            poppins("P = 2(3+2) = 10", 14, DARK_GREY),
            poppins("A = 3 × 2 = 6", 14, DARK_GREY),
        ).arrange(DOWN, buff=0.15).next_to(rB19, DOWN, buff=0.4)
        equ = MathTex("=", color=DARK_NAVY, font_size=32).move_to(ORIGIN + UP*0.2)
        neq = MathTex(r"\neq", color=DARK_NAVY, font_size=32).move_to(ORIGIN + DOWN*0.6)
        x19 = cross_icon().scale(0.6).next_to(neq, DOWN, buff=0.1)

        with self.voiceover(
            text='<bookmark mark="b1"/>Now, if two rectangles have the same '
                 'perimeter, must they have the same area? '
                 '<bookmark mark="b2"/>When I first learned this, I kept '
                 'confusing area with perimeter. I thought a larger boundary '
                 'always meant a larger space inside. '
                 '<bookmark mark="b3"/>But observe: a four-by-one rectangle '
                 'has perimeter ten and area four. '
                 '<bookmark mark="b4"/>A three-by-two rectangle also has '
                 'perimeter ten, yet area six.'
        ) as t:
            self.play(FadeIn(t19), run_time=0.5)
            self.wait_until_bookmark("b1")
            self.wait(0.3)
            self.wait_until_bookmark("b2")
            self.wait(0.3)
            self.wait_until_bookmark("b3")
            self.play(Create(rA19), FadeIn(fA19),
                      FadeIn(lblA_t), FadeIn(lblA_l),
                      FadeIn(cardA), run_time=1.0)
            self.wait_until_bookmark("b4")
            self.play(Create(rB19), FadeIn(fB19),
                      FadeIn(lblB_t), FadeIn(lblB_l),
                      FadeIn(cardB),
                      FadeIn(equ), FadeIn(neq), FadeIn(x19), run_time=1.0)
        self.wait(0.4)
        clear_all()

        # ========================================================
        # ROW 20 — Boundary same, space changed
        # ========================================================
        rA20 = Rectangle(width=2.4, height=0.6, color=RED_C, stroke_width=4,
                         fill_opacity=0).move_to(LEFT*3)
        rB20 = Rectangle(width=1.8, height=1.2, color=RED_C, stroke_width=4,
                         fill_color=PALE_BLUE, fill_opacity=1).move_to(RIGHT*3)
        # hatching for A (sparse red lines)
        hatch = VGroup()
        for i in range(6):
            x = -3 -1.0 + i*0.4
            hatch.add(Line([x, -0.25, 0],[x+0.5,0.25,0],
                           color=RED_C, stroke_width=1))
        lblA20 = poppins("Area = 4", 14, RED_C, BOLD).next_to(rA20, DOWN, buff=0.2)
        lblB20 = poppins("Area = 6", 14, BLUE_C, BOLD).next_to(rB20, DOWN, buff=0.2)
        same = poppins("Same boundary", 14, RED_C).move_to(UP*1.5)
        arrL = Arrow(same.get_bottom(), rA20.get_top(), color=RED_C,
                     stroke_width=1.5, buff=0.1)
        arrR = Arrow(same.get_bottom(), rB20.get_top(), color=RED_C,
                     stroke_width=1.5, buff=0.1)
        concl = poppins("Perimeter cannot measure area.", 18, DARK_NAVY, BOLD)
        concl_card = make_card(concl, fill=PALE_YELLOW, border=DARK_NAVY,
                               border_width=2, pad=0.3, radius=0.15)
        concl_card.to_edge(DOWN, buff=0.5)

        with self.voiceover(
            text='<bookmark mark="b1"/>The boundary stayed the same, '
                 '<bookmark mark="b2"/>but the space inside changed. '
                 '<bookmark mark="b3"/>This is why perimeter cannot '
                 'measure area.'
        ) as t:
            self.wait_until_bookmark("b1")
            self.play(Create(rA20), Create(rB20),
                      FadeIn(same), Create(arrL), Create(arrR),
                      run_time=1.0)
            self.wait_until_bookmark("b2")
            self.play(FadeIn(hatch), FadeIn(lblA20), FadeIn(lblB20),
                      run_time=0.8)
            self.wait_until_bookmark("b3")
            self.play(FadeIn(concl_card), run_time=0.8)
        self.wait(0.4)
        clear_all()

        # ========================================================
        # ROW 21 — Problem statement
        # ========================================================
        badge21_bg = RoundedRectangle(width=1.4, height=0.4, corner_radius=0.05,
                                      fill_color=DARK_NAVY, fill_opacity=1,
                                      stroke_width=0)
        badge21_txt = poppins("PROBLEM", 12, WHITE, BOLD)
        badge21 = VGroup(badge21_bg, badge21_txt)
        line_p1 = poppins("A rectangular park measures ", 18, DARK_GREY)
        line_p2 = poppins("fourteen metres by twelve metres.", 18, DARK_GREEN, BOLD)
        l1 = VGroup(line_p1, line_p2).arrange(RIGHT, buff=0.1)
        line_p3 = poppins("A path of uniform width ", 18, DARK_GREY)
        line_p4 = poppins("two metres", 18, DARK_GREEN, BOLD)
        line_p5 = poppins(" is built around the park.", 18, DARK_GREY)
        l2 = VGroup(line_p3, line_p4, line_p5).arrange(RIGHT, buff=0.05)
        line_p6 = poppins("Find the area of the path.", 18, BLUE_C, BOLD)
        body21 = VGroup(l1, l2, line_p6).arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        card21 = make_card(body21, fill=VERY_PALE_BLUE, border=DARK_NAVY,
                           border_width=2, pad=0.4, radius=0.2)
        card21.move_to(ORIGIN)
        badge21.next_to(card21, UP, buff=-0.1).align_to(card21, LEFT).shift(RIGHT*0.3)
        # swatches
        sw1 = VGroup(Square(side_length=0.3, color=DARK_GREEN,
                            fill_color=DARK_GREEN, fill_opacity=1, stroke_width=0),
                     poppins("Given", 14, DARK_GREY))
        sw1.arrange(RIGHT, buff=0.15)
        sw2 = VGroup(Square(side_length=0.3, color=BLUE_C,
                            fill_color=BLUE_C, fill_opacity=1, stroke_width=0),
                     poppins("Asked", 14, DARK_GREY))
        sw2.arrange(RIGHT, buff=0.15)
        sw3 = VGroup(Square(side_length=0.3, color=RED_C,
                            fill_color=RED_C, fill_opacity=1, stroke_width=0),
                     poppins("Hidden ?", 14, DARK_GREY))
        sw3.arrange(RIGHT, buff=0.15)
        sws = VGroup(sw1, sw2, sw3).arrange(RIGHT, buff=0.6)
        sws.next_to(card21, DOWN, buff=0.5)

        with self.voiceover(
            text='<bookmark mark="b1"/>A rectangular park measures '
                 '<bookmark mark="b2"/>fourteen metres by twelve metres. '
                 '<bookmark mark="b3"/>A path of uniform width two metres is '
                 'built around the outside of the park. '
                 '<bookmark mark="b4"/>Find the area of the path.'
        ) as t:
            self.wait_until_bookmark("b1")
            self.play(FadeIn(card21), FadeIn(badge21), run_time=0.8)
            self.play(FadeIn(l1[0]), run_time=0.4)
            self.wait_until_bookmark("b2")
            self.play(FadeIn(l1[1]), run_time=0.5)
            self.wait_until_bookmark("b3")
            self.play(FadeIn(l2), run_time=0.7)
            self.wait_until_bookmark("b4")
            self.play(FadeIn(line_p6), FadeIn(sws), run_time=0.7)
        self.wait(0.4)
        clear_all()

        # ========================================================
        # ROW 22 — Park + path structure
        # ========================================================
        outer22 = Rectangle(width=5.6, height=4.0, color=BURNT_ORANGE,
                            stroke_width=3, fill_opacity=0)
        # dashed outline
        outer22 = DashedVMobject(outer22, num_dashes=40, dashed_ratio=0.6)
        inner22 = Rectangle(width=4.0, height=2.8, color=DARK_NAVY,
                            stroke_width=3, fill_color=LIGHT_GREEN, fill_opacity=1)
        # tan band: a frame
        frame22_outer = Rectangle(width=5.6, height=4.0,
                                  fill_color=TAN, fill_opacity=1, stroke_width=0)
        frame22_inner = Rectangle(width=4.0, height=2.8,
                                  fill_color=WHITE, fill_opacity=1, stroke_width=0)
        frame22 = Difference(frame22_outer, frame22_inner,
                             fill_color=TAN, fill_opacity=1, stroke_width=0)
        grp22 = VGroup(frame22, inner22, outer22).move_to(ORIGIN)
        arr_park = Arrow(RIGHT*3, inner22.get_right(), color=DARK_GREEN,
                         stroke_width=2, buff=0.1)
        lbl_park = poppins("Park (inside)", 14, DARK_GREEN).next_to(arr_park, RIGHT, buff=0.1)
        arr_path = Arrow(LEFT*4, frame22.get_left()+UP*1.5, color=DARK_GREY,
                         stroke_width=2, buff=0.1)
        lbl_path = poppins("Path (surrounding)", 14, DARK_GREY).next_to(arr_path, LEFT, buff=0.1)
        cap22 = poppins("Before I calculate, I want to understand the structure.",
                        16, DARK_GREY).to_edge(DOWN, buff=0.5)

        with self.voiceover(
            text='<bookmark mark="b1"/>Before I calculate, I want to '
                 'understand. <bookmark mark="b2"/>We have a park inside, '
                 '<bookmark mark="b3"/>and a path surrounding it.'
        ) as t:
            self.wait_until_bookmark("b1")
            self.play(FadeIn(cap22), run_time=0.5)
            self.play(FadeIn(frame22), Create(outer22), run_time=1.0)
            self.wait_until_bookmark("b2")
            self.play(Create(inner22), Create(arr_park), FadeIn(lbl_park),
                      run_time=0.8)
            self.wait_until_bookmark("b3")
            self.play(Create(arr_path), FadeIn(lbl_path), run_time=0.7)
        self.wait(0.4)
        # We'll reuse some pieces — but clear for clarity
        clear_all()

        # ========================================================
        # ROW 23 — What do we know
        # ========================================================
        t23 = title_text("What Do We Know?", color=DARK_GREEN)
        # rebuild diagram
        frame_outer = Rectangle(width=5.6, height=4.0,
                                fill_color=TAN, fill_opacity=1, stroke_width=0)
        frame_inner = Rectangle(width=4.0, height=2.8,
                                fill_color=WHITE, fill_opacity=1, stroke_width=0)
        frame23 = Difference(frame_outer, frame_inner,
                             fill_color=TAN, fill_opacity=1, stroke_width=0)
        inner23 = Rectangle(width=4.0, height=2.8, color=DARK_NAVY,
                            stroke_width=3, fill_color=LIGHT_GREEN, fill_opacity=1)
        outer23 = DashedVMobject(Rectangle(width=5.6, height=4.0,
                                            color=BURNT_ORANGE, stroke_width=3,
                                            fill_opacity=0),
                                  num_dashes=40, dashed_ratio=0.6)
        diag23 = VGroup(frame23, inner23, outer23).move_to(ORIGIN+DOWN*0.3)
        lbl14_23 = poppins("14 m", 16, DARK_GREEN, BOLD).next_to(inner23, UP, buff=0.1)
        lbl12_23 = poppins("12 m", 16, DARK_GREEN, BOLD).next_to(inner23, RIGHT, buff=0.1)
        # 4 green arrows showing 2m width on each side
        def make_2m_arrow(direction, side):
            if side == "left":
                start = outer23.get_left() + UP*1.0
                end = inner23.get_left() + UP*1.0
            elif side == "right":
                start = outer23.get_right() + DOWN*1.0
                end = inner23.get_right() + DOWN*1.0
            elif side == "top":
                start = outer23.get_top() + LEFT*1.0
                end = inner23.get_top() + LEFT*1.0
            else:  # bottom
                start = outer23.get_bottom() + RIGHT*1.0
                end = inner23.get_bottom() + RIGHT*1.0
            return Arrow(start, end, color=DARK_GREEN, stroke_width=1.5,
                         buff=0.05, max_tip_length_to_length_ratio=0.4)
        arr_L = make_2m_arrow(None, "left")
        arr_R = make_2m_arrow(None, "right")
        arr_T = make_2m_arrow(None, "top")
        arr_B = make_2m_arrow(None, "bottom")
        arrs23 = VGroup(arr_L, arr_R, arr_T, arr_B)
        lbl_2m_L = poppins("2 m", 12, DARK_GREEN, BOLD).next_to(arr_L, UP, buff=0.05)
        lbl_2m_R = poppins("2 m", 12, DARK_GREEN, BOLD).next_to(arr_R, DOWN, buff=0.05)
        lbl_2m_T = poppins("2 m", 12, DARK_GREEN, BOLD).next_to(arr_T, LEFT, buff=0.05)
        lbl_2m_B = poppins("2 m", 12, DARK_GREEN, BOLD).next_to(arr_B, RIGHT, buff=0.05)
        lbls2m = VGroup(lbl_2m_L, lbl_2m_R, lbl_2m_T, lbl_2m_B)
        card23 = make_card(poppins("Given: Park = 14 m × 12 m, Path width = 2 m",
                                   14, DARK_GREEN),
                           fill=WHITE, border=DARK_GREEN, border_width=2,
                           pad=0.25, radius=0.12)
        card23.to_edge(DOWN, buff=0.4)

        with self.voiceover(
            text='<bookmark mark="b1"/>What do we know? '
                 '<bookmark mark="b2"/>The inner park is fourteen by '
                 'twelve metres. <bookmark mark="b3"/>The path width is '
                 'two metres.'
        ) as t:
            self.play(FadeIn(t23), FadeIn(frame23), FadeIn(outer23),
                      Create(inner23), run_time=1.0)
            self.wait_until_bookmark("b1")
            self.wait(0.2)
            self.wait_until_bookmark("b2")
            self.play(FadeIn(lbl14_23), FadeIn(lbl12_23), run_time=0.6)
            self.wait_until_bookmark("b3")
            self.play(FadeIn(arrs23), FadeIn(lbls2m),
                      FadeIn(card23), run_time=0.9)
        self.wait(0.4)
        clear_all()

        # ========================================================
        # ROW 24 — What is hidden
        # ========================================================
        t24 = title_text("What Is Hidden?", color=RED_C)
        frame24 = Difference(
            Rectangle(width=5.6, height=4.0, fill_color=TAN, fill_opacity=1, stroke_width=0),
            Rectangle(width=4.0, height=2.8, fill_color=WHITE, fill_opacity=1, stroke_width=0),
            fill_color=TAN, fill_opacity=1, stroke_width=0)
        inner24 = Rectangle(width=4.0, height=2.8, color=DARK_NAVY,
                            stroke_width=3, fill_color=LIGHT_GREEN, fill_opacity=1)
        outer24 = DashedVMobject(Rectangle(width=5.6, height=4.0,
                                            color=BURNT_ORANGE, stroke_width=3,
                                            fill_opacity=0),
                                  num_dashes=40, dashed_ratio=0.6)
        diag24 = VGroup(frame24, inner24, outer24).move_to(ORIGIN+DOWN*0.2)
        # red outward arrows
        def red_arrow(side):
            if side == "left":
                start = inner24.get_left() + UP*1.0
                end = outer24.get_left() + UP*1.0
            elif side == "right":
                start = inner24.get_right() + DOWN*1.0
                end = outer24.get_right() + DOWN*1.0
            elif side == "top":
                start = inner24.get_top() + LEFT*1.0
                end = outer24.get_top() + LEFT*1.0
            else:
                start = inner24.get_bottom() + RIGHT*1.0
                end = outer24.get_bottom() + RIGHT*1.0
            return Arrow(start, end, color=RED_C, stroke_width=2,
                         buff=0.05, max_tip_length_to_length_ratio=0.4)
        red_L = red_arrow("left"); red_R = red_arrow("right")
        red_T = red_arrow("top");  red_B = red_arrow("bottom")
        red_arrs = VGroup(red_L, red_R, red_T, red_B)
        each = poppins("EACH", 28, RED_C, BOLD).to_corner(UR, buff=0.7).shift(DOWN*1.0)
        each_under = Line(each.get_left()+DOWN*0.05, each.get_right()+DOWN*0.05,
                          color=RED_C, stroke_width=2)
        card24 = make_card(poppins("Hidden: Path adds 2 m to EACH side (left, right, top, bottom)",
                                   14, RED_C),
                           fill=WHITE, border=RED_C, border_width=2,
                           pad=0.25, radius=0.12)
        card24.to_edge(DOWN, buff=0.4)
        red2m_lbls = VGroup(
            poppins("2 m", 12, RED_C, BOLD).next_to(red_L, UP, buff=0.05),
            poppins("2 m", 12, RED_C, BOLD).next_to(red_R, DOWN, buff=0.05),
            poppins("2 m", 12, RED_C, BOLD).next_to(red_T, LEFT, buff=0.05),
            poppins("2 m", 12, RED_C, BOLD).next_to(red_B, RIGHT, buff=0.05),
        )

        with self.voiceover(
            text='<bookmark mark="b1"/>What is hidden? <bookmark mark="b2"/>'
                 'The path sits outside, so it adds two metres to '
                 '<bookmark mark="b3"/>EACH side of the park.'
        ) as t:
            self.play(FadeIn(t24), FadeIn(frame24), FadeIn(outer24),
                      Create(inner24), run_time=0.9)
            self.wait_until_bookmark("b1")
            self.wait(0.2)
            self.wait_until_bookmark("b2")
            self.play(FadeIn(red_arrs), FadeIn(red2m_lbls), run_time=0.8)
            self.wait_until_bookmark("b3")
            self.play(FadeIn(each), Create(each_under),
                      FadeIn(card24), run_time=0.8)
        self.wait(0.4)
        clear_all()

        # ========================================================
        # ROW 25 — Common mistake split
        # ========================================================
        t25 = title_text("Common Mistake")
        # Left: wrong asymmetric
        left_bg25 = Rectangle(width=6.2, height=4.0, color=PALE_RED,
                              fill_color=PALE_RED, fill_opacity=1, stroke_width=0)
        left_bg25.move_to(LEFT*3.3 + DOWN*0.5)
        wrong_inner = Rectangle(width=2.0, height=1.4, color=DARK_NAVY,
                                stroke_width=2, fill_color=LIGHT_GREEN, fill_opacity=1)
        wrong_path = Rectangle(width=2.5, height=1.9, color=BURNT_ORANGE,
                               stroke_width=2, fill_color=TAN, fill_opacity=1)
        wrong_inner.align_to(wrong_path, UP).align_to(wrong_path, LEFT)
        wrong_inner.shift(DOWN*0.05+RIGHT*0.05)
        wrong_grp = VGroup(wrong_path, wrong_inner).move_to(left_bg25.get_center()+UP*0.3)
        wrong_lbls = VGroup(
            poppins("14+2=16 m", 12, RED_C),
            poppins("12+2=14 m", 12, RED_C),
        ).arrange(DOWN, buff=0.1).next_to(wrong_grp, RIGHT, buff=0.2)
        x25 = cross_icon().scale(0.7).next_to(wrong_grp, UP, buff=0.1)
        wrong_cap = poppins("WRONG: Added 2 m only once",
                            14, RED_C, BOLD).next_to(left_bg25, DOWN, buff=-0.6).align_to(left_bg25.get_bottom(), DOWN).shift(UP*0.3)
        # Right correct
        right_bg25 = Rectangle(width=6.2, height=4.0, color=SOFT_GREEN,
                               fill_color=SOFT_GREEN, fill_opacity=1, stroke_width=0)
        right_bg25.move_to(RIGHT*3.3 + DOWN*0.5)
        correct_outer = Rectangle(width=2.8, height=2.2, color=BURNT_ORANGE,
                                  stroke_width=2, fill_color=TAN, fill_opacity=1)
        correct_inner = Rectangle(width=2.0, height=1.4, color=DARK_NAVY,
                                  stroke_width=2, fill_color=LIGHT_GREEN, fill_opacity=1)
        correct_inner.move_to(correct_outer.get_center())
        correct_grp = VGroup(correct_outer, correct_inner).move_to(right_bg25.get_center()+UP*0.3)
        correct_lbls = VGroup(
            poppins("14+2+2=18 m", 12, DARK_GREEN),
            poppins("12+2+2=16 m", 12, DARK_GREEN),
        ).arrange(DOWN, buff=0.1).next_to(correct_grp, RIGHT, buff=0.2)
        v25 = check_icon().scale(0.7).next_to(correct_grp, UP, buff=0.1)
        correct_cap = poppins("CORRECT: Added 2 m to EACH side",
                              14, DARK_GREEN, BOLD)
        correct_cap.next_to(right_bg25, DOWN, buff=-0.6).align_to(right_bg25.get_bottom(), DOWN).shift(UP*0.3)
        bottom_cap25 = poppins("Draw the diagram and label outer and inner separately.",
                               14, DARK_GREY).to_edge(DOWN, buff=0.2)

        with self.voiceover(
            text='<bookmark mark="b1"/>It seems logical to add two metres '
                 'only once. We hear "two metres around the park" and picture '
                 'adding two metres to the fence line. <bookmark mark="b2"/>'
                 'But width surrounds the park — it extends outward on both '
                 'sides. <bookmark mark="b3"/>When I first saw such a '
                 'problem, I only added two metres to one side, and my '
                 'answer was wrong. <bookmark mark="b4"/>What helped me was '
                 'drawing the diagram and labelling outer and inner '
                 'separately.'
        ) as t:
            self.play(FadeIn(t25), run_time=0.5)
            self.wait_until_bookmark("b1")
            self.play(FadeIn(left_bg25), Create(wrong_grp),
                      FadeIn(wrong_lbls), FadeIn(x25), FadeIn(wrong_cap),
                      run_time=1.2)
            self.wait_until_bookmark("b2")
            self.play(FadeIn(right_bg25), Create(correct_grp),
                      FadeIn(correct_lbls), FadeIn(v25), FadeIn(correct_cap),
                      run_time=1.2)
            self.wait_until_bookmark("b3")
            self.wait(0.3)
            self.wait_until_bookmark("b4")
            self.play(FadeIn(bottom_cap25), run_time=0.6)
        self.wait(0.4)
        clear_all()

        # ========================================================
        # ROW 26 — Composite figure equation
        # ========================================================
        t26 = title_text("Composite Figure Problem")
        # Diagram 1
        d1_outer = Rectangle(width=2.0, height=1.5, color=BURNT_ORANGE,
                             stroke_width=2, fill_color=TAN, fill_opacity=1)
        d1_inner = Rectangle(width=1.4, height=1.0, color=DARK_NAVY,
                             stroke_width=2, fill_color=LIGHT_GREEN, fill_opacity=1)
        d1_inner.move_to(d1_outer.get_center())
        d1 = VGroup(d1_outer, d1_inner)
        d1_lbl = poppins("Outer Rectangle", 12, BURNT_ORANGE).next_to(d1, DOWN, buff=0.2)
        minus = MathTex("-", color=DARK_NAVY, font_size=42)
        d2 = Rectangle(width=1.4, height=1.0, color=DARK_NAVY,
                       stroke_width=2, fill_color=LIGHT_GREEN, fill_opacity=1)
        d2_lbl = poppins("Inner Park", 12, DARK_GREEN).next_to(d2, DOWN, buff=0.2)
        eqs = MathTex("=", color=DARK_NAVY, font_size=42)
        d3_outer = Rectangle(width=2.0, height=1.5, color=BURNT_ORANGE,
                             stroke_width=2, fill_color=TAN, fill_opacity=1)
        d3_inner = Rectangle(width=1.4, height=1.0, color=DARK_NAVY,
                             stroke_width=2, fill_color=WHITE, fill_opacity=1)
        d3_inner.move_to(d3_outer.get_center())
        d3 = VGroup(d3_outer, d3_inner)
        d3_lbl = poppins("Path Area", 12, BLUE_C).next_to(d3, DOWN, buff=0.2)
        row26 = VGroup(d1, minus, d2, eqs, d3).arrange(RIGHT, buff=0.6)
        row26.move_to(ORIGIN)
        # re-position labels
        d1_lbl.next_to(d1, DOWN, buff=0.2)
        d2_lbl.next_to(d2, DOWN, buff=0.2)
        d3_lbl.next_to(d3, DOWN, buff=0.2)
        cap26 = poppins("Path = Outer Area − Inner Area",
                        18, DARK_NAVY, BOLD).next_to(row26, DOWN, buff=1.0)

        with self.voiceover(
            text='<bookmark mark="b1"/>What type of problem is this? '
                 '<bookmark mark="b2"/>It is a composite figure problem. '
                 '<bookmark mark="b3"/>The total shape is a larger rectangle. '
                 '<bookmark mark="b4"/>The path is the difference between '
                 'the outer rectangle and the inner park.'
        ) as t:
            self.play(FadeIn(t26), run_time=0.5)
            self.wait_until_bookmark("b1")
            self.wait(0.2)
            self.wait_until_bookmark("b2")
            self.play(Create(d1), FadeIn(d1_lbl), run_time=0.7)
            self.wait_until_bookmark("b3")
            self.play(FadeIn(minus), Create(d2), FadeIn(d2_lbl), run_time=0.7)
            self.wait_until_bookmark("b4")
            self.play(FadeIn(eqs), Create(d3), FadeIn(d3_lbl),
                      FadeIn(cap26), run_time=0.9)
        self.wait(0.4)
        clear_all()

        # ========================================================
        # ROW 27 — Which concept applies
        # ========================================================
        t27 = title_text("Which Concept Applies?")
        mini26 = VGroup(
            Rectangle(width=1.2, height=0.9, color=BURNT_ORANGE, stroke_width=2,
                      fill_color=TAN, fill_opacity=1),
            MathTex("-", color=DARK_NAVY, font_size=28),
            Rectangle(width=1.0, height=0.7, color=DARK_NAVY, stroke_width=2,
                      fill_color=LIGHT_GREEN, fill_opacity=1),
            MathTex("=", color=DARK_NAVY, font_size=28),
            Rectangle(width=1.2, height=0.9, color=BURNT_ORANGE, stroke_width=2,
                      fill_color=TAN, fill_opacity=1),
        ).arrange(RIGHT, buff=0.3).move_to(UP*1.5)
        strategy_card = make_card(
            poppins("Strategy: Find two rectangle areas, then subtract.",
                    16, DARK_NAVY, BOLD),
            fill=VERY_PALE_BLUE, border=DARK_NAVY,
            border_width=2, pad=0.25, radius=0.15)
        strategy_card.move_to(ORIGIN)
        formula27 = MathTex(r"\text{Area} = \text{Length} \times \text{Breadth}",
                            color=DARK_NAVY, font_size=24)
        formula27.next_to(strategy_card, DOWN, buff=0.6)
        arr_l = Arrow(formula27.get_top(), mini26[0].get_bottom(),
                      color=DARK_GREY, stroke_width=1.5, buff=0.2)
        arr_r = Arrow(formula27.get_top(), mini26[2].get_bottom(),
                      color=DARK_GREY, stroke_width=1.5, buff=0.2)

        with self.voiceover(
            text='<bookmark mark="b1"/>Which concept applies? '
                 '<bookmark mark="b2"/>The area of a rectangle. '
                 '<bookmark mark="b3"/>We will find two areas and subtract.'
        ) as t:
            self.play(FadeIn(t27), run_time=0.5)
            self.wait_until_bookmark("b1")
            self.play(FadeIn(mini26), run_time=0.7)
            self.wait_until_bookmark("b2")
            self.play(FadeIn(formula27), Create(arr_l), Create(arr_r),
                      run_time=0.8)
            self.wait_until_bookmark("b3")
            self.play(FadeIn(strategy_card), run_time=0.7)
        self.wait(0.4)
        clear_all()

        # ========================================================
        # ROW 28 — Two methods
        # ========================================================
        # Left panel
        lt28 = poppins("Method 1: Outer − Inner", 16, DARK_NAVY, BOLD).move_to(LEFT*3.5 + UP*2.8)
        mini28L = VGroup(
            Rectangle(width=0.9, height=0.7, color=BURNT_ORANGE, stroke_width=2,
                      fill_color=TAN, fill_opacity=1),
            MathTex("-", font_size=22, color=DARK_NAVY),
            Rectangle(width=0.7, height=0.5, color=DARK_NAVY, stroke_width=2,
                      fill_color=LIGHT_GREEN, fill_opacity=1),
            MathTex("=", font_size=22, color=DARK_NAVY),
            Rectangle(width=0.9, height=0.7, color=BURNT_ORANGE, stroke_width=2,
                      fill_color=TAN, fill_opacity=1),
        ).arrange(RIGHT, buff=0.15).next_to(lt28, DOWN, buff=0.5)
        banner28L_bg = RoundedRectangle(width=4.5, height=0.5, corner_radius=0.1,
                                        fill_color=DARK_GREEN, fill_opacity=1,
                                        stroke_width=0)
        banner28L_txt = poppins("We will use this (faster)", 12, WHITE, BOLD)
        banner28L = VGroup(banner28L_bg, banner28L_txt).next_to(mini28L, DOWN, buff=0.5)
        # Right panel: 4 strips
        rt28 = poppins("Method 2: Four Strips", 16, DARK_NAVY, BOLD).move_to(RIGHT*3.5 + UP*2.8)
        strip_outer = Rectangle(width=3.2, height=2.2, color=BURNT_ORANGE,
                                stroke_width=2, fill_opacity=0)
        # top strip pink
        top_strip = Rectangle(width=3.2, height=0.4, color=DARK_NAVY,
                              stroke_width=1, fill_color=PINK, fill_opacity=1)
        top_strip.align_to(strip_outer, UP)
        bot_strip = Rectangle(width=3.2, height=0.4, color=DARK_NAVY,
                              stroke_width=1, fill_color=PINK, fill_opacity=1)
        bot_strip.align_to(strip_outer, DOWN)
        left_strip = Rectangle(width=0.4, height=1.4, color=DARK_NAVY,
                               stroke_width=1, fill_color=PALE_YELLOW, fill_opacity=1)
        left_strip.align_to(strip_outer, LEFT)
        right_strip = Rectangle(width=0.4, height=1.4, color=DARK_NAVY,
                                stroke_width=1, fill_color=PALE_YELLOW, fill_opacity=1)
        right_strip.align_to(strip_outer, RIGHT)
        inner_blank = Rectangle(width=2.4, height=1.4, color=DARK_NAVY,
                                stroke_width=1, fill_color=WHITE, fill_opacity=1)
        strip_diag = VGroup(strip_outer, top_strip, bot_strip,
                            left_strip, right_strip, inner_blank).move_to(RIGHT*3.5+DOWN*0.2)
        # adjust positions inside strip_diag
        strip_diag.arrange(ORIGIN)  # no-op; layout was set via align_to before move
        # re-do positioning relative to outer
        strip_outer.move_to(RIGHT*3.5+DOWN*0.2)
        top_strip.next_to(strip_outer.get_top(), DOWN, buff=0).shift(UP*0.2)
        bot_strip.next_to(strip_outer.get_bottom(), UP, buff=0).shift(DOWN*0.2)
        left_strip.next_to(strip_outer.get_left(), RIGHT, buff=0).shift(LEFT*0.2)
        right_strip.next_to(strip_outer.get_right(), LEFT, buff=0).shift(RIGHT*0.2)
        inner_blank.move_to(strip_outer.get_center())
        strip_lbls = VGroup(
            poppins("18 m × 2 m", 9, DARK_GREY).move_to(top_strip.get_center()),
            poppins("18 m × 2 m", 9, DARK_GREY).move_to(bot_strip.get_center()),
            poppins("12×2", 8, DARK_GREY).move_to(left_strip.get_center()),
            poppins("12×2", 8, DARK_GREY).move_to(right_strip.get_center()),
        )
        banner28R_bg = RoundedRectangle(width=4.5, height=0.5, corner_radius=0.1,
                                        fill_color=LIGHT_GREY, fill_opacity=1,
                                        stroke_width=0)
        banner28R_txt = poppins("Also valid — proves the answer",
                                12, DARK_GREY, BOLD)
        banner28R = VGroup(banner28R_bg, banner28R_txt).next_to(strip_outer, DOWN, buff=0.4)
        both_cap = poppins("Both methods give the same answer.",
                           16, DARK_NAVY, BOLD).to_edge(DOWN, buff=0.3)

        with self.voiceover(
            text='<bookmark mark="b1"/>Another valid way — the one your '
                 'textbook also shows — is to split the path into four '
                 'separate strips. <bookmark mark="b2"/>The top and bottom '
                 'strips are each eighteen metres long and two metres wide. '
                 '<bookmark mark="b3"/>The left and right strips are each '
                 'twelve metres long and two metres wide. '
                 '<bookmark mark="b4"/>You could add those four areas '
                 'together. Both paths lead to the same answer. '
                 '<bookmark mark="b5"/>For now, we will use the outer-minus-'
                 'inner method because it is faster. '
                 '<bookmark mark="b6"/>But keep the four-strip picture in '
                 'your mind — it proves the answer is correct.'
        ) as t:
            self.play(FadeIn(lt28), FadeIn(rt28), run_time=0.5)
            self.wait_until_bookmark("b1")
            self.play(Create(strip_outer), run_time=0.7)
            self.play(FadeIn(top_strip), FadeIn(strip_lbls[0]),
                      FadeIn(bot_strip), FadeIn(strip_lbls[1]),
                      run_time=0.7)
            self.wait_until_bookmark("b2")
            self.wait(0.2)
            self.wait_until_bookmark("b3")
            self.play(FadeIn(left_strip), FadeIn(strip_lbls[2]),
                      FadeIn(right_strip), FadeIn(strip_lbls[3]),
                      FadeIn(inner_blank), run_time=0.8)
            self.wait_until_bookmark("b4")
            self.play(FadeIn(both_cap), run_time=0.6)
            self.wait_until_bookmark("b5")
            self.play(FadeIn(mini28L), FadeIn(banner28L), run_time=0.7)
            self.wait_until_bookmark("b6")
            self.play(FadeIn(banner28R), run_time=0.5)
        self.wait(0.4)
        clear_all()

        # ========================================================
        # ROW 29 — Plan
        # ========================================================
        header29 = VGroup(
            poppins("📋", 24, DARK_NAVY),
            poppins("PLAN", 22, DARK_NAVY, BOLD),
        ).arrange(RIGHT, buff=0.2)
        def plan_step(num, text_str):
            n = Circle(radius=0.18, color=DARK_NAVY, stroke_width=0,
                       fill_color=DARK_NAVY, fill_opacity=1)
            nt = poppins(str(num), 14, WHITE, BOLD).move_to(n.get_center())
            body = poppins(text_str, 14, DARK_GREY)
            box = Square(side_length=0.25, color=DARK_GREY, stroke_width=1)
            row = VGroup(VGroup(n, nt), body, box).arrange(RIGHT, buff=0.3)
            return row
        s1 = plan_step(1, "Find the outer dimensions")
        s2 = plan_step(2, "Find the outer area")
        s3 = plan_step(3, "Find the inner area")
        s4 = plan_step(4, "Subtract to get the path area")
        steps = VGroup(s1, s2, s3, s4).arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        all29 = VGroup(header29, steps).arrange(DOWN, buff=0.4)
        card29 = make_card(all29, fill=WHITE, border=DARK_NAVY,
                           border_width=2, pad=0.4, radius=0.2).move_to(ORIGIN)

        with self.voiceover(
            text='<bookmark mark="b1"/>Let us plan before calculating. '
                 '<bookmark mark="b2"/>Step one: find the outer dimensions. '
                 '<bookmark mark="b3"/>Step two: find the outer area. '
                 '<bookmark mark="b4"/>Step three: find the inner area. '
                 '<bookmark mark="b5"/>Step four: subtract to get the path '
                 'area.'
        ) as t:
            self.wait_until_bookmark("b1")
            self.play(FadeIn(card29[0]), FadeIn(header29), run_time=0.7)
            self.wait_until_bookmark("b2")
            self.play(FadeIn(s1), run_time=0.5)
            self.wait_until_bookmark("b3")
            self.play(FadeIn(s2), run_time=0.5)
            self.wait_until_bookmark("b4")
            self.play(FadeIn(s3), run_time=0.5)
            self.wait_until_bookmark("b5")
            self.play(FadeIn(s4), run_time=0.5)
        self.wait(0.4)
        clear_all()

        # ========================================================
        # ROW 30 — Estimation
        # ========================================================
        t30 = title_text("Estimation Before Solving")
        park_rect = Rectangle(width=2.0, height=1.4, color=DARK_NAVY,
                              stroke_width=2, fill_color=LIGHT_GREEN, fill_opacity=1)
        park_rect.move_to(LEFT*2.5)
        park_lbl = poppins("Park Area", 14, DARK_GREEN).next_to(park_rect, DOWN, buff=0.15)
        park_q = poppins("?", 24, DARK_GREEN, BOLD).next_to(park_rect, UP, buff=0.1)
        path_frame_outer = Rectangle(width=1.6, height=1.1, color=BURNT_ORANGE,
                                     stroke_width=2, fill_color=TAN, fill_opacity=1)
        path_frame_inner = Rectangle(width=1.1, height=0.7, color=BURNT_ORANGE,
                                     stroke_width=1, fill_color=WHITE, fill_opacity=1)
        path_frame_inner.move_to(path_frame_outer.get_center())
        path_frame = VGroup(path_frame_outer, path_frame_inner).move_to(RIGHT*2.5)
        path_lbl = poppins("Path Area", 14, BLUE_C).next_to(path_frame, DOWN, buff=0.15)
        path_q = poppins("?", 24, BLUE_C, BOLD).next_to(path_frame, UP, buff=0.1)
        lt_sym = MathTex("<", color=DARK_NAVY, font_size=42).move_to(UP*0.2)
        # Wait: storyboard says path "<" park (path smaller). Actually transcript says "smaller than the park itself"
        # so park > path. Symbol between path < park.
        # Position: between path (right) and park (left). path < park => path < park.
        # Let's place path on right and put < pointing... we already have < at center which means left < right.
        # left is park, right is path. Park < Path — wrong direction.
        # Use ">" so park > path is shown: park > path.
        lt_sym = MathTex(">", color=DARK_NAVY, font_size=42).move_to(UP*0.2)
        bulb_card_body = VGroup(
            poppins("💡", 20, DARK_GREY),
            poppins("Prediction: Path area ≈ 100 m²", 16, DARK_GREY),
        ).arrange(RIGHT, buff=0.2)
        bulb_card = make_card(bulb_card_body, fill=PALE_YELLOW, border=LIGHT_GREY,
                              border_width=1, pad=0.25, radius=0.12)
        bulb_card.to_edge(DOWN, buff=0.7)

        with self.voiceover(
            text='<bookmark mark="b1"/>I predict the path area should be '
                 '<bookmark mark="b2"/>smaller than the park itself, '
                 '<bookmark mark="b3"/>perhaps around one hundred square '
                 'metres.'
        ) as t:
            self.play(FadeIn(t30), run_time=0.5)
            self.wait_until_bookmark("b1")
            self.play(Create(park_rect), FadeIn(park_lbl), FadeIn(park_q),
                      run_time=0.7)
            self.play(Create(path_frame), FadeIn(path_lbl), FadeIn(path_q),
                      run_time=0.7)
            self.wait_until_bookmark("b2")
            self.play(FadeIn(lt_sym), run_time=0.5)
            self.wait_until_bookmark("b3")
            self.play(FadeIn(bulb_card), run_time=0.7)
        self.wait(0.4)
        clear_all()

        # ========================================================
        # ROW 31 — Step 1: Outer Dimensions
        # ========================================================
        t31 = title_text("Step 1: Outer Dimensions")
        outer31 = Rectangle(width=5.6, height=4.0, color=BURNT_ORANGE,
                            stroke_width=3, fill_color=TAN, fill_opacity=1)
        inner31 = Rectangle(width=4.0, height=2.8, color=DARK_NAVY,
                            stroke_width=3, fill_color=LIGHT_GREEN, fill_opacity=1)
        inner31.move_to(outer31.get_center())
        diag31 = VGroup(outer31, inner31).move_to(LEFT*1.0+DOWN*0.3)
        top_eq = poppins("14 + 2 + 2 = 18 m", 18, BURNT_ORANGE, BOLD)
        top_eq.next_to(outer31, UP, buff=0.15)
        right_eq = poppins("12 + 2 + 2 = 16 m", 18, BURNT_ORANGE, BOLD)
        right_eq.next_to(outer31, RIGHT, buff=0.15).rotate(-PI/2)
        inner_top = poppins("14 m", 14, DARK_GREEN, BOLD).next_to(inner31, UP, buff=0.05)
        inner_right = poppins("12 m", 14, DARK_GREEN, BOLD).next_to(inner31, RIGHT, buff=0.05)
        # red 2m arrows (small)
        def small_red(side):
            if side == "left":
                s, e = outer31.get_left()+UP*0.8, inner31.get_left()+UP*0.8
            elif side == "right":
                s, e = inner31.get_right()+DOWN*0.8, outer31.get_right()+DOWN*0.8
            elif side == "top":
                s, e = inner31.get_top()+LEFT*0.8, outer31.get_top()+LEFT*0.8
            else:
                s, e = inner31.get_bottom()+RIGHT*0.8, outer31.get_bottom()+RIGHT*0.8
            return Arrow(s, e, color=RED_C, stroke_width=1.5,
                         buff=0.05, max_tip_length_to_length_ratio=0.4)
        r_arrs = VGroup(small_red("left"), small_red("right"),
                        small_red("top"), small_red("bottom"))
        # mini plan card top-right with step 1 checked
        mini_plan = VGroup(
            poppins("PLAN", 12, DARK_NAVY, BOLD),
            poppins("✓ 1. Outer dimensions", 10, DARK_GREEN),
            poppins("☐ 2. Outer area", 10, DARK_GREY),
            poppins("☐ 3. Inner area", 10, DARK_GREY),
            poppins("☐ 4. Path area", 10, DARK_GREY),
        ).arrange(DOWN, buff=0.1, aligned_edge=LEFT)
        mini_plan = make_card(mini_plan, fill=WHITE, border=DARK_NAVY,
                              border_width=1, pad=0.2, radius=0.1)
        mini_plan.to_corner(UR, buff=0.4)

        with self.voiceover(
            text='<bookmark mark="b1"/>Now, the outer length: '
                 '<bookmark mark="b2"/>fourteen plus two plus two equals '
                 'eighteen metres. <bookmark mark="b3"/>The outer breadth: '
                 'twelve plus two plus two equals sixteen metres.'
        ) as t:
            self.play(FadeIn(t31), run_time=0.5)
            self.play(Create(outer31), Create(inner31), run_time=1.0)
            self.play(FadeIn(inner_top), FadeIn(inner_right),
                      FadeIn(r_arrs), run_time=0.6)
            self.wait_until_bookmark("b1")
            self.wait(0.2)
            self.wait_until_bookmark("b2")
            self.play(FadeIn(top_eq), run_time=0.7)
            self.wait_until_bookmark("b3")
            self.play(FadeIn(right_eq), FadeIn(mini_plan), run_time=0.8)
        self.wait(0.4)
        clear_all()

        # ========================================================
        # ROW 32 — Step 2: Outer Area
        # ========================================================
        t32 = title_text("Step 2: Outer Area")
        out32 = Rectangle(width=4.0, height=2.8, color=BURNT_ORANGE,
                          stroke_width=3, fill_color=TAN, fill_opacity=0.5)
        out32.move_to(LEFT*1.0)
        l18 = poppins("18 m", 18, BURNT_ORANGE, BOLD).next_to(out32, UP, buff=0.15)
        l16 = poppins("16 m", 18, BURNT_ORANGE, BOLD).next_to(out32, RIGHT, buff=0.15)
        eq32 = MathTex(r"\text{Outer Area} = 18 \times 16 = 288\,\text{m}^2",
                       color=DARK_NAVY, font_size=28)
        eq32.next_to(out32, DOWN, buff=0.6)
        eq32[0][-7:].set_color(BURNT_ORANGE)
        mini_plan2 = VGroup(
            poppins("PLAN", 12, DARK_NAVY, BOLD),
            poppins("✓ 1. Outer dimensions", 10, DARK_GREEN),
            poppins("✓ 2. Outer area", 10, DARK_GREEN),
            poppins("☐ 3. Inner area", 10, DARK_GREY),
            poppins("☐ 4. Path area", 10, DARK_GREY),
        ).arrange(DOWN, buff=0.1, aligned_edge=LEFT)
        mini_plan2 = make_card(mini_plan2, fill=WHITE, border=DARK_NAVY,
                               border_width=1, pad=0.2, radius=0.1)
        mini_plan2.to_corner(UR, buff=0.4)

        with self.voiceover(
            text='<bookmark mark="b1"/>Outer area: <bookmark mark="b2"/>'
                 'eighteen times sixteen, <bookmark mark="b3"/>which is two '
                 'hundred eighty-eight square metres.'
        ) as t:
            self.play(FadeIn(t32), run_time=0.5)
            self.wait_until_bookmark("b1")
            self.play(Create(out32), FadeIn(l18), FadeIn(l16), run_time=0.9)
            self.wait_until_bookmark("b2")
            self.play(FadeIn(eq32), run_time=0.7)
            self.wait_until_bookmark("b3")
            self.play(FadeIn(mini_plan2), run_time=0.6)
        self.wait(0.4)
        clear_all()

        # ========================================================
        # ROW 33 — Step 3: Inner Area
        # ========================================================
        t33 = title_text("Step 3: Inner Area")
        in33 = Rectangle(width=3.4, height=2.4, color=DARK_NAVY, stroke_width=3,
                         fill_color=LIGHT_GREEN, fill_opacity=1).move_to(LEFT*1.0)
        l14 = poppins("14 m", 18, DARK_GREEN, BOLD).next_to(in33, UP, buff=0.15)
        l12 = poppins("12 m", 18, DARK_GREEN, BOLD).next_to(in33, RIGHT, buff=0.15)
        eq33 = MathTex(r"\text{Inner Area} = 14 \times 12 = 168\,\text{m}^2",
                       color=DARK_NAVY, font_size=28)
        eq33.next_to(in33, DOWN, buff=0.6)
        mini_plan3 = VGroup(
            poppins("PLAN", 12, DARK_NAVY, BOLD),
            poppins("✓ 1. Outer dimensions", 10, DARK_GREEN),
            poppins("✓ 2. Outer area", 10, DARK_GREEN),
            poppins("✓ 3. Inner area", 10, DARK_GREEN),
            poppins("☐ 4. Path area", 10, DARK_GREY),
        ).arrange(DOWN, buff=0.1, aligned_edge=LEFT)
        mini_plan3 = make_card(mini_plan3, fill=WHITE, border=DARK_NAVY,
                               border_width=1, pad=0.2, radius=0.1)
        mini_plan3.to_corner(UR, buff=0.4)

        with self.voiceover(
            text='<bookmark mark="b1"/>Inner area: <bookmark mark="b2"/>'
                 'fourteen times twelve equals one hundred sixty-eight '
                 'square metres.'
        ) as t:
            self.play(FadeIn(t33), run_time=0.5)
            self.wait_until_bookmark("b1")
            self.play(Create(in33), FadeIn(l14), FadeIn(l12), run_time=0.9)
            self.wait_until_bookmark("b2")
            self.play(FadeIn(eq33), FadeIn(mini_plan3), run_time=0.8)
        self.wait(0.4)
        clear_all()

        # ========================================================
        # ROW 34 — Step 4: Path Area
        # ========================================================
        t34 = title_text("Step 4: Path Area")
        D1 = VGroup(
            Rectangle(width=1.6, height=1.2, color=BURNT_ORANGE, stroke_width=2,
                      fill_color=TAN, fill_opacity=1),
        )
        D1_lbl = poppins("288 m²", 16, BURNT_ORANGE, BOLD).next_to(D1, DOWN, buff=0.2)
        m34 = MathTex("-", color=DARK_NAVY, font_size=40)
        D2 = Rectangle(width=1.4, height=1.0, color=DARK_NAVY, stroke_width=2,
                       fill_color=LIGHT_GREEN, fill_opacity=1)
        D2_lbl = poppins("168 m²", 16, DARK_GREEN, BOLD).next_to(D2, DOWN, buff=0.2)
        e34 = MathTex("=", color=DARK_NAVY, font_size=40)
        D3_outer = Rectangle(width=1.6, height=1.2, color=BURNT_ORANGE, stroke_width=2,
                             fill_color=TAN, fill_opacity=1)
        D3_inner = Rectangle(width=1.0, height=0.7, color=DARK_NAVY, stroke_width=1,
                             fill_color=WHITE, fill_opacity=1)
        D3_inner.move_to(D3_outer.get_center())
        D3 = VGroup(D3_outer, D3_inner)
        D3_lbl = poppins("120 m²", 22, BLUE_C, BOLD).next_to(D3, DOWN, buff=0.2)
        D3_lbl_hl = SurroundingRectangle(D3_lbl, color=PALE_YELLOW, stroke_width=0,
                                         fill_color=PALE_YELLOW, fill_opacity=0.6,
                                         buff=0.1, corner_radius=0.05)
        D3_lbl_hl.set_z_index(-1)
        row34 = VGroup(D1, m34, D2, e34, D3).arrange(RIGHT, buff=0.5).move_to(UP*0.3)
        D1_lbl.next_to(D1, DOWN, buff=0.2)
        D2_lbl.next_to(D2, DOWN, buff=0.2)
        D3_lbl.next_to(D3, DOWN, buff=0.2)
        D3_lbl_hl.move_to(D3_lbl.get_center())
        full_eq = MathTex(r"\text{Path Area} = 288 - 168 = 120\,\text{m}^2",
                          color=DARK_NAVY, font_size=30)
        full_eq.to_edge(DOWN, buff=0.7)
        mini_plan4 = VGroup(
            poppins("PLAN", 12, DARK_NAVY, BOLD),
            poppins("✓ 1. Outer dimensions", 10, DARK_GREEN),
            poppins("✓ 2. Outer area", 10, DARK_GREEN),
            poppins("✓ 3. Inner area", 10, DARK_GREEN),
            poppins("✓ 4. Path area", 10, DARK_GREEN),
        ).arrange(DOWN, buff=0.1, aligned_edge=LEFT)
        mini_plan4 = make_card(mini_plan4, fill=WHITE, border=DARK_NAVY,
                               border_width=1, pad=0.2, radius=0.1)
        mini_plan4.to_corner(UR, buff=0.4)

        with self.voiceover(
            text='<bookmark mark="b1"/>Path area: <bookmark mark="b2"/>'
                 'two hundred eighty-eight minus one hundred sixty-eight '
                 '<bookmark mark="b3"/>equals one hundred twenty square '
                 'metres.'
        ) as t:
            self.play(FadeIn(t34), run_time=0.5)
            self.wait_until_bookmark("b1")
            self.play(Create(D1), FadeIn(D1_lbl), run_time=0.7)
            self.wait_until_bookmark("b2")
            self.play(FadeIn(m34), Create(D2), FadeIn(D2_lbl), run_time=0.8)
            self.wait_until_bookmark("b3")
            self.play(FadeIn(e34), Create(D3), FadeIn(D3_lbl_hl),
                      FadeIn(D3_lbl), FadeIn(full_eq), FadeIn(mini_plan4),
                      run_time=1.0)
        self.wait(0.6)
        clear_all()

        # ========================================================
        # ROW 35 — Verification
        # ========================================================
        t35 = title_text("Does This Make Sense?")
        v_title = poppins("✓ Verification", 20, DARK_GREEN, BOLD)
        v1 = poppins("✓ Path area = 120 m²", 16, DARK_GREY)
        v2 = poppins("✓ Prediction ≈ 100 m² → 120 in range", 16, DARK_GREY)
        v3 = poppins("✓ Units = m² → correct for area", 16, DARK_GREY)
        vbody = VGroup(v_title, v1, v2, v3).arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        vcard = make_card(vbody, fill=SOFT_GREEN, border=DARK_GREEN,
                          border_width=2, pad=0.4, radius=0.15)
        vcard.move_to(LEFT*2)
        # small frame shape right
        sf_outer = Rectangle(width=2.0, height=1.4, color=BURNT_ORANGE, stroke_width=2,
                             fill_color=TAN, fill_opacity=1)
        sf_inner = Rectangle(width=1.4, height=0.9, color=DARK_NAVY, stroke_width=1,
                             fill_color=WHITE, fill_opacity=1)
        sf_inner.move_to(sf_outer.get_center())
        sf = VGroup(sf_outer, sf_inner).next_to(vcard, RIGHT, buff=0.8)
        sf_lbl = poppins("120 m²", 18, BLUE_C, BOLD).next_to(sf, DOWN, buff=0.2)

        with self.voiceover(
            text='<bookmark mark="b1"/>Does this make sense? '
                 '<bookmark mark="b2"/>The path is one hundred twenty square '
                 'metres. <bookmark mark="b3"/>My prediction was in the '
                 'right range. <bookmark mark="b4"/>The units are square '
                 'metres, which matches area.'
        ) as t:
            self.play(FadeIn(t35), run_time=0.5)
            self.wait_until_bookmark("b1")
            self.play(FadeIn(vcard[0]), FadeIn(v_title), run_time=0.6)
            self.wait_until_bookmark("b2")
            self.play(FadeIn(v1), Create(sf), FadeIn(sf_lbl), run_time=0.7)
            self.wait_until_bookmark("b3")
            self.play(FadeIn(v2), run_time=0.6)
            self.wait_until_bookmark("b4")
            self.play(FadeIn(v3), run_time=0.6)
        self.wait(0.4)
        clear_all()

        # ========================================================
        # ROW 36 — Key insight
        # ========================================================
        t36 = title_text("Key Insight")
        out36 = DashedVMobject(Rectangle(width=4.8, height=3.4, color=BURNT_ORANGE,
                                          stroke_width=3, fill_opacity=0),
                                num_dashes=40)
        in36 = Rectangle(width=3.0, height=2.0, color=DARK_NAVY, stroke_width=3,
                         fill_color=LIGHT_GREEN, fill_opacity=1)
        between = Rectangle(width=4.8, height=3.4, fill_color=TAN, fill_opacity=1,
                            stroke_width=0)
        between_inner = Rectangle(width=3.0, height=2.0, fill_color=WHITE,
                                  fill_opacity=1, stroke_width=0)
        band36 = Difference(between, between_inner,
                            fill_color=TAN, fill_opacity=1, stroke_width=0)
        diag36 = VGroup(band36, in36, out36).move_to(LEFT*0.5)
        L_lbl = MathTex("L", color=DARK_GREY, font_size=24).next_to(in36, UP, buff=0.1)
        B_lbl = MathTex("B", color=DARK_GREY, font_size=24).next_to(in36, RIGHT, buff=0.1)
        # w on each side (red)
        w_lbls = VGroup(
            MathTex("w", color=RED_C, font_size=20).move_to(in36.get_left()+LEFT*0.4),
            MathTex("w", color=RED_C, font_size=20).move_to(in36.get_right()+RIGHT*0.4),
            MathTex("w", color=RED_C, font_size=20).move_to(in36.get_top()+UP*0.35),
            MathTex("w", color=RED_C, font_size=20).move_to(in36.get_bottom()+DOWN*0.35),
        )
        outer_top = MathTex("L + 2w", color=BURNT_ORANGE, font_size=24)
        outer_top.next_to(out36, UP, buff=0.15)
        hl_top = SurroundingRectangle(outer_top[0][-2:], color=PALE_YELLOW,
                                      fill_color=PALE_YELLOW, fill_opacity=0.6,
                                      stroke_width=0, buff=0.05)
        hl_top.set_z_index(-1)
        outer_right = MathTex("B + 2w", color=BURNT_ORANGE, font_size=24)
        outer_right.next_to(out36, RIGHT, buff=0.15)
        insight_body = VGroup(
            poppins("🔑", 22, BURNT_ORANGE),
            poppins("Outer dimensions increase by twice the path width.",
                    16, DARK_NAVY, BOLD),
        ).arrange(RIGHT, buff=0.2)
        insight_card = make_card(insight_body, fill=YELLOW_C, border=DARK_NAVY,
                                 border_width=2, pad=0.25, radius=0.15)
        insight_card.to_edge(DOWN, buff=0.5)

        with self.voiceover(
            text='<bookmark mark="b1"/>The key insight is this: '
                 '<bookmark mark="b2"/>when a path surrounds a rectangle, '
                 '<bookmark mark="b3"/>the outer dimensions increase by twice '
                 'the path width.'
        ) as t:
            self.play(FadeIn(t36), run_time=0.5)
            self.wait_until_bookmark("b1")
            self.play(FadeIn(band36), Create(in36), Create(out36),
                      FadeIn(L_lbl), FadeIn(B_lbl), FadeIn(w_lbls),
                      run_time=1.2)
            self.wait_until_bookmark("b2")
            self.play(FadeIn(hl_top), FadeIn(outer_top),
                      FadeIn(outer_right), run_time=0.8)
            self.wait_until_bookmark("b3")
            self.play(FadeIn(insight_card), run_time=0.7)
        self.wait(0.4)
        clear_all()

        # ========================================================
        # ROW 37 — Variation: path inside
        # ========================================================
        # Left: outside (original)
        lt37 = poppins("Path Outside — Original", 16, DARK_NAVY, BOLD).move_to(LEFT*3.5+UP*2.8)
        out37L = DashedVMobject(Rectangle(width=2.6, height=1.9, color=BURNT_ORANGE,
                                           stroke_width=2, fill_opacity=0),
                                 num_dashes=30)
        in37L = Rectangle(width=1.8, height=1.2, color=DARK_NAVY, stroke_width=2,
                          fill_color=LIGHT_GREEN, fill_opacity=1)
        band37L = Difference(
            Rectangle(width=2.6, height=1.9, fill_color=TAN, fill_opacity=1, stroke_width=0),
            Rectangle(width=1.8, height=1.2, fill_color=WHITE, fill_opacity=1, stroke_width=0),
            fill_color=TAN, fill_opacity=1, stroke_width=0)
        diag37L = VGroup(band37L, in37L, out37L).move_to(LEFT*3.5)
        lblL_top = MathTex("L + 2w", color=BURNT_ORANGE, font_size=18).next_to(out37L, UP, buff=0.1)
        lblL_right = MathTex("B + 2w", color=BURNT_ORANGE, font_size=18).next_to(out37L, RIGHT, buff=0.1)
        cap37L = poppins("Outer grows", 14, DARK_GREEN).next_to(diag37L, DOWN, buff=0.5)
        # Right: path inside
        rt37 = poppins("Path Inside", 16, DARK_NAVY, BOLD).move_to(RIGHT*3.5+UP*2.8)
        out37R = Rectangle(width=2.6, height=1.9, color=DARK_NAVY, stroke_width=2,
                           fill_color=LIGHT_GREEN, fill_opacity=1)
        in37R = Rectangle(width=1.6, height=1.0, color=DARK_NAVY, stroke_width=1,
                          fill_color=WHITE, fill_opacity=1)
        in37R.move_to(out37R.get_center())
        band37R = Difference(
            Rectangle(width=2.6, height=1.9, fill_color=TAN, fill_opacity=1, stroke_width=0),
            Rectangle(width=1.6, height=1.0, fill_color=WHITE, fill_opacity=1, stroke_width=0),
            fill_color=TAN, fill_opacity=1, stroke_width=0)
        band37R.move_to(out37R.get_center())
        # but outer is green park; rebuild: green park entire + tan band inside between green outer and white inner
        # simpler: green outer rect already; overlay tan band; overlay white inner
        diag37R = VGroup(out37R, band37R, in37R).move_to(RIGHT*3.5)
        lblR_in = VGroup(
            MathTex(r"L - 2w", color=RED_C, font_size=18),
            MathTex(r"B - 2w", color=RED_C, font_size=18),
        ).arrange(DOWN, buff=0.1)
        lblR_in.next_to(diag37R, RIGHT, buff=0.3)
        cap37R = poppins("Inner shrinks", 14, RED_C).next_to(diag37R, DOWN, buff=0.5)
        bottom37 = poppins("When the path is inside, the inner dimensions decrease.",
                           16, DARK_GREY).to_edge(DOWN, buff=0.3)

        with self.voiceover(
            text='<bookmark mark="b1"/>Before we move on, picture two '
                 'variations. <bookmark mark="b2"/>First: what if the path '
                 'were built inside the park instead of outside? '
                 '<bookmark mark="b3"/>Would the outer dimensions still '
                 'increase? No — <bookmark mark="b4"/>the inner carpet '
                 'would shrink.'
        ) as t:
            self.wait_until_bookmark("b1")
            self.play(FadeIn(lt37), FadeIn(rt37), run_time=0.5)
            self.wait_until_bookmark("b2")
            self.play(FadeIn(band37L), Create(in37L), Create(out37L),
                      FadeIn(lblL_top), FadeIn(lblL_right),
                      FadeIn(cap37L), run_time=1.0)
            self.wait_until_bookmark("b3")
            self.play(Create(out37R), FadeIn(band37R), Create(in37R),
                      run_time=1.0)
            self.wait_until_bookmark("b4")
            self.play(FadeIn(lblR_in), FadeIn(cap37R),
                      FadeIn(bottom37), run_time=0.8)
        self.wait(0.4)
        clear_all()

        # ========================================================
        # ROW 38 — Non-uniform path width
        # ========================================================
        t38 = title_text("Variation 2: Non-Uniform Path Width")
        in38 = Rectangle(width=2.6, height=1.8, color=DARK_NAVY, stroke_width=3,
                         fill_color=LIGHT_GREEN, fill_opacity=1)
        out38 = DashedVMobject(Rectangle(width=4.6, height=2.6, color=BURNT_ORANGE,
                                          stroke_width=2, fill_opacity=0),
                                num_dashes=30)
        band38_outer = Rectangle(width=4.6, height=2.6, fill_color=TAN, fill_opacity=1, stroke_width=0)
        band38_inner = Rectangle(width=2.6, height=1.8, fill_color=WHITE, fill_opacity=1, stroke_width=0)
        band38 = Difference(band38_outer, band38_inner,
                            fill_color=TAN, fill_opacity=1, stroke_width=0)
        diag38 = VGroup(band38, in38, out38).move_to(LEFT*1.0)
        w2_L = poppins("2 m", 12, RED_C).move_to(in38.get_left()+LEFT*0.45)
        w2_R = poppins("2 m", 12, RED_C).move_to(in38.get_right()+RIGHT*0.45)
        w1_T = poppins("1 m", 12, RED_C).move_to(in38.get_top()+UP*0.2)
        w1_B = poppins("1 m", 12, RED_C).move_to(in38.get_bottom()+DOWN*0.2)
        ws38 = VGroup(w2_L, w2_R, w1_T, w1_B)
        out_top = MathTex("L + 4", color=BURNT_ORANGE, font_size=20).next_to(out38, UP, buff=0.15)
        out_right = MathTex("B + 2", color=BURNT_ORANGE, font_size=20).next_to(out38, RIGHT, buff=0.15)
        reminder = make_card(
            poppins("1. Read carefully → 2. Draw carefully → 3. Compute",
                    14, DARK_GREY),
            fill=WHITE, border=DARK_NAVY, border_width=1.5,
            pad=0.25, radius=0.12)
        reminder.to_edge(DOWN, buff=0.5)

        with self.voiceover(
            text='<bookmark mark="b1"/>Second: what if the path were two '
                 'metres wide on the length sides but only one metre wide '
                 'on the breadth sides? <bookmark mark="b2"/>The hidden '
                 'condition changes, but the principle stays the same: '
                 '<bookmark mark="b3"/>read carefully, draw carefully, then '
                 'compute.'
        ) as t:
            self.play(FadeIn(t38), run_time=0.5)
            self.wait_until_bookmark("b1")
            self.play(FadeIn(band38), Create(in38), Create(out38),
                      FadeIn(ws38), run_time=1.2)
            self.play(FadeIn(out_top), FadeIn(out_right), run_time=0.6)
            self.wait_until_bookmark("b2")
            self.wait(0.2)
            self.wait_until_bookmark("b3")
            self.play(FadeIn(reminder), run_time=0.7)
        self.wait(0.4)
        clear_all()

        # ========================================================
        # ROW 39 — Read structure before calculate
        # ========================================================
        bigt = poppins("Read the Structure Before You Calculate.",
                       30, DARK_NAVY, BOLD).move_to(UP*1.8)
        icon1 = poppins("🔍", 36, DARK_GREY)
        lbl1 = poppins("Read", 14, DARK_GREY).next_to(icon1, DOWN, buff=0.2)
        n1 = VGroup(icon1, lbl1).move_to(LEFT*4)
        icon2 = poppins("✏️", 36, DARK_GREY)
        lbl2 = poppins("Draw", 14, DARK_GREY).next_to(icon2, DOWN, buff=0.2)
        n2 = VGroup(icon2, lbl2).move_to(ORIGIN+DOWN*0.5)
        icon3 = poppins("🖩", 36, DARK_GREY)
        lbl3 = poppins("Calculate", 14, DARK_GREY).next_to(icon3, DOWN, buff=0.2)
        n3 = VGroup(icon3, lbl3).move_to(RIGHT*4)
        arr_a = Arrow(n1.get_right(), n2.get_left(), color=DARK_GREY,
                      stroke_width=2, buff=0.2)
        arr_b = Arrow(n2.get_right(), n3.get_left(), color=DARK_GREY,
                      stroke_width=2, buff=0.2)
        # dashed shortcut
        shortcut = DashedLine(n1.get_top()+UP*0.2, n3.get_top()+UP*0.2,
                              color=RED_C, dash_length=0.15, stroke_width=2)
        sx = cross_icon().scale(0.7).move_to(shortcut.get_center())

        with self.voiceover(
            text='<bookmark mark="b1"/>The skill you have built is '
                 '<bookmark mark="b2"/>reading the structure before you '
                 'calculate.'
        ) as t:
            self.wait_until_bookmark("b1")
            self.play(FadeIn(bigt), run_time=0.7)
            self.wait_until_bookmark("b2")
            self.play(FadeIn(n1), Create(arr_a), FadeIn(n2),
                      Create(arr_b), FadeIn(n3),
                      Create(shortcut), FadeIn(sx), run_time=1.2)
        self.wait(0.4)
        clear_all()

        # ========================================================
        # ROW 40 — Misconception confronted
        # ========================================================
        t40 = title_text("Misconception Confronted")
        misc_body = VGroup(
            poppins("⚠", 20, RED_C),
            poppins("Same perimeter → same area", 18, DARK_GREY),
        ).arrange(RIGHT, buff=0.2)
        # Strikethrough on "same area"
        strike = Line(misc_body[1].get_left()+RIGHT*1.7,
                      misc_body[1].get_right(), color=RED_C, stroke_width=2)
        misc_card = make_card(misc_body, fill=PALE_RED, border=RED_C,
                              border_width=2, pad=0.25, radius=0.12)
        misc_card.move_to(UP*2.5)
        strike.move_to(misc_body[1].get_center()).align_to(misc_body[1].get_right(), RIGHT).shift(LEFT*0.5)
        # rectangles row 19 redone smaller
        rA40 = grid_rect(4, 1, cell=0.4).move_to(LEFT*3+DOWN*0.3)
        fA40 = fill_cells(4, 1, 0.4, [(0,c,PALE_RED) for c in range(4)],
                          base_pos=rA40.get_center())
        lA40 = VGroup(poppins("P = 10", 14, DARK_GREY),
                      poppins("A = 4", 14, RED_C, BOLD)
                      ).arrange(DOWN, buff=0.1).next_to(rA40, DOWN, buff=0.3)
        rB40 = grid_rect(3, 2, cell=0.4).move_to(RIGHT*3+DOWN*0.3)
        fB40 = fill_cells(3, 2, 0.4,
                          [(r,c,PALE_BLUE) for r in range(2) for c in range(3)],
                          base_pos=rB40.get_center())
        lB40 = VGroup(poppins("P = 10", 14, DARK_GREY),
                      poppins("A = 6", 14, BLUE_C, BOLD)
                      ).arrange(DOWN, buff=0.1).next_to(rB40, DOWN, buff=0.3)
        between40 = VGroup(
            poppins("P = 10 = 10", 14, DARK_GREY),
            poppins("A = 4 ≠ 6", 14, RED_C, BOLD),
        ).arrange(DOWN, buff=0.15).move_to(DOWN*0.3)
        big_x = cross_icon().scale(0.8).next_to(misc_card, RIGHT, buff=0.3)

        with self.voiceover(
            text='<bookmark mark="b1"/>Let us confront that misconception '
                 'more directly. <bookmark mark="b2"/>It seems logical that '
                 'if two rectangles have the same perimeter, they must have '
                 'the same area. The boundary encloses the space, after all. '
                 '<bookmark mark="b3"/>But remember our examples: a four-by-'
                 'one rectangle and a three-by-two rectangle both have '
                 'perimeter ten, <bookmark mark="b4"/>yet their areas are '
                 'four and six.'
        ) as t:
            self.play(FadeIn(t40), run_time=0.5)
            self.wait_until_bookmark("b1")
            self.play(FadeIn(misc_card), run_time=0.7)
            self.wait_until_bookmark("b2")
            self.play(Create(strike), FadeIn(big_x), run_time=0.6)
            self.wait_until_bookmark("b3")
            self.play(Create(rA40), FadeIn(fA40), FadeIn(lA40),
                      Create(rB40), FadeIn(fB40), FadeIn(lB40), run_time=1.2)
            self.wait_until_bookmark("b4")
            self.play(FadeIn(between40), run_time=0.7)
        self.wait(0.4)
        clear_all()

        # ========================================================
        # ROW 41 — Fence vs Field memory aid
        # ========================================================
        self.camera.background_color = SOFT_GREEN
        t41 = title_text("💡 Memory Aid")
        # Fence diagram
        fence_rect = DashedVMobject(Rectangle(width=2.6, height=1.8,
                                              color=BROWN, stroke_width=3),
                                     num_dashes=40)
        posts = VGroup(*[
            Dot(point=fence_rect.get_corner(d)+np.array([0,0,0]),
                radius=0.08, color=BROWN)
            for d in [UL, UR, DL, DR]
        ])
        fence_grp = VGroup(fence_rect, posts).move_to(LEFT*3.5)
        fence_lbl = poppins("Perimeter = Fence", 18, DARK_GREY, BOLD).next_to(fence_grp, DOWN, buff=0.3)
        # Field
        field_rect = Rectangle(width=2.6, height=1.8, color=BROWN, stroke_width=2,
                               fill_color=MED_GREEN, fill_opacity=1).set_stroke(opacity=0.3)
        field_dots = VGroup(*[Dot(point=np.array([np.random.uniform(-1.2,1.2),
                                                  np.random.uniform(-0.8,0.8),0]),
                                   radius=0.04, color=DARK_GREEN)
                              for _ in range(25)])
        field_dots.move_to(field_rect.get_center())
        field_grp = VGroup(field_rect, field_dots).move_to(RIGHT*3.5)
        field_lbl = poppins("Area = Field", 18, DARK_GREY, BOLD).next_to(field_grp, DOWN, buff=0.3)
        concl_body = poppins("Same fence length → Different field sizes",
                             16, DARK_NAVY, BOLD)
        concl_card41 = make_card(concl_body, fill=PALE_YELLOW, border=DARK_NAVY,
                                 border_width=2, pad=0.25, radius=0.12)
        concl_card41.to_edge(DOWN, buff=0.4)

        with self.voiceover(
            text='<bookmark mark="b1"/>Here is a memory aid: '
                 '<bookmark mark="b2"/>perimeter is the fence; '
                 '<bookmark mark="b3"/>area is the field. '
                 '<bookmark mark="b4"/>Same fence length can enclose '
                 'different field sizes.'
        ) as t:
            self.play(FadeIn(t41), run_time=0.5)
            self.wait_until_bookmark("b1")
            self.wait(0.2)
            self.wait_until_bookmark("b2")
            self.play(Create(fence_grp), FadeIn(fence_lbl), run_time=1.0)
            self.wait_until_bookmark("b3")
            self.play(Create(field_grp), FadeIn(field_lbl), run_time=1.0)
            self.wait_until_bookmark("b4")
            self.play(FadeIn(concl_card41), run_time=0.7)
        self.wait(0.4)
        clear_all()
        self.camera.background_color = WHITE

        # ========================================================
        # ROW 42 — Independent measures
        # ========================================================
        badge_A = Circle(radius=0.7, color=DARK_GREEN, stroke_width=3,
                         fill_opacity=0)
        bA_icon = Rectangle(width=0.5, height=0.3, color=DARK_GREEN,
                            fill_color=DARK_GREEN, fill_opacity=1).move_to(badge_A.get_center())
        bA_lbl = poppins("AREA\nMeasures surface", 12, DARK_GREEN).next_to(badge_A, DOWN, buff=0.15)
        b_a = VGroup(badge_A, bA_icon, bA_lbl).move_to(LEFT*3.5 + UP*1.5)
        badge_P = Circle(radius=0.7, color=BURNT_ORANGE, stroke_width=3,
                         fill_opacity=0)
        bP_icon = Rectangle(width=0.5, height=0.3, color=BURNT_ORANGE,
                            stroke_width=3).move_to(badge_P.get_center())
        bP_lbl = poppins("PERIMETER\nMeasures boundary", 12, BURNT_ORANGE).next_to(badge_P, DOWN, buff=0.15)
        b_p = VGroup(badge_P, bP_icon, bP_lbl).move_to(RIGHT*3.5 + UP*1.5)
        neq42 = VGroup(
            MathTex(r"\neq", color=DARK_NAVY, font_size=36),
            poppins("Independent", 14, DARK_NAVY, BOLD),
        ).arrange(DOWN, buff=0.15).move_to(UP*1.5)
        # Flow paths
        wrong_strip = Rectangle(width=12, height=1.0, color=PALE_RED,
                                fill_color=PALE_RED, fill_opacity=1, stroke_width=0)
        wrong_strip.move_to(DOWN*0.5)
        wrong_items = VGroup(
            poppins("Problem", 12, DARK_GREY),
            poppins("→", 14, DARK_GREY),
            poppins("Skip comprehension", 12, RED_C),
            poppins("→", 14, DARK_GREY),
            poppins("Calculator", 12, DARK_GREY),
            poppins("→", 14, DARK_GREY),
            cross_icon().scale(0.4),
        ).arrange(RIGHT, buff=0.3).move_to(wrong_strip.get_center())
        # strikethrough on "Skip comprehension"
        strike42 = Line(wrong_items[2].get_left(), wrong_items[2].get_right(),
                        color=RED_C, stroke_width=2)
        right_strip42 = Rectangle(width=12, height=1.0, color=SOFT_GREEN,
                                  fill_color=SOFT_GREEN, fill_opacity=1, stroke_width=0)
        right_strip42.move_to(DOWN*1.8)
        right_items = VGroup(
            poppins("Problem", 12, DARK_GREY),
            poppins("→", 14, DARK_GREY),
            poppins("Identify Given & Asked", 12, DARK_GREEN),
            poppins("→", 14, DARK_GREY),
            poppins("Comprehend", 12, DARK_GREEN),
            poppins("→", 14, DARK_GREY),
            poppins("Calculator", 12, DARK_GREY),
            poppins("→", 14, DARK_GREY),
            check_icon().scale(0.4),
        ).arrange(RIGHT, buff=0.25).move_to(right_strip42.get_center())

        with self.voiceover(
            text='<bookmark mark="b1"/>The precise way to think about this '
                 'is that <bookmark mark="b2"/>area and perimeter are '
                 'independent measures. <bookmark mark="b3"/>This error '
                 'typically arises when we skip the comprehension stage and '
                 'jump straight to numbers. <bookmark mark="b4"/>If you '
                 'identify what is given and what is asked, this confusion '
                 'will not trap you.'
        ) as t:
            self.wait_until_bookmark("b1")
            self.play(FadeIn(b_a), FadeIn(b_p), run_time=0.8)
            self.wait_until_bookmark("b2")
            self.play(FadeIn(neq42), run_time=0.5)
            self.wait_until_bookmark("b3")
            self.play(FadeIn(wrong_strip), FadeIn(wrong_items),
                      Create(strike42), run_time=1.0)
            self.wait_until_bookmark("b4")
            self.play(FadeIn(right_strip42), FadeIn(right_items), run_time=1.0)
        self.wait(0.4)
        clear_all()

        # ========================================================
        # ROW 43 — Unit error
        # ========================================================
        t43 = title_text("Unit Error Alert", color=RED_C)
        warn = poppins("⚠", 28, RED_C, BOLD).next_to(t43, LEFT, buff=0.2)
        left_bg43 = Rectangle(width=6.0, height=4.0, color=PALE_RED,
                              fill_color=PALE_RED, fill_opacity=1, stroke_width=0)
        left_bg43.move_to(LEFT*3.3+DOWN*0.5)
        wrong43 = poppins("120 m", 32, DARK_GREY, BOLD)
        wrong43.move_to(left_bg43.get_center()+UP*0.8)
        strike43 = Line(wrong43.get_left(), wrong43.get_right(),
                        color=RED_C, stroke_width=3)
        x43 = cross_icon().scale(0.8).next_to(wrong43, RIGHT, buff=0.3)
        line43 = Line(LEFT*1.5, RIGHT*1.5, color=DARK_GREY, stroke_width=3).move_to(left_bg43.get_center()+DOWN*0.5)
        line_lbl = poppins("This is a line (length)", 12, RED_C).next_to(line43, DOWN, buff=0.2)
        right_bg43 = Rectangle(width=6.0, height=4.0, color=SOFT_GREEN,
                               fill_color=SOFT_GREEN, fill_opacity=1, stroke_width=0)
        right_bg43.move_to(RIGHT*3.3+DOWN*0.5)
        good43 = MathTex(r"120\,\text{m}^2", color=DARK_NAVY, font_size=40)
        good43.move_to(right_bg43.get_center()+UP*0.8)
        hl43 = SurroundingRectangle(good43, color=SOFT_GREEN, fill_color=YELLOW_C,
                                    fill_opacity=0.3, stroke_width=0, buff=0.1)
        hl43.set_z_index(-1)
        sup_circle = Circle(radius=0.18, color=DARK_GREEN, stroke_width=2)
        sup_circle.move_to(good43[0][-1].get_center())
        v43 = check_icon().scale(0.8).next_to(good43, RIGHT, buff=0.3)
        surf43 = Rectangle(width=1.5, height=0.9, color=DARK_NAVY, stroke_width=2,
                           fill_color=PALE_BLUE, fill_opacity=1).move_to(right_bg43.get_center()+DOWN*0.5)
        surf_lbl = poppins("This is a surface (area)", 12, DARK_GREEN).next_to(surf43, DOWN, buff=0.2)
        summary43 = poppins("metres → length    |    square metres → area",
                            16, DARK_NAVY, BOLD).to_edge(DOWN, buff=0.3)
        summary_card = make_card(summary43, fill=WHITE, border=DARK_NAVY,
                                 border_width=1.5, pad=0.2, radius=0.1)
        summary_card.to_edge(DOWN, buff=0.3)

        with self.voiceover(
            text='<bookmark mark="b1"/>Here is another error that appears '
                 'even in higher classes. <bookmark mark="b2"/>A student '
                 'finishes the calculation and says the path is one hundred '
                 'twenty metres. <bookmark mark="b3"/>That would be a line, '
                 'not a surface. <bookmark mark="b4"/>We are covering a '
                 'surface with tiles, so the unit must be square metres. '
                 '<bookmark mark="b5"/>Remember: metres measure length; '
                 'square metres measure area.'
        ) as t:
            self.play(FadeIn(t43), FadeIn(warn), run_time=0.5)
            self.wait_until_bookmark("b1")
            self.play(FadeIn(left_bg43), run_time=0.5)
            self.wait_until_bookmark("b2")
            self.play(FadeIn(wrong43), FadeIn(x43), run_time=0.6)
            self.wait_until_bookmark("b3")
            self.play(Create(strike43), Create(line43), FadeIn(line_lbl),
                      run_time=0.8)
            self.wait_until_bookmark("b4")
            self.play(FadeIn(right_bg43), FadeIn(hl43), FadeIn(good43),
                      Create(sup_circle), FadeIn(v43),
                      Create(surf43), FadeIn(surf_lbl), run_time=1.2)
            self.wait_until_bookmark("b5")
            self.play(FadeIn(summary_card), run_time=0.7)
        self.wait(0.4)
        clear_all()

        # ========================================================
        # ROW 44 — Connections: quadrilaterals
        # ========================================================
        t44 = title_text("Connections: What Comes Next")
        central = Rectangle(width=2.0, height=1.0, color=DARK_NAVY, stroke_width=3,
                            fill_color=PALE_BLUE, fill_opacity=1).move_to(UP*1.5)
        central_lbl = poppins("Rectangle", 16, DARK_NAVY, BOLD).move_to(central.get_center())
        # 3 dashed shapes below
        para = Polygon([-1,0,0],[1,0,0],[0.6,0.8,0],[-1.4,0.8,0],
                       color=DARK_GREY, stroke_width=2).set_stroke(opacity=0.6)
        para = DashedVMobject(para, num_dashes=20)
        rhom = Polygon([0,0.6,0],[0.7,0,0],[0,-0.6,0],[-0.7,0,0],
                       color=DARK_GREY, stroke_width=2)
        rhom = DashedVMobject(rhom, num_dashes=20)
        trap = Polygon([-1,-0.4,0],[1,-0.4,0],[0.6,0.4,0],[-0.6,0.4,0],
                       color=DARK_GREY, stroke_width=2)
        trap = DashedVMobject(trap, num_dashes=20)
        shapes44 = VGroup(para, rhom, trap).arrange(RIGHT, buff=1.2).move_to(DOWN*1.0)
        sl1 = poppins("Parallelogram 🔒", 12, DARK_GREY).next_to(shapes44[0], DOWN, buff=0.15)
        sl2 = poppins("Rhombus 🔒", 12, DARK_GREY).next_to(shapes44[1], DOWN, buff=0.15)
        sl3 = poppins("Trapezium 🔒", 12, DARK_GREY).next_to(shapes44[2], DOWN, buff=0.15)
        # arrows from central down to each
        arr44 = VGroup(*[Arrow(central.get_bottom(), s.get_top(),
                                color=DARK_GREY, stroke_width=1.5, buff=0.1)
                         for s in shapes44])
        scissors = poppins("✂", 22, DARK_GREY).move_to(LEFT*5+DOWN*1.0)
        cap44 = poppins("All secretly built from rectangles.",
                        16, DARK_NAVY, BOLD).to_edge(DOWN, buff=0.4)

        with self.voiceover(
            text='<bookmark mark="b1"/>Notice how this connects to what '
                 'comes next. <bookmark mark="b2"/>In this chapter, every '
                 'quadrilateral area formula — parallelogram, rhombus, '
                 'trapezium — is secretly built from rectangles. '
                 '<bookmark mark="b3"/>Today we master the rectangle. '
                 '<bookmark mark="b4"/>Tomorrow, we cut and rearrange it.'
        ) as t:
            self.play(FadeIn(t44), run_time=0.5)
            self.wait_until_bookmark("b1")
            self.play(Create(central), FadeIn(central_lbl), run_time=0.7)
            self.wait_until_bookmark("b2")
            self.play(FadeIn(shapes44), FadeIn(sl1), FadeIn(sl2), FadeIn(sl3),
                      Create(arr44), run_time=1.2)
            self.wait_until_bookmark("b3")
            self.play(FadeIn(cap44), run_time=0.6)
            self.wait_until_bookmark("b4")
            self.play(FadeIn(scissors), run_time=0.5)
        self.wait(0.4)
        clear_all()

        # ========================================================
        # ROW 45 — Triangle preview
        # ========================================================
        t45 = title_text("Coming Next: Triangle Area")
        rect45 = DashedVMobject(Rectangle(width=3.0, height=2.0, color=DARK_NAVY,
                                           stroke_width=3, fill_opacity=0),
                                 num_dashes=40)
        rect45.move_to(ORIGIN)
        tri45 = Polygon(
            rect45.get_corner(DL), rect45.get_corner(DR),
            rect45.get_top(),
            color=DARK_NAVY, stroke_width=3,
            fill_color=PALE_YELLOW, fill_opacity=0.5)
        rl = poppins("Rectangle", 12, DARK_GREY).next_to(rect45, UR, buff=0.2)
        tl = poppins("Triangle (next topic) 🔒", 12, DARK_GREY).next_to(rect45, DR, buff=0.4)
        cap45 = poppins("Triangle area comes from the rectangle formula.",
                        16, DARK_GREY).to_edge(DOWN, buff=0.5)

        with self.voiceover(
            text='<bookmark mark="b1"/>In the next section, we will use this '
                 'rectangle formula <bookmark mark="b2"/>to discover the area '
                 'of a triangle <bookmark mark="b3"/>by drawing a rectangle '
                 'around it.'
        ) as t:
            self.play(FadeIn(t45), run_time=0.5)
            self.wait_until_bookmark("b1")
            self.play(Create(rect45), FadeIn(rl), run_time=0.9)
            self.wait_until_bookmark("b2")
            self.play(Create(tri45), FadeIn(tl), run_time=1.0)
            self.wait_until_bookmark("b3")
            self.play(FadeIn(cap45), run_time=0.6)
        self.wait(0.4)
        clear_all()

        # ========================================================
        # ROW 46 — Why this matters levels
        # ========================================================
        t46 = title_text("Why This Matters")
        lvl1 = Rectangle(width=5.5, height=0.9, color=DARK_NAVY, stroke_width=2,
                         fill_color=PALE_BLUE, fill_opacity=1).move_to(DOWN*1.5)
        lvl1_lbl = VGroup(
            poppins("Rectangle Area", 16, DARK_NAVY, BOLD),
            poppins("Used daily by architects & gardeners",
                    12, DARK_GREY),
        ).arrange(DOWN, buff=0.05).move_to(lvl1.get_center())
        lvl2 = Rectangle(width=4.5, height=0.7, color=DARK_GREY, stroke_width=2,
                         fill_opacity=0).move_to(ORIGIN).set_stroke(opacity=0.5)
        lvl2_lbl = poppins("Volume & Surface Area 🔒", 14, DARK_GREY).move_to(lvl2.get_center()).set_opacity(0.6)
        lvl3 = Rectangle(width=3.5, height=0.5, color=LIGHT_GREY, stroke_width=2,
                         fill_opacity=0).move_to(UP*1.2).set_stroke(opacity=0.3)
        lvl3_lbl = poppins("Higher Classes", 12, LIGHT_GREY).move_to(lvl3.get_center())
        arr_up_1 = Arrow(lvl1.get_top(), lvl2.get_bottom(),
                         color=DARK_GREY, stroke_width=1.5, buff=0.1).set_stroke(opacity=0.6)
        arr_up_2 = Arrow(lvl2.get_top(), lvl3.get_bottom(),
                         color=DARK_GREY, stroke_width=1.5, buff=0.1).set_stroke(opacity=0.4)
        cap46 = poppins("None of that works unless the rectangle is clear.",
                        16, DARK_NAVY, BOLD).to_edge(DOWN, buff=0.3)

        with self.voiceover(
            text='<bookmark mark="b1"/>Architects and gardeners use these '
                 'calculations daily to estimate materials. '
                 '<bookmark mark="b2"/>In higher classes, you will see area '
                 'become the foundation for volume and surface area. '
                 '<bookmark mark="b3"/>But none of that works unless the '
                 'rectangle is clear in your mind.'
        ) as t:
            self.play(FadeIn(t46), run_time=0.5)
            self.wait_until_bookmark("b1")
            self.play(Create(lvl1), FadeIn(lvl1_lbl), run_time=0.8)
            self.wait_until_bookmark("b2")
            self.play(Create(arr_up_1), Create(lvl2), FadeIn(lvl2_lbl),
                      Create(arr_up_2), Create(lvl3), FadeIn(lvl3_lbl),
                      run_time=1.2)
            self.wait_until_bookmark("b3")
            self.play(FadeIn(cap46), run_time=0.7)
        self.wait(0.4)
        clear_all()

        # ========================================================
        # ROW 47 — Your turn
        # ========================================================
        badge47_bg = RoundedRectangle(width=1.6, height=0.4, corner_radius=0.05,
                                      fill_color=BLUE_C, fill_opacity=1,
                                      stroke_width=0)
        badge47_txt = poppins("YOUR TURN", 12, WHITE, BOLD)
        badge47 = VGroup(badge47_bg, badge47_txt)
        p47_l1 = VGroup(
            poppins("A rectangular room is ", 16, DARK_GREY),
            poppins("eight metres by five metres.", 16, DARK_GREEN, BOLD),
        ).arrange(RIGHT, buff=0.1)
        p47_l2 = VGroup(
            poppins("A carpet covers the centre, leaving a ", 16, DARK_GREY),
            poppins("one-metre border", 16, DARK_GREEN, BOLD),
            poppins(" all around.", 16, DARK_GREY),
        ).arrange(RIGHT, buff=0.05)
        p47_l3 = poppins("What is the area of the border?", 16, BLUE_C, BOLD)
        body47 = VGroup(p47_l1, p47_l2, p47_l3).arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        card47 = make_card(body47, fill=PALE_YELLOW, border=DARK_NAVY,
                           border_width=2, pad=0.4, radius=0.2)
        card47.move_to(UP*1.8)
        badge47.next_to(card47, UP, buff=-0.15).align_to(card47, LEFT).shift(RIGHT*0.3)
        # diagram
        out47 = Rectangle(width=4.0, height=2.5, color=DARK_NAVY, stroke_width=3,
                          fill_color=TAN, fill_opacity=1)
        in47 = DashedVMobject(Rectangle(width=3.0, height=1.5, color=DARK_NAVY,
                                         stroke_width=2, fill_color=WHITE, fill_opacity=1),
                               num_dashes=30)
        in47_fill = Rectangle(width=3.0, height=1.5, fill_color=WHITE, fill_opacity=1,
                              stroke_width=0).move_to(out47.get_center())
        in47_grp = VGroup(in47_fill, in47).move_to(out47.get_center())
        l8 = poppins("8 m", 14, DARK_GREEN, BOLD).next_to(out47, UP, buff=0.1)
        l5 = poppins("5 m", 14, DARK_GREEN, BOLD).next_to(out47, RIGHT, buff=0.1)
        diag47 = VGroup(out47, in47_grp).move_to(DOWN*1.5)
        l8.next_to(out47, UP, buff=0.1)
        l5.next_to(out47, RIGHT, buff=0.1)
        # 1m red arrows
        def red1m(side):
            if side == "left":
                s, e = out47.get_left()+UP*0.5, in47_grp.get_left()+UP*0.5
            elif side == "right":
                s, e = in47_grp.get_right()+DOWN*0.5, out47.get_right()+DOWN*0.5
            elif side == "top":
                s, e = in47_grp.get_top()+LEFT*0.5, out47.get_top()+LEFT*0.5
            else:
                s, e = in47_grp.get_bottom()+RIGHT*0.5, out47.get_bottom()+RIGHT*0.5
            return Arrow(s, e, color=RED_C, stroke_width=1.5,
                         buff=0.05, max_tip_length_to_length_ratio=0.5)
        arrs47 = VGroup(red1m("left"), red1m("right"), red1m("top"), red1m("bottom"))
        lbls1m = VGroup(*[poppins("1 m", 10, RED_C) for _ in range(4)])
        lbls1m[0].next_to(arrs47[0], UP, buff=0.03)
        lbls1m[1].next_to(arrs47[1], DOWN, buff=0.03)
        lbls1m[2].next_to(arrs47[2], LEFT, buff=0.03)
        lbls1m[3].next_to(arrs47[3], RIGHT, buff=0.03)
        pause47 = poppins("⏸", 28, DARK_NAVY).to_corner(DR, buff=0.4)

        with self.voiceover(
            text='<bookmark mark="b1"/>Here is a problem for you. '
                 '<bookmark mark="b2"/>A rectangular room is eight metres by '
                 'five metres. <bookmark mark="b3"/>A carpet covers the '
                 'centre, leaving a one-metre border all around. '
                 '<bookmark mark="b4"/>What is the area of the border?'
        ) as t:
            self.wait_until_bookmark("b1")
            self.play(FadeIn(card47), FadeIn(badge47), FadeIn(p47_l1[0]),
                      run_time=0.8)
            self.wait_until_bookmark("b2")
            self.play(FadeIn(p47_l1[1]), Create(out47), FadeIn(l8), FadeIn(l5),
                      run_time=0.9)
            self.wait_until_bookmark("b3")
            self.play(FadeIn(p47_l2), FadeIn(in47_grp),
                      FadeIn(arrs47), FadeIn(lbls1m), run_time=1.0)
            self.wait_until_bookmark("b4")
            self.play(FadeIn(p47_l3), FadeIn(pause47), run_time=0.7)
        self.wait(0.6)
        clear_all()

        # ========================================================
        # ROW 48 — Hidden condition revealed
        # ========================================================
        t48 = title_text("Hidden Condition Revealed")
        out48 = Rectangle(width=4.0, height=2.5, color=DARK_NAVY, stroke_width=3,
                          fill_color=TAN, fill_opacity=1)
        in48 = Rectangle(width=3.0, height=1.5, color=DARK_NAVY, stroke_width=2,
                         fill_color=WHITE, fill_opacity=1).move_to(out48.get_center())
        diag48 = VGroup(out48, in48).move_to(LEFT*1.5)
        in_top = poppins("8 − 1 − 1 = 6 m", 14, RED_C, BOLD).next_to(in48, UP, buff=0.1)
        in_right = poppins("5 − 1 − 1 = 3 m", 14, RED_C, BOLD).next_to(in48, RIGHT, buff=0.1)
        callout_body = poppins("Inner carpet is\nsix by four metres",
                               14, DARK_GREY)
        callout_card = make_card(callout_body, fill=PALE_YELLOW, border=LIGHT_GREY,
                                 border_width=1, pad=0.2, radius=0.1)
        callout_card.next_to(diag48, RIGHT, buff=1.0)
        bot48 = poppins("Structure: Outer − Inner (same pattern as the garden problem)",
                        14, DARK_GREY).to_edge(DOWN, buff=0.4)
        v48 = check_icon().scale(0.5).next_to(bot48, RIGHT, buff=0.3)

        with self.voiceover(
            text='<bookmark mark="b1"/>Identify the hidden condition and the '
                 'structural pattern. <bookmark mark="b2"/>If you saw that '
                 'the inner carpet is six by four metres, '
                 '<bookmark mark="b3"/>and recognised this as an outer-minus-'
                 'inner problem, <bookmark mark="b4"/>you have comprehended '
                 'it correctly.'
        ) as t:
            self.play(FadeIn(t48), run_time=0.5)
            self.wait_until_bookmark("b1")
            self.play(Create(diag48), run_time=0.9)
            self.wait_until_bookmark("b2")
            self.play(FadeIn(in_top), FadeIn(in_right),
                      FadeIn(callout_card), run_time=0.8)
            self.wait_until_bookmark("b3")
            self.play(FadeIn(bot48), run_time=0.6)
            self.wait_until_bookmark("b4")
            self.play(FadeIn(v48), run_time=0.5)
        self.wait(0.4)
        clear_all()

        # ========================================================
        # ROW 49 — Think before you solve
        # ========================================================
        t49 = title_text("Think Before You Solve")
        c1_49 = VGroup(
            poppins("🤔", 22, BLUE_C),
            poppins("Will the border be larger or smaller than the carpet?",
                    16, BLUE_C),
        ).arrange(RIGHT, buff=0.3)
        c1_49 = make_card(c1_49, fill=WHITE, border=BLUE_C,
                          border_width=2, pad=0.3, radius=0.15)
        c2_49 = VGroup(
            poppins("🤔", 22, BLUE_C),
            poppins("If the border were 2 m instead of 1 m, how would the carpet change?",
                    14, BLUE_C),
        ).arrange(RIGHT, buff=0.3)
        c2_49 = make_card(c2_49, fill=WHITE, border=BLUE_C,
                          border_width=2, pad=0.3, radius=0.15)
        cards49 = VGroup(c1_49, c2_49).arrange(DOWN, buff=0.4).move_to(ORIGIN)
        pause49 = VGroup(
            poppins("⏸", 24, DARK_GREY),
            poppins("Pause and think", 14, DARK_GREY),
        ).arrange(RIGHT, buff=0.2).to_edge(DOWN, buff=0.4)

        with self.voiceover(
            text='<bookmark mark="b1"/>Before you solve, answer this: '
                 '<bookmark mark="b2"/>will the border area be larger or '
                 'smaller than the carpet area? How do you know? '
                 '<bookmark mark="b3"/>And if the border were two metres '
                 'instead of one, would the inner carpet dimensions change '
                 'by the same amount? Why or why not?'
        ) as t:
            self.play(FadeIn(t49), run_time=0.5)
            self.wait_until_bookmark("b1")
            self.wait(0.2)
            self.wait_until_bookmark("b2")
            self.play(FadeIn(c1_49), run_time=0.8)
            self.wait_until_bookmark("b3")
            self.play(FadeIn(c2_49), FadeIn(pause49), run_time=0.9)
        self.wait(0.4)
        clear_all()

        # ========================================================
        # ROW 50 — Self check
        # ========================================================
        badge50_bg = RoundedRectangle(width=1.7, height=0.4, corner_radius=0.05,
                                      fill_color=DARK_NAVY, fill_opacity=1,
                                      stroke_width=0)
        badge50_txt = poppins("SELF-CHECK", 12, WHITE, BOLD)
        badge50 = VGroup(badge50_bg, badge50_txt)
        q1_body = VGroup(
            poppins("✏", 18, DARK_GREY),
            poppins("1. What does the area of a rectangle mean?",
                    16, DARK_GREY),
        ).arrange(RIGHT, buff=0.2)
        line1_50 = DashedLine(LEFT*2.5, RIGHT*2.5, color=DARK_GREY, dash_length=0.1, stroke_width=1)
        q1_grp = VGroup(q1_body, line1_50).arrange(DOWN, buff=0.15)
        q2_body = VGroup(
            poppins("✏", 18, DARK_GREY),
            poppins("2. When does the formula not apply?", 16, DARK_GREY),
        ).arrange(RIGHT, buff=0.2)
        line2_50 = DashedLine(LEFT*2.5, RIGHT*2.5, color=DARK_GREY, dash_length=0.1, stroke_width=1)
        q2_grp = VGroup(q2_body, line2_50).arrange(DOWN, buff=0.15)
        body50 = VGroup(q1_grp, q2_grp).arrange(DOWN, buff=0.4)
        card50 = make_card(body50, fill=VERY_PALE_BLUE, border=DARK_NAVY,
                           border_width=2, pad=0.4, radius=0.2)
        card50.move_to(ORIGIN)
        badge50.next_to(card50, UP, buff=-0.15).align_to(card50, LEFT).shift(RIGHT*0.3)
        cap50 = VGroup(
            poppins("Try to answer without looking back.", 14, DARK_GREY),
            poppins("⏸", 20, DARK_GREY),
        ).arrange(RIGHT, buff=0.3).to_edge(DOWN, buff=0.4)

        with self.voiceover(
            text='<bookmark mark="b1"/>Now, without looking back, '
                 '<bookmark mark="b2"/>describe in your own words: what does '
                 'the area of a rectangle mean, <bookmark mark="b3"/>and '
                 'when does the formula not apply?'
        ) as t:
            self.wait_until_bookmark("b1")
            self.play(FadeIn(card50), FadeIn(badge50), run_time=0.7)
            self.wait_until_bookmark("b2")
            self.play(FadeIn(q1_grp), run_time=0.7)
            self.wait_until_bookmark("b3")
            self.play(FadeIn(q2_grp), FadeIn(cap50), run_time=0.8)
        self.wait(0.4)
        clear_all()

        # ========================================================
        # ROW 51 — Full circle answer
        # ========================================================
        self.camera.background_color = SOFT_GREEN
        t51 = title_text("Full Circle: The Garden Problem Solved")
        garden51 = make_garden(scale=0.9).move_to(DOWN*0.3)
        ans_bg = RoundedRectangle(width=3.0, height=0.9, corner_radius=0.1,
                                  fill_color=BLUE_C, fill_opacity=1,
                                  stroke_color=WHITE, stroke_width=2)
        ans_txt = MathTex(r"120\,\text{m}^2", color=WHITE, font_size=42)
        ans_badge = VGroup(ans_bg, ans_txt).next_to(garden51, DOWN, buff=0.5)
        curved = CurvedArrow(garden51.get_bottom()+UP*0.1, ans_bg.get_top()+UP*0.1,
                             angle=-PI/3, color=DARK_GREY, stroke_width=2)
        cap51 = poppins("The answer: one hundred twenty square metres of tiles.",
                        16, DARK_GREY).to_edge(DOWN, buff=0.3)

        with self.voiceover(
            text='<bookmark mark="b1"/>At the beginning of this video, we '
                 'asked how many tiles you need for that fourteen-by-twelve-'
                 'metre patch with a two-metre path. '
                 '<bookmark mark="b2"/>Now, with what we have built, the '
                 'answer becomes clear: <bookmark mark="b3"/>one hundred '
                 'twenty square metres.'
        ) as t:
            self.play(FadeIn(t51), run_time=0.5)
            self.wait_until_bookmark("b1")
            self.play(FadeIn(garden51), run_time=1.0)
            self.wait_until_bookmark("b2")
            self.play(Create(curved), run_time=0.7)
            self.wait_until_bookmark("b3")
            self.play(FadeIn(ans_badge), FadeIn(cap51), run_time=0.9)
        self.wait(0.5)
        clear_all()
        self.camera.background_color = WHITE

        # ========================================================
        # ROW 52 — Problem-solving checklist
        # ========================================================
        t52 = title_text("Problem-Solving Checklist")
        labels52 = ["Read","Extract","Identify","Map","Plan","Solve","Verify"]
        fills52 = [PALE_BLUE, SOFT_GREEN, PALE_BLUE, SOFT_GREEN,
                   PALE_BLUE, SOFT_GREEN, PALE_BLUE]
        nodes52 = VGroup()
        for i,(lab,col) in enumerate(zip(labels52, fills52)):
            c = Circle(radius=0.32, color=DARK_NAVY, stroke_width=2,
                       fill_color=col, fill_opacity=1)
            n = poppins(str(i+1), 16, DARK_NAVY, BOLD).move_to(c.get_center())
            l = poppins(lab, 12, DARK_GREY).next_to(c, DOWN, buff=0.2)
            nodes52.add(VGroup(c, n, l))
        nodes52.arrange(RIGHT, buff=0.45).move_to(ORIGIN)
        arrows52 = VGroup()
        for i in range(6):
            a = Arrow(nodes52[i][0].get_right(), nodes52[i+1][0].get_left(),
                      color=DARK_GREY, stroke_width=1.5,
                      buff=0.05, max_tip_length_to_length_ratio=0.3)
            arrows52.add(a)
        cap52 = poppins("This checklist works for every rectangle problem.",
                        14, DARK_GREY).to_edge(DOWN, buff=0.5)

        with self.voiceover(
            text='<bookmark mark="b1"/>The concept of rectangular area is '
                 'what made that answer possible. <bookmark mark="b2"/>'
                 'Remember: read, extract, identify, map, plan, solve, '
                 'verify.'
        ) as t:
            self.play(FadeIn(t52), run_time=0.5)
            self.wait_until_bookmark("b1")
            self.wait(0.3)
            self.wait_until_bookmark("b2")
            for i, n in enumerate(nodes52):
                if i == 0:
                    self.play(FadeIn(n), run_time=0.3)
                else:
                    self.play(Create(arrows52[i-1]), FadeIn(n), run_time=0.3)
            self.play(FadeIn(cap52), run_time=0.5)
        self.wait(0.4)
        clear_all()

        # ========================================================
        # ROW 53 — Principle over procedure
        # ========================================================
        # Left faded
        left_bg53 = Rectangle(width=6.0, height=5.0, color=LIGHT_GREY,
                              fill_color=LIGHT_GREY, fill_opacity=0.3, stroke_width=0)
        left_bg53.move_to(LEFT*3.3)
        lt53 = poppins("Path Procedure", 14, DARK_GREY).move_to(left_bg53.get_top()+DOWN*0.3)
        mini_plan_53 = VGroup(
            poppins("1. Outer dimensions", 11, DARK_GREY),
            poppins("2. Outer area", 11, DARK_GREY),
            poppins("3. Inner area", 11, DARK_GREY),
            poppins("4. Subtract", 11, DARK_GREY),
        ).arrange(DOWN, buff=0.15).set_opacity(0.6).move_to(left_bg53.get_center())
        l53_cap = VGroup(
            poppins("🔓", 18, DARK_GREY),
            poppins("Can be reconstructed — no need to memorise",
                    11, DARK_GREY),
        ).arrange(RIGHT, buff=0.15).next_to(mini_plan_53, DOWN, buff=0.4)
        # Right highlighted
        right_bg53 = Rectangle(width=6.0, height=5.0, color=SOFT_GREEN,
                               fill_color=SOFT_GREEN, fill_opacity=0.7, stroke_width=0)
        right_bg53.move_to(RIGHT*3.3)
        rt53 = poppins("Comprehension Checklist", 14, DARK_NAVY, BOLD).move_to(right_bg53.get_top()+DOWN*0.3)
        mini_flow = VGroup(*[
            VGroup(
                Circle(radius=0.15, color=DARK_NAVY, stroke_width=1,
                       fill_color=PALE_BLUE if i%2==0 else SOFT_GREEN, fill_opacity=1),
                poppins(s, 9, DARK_GREY)
            ).arrange(DOWN, buff=0.05)
            for i,s in enumerate(["Read","Extract","Identify","Map","Plan","Solve","Verify"])
        ]).arrange(RIGHT, buff=0.15).scale(0.85).move_to(right_bg53.get_center()+UP*0.2)
        r53_cap = VGroup(
            poppins("🧠", 18, DARK_GREEN),
            poppins("Commit this to memory ✓", 12, DARK_GREEN, BOLD),
        ).arrange(RIGHT, buff=0.15).next_to(mini_flow, DOWN, buff=0.6)
        bottom53 = poppins("Principle over procedure.", 18, DARK_NAVY, BOLD).to_edge(DOWN, buff=0.3)

        with self.voiceover(
            text='<bookmark mark="b1"/>You do not need to memorise the path '
                 'procedure. <bookmark mark="b2"/>You can always reconstruct '
                 'it from the rectangle area principle. '
                 '<bookmark mark="b3"/>But do commit the comprehension '
                 'checklist to memory.'
        ) as t:
            self.wait_until_bookmark("b1")
            self.play(FadeIn(left_bg53), FadeIn(lt53), FadeIn(mini_plan_53),
                      FadeIn(l53_cap), run_time=1.0)
            self.wait_until_bookmark("b2")
            self.wait(0.2)
            self.wait_until_bookmark("b3")
            self.play(FadeIn(right_bg53), FadeIn(rt53), FadeIn(mini_flow),
                      FadeIn(r53_cap), FadeIn(bottom53), run_time=1.2)
        self.wait(0.4)
        clear_all()

        # ========================================================
        # ROW 54 — Concept map
        # ========================================================
        central54 = Rectangle(width=3.0, height=1.0, color=DARK_NAVY, stroke_width=3,
                              fill_color=PALE_BLUE, fill_opacity=1).move_to(ORIGIN)
        central_lbl54 = poppins("Rectangle Area", 18, DARK_NAVY, BOLD).move_to(central54.get_center())
        br1 = Rectangle(width=2.6, height=0.8, color=DARK_NAVY, stroke_width=2,
                        fill_color=PALE_BLUE, fill_opacity=1).move_to(UR*2.5)
        br1_l = MathTex(r"\text{Formula: } L \times B", color=DARK_NAVY,
                        font_size=18).move_to(br1.get_center())
        br2 = Rectangle(width=2.6, height=0.8, color=DARK_NAVY, stroke_width=2,
                        fill_color=SOFT_GREEN, fill_opacity=1).move_to(DR*2.5)
        br2_l = MathTex(r"\text{Units: } cm^2, m^2", color=DARK_NAVY,
                        font_size=18).move_to(br2.get_center())
        br3 = Rectangle(width=2.6, height=0.8, color=DARK_NAVY, stroke_width=2,
                        fill_color=PALE_YELLOW, fill_opacity=1).move_to(DL*2.5)
        br3_l = MathTex(r"\text{Square: } s \times s", color=DARK_NAVY,
                        font_size=18).move_to(br3.get_center())
        br4 = Rectangle(width=2.6, height=0.8, color=DARK_NAVY, stroke_width=2,
                        fill_color=TAN, fill_opacity=1).move_to(UL*2.5)
        br4_l = poppins("Composite Figures", 14, DARK_NAVY, BOLD).move_to(br4.get_center())
        lines54 = VGroup(
            Line(central54.get_corner(UR), br1.get_corner(DL), color=DARK_GREY, stroke_width=1.5),
            Line(central54.get_corner(DR), br2.get_corner(UL), color=DARK_GREY, stroke_width=1.5),
            Line(central54.get_corner(DL), br3.get_corner(UR), color=DARK_GREY, stroke_width=1.5),
            Line(central54.get_corner(UL), br4.get_corner(DR), color=DARK_GREY, stroke_width=1.5),
        )
        banner54_bg = RoundedRectangle(width=6.5, height=0.7, corner_radius=0.1,
                                       fill_color=YELLOW_C, fill_opacity=1,
                                       stroke_width=0)
        banner54_txt = poppins("Comprehend before you compute.",
                               18, DARK_NAVY, BOLD)
        banner54 = VGroup(banner54_bg, banner54_txt).to_edge(DOWN, buff=0.9)
        cap54 = poppins("Practice with the checklist → confidence.",
                        14, DARK_GREY).next_to(banner54, DOWN, buff=0.2)

        with self.voiceover(
            text='<bookmark mark="b1"/>You have built a genuine understanding '
                 'of rectangular area today. <bookmark mark="b2"/>More '
                 'importantly, you now possess a systematic way to approach '
                 'any problem on this topic. <bookmark mark="b3"/>That '
                 'skill — the ability to comprehend before you compute — is '
                 'what separates confident problem-solvers from those who '
                 'struggle. <bookmark mark="b4"/>Practice with that '
                 'checklist, and this concept will become a tool you wield '
                 'with confidence.'
        ) as t:
            self.wait_until_bookmark("b1")
            self.play(Create(central54), FadeIn(central_lbl54), run_time=0.8)
            self.wait_until_bookmark("b2")
            self.play(Create(lines54),
                      Create(br1), FadeIn(br1_l),
                      Create(br2), FadeIn(br2_l),
                      Create(br3), FadeIn(br3_l),
                      Create(br4), FadeIn(br4_l),
                      run_time=1.5)
            self.wait_until_bookmark("b3")
            self.play(FadeIn(banner54), run_time=0.7)
            self.wait_until_bookmark("b4")
            self.play(FadeIn(cap54), run_time=0.6)
        self.wait(0.6)
        clear_all()

        # ========================================================
        # ROW 55 — Coming next teaser
        # ========================================================
        rect55 = Rectangle(width=2.0, height=1.4, color=DARK_NAVY, stroke_width=3,
                           fill_color=PALE_BLUE, fill_opacity=1).move_to(LEFT*3.5)
        arr55 = Arrow(rect55.get_right()+RIGHT*0.3, RIGHT*1.0,
                      color=DARK_GREY, stroke_width=2, buff=0.1)
        tri55 = DashedVMobject(Polygon([0,0.7,0],[0.7,-0.5,0],[-0.7,-0.5,0],
                                         color=DARK_GREY, stroke_width=2))
        para55 = DashedVMobject(Polygon([-0.6,0.4,0],[0.8,0.4,0],
                                          [0.4,-0.4,0],[-1.0,-0.4,0],
                                          color=DARK_GREY, stroke_width=2))
        irr55 = DashedVMobject(Polygon([0,0.5,0],[0.7,0.2,0],[0.5,-0.5,0],
                                         [-0.5,-0.4,0],[-0.6,0.1,0],
                                         color=DARK_GREY, stroke_width=2))
        shapes55 = VGroup(tri55, para55, irr55).arrange(RIGHT, buff=0.4).move_to(RIGHT*3.5)
        qs = VGroup(*[poppins("?", 22, DARK_GREY, BOLD).move_to(s.get_center())
                      for s in shapes55])
        q55 = poppins("What happens when the shape is not a rectangle?",
                      16, DARK_GREY).to_edge(DOWN, buff=1.0)
        cn = VGroup(
            poppins("Coming next…", 20, DARK_NAVY, BOLD),
            poppins("→", 22, DARK_NAVY, BOLD),
        ).arrange(RIGHT, buff=0.2).to_edge(DOWN, buff=0.4)

        with self.voiceover(
            text='<bookmark mark="b1"/>But consider this: what happens when '
                 'the shape is not a rectangle? <bookmark mark="b2"/>That is '
                 'what we will explore next.'
        ) as t:
            self.wait_until_bookmark("b1")
            self.play(Create(rect55), run_time=0.7)
            self.play(Create(arr55), Create(shapes55), FadeIn(qs), run_time=1.0)
            self.play(FadeIn(q55), run_time=0.6)
            self.wait_until_bookmark("b2")
            self.play(FadeIn(cn), run_time=0.7)
        self.wait(0.8)
        clear_all(rt=1.0)