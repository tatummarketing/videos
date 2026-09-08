#!/usr/bin/env python3
"""Build the Robinhood teaser VO with ElevenLabs + arcade soundtrack.

Reuses the podcast pipeline techniques: per-clip edge trims and fades,
pause caps, tempo lift for Hannah, per-clip loudness match, tail-blip
removal, deterministic tempo jitter, and a piecewise music envelope.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
# ELEVENLABS_API_KEY comes from the environment or a .env in the project root
ENV = os.path.join(HERE, "..", ".env")
BGM = os.path.join(HERE, "bgm-arcade.mp3")
SPEECH_MIX = os.path.join(HERE, "teaser-speech.wav")
FINAL = os.path.join(HERE, "teaser-final.mp3")
TIMINGS = os.path.join(HERE, "timings.json")

VOICES = {"Mantas": "N8xJcEC4oSwBaqtm3e8m", "Hannah": "mrmaApeLxpgZi4RK7oGq"}
BASE = {
    "Mantas": {"stability": 0.35, "similarity_boost": 0.75, "style": 0.5,
               "use_speaker_boost": True, "speed": 1.05},
    "Hannah": {"stability": 0.45, "similarity_boost": 0.75, "speed": 1.08},
}
MODEL = "eleven_multilingual_v2"

# speaker, text, gap-before (s), per-turn settings overrides
TURNS = [
    ("Mantas", "Hey — this is the Tatum Podcast. I'm Mantas.", 0.0, {}),
    ("Hannah", "And I'm Hannah. We've spent all week digging into Robinhood Chain.", 0.18, {}),
    ("Mantas", "They built it for tokenized stocks and on-chain finance… with twenty-eight million customers already behind it.", 0.3, {}),
    ("Hannah", "Then volume just took off, overnight.", 0.28, {}),
    ("Mantas", "And then, of course… the meme coins showed up.", 0.25, {"speed": 1.0}),
    ("Hannah", "But that's only part of what's going on. We get into the whole thing on Spotify.", 0.45, {}),
    ("Mantas", "Link's in the comments.", 0.3, {"speed": 1.0}),
]

LEAD_IN = 0.9      # music alone before the first line
BED = 0.26         # music level under speech
INTRO_LVL = 0.85   # opening sting level
SWELL = 0.5        # after the last line
TAIL = 3.4         # swell + fade after speech ends


def jitter(i, spread=0.015):
    h = int(hashlib.md5(f"turn-{i}".encode()).hexdigest()[:6], 16)
    return (h % 1000) / 1000.0 * 2 * spread - spread


def api_key():
    key = os.environ.get("ELEVENLABS_API_KEY", "")
    if not key and os.path.exists(ENV):
        with open(ENV) as f:
            for line in f:
                m = re.match(r"\s*ELEVENLABS_API_KEY\s*=\s*(\S+)", line)
                if m:
                    key = m.group(1)
    if not key:
        sys.exit("no api key")
    return key


def tts(key, speaker, text, prev_text, next_text, overrides, out):
    settings = {**BASE[speaker], **overrides}
    body = {"text": text, "model_id": MODEL, "voice_settings": settings}
    if prev_text:
        body["previous_text"] = prev_text[-300:]
    if next_text:
        body["next_text"] = next_text[:300]
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{VOICES[speaker]}?output_format=mp3_44100_128",
        data=json.dumps(body).encode(),
        headers={"xi-api-key": key, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as resp:
        with open(out, "wb") as f:
            f.write(resp.read())


def duration_of(path):
    return float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True, check=True).stdout.strip())


def mean_volume(path):
    err = subprocess.run(["ffmpeg", "-i", path, "-af", "volumedetect", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    m = re.search(r"mean_volume:\s*(-?[\d.]+) dB", err)
    return float(m.group(1)) if m else None


def kill_tail_blip(path):
    err = subprocess.run(
        ["ffmpeg", "-i", path, "-af", "silencedetect=n=-45dB:d=0.35", "-f", "null", "-"],
        capture_output=True, text=True).stderr
    events = re.findall(r"silence_(start|end): ([\d.]+)", err)
    if len(events) < 2 or events[-1][0] != "end" or events[-2][0] != "start":
        return
    resume, cut_at = float(events[-1][1]), float(events[-2][1])
    if duration_of(path) - resume < 0.25:
        tmp = path + ".tmp.wav"
        subprocess.run(["ffmpeg", "-y", "-i", path, "-af",
                        f"atrim=0:{cut_at + 0.05:.3f},afade=t=out:st={cut_at - 0.06:.3f}:d=0.11", tmp],
                       check=True, capture_output=True)
        os.replace(tmp, path)


def process(src, dst, speaker, i):
    pause_cap = 0.5 if speaker == "Hannah" else 0.6
    filters = (
        "silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.06,"
        "areverse,silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.12,areverse,"
        f"silenceremove=stop_periods=-1:stop_duration={pause_cap}:stop_threshold=-45dB"
    )
    base = 1.06 if speaker == "Hannah" else 1.0
    tempo = base * (1 + jitter(i))
    if abs(tempo - 1.0) > 0.005:
        filters += f",atempo={tempo:.3f}"
    filters += ",afade=t=in:st=0:d=0.08,areverse,afade=t=in:st=0:d=0.1,areverse"
    subprocess.run(["ffmpeg", "-y", "-i", src, "-af", filters, "-ar", "44100", "-ac", "1", dst],
                   check=True, capture_output=True)
    kill_tail_blip(dst)
    mv = mean_volume(dst)
    if mv is not None and abs(-18.5 - mv) > 0.5:
        tmp = dst + ".g.wav"
        subprocess.run(["ffmpeg", "-y", "-i", dst, "-af", f"volume={-18.5 - mv:.2f}dB", tmp],
                       check=True, capture_output=True)
        os.replace(tmp, dst)


def main():
    key = api_key()
    force = "--force" in sys.argv
    procs, starts = [], []
    t = LEAD_IN
    for i, (speaker, text, gap, overrides) in enumerate(TURNS):
        raw = os.path.join(HERE, f"t{i}-{speaker.lower()}.mp3")
        proc = os.path.join(HERE, f"t{i}-{speaker.lower()}.wav")
        if force or not os.path.exists(raw) or os.path.getsize(raw) < 1000:
            prev = next((x[1] for x in reversed(TURNS[:i]) if x[0] == speaker), "")
            nxt = next((x[1] for x in TURNS[i + 1:] if x[0] == speaker), "")
            print(f"tts {i} {speaker}...", flush=True)
            tts(key, speaker, text, prev, nxt, overrides, raw)
        process(raw, proc, speaker, i)
        t += gap
        starts.append(round(t, 3))
        t += duration_of(proc)
        procs.append(proc)

    speech_end = t
    total = speech_end + TAIL
    print(f"speech ends {speech_end:.2f}, total {total:.2f}")

    # speech mix
    inputs, delays, mix = [], [], []
    for i, (proc, st) in enumerate(zip(procs, starts)):
        inputs += ["-i", proc]
        delays.append(f"[{i}:a]adelay={int(st * 1000)}|{int(st * 1000)}[d{i}]")
        mix.append(f"[d{i}]")
    fc = ";".join(delays) + f";{''.join(mix)}amix=inputs={len(procs)}:normalize=0:duration=longest[out]"
    subprocess.run(["ffmpeg", "-y", *inputs, "-filter_complex", fc, "-map", "[out]",
                    "-t", f"{total:.2f}", "-ar", "44100", "-ac", "2", SPEECH_MIX],
                   check=True, capture_output=True)

    # music envelope: sting -> duck -> swell after last line -> fade
    first = starts[0]
    pts = [(0, INTRO_LVL), (max(first - 0.35, 0.1), INTRO_LVL), (first, BED),
           (speech_end, BED), (speech_end + 0.9, SWELL),
           (total - 1.4, SWELL), (total - 0.05, 0.0)]
    expr = f"{pts[-1][1]}"
    for (t0, v0), (t1, v1) in reversed(list(zip(pts, pts[1:]))):
        seg = f"{v0}" if v0 == v1 else f"{v0}+(t-{t0:.2f})/{t1 - t0:.2f}*{v1 - v0:.4f}"
        expr = f"if(lt(t,{t1:.2f}),{seg},{expr})"
    expr = f"if(lt(t,{pts[0][0]:.2f}),{pts[0][1]},{expr})"

    fc = (f"[1:a]volume='{expr}':eval=frame[bgm];"
          f"[0:a][bgm]amix=inputs=2:normalize=0:duration=first[mix];"
          f"[mix]loudnorm=I=-15:TP=-1.5:LRA=11[out]")
    subprocess.run(["ffmpeg", "-y", "-i", SPEECH_MIX, "-i", BGM,
                    "-filter_complex", fc, "-map", "[out]",
                    "-t", f"{total:.2f}", "-ar", "44100", "-b:a", "192k", FINAL],
                   check=True, capture_output=True)

    with open(TIMINGS, "w") as f:
        json.dump({"starts": starts,
                   "ends": [round(s + duration_of(p), 3) for s, p in zip(starts, procs)],
                   "speech_end": round(speech_end, 3), "total": round(total, 3),
                   "turns": [{"speaker": s, "text": x} for s, x, _, _ in TURNS]}, f, indent=2)
    print(f"final: {FINAL}")


if __name__ == "__main__":
    main()
