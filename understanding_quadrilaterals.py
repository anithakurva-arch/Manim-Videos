import os
import urllib.request
import manimpango
from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.openai import OpenAIService

# ============================================================
# COSCHOOL COLOR PALETTE
# ============================================================
LAVENDER_BG = "#E7E5F3"
PURPLE      = "#7464CE"
ORANGE_HL   = "#FF9302"
PALE_PURPLE = "#9495D7"

# ============================================================
# POPPINS AUTO-DOWNLOAD & REGISTRATION
# ============================================================
def _setup_poppins():
    base_dir  = os.path.dirname(os.path.abspath(__file__))
    fonts_dir = os.path.join(base_dir, ".fonts")
    os.makedirs(fonts_dir, exist_ok=True)
    base_url = (
        "https://raw.githubusercontent.com/google/fonts/main/ofl/poppins/"
    )
    fonts = {
        "Poppins-Regular.ttf":  base_url + "Poppins-Regular.ttf",
        "Poppins-Bold.ttf":     base_url + "Poppins-Bold.ttf",
        "Poppins-Italic.ttf":   base_url + "Poppins-Italic.ttf",
        "Poppins-SemiBold.ttf": base_url + "Poppins-SemiBold.ttf",
    }
    for fname, url in fonts.items():
        path = os.path.join(fonts_dir, fname)
        if not os.path.exists(path):
            try:
                print(f"Downloading {fname}")
                urllib.request.urlretrieve(url, path)
            except Exception as e:
                print(f"   Could not download {fname}: {e}")
                continue
        try:
            manimpango.register_font(path)
        except Exception:
            pass
    print("Poppins setup complete.")

_setup_poppins()

# ============================================================
# BOOKMARK FAILURE TRACKER (DEBUG)
# ============================================================
import manim_voiceover.tracker as _vt
_orig_time_until_bookmark = _vt.VoiceoverTracker.time_until_bookmark
_FAILED_BOOKMARKS = []

def _safe_time_until_bookmark(self, mark, buff=0.0, limit=None):
    try:
        return _orig_time_until_bookmark(self, mark, buff, limit)
    except Exception:
        scene_text = getattr(self, 'data', {}).get('input_text', 'unknown')[:80]
        _FAILED_BOOKMARKS.append((mark, scene_text))
        print(f"WARNING  Bookmark '{mark}' NOT FOUND in: {scene_text}...")
        return 0.0

_vt.VoiceoverTracker.time_until_bookmark = _safe_time_until_bookmark

import atexit
def _report():
    if _FAILED_BOOKMARKS:
        print("\n" + "=" * 60)
        print(f"FAILED BOOKMARKS SUMMARY ({len(_FAILED_BOOKMARKS)} total):")
        print("=" * 60)
        for mark, text in _FAILED_BOOKMARKS:
            print(f"  FAILED: {mark}  ->  {text}")
        print("=" * 60)
atexit.register(_report)

# ============================================================
# TTS INSTRUCTIONS
# ============================================================
TTS_INSTRUCTIONS = """
Voice & Personality:
You are a warm, patient, and encouraging mathematics teacher
speaking to a middle-school student. Your tone is friendly,
calm, and confident — never rushed, never robotic. The voice
profile is shimmer — bright, warm, and slightly playful.

Pacing:
Speak at a MODERATE-TO-SLOW pace. Honor the commas, dashes,
and ellipses in the script — they are deliberate pacing marks.

Emphasis:
Naturally emphasize key terms: shape names like polygon,
quadrilateral, parallelogram, rhombus, rectangle, and square.

Pauses:
Beat at commas, medium pause at dashes, dramatic pause at
ellipses.

Do NOT race, flatten, improvise, or paraphrase.
"""

# ============================================================
# HELPERS
# ============================================================
def create_heading_badge(text_str):
    t = Text(text_str, font="Poppins", font_size=28,
             color=WHITE, weight=BOLD)
    badge = RoundedRectangle(
        corner_radius=0.2,
        width=t.width + 0.6, height=t.height + 0.3,
        fill_color=PURPLE, fill_opacity=1, stroke_width=0,
    )
    badge.move_to(t)
    return VGroup(badge, t).to_corner(UL, buff=0.3)


def math_obj(tex_str, color=PURPLE, font_size=36):
    return MathTex(
        tex_str,
        tex_template=TexFontTemplates.gnu_freesans_tx,
        color=color, font_size=font_size,
    )


def label_text(s, font_size=22, color=PURPLE, weight=NORMAL):
    return Text(s, font="Poppins", font_size=font_size,
                color=color, weight=weight)


def shape_label_box(name, target, direction=DOWN, buff=0.2):
    lbl = label_text(name, font_size=24, color=PURPLE, weight=BOLD)
    lbl.next_to(target, direction, buff=buff)
    return lbl


SAFE_LEFT, SAFE_RIGHT = -6.11, 6.11
SAFE_TOP, SAFE_BOTTOM = 3.25, -3.25


def check_safe_margins(mob, name="object"):
    return True


# ============================================================
# SCENE
# ============================================================
class UnderstandingQuadrilaterals(VoiceoverScene):
    def construct(self):
        self.camera.background_color = LAVENDER_BG

        self.set_speech_service(
            OpenAIService(
                voice="shimmer",
                model="gpt-4o-mini-tts",
                transcription_model="medium",
                instructions=TTS_INSTRUCTIONS,
            ),
            create_subcaption=False,
        )

        self.play_title_slide()
        self.play_segment_1_hook()
        self.play_segment_2_polygons()
        self.play_segment_3_quadrilaterals()
        self.play_segment_4_hierarchy()

    # --------------------------------------------------------
    def play_title_slide(self):
        bg = FullScreenRectangle(color=PURPLE, fill_color=PURPLE,
                                 fill_opacity=1, stroke_width=0)
        self.add(bg)
        title = Text("Understanding", font="Poppins",
                     font_size=72, color=WHITE, weight=BOLD)
        sub   = Text("Quadrilaterals", font="Poppins",
                     font_size=72, color=WHITE, weight=BOLD)
        grp = VGroup(title, sub).arrange(DOWN, buff=0.3).move_to(ORIGIN)

        with self.voiceover(
            text='<bookmark mark="bk_hello"/>Hello students!'
        ) as tracker:
            self.wait_until_bookmark("bk_hello")
            self.play(FadeIn(grp), run_time=1.0)
            self.wait(0.4)

        self.play(FadeOut(grp), FadeOut(bg), run_time=0.8)

    # --------------------------------------------------------
    def play_segment_1_hook(self):
        badge = create_heading_badge("Around You")

        classroom = Rectangle(
            width=8.0, height=4.5,
            color=PURPLE, stroke_width=2.5,
        ).move_to(DOWN * 0.2)

        # Door (rectangle)
        door = Rectangle(
            width=0.8, height=1.8,
            color=PURPLE, stroke_width=2.5,
            fill_color=PALE_PURPLE, fill_opacity=0.2,
        ).move_to(classroom.get_left() + RIGHT * 0.7 + DOWN * 0.4)
        door_lbl = label_text("Door", font_size=20, color=PURPLE)
        door_lbl.next_to(door, DOWN, buff=0.15)

        # Tiles (squares)
        tile1 = Square(side_length=0.6, color=PURPLE, stroke_width=2.5,
                       fill_color=PALE_PURPLE, fill_opacity=0.2)
        tile2 = Square(side_length=0.6, color=PURPLE, stroke_width=2.5,
                       fill_color=PALE_PURPLE, fill_opacity=0.2)
        tile3 = Square(side_length=0.6, color=PURPLE, stroke_width=2.5,
                       fill_color=PALE_PURPLE, fill_opacity=0.2)
        tiles = VGroup(tile1, tile2, tile3).arrange(RIGHT, buff=0.1)
        tiles.move_to(classroom.get_bottom() + UP * 0.5)
        tiles_lbl = label_text("Tiles", font_size=20, color=PURPLE)
        tiles_lbl.next_to(tiles, UP, buff=0.15)

        # Window (quadrilateral - trapezoid-like)
        window = Polygon(
            [-0.7, 0.6, 0], [0.8, 0.7, 0],
            [0.7, -0.5, 0], [-0.6, -0.6, 0],
            color=PURPLE, stroke_width=2.5,
            fill_color=PALE_PURPLE, fill_opacity=0.2,
        ).move_to(classroom.get_right() + LEFT * 1.2 + UP * 0.3)
        window_lbl = label_text("Window", font_size=20, color=PURPLE)
        window_lbl.next_to(window, DOWN, buff=0.15)

        with self.voiceover(
            text='Look around your <bookmark mark="bk_classroom"/>classroom — '
                 'the <bookmark mark="bk_door"/>door is a rectangle, '
                 'the <bookmark mark="bk_tiles"/>floor tiles are squares, '
                 'the <bookmark mark="bk_windows"/>windows are quadrilaterals. '
                 'Every flat shape with straight sides has a name. '
                 'But how do we decide... what to call each one?'
        ) as tracker:
            self.wait_until_bookmark("bk_classroom")
            self.play(FadeIn(badge), Create(classroom), run_time=1.2)

            self.wait_until_bookmark("bk_door")
            self.play(Create(door), FadeIn(door_lbl), run_time=0.9)

            self.wait_until_bookmark("bk_tiles")
            self.play(Create(tiles), FadeIn(tiles_lbl), run_time=1.0)

            self.wait_until_bookmark("bk_windows")
            self.play(Create(window), FadeIn(window_lbl), run_time=0.9)
            self.wait(0.6)

        self.play(
            FadeOut(VGroup(badge, classroom, door, door_lbl,
                           tiles, tiles_lbl, window, window_lbl)),
            run_time=0.8,
        )

    # --------------------------------------------------------
    def play_segment_2_polygons(self):
        badge = create_heading_badge("Polygons")

        # Generic pentagon
        pentagon = RegularPolygon(n=5, color=PURPLE, stroke_width=2.5)
        pentagon.scale(1.3).move_to(ORIGIN)

        with self.voiceover(
            text='A <bookmark mark="bk_polygon"/>polygon — '
                 'is a closed flat figure, made of straight line segments.'
        ) as tracker:
            self.wait_until_bookmark("bk_polygon")
            self.play(FadeIn(badge), Create(pentagon), run_time=1.3)
            self.wait(0.4)

        # Move pentagon LEFT, build convex with diagonals
        self.play(pentagon.animate.scale(0.8).shift(LEFT * 3.5),
                  run_time=0.9)

        # Convex diagonals (all inside)
        verts_convex = [pentagon.get_vertices()[i] for i in range(5)]
        convex_diags = VGroup()
        for i in range(5):
            for j in range(i + 2, 5):
                if not (i == 0 and j == 4):
                    line = Line(verts_convex[i], verts_convex[j],
                                color=ORANGE_HL, stroke_width=2.0)
                    convex_diags.add(line)
        convex_lbl = label_text("Convex", font_size=26,
                                color=PURPLE, weight=BOLD)
        convex_lbl.next_to(pentagon, DOWN, buff=0.3)

        # Concave shape (right)
        concave = Polygon(
            [0, 1.2, 0], [1.2, 0.4, 0], [0.4, 0, 0],
            [1.2, -0.8, 0], [-1.0, -0.6, 0],
            color=PURPLE, stroke_width=2.5,
        ).shift(RIGHT * 3.5)
        concave_diag = Line(
            concave.get_vertices()[0],
            concave.get_vertices()[3],
            color=ORANGE_HL, stroke_width=2.0,
        )
        concave_lbl = label_text("Concave", font_size=26,
                                 color=PURPLE, weight=BOLD)
        concave_lbl.next_to(concave, DOWN, buff=0.3)

        with self.voiceover(
            text='If all its <bookmark mark="bk_convex"/>diagonals lie inside, '
                 'it is convex. '
                 'If any diagonal <bookmark mark="bk_concave"/>goes outside, '
                 'it is concave.'
        ) as tracker:
            self.wait_until_bookmark("bk_convex")
            self.play(Create(convex_diags), FadeIn(convex_lbl),
                      run_time=1.2)

            self.wait_until_bookmark("bk_concave")
            self.play(Create(concave), run_time=0.9)
            self.play(Create(concave_diag), FadeIn(concave_lbl),
                      run_time=0.9)
            self.wait(0.4)

        # Fade out and show regular vs irregular
        self.play(FadeOut(VGroup(pentagon, convex_diags, convex_lbl,
                                 concave, concave_diag, concave_lbl)),
                  run_time=0.7)

        regular = RegularPolygon(n=5, color=PURPLE, stroke_width=2.5)
        regular.scale(1.1).shift(LEFT * 3.0)
        reg_lbl = label_text("Regular", font_size=26,
                             color=PURPLE, weight=BOLD)
        reg_lbl.next_to(regular, DOWN, buff=0.3)

        irregular = Polygon(
            [0, 1.3, 0], [1.2, 0.6, 0],
            [0.9, -0.9, 0], [-0.8, -0.7, 0], [-1.0, 0.5, 0],
            color=PURPLE, stroke_width=2.5,
        ).shift(RIGHT * 3.0)
        irreg_lbl = label_text("Irregular", font_size=26,
                               color=PURPLE, weight=BOLD)
        irreg_lbl.next_to(irregular, DOWN, buff=0.3)

        with self.voiceover(
            text='A polygon is <bookmark mark="bk_regular"/>regular, '
                 'when all its sides and angles are equal — otherwise it is irregular.'
        ) as tracker:
            self.wait_until_bookmark("bk_regular")
            self.play(
                Create(regular), FadeIn(reg_lbl),
                Create(irregular), FadeIn(irreg_lbl),
                run_time=1.3,
            )
            self.wait(0.6)

        self.play(FadeOut(VGroup(badge, regular, reg_lbl,
                                 irregular, irreg_lbl)),
                  run_time=0.8)

    # --------------------------------------------------------
    def play_segment_3_quadrilaterals(self):
        badge = create_heading_badge("Quadrilaterals")

        # Generic quadrilateral center
        quad = Polygon(
            [-1.5, 1.0, 0], [1.6, 1.2, 0],
            [1.3, -1.1, 0], [-1.4, -0.9, 0],
            color=PURPLE, stroke_width=2.5,
        ).move_to(ORIGIN)

        with self.voiceover(
            text='When a polygon has exactly <bookmark mark="bk_quad"/>four sides, '
                 'it is called a quadrilateral. '
                 'Within quadrilaterals, there are several named types.'
        ) as tracker:
            self.wait_until_bookmark("bk_quad")
            self.play(FadeIn(badge), Create(quad), run_time=1.3)
            self.play(Indicate(quad, color=ORANGE_HL, scale_factor=1.1),
                      run_time=0.7)
            self.wait(0.4)

        self.play(FadeOut(quad), run_time=0.5)

        # --- TRAPEZIUM ---
        trap = Polygon(
            [-1.2, 0.7, 0], [1.2, 0.7, 0],
            [0.8, -0.7, 0], [-0.8, -0.7, 0],
            color=PURPLE, stroke_width=2.5,
        )
        trap_top = Line(trap.get_vertices()[0], trap.get_vertices()[1],
                        color=ORANGE_HL, stroke_width=3.0)
        trap_bot = Line(trap.get_vertices()[3], trap.get_vertices()[2],
                        color=ORANGE_HL, stroke_width=3.0)
        trap_grp = VGroup(trap, trap_top, trap_bot).move_to(ORIGIN)
        trap_lbl = label_text("Trapezium", font_size=28,
                              color=PURPLE, weight=BOLD)
        trap_lbl.next_to(trap_grp, DOWN, buff=0.3)

        with self.voiceover(
            text='First, a <bookmark mark="bk_trapezium"/>trapezium, '
                 'has one pair of parallel sides.'
        ) as tracker:
            self.wait_until_bookmark("bk_trapezium")
            self.play(Create(trap), run_time=0.9)
            self.play(Create(trap_top), Create(trap_bot),
                      FadeIn(trap_lbl), run_time=0.8)
            self.wait(0.4)

        self.play(FadeOut(VGroup(trap, trap_top, trap_bot, trap_lbl)),
                  run_time=0.5)

        # --- KITE ---
        kite = Polygon(
            [0, 1.4, 0], [1.0, 0.2, 0],
            [0, -1.4, 0], [-1.0, 0.2, 0],
            color=PURPLE, stroke_width=2.5,
        ).move_to(ORIGIN)
        # Tick marks on adjacent equal sides
        kite_v = kite.get_vertices()
        side_a = Line(kite_v[0], kite_v[1], color=ORANGE_HL, stroke_width=3.0)
        side_b = Line(kite_v[0], kite_v[3], color=ORANGE_HL, stroke_width=3.0)
        side_c = Line(kite_v[1], kite_v[2], color=ORANGE_HL, stroke_width=3.0)
        side_d = Line(kite_v[3], kite_v[2], color=ORANGE_HL, stroke_width=3.0)
        kite_lbl = label_text("Kite", font_size=28,
                              color=PURPLE, weight=BOLD)
        kite_lbl.next_to(kite, DOWN, buff=0.3)

        with self.voiceover(
            text='Next, a <bookmark mark="bk_kite"/>kite, '
                 'has two pairs of adjacent sides equal — '
                 'like a real kite in the sky.'
        ) as tracker:
            self.wait_until_bookmark("bk_kite")
            self.play(Create(kite), run_time=0.9)
            self.play(Create(side_a), Create(side_b), run_time=0.6)
            self.play(Create(side_c), Create(side_d),
                      FadeIn(kite_lbl), run_time=0.7)
            self.wait(0.4)

        self.play(FadeOut(VGroup(kite, side_a, side_b,
                                 side_c, side_d, kite_lbl)),
                  run_time=0.5)

        # --- PARALLELOGRAM ---
        para = Polygon(
            [-1.5, 0.7, 0], [1.5, 0.7, 0],
            [1.0, -0.7, 0], [-2.0, -0.7, 0],
            color=PURPLE, stroke_width=2.5,
        ).move_to(ORIGIN)
        pv = para.get_vertices()
        p_top = Line(pv[0], pv[1], color=ORANGE_HL, stroke_width=3.0)
        p_bot = Line(pv[3], pv[2], color=ORANGE_HL, stroke_width=3.0)
        p_right = Line(pv[1], pv[2], color=ORANGE_HL, stroke_width=3.0)
        p_left = Line(pv[0], pv[3], color=ORANGE_HL, stroke_width=3.0)
        para_lbl = label_text("Parallelogram", font_size=28,
                              color=PURPLE, weight=BOLD)
        para_lbl.next_to(para, DOWN, buff=0.3)

        with self.voiceover(
            text='Then we have a <bookmark mark="bk_parallelogram"/>parallelogram, '
                 'where both pairs of opposite sides are parallel.'
        ) as tracker:
            self.wait_until_bookmark("bk_parallelogram")
            self.play(Create(para), run_time=0.9)
            self.play(Create(p_top), Create(p_bot), run_time=0.6)
            self.play(Create(p_left), Create(p_right),
                      FadeIn(para_lbl), run_time=0.7)
            self.wait(0.4)

        self.play(FadeOut(VGroup(para, p_top, p_bot,
                                 p_left, p_right, para_lbl)),
                  run_time=0.5)

        # --- RHOMBUS ---
        rhom = Polygon(
            [0, 1.2, 0], [1.4, 0, 0],
            [0, -1.2, 0], [-1.4, 0, 0],
            color=PURPLE, stroke_width=2.5,
        ).move_to(ORIGIN)
        rv = rhom.get_vertices()
        r_sides = VGroup(
            Line(rv[0], rv[1], color=ORANGE_HL, stroke_width=3.0),
            Line(rv[1], rv[2], color=ORANGE_HL, stroke_width=3.0),
            Line(rv[2], rv[3], color=ORANGE_HL, stroke_width=3.0),
            Line(rv[3], rv[0], color=ORANGE_HL, stroke_width=3.0),
        )
        rhom_lbl = label_text("Rhombus", font_size=28,
                              color=PURPLE, weight=BOLD)
        rhom_lbl.next_to(rhom, DOWN, buff=0.3)

        with self.voiceover(
            text='A <bookmark mark="bk_rhombus"/>rhombus, '
                 'is a parallelogram with all four sides equal.'
        ) as tracker:
            self.wait_until_bookmark("bk_rhombus")
            self.play(Create(rhom), run_time=0.9)
            self.play(Create(r_sides), FadeIn(rhom_lbl), run_time=0.9)
            self.wait(0.4)

        self.play(FadeOut(VGroup(rhom, r_sides, rhom_lbl)),
                  run_time=0.5)

        # --- RECTANGLE ---
        rect = Rectangle(width=2.8, height=1.6,
                         color=PURPLE, stroke_width=2.5).move_to(ORIGIN)
        rv2 = rect.get_vertices()
        # Right-angle markers (small squares at corners)
        corner_marks = VGroup()
        for v in rv2:
            cx = 0.18 * (-1 if v[0] > 0 else 1)
            cy = 0.18 * (-1 if v[1] > 0 else 1)
            mark = Square(side_length=0.18, color=ORANGE_HL,
                          stroke_width=2.5)
            mark.move_to(v + np.array([cx, cy, 0]))
            corner_marks.add(mark)
        rect_lbl = label_text("Rectangle", font_size=28,
                              color=PURPLE, weight=BOLD)
        rect_lbl.next_to(rect, DOWN, buff=0.3)

        with self.voiceover(
            text='A <bookmark mark="bk_rectangle"/>rectangle, '
                 'is a parallelogram with all four angles right angles — '
                 'like a window frame.'
        ) as tracker:
            self.wait_until_bookmark("bk_rectangle")
            self.play(Create(rect), run_time=0.9)
            self.play(Create(corner_marks), FadeIn(rect_lbl),
                      run_time=0.9)
            self.wait(0.4)

        self.play(FadeOut(VGroup(rect, corner_marks, rect_lbl)),
                  run_time=0.5)

        # --- SQUARE ---
        sq = Square(side_length=2.0, color=PURPLE,
                    stroke_width=2.5).move_to(ORIGIN)
        sv = sq.get_vertices()
        sq_corner_marks = VGroup()
        for v in sv:
            cx = 0.18 * (-1 if v[0] > 0 else 1)
            cy = 0.18 * (-1 if v[1] > 0 else 1)
            mark = Square(side_length=0.18, color=ORANGE_HL,
                          stroke_width=2.5)
            mark.move_to(v + np.array([cx, cy, 0]))
            sq_corner_marks.add(mark)
        sq_side_marks = VGroup(
            Line(sv[0], sv[1], color=ORANGE_HL, stroke_width=3.5),
            Line(sv[1], sv[2], color=ORANGE_HL, stroke_width=3.5),
            Line(sv[2], sv[3], color=ORANGE_HL, stroke_width=3.5),
            Line(sv[3], sv[0], color=ORANGE_HL, stroke_width=3.5),
        )
        sq_lbl = label_text("Square", font_size=28,
                            color=PURPLE, weight=BOLD)
        sq_lbl.next_to(sq, DOWN, buff=0.3)

        with self.voiceover(
            text='And finally, a <bookmark mark="bk_square"/>square, '
                 'has all sides equal and all angles right angles, '
                 'making it both a rhombus and a rectangle.'
        ) as tracker:
            self.wait_until_bookmark("bk_square")
            self.play(Create(sq), run_time=0.9)
            self.play(Create(sq_side_marks), run_time=0.7)
            self.play(Create(sq_corner_marks), FadeIn(sq_lbl),
                      run_time=0.8)
            self.wait(0.5)

        self.play(FadeOut(VGroup(badge, sq, sq_side_marks,
                                 sq_corner_marks, sq_lbl)),
                  run_time=0.8)

    # --------------------------------------------------------
    def play_segment_4_hierarchy(self):
        badge = create_heading_badge("Hierarchy")

        def make_box(name, color=PURPLE, fill_op=0.2):
            txt = label_text(name, font_size=22,
                             color=PURPLE, weight=BOLD)
            box = RoundedRectangle(
                corner_radius=0.15,
                width=max(2.2, txt.width + 0.5),
                height=txt.height + 0.35,
                color=color, stroke_width=2.5,
                fill_color=PALE_PURPLE, fill_opacity=fill_op,
            )
            box.move_to(txt)
            return VGroup(box, txt)

        quad_box = make_box("Quadrilateral").move_to(UP * 2.6)

        with self.voiceover(
            text='Now, why <bookmark mark="bk_why"/>classify them this way? '
                 'Each name adds one more condition to the previous one.'
        ) as tracker:
            self.wait_until_bookmark("bk_why")
            self.play(FadeIn(badge), FadeIn(quad_box), run_time=1.0)
            self.wait(0.6)

        # Parallelogram below
        para_box = make_box("Parallelogram").move_to(UP * 1.0)
        arrow1 = Arrow(
            start=quad_box.get_bottom() + DOWN * 0.05,
            end=para_box.get_top() + UP * 0.05,
            color=PURPLE, stroke_width=2.5, tip_length=0.2,
            buff=0.05,
        )
        cond1 = label_text("opposite sides parallel",
                           font_size=18, color=ORANGE_HL)
        cond1.next_to(arrow1, RIGHT, buff=0.2)

        with self.voiceover(
            text='A quadrilateral becomes a '
                 '<bookmark mark="bk_q_to_p"/>parallelogram, '
                 'when opposite sides are parallel.'
        ) as tracker:
            self.wait_until_bookmark("bk_q_to_p")
            self.play(Create(arrow1), FadeIn(para_box),
                      FadeIn(cond1), run_time=1.0)
            self.wait(0.4)

        # Rhombus branch LEFT
        rhom_box = make_box("Rhombus").move_to(DOWN * 0.5 + LEFT * 2.6)
        arrow_left = Arrow(
            start=para_box.get_bottom() + DOWN * 0.05,
            end=rhom_box.get_top() + UP * 0.05,
            color=PURPLE, stroke_width=2.5, tip_length=0.2,
            buff=0.05,
        )
        cond_left = label_text("all sides equal",
                               font_size=18, color=ORANGE_HL)
        cond_left.next_to(arrow_left, LEFT, buff=0.15)

        with self.voiceover(
            text='A parallelogram becomes a '
                 '<bookmark mark="bk_p_to_rh"/>rhombus, '
                 'when all sides are equal,'
        ) as tracker:
            self.wait_until_bookmark("bk_p_to_rh")
            self.play(Create(arrow_left), FadeIn(rhom_box),
                      FadeIn(cond_left), run_time=1.0)
            self.wait(0.3)

        # Rectangle branch RIGHT
        rect_box = make_box("Rectangle").move_to(DOWN * 0.5 + RIGHT * 2.6)
        arrow_right = Arrow(
            start=para_box.get_bottom() + DOWN * 0.05,
            end=rect_box.get_top() + UP * 0.05,
            color=PURPLE, stroke_width=2.5, tip_length=0.2,
            buff=0.05,
        )
        cond_right = label_text("all right angles",
                                font_size=18, color=ORANGE_HL)
        cond_right.next_to(arrow_right, RIGHT, buff=0.15)

        with self.voiceover(
            text='or a <bookmark mark="bk_p_to_rect"/>rectangle, '
                 'when all angles are right angles.'
        ) as tracker:
            self.wait_until_bookmark("bk_p_to_rect")
            self.play(Create(arrow_right), FadeIn(rect_box),
                      FadeIn(cond_right), run_time=1.0)
            self.wait(0.3)

        # Square at bottom (both converge)
        sq_box = make_box("Square").move_to(DOWN * 2.4)
        sq_box[0].set_color(ORANGE_HL)
        sq_box[0].set_fill(ORANGE_HL, opacity=0.2)
        sq_box[1].set_color(PURPLE)

        arrow_sq_l = Arrow(
            start=rhom_box.get_bottom() + DOWN * 0.05,
            end=sq_box.get_top() + UP * 0.05 + LEFT * 0.2,
            color=PURPLE, stroke_width=2.5, tip_length=0.2,
            buff=0.05,
        )
        arrow_sq_r = Arrow(
            start=rect_box.get_bottom() + DOWN * 0.05,
            end=sq_box.get_top() + UP * 0.05 + RIGHT * 0.2,
            color=PURPLE, stroke_width=2.5, tip_length=0.2,
            buff=0.05,
        )

        with self.voiceover(
            text='A <bookmark mark="bk_square_both"/>square — '
                 'satisfies both. '
                 'So each shape <bookmark mark="bk_inherits"/>inherits '
                 'the rules of the one above it, with one extra added.'
        ) as tracker:
            self.wait_until_bookmark("bk_square_both")
            self.play(Create(arrow_sq_l), Create(arrow_sq_r),
                      FadeIn(sq_box), run_time=1.1)
            self.play(Indicate(sq_box, color=ORANGE_HL,
                               scale_factor=1.1), run_time=0.7)

            self.wait_until_bookmark("bk_inherits")
            self.play(Indicate(quad_box, color=ORANGE_HL), run_time=0.5)
            self.play(Indicate(para_box, color=ORANGE_HL), run_time=0.5)
            self.play(Indicate(rhom_box, color=ORANGE_HL),
                      Indicate(rect_box, color=ORANGE_HL),
                      run_time=0.6)
            self.play(Indicate(sq_box, color=ORANGE_HL), run_time=0.5)
            self.wait(0.8)

        self.play(
            FadeOut(VGroup(badge, quad_box, para_box, rhom_box,
                           rect_box, sq_box, arrow1, arrow_left,
                           arrow_right, arrow_sq_l, arrow_sq_r,
                           cond1, cond_left, cond_right)),
            run_time=0.9,
        )
        self.wait(0.6)