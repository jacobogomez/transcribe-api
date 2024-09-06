from pydub import AudioSegment


def convert_to_wav_pcm_mono(input_file, output_file, frame_rate=16000):
    input_file.seek(0)
    audio = AudioSegment.from_file(input_file)
    audio = audio.set_channels(1)
    audio = audio.set_frame_rate(frame_rate)
    audio.export(output_file, format="wav", codec="pcm_s16le")
