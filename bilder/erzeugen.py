"""Erzeugt Beispielbilder mit einem frei lizenzierten Bildmodell (läuft kostenlos auf GitHub Actions, nur CPU).

Aufruf: python3 bilder/erzeugen.py bilder/jobs/<name>.json
Job-Datei: {"model": "SimianLuo/LCM_Dreamshaper_v7", "steps": 6, "size": 768,
            "images": [{"file": "bilder/<ordner>/einfach.png", "prompt": "...", "seed": 1}]}
Das Modell und seine Lizenz werden in bilder/info/ festgehalten.
"""
import json, os, sys, time
import torch
from diffusers import DiffusionPipeline

job = json.load(open(sys.argv[1]))
model = job.get("model", "SimianLuo/LCM_Dreamshaper_v7")
pipe = DiffusionPipeline.from_pretrained(model, torch_dtype=torch.float32, safety_checker=None)
pipe.set_progress_bar_config(disable=True)
torch.set_num_threads(os.cpu_count() or 4)
log = []
for im in job["images"]:
    t = time.time()
    g = torch.Generator().manual_seed(im.get("seed", 1))
    out = pipe(im["prompt"], num_inference_steps=job.get("steps", 6), guidance_scale=job.get("guidance", 8.0),
               width=job.get("size", 768), height=job.get("size", 768), generator=g).images[0]
    os.makedirs(os.path.dirname(im["file"]), exist_ok=True)
    out.save(im["file"])
    log.append(f'{im["file"]}: {time.time() - t:.0f}s, seed {im.get("seed", 1)}, prompt: {im["prompt"]}')
    print(log[-1], flush=True)
with open(os.path.join(os.path.dirname(job["images"][0]["file"]), "erzeugt.txt"), "w") as f:
    f.write(f"Modell: {model}\n" + "\n".join(log) + "\n")
