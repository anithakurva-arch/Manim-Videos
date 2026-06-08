import os
import urllib.request
import manimpango
from dotenv import load_dotenv
from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.openai import OpenAIService

load_dotenv()

LAVENDER_BG = "#E7E5F3"
PURPLE      = "#7464CE"
ORANGE_HL   = "#FF9302"
PALE_PURPLE = "#9495D7"

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
                urllib.request.urlretrieve(url, path)
            except Exception as e:
                print(f"Could not download {fname}: {e}")
                continue
        try:
            manimpango.register_font(path)
        except Exception:
            pass

_setup_poppins()

import manim_voiceover.tracker as _vt
_orig = _vt.VoiceoverTracker.time_until_bookmark
_FAILED = []

def _safe_tub(self, mark, buff=0.0, limit=None):
    try:
        return _orig(self, mark, buff, limit)
    except Exception:
        _FAILED.append(mark)
        print(f"WARNING: bookmark '{mark}' not found")
        return 0.0

_vt.VoiceoverTracker.time_until_bookmark = _safe_tub

import atexit
def _report():
    if _FAILED:
        print(f"\nFAILED BOOKMARKS: {_FAILED}")
atexit.register(_report)

TTS_INSTRUCTIONS = """
You are a warm, patient math teacher. Tone: friendly, calm, never rushed.
Pace: moderate-to-slow. Honor commas, dashes, ellipses as pacing marks.
Slow down on variables and formulas. Emphasize final answers.
Read the script EXACTLY. No filler. No improvisation.
"""


def create_heading_badge(text_str):
    t = Text(text_str, font="Poppins", font_size=28,
             color=WHITE)
    bg = RoundedRectangle(
        corner_radius=0.2, width=t.width + 0.6,
        height=t.height + 0.3,
        fill_color=PURPLE, fill_opacity=1, stroke_width=0)
    bg.move_to(t)
    return VGroup(bg, t).to_corner(UL, buff=0.3)


def math_obj(tex_str, color=PURPLE, font_size=36):
    return MathTex(tex_str,
                   tex_template=TexFontTemplates.gnu_freesans_tx,
                   color=color, font_size=font_size)


def make_legend(entries, position=DR, buff=0.4):
    rows = []
    for var_tex, def_str in entries:
        v = MathTex(var_tex,
                    tex_template=TexFontTemplates.gnu_freesans_tx,
                    font_size=20, color=ORANGE_HL)
        d = Text(def_str, font="Poppins",
                 font_size=20, color=PURPLE)
        rows.append(VGroup(v, d).arrange(RIGHT, buff=0.1))
    content = VGroup(*rows).arrange(
        DOWN, aligned_edge=LEFT, buff=0.25)
    bg = RoundedRectangle(
        corner_radius=0.15,
        width=content.width + 0.4,
        height=content.height + 0.3,
        fill_color=WHITE, fill_opacity=0.85,
        stroke_color=PALE_PURPLE, stroke_width=1.0)
    bg.move_to(content)
    g = VGroup(bg, content)
    if position is not None:
        g.to_corner(position, buff=buff)
    return g


def make_concept_card(text_str, position=ORIGIN,
                      font_size=24, max_chars=52):
    if len(text_str) > max_chars:
        words = text_str.split()
        lines, cur = [], ""
        for w in words:
            if len(cur) + len(w) + 1 <= max_chars:
                cur += (" " if cur else "") + w
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        text_str = "\n".join(lines)
    txt = Text(text_str, font="Poppins",
               font_size=font_size, color=PURPLE)
    bg = RoundedRectangle(
        corner_radius=0.2,
        width=min(txt.width + 0.8, 10.5),
        height=txt.height + 0.4,
        fill_color=WHITE, fill_opacity=0.85,
        stroke_color=PALE_PURPLE, stroke_width=1.5)
    bg.move_to(position)
    txt.move_to(bg.get_center())
    return VGroup(bg, txt)


def make_bullet_point(text_str, position=ORIGIN,
                      font_size=24, max_chars=50):
    if len(text_str) > max_chars:
        words = text_str.split()
        lines, cur = [], ""
        for w in words:
            if len(cur) + len(w) + 1 <= max_chars:
                cur += (" " if cur else "") + w
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        text_str = "\n".join(lines)
    dot = Text("\u2022", font="Poppins",
               font_size=font_size + 4, color=ORANGE_HL)
    txt = Text(text_str, font="Poppins",
               font_size=font_size, color=PURPLE)
    row = VGroup(dot, txt).arrange(
        RIGHT, buff=0.25, aligned_edge=UP)
    row.move_to(position)
    return row


def clear_and_transition(scene, active_mobs, new_bg,
                         ft=0.8, buf=0.2, settle=0.1):
    if active_mobs:
        scene.play(
            *[FadeOut(m) for m in active_mobs],
            run_time=ft)
    scene.wait(buf)
    scene.camera.background_color = new_bg
    scene.wait(settle)


SAFE_L, SAFE_R = -6.11, 6.11
SAFE_T, SAFE_B = 3.25, -3.25


def check_safe_margins(mob, name="obj"):
    ok = True
    if mob.get_left()[0]   < SAFE_L: ok = False
    if mob.get_right()[0]  > SAFE_R: ok = False
    if mob.get_top()[1]    > SAFE_T: ok = False
    if mob.get_bottom()[1] < SAFE_B: ok = False
    if not ok:
        print(f"MARGIN WARNING: {name}")
        clamp_to_safe_area(mob)
    return ok


def clamp_to_safe_area(mob):
    sx, sy = 0, 0
    if   mob.get_left()[0]   < SAFE_L:
        sx = SAFE_L - mob.get_left()[0]
    elif mob.get_right()[0]  > SAFE_R:
        sx = SAFE_R - mob.get_right()[0]
    if   mob.get_bottom()[1] < SAFE_B:
        sy = SAFE_B - mob.get_bottom()[1]
    elif mob.get_top()[1]    > SAFE_T:
        sy = SAFE_T - mob.get_top()[1]
    if sx or sy:
        mob.shift(RIGHT * sx + UP * sy)
    return mob


def build_expr_row(terms, font_size=32):
    mobs = {}
    parts = []
    for key, tex in terms:
        mo = math_obj(tex, font_size=font_size)
        mobs[key] = mo
        parts.append(mo)
    row = VGroup(*parts).arrange(RIGHT, buff=0.18)
    mobs["row"] = row
    return mobs


def make_seq_blocks(values, block_w=1.1, block_h=0.9):
    """
    Build a row of coloured blocks labelled with sequence values.
    Returns {"blocks": VGroup, "labels": VGroup, "group": VGroup}
    """
    blocks = VGroup()
    labels = VGroup()
    for i, val in enumerate(values):
        blk = Rectangle(
            width=block_w, height=block_h,
            fill_color=PALE_PURPLE, fill_opacity=0.35,
            stroke_color=PURPLE, stroke_width=2.5)
        lbl = Text(str(val), font="Poppins",
                   font_size=26, color=PURPLE)
        blocks.add(blk)
        labels.add(lbl)
    blocks.arrange(RIGHT, buff=0.2)
    for i, blk in enumerate(blocks):
        labels[i].move_to(blk.get_center())
    return {
        "blocks": blocks,
        "labels": labels,
        "group": VGroup(blocks, labels),
    }


class StepManager:
    LIMITS = {(32, 0.4): 3, (28, 0.3): 4,
              (24, 0.25): 5, (20, 0.2): 6}

    def __init__(self, scene, start_anchor=None,
                 font_size=24, buff=0.25):
        self.scene  = scene
        self.steps  = []
        self.fs     = font_size
        self.buff   = buff
        self.max    = self.LIMITS.get((font_size, buff), 5)
        self.anchor = (
            start_anchor if start_anchor is not None
            else (UP * 2.0 + LEFT * 3.5)
        )

    def add_step(self, mob, run_time=0.7):
        if len(self.steps) >= self.max:
            print(f"WARNING: StepManager at limit ({self.max}).")
        if self.steps:
            mob.next_to(self.steps[-1], DOWN,
                        aligned_edge=LEFT, buff=self.buff)
            self.scene.play(
                *[s.animate.set_opacity(0.4)
                  for s in self.steps],
                FadeIn(mob), run_time=run_time)
        else:
            mob.move_to(self.anchor)
            self.scene.play(FadeIn(mob), run_time=run_time)
        self.steps.append(mob)
        if mob.get_bottom()[1] < SAFE_B:
            print("WARNING: step below safe area")
        return mob

    def fadeout_all(self, rt=0.8):
        if self.steps:
            self.scene.play(
                *[FadeOut(s) for s in self.steps],
                run_time=rt)
            self.steps.clear()

    def get_all(self):
        return VGroup(*self.steps)


# ══════════════════════════════════════════════════════════
class GeneralTermScene(VoiceoverScene):

    def construct(self):
        self._setup_tts()
        self.show_title()
        self.show_concept()
        self.show_question()
        self.show_solution()
        self.show_summary()

    def _setup_tts(self):
        self.set_speech_service(
            OpenAIService(
                voice="shimmer",
                model="gpt-4o-mini-tts",
                transcription_model="medium",
                instructions=TTS_INSTRUCTIONS,
            ),
            create_subcaption=False,
        )

    # ── TITLE ─────────────────────────────────────────────
    def show_title(self):
        active_mobs = []
        with self.voiceover(
            text='<bookmark mark="bk_hello"/>Hello students!'
        ) as tracker:
            self.wait_until_bookmark("bk_hello")
            self.camera.background_color = PURPLE
            topic = Text(
                "General Terms for Sequences",
                font="Poppins", font_size=40,
                color=WHITE)
            topic.move_to(ORIGIN)
            check_safe_margins(topic, "title")
            self.play(FadeIn(topic), run_time=0.8)
            active_mobs.append(topic)
        self.wait(0.4)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── CONCEPT ───────────────────────────────────────────
    def show_concept(self):
        active_mobs = []
        badge = create_heading_badge("Concept")
        check_safe_margins(badge, "badge_concept")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)
        self._concept_seq1(active_mobs)
        self._concept_seq2(active_mobs)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── CONCEPT PART A — sequence 5,10,15,20 ──────────────
    def _concept_seq1(self, active_mobs):
        with self.voiceover(
            text=(
                'Look at this sequence: five, ten, fifteen, twenty. '
                'Each term is five more than the previous one. '
                'If someone asked for the hundredth term, '
                '<bookmark mark="bk_smarter"/>you would not want to '
                'keep adding five all the way. '
                'There is a much smarter way. '
                '<bookmark mark="bk_position"/>We use the position number '
                'of a term, to describe it with a letter-number. '
                'Let n represent the position number — '
                '<bookmark mark="bk_n_def"/>so n equals one for the '
                'first term, n equals two for the second, and so on. '
                'In this sequence, the first term is five times one, '
                'the second is five times two, '
                '<bookmark mark="bk_pattern"/>the third is five times three. '
                'The pattern is clear — every term is five times '
                'its position number. '
                '<bookmark mark="bk_general"/>So the general term is five n. '
                'For the hundredth term, substitute n equals one hundred: '
                '<bookmark mark="bk_hundred"/>five times one hundred '
                'equals five hundred.'
            )
        ) as tracker:
            # ── sequence blocks 5,10,15,20 ──
            seq1 = make_seq_blocks([5, 10, 15, 20])
            seq1["group"].move_to(ORIGIN)
            check_safe_margins(seq1["group"], "seq1_blocks")
            self.play(Create(seq1["blocks"]), run_time=1.0)
            self.play(FadeIn(seq1["labels"]), run_time=0.5)
            active_mobs.append(seq1["group"])

            # position labels n=1..4 below blocks
            self.wait_until_bookmark("bk_smarter")
            pos_lbls = VGroup()
            for i, blk in enumerate(seq1["blocks"]):
                pl = Text(f"n={i+1}", font="Poppins",
                          font_size=18, color=PALE_PURPLE)
                pl.next_to(blk, DOWN, buff=0.22)
                pos_lbls.add(pl)
            check_safe_margins(pos_lbls, "pos_lbls")
            self.play(FadeIn(pos_lbls), run_time=0.6)
            active_mobs.append(pos_lbls)

            # n definition card
            self.wait_until_bookmark("bk_position")
            n_card = make_concept_card(
                "n = position number of each term",
                position=UP * 2.4, font_size=22)
            check_safe_margins(n_card, "n_card")
            self.play(FadeIn(n_card), run_time=0.6)
            active_mobs.append(n_card)

            # highlight blocks and show multiplication labels
            self.wait_until_bookmark("bk_n_def")
            mult_lbls = VGroup()
            for i, (blk, val) in enumerate(
                    zip(seq1["blocks"], [5, 10, 15, 20])):
                ml = math_obj(
                    rf"5 \times {i+1}",
                    font_size=20, color=ORANGE_HL)
                ml.next_to(blk, UP, buff=0.28)
                mult_lbls.add(ml)
            check_safe_margins(mult_lbls, "mult_lbls")

            self.wait_until_bookmark("bk_pattern")
            for i in range(3):
                self.play(
                    seq1["blocks"][i].animate.set_fill(
                        ORANGE_HL, opacity=0.55),
                    FadeIn(mult_lbls[i]),
                    run_time=0.5)
                self.wait(0.15)
            active_mobs.append(mult_lbls)

            # general term 5n
            self.wait_until_bookmark("bk_general")
            self.play(
                *[b.animate.set_fill(PALE_PURPLE, opacity=0.35)
                  for b in seq1["blocks"]],
                run_time=0.4)
            gt_5n = build_expr_row([
                ("lbl", r"\text{General term:}"),
                ("fn",  r"5n"),
            ], font_size=30)
            gt_5n["fn"].set_color(ORANGE_HL)
            gt_5n["row"].next_to(seq1["group"], DOWN, buff=0.55)
            check_safe_margins(gt_5n["row"], "gt_5n")
            self.play(FadeIn(gt_5n["row"]), run_time=0.7)
            active_mobs.append(gt_5n["row"])

            # substitute n=100
            self.wait_until_bookmark("bk_hundred")
            sub_row = build_expr_row([
                ("s5",   r"5"),
                ("sn",   r"n"),
                ("seq",  r"="),
                ("s5b",  r"5"),
                ("s100", r"\times 100"),
                ("seq2", r"="),
                ("s500", r"500"),
            ], font_size=28)
            sub_row["sn"].set_color(ORANGE_HL)
            sub_row["s100"].set_color(ORANGE_HL)
            sub_row["s500"].set_color(ORANGE_HL)
            sub_row["row"].next_to(
                gt_5n["row"], DOWN, buff=0.35)
            check_safe_margins(sub_row["row"], "sub100")
            self.play(FadeIn(sub_row["row"]), run_time=0.7)
            active_mobs.append(sub_row["row"])

    # ── CONCEPT PART B — sequence 3,7,11,15 ───────────────
    def _concept_seq2(self, active_mobs):
        with self.voiceover(
            text=(
                '<bookmark mark="bk_seq2"/>Now consider the sequence '
                'three, seven, eleven, fifteen. '
                'The terms increase by '
                '<bookmark mark="bk_diff4"/>four each time. '
                'We multiply the common difference — four — by n, '
                '<bookmark mark="bk_adjust"/>then adjust. '
                'Check: four times one gives four, but we need three. '
                '<bookmark mark="bk_sub1"/>So we subtract one. '
                'The general term is '
                '<bookmark mark="bk_gen2"/>four n minus one. '
                'Check: four times two minus one equals seven. '
                '<bookmark mark="bk_correct"/>Correct.'
            )
        ) as tracker:
            # clear seq1 content (keep badge)
            to_clear = [m for m in active_mobs
                        if m is not active_mobs[0]]
            if to_clear:
                self.play(
                    *[FadeOut(m) for m in to_clear],
                    run_time=0.6)
                for m in to_clear:
                    active_mobs.remove(m)

            # ── sequence blocks 3,7,11,15 ──
            self.wait_until_bookmark("bk_seq2")
            seq2 = make_seq_blocks([3, 7, 11, 15])
            seq2["group"].move_to(UP * 0.3)
            check_safe_margins(seq2["group"], "seq2_blocks")
            self.play(Create(seq2["blocks"]), run_time=0.9)
            self.play(FadeIn(seq2["labels"]), run_time=0.5)
            active_mobs.append(seq2["group"])

            # +4 difference arrows
            self.wait_until_bookmark("bk_diff4")
            diff_arrows = VGroup()
            for i in range(3):
                b1 = seq2["blocks"][i]
                b2 = seq2["blocks"][i + 1]
                mid_x = (b1.get_right()[0] + b2.get_left()[0]) / 2
                mid_y = seq2["blocks"].get_top()[1] + 0.45
                arr = Arrow(
                    b1.get_top() + UP * 0.05,
                    b2.get_top() + UP * 0.05,
                    color=ORANGE_HL, stroke_width=2.0,
                    tip_length=0.14, buff=0.08,
                    path_arc=-PI / 3)
                d_lbl = Text("+4", font="Poppins",
                             font_size=18, color=ORANGE_HL)
                d_lbl.move_to(
                    np.array([mid_x, mid_y + 0.1, 0]))
                diff_arrows.add(arr, d_lbl)
            check_safe_margins(diff_arrows, "diff_arrows")
            self.play(Create(diff_arrows), run_time=0.8)
            active_mobs.append(diff_arrows)

            # try 4n adjust card
            self.wait_until_bookmark("bk_adjust")
            adj_card = make_concept_card(
                "Try: 4n, then adjust.",
                position=DOWN * 1.3, font_size=24)
            check_safe_margins(adj_card, "adj_card")
            self.play(FadeIn(adj_card), run_time=0.6)
            active_mobs.append(adj_card)

            # 4×1=4 but need 3 → subtract 1
            self.wait_until_bookmark("bk_sub1")
            check_row = build_expr_row([
                ("c4",  r"4 \times 1"),
                ("ceq", r"="),
                ("c4v", r"4"),
                ("cbut",r",\text{ need } 3"),
                ("csub",r"\Rightarrow -1"),
            ], font_size=26)
            check_row["c4v"].set_color(ORANGE_HL)
            check_row["csub"].set_color(ORANGE_HL)
            check_row["row"].next_to(
                adj_card, DOWN, buff=0.35)
            check_safe_margins(check_row["row"], "check_row")
            self.play(FadeIn(check_row["row"]), run_time=0.7)
            active_mobs.append(check_row["row"])

            # general term 4n−1
            self.wait_until_bookmark("bk_gen2")
            self.play(
                FadeOut(adj_card),
                FadeOut(check_row["row"]),
                run_time=0.4)
            active_mobs.remove(adj_card)
            active_mobs.remove(check_row["row"])

            gt_4n = build_expr_row([
                ("lbl2", r"\text{General term:}"),
                ("fn2",  r"4n - 1"),
            ], font_size=30)
            gt_4n["fn2"].set_color(ORANGE_HL)
            gt_4n["fn2"].set_stroke(width=2.0)
            gt_4n["row"].move_to(DOWN * 1.4)
            check_safe_margins(gt_4n["row"], "gt_4n")
            self.play(FadeIn(gt_4n["row"]), run_time=0.7)
            active_mobs.append(gt_4n["row"])

            # verify: 4×2−1=7 ✓
            self.wait_until_bookmark("bk_correct")
            verify_row = build_expr_row([
                ("v4",  r"4 \times 2 - 1"),
                ("veq", r"="),
                ("v7",  r"7"),
                ("vck", r"\checkmark"),
            ], font_size=26)
            verify_row["v7"].set_color(ORANGE_HL)
            verify_row["vck"].set_color(ORANGE_HL)
            verify_row["v4"].set_stroke(width=2.0)
            verify_row["row"].next_to(
                gt_4n["row"], DOWN, buff=0.3)
            check_safe_margins(verify_row["row"], "verify_row")
            self.play(FadeIn(verify_row["row"]), run_time=0.6)
            active_mobs.append(verify_row["row"])

    # ── QUESTION ──────────────────────────────────────────
    def show_question(self):
        active_mobs = []
        badge = create_heading_badge("Question")
        check_safe_margins(badge, "badge_q")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        with self.voiceover(
            text=(
                '<bookmark mark="bk_question"/>A sequence is seven, '
                'ten, thirteen, sixteen. '
                'Write the general term and '
                '<bookmark mark="bk_find20"/>find the twentieth term.'
            )
        ) as tracker:
            self.wait_until_bookmark("bk_question")
            q_text = Text(
                "Sequence: 7, 10, 13, 16  —  Find the general term"
                " and the 20th term.",
                font="Poppins", font_size=22, color=PURPLE)
            q_text.move_to(UP * 2.6)
            check_safe_margins(q_text, "q_text")
            self.play(FadeIn(q_text), run_time=0.7)
            active_mobs.append(q_text)

            # question sequence blocks
            self.wait_until_bookmark("bk_find20")
            qseq = make_seq_blocks([7, 10, 13, 16])
            qseq["group"].move_to(ORIGIN)
            check_safe_margins(qseq["group"], "q_blocks")
            self.play(Create(qseq["blocks"]), run_time=0.9)
            self.play(FadeIn(qseq["labels"]), run_time=0.5)
            active_mobs.append(qseq["group"])

            q_pos_lbls = VGroup()
            for i, blk in enumerate(qseq["blocks"]):
                pl = Text(f"n={i+1}", font="Poppins",
                          font_size=18, color=PALE_PURPLE)
                pl.next_to(blk, DOWN, buff=0.22)
                q_pos_lbls.add(pl)
            check_safe_margins(q_pos_lbls, "q_pos_lbls")
            self.play(FadeIn(q_pos_lbls), run_time=0.5)
            active_mobs.append(q_pos_lbls)

            pos20 = Text("n = 20  =  ?",
                         font="Poppins", font_size=24,
                         color=ORANGE_HL)
            pos20.move_to(DOWN * 1.8)
            check_safe_margins(pos20, "pos20")
            self.play(FadeIn(pos20), run_time=0.6)
            active_mobs.append(pos20)

        self._qseq_group  = qseq["group"]
        self._q_pos_lbls  = q_pos_lbls
        self._pos20       = pos20
        self._active_from_question = active_mobs

    # ── SOLUTION ──────────────────────────────────────────
    def show_solution(self):
        active_mobs = list(self._active_from_question)

        # shift blocks + labels + pos20 to right together
        self.play(
            self._qseq_group.animate.move_to(
                RIGHT * 3.2 + UP * 0.6),
            self._q_pos_lbls.animate.move_to(
                RIGHT * 3.2 + DOWN * 0.05),
            self._pos20.animate.move_to(
                RIGHT * 3.2 + DOWN * 0.85),
            run_time=1.0)

        badge_old = active_mobs[0]
        badge_new = create_heading_badge("Solution")
        self.play(
            FadeOut(badge_old), FadeIn(badge_new),
            run_time=0.5)
        active_mobs[0] = badge_new

        with self.voiceover(
            text=(
                '<bookmark mark="bk_s1"/>Common difference is three. '
                '<bookmark mark="bk_s2"/>Try three n and adjust. '
                '<bookmark mark="bk_s3"/>Three times one equals three, '
                'but the first term is seven. '
                '<bookmark mark="bk_s4"/>So add four. '
                '<bookmark mark="bk_s5"/>General term is three n plus four. '
                '<bookmark mark="bk_s6"/>Check: three times one plus four '
                'equals seven. '
                '<bookmark mark="bk_s7"/>Correct. '
                '<bookmark mark="bk_s8"/>For the twentieth term: three times '
                'twenty plus four equals sixty-four.'
            )
        ) as tracker:
            # ── PHASE 1: steps 1–4 (font 24, buff 0.25 → max 5) ──
            mgr = StepManager(
                self,
                start_anchor=UP * 2.0 + LEFT * 3.5,
                font_size=24, buff=0.25)

            self.wait_until_bookmark("bk_s1")
            s1 = math_obj(
                r"\text{Common difference} = 3",
                font_size=24)
            mgr.add_step(s1)
            active_mobs.append(s1)

            self.wait_until_bookmark("bk_s2")
            s2 = math_obj(
                r"\text{Try: } 3n, \text{ adjust}",
                font_size=24)
            mgr.add_step(s2)
            active_mobs.append(s2)

            self.wait_until_bookmark("bk_s3")
            s3 = math_obj(
                r"3 \times 1 = 3, \text{ need } 7",
                font_size=24)
            mgr.add_step(s3)
            active_mobs.append(s3)

            self.wait_until_bookmark("bk_s4")
            s4 = math_obj(
                r"\text{Adjustment: } +4",
                font_size=24, color=ORANGE_HL)
            mgr.add_step(s4)
            active_mobs.append(s4)

            # ── clear phase 1 before phase 2 ──
            self.wait_until_bookmark("bk_s5")
            mgr.fadeout_all()
            for item in [s1, s2, s3, s4]:
                if item in active_mobs:
                    active_mobs.remove(item)

            # ── PHASE 2: steps 5–7 ──
            mgr2 = StepManager(
                self,
                start_anchor=UP * 2.0 + LEFT * 3.5,
                font_size=24, buff=0.25)

            s5 = math_obj(
                r"\text{General term: } 3n + 4",
                font_size=24, color=ORANGE_HL)
            mgr2.add_step(s5)
            active_mobs.append(s5)

            self.wait_until_bookmark("bk_s6")
            s6 = math_obj(
                r"3(1) + 4 = 7",
                font_size=24)
            mgr2.add_step(s6)
            active_mobs.append(s6)

            self.wait_until_bookmark("bk_s7")
            s7 = math_obj(
                r"\checkmark \text{ Correct}",
                font_size=24, color=ORANGE_HL)
            mgr2.add_step(s7)
            active_mobs.append(s7)

            self.wait_until_bookmark("bk_s8")
            s8 = math_obj(
                r"3(20) + 4 = 64",
                font_size=24, color=ORANGE_HL)
            mgr2.add_step(s8)
            active_mobs.append(s8)

            # legend
            legend = make_legend(
                [("n", "= position number")],
                position=DR, buff=0.4)
            check_safe_margins(legend, "legend")
            self.play(FadeIn(legend), run_time=0.6)
            active_mobs.append(legend)

        self.wait(0.6)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()

    # ── SUMMARY ───────────────────────────────────────────
    def show_summary(self):
        active_mobs = []
        badge = create_heading_badge("Summary")
        check_safe_margins(badge, "badge_sum")
        self.play(FadeIn(badge), run_time=0.5)
        active_mobs.append(badge)

        summary_points = [
            "Let n represent the position number"
            " of a term in the sequence.",
            "Use the common difference and adjustment"
            " to build the general term.",
            "Substitute any position number n to find"
            " that term directly.",
        ]
        positions = [UP * 1.5, ORIGIN, DOWN * 1.5]

        with self.voiceover(
            text=(
                '<bookmark mark="bk_sum1"/>Let n represent the position '
                'number of a term in the sequence. '
                '<bookmark mark="bk_sum2"/>Use the common difference and '
                'adjustment to build the general term. '
                '<bookmark mark="bk_sum3"/>Substitute any position number n '
                'to find that term directly.'
            )
        ) as tracker:
            for i, (txt, pos) in enumerate(
                    zip(summary_points, positions)):
                self.wait_until_bookmark(f"bk_sum{i + 1}")
                bullet = make_bullet_point(
                    txt, position=pos, font_size=24)
                check_safe_margins(bullet, f"bullet_{i}")
                self.play(FadeIn(bullet), run_time=0.7)
                active_mobs.append(bullet)

        self.wait(0.6)
        clear_and_transition(self, active_mobs, LAVENDER_BG)
        active_mobs.clear()