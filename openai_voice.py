from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.openai import OpenAIService

class OpenAIVoiceDemo(VoiceoverScene):
    def construct(self):
        self.set_speech_service(
            OpenAIService(
                voice="nova",
                model="tts-1",
                transcription_model=None,
            ),
            create_subcaption=False,
        )

        circle = Circle(color=BLUE)
        square = Square(color=RED).shift(2 * RIGHT)

        with self.voiceover(text="Hello! This is OpenAI's text to speech in action.") as tracker:
            self.play(Create(circle), run_time=tracker.duration)

        with self.voiceover(text="Doesn't this voice sound much more natural?") as tracker:
            self.play(Create(square), run_time=tracker.duration)

        with self.voiceover(text="Let's make them disappear gracefully.") as tracker:
            self.play(FadeOut(circle), FadeOut(square), run_time=tracker.duration)