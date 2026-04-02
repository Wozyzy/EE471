from pathlib import Path
from uuid import uuid4

from flask import Flask, render_template, request, send_from_directory, url_for

from speech_service import get_default_voice, synthesize_text_to_file


BASE_DIR = Path(__file__).resolve().parent
GENERATED_DIR = BASE_DIR / "generated"


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["GENERATED_DIR"] = GENERATED_DIR

    @app.get("/")
    def index():
        return render_template("index.html", default_voice=get_default_voice())

    @app.post("/synthesize")
    def synthesize():
        text = request.form.get("text", "").strip()
        voice = request.form.get("voice", "").strip() or get_default_voice()

        if not text:
            return render_template(
                "index.html",
                default_voice=voice,
                error="Please enter text to convert into speech.",
                text=text,
            ), 400

        filename = f"{uuid4().hex}.wav"
        output_path = app.config["GENERATED_DIR"] / filename

        try:
            synthesize_text_to_file(text=text, output_path=output_path, voice_name=voice)
        except RuntimeError as exc:
            return render_template(
                "index.html",
                default_voice=voice,
                error=str(exc),
                text=text,
            ), 500

        audio_url = url_for("serve_audio", filename=filename)
        return render_template(
            "index.html",
            default_voice=voice,
            success="Audio file generated successfully.",
            text=text,
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
