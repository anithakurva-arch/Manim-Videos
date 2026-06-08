from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.openai import OpenAIService

# Coschool Color Palette
LAVENDER_BG = "#E7E5F3"
PURPLE      = "#7464CE"
ORANGE_HL   = "#FF9302"
PALE_PURPLE = "#9495D7"

TTS_INSTRUCTIONS = """
Voice & Personality:
You are a warm, patient, and encouraging math teacher speaking to a 
middle-school student. Your tone is friendly, calm, and confident — 
never rushed, never robotic. You sound like a human explainer in a 
Khan Academy or 3Blue1Brown style video.

Pacing:
Speak at a MODERATE-TO-SLOW pace. Prioritize clarity over speed. 
Every word must be clearly heard and mentally absorbed by the student. 
Do NOT race through sentences. Allow the listener to follow along 
with the visual on screen.

Variables and Math Terms:
When pronouncing single-letter variables like x, y, z, a, b, c, h, r, 
or t, slow down noticeably and articulate each letter clearly with a 
brief micro-pause before and after it. Treat each variable as an 
important named character in the explanation.

Formulas:
When reading a formula or equation, slow your pace even further. 
Pause briefly between each component of the formula so the student 
can match the spoken word to the symbol on screen.

Numbers and Units:
Pronounce numbers clearly. For units like "centimeter square" or 
"meter cube," say them with a confident, deliberate cadence — never 
mumbled or rushed.

Emphasis:
Naturally emphasize key terms: the name of the shape, the formula 
being introduced, the final answer, and any word that introduces a 
new concept. Use gentle stress, not loudness.

Pauses:
Add a natural beat (short pause) at commas, and a slightly longer 
pause at periods. After stating a final answer, pause for a moment 
before continuing.

Mood:
Encouraging, curious, and warm. You want the student to succeed and 
feel confident. Avoid monotone delivery.

Do NOT:
- Do not speak in a rushed, news-anchor tone.
- Do not flatten your voice into monotone.
- Do not add filler words, sounds, or commentary not in the script.
- Do not improvise or paraphrase — read the script exactly as written.
"""


def make_badge(text_str):
    t = Text(text_str, font="Poppins", font_size=28, color=WHITE, weight=BOLD)
    bg = RoundedRectangle(
        corner_radius=0.2,
        width=t.width + 0.6, height=t.height + 0.3,
        fill_color=PURPLE, fill_opacity=1, stroke_width=0,
    )
    bg.move_to(t)
    return VGroup(bg, t).to_corner(UL, buff=0.3)


def dim_arrow(start, end, label_str, direction=DOWN, buff_amt=0.15):
    arrow = DoubleArrow(
        start=start, end=end,
        color=PURPLE, stroke_width=2, tip_length=0.18, buff=0,
    )
    label = Text(label_str, font="Poppins", font_size=22, color=PURPLE)
    label.next_to(arrow.get_center(), direction, buff=buff_amt)
    return arrow, label


def unknown_mark(position):
    return Text("?", font="Poppins", font_size=36,
                color=ORANGE_HL, weight=BOLD).move_to(position)


class TrapeziumRhombus(VoiceoverScene):
    def construct(self):
        self.camera.background_color = LAVENDER_BG
        self.set_speech_service(
            OpenAIService(
                voice="nova",
                model="gpt-4o-mini-tts",
                transcription_model="medium",
                instructions=TTS_INSTRUCTIONS,
            ),
            create_subcaption=False,
        )

        # --- SCENE 1: Title Slide ---
        title_bg = Rectangle(
            width=config.frame_width, height=config.frame_height,
            fill_color=PURPLE, fill_opacity=1, stroke_width=0,
        )
        title = Text("Trapezium & Rhombus", font="Poppins", font_size=72,
                     color=WHITE, weight=BOLD).move_to(ORIGIN)

        # Show title first, then narrate (no leading bookmark issue)
        self.play(FadeIn(title_bg), FadeIn(title), run_time=1.0)
        self.wait(0.3)
        with self.voiceover(
            text='Hello students! Today we will explore the trapezium and its area.'
        ) as tracker:
            pass
        self.wait(0.5)
        self.play(FadeOut(title_bg), FadeOut(title), run_time=0.8)

        # --- SCENE 2: Trapezium Definition ---
        heading = make_badge("Trapezium")
        self.play(FadeIn(heading), run_time=0.6)

        W = np.array([-1.2, 0.9, 0])
        X = np.array([1.6, 0.9, 0])
        Y = np.array([2.6, -1.4, 0])
        Z = np.array([-2.2, -1.4, 0])

        side_top = Line(W, X, color=PURPLE, stroke_width=2.5)
        side_right = Line(X, Y, color=PURPLE, stroke_width=2.5)
        side_bot = Line(Z, Y, color=PURPLE, stroke_width=2.5)
        side_left = Line(Z, W, color=PURPLE, stroke_width=2.5)
        trap = VGroup(side_top, side_right, side_bot, side_left).shift(DOWN*0.2)

        with self.voiceover(
            text='A trapezium is a <bookmark mark="bk_shape"/>quadrilateral '
                 'in which exactly one pair of opposite sides is parallel to each other.'
        ) as tracker:
            self.wait_until_bookmark("bk_shape")
            self.play(Create(trap), run_time=1.3)

        bases_lbl = Text("Bases", font="Poppins", font_size=22,
                         color=ORANGE_HL, weight=BOLD).next_to(side_bot, DOWN, buff=0.4)
        with self.voiceover(
            text='The <bookmark mark="bk_par"/>parallel sides are called '
                 '<bookmark mark="bk_blbl"/>the bases.'
        ) as tracker:
            self.wait_until_bookmark("bk_par")
            self.play(side_top.animate.set_color(ORANGE_HL),
                      side_bot.animate.set_color(ORANGE_HL), run_time=0.6)
            self.wait_until_bookmark("bk_blbl")
            self.play(FadeIn(bases_lbl), run_time=0.5)

        legs_lbl = Text("Legs", font="Poppins", font_size=22,
                        color=ORANGE_HL, weight=BOLD).next_to(side_right, RIGHT, buff=0.3)
        with self.voiceover(
            text='The <bookmark mark="bk_leg"/>non-parallel sides are called '
                 '<bookmark mark="bk_llbl"/>the legs.'
        ) as tracker:
            self.wait_until_bookmark("bk_leg")
            self.play(side_top.animate.set_color(PURPLE),
                      side_bot.animate.set_color(PURPLE),
                      side_left.animate.set_color(ORANGE_HL),
                      side_right.animate.set_color(ORANGE_HL),
                      FadeOut(bases_lbl), run_time=0.6)
            self.wait_until_bookmark("bk_llbl")
            self.play(FadeIn(legs_lbl), run_time=0.5)

        top_mid = (W + X) / 2 + DOWN*0.2
        bot_mid = np.array([top_mid[0], (Z+Y)[1]/2 + (-0.2), 0])
        height_line = DashedLine(top_mid, bot_mid, color=ORANGE_HL, stroke_width=2.5)
        height_lbl = Text("Height", font="Poppins", font_size=22,
                          color=ORANGE_HL, weight=BOLD).next_to(height_line, RIGHT, buff=0.15)

        with self.voiceover(
            text='The <bookmark mark="bk_h"/>perpendicular distance between '
                 'the parallel sides is called '
                 '<bookmark mark="bk_hlbl"/>the height of the trapezium.'
        ) as tracker:
            self.wait_until_bookmark("bk_h")
            self.play(side_left.animate.set_color(PURPLE),
                      side_right.animate.set_color(PURPLE),
                      FadeOut(legs_lbl),
                      Create(height_line), run_time=0.7)
            self.wait_until_bookmark("bk_hlbl")
            self.play(FadeIn(height_lbl), run_time=0.5)

        iso_note = Text("Isosceles: legs are equal",
                        font="Poppins", font_size=22, color=PURPLE).to_edge(DOWN, buff=0.6)
        with self.voiceover(
            text='An <bookmark mark="bk_iso"/>isosceles trapezium is a special type '
                 'where the two legs are equal in length.'
        ) as tracker:
            self.wait_until_bookmark("bk_iso")
            self.play(FadeIn(iso_note), run_time=0.7)

        self.wait(0.4)
        self.play(FadeOut(height_line), FadeOut(height_lbl),
                  FadeOut(iso_note), run_time=0.6)

        # --- SCENE 3: Derivation ---
        new_head = make_badge("Area Derivation")
        self.play(FadeOut(heading), FadeIn(new_head), run_time=0.7)
        heading = new_head

        with self.voiceover(
            text='Now <bookmark mark="bk_d"/>let us derive the area formula.'
        ) as tracker:
            self.wait_until_bookmark("bk_d")
            self.wait(0.2)

        W_lbl = Text("W", font="Poppins", font_size=22, color=PURPLE).next_to(W + DOWN*0.2, UL, buff=0.05)
        X_lbl = Text("X", font="Poppins", font_size=22, color=PURPLE).next_to(X + DOWN*0.2, UR, buff=0.05)
        Y_lbl = Text("Y", font="Poppins", font_size=22, color=PURPLE).next_to(Y + DOWN*0.2, DR, buff=0.05)
        Z_lbl = Text("Z", font="Poppins", font_size=22, color=PURPLE).next_to(Z + DOWN*0.2, DL, buff=0.05)
        a_lbl = MathTex("a", color=PURPLE, font_size=30).next_to(side_top, UP, buff=0.1)
        b_lbl = MathTex("b", color=PURPLE, font_size=30).next_to(side_bot, DOWN, buff=0.1)

        with self.voiceover(
            text='Consider <bookmark mark="bk_vert"/>trapezium W X Y Z '
                 '<bookmark mark="bk_par2"/>with W X parallel to Z Y, '
                 'where W X equals <bookmark mark="bk_a"/>a '
                 'and Z Y equals <bookmark mark="bk_b"/>b.'
        ) as tracker:
            self.wait_until_bookmark("bk_vert")
            self.play(FadeIn(W_lbl), FadeIn(X_lbl), FadeIn(Y_lbl), FadeIn(Z_lbl), run_time=0.7)
            self.wait_until_bookmark("bk_par2")
            self.play(Indicate(side_top, color=ORANGE_HL),
                      Indicate(side_bot, color=ORANGE_HL), run_time=0.6)
            self.wait_until_bookmark("bk_a")
            self.play(FadeIn(a_lbl), run_time=0.5)
            self.wait_until_bookmark("bk_b")
            self.play(FadeIn(b_lbl), run_time=0.5)

        M = np.array([W[0], (Z+Y)[1]/2, 0]) + DOWN*0.2
        N = np.array([X[0], (Z+Y)[1]/2, 0]) + DOWN*0.2
        W_off = W + DOWN*0.2
        X_off = X + DOWN*0.2
        Z_off = Z + DOWN*0.2
        Y_off = Y + DOWN*0.2

        perp_W = DashedLine(W_off, M, color=PURPLE, stroke_width=2)
        perp_X = DashedLine(X_off, N, color=PURPLE, stroke_width=2)

        with self.voiceover(
            text='Drop <bookmark mark="bk_drop"/>perpendiculars from W and X to Z Y,'
        ) as tracker:
            self.wait_until_bookmark("bk_drop")
            self.play(Create(perp_W), Create(perp_X), run_time=1.0)

        rect_WXNM = Polygon(W_off, X_off, N, M, color=ORANGE_HL,
                            fill_color=ORANGE_HL, fill_opacity=0.15, stroke_width=0)
        M_lbl = Text("M", font="Poppins", font_size=20, color=PURPLE).next_to(M, DL, buff=0.05)
        N_lbl = Text("N", font="Poppins", font_size=20, color=PURPLE).next_to(N, DR, buff=0.05)

        with self.voiceover(
            text='creating <bookmark mark="bk_rect"/>a rectangle W X N M'
        ) as tracker:
            self.wait_until_bookmark("bk_rect")
            self.play(FadeIn(rect_WXNM), FadeIn(M_lbl), FadeIn(N_lbl), run_time=0.8)

        tri_L = Polygon(Z_off, W_off, M, color=ORANGE_HL,
                        fill_color=ORANGE_HL, fill_opacity=0.15, stroke_width=0)
        tri_R = Polygon(N, X_off, Y_off, color=ORANGE_HL,
                        fill_color=ORANGE_HL, fill_opacity=0.15, stroke_width=0)

        with self.voiceover(
            text='and <bookmark mark="bk_tri"/>two triangles.'
        ) as tracker:
            self.wait_until_bookmark("bk_tri")
            self.play(FadeIn(tri_L), FadeIn(tri_R), run_time=0.8)

        x_arrow, x_lbl_d = dim_arrow(Z_off + DOWN*0.4, M + DOWN*0.4, "x", DOWN)
        y_arrow, y_lbl_d = dim_arrow(N + DOWN*0.4, Y_off + DOWN*0.4, "y", DOWN)
        h_arrow_d, h_lbl_d = dim_arrow(W_off + LEFT*0.4, M + LEFT*0.4, "h", LEFT)

        with self.voiceover(
            text='Let <bookmark mark="bk_x"/>M Z equals x, '
                 '<bookmark mark="bk_y"/>N Y equals y, '
                 'and <bookmark mark="bk_hd"/>height equals h.'
        ) as tracker:
            self.wait_until_bookmark("bk_x")
            self.play(Create(x_arrow), FadeIn(x_lbl_d), run_time=0.7)
            self.wait_until_bookmark("bk_y")
            self.play(Create(y_arrow), FadeIn(y_lbl_d), run_time=0.7)
            self.wait_until_bookmark("bk_hd")
            self.play(Create(h_arrow_d), FadeIn(h_lbl_d), run_time=0.7)

        figure_grp = VGroup(trap, W_lbl, X_lbl, Y_lbl, Z_lbl, a_lbl, b_lbl,
                            perp_W, perp_X, rect_WXNM, tri_L, tri_R,
                            M_lbl, N_lbl, x_arrow, x_lbl_d, y_arrow, y_lbl_d,
                            h_arrow_d, h_lbl_d)

        eq1 = MathTex(r"A = \tfrac{1}{2}hx + ha + \tfrac{1}{2}hy",
                      color=PURPLE, font_size=32)
        eq1.to_edge(LEFT, buff=0.7).shift(UP*1.0)

        with self.voiceover(
            text='The <bookmark mark="bk_shift"/>total area becomes '
                 '<bookmark mark="bk_eq1"/>one half h x plus h a plus one half h y'
        ) as tracker:
            self.wait_until_bookmark("bk_shift")
            self.play(figure_grp.animate.scale(0.7).to_edge(RIGHT, buff=0.6), run_time=1.0)
            self.wait_until_bookmark("bk_eq1")
            self.play(FadeIn(eq1), run_time=0.8)

        eq2 = MathTex(r"= \tfrac{1}{2}h(x + y + 2a)", color=PURPLE, font_size=32)
        eq2.next_to(eq1, DOWN, buff=0.35).align_to(eq1, LEFT)
        with self.voiceover(
            text='equals <bookmark mark="bk_eq2"/>one half h times open paren '
                 'x plus y plus 2 a close paren.'
        ) as tracker:
            self.wait_until_bookmark("bk_eq2")
            self.play(FadeIn(eq2), run_time=0.8)

        eq3 = MathTex(r"b = x + y + a \;\Rightarrow\; x + y = b - a",
                      color=PURPLE, font_size=28)
        eq3.next_to(eq2, DOWN, buff=0.35).align_to(eq1, LEFT)
        with self.voiceover(
            text='Since <bookmark mark="bk_eq3"/>b equals x plus y plus a, '
                 'we get x plus y equals b minus a.'
        ) as tracker:
            self.wait_until_bookmark("bk_eq3")
            self.play(eq1.animate.set_opacity(0.4),
                      eq2.animate.set_opacity(0.4),
                      FadeIn(eq3), run_time=0.9)

        final_formula = MathTex(r"A = \tfrac{1}{2} \times h \times (a + b)",
                                color=ORANGE_HL, font_size=36)
        final_formula.next_to(eq3, DOWN, buff=0.5).align_to(eq1, LEFT)
        formula_box = SurroundingRectangle(final_formula, color=ORANGE_HL,
                                           corner_radius=0.15, buff=0.2, stroke_width=3)
        with self.voiceover(
            text='Substituting <bookmark mark="bk_fin"/>gives us, '
                 'Area equals one half times h times open paren a plus b close paren.'
        ) as tracker:
            self.wait_until_bookmark("bk_fin")
            self.play(eq3.animate.set_opacity(0.4),
                      FadeIn(final_formula), Create(formula_box), run_time=1.0)

        self.wait(0.6)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

        # --- SCENE 4: Two Copies Method ---
        heading = make_badge("Two Copies Method")
        self.play(FadeIn(heading), run_time=0.6)

        with self.voiceover(
            text='The <bookmark mark="bk_tc"/>two copies method '
                 'confirms this beautifully.'
        ) as tracker:
            self.wait_until_bookmark("bk_tc")
            self.wait(0.2)

        T1 = Polygon(
            np.array([-1.0, -0.8, 0]),
            np.array([1.0, -0.8, 0]),
            np.array([0.5, 0.8, 0]),
            np.array([-0.5, 0.8, 0]),
            color=PURPLE, stroke_width=2.5,
            fill_color=PURPLE, fill_opacity=0.1,
        ).shift(LEFT*2 + DOWN*0.3)
        T2 = T1.copy().set_fill(opacity=0.15).shift(RIGHT*4)

        with self.voiceover(
            text='Take <bookmark mark="bk_t1"/>two identical trapeziums'
        ) as tracker:
            self.wait_until_bookmark("bk_t1")
            self.play(Create(T1), Create(T2), run_time=1.2)

        with self.voiceover(
            text='and <bookmark mark="bk_rot"/>rotate the second copy,'
        ) as tracker:
            self.wait_until_bookmark("bk_rot")
            self.play(Rotate(T2, PI, about_point=T2.get_center()), run_time=1.0)

        with self.voiceover(
            text='then <bookmark mark="bk_join"/>join them along a '
                 'non-parallel side.'
        ) as tracker:
            self.wait_until_bookmark("bk_join")
            self.play(T2.animate.next_to(T1, RIGHT, buff=0), run_time=1.2)

        ang_lbl = MathTex(r"180^\circ", color=ORANGE_HL, font_size=28)
        ang_lbl.next_to(T1.get_right(), UP*0.3)
        with self.voiceover(
            text='Because the <bookmark mark="bk_ang"/>co-interior angles '
                 'sum to 180 degrees,'
        ) as tracker:
            self.wait_until_bookmark("bk_ang")
            self.play(FadeIn(ang_lbl), run_time=0.7)

        combined = VGroup(T1, T2)
        base_arrow, base_lbl = dim_arrow(
            combined.get_corner(DL) + DOWN*0.3,
            combined.get_corner(DR) + DOWN*0.3,
            "a + b", DOWN
        )
        h_arrow2, h_lbl2 = dim_arrow(
            combined.get_corner(UL) + LEFT*0.3,
            combined.get_corner(DL) + LEFT*0.3,
            "h", LEFT
        )

        with self.voiceover(
            text='the <bookmark mark="bk_pgram"/>combined figure forms a '
                 'parallelogram with base open paren a plus b close paren '
                 '<bookmark mark="bk_hh"/>and height h.'
        ) as tracker:
            self.wait_until_bookmark("bk_pgram")
            self.play(Create(base_arrow), FadeIn(base_lbl), run_time=0.8)
            self.wait_until_bookmark("bk_hh")
            self.play(Create(h_arrow2), FadeIn(h_lbl2), run_time=0.7)

        confirm = MathTex(r"A = \tfrac{1}{2} \times h \times (a + b)",
                          color=ORANGE_HL, font_size=36).to_edge(UP, buff=1.4)
        confirm_box = SurroundingRectangle(confirm, color=ORANGE_HL,
                                           corner_radius=0.15, buff=0.2, stroke_width=3)
        with self.voiceover(
            text='The <bookmark mark="bk_half"/>trapezium is exactly half '
                 'this parallelogram, so Area equals one half times h times '
                 'open paren a plus b close paren.'
        ) as tracker:
            self.wait_until_bookmark("bk_half")
            self.play(FadeIn(confirm), Create(confirm_box), run_time=1.0)

        self.wait(0.6)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

        # --- SCENE 5: Trapezium Example ---
        heading = make_badge("Example")
        self.play(FadeIn(heading), run_time=0.5)

        q_text = Text(
            "A trapezium has parallel sides of 18 m and 30 m,\n"
            "and a height of 10 m. Find its area.",
            font="Poppins", font_size=24, color=PURPLE, line_spacing=1.0,
        ).to_edge(UP, buff=1.3)

        ex_W = np.array([-1.0, 0.2, 0])
        ex_X = np.array([1.0, 0.2, 0])
        ex_Y = np.array([2.0, -1.5, 0])
        ex_Z = np.array([-2.0, -1.5, 0])
        ex_trap = Polygon(ex_W, ex_X, ex_Y, ex_Z, color=PURPLE, stroke_width=2.5)
        ex_trap.shift(DOWN*0.5)

        a_arr, a_lbl_ex = dim_arrow(ex_W + UP*0.3 + DOWN*0.5,
                                     ex_X + UP*0.3 + DOWN*0.5, "18 m", UP)
        b_arr, b_lbl_ex = dim_arrow(ex_Z + DOWN*0.3 + DOWN*0.5,
                                     ex_Y + DOWN*0.3 + DOWN*0.5, "30 m", DOWN)
        h_arr_ex, h_lbl_ex = dim_arrow(ex_W + LEFT*0.4 + DOWN*0.5,
                                         np.array([ex_W[0], ex_Z[1], 0]) + LEFT*0.4 + DOWN*0.5,
                                         "10 m", LEFT)

        with self.voiceover(
            text='Now <bookmark mark="bk_app"/>let us apply this formula. '
                 'A trapezium has <bookmark mark="bk_q"/>parallel sides of '
                 '18 meters and 30 meters, <bookmark mark="bk_fig"/>and a '
                 'height of 10 meters. Find its area.'
        ) as tracker:
            self.wait_until_bookmark("bk_app")
            self.wait(0.2)
            self.wait_until_bookmark("bk_q")
            self.play(FadeIn(q_text), run_time=0.8)
            self.wait_until_bookmark("bk_fig")
            self.play(Create(ex_trap),
                      Create(a_arr), FadeIn(a_lbl_ex),
                      Create(b_arr), FadeIn(b_lbl_ex),
                      Create(h_arr_ex), FadeIn(h_lbl_ex),
                      run_time=1.4)

        unk = unknown_mark(ex_trap.get_center())
        self.play(FadeIn(unk), run_time=0.5)
        self.wait(0.3)

        # Transition to solution
        figure_ex = VGroup(ex_trap, a_arr, a_lbl_ex, b_arr, b_lbl_ex,
                           h_arr_ex, h_lbl_ex, unk)
        new_head = make_badge("Solution")
        self.play(FadeOut(heading), FadeIn(new_head),
                  FadeOut(q_text),
                  figure_ex.animate.scale(0.8).to_edge(RIGHT, buff=0.7),
                  run_time=1.0)
        heading = new_head

        with self.voiceover(text='Solution.') as tracker:
            pass

        sol_formula = MathTex(r"A = \tfrac{1}{2} \times h \times (a + b)",
                              color=PURPLE, font_size=32)
        sol_formula.to_edge(LEFT, buff=0.8).shift(UP*1.5)
        with self.voiceover(
            text='Area equals <bookmark mark="bk_sf"/>one half times h times '
                 'open paren a plus b close paren.'
        ) as tracker:
            self.wait_until_bookmark("bk_sf")
            self.play(FadeIn(sol_formula), run_time=0.8)

        sub1 = MathTex(r"A = \tfrac{1}{2} \times 10 \times (18 + 30)",
                       color=PURPLE, font_size=32)
        sub1.next_to(sol_formula, DOWN, buff=0.4).align_to(sol_formula, LEFT)
        with self.voiceover(
            text='Area equals <bookmark mark="bk_sub"/>one half times 10 times '
                 'open paren 18 plus 30 close paren.'
        ) as tracker:
            self.wait_until_bookmark("bk_sub")
            self.play(FadeIn(sub1), run_time=0.9)

        sub2 = MathTex(r"A = 5 \times 48", color=PURPLE, font_size=32)
        sub2.next_to(sub1, DOWN, buff=0.4).align_to(sol_formula, LEFT)
        with self.voiceover(
            text='Area equals <bookmark mark="bk_s2"/>5 times 48.'
        ) as tracker:
            self.wait_until_bookmark("bk_s2")
            self.play(sol_formula.animate.set_opacity(0.4),
                      sub1.animate.set_opacity(0.4),
                      FadeIn(sub2), run_time=0.7)

        ans = MathTex(r"A = 240 \, \text{m}^2", color=ORANGE_HL, font_size=40)
        ans.next_to(sub2, DOWN, buff=0.5).align_to(sol_formula, LEFT)
        with self.voiceover(
            text='Area equals <bookmark mark="bk_ans"/>240 meter square.'
        ) as tracker:
            self.wait_until_bookmark("bk_ans")
            self.play(sub2.animate.set_opacity(0.4),
                      FadeOut(unk),
                      FadeIn(ans), run_time=0.9)

        self.wait(0.7)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

        # --- SCENE 6: Rhombus ---
        heading = make_badge("Rhombus")
        self.play(FadeIn(heading), run_time=0.6)

        rA = np.array([0, 1.5, 0])
        rB = np.array([2, 0, 0])
        rC = np.array([0, -1.5, 0])
        rD = np.array([-2, 0, 0])
        rhombus = Polygon(rA, rB, rC, rD, color=PURPLE, stroke_width=2.5)
        rhombus.shift(DOWN*0.3)

        with self.voiceover(
            text='Moving <bookmark mark="bk_rh"/>on to the rhombus, '
                 'a <bookmark mark="bk_quad"/>quadrilateral with all four '
                 'sides equal.'
        ) as tracker:
            self.wait_until_bookmark("bk_rh")
            self.wait(0.2)
            self.wait_until_bookmark("bk_quad")
            self.play(Create(rhombus), run_time=1.3)

        d1 = DashedLine(rA + DOWN*0.3, rC + DOWN*0.3, color=PURPLE, stroke_width=2)
        d2 = DashedLine(rD + DOWN*0.3, rB + DOWN*0.3, color=PURPLE, stroke_width=2)
        center = np.array([0, -0.3, 0])
        right_angle = Square(side_length=0.25, color=ORANGE_HL, stroke_width=2)
        right_angle.move_to(center + UR*0.15)

        with self.voiceover(
            text='In a rhombus, <bookmark mark="bk_diag"/>diagonals bisect each '
                 'other at right angles,'
        ) as tracker:
            self.wait_until_bookmark("bk_diag")
            self.play(Create(d1), Create(d2), FadeIn(right_angle), run_time=1.0)

        with self.voiceover(
            text='dividing <bookmark mark="bk_4tri"/>it into four congruent '
                 'right-angled triangles.'
        ) as tracker:
            self.wait_until_bookmark("bk_4tri")
            tri_pts = [(rA, rB, center), (rB, rC, center), (rC, rD, center), (rD, rA, center)]
            tris = VGroup(*[
                Polygon(p1 + DOWN*0.3, p2 + DOWN*0.3, p3,
                        color=ORANGE_HL, fill_color=ORANGE_HL,
                        fill_opacity=0.2, stroke_width=0)
                for p1, p2, p3 in tri_pts
            ])
            self.play(FadeIn(tris), run_time=0.6)
            self.play(FadeOut(tris), run_time=0.4)

        rh_formula = MathTex(r"A = \tfrac{1}{2} \times d_1 \times d_2",
                             color=ORANGE_HL, font_size=36).to_edge(UP, buff=1.4)
        rh_box = SurroundingRectangle(rh_formula, color=ORANGE_HL,
                                       corner_radius=0.15, buff=0.2, stroke_width=3)
        with self.voiceover(
            text='This gives us <bookmark mark="bk_rf"/>Area of a rhombus equals '
                 'one half times d sub 1 times d sub 2.'
        ) as tracker:
            self.wait_until_bookmark("bk_rf")
            self.play(FadeIn(rh_formula), Create(rh_box), run_time=1.0)

        self.wait(0.5)
        self.play(FadeOut(rh_formula), FadeOut(rh_box),
                  FadeOut(right_angle), run_time=0.6)

        # --- SCENE 7: Rhombus Example ---
        new_head = make_badge("Example")
        self.play(FadeOut(heading), FadeIn(new_head), run_time=0.6)
        heading = new_head

        q2 = Text("Find the area of a rhombus with\n"
                  "diagonals 16 cm and 12 cm.",
                  font="Poppins", font_size=24, color=PURPLE,
                  line_spacing=1.0).to_edge(UP, buff=1.3)

        d1_arr, d1_lbl = dim_arrow(rA + DOWN*0.3 + RIGHT*0.4,
                                     rC + DOWN*0.3 + RIGHT*0.4, "16 cm", RIGHT)
        d2_arr, d2_lbl = dim_arrow(rD + DOWN*0.3 + DOWN*0.3,
                                     rB + DOWN*0.3 + DOWN*0.3, "12 cm", DOWN)

        with self.voiceover(
            text='Let\'s work <bookmark mark="bk_we"/>an example. '
                 'Find the <bookmark mark="bk_q2"/>area of a rhombus with '
                 '<bookmark mark="bk_d1arr"/>diagonals 16 centimeters '
                 'and <bookmark mark="bk_d2arr"/>12 centimeters.'
        ) as tracker:
            self.wait_until_bookmark("bk_we")
            self.wait(0.2)
            self.wait_until_bookmark("bk_q2")
            self.play(FadeIn(q2), run_time=0.8)
            self.wait_until_bookmark("bk_d1arr")
            self.play(Create(d1_arr), FadeIn(d1_lbl), run_time=0.7)
            self.wait_until_bookmark("bk_d2arr")
            self.play(Create(d2_arr), FadeIn(d2_lbl), run_time=0.7)

        unk2 = unknown_mark(np.array([0.6, -0.3, 0]))
        self.play(FadeIn(unk2), run_time=0.5)
        self.wait(0.3)

        # Transition to solution
        rh_grp = VGroup(rhombus, d1, d2, d1_arr, d1_lbl, d2_arr, d2_lbl, unk2)
        new_head = make_badge("Solution")
        self.play(FadeOut(heading), FadeIn(new_head),
                  FadeOut(q2),
                  rh_grp.animate.scale(0.75).to_edge(RIGHT, buff=0.7),
                  run_time=1.0)
        heading = new_head

        with self.voiceover(text='Solution.') as tracker:
            pass

        rh_s1 = MathTex(r"A = \tfrac{1}{2} \times 16 \times 12",
                        color=PURPLE, font_size=34)
        rh_s1.to_edge(LEFT, buff=0.8).shift(UP*1.0)
        with self.voiceover(
            text='Area equals <bookmark mark="bk_rs1"/>one half times 16 times 12'
        ) as tracker:
            self.wait_until_bookmark("bk_rs1")
            self.play(FadeIn(rh_s1), run_time=0.8)

        rh_s2 = MathTex(r"= \tfrac{1}{2} \times 192", color=PURPLE, font_size=34)
        rh_s2.next_to(rh_s1, DOWN, buff=0.4).align_to(rh_s1, LEFT)
        with self.voiceover(
            text='equals <bookmark mark="bk_rs2"/>one half times 192'
        ) as tracker:
            self.wait_until_bookmark("bk_rs2")
            self.play(rh_s1.animate.set_opacity(0.4),
                      FadeIn(rh_s2), run_time=0.7)

        rh_ans = MathTex(r"A = 96 \, \text{cm}^2", color=ORANGE_HL, font_size=40)
        rh_ans.next_to(rh_s2, DOWN, buff=0.5).align_to(rh_s1, LEFT)
        with self.voiceover(
            text='equals <bookmark mark="bk_rans"/>96 centimeter square.'
        ) as tracker:
            self.wait_until_bookmark("bk_rans")
            self.play(rh_s2.animate.set_opacity(0.4),
                      FadeOut(unk2),
                      FadeIn(rh_ans), run_time=0.9)

        self.wait(0.7)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

        # --- SCENE 8: Unit Conversions Intro ---
        intro2 = Text("Let's consider unit conversions.",
                      font="Poppins", font_size=36, color=PURPLE).move_to(ORIGIN)
        self.play(FadeIn(intro2), run_time=0.8)
        with self.voiceover(
            text='Now let us consider unit conversions.'
        ) as tracker:
            pass
        self.wait(0.4)
        self.play(FadeOut(intro2), run_time=0.6)

        # --- SCENE 9: Areas in Real Life — Conversions ---
        heading = make_badge("Areas in Real Life")
        self.play(FadeIn(heading), run_time=0.5)

        line1 = MathTex(r"1\text{ in} = 2.54\text{ cm} \;\Rightarrow\; "
                        r"1\text{ in}^2 = 6.4516\text{ cm}^2",
                        color=PURPLE, font_size=30).to_edge(UP, buff=1.4)
        with self.voiceover(
            text='Since <bookmark mark="bk_in"/>1 inch equals 2.54 centimeters, '
                 'we get 1 inch square equals 6.4516 centimeter square.'
        ) as tracker:
            self.wait_until_bookmark("bk_in")
            self.play(FadeIn(line1), run_time=0.9)

        line2 = MathTex(r"\text{in}^2 \to \text{cm}^2: \;\times 6.4516",
                        color=ORANGE_HL, font_size=30)
        line2.next_to(line1, DOWN, buff=0.5)
        with self.voiceover(
            text='To convert <bookmark mark="bk_mul"/>inch square to '
                 'centimeter square, multiply by 6.4516.'
        ) as tracker:
            self.wait_until_bookmark("bk_mul")
            self.play(FadeIn(line2), run_time=0.8)

        line3 = MathTex(r"\text{cm}^2 \to \text{in}^2: \;\div 6.4516",
                        color=ORANGE_HL, font_size=30)
        line3.next_to(line2, DOWN, buff=0.35)
        with self.voiceover(
            text='To convert <bookmark mark="bk_div"/>centimeter square to '
                 'inch square, divide by 6.4516.'
        ) as tracker:
            self.wait_until_bookmark("bk_div")
            self.play(FadeIn(line3), run_time=0.8)

        line4 = MathTex(r"1\text{ ft} = 12\text{ in} \;\Rightarrow\; "
                        r"1\text{ ft}^2 = 144\text{ in}^2",
                        color=PURPLE, font_size=30)
        line4.next_to(line3, DOWN, buff=0.5)
        with self.voiceover(
            text='Also, <bookmark mark="bk_ft"/>1 foot equals 12 inches, '
                 'so 1 foot square equals 144 inch square.'
        ) as tracker:
            self.wait_until_bookmark("bk_ft")
            self.play(FadeIn(line4), run_time=0.9)

        line5 = MathTex(r"1\text{ acre} = 43{,}560\text{ ft}^2",
                        color=PURPLE, font_size=30)
        line5.next_to(line4, DOWN, buff=0.35)
        with self.voiceover(
            text='For land, <bookmark mark="bk_ac"/>1 acre equals '
                 '43,560 foot square.'
        ) as tracker:
            self.wait_until_bookmark("bk_ac")
            self.play(FadeIn(line5), run_time=0.8)

        self.wait(0.5)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

        # --- SCENE 10: Choosing Units ---
        heading = make_badge("Choosing Units")
        self.play(FadeIn(heading), run_time=0.5)

        bullets = VGroup(
            Text("• Paper / small surfaces  ->  cm²",
                 font="Poppins", font_size=26, color=PURPLE),
            Text("• Rooms  ->  m² or ft²",
                 font="Poppins", font_size=26, color=PURPLE),
            Text("• Cities  ->  km²",
                 font="Poppins", font_size=26, color=PURPLE),
            Text("• Land  ->  acres",
                 font="Poppins", font_size=26, color=PURPLE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3).to_edge(LEFT, buff=1.0)

        with self.voiceover(
            text='Choosing <bookmark mark="bk_cu"/>the right unit matters. '
                 'Use <bookmark mark="bk_bul"/>centimeter square for small surfaces '
                 'like paper, meter square or foot square for rooms, '
                 'kilometer square for cities, and acres for land.'
        ) as tracker:
            self.wait_until_bookmark("bk_cu")
            self.wait(0.2)
            self.wait_until_bookmark("bk_bul")
            self.play(FadeIn(bullets), run_time=1.2)

        india_note = Text(
            "In India: bigha, gaj, katha, dhur, cent, ankanam",
            font="Poppins", font_size=22, color=PURPLE
        ).next_to(bullets, DOWN, buff=0.5).align_to(bullets, LEFT)
        with self.voiceover(
            text='In India, <bookmark mark="bk_in2"/>local units such as bigha, '
                 'gaj, katha, dhur, cent, and ankanam are also used.'
        ) as tracker:
            self.wait_until_bookmark("bk_in2")
            self.play(FadeIn(india_note), run_time=1.0)

        self.wait(0.5)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

        # --- SCENE 11: A4 Estimation ---
        heading = make_badge("A4 Estimation")
        self.play(FadeIn(heading), run_time=0.5)

        a4_rect = Rectangle(width=2.1, height=2.97, color=PURPLE, stroke_width=2.5,
                            fill_color=PURPLE, fill_opacity=0.05)
        a4_rect.move_to(ORIGIN).shift(LEFT*2.5 + DOWN*0.3)
        a4_w_arr, a4_w_lbl = dim_arrow(
            a4_rect.get_corner(DL) + DOWN*0.25,
            a4_rect.get_corner(DR) + DOWN*0.25, "21 cm", DOWN)
        a4_h_arr, a4_h_lbl = dim_arrow(
            a4_rect.get_corner(UL) + LEFT*0.25,
            a4_rect.get_corner(DL) + LEFT*0.25, "29.7 cm", LEFT)

        with self.voiceover(
            text='For real-life estimation, <bookmark mark="bk_a4"/>an A4 sheet '
                 'measures 21 centimeters times 29.7 centimeters,'
        ) as tracker:
            self.wait_until_bookmark("bk_a4")
            self.play(Create(a4_rect),
                      Create(a4_w_arr), FadeIn(a4_w_lbl),
                      Create(a4_h_arr), FadeIn(a4_h_lbl),
                      run_time=1.2)

        a4_area = MathTex(r"\text{Area} = 623.7 \, \text{cm}^2",
                          color=ORANGE_HL, font_size=32)
        a4_area.next_to(a4_rect, RIGHT, buff=1.5).shift(UP*0.8)
        with self.voiceover(
            text='giving <bookmark mark="bk_aa"/>an area of 623.7 '
                 'centimeter square.'
        ) as tracker:
            self.wait_until_bookmark("bk_aa")
            self.play(FadeIn(a4_area), run_time=0.7)

        table_calc = MathTex(r"6 \times 623.7 \approx 3742 \, \text{cm}^2",
                             color=ORANGE_HL, font_size=30)
        table_calc.next_to(a4_area, DOWN, buff=0.5).align_to(a4_area, LEFT)
        with self.voiceover(
            text='If about <bookmark mark="bk_six"/>six A4 sheets cover your '
                 'tabletop, the table area is roughly 3742 centimeter square.'
        ) as tracker:
            self.wait_until_bookmark("bk_six")
            self.play(FadeIn(table_calc), run_time=0.9)

        scale_note = Text(
            "Classrooms -> m² or ft²\nSchools -> m²\nCities/Villages -> km² or acres",
            font="Poppins", font_size=22, color=PURPLE, line_spacing=1.0,
        ).next_to(table_calc, DOWN, buff=0.5).align_to(a4_area, LEFT)
        with self.voiceover(
            text='Classrooms <bookmark mark="bk_sc"/>are measured in meter square '
                 'or foot square, schools in meter square, and villages or cities '
                 'in kilometer square or acres.'
        ) as tracker:
            self.wait_until_bookmark("bk_sc")
            self.play(FadeIn(scale_note), run_time=1.1)

        self.wait(0.6)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

     # --- SCENE 12: Summary ---
        heading = make_badge("Summary")
        self.play(FadeIn(heading), run_time=0.5)

        summary_items = VGroup(
            Text("• Areas of trapeziums and rhombuses",
                 font="Poppins", font_size=26, color=PURPLE),
            Text("• Comparing areas through dissection",
                 font="Poppins", font_size=26, color=PURPLE),
            Text("• Choosing suitable area units",
                 font="Poppins", font_size=26, color=PURPLE),
            Text("• Converting between units",
                 font="Poppins", font_size=26, color=PURPLE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.4).move_to(ORIGIN)

        with self.voiceover(text='Summary. We have learned about') as tracker:
            pass

        with self.voiceover(text='areas of trapeziums and rhombuses,') as tracker:
            self.play(FadeIn(summary_items[0]), run_time=0.7)

        with self.voiceover(text='comparing areas through dissection,') as tracker:
            self.play(FadeIn(summary_items[1]), run_time=0.7)

        with self.voiceover(text='choosing suitable area units,') as tracker:
            self.play(FadeIn(summary_items[2]), run_time=0.7)

        with self.voiceover(text='and converting between them.') as tracker:
            self.play(FadeIn(summary_items[3]), run_time=0.7)

        self.wait(0.8)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=1.0)