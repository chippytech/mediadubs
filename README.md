# MediaDubs

MediaDubs is a fully local, offline video dubbing tool that automatically translates and revoices videos into another language — without uploading your media anywhere.

It combines state-of-the-art open-source models into a single deterministic pipeline:

Whisper → Argos Translate → Piper TTS → FFmpeg

No cloud APIs. No subscriptions. No telemetry.

Features

🔒 100% local & offline

🎙️ Automatic speech transcription (Whisper)

🌍 Machine translation (Argos / LibreTranslate stack)

🗣️ Neural text-to-speech (Piper)

🎬 Automatic audio/video sync

💻 Runs on consumer hardware

🧩 Simple, auditable Python codebase

How it works

Transcribes the original audio with timestamps

Translates each segment into the target language

Synthesizes translated speech using Piper TTS

Time-stretches audio to match original pacing

Rebuilds the video with dubbed audio

All processing happens locally on your machine.

Requirements
System

Python 3.9+

ffmpeg and ffprobe available in PATH

Linux / macOS / Windows (WSL works)

Python dependencies

Installed automatically via pip:

openai-whisper

argostranslate

piper-tts

numpy

soundfile

Installation

Clone the repository and install locally:

git clone https://github.com/yourname/mediadubs.git
cd mediadubs
pip install .

Usage
mediadubs input_video.mp4 --src en --tgt es --voice es_ES-davefx-medium.onnx

Arguments
Argument	Description
video	Input video file
--src	Source language code (e.g. en)
--tgt	Target language code (e.g. es)
--voice	Piper ONNX voice model
Output

The dubbed video will be saved as:

<input>_dubbed_<language>.mp4

Language Support
Transcription

Any language supported by Whisper.

Translation

Any language pair installed in Argos Translate.

To install additional Argos language packs:

argos-translate-cli --install-language en es

Piper Voice Models

You must download Piper voice models separately.

Example:

es_ES-davefx-medium.onnx


More voices:
👉 https://github.com/rhasspy/piper

Design Philosophy

MediaDubs is intentionally:

Local-first

Scriptable

Deterministic

Minimal

It’s meant to be:

Auditable

Forkable

Embedded into other workflows

Not a black-box SaaS.

Limitations (by design)

No lip-sync correction

Limited emotional prosody (depends on Piper voice)

Translation is automatic (no human review)

These tradeoffs enable:

Speed

Privacy

Offline use

Zero marginal cost

License

MIT License
Use it, fork it, improve it.

