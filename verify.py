#!/usr/bin/env python3
"""Emit verify.html: every pin overlaid + labelled on each cropped image."""
import json, pathlib
import build  # reuses IMAGES, Q, images_payload, questions_payload

BASE = pathlib.Path(__file__).parent
groups = {}
for i, q in enumerate(build.questions_payload):
    groups.setdefault(q["img"], []).append((i, q))

blocks = []
for name, meta in build.images_payload.items():
    cx, cy, cw, ch = meta["crop"]
    asp = (cw*meta["w"])/(ch*meta["h"])
    pins = []
    for c in meta.get("covers", []):
        L=(c[0]-cx)/cw*100; T=(c[1]-cy)/ch*100; W=c[2]/cw*100; H=c[3]/ch*100
        pins.append(f'<div class="cov" style="left:{L}%;top:{T}%;width:{W}%;height:{H}%"></div>')
    for n,(i,q) in enumerate(groups.get(name, []), 1):
        mx = (q["x"]-cx)/cw*100
        my = (q["y"]-cy)/ch*100
        pins.append(f'<div class="pin" style="left:{mx}%;top:{my}%">{n}</div>')
        pins.append(f'<div class="tag" style="left:{mx}%;top:{my}%">{n} {q["name"]}</div>')
    imgstyle = f'width:{10000/cw}%;left:{-cx/cw*100}%;top:{-cy/ch*100}%'
    src = build.assets[meta["asset"]]
    blocks.append(f'''<h2>{name} — {meta["caption"]}</h2>
    <div class="fig" style="aspect-ratio:{asp}">
      <img src="{src}" style="{imgstyle}">{''.join(pins)}
    </div>''')

html = '''<!doctype html><meta charset="utf-8"><style>
body{margin:0;background:#2a2a2a;color:#eee;font-family:sans-serif;padding:16px}
h2{font-size:14px;margin:22px 0 6px}
.fig{position:relative;width:760px;background:#fff;overflow:hidden;line-height:0}
.fig img{position:absolute;max-width:none}
.pin{position:absolute;width:16px;height:16px;transform:translate(-50%,-50%);border-radius:50%;
  background:#ffe000;border:2px solid #b5232f;color:#000;font-size:10px;font-weight:700;
  display:grid;place-items:center;line-height:1;z-index:5}
.cov{position:absolute;background:#fff;z-index:3}
.tag{position:absolute;transform:translate(10px,-50%);font-size:10px;color:#00e5ff;
  background:rgba(0,0,0,.65);padding:0 3px;white-space:nowrap;z-index:6;line-height:1.4}
</style>''' + ''.join(blocks)
(BASE/"verify.html").write_text(html)
print("wrote verify.html")
