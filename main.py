import os
import subprocess
import tempfile
import shutil
import argparse
import numpy as np
import soundfile as sf

import whisper
import argostranslate.translate as argos
from piper.voice import PiperVoice


# ---------------------------
# Helpers
# ---------------------------

def run(cmd: str):
    subprocess.run(cmd, shell=True, check=True)


def duration(path: str) -> float:
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        path,
    ]
    out = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    return float(out.decode().strip())


def split_path(path):
    base, ext = os.path.splitext(path)
    return base, ext.lstrip(".")


# ---------------------------
# ASR
# ---------------------------

def transcribe(video_path: str, model_size="base"):
    model = whisper.load_model(model_size)
    result = model.transcribe(video_path)
    return result["segments"]


# ---------------------------
# Translation
# ---------------------------

def translate_text(text: str, src_lang: str, tgt_lang: str):
    languages = argos.get_installed_languages()
    src = next(l for l in languages if l.code == src_lang)
    tgt = next(l for l in languages if l.code == tgt_lang)

    translator = src.get_translation(tgt)
    if translator is None:
        raise RuntimeError(f"No translation available: {src_lang} → {tgt_lang}")

    return translator.translate(text)


# ---------------------------
# TTS (Piper)
# ---------------------------

def load_voice(model_path: str):
    return PiperVoice.load(model_path)


def synthesize(voice, text: str, out_wav: str):
    audio = np.concatenate(
        [c.audio_float_array for c in voice.synthesize(text)]
    ).astype(np.float32)
    sf.write(out_wav, audio, voice.config.sample_rate)


# ---------------------------
# Media helpers
# ---------------------------

def cut_video(src, start, end, dst, mute=True):
    audio_flag = "-an" if mute else "-c:a aac"
    run(
        f'ffmpeg -y -ss {start} -to {end} -i "{src}" '
        f'-c:v libx264 -preset veryfast -crf 23 '
        f'{audio_flag} "{dst}"'
    )


def stretch_audio(audio_in, target_dur, audio_out):
    current = duration(audio_in)
    ratio = current / target_dur

    filters = []
    while ratio < 0.5:
        filters.append("atempo=0.5")
        ratio /= 0.5
    while ratio > 2.0:
        filters.append("atempo=2.0")
        ratio /= 2.0

    filters.append(f"atempo={ratio:.5f}")
    run(
        f'ffmpeg -y -i "{audio_in}" -filter:a "{",".join(filters)}" "{audio_out}"'
    )


def mux(video, audio, out):
    run(
        f'ffmpeg -y -i "{video}" -i "{audio}" '
        f'-map 0:v:0 -map 1:a:0 -c:v copy "{out}"'
    )


def concat(files, out):
    with tempfile.NamedTemporaryFile("w", delete=False) as f:
        for file in files:
            f.write(f"file '{os.path.abspath(file)}'\n")

    try:
        run(
            f'ffmpeg -y -f concat -safe 0 -i "{f.name}" '
            f'-c:v libx264 -preset veryfast -crf 23 '
            f'-c:a aac -movflags +faststart "{out}"'
        )
    finally:
        os.unlink(f.name)


# ---------------------------
# Pipeline
# ---------------------------

def dub_video(video, src_lang, tgt_lang, piper_model):
    base, _ = split_path(video)
    tmp = tempfile.mkdtemp()

    try:
        segments = transcribe(video)
        voice = load_voice(piper_model)

        final_segments = []
        last_end = 0.0

        for i, seg in enumerate(segments):
            start, end = seg["start"], seg["end"]

            if start > last_end:
                gap = os.path.join(tmp, f"gap_{i}.mp4")
                cut_video(video, last_end, start, gap, mute=False)
                final_segments.append(gap)

            translated = translate_text(seg["text"], src_lang, tgt_lang)

            tts = os.path.join(tmp, f"tts_{i}.wav")
            synthesize(voice, translated, tts)

            vid = os.path.join(tmp, f"vid_{i}.mp4")
            cut_video(video, start, end, vid, mute=True)

            stretched = os.path.join(tmp, f"tts_stretch_{i}.wav")
            stretch_audio(tts, end - start, stretched)

            dubbed = os.path.join(tmp, f"dub_{i}.mp4")
            mux(vid, stretched, dubbed)

            final_segments.append(dubbed)
            last_end = end

        total = duration(video)
        if last_end < total:
            tail = os.path.join(tmp, "tail.mp4")
            cut_video(video, last_end, total, tail, mute=False)
            final_segments.append(tail)

        output = f"{base}_dubbed_{tgt_lang}.mp4"
        concat(final_segments, output)
        return output

    finally:
        shutil.rmtree(tmp)


# ---------------------------
# CLI
# ---------------------------

def main():
    parser = argparse.ArgumentParser("mediadubs")
    parser.add_argument("video", help="Input video file")
    parser.add_argument("--src", required=True, help="Source language code")
    parser.add_argument("--tgt", required=True, help="Target language code")
    parser.add_argument("--voice", required=True, help="Piper ONNX voice model")

    args = parser.parse_args()
    out = dub_video(args.video, args.src, args.tgt, args.voice)
    print("Dubbed video:", out)


if __name__ == "__main__":
    main()
