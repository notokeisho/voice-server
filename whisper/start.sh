#!/bin/bash

# VAD (Voice Activity Detection) settings
# Can be toggled via environment variables
VAD_OPTS=""
if [ "${ENABLE_VAD:-true}" = "true" ]; then
    VAD_OPTS="--vad \
        --vad-model /app/models/ggml-silero-vad.bin \
        --vad-threshold ${VAD_THRESHOLD:-0.5} \
        --vad-min-speech-duration-ms ${VAD_MIN_SPEECH_MS:-250} \
        --vad-min-silence-duration-ms ${VAD_MIN_SILENCE_MS:-100} \
        --vad-speech-pad-ms ${VAD_SPEECH_PAD_MS:-50}"
fi

exec /app/whisper-server \
    --model /app/models/ggml-large-v3-turbo-q8_0.bin \
    --host 0.0.0.0 \
    --port 8080 \
    --language ${VOICE_LANGUAGE:-ja} \
    $VAD_OPTS
