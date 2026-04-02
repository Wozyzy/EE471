# EE471

Flask-based Azure Speech text-to-speech demo for EE471.

## Features

- Accepts text input from a browser form on `localhost`
- Generates a `.wav` audio file with Azure Speech Services
- Plays the generated audio in the page and lets you download it
- Keeps Azure credentials in a local `.env` file

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Update `.env` with your own Azure Speech credentials:

```env
AZURE_SPEECH_KEY=your_azure_speech_key
AZURE_SPEECH_REGION=your_service_region
AZURE_SPEECH_VOICE=tr-TR-AhmetNeural
```

## Run The Website

```bash
source .venv/bin/activate
flask --app app run --debug
```

Open `http://127.0.0.1:5000` in your browser.

## Optional CLI Test

```bash
python speech_tts.py "Merhaba, Azure Speech Services hazir."
```
