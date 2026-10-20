"""Erzeugt Beispielbilder mit einem frei lizenzierten Bildmodell (läuft kostenlos auf GitHub Actions, nur CPU).

Aufruf: python3 bilder/erzeugen.py bilder/jobs/<name>.json
Job-Datei: {"model": "SimianLuo/LCM_Dreamshaper_v7", "steps": 6, "size": 768 (oder "width"/"height"),
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
ref = None
if job.get("ip_adapter"):
    # Gesichts-Ähnlichkeit zu einem Referenzbild (IP-Adapter, Apache 2.0), z. B. für Nova
    from PIL import Image
    pipe.load_ip_adapter("h94/IP-Adapter", subfolder="models", weight_name=job["ip_adapter"])
    pipe.set_ip_adapter_scale(job.get("ip_scale", 0.6))
    ref = Image.open(job["ref"]).convert("RGB")
torch.set_num_threads(os.cpu_count() or 4)
log = []
for im in job["images"]:
    t = time.time()
    g = torch.Generator().manual_seed(im.get("seed", 1))
    if ref is not None and "ip_scale" in im:
        pipe.set_ip_adapter_scale(im["ip_scale"])
    out = pipe(im["prompt"], num_inference_steps=job.get("steps", 6), guidance_scale=job.get("guidance", 8.0),
               width=job.get("width", job.get("size", 768)), height=job.get("height", job.get("size", 768)), generator=g, **({"ip_adapter_image": ref} if ref is not None else {})).images[0]
    os.makedirs(os.path.dirname(im["file"]), exist_ok=True)
    out.save(im["file"])
    log.append(f'{im["file"]}: {time.time() - t:.0f}s, seed {im.get("seed", 1)}, prompt: {im["prompt"]}')
    print(log[-1], flush=True)
with open(os.path.join(os.path.dirname(job["images"][0]["file"]), "erzeugt.txt"), "w") as f:
    f.write(f"Modell: {model}\n" + "\n".join(log) + "\n")
