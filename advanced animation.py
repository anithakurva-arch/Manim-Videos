import os
import urllib.request
import manimpango
from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.openai import OpenAIService

# Coschool Color Palette
LAVENDER_BG = "#E7E5F3"
PURPLE      = "#7464CE"
ORANGE_HL   = "#FF9302"
PALE_PURPLE = "#9495D7"
WHITE = "#FFFFFF"

# ============================================================
# POPPINS AUTO-DOWNLOAD & REGISTRATION
# ============================================================
def _setup_poppins():
    base_dir  = os.path.dirname(os.path.abspath(__file__))
    fonts_dir = os.path.join(base_dir, ".fonts")
    os.makedirs(fonts_dir, exist_ok=True)
    base_url = "https://raw.githubusercontent.com/google/fonts/main/ofl/poppins/"
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
                urllib.request.urlretrieve(url, path)
            except Exception:
                continue
        try:
            manimpango.register_font(path)
        except Exception:
            pass

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
        return 0.0

_vt.VoiceoverTracker.time_until_bookmark = _safe_time_until_bookmark

import atexit
def _report():
    if _FAILED_BOOKMARKS:
        print("\nFAILED BOOKMARKS SUMMARY:")
        for mark, text in _FAILED_BOOKMARKS:
            print(f"  FAILED: {mark}  ->  {text}")
atexit.register(_report)

# ============================================================
# HELPER FUNCTIONS
# ============================================================
def math(tex_str, color=PURPLE, font_size=36):
    return MathTex(tex_str, tex_template=TexFontTemplates.gnu_freesans_tx, color=color, font_size=font_size)

def create_heading_badge(text_str):
    t = Text(text_str, font="Poppins", font_size=28, color=WHITE, weight=BOLD)
    badge = RoundedRectangle(corner_radius=0.2, width=t.width + 0.6, height=t.height + 0.3,
                             fill_color=PURPLE, fill_opacity=1, stroke_width=0).move_to(t)
    return VGroup(badge, t).to_corner(UL, buff=0.3)

def create_dimension(start, end, label_str, direction=DOWN, buff=0.3):
    arrow = DoubleArrow(start=start, end=end, color=PURPLE, stroke_width=2, tip_length=0.2, buff=0)
    label = Text(label_str, font="Poppins", font_size=22, color=PURPLE)
    label.next_to(arrow.get_center(), direction, buff=0.15)
    return VGroup(arrow, label)

def create_unknown(position):
    return Text("?", font="Poppins", font_size=36, color=ORANGE_HL, weight=BOLD).move_to(position)

# ============================================================
# MAIN SCENE
# ============================================================

TTS_INSTRUCTIONS = """
Voice: shimmer. Tone: warm, patient, encouraging teacher.
Pace: Moderate-to-slow. Honor commas, dashes, and ellipses.
"""

class PerimeterExplainer(VoiceoverScene):
    def construct(self):
        self.set_speech_service(
            OpenAIService(voice="shimmer", model="gpt-4o-mini-tts", transcription_model="medium", instructions=TTS_INSTRUCTIONS),
            create_subcaption=False,
        )
        self.camera.background_color = LAVENDER_BG

        # --- SEGMENT 1: HOOK ---
        with self.voiceover(text='<bookmark mark="bk_hello"/>Hello students! <bookmark mark="bk_imagine"/>Imagine you are arranging chairs around a rectangular classroom table. You know the total number of chairs that fit around it, and you know how many fit along one side. <bookmark mark="bk_could"/>Could you figure out how many fit along the other side — without counting again?') as tracker:
            self.wait_until_bookmark("bk_hello")
            greet = Text("Hello students!", font="Poppins", font_size=40, color=PURPLE)
            self.play(FadeIn(greet))
            self.wait(1)
            self.play(FadeOut(greet))

            self.wait_until_bookmark("bk_imagine")
            table = Rectangle(width=5, height=3, color=PURPLE, stroke_width=2.5)
            chairs = VGroup(*[Circle(radius=0.15, color=PALE_PURPLE, fill_opacity=1) for _ in range(12)])
            chairs.arrange_in_grid(rows=2, cols=6, buff=0.4).move_to(table.get_center())
            self.play(Create(table), FadeIn(chairs))
            
            self.wait_until_bookmark("bk_could")
            q_mark = create_unknown(table.get_center())
            self.play(FadeIn(q_mark))
            self.wait(1)
            self.play(FadeOut(table), FadeOut(chairs), FadeOut(q_mark))

        # --- SEGMENT 2: CONCEPT ---
        with self.voiceover(text='<bookmark mark="bk_perimeter"/>The perimeter is the total length around a shape. <bookmark mark="bk_rect_form"/>For a rectangle, the perimeter equals, two times, the sum of, length, and width. <bookmark mark="bk_sq_form"/>For a square, the perimeter equals, four times, the length of one side. <bookmark mark="bk_rearrange"/>So if we know the perimeter and one dimension, we can rearrange the formula — and find the missing one. <bookmark mark="bk_tool"/>This means perimeter is not just for measuring — it is also a tool to work backwards.') as tracker:
            self.wait_until_bookmark("bk_perimeter")
            badge = create_heading_badge("Definition")
            self.play(FadeIn(badge))
            rect = Rectangle(width=4, height=2, color=PURPLE, stroke_width=2.5)
            self.play(Create(rect))
            
            self.wait_until_bookmark("bk_rect_form")
            f1 = math("P = 2(l + w)").to_edge(UP, buff=1.5)
            self.play(FadeIn(f1))
            
            self.wait_until_bookmark("bk_sq_form")
            self.play(FadeOut(rect), FadeOut(f1))
            sq = Square(side_length=2, color=PURPLE, stroke_width=2.5)
            f2 = math("P = 4s").to_edge(UP, buff=1.5)
            self.play(Create(sq), FadeIn(f2))

            self.wait_until_bookmark("bk_rearrange")
            self.play(FadeOut(sq), FadeOut(f2))
            rearrange = Text("Rearrange to find unknown", font="Poppins", font_size=32, color=PURPLE)
            self.play(FadeIn(rearrange))
            
            self.wait_until_bookmark("bk_tool")
            self.play(FadeOut(rearrange))
            tool = Text("Perimeter is a tool", font="Poppins", font_size=36, color=PURPLE)
            self.play(FadeIn(tool))
            self.wait(1)
            self.play(FadeOut(tool), FadeOut(badge))

        # --- SEGMENT 3: EXPLANATION ---
        with self.voiceover(text='<bookmark mark="bk_why"/>Now, why does this work? <bookmark mark="bk_rect_exp"/>A rectangle, has two equal lengths and two equal widths. So once we know the perimeter and one of them, simple algebra gives us the other. <bookmark mark="bk_sq_exp"/>A square, has four equal sides, so its side is simply, the perimeter, divided by four.') as tracker:
            self.wait_until_bookmark("bk_why")
            why = Text("Why does this work?", font="Poppins", font_size=36, color=PURPLE)
            self.play(FadeIn(why))
            self.wait(1)
            self.play(FadeOut(why))

            self.wait_until_bookmark("bk_rect_exp")
            r_exp = Rectangle(width=3, height=1.5, color=PURPLE, stroke_width=2.5)
            l_lbl = math("l").next_to(r_exp, UP, buff=0.1)
            w_lbl = math("w").next_to(r_exp, RIGHT, buff=0.1)
            self.play(Create(r_exp), FadeIn(l_lbl), FadeIn(w_lbl))
            
            self.wait_until_bookmark("bk_sq_exp")
            self.play(FadeOut(r_exp), FadeOut(l_lbl), FadeOut(w_lbl))
            s_exp = Square(side_length=2, color=PURPLE, stroke_width=2.5)
            s_lbl = math("s").move_to(s_exp.get_center())
            self.play(Create(s_exp), FadeIn(s_lbl))
            self.wait(1)
            self.play(FadeOut(s_exp), FadeOut(s_lbl))

        # --- SEGMENT 4: QUESTION ---
        with self.voiceover(text='<bookmark mark="bk_q_part1"/>Part 1: The perimeter of a rectangular notebook is, thirty-four centimeters. Its length is, <bookmark mark="bk_q_len"/>eleven centimeters. Find its width — and check whether two such notebooks would fit along a, <bookmark mark="bk_q_shelf"/>twenty-four centimeter shelf. <bookmark mark="bk_q_part2"/>Part 2: A square tile has a perimeter of, forty-eight centimeters. Find the length of, <bookmark mark="bk_q_side"/>one side.') as tracker:
            self.wait_until_bookmark("bk_q_part1")
            p1_badge = create_heading_badge("Part 1")
            self.play(FadeIn(p1_badge))
            nb = Rectangle(width=4, height=2, color=PURPLE, stroke_width=2.5).to_edge(RIGHT, buff=1)
            q1_txt = Text("P = 34 cm, l = 11 cm", font="Poppins", font_size=26, color=PURPLE).to_edge(UP, buff=2)
            self.play(Create(nb), FadeIn(q1_txt))

            self.wait_until_bookmark("bk_q_len")
            l_arr = create_dimension(nb.get_corner(DL), nb.get_corner(DR), "11 cm", DOWN)
            self.play(Create(l_arr))

            self.wait_until_bookmark("bk_q_shelf")
            q1_sub = Text("Shelf: 24 cm", font="Poppins", font_size=26, color=PURPLE).next_to(q1_txt, DOWN)
            self.play(FadeIn(q1_sub))

            self.wait_until_bookmark("bk_q_part2")
            self.play(FadeOut(p1_badge), FadeOut(q1_txt), FadeOut(q1_sub), FadeOut(nb), FadeOut(l_arr))
            p2_badge = create_heading_badge("Part 2")
            self.play(FadeIn(p2_badge))
            tile = Square(side_length=2, color=PURPLE, stroke_width=2.5).to_edge(RIGHT, buff=1)
            q2_txt = Text("P = 48 cm", font="Poppins", font_size=26, color=PURPLE).to_edge(UP, buff=2)
            self.play(Create(tile), FadeIn(q2_txt))

            self.wait_until_bookmark("bk_q_side")
            unk = create_unknown(tile.get_center())
            self.play(FadeIn(unk))
            self.wait(1)
            self.play(FadeOut(p2_badge), FadeOut(q2_txt), FadeOut(tile), FadeOut(unk))

        # --- SEGMENT 5: SOLUTION (NOTEBOOK) ---
        with self.voiceover(text='<bookmark mark="bk_s_notebook"/>For the notebook: Two times, the sum of, length, and width, equals the perimeter. <bookmark mark="bk_s_eq1"/>Two times, eleven, plus width, equals, thirty-four. <bookmark mark="bk_s_eq2"/>Eleven, plus width, equals, seventeen. <bookmark mark="bk_s_ans1"/>So width equals — six centimeters. <bookmark mark="bk_s_check"/>Two notebooks placed side by side would need, twelve centimeters, which fits well on the shelf.') as tracker:
            self.wait_until_bookmark("bk_s_notebook")
            s1_badge = create_heading_badge("Solution: Notebook")
            self.play(FadeIn(s1_badge))
            nb_sol = Rectangle(width=3, height=1.5, color=PURPLE, stroke_width=2.5).to_edge(RIGHT, buff=1)
            self.play(Create(nb_sol))
            
            step1 = math("2(l + w) = P").to_edge(LEFT, buff=1).shift(UP*2)
            self.play(FadeIn(step1))

            self.wait_until_bookmark("bk_s_eq1")
            step2 = math("2(11 + w) = 34").next_to(step1, DOWN, buff=0.4)
            self.play(FadeIn(step2))
            step1.set_opacity(0.4)

            self.wait_until_bookmark("bk_s_eq2")
            step3 = math("11 + w = 17").next_to(step2, DOWN, buff=0.4)
            self.play(FadeIn(step3))
            step2.set_opacity(0.4)

            self.wait_until_bookmark("bk_s_ans1")
            ans1 = math("w = 6\\text{ cm}", color=ORANGE_HL).next_to(step3, DOWN, buff=0.4)
            self.play(FadeIn(ans1))
            step3.set_opacity(0.4)

            self.wait_until_bookmark("bk_s_check")
            check = Text("12 cm < 24 cm (YES)", font="Poppins", font_size=28, color=PURPLE).next_to(ans1, DOWN, buff=0.4)
            self.play(FadeIn(check))
            self.wait(1)
            self.play(FadeOut(s1_badge), FadeOut(nb_sol), FadeOut(step1), FadeOut(step2), FadeOut(step3), FadeOut(ans1), FadeOut(check))

        # --- SEGMENT 6: SOLUTION (TILE) ---
        with self.voiceover(text='<bookmark mark="bk_s_tile"/>For the tile: The perimeter, equals, four times the side. <bookmark mark="bk_s_eq3"/>Four times the side, equals, forty-eight. <bookmark mark="bk_s_ans2"/>So the side equals — twelve centimeters. <bookmark mark="bk_s_builder"/>This is the same idea, builders use when calculating tile sizes for a floor.') as tracker:
            self.wait_until_bookmark("bk_s_tile")
            s2_badge = create_heading_badge("Solution: Tile")
            self.play(FadeIn(s2_badge))
            tile_sol = Square(side_length=2, color=PURPLE, stroke_width=2.5).to_edge(RIGHT, buff=1)
            self.play(Create(tile_sol))

            step1 = math("P = 4s").to_edge(LEFT, buff=1).shift(UP*2)
            self.play(FadeIn(step1))

            self.wait_until_bookmark("bk_s_eq3")
            step2 = math("4s = 48").next_to(step1, DOWN, buff=0.4)
            self.play(FadeIn(step2))
            step1.set_opacity(0.4)

            self.wait_until_bookmark("bk_s_ans2")
            ans2 = math("s = 12\\text{ cm}", color=ORANGE_HL).next_to(step2, DOWN, buff=0.4)
            self.play(FadeIn(ans2))
            step2.set_opacity(0.4)

            self.wait_until_bookmark("bk_s_builder")
            self.play(FadeOut(s2_badge), FadeOut(tile_sol), FadeOut(step1), FadeOut(step2), FadeOut(ans2))
            builder = Text("Builders use this!", font="Poppins", font_size=32, color=PURPLE)
            self.play(FadeIn(builder))
            self.wait(1)
            self.play(FadeOut(builder))

        # --- SEGMENT 7: SUMMARY ---
        with self.voiceover(text='<bookmark mark="bk_sum"/>Summary. Perimeter formulas, can be rearranged, to find missing dimensions. Rectangle: <bookmark mark="bk_sum_rect"/>perimeter is, two times, the sum of, length, and width. Square: <bookmark mark="bk_sum_sq"/>side is, the perimeter, divided by four.') as tracker:
            self.wait_until_bookmark("bk_sum")
            sum_badge = create_heading_badge("Summary")
            self.play(FadeIn(sum_badge))
            summ = Text("Rearrange to find missing values", font="Poppins", font_size=30, color=PURPLE).shift(UP*1)
            self.play(FadeIn(summ))

            self.wait_until_bookmark("bk_sum_rect")
            f_rect = math("P = 2(l + w)").next_to(summ, DOWN, buff=0.5)
            self.play(FadeIn(f_rect))

            self.wait_until_bookmark("bk_sum_sq")
            f_sq = math("s = \\frac{P}{4}").next_to(f_rect, DOWN, buff=0.4)
            self.play(FadeIn(f_sq))
            self.wait(1)
            self.play(FadeOut(sum_badge), FadeOut(summ), FadeOut(f_rect), FadeOut(f_sq))

        self.wait(0.6)