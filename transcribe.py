import json
import sys
import wave
from io import BytesIO

from vosk import KaldiRecognizer, Model, SetLogLevel

import convert


class VoiceTranscriber:
    def __init__(self):
        SetLogLevel(-1)
        self.model = Model("vosk-model-small-es-0.42")

    def transcribe_audio(self, audio_file: BytesIO) -> str:
        try:
            wf = wave.open(audio_file, "rb")
        except wave.Error:
            print("Error opening file, trying to convert to suitable format")
            converted = BytesIO()
            convert.convert_to_wav_pcm_mono(audio_file, converted, 16000)
            wf = wave.open(converted, "rb")
        if (
            wf.getnchannels() != 1
            or wf.getsampwidth() != 2
            or wf.getcomptype() != "NONE"
        ):
            print("Incorrect number of channels, trying to convert to suitable format")
            converted = BytesIO()
            convert.convert_to_wav_pcm_mono(audio_file, converted, 16000)
            wf = wave.open(converted, "rb")
        recognizer = KaldiRecognizer(self.model, wf.getframerate())
        recognizer.SetWords(True)

        text_list = []
        partial_text_list = []
        partial_string = []
        length_partial_string = []
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if recognizer.AcceptWaveform(data):
                text_list.append(recognizer.Result())
            else:
                partial_text_list.append(recognizer.PartialResult())

        if len(text_list) != 0:
            jd = json.loads(text_list[0])
            text_string = jd["text"]

        elif len(partial_text_list) != 0:
            for i in range(0, len(partial_text_list)):
                temp_txt_dict = json.loads(partial_text_list[i])
                partial_string.append(temp_txt_dict["partial"])

            length_partial_string = [
                len(partial_string[j]) for j in range(0, len(partial_string))
            ]
            max_val = max(length_partial_string)
            i = length_partial_string.index(max_val)
            text_string = partial_string[i]

        else:
            text_string = ""

        return text_string


def file_path_to_bytesio(file_path):
    with open(file_path, "rb") as f:
        file_contents = f.read()

    bytes_io = BytesIO(file_contents)

    return bytes_io


if __name__ == "__main__":
    audio_path = sys.argv[1]
    to_bytes = file_path_to_bytesio(audio_path)
    transcriber = VoiceTranscriber()
    print(f"TRANSCRIBED: {transcriber.transcribe_audio(to_bytes)}")
