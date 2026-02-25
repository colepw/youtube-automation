from pydub import AudioSegment
from pathlib import Path
import random

USE_FIRE = False  # set to True if you want to add fire crackle underneath
TARGET = 3 * 60 * 60 * 1000  # target length in milliseconds (3 hours)
TOLERANCE = 3 * 60 * 1000  # tolerance in milliseconds (3 minutes)

def soft_shuffle(paths):
    paths = list(paths)
    random.shuffle(paths)

    result = []
    while paths:
        placed = False

        for i, p in enumerate(paths):
            # use filename prefix before " - " or "_" as a simple grouping key
            name = p.stem.lower()
            key = name.split(" - ")[0].split("_")[0]

            if not result:
                result.append(paths.pop(i))
                placed = True
                break

            prev_name = result[-1].stem.lower()
            prev_key = prev_name.split(" - ")[0].split("_")[0]

            if key != prev_key:
                result.append(paths.pop(i))
                placed = True
                break

        # if all remaining tracks share same key, just place one
        if not placed:
            result.append(paths.pop(0))

    return result

# folder with your lofi tracks
music_folder = Path("snips")
fire_file = Path("fire_crackle.mp3")  # optional
output_file = "final_3hr_mix.mp3"

# load and sort files
music_files = [*music_folder.glob("*.mp3"), *music_folder.glob("*.wav"), *music_folder.glob("*.m4a")]
random.seed(42)  # optional: same random order every run
music_files = soft_shuffle(music_files)

if not music_files:
    raise FileNotFoundError("No audio files found in snips/")

# concatenate all tracks
final_mix = AudioSegment.silent(duration=0)
for f in music_files:
    track = AudioSegment.from_file(f)

    if (len(final_mix) + len(track)) > (TARGET + TOLERANCE):
        continue

    if track.dBFS != float("-inf"):
        target_dbfs = -16.0
        track = track.apply_gain(target_dbfs - track.dBFS)

    # optional fade in/out to reduce harsh transitions
    track = track.fade_in(1000).fade_out(1000)
    final_mix += track

# optional: add looping fire crackle underneath
if USE_FIRE and fire_file.exists():
    fire = AudioSegment.from_file(fire_file) - 20  # lower volume by 20 dB
    while len(fire) < len(final_mix):
        fire += fire
    fire = fire[:len(final_mix)]
    final_mix = final_mix.overlay(fire)

# export
final_mix.export(output_file, format="mp3", bitrate="192k")
print(f"Saved: {output_file}")
print(f"Length (ms): {len(final_mix)}")
print(f"Length (sec): {len(final_mix)/1000:.2f}")
print(f"Length (min): {len(final_mix)/(1000*60):.2f}")
print(f"Length (hrs): {len(final_mix)/(1000*60*60):.2f}")