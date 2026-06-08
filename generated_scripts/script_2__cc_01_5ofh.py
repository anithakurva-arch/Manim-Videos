import os
os.environ["OPENAI_API_KEY"] = "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"
from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.openai import OpenAIService

config.background_color = "#E7E5F3"
LAVENDER_BG = "#E7E5F3"
PURPLE = "#7464CE"
ORANGE_HL = "#FF9302"

class Script2Cc01Scene(VoiceoverScene):
    def construct(self):
        self.set_speech_service(OpenAIService(voice="shimmer", model="gpt-4o-mini-tts"))
        
        # SEGMENT 1: HOOK
        title = Text("Sets: Three Ways to Describe", font="Poppins", color=PURPLE, font_size=40)
        bookshelf_icon = SVGMobject("bookshelf").set_color(PURPLE).scale(0.8) if os.path.exists("bookshelf.svg") else Circle(color=PURPLE, fill_opacity=0.3).scale(0.5)
        bookshelf_icon.next_to(title, DOWN, buff=0.5)
        
        with self.voiceover(text="""<bookmark mark='intro'/> Hello students! Imagine you need to tell a friend over the phone which books to bring from your shelf, but there are too many to list one by one.""") as tracker:
            self.play(FadeIn(title))
            self.wait_until_bookmark("intro")
            self.play(bookshelf_icon.animate.scale(1.2))
            self.wait(0.5)
        
        with self.voiceover(text="""<bookmark mark='examples'/> You could say 