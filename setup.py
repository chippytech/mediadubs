from setuptools import setup

setup(
    name="mediadubs",
    version="0.1.0",
    py_modules=["main"],
    python_requires=">=3.9",
    install_requires=[
        "numpy",
        "soundfile",
        "openai-whisper",
        "argostranslate",
        "piper-tts",
    ],
    entry_points={
        "console_scripts": [
            "mediadubs=main:main",
        ]
    },
)
