"""Spricht die Sätze aus <ordner>/nova-video.json mit Chatterbox Multilingual (MIT-Lizenz) auf Deutsch.
Läuft im GitHub-Ablauf „Nova spricht“. Ergebnis: <ordner>/voice/line-NN.wav (eine Datei pro Satz).
Stimmfarbe kommt aus der Referenz tts/ref/nova-ref-a.wav (Stimme A, Piper Kerstin, CC0).
Chatterbox setzt ein unhörbares Wasserzeichen, das die Datei als KI-Audio kennzeichnet.
"""
import json, os, sys
import torch, torchaudio
from chatterbox.mtl_tts import ChatterboxMultilingualTTS

folder = sys.argv[1]
cfg = json.load(open(os.path.join(folder, "nova-video.json")))
ref = cfg.get("ref", "tts/ref/nova-ref-a.wav")
import traceback
log = open(os.path.join(folder, "voice-log.txt"), "w")
try:
    model = ChatterboxMultilingualTTS.from_pretrained(device=torch.device("cpu"))
    os.makedirs(os.path.join(folder, "voice"), exist_ok=True)
    for i, line in enumerate(cfg["lines"], 1):
        wav = model.generate(line.replace("*", ""), language_id="de", audio_prompt_path=ref,
                             exaggeration=cfg.get("exaggeration", 0.5), cfg_weight=cfg.get("cfg_weight", 0.5))
        torchaudio.save(os.path.join(folder, "voice", f"line-{i:02d}.wav"), wav, model.sr)
        print("Satz", i, "fertig", file=log, flush=True)
except Exception:
    traceback.print_exc(file=log)
    log.close()
    raise
