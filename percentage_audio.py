import asyncio
import edge_tts
import os
import re

VOICE = "en-IN-NeeraNeural"   # alt: "en-US-AriaNeural", "en-IN-PrabhatNeural"
RATE = "-8%"

# Use plain ASCII punctuation only — no "…" or "—"
narrations = {
    "segment1": (
        "You've seen these everywhere, fifty percent off. "
        "And on report cards, scored eighty-three percent. "
        "But what does that little percent sign actually mean?"
    ),
    "segment2": (
        "The word per cent comes from Latin, per centum. "
        "It means, out of a hundred. "
        "So twenty-five percent simply means, twenty-five parts out of every hundred. "
        "The percent symbol, is just another way of writing, over one hundred."
    ),
    "segment3": (
        "Here's a fraction, three-fourths. "
        "To turn it into a percentage, line it up against a scale of one hundred. "
        "Three-fourths lands exactly, on seventy-five. "
        "So three-fourths equals seventy-five over one hundred, equals seventy-five percent. "
        "The rule? Scale the fraction, so its denominator becomes one hundred."
    ),
    "segment4": (
        "Careful, a bigger percentage doesn't always mean a bigger quantity. "
        "Fifty percent of twenty is only ten, but twenty-five percent of eighty is twenty. "
        "A percentage, always depends on the whole it refers to."
    ),
    "segment5": (
        "Let's apply this. "
        "A cyclist has covered seventy-five percent of a two hundred and forty kilometre journey. "
        "How far has he cycled? Let's use our five-step method. "
        "Given. Total distance is two hundred forty kilometres, and percentage cycled is seventy-five percent. "
        "To Find. Distance cycled, in kilometres. "
        "Strategy. Distance cycled equals seventy-five by one hundred, times the total distance. "
        "Solution. Seventy-five by one hundred times two hundred forty, "
        "which is three by four times two hundred forty, which equals one hundred eighty kilometres. "
        "Answer. The cyclist has cycled one hundred eighty kilometres."
    ),
    "segment6": (
        "So, a percentage is just parts out of one hundred. "
        "Any fraction can be scaled to a percentage. "
        "And a percentage of any quantity, is found by multiplying. "
        "Look around today, where do you see percentages at work?"
    ),
}

def sanitize(text: str) -> str:
    """Strip any non-ASCII / smart punctuation that edge-tts rejects."""
    text = text.replace("…", ", ").replace("—", ", ").replace("–", ", ")
    text = text.replace("\u2019", "'").replace("\u2018", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    # collapse extra spaces
    text = re.sub(r"\s+", " ", text).strip()
    return text

async def generate(name: str, text: str):
    print(f"🎙  Generating {name}.mp3 ...")
    clean = sanitize(text)
    tts = edge_tts.Communicate(text=clean, voice=VOICE, rate=RATE)
    await tts.save(f"audio_output/{name}.mp3")

async def main():
    os.makedirs("audio_output", exist_ok=True)
    for name, text in narrations.items():
        await generate(name, text)
    print("\n✅ All audio files saved in 'audio_output/'")

if __name__ == "__main__":
    asyncio.run(main())