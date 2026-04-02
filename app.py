from pathlib import Path
from uuid import uuid4

from flask import Flask, render_template, request, send_from_directory, url_for

from speech_service import build_ssml_preview, get_default_voice, synthesize_text_to_file


BASE_DIR = Path(__file__).resolve().parent
GENERATED_DIR = BASE_DIR / "generated"

DEMO_TEXTS = {
    "podcast": (
        "Welcome back to the show. Today we are exploring how high quality text "
        "to speech can transform content creation, accessibility, and productivity."
    ),
    "narration": (
        "In a quiet village surrounded by olive trees, a young inventor worked "
        "through the night, chasing an idea that could change everything."
    ),
    "product": (
        "Meet Voxify, your AI voice studio for natural, expressive, and "
        "multilingual speech generation."
    ),
}

VOICE_OPTIONS = [
    {"id": "tr-TR-AhmetNeural", "name": "Ahmet", "tag": "Warm", "language": "tr"},
    {"id": "tr-TR-EmelNeural", "name": "Emel", "tag": "Calm", "language": "tr"},
    {"id": "en-US-JennyNeural", "name": "Jenny", "tag": "Bright", "language": "en"},
    {"id": "en-US-GuyNeural", "name": "Guy", "tag": "Deep", "language": "en"},
]

LANGUAGE_OPTIONS = [
    {"id": "en", "name": "English"},
    {"id": "tr", "name": "Turkish"},
]

LANGUAGE_DEFAULT_VOICE = {
    "en": "en-US-JennyNeural",
    "tr": "tr-TR-AhmetNeural",
}

FEATURES = [
    "40+ Languages",
    "Studio Voices",
    "Custom Tone",
    "Export Audio",
]

RECENT_PROJECTS = [
    {"title": "Podcast Intro", "meta": "English • Jenny • 00:42"},
    {"title": "YouTube Narration", "meta": "Turkish • Emel • 01:18"},
    {"title": "App Voiceover", "meta": "English • Guy • 00:27"},
]

HIGHLIGHTS = [
    "Clear left-to-right workflow: text input, voice controls, preview, export.",
    "Strong CTA placement for generation and audio download.",
    "Direct Azure Speech integration behind a Flask backend.",
    "Good base for adding file upload, history, and user accounts later.",
]


def render_index(**overrides):
    text = overrides.get("text", DEMO_TEXTS["product"])
    selected_language = overrides.get("selected_language", "tr")
    selected_voice = overrides.get(
        "selected_voice",
        LANGUAGE_DEFAULT_VOICE.get(selected_language, get_default_voice()),
    )
    speed = float(overrides.get("speed", 1.0))
    pitch = float(overrides.get("pitch", 1.0))

    context = {
        "demo_texts": DEMO_TEXTS,
        "voice_options": VOICE_OPTIONS,
        "language_options": LANGUAGE_OPTIONS,
        "feature_items": FEATURES,
        "recent_projects": RECENT_PROJECTS,
        "highlights": HIGHLIGHTS,
        "text": text,
        "selected_language": selected_language,
        "selected_voice": selected_voice,
        "speed": speed,
        "pitch": pitch,
        "char_count": len(text),
        "word_count": len(text.split()) if text.strip() else 0,
        "estimated_seconds": int(((len(text.split()) / 150) * 60) + 0.9999) if text.strip() else 0,
        "ssml_preview": build_ssml_preview(text=text, voice_name=selected_voice, speed=speed, pitch=pitch),
        "default_voice": get_default_voice(),
    }
    context.update(overrides)
    return render_template("index.html", **context)


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["GENERATED_DIR"] = GENERATED_DIR

    @app.get("/")
    def index():
        return render_index()

    @app.post("/synthesize")
    def synthesize():
        text = request.form.get("text", "").strip()
        selected_language = request.form.get("language", "tr").strip() or "tr"
        voice = request.form.get("voice", "").strip() or LANGUAGE_DEFAULT_VOICE.get(
            selected_language,
            get_default_voice(),
        )
        speed = float(request.form.get("speed", "1.0"))
        pitch = float(request.form.get("pitch", "1.0"))

        if not text:
            return render_index(
                error="Please enter text to convert into speech.",
                text=text,
                selected_language=selected_language,
                selected_voice=voice,
                speed=speed,
                pitch=pitch,
            ), 400

        filename = f"{uuid4().hex}.wav"
        output_path = app.config["GENERATED_DIR"] / filename

        try:
            synthesize_text_to_file(
                text=text,
                output_path=output_path,
                voice_name=voice,
                speed=speed,
                pitch=pitch,
            )
        except RuntimeError as exc:
            return render_index(
                error=str(exc),
                text=text,
                selected_language=selected_language,
                selected_voice=voice,
                speed=speed,
                pitch=pitch,
            ), 500

        audio_url = url_for("serve_audio", filename=filename)
        return render_index(
            success="Audio file generated successfully.",
            text=text,
            selected_language=selected_language,
            selected_voice=voice,
            speed=speed,
            pitch=pitch,
            audio_url=audio_url,
            filename=filename,
        )

    @app.get("/audio/<path:filename>")
    def serve_audio(filename: str):
        return send_from_directory(app.config["GENERATED_DIR"], filename, as_attachment=False)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
