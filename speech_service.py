import os
from pathlib import Path
from xml.sax.saxutils import escape

import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
DOTENV_PATH = BASE_DIR / ".env"
DEFAULT_VOICE = "tr-TR-AhmetNeural"


def get_default_voice() -> str:
    load_dotenv(dotenv_path=DOTENV_PATH)
    return os.getenv("AZURE_SPEECH_VOICE", DEFAULT_VOICE)


def format_percentage(multiplier: float) -> str:
    percentage = round((multiplier - 1.0) * 100)
    return f"{percentage:+d}%"


def build_ssml_preview(text: str, voice_name: str, speed: float, pitch: float) -> str:
    escaped_text = escape(text or "")
    rate = format_percentage(speed)
    pitch_value = format_percentage(pitch)
    return (
        "<speak version=\"1.0\" xml:lang=\"en-US\">"
        f"<voice name=\"{voice_name}\">"
        f"<prosody rate=\"{rate}\" pitch=\"{pitch_value}\">{escaped_text}</prosody>"
        "</voice>"
        "</speak>"
    )


def synthesize_text_to_file(
    text: str,
    output_path: Path,
    voice_name: str = DEFAULT_VOICE,
    speed: float = 1.0,
    pitch: float = 1.0,
) -> Path:
    load_dotenv(dotenv_path=DOTENV_PATH)

    speech_key = os.getenv("AZURE_SPEECH_KEY")
    speech_region = os.getenv("AZURE_SPEECH_REGION")
    selected_voice = voice_name or get_default_voice()

    if not speech_key or not speech_region:
        raise RuntimeError("Set AZURE_SPEECH_KEY and AZURE_SPEECH_REGION in your .env file.")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
    speech_config.speech_synthesis_voice_name = selected_voice
    audio_config = speechsdk.audio.AudioOutputConfig(filename=str(output_path))
    synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config,
        audio_config=audio_config,
    )
    ssml = build_ssml_preview(text=text, voice_name=selected_voice, speed=speed, pitch=pitch)

    result = synthesizer.speak_ssml_async(ssml).get()

    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        return output_path

    cancellation = result.cancellation_details
    details = cancellation.error_details or "Unknown Azure Speech error."
    raise RuntimeError(f"Synthesis failed: {details}")
