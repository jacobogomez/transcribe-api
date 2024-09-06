import json
import sys
import wave

from vosk import KaldiRecognizer, Model, SetLogLevel

SetLogLevel(-1)

wf = wave.open(sys.argv[1], "rb")

model = Model("vosk-model-small-es-0.42")
rec = KaldiRecognizer(model, wf.getframerate())
rec.SetMaxAlternatives(10)
rec.SetWords(True)

while True:
    data = wf.readframes(4000)
    if len(data) == 0:
        break
    if rec.AcceptWaveform(data):
        print(json.loads(rec.Result()))
    else:
        print(json.loads(rec.PartialResult()))

print(json.loads(rec.FinalResult()).get("alternatives")[-1].get("text"))
