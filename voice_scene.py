from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.gtts import GTTSService

class VoiceDemo(VoiceoverScene):
    def construct(self):
        self.set_speech_service(GTTSService(lang="en", tld="com"))

        circle = Circle()
        square = Square().shift(2 * RIGHT)

        with self.voiceover(text="This is a circle.") as tracker:
            self.play(Create(circle), run_time=tracker.duration)

        with self.voiceover(text="And this is a square next to it.") as tracker:
            self.play(Create(square), run_time=tracker.duration)

        with self.voiceover(text="Now let's make them disappear.") as tracker:
            self.play(FadeOut(circle), FadeOut(square), run_time=tracker.duration)