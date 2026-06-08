from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.openai import OpenAIService
import numpy as np
import atexit

# ─── Diagnostic monkey-patch ─────────────────────────────────────────
import manim_voiceover.tracker as _vt
_orig_time_until_bookmark = _vt.VoiceoverTracker.time_until_bookmark
_FAILED_BOOKMARKS = []

def _safe_time_until_bookmark(self, mark, buff=0.0, limit=None):
    try:
        return _orig_time_until_bookmark(self, mark, buff, limit)
    except Exception:
        _FAILED_BOOKMARKS.append(mark)
        print(f"⚠️  bookmark '{mark}' NOT FOUND — continuing")
        return 0.0

_vt.VoiceoverTracker.time_until_bookmark = _safe_time_until_bookmark

def _report():
    if _FAILED_BOOKMARKS:
        print("\n" + "="*60)
        print(f"FAILED BOOKMARKS: {len(_FAILED_BOOKMARKS)}")
        for m in _FAILED_BOOKMARKS:
            print(f"  ❌ {m}")
        print("="*60)
atexit.register(_report)

# ─── Coschool Palette ────────────────────────────────────────────────
LAVENDER_BG = "#E7E5F3"
PURPLE      = "#7464CE"
ORANGE_HL   = "#FF9302"
PALE_PURPLE = "#9495D7"

TTS_INSTRUCTIONS = """
You are a warm, patient, encouraging math teacher speaking to a middle-school 
student. Moderate-to-slow pace, clear articulation. Slow further on formulas, 
pause between components. Pronounce numbers and units (square metres) with 
deliberate cadence. Emphasize key terms (shape names, formulas, final answers). 
Natural beats at commas, longer at periods. Warm and curious mood. Do NOT 
rush, monotone, add filler, or paraphrase.
"""


# ─── Helpers ─────────────────────────────────────────────────────────
def poppins(text_str, size=22, color=PURPLE, weight=NORMAL):
    return Text(text_str, font="Poppins", font_size=size, color=color, weight=weight)

def heading_badge(text_str):
    t = poppins(text_str, size=28, color=WHITE, weight=BOLD)
    bg = RoundedRectangle(corner_radius=0.2, width=t.width+0.6, height=t.height+0.3,
                          fill_color=PURPLE, fill_opacity=1, stroke_width=0)
    bg.move_to(t)
    return VGroup(bg, t).to_corner(UL, buff=0.3)

def dim_arrow(start, end, label, side=UP, color=PURPLE, label_size=22):
    a = DoubleArrow(start, end, color=color, stroke_width=2, tip_length=0.2, buff=0)
    l = poppins(label, label_size, color).next_to(a, side, buff=0.12)
    return VGroup(a, l)

def unknown_mark(pos):
    return poppins("?", 36, ORANGE_HL, BOLD).move_to(pos)

def fade_all(scene, rt=0.7):
    if scene.mobjects:
        scene.play(*[FadeOut(m) for m in scene.mobjects], run_time=rt)


# ─── Main Scene ──────────────────────────────────────────────────────
class RectangleAreaExplainer(VoiceoverScene):
    def construct(self):
        self.camera.background_color = LAVENDER_BG
        self.set_speech_service(
            OpenAIService(
                voice="nova",
                model="gpt-4o-mini-tts",
                transcription_model="large-v2",
                instructions=TTS_INSTRUCTIONS,
            ),
            create_subcaption=False,
        )

        # ════════════════════════════════════════════════════════
        # SCENE 1 — Title
        # ════════════════════════════════════════════════════════
        title_bg = Rectangle(width=config.frame_width, height=config.frame_height,
                             fill_color=PURPLE, fill_opacity=1, stroke_width=0)
        title = poppins("Area of a Rectangle", 72, WHITE, BOLD)
        with self.voiceover(text='Area of a <bookmark mark="t1"/>Rectangle.'):
            self.play(FadeIn(title_bg), FadeIn(title), run_time=1.0)
            self.wait_until_bookmark("t1")
        self.wait(0.5)
        self.play(FadeOut(title_bg), FadeOut(title), run_time=0.8)

        # ════════════════════════════════════════════════════════
        # SCENE 2 — Intro tile icon
        # ════════════════════════════════════════════════════════
        tile_icon = VGroup(*[
            Square(side_length=0.5, color=PURPLE, stroke_width=2,
                   fill_color=ORANGE_HL, fill_opacity=0.4)
            for _ in range(9)
        ]).arrange_in_grid(3, 3, buff=0.05)
        intro = poppins("Let's tile a courtyard.", 36, PURPLE).next_to(tile_icon, DOWN, buff=0.6)

        with self.voiceover(
            text='Imagine you are helping your family <bookmark mark="i1"/>tile a courtyard.'
        ):
            self.wait_until_bookmark("i1")
            self.play(FadeIn(tile_icon), FadeIn(intro), run_time=1.0)
        self.wait(0.4)
        fade_all(self)

        # ════════════════════════════════════════════════════════
        # SCENE 3 — Garden Problem (figure shown with proper arrows)
        # ════════════════════════════════════════════════════════
        bdg = heading_badge("The Garden Problem")
        # Inner park
        inner = Rectangle(width=4.4, height=3.2, color=PURPLE, stroke_width=2.5,
                          fill_color=PURPLE, fill_opacity=0.1).move_to(ORIGIN)
        # Outer dashed
        outer = DashedVMobject(
            Rectangle(width=5.6, height=4.4, color=PURPLE, stroke_width=2.5, fill_opacity=0),
            num_dashes=44).move_to(inner.get_center())
        # 14m label (top of inner)
        a14 = DoubleArrow(inner.get_corner(UL)+UP*0.25, inner.get_corner(UR)+UP*0.25,
                          color=PURPLE, stroke_width=2, tip_length=0.18, buff=0)
        l14 = poppins("14 m", 22, PURPLE).next_to(a14, UP, buff=0.12)
        # 12m label (right of inner)
        a12 = DoubleArrow(inner.get_corner(UR)+RIGHT*0.25, inner.get_corner(DR)+RIGHT*0.25,
                          color=PURPLE, stroke_width=2, tip_length=0.18, buff=0)
        l12 = poppins("12 m", 22, PURPLE).next_to(a12, RIGHT, buff=0.12)
        # 2m path width (between outer and inner, on left)
        a2 = DoubleArrow(outer.get_left()+UP*1.5, inner.get_left()+UP*1.5,
                         color=PURPLE, stroke_width=1.8, tip_length=0.14, buff=0)
        l2 = poppins("2 m", 18, PURPLE).next_to(a2, UP, buff=0.06)
        # Unknown ? in path band
        unk = unknown_mark(inner.get_top()+UP*0.6+RIGHT*2.0)

        with self.voiceover(
            text='It is a rectangular <bookmark mark="g1"/>vegetable patch, '
                 'fourteen metres <bookmark mark="g2"/>by twelve metres. '
                 'You want to build a <bookmark mark="g3"/>walking path all around it, '
                 'two metres wide. How many square metres <bookmark mark="g4"/>of tiles '
                 'do you need to buy?'
        ):
            self.play(FadeIn(bdg), run_time=0.5)
            self.wait_until_bookmark("g1")
            self.play(Create(inner), run_time=1.0)
            self.play(Create(a14), FadeIn(l14), run_time=0.6)
            self.wait_until_bookmark("g2")
            self.play(Create(a12), FadeIn(l12), run_time=0.6)
            self.wait_until_bookmark("g3")
            self.play(Create(outer), Create(a2), FadeIn(l2), run_time=1.0)
            self.wait_until_bookmark("g4")
            self.play(FadeIn(unk), run_time=0.6)
        self.wait(0.6)
        fade_all(self)

        # ════════════════════════════════════════════════════════
        # SCENE 4 — Trap warning (visual: warning sign + small park icon)
        # ════════════════════════════════════════════════════════
        bdg = heading_badge("The Trap")
        # Warning triangle
        tri = Polygon([0,0.8,0],[0.9,-0.7,0],[-0.9,-0.7,0],
                      color=ORANGE_HL, stroke_width=3,
                      fill_color=ORANGE_HL, fill_opacity=0.3).scale(0.9)
        excl = poppins("!", 60, ORANGE_HL, BOLD).move_to(tri.get_center()+DOWN*0.1)
        warn = VGroup(tri, excl).move_to(ORIGIN)
        decode = poppins("Decode the hidden trap.", 28, PURPLE).next_to(warn, DOWN, buff=0.7)

        with self.voiceover(
            text='This question appears <bookmark mark="tr1"/>straightforward, '
                 'but it hides a trap that has misled many learners. '
                 'Today we will <bookmark mark="tr2"/>decode it.'
        ):
            self.play(FadeIn(bdg), run_time=0.5)
            self.wait_until_bookmark("tr1")
            self.play(FadeIn(warn), run_time=0.9)
            self.wait_until_bookmark("tr2")
            self.play(FadeIn(decode), run_time=0.7)
        self.wait(0.5)
        fade_all(self)

        # ════════════════════════════════════════════════════════
        # SCENE 5 — Learning Objectives (icon cards)
        # ════════════════════════════════════════════════════════
        bdg = heading_badge("Learning Objectives")
        def obj(icon_mobj, text):
            tx = poppins(text, 22, PURPLE)
            row = VGroup(icon_mobj, tx).arrange(RIGHT, buff=0.4)
            return row
        # icon 1: small rectangle
        ic1 = Rectangle(width=0.7, height=0.45, color=PURPLE, stroke_width=2.5,
                        fill_color=PURPLE, fill_opacity=0.2)
        # icon 2: nested rectangles
        ic2_o = Rectangle(width=0.7, height=0.45, color=PURPLE, stroke_width=2.5,
                          fill_color=PURPLE, fill_opacity=0.2)
        ic2_i = Rectangle(width=0.4, height=0.22, color=ORANGE_HL, stroke_width=1.5)
        ic2_i.move_to(ic2_o.get_center())
        ic2 = VGroup(ic2_o, ic2_i)
        o1 = obj(ic1, "Area of any rectangle")
        o2 = obj(ic2, "Read composite figures")
        VGroup(o1, o2).arrange(DOWN, buff=0.7, aligned_edge=LEFT).move_to(ORIGIN)

        with self.voiceover(
            text='By the end you will <bookmark mark="lo1"/>find the area of any '
                 'rectangle. You will also <bookmark mark="lo2"/>read composite figures '
                 'before you compute.'
        ):
            self.play(FadeIn(bdg), run_time=0.5)
            self.wait_until_bookmark("lo1")
            self.play(FadeIn(o1), run_time=0.7)
            self.wait_until_bookmark("lo2")
            self.play(FadeIn(o2), run_time=0.7)
        self.wait(0.5)
        fade_all(self)

        # ════════════════════════════════════════════════════════
        # SCENE 6 — Roadmap (4 visual stages)
        # ════════════════════════════════════════════════════════
        bdg = heading_badge("Roadmap")
        labels = ["Meaning", "Formula", "Misconception", "Solve"]
        nodes = VGroup()
        for s in labels:
            c = Circle(radius=0.5, color=PURPLE, stroke_width=2.5,
                       fill_color=PALE_PURPLE, fill_opacity=0.3)
            lbl = poppins(s, 16, PURPLE, BOLD).next_to(c, DOWN, buff=0.25)
            nodes.add(VGroup(c, lbl))
        nodes.arrange(RIGHT, buff=1.0).move_to(ORIGIN)
        arrows = VGroup()
        for i in range(3):
            arrows.add(Arrow(nodes[i][0].get_right(), nodes[i+1][0].get_left(),
                             color=PURPLE, stroke_width=2,
                             buff=0.05, max_tip_length_to_length_ratio=0.2))

        with self.voiceover(
            text='We will revisit what area <bookmark mark="rm1"/>means. '
                 'Then build the rectangle <bookmark mark="rm2"/>formula, '
                 'confront a common <bookmark mark="rm3"/>misconception, '
                 'and solve the garden <bookmark mark="rm4"/>problem step by step.'
        ):
            self.play(FadeIn(bdg), run_time=0.5)
            self.wait_until_bookmark("rm1")
            self.play(FadeIn(nodes[0]), run_time=0.6)
            self.wait_until_bookmark("rm2")
            self.play(Create(arrows[0]), FadeIn(nodes[1]), run_time=0.6)
            self.wait_until_bookmark("rm3")
            self.play(Create(arrows[1]), FadeIn(nodes[2]), run_time=0.6)
            self.wait_until_bookmark("rm4")
            self.play(Create(arrows[2]), FadeIn(nodes[3]), run_time=0.6)
        self.wait(0.5)
        fade_all(self)

        # ════════════════════════════════════════════════════════
        # SCENE 7 — Rectangle Properties (figure with highlights)
        # ════════════════════════════════════════════════════════
        bdg = heading_badge("Rectangle Properties")
        rect = Rectangle(width=4.0, height=2.5, color=PURPLE, stroke_width=2.5,
                         fill_color=PURPLE, fill_opacity=0.1).move_to(ORIGIN)
        # right-angle marks
        ra = VGroup()
        for corner, off in [(UL, [0.18,-0.18,0]), (UR, [-0.18,-0.18,0]),
                            (DL, [0.18,0.18,0]), (DR, [-0.18,0.18,0])]:
            sq = Square(side_length=0.2, color=ORANGE_HL, stroke_width=2.5, fill_opacity=0)
            sq.move_to(rect.get_corner(corner) + np.array(off))
            ra.add(sq)
        # side labels
        a_top = poppins("a", 24, PURPLE).next_to(rect, UP, buff=0.15)
        a_bot = poppins("a", 24, PURPLE).next_to(rect, DOWN, buff=0.15)
        b_l = poppins("b", 24, PURPLE).next_to(rect, LEFT, buff=0.15)
        b_r = poppins("b", 24, PURPLE).next_to(rect, RIGHT, buff=0.15)
        # grid for unit-squares step
        grid = VGroup()
        cols, rows = 8, 5
        cw, ch = 4.0/cols, 2.5/rows
        for i in range(1, cols):
            x = rect.get_left()[0]+i*cw
            grid.add(Line([x, rect.get_bottom()[1],0],[x, rect.get_top()[1],0],
                          color=PALE_PURPLE, stroke_width=1))
        for j in range(1, rows):
            y = rect.get_bottom()[1]+j*ch
            grid.add(Line([rect.get_left()[0], y,0],[rect.get_right()[0], y,0],
                          color=PALE_PURPLE, stroke_width=1))

        with self.voiceover(
            text='A rectangle has four <bookmark mark="rp1"/>right angles, '
                 'and its opposite <bookmark mark="rp2"/>sides are equal. '
                 'We measure a surface by counting <bookmark mark="rp3"/>unit squares '
                 'that fit inside.'
        ):
            self.play(FadeIn(bdg), Create(rect), run_time=1.0)
            self.wait_until_bookmark("rp1")
            self.play(FadeIn(ra), run_time=0.7)
            self.play(Indicate(ra, color=ORANGE_HL), run_time=0.5)
            self.wait_until_bookmark("rp2")
            self.play(FadeIn(a_top), FadeIn(a_bot), FadeIn(b_l), FadeIn(b_r), run_time=0.7)
            self.play(a_top.animate.set_color(ORANGE_HL),
                      a_bot.animate.set_color(ORANGE_HL), run_time=0.4)
            self.play(a_top.animate.set_color(PURPLE),
                      a_bot.animate.set_color(PURPLE),
                      b_l.animate.set_color(ORANGE_HL),
                      b_r.animate.set_color(ORANGE_HL), run_time=0.4)
            self.play(b_l.animate.set_color(PURPLE),
                      b_r.animate.set_color(PURPLE), run_time=0.3)
            self.wait_until_bookmark("rp3")
            self.play(FadeIn(grid), run_time=0.9)
        self.wait(0.5)
        fade_all(self)

        # ════════════════════════════════════════════════════════
        # SCENE 8 — Foundation → Shortcut (visual: grid → equation)
        # ════════════════════════════════════════════════════════
        bdg = heading_badge("Foundation")
        # Left: small 4x3 numbered grid
        gw, gh = 1.8, 1.35
        gcols, grows = 4, 3
        grid8 = Rectangle(width=gw, height=gh, color=PURPLE, stroke_width=2.5,
                          fill_opacity=0).move_to(LEFT*3.5)
        gl8 = VGroup()
        cw, ch = gw/gcols, gh/grows
        for i in range(1, gcols):
            x = grid8.get_left()[0]+i*cw
            gl8.add(Line([x, grid8.get_bottom()[1],0],[x, grid8.get_top()[1],0],
                         color=PALE_PURPLE, stroke_width=1))
        for j in range(1, grows):
            y = grid8.get_bottom()[1]+j*ch
            gl8.add(Line([grid8.get_left()[0], y,0],[grid8.get_right()[0], y,0],
                         color=PALE_PURPLE, stroke_width=1))
        slow_cap = poppins("count 1,2,3...", 18, PURPLE).next_to(grid8, DOWN, buff=0.4)
        x_mark = poppins("✗", 28, ORANGE_HL, BOLD).next_to(slow_cap, RIGHT, buff=0.15)
        # arrow middle
        arr8 = Arrow(LEFT*1.2, RIGHT*1.2, color=PURPLE, stroke_width=3).move_to(ORIGIN)
        # Right: bolt + formula icon
        bolt = poppins("⚡", 60, ORANGE_HL, BOLD).move_to(RIGHT*3.5+UP*0.3)
        fast_cap = poppins("L × B", 30, PURPLE, BOLD).next_to(bolt, DOWN, buff=0.4)

        with self.voiceover(
            text='You can already <bookmark mark="fd1"/>count squares one by one. '
                 'Now we discover a powerful <bookmark mark="fd2"/>shortcut '
                 'so you never count <bookmark mark="fd3"/>one by one again.'
        ):
            self.play(FadeIn(bdg), run_time=0.5)
            self.wait_until_bookmark("fd1")
            self.play(Create(grid8), FadeIn(gl8), FadeIn(slow_cap), FadeIn(x_mark),
                      run_time=1.0)
            self.wait_until_bookmark("fd2")
            self.play(Create(arr8), FadeIn(bolt), run_time=0.8)
            self.wait_until_bookmark("fd3")
            self.play(FadeIn(fast_cap), run_time=0.7)
        self.wait(0.5)
        fade_all(self)

        # ════════════════════════════════════════════════════════
        # SCENE 9 — Pause & Reflect (visual thought bubble)
        # ════════════════════════════════════════════════════════
        bdg = heading_badge("Pause & Reflect")
        bubble = Ellipse(width=4.5, height=2.4, color=PURPLE, stroke_width=2.5,
                         fill_color=LAVENDER_BG, fill_opacity=1).shift(UP*0.7)
        # mini grid inside bubble
        mg = Rectangle(width=1.4, height=0.9, color=PURPLE, stroke_width=2,
                       fill_opacity=0).move_to(bubble.get_center())
        gl_in = VGroup()
        for i in range(1,4):
            x = mg.get_left()[0]+i*1.4/4
            gl_in.add(Line([x, mg.get_bottom()[1],0],[x, mg.get_top()[1],0],
                           color=PALE_PURPLE, stroke_width=1))
        for j in range(1,3):
            y = mg.get_bottom()[1]+j*0.9/3
            gl_in.add(Line([mg.get_left()[0], y,0],[mg.get_right()[0], y,0],
                           color=PALE_PURPLE, stroke_width=1))
        ready = poppins("Then you are ready!", 26, ORANGE_HL, BOLD).next_to(bubble, DOWN, buff=0.8)

        with self.voiceover(
            text='Ask yourself: can you picture a <bookmark mark="ps1"/>rectangle and '
                 'count the squares inside it? '
                 'If yes, you are <bookmark mark="ps2"/>prepared.'
        ):
            self.play(FadeIn(bdg), run_time=0.5)
            self.wait_until_bookmark("ps1")
            self.play(Create(bubble), Create(mg), FadeIn(gl_in), run_time=1.2)
            self.wait_until_bookmark("ps2")
            self.play(FadeIn(ready), run_time=0.8)
        self.wait(0.5)
        fade_all(self)

        # ════════════════════════════════════════════════════════
        # SCENE 10 — Rangoli (colorful grid, no extra text)
        # ════════════════════════════════════════════════════════
        bdg = heading_badge("Real-World")
        rg = Rectangle(width=4.5, height=2.7, color=PURPLE, stroke_width=2.5,
                       fill_opacity=0).move_to(ORIGIN)
        cols, rows = 6, 4
        cw, ch = 4.5/cols, 2.7/rows
        glines = VGroup()
        for i in range(1, cols):
            x = rg.get_left()[0]+i*cw
            glines.add(Line([x, rg.get_bottom()[1],0],[x, rg.get_top()[1],0],
                            color=PALE_PURPLE, stroke_width=1))
        for j in range(1, rows):
            y = rg.get_bottom()[1]+j*ch
            glines.add(Line([rg.get_left()[0], y,0],[rg.get_right()[0], y,0],
                            color=PALE_PURPLE, stroke_width=1))
        # Colorful fills
        fills = VGroup()
        cols_palette = [ORANGE_HL, PURPLE, PALE_PURPLE, ORANGE_HL, PURPLE, PALE_PURPLE]
        for idx, (r, c) in enumerate([(0,1),(1,3),(2,0),(0,4),(2,2),(1,5)]):
            cx = rg.get_left()[0]+(c+0.5)*cw
            cy = rg.get_bottom()[1]+(rows-1-r+0.5)*ch
            sq = Square(side_length=min(cw,ch)*0.85, color=PURPLE, stroke_width=1,
                        fill_color=cols_palette[idx % len(cols_palette)], fill_opacity=0.7)
            sq.move_to([cx,cy,0])
            fills.add(sq)
        cap = poppins("Each square = one unit of powder", 20, PURPLE).next_to(rg, DOWN, buff=0.5)

        with self.voiceover(
            text='Rangoli artists fill rectangular <bookmark mark="rg1"/>regions with '
                 'coloured powder. '
                 'To know how much powder they need, they count <bookmark mark="rg2"/>'
                 'unit squares.'
        ):
            self.play(FadeIn(bdg), run_time=0.5)
            self.wait_until_bookmark("rg1")
            self.play(Create(rg), FadeIn(glines), run_time=1.0)
            self.wait_until_bookmark("rg2")
            self.play(LaggedStart(*[FadeIn(s) for s in fills], lag_ratio=0.15),
                      FadeIn(cap), run_time=1.0)
        self.wait(0.5)
        fade_all(self)

        # ════════════════════════════════════════════════════════
        # SCENE 11 — Counting Rows 7×4 (with row-by-row reveal)
        # ════════════════════════════════════════════════════════
        bdg = heading_badge("Counting Rows")
        cell = 0.45
        cols, rows = 4, 7
        rect11 = Rectangle(width=cols*cell, height=rows*cell, color=PURPLE,
                           stroke_width=2.5, fill_opacity=0).move_to(LEFT*1.5)
        gl11 = VGroup()
        for i in range(1, cols):
            x = rect11.get_left()[0]+i*cell
            gl11.add(Line([x, rect11.get_bottom()[1],0],[x, rect11.get_top()[1],0],
                          color=PALE_PURPLE, stroke_width=1))
        for j in range(1, rows):
            y = rect11.get_bottom()[1]+j*cell
            gl11.add(Line([rect11.get_left()[0], y,0],[rect11.get_right()[0], y,0],
                          color=PALE_PURPLE, stroke_width=1))
        a7 = DoubleArrow(rect11.get_corner(UL)+LEFT*0.3, rect11.get_corner(DL)+LEFT*0.3,
                         color=PURPLE, stroke_width=2, tip_length=0.18, buff=0)
        l7 = poppins("7 cm", 22, PURPLE).next_to(a7, LEFT, buff=0.12)
        a4 = DoubleArrow(rect11.get_corner(UL)+UP*0.3, rect11.get_corner(UR)+UP*0.3,
                         color=PURPLE, stroke_width=2, tip_length=0.18, buff=0)
        l4 = poppins("4 cm", 22, PURPLE).next_to(a4, UP, buff=0.12)
        # row highlights
        row_hls = VGroup()
        for j in range(rows):
            row_y = rect11.get_top()[1] - (j+0.5)*cell
            r = Rectangle(width=cols*cell, height=cell, color=ORANGE_HL, stroke_width=0,
                          fill_color=ORANGE_HL, fill_opacity=0.4)
            r.move_to([rect11.get_center()[0], row_y, 0])
            row_hls.add(r)
        rcap = poppins("4 squares per row", 22, ORANGE_HL, BOLD).next_to(rect11, RIGHT, buff=0.8)
        rcap.move_to([rcap.get_x(), rect11.get_top()[1]-cell/2, 0])

        with self.voiceover(
            text='Look at this rectangle: <bookmark mark="cr1"/>seven centimetres tall, '
                 'four centimetres <bookmark mark="cr2"/>wide. '
                 'Each row holds <bookmark mark="cr3"/>four squares, '
                 'and there are <bookmark mark="cr4"/>seven such rows.'
        ):
            self.play(FadeIn(bdg), run_time=0.5)
            self.wait_until_bookmark("cr1")
            self.play(Create(rect11), FadeIn(gl11), Create(a7), FadeIn(l7), run_time=1.2)
            self.wait_until_bookmark("cr2")
            self.play(Create(a4), FadeIn(l4), run_time=0.7)
            self.wait_until_bookmark("cr3")
            self.play(FadeIn(row_hls[0]), FadeIn(rcap), run_time=0.6)
            self.wait_until_bookmark("cr4")
            self.play(LaggedStart(*[FadeIn(row_hls[j]) for j in range(1, rows)],
                                  lag_ratio=0.1), run_time=1.2)
        self.wait(0.5)
        fade_all(self)

        # ════════════════════════════════════════════════════════
        # SCENE 12 — Shortcut: 7×4=28
        # ════════════════════════════════════════════════════════
        bdg = heading_badge("The Shortcut")
        cell = 0.4
        cols, rows = 4, 7
        rect12 = Rectangle(width=cols*cell, height=rows*cell, color=PURPLE,
                           stroke_width=2.5, fill_color=ORANGE_HL, fill_opacity=0.35
                           ).move_to(LEFT*3)
        gl12 = VGroup()
        for i in range(1, cols):
            x = rect12.get_left()[0]+i*cell
            gl12.add(Line([x, rect12.get_bottom()[1],0],[x, rect12.get_top()[1],0],
                          color=PURPLE, stroke_width=1))
        for j in range(1, rows):
            y = rect12.get_bottom()[1]+j*cell
            gl12.add(Line([rect12.get_left()[0], y,0],[rect12.get_right()[0], y,0],
                          color=PURPLE, stroke_width=1))
        l7b = poppins("7 cm", 22, PURPLE).next_to(rect12, LEFT, buff=0.3)
        l4b = poppins("4 cm", 22, PURPLE).next_to(rect12, UP, buff=0.3)
        eq = MathTex("7", r"\times", "4", "=", "28", color=PURPLE, font_size=72)
        eq[4].set_color(ORANGE_HL)
        eq.move_to(RIGHT*2.5)

        with self.voiceover(
            text='Seven times four equals <bookmark mark="sh1"/>twenty-eight. '
                 'This is the heart of the <bookmark mark="sh2"/>formula.'
        ):
            self.play(FadeIn(bdg), Create(rect12), FadeIn(gl12),
                      FadeIn(l7b), FadeIn(l4b), run_time=1.2)
            self.play(FadeIn(eq[0]), FadeIn(eq[1]), FadeIn(eq[2]), run_time=0.6)
            self.wait_until_bookmark("sh1")
            self.play(FadeIn(eq[3]), FadeIn(eq[4]), run_time=0.7)
            self.wait_until_bookmark("sh2")
            self.play(Indicate(eq[4], color=ORANGE_HL, scale_factor=1.4), run_time=0.7)
        self.wait(0.5)
        fade_all(self)

        # ════════════════════════════════════════════════════════
        # SCENE 13 — The Formula A = l × w
        # ════════════════════════════════════════════════════════
        bdg = heading_badge("The Formula")
        A = MathTex("A", color=PURPLE, font_size=80)
        eq_sign = MathTex("=", color=PURPLE, font_size=80)
        l = MathTex("l", color=PURPLE, font_size=80)
        times = MathTex(r"\times", color=ORANGE_HL, font_size=80)
        w = MathTex("w", color=PURPLE, font_size=80)
        formula = VGroup(A, eq_sign, l, times, w).arrange(RIGHT, buff=0.3).move_to(ORIGIN)

        with self.voiceover(
            text='Area equals <bookmark mark="fm1"/>length '
                 'times <bookmark mark="fm2"/>breadth.'
        ):
            self.play(FadeIn(bdg), FadeIn(A), FadeIn(eq_sign), run_time=0.8)
            self.wait_until_bookmark("fm1")
            self.play(FadeIn(l), run_time=0.6)
            self.play(FadeIn(times), run_time=0.4)
            self.wait_until_bookmark("fm2")
            self.play(FadeIn(w), run_time=0.6)
        self.wait(0.5)
        fade_all(self)

        # ════════════════════════════════════════════════════════
        # SCENE 14 — Works For All (3 rect shapes)
        # ════════════════════════════════════════════════════════
        bdg = heading_badge("Every Rectangle")
        rA = Rectangle(width=3.5, height=0.6, color=PURPLE, stroke_width=2.5,
                       fill_color=PURPLE, fill_opacity=0.15)
        rB = Rectangle(width=2.2, height=1.8, color=PURPLE, stroke_width=2.5,
                       fill_color=PURPLE, fill_opacity=0.15)
        rC = Rectangle(width=1.6, height=1.6, color=PURPLE, stroke_width=2.5,
                       fill_color=PURPLE, fill_opacity=0.15)
        VGroup(rA, rB, rC).arrange(RIGHT, buff=0.8).move_to(ORIGIN)
        # checkmarks
        c1 = poppins("✓", 36, ORANGE_HL, BOLD).next_to(rA, UP, buff=0.2)
        c2 = poppins("✓", 36, ORANGE_HL, BOLD).next_to(rB, UP, buff=0.2)
        c3 = poppins("✓", 36, ORANGE_HL, BOLD).next_to(rC, UP, buff=0.2)

        with self.voiceover(
            text='This works for every <bookmark mark="wa1"/>rectangle: '
                 'long and thin, short and <bookmark mark="wa2"/>wide, '
                 'or a perfect <bookmark mark="wa3"/>square.'
        ):
            self.play(FadeIn(bdg), run_time=0.5)
            self.wait_until_bookmark("wa1")
            self.play(Create(rA), FadeIn(c1), run_time=0.7)
            self.wait_until_bookmark("wa2")
            self.play(Create(rB), FadeIn(c2), run_time=0.7)
            self.wait_until_bookmark("wa3")
            self.play(Create(rC), FadeIn(c3), run_time=0.7)
        self.wait(0.5)
        fade_all(self)

        # ════════════════════════════════════════════════════════
        # SCENE 15 — Units: 28 cm² (visual emphasis)
        # ════════════════════════════════════════════════════════
        bdg = heading_badge("Writing Units")
        ans = MathTex(r"28\,\text{cm}^2", color=ORANGE_HL, font_size=96).move_to(ORIGIN)
        circle_sup = Circle(radius=0.3, color=PURPLE, stroke_width=3)
        circle_sup.move_to(ans[0][-1].get_center())
        caption = poppins("the small two = square units",
                          22, PURPLE).next_to(ans, DOWN, buff=0.7)

        with self.voiceover(
            text='We write the answer as <bookmark mark="un1"/>twenty-eight centimetre '
                 'squared. The small two means <bookmark mark="un2"/>square units.'
        ):
            self.play(FadeIn(bdg), run_time=0.5)
            self.wait_until_bookmark("un1")
            self.play(FadeIn(ans), run_time=1.0)
            self.wait_until_bookmark("un2")
            self.play(Create(circle_sup), FadeIn(caption), run_time=0.8)
        self.wait(0.5)
        fade_all(self)

        # ════════════════════════════════════════════════════════
        # SCENE 16 — Square Special
        # ════════════════════════════════════════════════════════
        bdg = heading_badge("Square: Special Rectangle")
        sq = Square(side_length=2.5, color=PURPLE, stroke_width=2.5,
                    fill_color=PURPLE, fill_opacity=0.15).move_to(LEFT*2.8)
        a_t = DoubleArrow(sq.get_corner(UL)+UP*0.3, sq.get_corner(UR)+UP*0.3,
                          color=ORANGE_HL, stroke_width=2, tip_length=0.18, buff=0)
        l_t = poppins("s", 24, ORANGE_HL).next_to(a_t, UP, buff=0.12)
        a_r = DoubleArrow(sq.get_corner(UR)+RIGHT*0.3, sq.get_corner(DR)+RIGHT*0.3,
                          color=ORANGE_HL, stroke_width=2, tip_length=0.18, buff=0)
        l_r = poppins("s", 24, ORANGE_HL).next_to(a_r, RIGHT, buff=0.12)
        formula_sq = MathTex("A", "=", "s", r"\times", "s",
                             color=PURPLE, font_size=64).move_to(RIGHT*2.8)
        formula_sq[3].set_color(ORANGE_HL)

        with self.voiceover(
            text='A square has equal <bookmark mark="sq1"/>sides. '
                 'So its area is side times <bookmark mark="sq2"/>side.'
        ):
            self.play(FadeIn(bdg), Create(sq), run_time=1.0)
            self.wait_until_bookmark("sq1")
            self.play(Create(a_t), FadeIn(l_t), Create(a_r), FadeIn(l_r), run_time=1.0)
            self.wait_until_bookmark("sq2")
            self.play(FadeIn(formula_sq), run_time=0.8)
        self.wait(0.5)
        fade_all(self)

        # ════════════════════════════════════════════════════════
        # SCENE 17 — Why × Works (crowd analogy)
        # ════════════════════════════════════════════════════════
        bdg = heading_badge("Why Multiplication Works")
        seats = VGroup()
        for r in range(4):
            for c in range(5):
                d = Dot(radius=0.2, color=PURPLE).set_fill(PALE_PURPLE, opacity=1)
                d.move_to([-1.0+c*0.55, 0.8-r*0.55, 0])
                seats.add(d)
        seats.move_to(LEFT*3)
        br_t = Brace(seats, UP, color=PURPLE)
        br_t_l = poppins("5 seats", 20, PURPLE).next_to(br_t, UP, buff=0.1)
        br_l = Brace(seats, LEFT, color=PURPLE)
        br_l_l = poppins("4 rows", 20, PURPLE).next_to(br_l, LEFT, buff=0.1)
        eq17 = MathTex(r"4 \times 5 = 20", color=PURPLE, font_size=56)
        eq17[0][-2:].set_color(ORANGE_HL)
        eq17.move_to(RIGHT*2.8)

        with self.voiceover(
            text='Think of area as a <bookmark mark="wm1"/>crowd in rows. '
                 'Rows times seats gives <bookmark mark="wm2"/>total people, '
                 'exactly like rows times <bookmark mark="wm3"/>columns of squares.'
        ):
            self.play(FadeIn(bdg), run_time=0.5)
            self.wait_until_bookmark("wm1")
            self.play(FadeIn(seats), run_time=0.9)
            self.play(FadeIn(br_t), FadeIn(br_t_l), FadeIn(br_l), FadeIn(br_l_l), run_time=0.7)
            self.wait_until_bookmark("wm2")
            self.play(FadeIn(eq17), run_time=0.7)
            self.wait_until_bookmark("wm3")
            self.play(Indicate(eq17, color=ORANGE_HL), run_time=0.6)
        self.wait(0.5)
        fade_all(self)

        # ════════════════════════════════════════════════════════
        # SCENE 18 — Order doesn't matter (visual flip)
        # ════════════════════════════════════════════════════════
        bdg = heading_badge("Order Doesn't Matter")
        # Two grids
        cell = 0.4
        gA = Rectangle(width=4*cell, height=7*cell, color=PURPLE, stroke_width=2.5,
                       fill_color=ORANGE_HL, fill_opacity=0.3).move_to(LEFT*3)
        glA = VGroup()
        for i in range(1, 4):
            x = gA.get_left()[0]+i*cell
            glA.add(Line([x, gA.get_bottom()[1],0],[x, gA.get_top()[1],0],
                         color=PURPLE, stroke_width=1))
        for j in range(1, 7):
            y = gA.get_bottom()[1]+j*cell
            glA.add(Line([gA.get_left()[0], y,0],[gA.get_right()[0], y,0],
                         color=PURPLE, stroke_width=1))
        eA = MathTex(r"7 \times 4 = 28", color=PURPLE, font_size=32).next_to(gA, DOWN, buff=0.3)
        eq_sign18 = MathTex("=", color=ORANGE_HL, font_size=72).move_to(ORIGIN)
        gB = Rectangle(width=7*cell, height=4*cell, color=PURPLE, stroke_width=2.5,
                       fill_color=ORANGE_HL, fill_opacity=0.3).move_to(RIGHT*3)
        glB = VGroup()
        for i in range(1, 7):
            x = gB.get_left()[0]+i*cell
            glB.add(Line([x, gB.get_bottom()[1],0],[x, gB.get_top()[1],0],
                         color=PURPLE, stroke_width=1))
        for j in range(1, 4):
            y = gB.get_bottom()[1]+j*cell
            glB.add(Line([gB.get_left()[0], y,0],[gB.get_right()[0], y,0],
                         color=PURPLE, stroke_width=1))
        eB = MathTex(r"4 \times 7 = 28", color=PURPLE, font_size=32).next_to(gB, DOWN, buff=0.3)

        with self.voiceover(
            text='Does it matter which side we call <bookmark mark="od1"/>length? '
                 'No. Seven times four and four times seven both give '
                 '<bookmark mark="od2"/>twenty-eight.'
        ):
            self.play(FadeIn(bdg), run_time=0.5)
            self.wait_until_bookmark("od1")
            self.play(Create(gA), FadeIn(glA), FadeIn(eA), run_time=1.0)
            self.play(Create(gB), FadeIn(glB), FadeIn(eB), run_time=1.0)
            self.wait_until_bookmark("od2")
            self.play(FadeIn(eq_sign18), run_time=0.6)
        self.wait(0.5)
        fade_all(self)

        # ════════════════════════════════════════════════════════
        # SCENE 19 — Same Perimeter Different Area
        # ════════════════════════════════════════════════════════
        bdg = heading_badge("Same Perimeter, Different Area")
        # 4x1 rect
        r1 = Rectangle(width=3.2, height=0.8, color=PURPLE, stroke_width=2.5,
                       fill_color=PURPLE, fill_opacity=0.15).move_to(LEFT*3+UP*0.7)
        r1_t = poppins("4 × 1", 18, PURPLE).next_to(r1, UP, buff=0.15)
        r1_pa = VGroup(
            MathTex("P = 10", color=PURPLE, font_size=30),
            MathTex("A = 4", color=ORANGE_HL, font_size=30),
        ).arrange(DOWN, buff=0.15).next_to(r1, DOWN, buff=0.4)
        # 3x2 rect
        r2 = Rectangle(width=2.4, height=1.6, color=PURPLE, stroke_width=2.5,
                       fill_color=PURPLE, fill_opacity=0.15).move_to(RIGHT*3+UP*0.3)
        r2_t = poppins("3 × 2", 18, PURPLE).next_to(r2, UP, buff=0.15)
        r2_pa = VGroup(
            MathTex("P = 10", color=PURPLE, font_size=30),
            MathTex("A = 6", color=ORANGE_HL, font_size=30),
        ).arrange(DOWN, buff=0.15).next_to(r2, DOWN, buff=0.4)

        with self.voiceover(
            text='Two rectangles can share the same <bookmark mark="sp1"/>perimeter '
                 'but have completely different <bookmark mark="sp2"/>areas. '
                 'Same boundary, different <bookmark mark="sp3"/>space inside.'
        ):
            self.play(FadeIn(bdg), run_time=0.5)
            self.wait_until_bookmark("sp1")
            self.play(Create(r1), FadeIn(r1_t), Create(r2), FadeIn(r2_t), run_time=1.2)
            self.wait_until_bookmark("sp2")
            self.play(FadeIn(r1_pa), FadeIn(r2_pa), run_time=0.9)
            self.wait_until_bookmark("sp3")
            self.play(Indicate(r1_pa[1], color=ORANGE_HL),
                      Indicate(r2_pa[1], color=ORANGE_HL), run_time=0.7)
        self.wait(0.5)
        fade_all(self)

        # ════════════════════════════════════════════════════════
        # SCENE 20 — Fence vs Field (memory aid)
        # ════════════════════════════════════════════════════════
        bdg = heading_badge("Fence vs Field")
        # Fence (outline)
        fence = DashedVMobject(Rectangle(width=3.0, height=2.0, color=PURPLE,
                                         stroke_width=4), num_dashes=30).move_to(LEFT*3)
        fence_lbl = poppins("Perimeter = Fence", 22, PURPLE, BOLD).next_to(fence, DOWN, buff=0.4)
        # Field (filled)
        field = Rectangle(width=3.0, height=2.0, color=PURPLE, stroke_width=2.5,
                          fill_color=ORANGE_HL, fill_opacity=0.5).move_to(RIGHT*3)
        field_lbl = poppins("Area = Field", 22, ORANGE_HL, BOLD).next_to(field, DOWN, buff=0.4)

        with self.voiceover(
            text='Memory aid. Perimeter is the <bookmark mark="ff1"/>fence. '
                 'Area is the <bookmark mark="ff2"/>field. '
                 'Same fence can enclose different <bookmark mark="ff3"/>fields.'
        ):
            self.play(FadeIn(bdg), run_time=0.5)
            self.wait_until_bookmark("ff1")
            self.play(Create(fence), FadeIn(fence_lbl), run_time=1.0)
            self.wait_until_bookmark("ff2")
            self.play(Create(field), FadeIn(field_lbl), run_time=1.0)
            self.wait_until_bookmark("ff3")
            self.play(Indicate(field, color=ORANGE_HL), run_time=0.7)
        self.wait(0.5)
        fade_all(self)

        # ════════════════════════════════════════════════════════
        # SCENES 21-26 — Garden Problem with PERSISTENT FIGURE
        # ════════════════════════════════════════════════════════
        # Build the persistent figure once
        bdg = heading_badge("The Garden Problem")
        inner_p = Rectangle(width=3.6, height=2.4, color=PURPLE, stroke_width=2.5,
                            fill_color=PURPLE, fill_opacity=0.1).move_to(RIGHT*3+DOWN*0.3)
        outer_p = DashedVMobject(Rectangle(width=4.6, height=3.4, color=PURPLE,
                                           stroke_width=2.5, fill_opacity=0),
                                 num_dashes=44).move_to(inner_p.get_center())
        a14_p = DoubleArrow(inner_p.get_corner(UL)+UP*0.2, inner_p.get_corner(UR)+UP*0.2,
                            color=PURPLE, stroke_width=2, tip_length=0.15, buff=0)
        l14_p = poppins("14 m", 18, PURPLE).next_to(a14_p, UP, buff=0.08)
        a12_p = DoubleArrow(inner_p.get_corner(UR)+RIGHT*0.2, inner_p.get_corner(DR)+RIGHT*0.2,
                            color=PURPLE, stroke_width=2, tip_length=0.15, buff=0)
        l12_p = poppins("12 m", 18, PURPLE).next_to(a12_p, RIGHT, buff=0.08)
        a2_p = DoubleArrow(outer_p.get_left()+UP*1.2, inner_p.get_left()+UP*1.2,
                           color=PURPLE, stroke_width=1.8, tip_length=0.12, buff=0)
        l2_p = poppins("2 m", 16, PURPLE).next_to(a2_p, UP, buff=0.05)

        with self.voiceover(
            text='A rectangular park measures <bookmark mark="pb1"/>fourteen by twelve '
                 'metres. A two-metre path is built <bookmark mark="pb2"/>around the '
                 'outside. Find the area <bookmark mark="pb3"/>of the path.'
        ):
            self.play(FadeIn(bdg), run_time=0.5)
            self.wait_until_bookmark("pb1")
            self.play(Create(inner_p), Create(a14_p), FadeIn(l14_p),
                      Create(a12_p), FadeIn(l12_p), run_time=1.4)
            self.wait_until_bookmark("pb2")
            self.play(Create(outer_p), Create(a2_p), FadeIn(l2_p), run_time=1.2)
            self.wait_until_bookmark("pb3")
            ask_q = unknown_mark(inner_p.get_top()+UP*0.5+RIGHT*1.5)
            self.play(FadeIn(ask_q), run_time=0.5)
        self.wait(0.5)
        # Don't fade — keep persistent figure for next scenes
        figure = VGroup(inner_p, outer_p, a14_p, l14_p, a12_p, l12_p, a2_p, l2_p)

        # Move figure to far right for solution phase
        self.play(figure.animate.scale(0.85).to_edge(RIGHT, buff=0.6),
                  FadeOut(ask_q), run_time=1.0)

        # ════════════════════════════════════════════════════════
        # SCENE 22 — Outer-minus-Inner concept (visual eq with figure persisting)
        # ════════════════════════════════════════════════════════
        new_bdg = heading_badge("Composite Figure")
        # Mini visual equation on left
        m_outer = Rectangle(width=1.1, height=0.85, color=PURPLE, stroke_width=2,
                            fill_color=PURPLE, fill_opacity=0.15)
        m_minus = MathTex("-", color=PURPLE, font_size=40)
        m_inner = Rectangle(width=0.85, height=0.6, color=PURPLE, stroke_width=2,
                            fill_color=PURPLE, fill_opacity=0.4)
        m_eq = MathTex("=", color=PURPLE, font_size=40)
        m_path = Rectangle(width=1.1, height=0.85, color=ORANGE_HL, stroke_width=2,
                           fill_color=ORANGE_HL, fill_opacity=0.3)
        mini_eq = VGroup(m_outer, m_minus, m_inner, m_eq, m_path).arrange(RIGHT, buff=0.2)
        mini_eq.move_to(LEFT*3.5+UP*1.0)
        concept = poppins("Path = Outer − Inner", 26, ORANGE_HL, BOLD).next_to(mini_eq, DOWN, buff=0.5)

        with self.voiceover(
            text='The path is the difference: <bookmark mark="cf1"/>outer rectangle '
                 'minus the inner <bookmark mark="cf2"/>park.'
        ):
            self.play(FadeOut(bdg), FadeIn(new_bdg), run_time=0.5)
            bdg = new_bdg
            self.wait_until_bookmark("cf1")
            self.play(FadeIn(mini_eq), run_time=0.9)
            self.wait_until_bookmark("cf2")
            self.play(FadeIn(concept), run_time=0.7)
        self.wait(0.5)
        self.play(FadeOut(mini_eq), FadeOut(concept), run_time=0.6)

        # ════════════════════════════════════════════════════════
        # SCENE 23 — Step 1: Outer Dimensions (highlight outer + calc left)
        # ════════════════════════════════════════════════════════
        new_bdg = heading_badge("Step 1: Outer Dimensions")
        # New arrows on outer (orange)
        a18 = DoubleArrow(outer_p.get_corner(UL)+UP*0.2, outer_p.get_corner(UR)+UP*0.2,
                          color=ORANGE_HL, stroke_width=2, tip_length=0.15, buff=0)
        l18 = poppins("18 m", 18, ORANGE_HL, BOLD).next_to(a18, UP, buff=0.08)
        a16 = DoubleArrow(outer_p.get_corner(UR)+RIGHT*0.2, outer_p.get_corner(DR)+RIGHT*0.2,
                          color=ORANGE_HL, stroke_width=2, tip_length=0.15, buff=0)
        l16 = poppins("16 m", 18, ORANGE_HL, BOLD).next_to(a16, RIGHT, buff=0.08)
        # Calc on left
        calc1 = MathTex("14 + 2 + 2", "=", "18", color=PURPLE, font_size=36)
        calc1[2].set_color(ORANGE_HL)
        calc2 = MathTex("12 + 2 + 2", "=", "16", color=PURPLE, font_size=36)
        calc2[2].set_color(ORANGE_HL)
        VGroup(calc1, calc2).arrange(DOWN, buff=0.5).move_to(LEFT*3.5)

        with self.voiceover(
            text='Outer length: fourteen plus two plus two equals '
                 '<bookmark mark="s1a"/>eighteen metres. '
                 'Outer breadth: twelve plus two plus two equals '
                 '<bookmark mark="s1b"/>sixteen metres.'
        ):
            self.play(FadeOut(bdg), FadeIn(new_bdg), run_time=0.5)
            bdg = new_bdg
            self.play(FadeIn(calc1), run_time=0.8)
            self.wait_until_bookmark("s1a")
            self.play(Create(a18), FadeIn(l18),
                      Indicate(outer_p, color=ORANGE_HL), run_time=0.8)
            self.play(FadeIn(calc2), run_time=0.8)
            self.wait_until_bookmark("s1b")
            self.play(Create(a16), FadeIn(l16), run_time=0.7)
        self.wait(0.5)
        # Keep calcs + new arrows for now; will be cleared with next step
        prev_calcs = VGroup(calc1, calc2)
        outer_orange = VGroup(a18, l18, a16, l16)

        # ════════════════════════════════════════════════════════
        # SCENE 24 — Step 2: Outer Area (highlight outer fill)
        # ════════════════════════════════════════════════════════
        new_bdg = heading_badge("Step 2: Outer Area")
        # Highlight outer figure (fill it)
        outer_fill = Rectangle(width=outer_p.width, height=outer_p.height,
                               color=ORANGE_HL, stroke_width=0,
                               fill_color=ORANGE_HL, fill_opacity=0.25)
        outer_fill.move_to(outer_p.get_center())
        outer_fill.set_z_index(-1)
        # Calculation
        s2 = MathTex(r"A_{\text{outer}}", "=", "18", r"\times", "16", "=", "288",
                     color=PURPLE, font_size=42)
        s2[3].set_color(ORANGE_HL)
        s2[6].set_color(ORANGE_HL)
        s2.move_to(LEFT*3.5)
        s2_u = MathTex(r"288 \,\text{m}^2", color=ORANGE_HL, font_size=44).next_to(s2, DOWN, buff=0.5)

        with self.voiceover(
            text='Outer area: eighteen times sixteen equals '
                 '<bookmark mark="s2a"/>two-eighty-eight square metres.'
        ):
            self.play(FadeOut(bdg), FadeIn(new_bdg),
                      FadeOut(prev_calcs), run_time=0.6)
            bdg = new_bdg
            self.play(FadeIn(outer_fill), FadeIn(s2), run_time=1.0)
            self.wait_until_bookmark("s2a")
            self.play(FadeIn(s2_u), Indicate(s2_u, color=ORANGE_HL), run_time=0.9)
        self.wait(0.5)
        prev_calcs = VGroup(s2, s2_u)
        self.play(FadeOut(outer_fill), run_time=0.4)

        # ════════════════════════════════════════════════════════
        # SCENE 25 — Step 3: Inner Area (highlight inner)
        # ════════════════════════════════════════════════════════
        new_bdg = heading_badge("Step 3: Inner Area")
        inner_fill = Rectangle(width=inner_p.width, height=inner_p.height,
                               color=ORANGE_HL, stroke_width=0,
                               fill_color=ORANGE_HL, fill_opacity=0.4)
        inner_fill.move_to(inner_p.get_center())
        inner_fill.set_z_index(-1)
        s3 = MathTex(r"A_{\text{inner}}", "=", "14", r"\times", "12", "=", "168",
                     color=PURPLE, font_size=42)
        s3[3].set_color(ORANGE_HL)
        s3[6].set_color(ORANGE_HL)
        s3.move_to(LEFT*3.5)
        s3_u = MathTex(r"168\,\text{m}^2", color=ORANGE_HL, font_size=44).next_to(s3, DOWN, buff=0.5)

        with self.voiceover(
            text='Inner area: fourteen times twelve equals '
                 '<bookmark mark="s3a"/>one hundred sixty-eight square metres.'
        ):
            self.play(FadeOut(bdg), FadeIn(new_bdg),
                      FadeOut(prev_calcs), run_time=0.6)
            bdg = new_bdg
            self.play(FadeIn(inner_fill), FadeIn(s3), run_time=1.0)
            self.wait_until_bookmark("s3a")
            self.play(FadeIn(s3_u), Indicate(s3_u, color=ORANGE_HL), run_time=0.9)
        self.wait(0.5)
        prev_calcs = VGroup(s3, s3_u)
        self.play(FadeOut(inner_fill), run_time=0.4)

        # ════════════════════════════════════════════════════════
        # SCENE 26 — Step 4: Path Area (highlight path band)
        # ════════════════════════════════════════════════════════
        new_bdg = heading_badge("Step 4: Path Area")
        # Path band highlight (frame between outer and inner)
        path_band = Difference(
            Rectangle(width=outer_p.width, height=outer_p.height, fill_opacity=1),
            Rectangle(width=inner_p.width, height=inner_p.height, fill_opacity=1),
            color=ORANGE_HL, stroke_width=0, fill_color=ORANGE_HL, fill_opacity=0.5
        )
        path_band.move_to(outer_p.get_center())
        path_band.set_z_index(-1)
        s4 = MathTex(r"A_{\text{path}}", "=", "288", "-", "168",
                     color=PURPLE, font_size=42).move_to(LEFT*3.5+UP*0.3)
        ans4 = MathTex("=", r"120\,\text{m}^2",
                       color=ORANGE_HL, font_size=64).next_to(s4, DOWN, buff=0.5)

        with self.voiceover(
            text='Path area: two-eighty-eight minus one-sixty-eight equals '
                 '<bookmark mark="s4a"/>one hundred twenty <bookmark mark="s4b"/>'
                 'square metres.'
        ):
            self.play(FadeOut(bdg), FadeIn(new_bdg),
                      FadeOut(prev_calcs), run_time=0.6)
            bdg = new_bdg
            self.play(FadeIn(path_band), FadeIn(s4), run_time=1.0)
            self.wait_until_bookmark("s4a")
            self.play(FadeIn(ans4), run_time=1.0)
            self.wait_until_bookmark("s4b")
            self.play(Indicate(ans4, color=ORANGE_HL, scale_factor=1.2), run_time=0.8)
        self.wait(0.8)
        fade_all(self)

        # ════════════════════════════════════════════════════════
        # SCENE 27 — Verify (checklist visual)
        # ════════════════════════════════════════════════════════
        bdg = heading_badge("Verification")
        items = VGroup(
            VGroup(poppins("✓", 32, ORANGE_HL, BOLD),
                   MathTex(r"120\,\text{m}^2", color=PURPLE, font_size=36)
                  ).arrange(RIGHT, buff=0.3),
            VGroup(poppins("✓", 32, ORANGE_HL, BOLD),
                   poppins("Near prediction (~100)", 24, PURPLE)
                  ).arrange(RIGHT, buff=0.3),
            VGroup(poppins("✓", 32, ORANGE_HL, BOLD),
                   poppins("Units are m² (area)", 24, PURPLE)
                  ).arrange(RIGHT, buff=0.3),
        ).arrange(DOWN, buff=0.5, aligned_edge=LEFT).move_to(ORIGIN)

        with self.voiceover(
            text='Does this make sense? Path is <bookmark mark="v1"/>one hundred twenty '
                 'square metres. The prediction was <bookmark mark="v2"/>close. '
                 'And the units are <bookmark mark="v3"/>square metres.'
        ):
            self.play(FadeIn(bdg), run_time=0.5)
            self.wait_until_bookmark("v1")
            self.play(FadeIn(items[0]), run_time=0.7)
            self.wait_until_bookmark("v2")
            self.play(FadeIn(items[1]), run_time=0.7)
            self.wait_until_bookmark("v3")
            self.play(FadeIn(items[2]), run_time=0.7)
        self.wait(0.5)
        fade_all(self)

        # ════════════════════════════════════════════════════════
        # SCENE 28 — Key Insight (formula visual)
        # ════════════════════════════════════════════════════════
        bdg = heading_badge("Key Insight")
        f1 = MathTex(r"\text{Outer Length}", "=", "L", "+", "2w",
                     color=PURPLE, font_size=44)
        f1[4].set_color(ORANGE_HL)
        f2 = MathTex(r"\text{Outer Breadth}", "=", "B", "+", "2w",
                     color=PURPLE, font_size=44)
        f2[4].set_color(ORANGE_HL)
        VGroup(f1, f2).arrange(DOWN, buff=0.6).move_to(ORIGIN)

        with self.voiceover(
            text='When a path surrounds a rectangle, the outer dimensions grow by '
                 '<bookmark mark="ki1"/>twice the path width.'
        ):
            self.play(FadeIn(bdg), run_time=0.5)
            self.wait_until_bookmark("ki1")
            self.play(FadeIn(f1), FadeIn(f2), run_time=1.0)
            self.play(Indicate(f1[4], color=ORANGE_HL),
                      Indicate(f2[4], color=ORANGE_HL), run_time=0.7)
        self.wait(0.5)
        fade_all(self)

        # ════════════════════════════════════════════════════════
        # SCENE 29 — Misconception confronted (split visual)
        # ════════════════════════════════════════════════════════
        bdg = heading_badge("Misconception")
        # Left: misconception
        mis_text = poppins("Same Perimeter = Same Area?",
                           22, PURPLE).move_to(UP*2.5)
        strike = Line(mis_text.get_left()+LEFT*0.1, mis_text.get_right()+RIGHT*0.1,
                      color=ORANGE_HL, stroke_width=4)
        # Two rectangles
        r1m = Rectangle(width=3.2, height=0.8, color=PURPLE, stroke_width=2.5,
                        fill_color=PURPLE, fill_opacity=0.15).move_to(LEFT*3+DOWN*0.3)
        r1m_a = MathTex("A=4", color=ORANGE_HL, font_size=32).next_to(r1m, DOWN, buff=0.3)
        r2m = Rectangle(width=2.4, height=1.6, color=PURPLE, stroke_width=2.5,
                        fill_color=PURPLE, fill_opacity=0.15).move_to(RIGHT*3+DOWN*0.3)
        r2m_a = MathTex("A=6", color=ORANGE_HL, font_size=32).next_to(r2m, DOWN, buff=0.3)
        same_p = MathTex("P=10", color=PURPLE, font_size=24).move_to(DOWN*2.5+LEFT*3)
        same_p2 = MathTex("P=10", color=PURPLE, font_size=24).move_to(DOWN*2.5+RIGHT*3)

        with self.voiceover(
            text='Same perimeter does <bookmark mark="ms1"/>not mean same area. '
                 'Four-by-one and three-by-two share perimeter ten, '
                 'but areas are <bookmark mark="ms2"/>four and six.'
        ):
            self.play(FadeIn(bdg), FadeIn(mis_text), run_time=0.7)
            self.wait_until_bookmark("ms1")
            self.play(Create(strike), run_time=0.5)
            self.play(Create(r1m), Create(r2m),
                      FadeIn(same_p), FadeIn(same_p2), run_time=1.0)
            self.wait_until_bookmark("ms2")
            self.play(FadeIn(r1m_a), FadeIn(r2m_a), run_time=0.8)
        self.wait(0.5)
        fade_all(self)

        # ════════════════════════════════════════════════════════
        # SCENE 30 — Unit Error (m vs m²)
        # ════════════════════════════════════════════════════════
        bdg = heading_badge("Unit Error")
        wrong = MathTex(r"120\,\text{m}", color=PURPLE, font_size=72).move_to(LEFT*3)
        strike2 = Line(wrong.get_left()+LEFT*0.1, wrong.get_right()+RIGHT*0.1,
                       color=ORANGE_HL, stroke_width=5)
        # line icon
        line_icon = Line(LEFT*1, RIGHT*1, color=PURPLE, stroke_width=4).next_to(wrong, DOWN, buff=0.6)
        line_cap = poppins("a line", 20, PURPLE).next_to(line_icon, DOWN, buff=0.2)
        # right side
        right_m2 = MathTex(r"120\,\text{m}^2", color=ORANGE_HL, font_size=72).move_to(RIGHT*3)
        surf = Rectangle(width=1.6, height=1.0, color=ORANGE_HL, stroke_width=2,
                         fill_color=ORANGE_HL, fill_opacity=0.4).next_to(right_m2, DOWN, buff=0.5)
        surf_cap = poppins("a surface", 20, ORANGE_HL, BOLD).next_to(surf, DOWN, buff=0.2)

        with self.voiceover(
            text='Be careful with units. One hundred twenty metres is '
                 '<bookmark mark="ue1"/>a line. '
                 'But tiles cover <bookmark mark="ue2"/>a surface, so the answer must '
                 'be square metres.'
        ):
            self.play(FadeIn(bdg), run_time=0.5)
            self.wait_until_bookmark("ue1")
            self.play(FadeIn(wrong), Create(line_icon), FadeIn(line_cap), run_time=0.9)
            self.play(Create(strike2), run_time=0.5)
            self.wait_until_bookmark("ue2")
            self.play(FadeIn(right_m2), Create(surf), FadeIn(surf_cap), run_time=1.0)
        self.wait(0.5)
        fade_all(self)

        # ════════════════════════════════════════════════════════
        # SCENE 31 — Connections (tree to other shapes)
        # ════════════════════════════════════════════════════════
        bdg = heading_badge("Connections")
        center_node = Rectangle(width=2.4, height=0.9, color=PURPLE, stroke_width=2.5,
                                fill_color=PURPLE, fill_opacity=0.2).move_to(UP*1.5)
        center_lbl = poppins("Rectangle", 22, PURPLE, BOLD).move_to(center_node.get_center())
        # 3 child shapes
        para = Polygon([-1,0,0],[1,0,0],[0.6,0.8,0],[-1.4,0.8,0],
                       color=PURPLE, stroke_width=2.5,
                       fill_color=ORANGE_HL, fill_opacity=0.2).scale(0.6)
        rhom = Polygon([0,0.6,0],[0.7,0,0],[0,-0.6,0],[-0.7,0,0],
                       color=PURPLE, stroke_width=2.5,
                       fill_color=ORANGE_HL, fill_opacity=0.2).scale(0.8)
        trap = Polygon([-1,-0.4,0],[1,-0.4,0],[0.6,0.4,0],[-0.6,0.4,0],
                       color=PURPLE, stroke_width=2.5,
                       fill_color=ORANGE_HL, fill_opacity=0.2).scale(0.8)
        shapes = VGroup(para, rhom, trap).arrange(RIGHT, buff=1.5).move_to(DOWN*1.5)
        labels_n = VGroup(
            poppins("Parallelogram", 14, PURPLE).next_to(para, DOWN, buff=0.2),
            poppins("Rhombus", 14, PURPLE).next_to(rhom, DOWN, buff=0.2),
            poppins("Trapezium", 14, PURPLE).next_to(trap, DOWN, buff=0.2),
        )
        connectors = VGroup(*[Line(center_node.get_bottom(), s.get_top(),
                                   color=PURPLE, stroke_width=2)
                              for s in shapes])

        with self.voiceover(
            text='Every quadrilateral area formula <bookmark mark="cn1"/>builds on the '
                 'rectangle. Tomorrow we cut and rearrange to <bookmark mark="cn2"/>'
                 'reach the others.'
        ):
            self.play(FadeIn(bdg), Create(center_node), FadeIn(center_lbl), run_time=0.9)
            self.wait_until_bookmark("cn1")
            self.play(Create(connectors), Create(shapes), FadeIn(labels_n), run_time=1.4)
            self.wait_until_bookmark("cn2")
            self.play(Indicate(shapes, color=ORANGE_HL), run_time=0.7)
        self.wait(0.5)
        fade_all(self)

        # ════════════════════════════════════════════════════════
        # SCENE 32 — Triangle Preview
        # ════════════════════════════════════════════════════════
        bdg = heading_badge("Next: Triangle Area")
        rect_t = DashedVMobject(Rectangle(width=4.0, height=2.5, color=PURPLE,
                                          stroke_width=2.5), num_dashes=40).move_to(ORIGIN)
        tri = Polygon(rect_t.get_corner(DL), rect_t.get_corner(DR), rect_t.get_top(),
                      color=PURPLE, stroke_width=2.5,
                      fill_color=ORANGE_HL, fill_opacity=0.4)

        with self.voiceover(
            text='Next we will find the area of a triangle by drawing a '
                 '<bookmark mark="tp1"/>rectangle around it.'
        ):
            self.play(FadeIn(bdg), run_time=0.5)
            self.wait_until_bookmark("tp1")
            self.play(Create(rect_t), run_time=0.9)
            self.play(Create(tri), run_time=0.9)
        self.wait(0.5)
        fade_all(self)

        # ════════════════════════════════════════════════════════
        # SCENE 33 — Your Turn (Problem with persistent figure)
        # ════════════════════════════════════════════════════════
        bdg = heading_badge("Your Turn")
        inner_c = Rectangle(width=3.8, height=2.4, color=PURPLE, stroke_width=2.5,
                            fill_color=PURPLE, fill_opacity=0.1).move_to(RIGHT*2.5)
        outer_c = DashedVMobject(Rectangle(width=4.6, height=3.2, color=PURPLE,
                                           stroke_width=2.5), num_dashes=42
                                ).move_to(inner_c.get_center())
        a8c = DoubleArrow(inner_c.get_corner(UL)+UP*0.2, inner_c.get_corner(UR)+UP*0.2,
                          color=PURPLE, stroke_width=2, tip_length=0.15, buff=0)
        l8c = poppins("8 m", 20, PURPLE).next_to(a8c, UP, buff=0.08)
        a5c = DoubleArrow(inner_c.get_corner(UR)+RIGHT*0.2, inner_c.get_corner(DR)+RIGHT*0.2,
                          color=PURPLE, stroke_width=2, tip_length=0.15, buff=0)
        l5c = poppins("5 m", 20, PURPLE).next_to(a5c, RIGHT, buff=0.08)
        a1c = DoubleArrow(outer_c.get_left()+UP*1.0, inner_c.get_left()+UP*1.0,
                          color=PURPLE, stroke_width=1.5, tip_length=0.1, buff=0)
        l1c = poppins("1 m", 16, PURPLE).next_to(a1c, UP, buff=0.05)
        unk_c = unknown_mark(inner_c.get_top()+UP*0.4+RIGHT*1.5)
        # Left side prompt
        prompt = poppins("Find the\nborder area", 30, ORANGE_HL, BOLD).move_to(LEFT*3.5)

        with self.voiceover(
            text='Your turn. A room measures <bookmark mark="yt1"/>eight by five metres '
                 'with a one-metre <bookmark mark="yt2"/>border around the carpet. '
                 'What is the area <bookmark mark="yt3"/>of the border?'
        ):
            self.play(FadeIn(bdg), run_time=0.5)
            self.wait_until_bookmark("yt1")
            self.play(Create(inner_c), Create(a8c), FadeIn(l8c),
                      Create(a5c), FadeIn(l5c), run_time=1.3)
            self.wait_until_bookmark("yt2")
            self.play(Create(outer_c), Create(a1c), FadeIn(l1c), run_time=1.2)
            self.wait_until_bookmark("yt3")
            self.play(FadeIn(unk_c), FadeIn(prompt), run_time=0.8)
        self.wait(0.8)
        fade_all(self)

        # ════════════════════════════════════════════════════════
        # SCENE 34 — Hidden hint
        # ════════════════════════════════════════════════════════
        bdg = heading_badge("Hidden Condition")
        hint = MathTex(r"\text{Inner carpet} = 6 \times 4",
                       color=ORANGE_HL, font_size=48).move_to(UP*0.5)
        struct = poppins("Same pattern: Outer − Inner",
                         24, PURPLE).next_to(hint, DOWN, buff=0.7)

        with self.voiceover(
            text='If you spotted the inner carpet as <bookmark mark="hc1"/>six by four, '
                 'and the same Outer-minus-Inner <bookmark mark="hc2"/>pattern, you have '
                 'comprehended it.'
        ):
            self.play(FadeIn(bdg), run_time=0.5)
            self.wait_until_bookmark("hc1")
            self.play(FadeIn(hint), run_time=0.9)
            self.wait_until_bookmark("hc2")
            self.play(FadeIn(struct), run_time=0.7)
        self.wait(0.5)
        fade_all(self)

        # ════════════════════════════════════════════════════════
        # SCENE 35 — Full Circle Answer
        # ════════════════════════════════════════════════════════
        bdg = heading_badge("Full Circle")
        ans = MathTex(r"120\,\text{m}^2", color=ORANGE_HL, font_size=120).move_to(ORIGIN)
        cap = poppins("the tiles you need", 24, PURPLE).next_to(ans, DOWN, buff=0.6)

        with self.voiceover(
            text='Back to our garden. The answer is <bookmark mark="fc1"/>one hundred '
                 'twenty square metres of <bookmark mark="fc2"/>tiles.'
        ):
            self.play(FadeIn(bdg), run_time=0.5)
            self.wait_until_bookmark("fc1")
            self.play(FadeIn(ans), run_time=1.0)
            self.wait_until_bookmark("fc2")
            self.play(FadeIn(cap), run_time=0.6)
        self.wait(0.6)
        fade_all(self)

        # ════════════════════════════════════════════════════════
        # SCENE 36 — Checklist (7 nodes)
        # ════════════════════════════════════════════════════════
        bdg = heading_badge("Checklist")
        steps_lbl = ["Read","Extract","Identify","Map","Plan","Solve","Verify"]
        nodes = VGroup()
        for i, s in enumerate(steps_lbl):
            c = Circle(radius=0.35, color=PURPLE, stroke_width=2.5,
                       fill_color=ORANGE_HL if i%2==0 else PALE_PURPLE,
                       fill_opacity=0.3)
            num = poppins(str(i+1), 18, PURPLE, BOLD).move_to(c.get_center())
            lbl = poppins(s, 14, PURPLE).next_to(c, DOWN, buff=0.2)
            nodes.add(VGroup(c, num, lbl))
        nodes.arrange(RIGHT, buff=0.35).move_to(ORIGIN)

        with self.voiceover(
            text='Remember this checklist: <bookmark mark="ch1"/>read, extract, '
                 'identify, map, plan, solve, <bookmark mark="ch2"/>verify.'
        ):
            self.play(FadeIn(bdg), run_time=0.5)
            self.wait_until_bookmark("ch1")
            self.play(LaggedStart(*[FadeIn(n) for n in nodes], lag_ratio=0.15),
                      run_time=2.0)
            self.wait_until_bookmark("ch2")
            self.play(Indicate(nodes[-1], color=ORANGE_HL), run_time=0.6)
        self.wait(0.5)
        fade_all(self)

        # ════════════════════════════════════════════════════════
        # SCENE 37 — Closing concept map
        # ════════════════════════════════════════════════════════
        bdg = heading_badge("Concept Map")
        center = RoundedRectangle(corner_radius=0.15, width=3.0, height=0.9,
                                  stroke_color=PURPLE, stroke_width=2.5,
                                  fill_color=PURPLE, fill_opacity=0.2)
        center_l = poppins("Rectangle Area", 22, PURPLE, BOLD).move_to(center.get_center())
        c_grp = VGroup(center, center_l).move_to(ORIGIN)
        def branch(s, pos):
            c = RoundedRectangle(corner_radius=0.1, width=2.3, height=0.7,
                                 stroke_color=PURPLE, stroke_width=2,
                                 fill_color=PALE_PURPLE, fill_opacity=0.2)
            tx = poppins(s, 16, PURPLE).move_to(c.get_center())
            return VGroup(c, tx).move_to(pos)
        b1 = branch("L × B", UR*2.3)
        b2 = branch("m², cm²", DR*2.3)
        b3 = branch("s × s", DL*2.3)
        b4 = branch("Composite", UL*2.3)
        lines = VGroup(
            Line(center.get_corner(UR), b1.get_corner(DL), color=PURPLE, stroke_width=1.5),
            Line(center.get_corner(DR), b2.get_corner(UL), color=PURPLE, stroke_width=1.5),
            Line(center.get_corner(DL), b3.get_corner(UR), color=PURPLE, stroke_width=1.5),
            Line(center.get_corner(UL), b4.get_corner(DR), color=PURPLE, stroke_width=1.5),
        )

        with self.voiceover(
            text='You now understand rectangular <bookmark mark="cm1"/>area completely. '
                 'Practice this checklist, and the concept becomes a tool you '
                 '<bookmark mark="cm2"/>wield with confidence.'
        ):
            self.play(FadeIn(bdg), FadeIn(c_grp), run_time=0.8)
            self.wait_until_bookmark("cm1")
            self.play(Create(lines),
                      FadeIn(b1), FadeIn(b2), FadeIn(b3), FadeIn(b4), run_time=1.4)
            self.wait_until_bookmark("cm2")
            self.play(Indicate(c_grp, color=ORANGE_HL), run_time=0.7)
        self.wait(0.6)
        fade_all(self)

        # ════════════════════════════════════════════════════════
        # SCENE 38 — Coming Next
        # ════════════════════════════════════════════════════════
        bdg = heading_badge("Coming Next")
        rect_n = Rectangle(width=2.0, height=1.4, color=PURPLE, stroke_width=2.5,
                           fill_color=PURPLE, fill_opacity=0.2).move_to(LEFT*3.5)
        arr_n = Arrow(LEFT*2.0, RIGHT*0.5, color=PURPLE, stroke_width=3)
        tri_n = Polygon([0,0.7,0],[0.7,-0.5,0],[-0.7,-0.5,0],
                        color=ORANGE_HL, stroke_width=2.5,
                        fill_color=ORANGE_HL, fill_opacity=0.3).move_to(RIGHT*1.5)
        para_n = Polygon([-0.5,0.4,0],[0.7,0.4,0],[0.4,-0.4,0],[-0.8,-0.4,0],
                         color=ORANGE_HL, stroke_width=2.5,
                         fill_color=ORANGE_HL, fill_opacity=0.3).move_to(RIGHT*3.5)
        q_n = poppins("?", 60, ORANGE_HL, BOLD).move_to(RIGHT*5)

        with self.voiceover(
            text='But what happens when the shape is <bookmark mark="cn_a"/>not '
                 'a rectangle? '
                 'That is what we explore <bookmark mark="cn_b"/>next.'
        ):
            self.play(FadeIn(bdg), Create(rect_n), run_time=0.8)
            self.wait_until_bookmark("cn_a")
            self.play(Create(arr_n), Create(tri_n), Create(para_n), run_time=1.0)
            self.wait_until_bookmark("cn_b")
            self.play(FadeIn(q_n), run_time=0.6)
        self.wait(0.8)
        fade_all(self, rt=1.0)