import os
os.environ["OPENAI_API_KEY"] = "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"
from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.openai import OpenAIService

config.background_color = "#E7E5F3"
LAVENDER_BG = "#E7E5F3"
PURPLE = "#7464CE"
ORANGE_HL = "#FF9302"
DARK_TEXT = "#2D2D2D"

class Script1Cc019457190Scene(VoiceoverScene):
    def construct(self):
        self.set_speech_service(
            OpenAIService(
                voice="shimmer",
                model="gpt-4o-mini-tts"
            )
        )
        
        # Title card
        title = Text("Letter-Numbers &\nAlgebraic Generalisation", font="Poppins", font_size=48, color=PURPLE)
        subtitle = Text("Concise Mathematical Notation", font="Poppins", font_size=28, color=DARK_TEXT)
        subtitle.next_to(title, DOWN, buff=0.3)
        
        with self.voiceover(text="""<bookmark mark='intro'/>Hello students! Imagine you are helping organise a school event where each table seats exactly five students. <break time='0.4s'/>""") as tracker:
            self.play(FadeIn(title))
            self.wait(0.5)
            self.play(FadeIn(subtitle))
            self.wait_until_bookmark("intro")
        
        self.play(FadeOut(title), FadeOut(subtitle))
        
        # Tables and chairs visualization
        def create_table_group(num_tables):
            group = VGroup()
            for i in range(num_tables):
                table = Rectangle(width=0.8, height=0.6, color=ORANGE_HL, fill_opacity=0.3)
                chairs = VGroup()
                for j in range(5):
                    chair = Circle(radius=0.15, color=PURPLE, fill_opacity=0.5)
                    angle = j * 2 * PI / 5
                    chair.shift(0.5 * np.array([np.cos(angle), np.sin(angle), 0]))
                    chairs.add(chair)
                table_unit = VGroup(table, chairs)
                table_unit.shift(RIGHT * (i - num_tables/2 + 0.5) * 2)
                group.add(table_unit)
            return group
        
        tables_3 = create_table_group(3)
        tables_3.scale(0.6)
        label_3_tables = Text("3 tables", font="Poppins", font_size=24, color=DARK_TEXT).next_to(tables_3, UP)
        label_15_students = Text("15 students", font="Poppins", font_size=24, color=ORANGE_HL).next_to(tables_3, DOWN)
        
        with self.voiceover(text="""You need to work out how many students can be seated for any number of tables — three tables, ten tables, or even a hundred tables. <break time='0.5s'/>""") as tracker:
            self.play(Create(tables_3))
            self.play(FadeIn(label_3_tables), FadeIn(label_15_students))
            self.wait(1)
        
        self.play(FadeOut(tables_3), FadeOut(label_3_tables), FadeOut(label_15_students))
        
        # Repetitive equations
        eq1 = MathTex("5", r"\times", "3", "=", "15", font_size=36, color=DARK_TEXT).shift(UP*1.5)
        eq2 = MathTex("5", r"\times", "10", "=", "50", font_size=36, color=DARK_TEXT).shift(UP*0.5)
        eq3 = MathTex("5", r"\times", "100", "=", "500", font_size=36, color=DARK_TEXT).shift(DOWN*0.5)
        
        with self.voiceover(text="""Writing out 