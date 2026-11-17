#!/usr/bin/env python3
"""Game voice pack (游戏配音): a CSV of lines -> one audio file per line, named by id, grouped by role, plus manifest.

  python3 scripts/game_voice.py selftest
  python3 scripts/game_voice.py check LINES.csv [--map 角色=账号角色名 ...]
  python3 scripts/game_voice.py build LINES.csv -o OUT [--voice 默认角色] [--map 村长=老者 --map 少女=少女角色]
                       [--layout role|flat] [--only id1,id2] [--dry-run]

CSV (UTF-8, header row): id, role, text, tag(optional, an expressive tag allowed by `capabilities`), speed(optional),
lang(optional language hint), note(optional, never spoken). Rows with the same id are an error.
Outputs: OUT/<role>/<id>.wav (or OUT/<id>.wav with --layout flat), manifest.csv, manifest.json, report.txt,
cache/ (a line is generated once; edit one row and rerun to regenerate only that row; --only redoes chosen ids).
Python 3.9+ standard library only. MIT licence.
"""
import argparse, csv, json, os, re, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audio_kit as K  # noqa: E402

VERSION = "1.0.0"
ID_RE = re.compile(r"^[A-Za-z0-9_\-.]+$")
SAFE_RE = re.compile(r'[\\/:*?"<>|\s]+')


def parse(path):
    rows = list(csv.DictReader(open(path, encoding="utf-8-sig", newline="")))
    if not rows:
        raise K.KitError("CSV 里没有数据行：第一行是表头 id,role,text[,tag,speed,lang,note]")
    need = {"id", "role", "text"}
    if not need <= set(rows[0].keys()):
        raise K.KitError("CSV 表头至少要有 id,role,text 三列，当前是：%s" % ",".join(rows[0].keys()))
    seen, out = set(), []
    for n, r in enumerate(rows, 2):
        i = (r.get("id") or "").strip()
        if not i or i.startswith("#"):
            continue
        if not ID_RE.match(i):
            raise K.KitError("第 %d 行 id「%s」只能用字母、数字、下划线、横线、点（要当文件名）" % (n, i))
        if i in seen:
            raise K.KitError("第 %d 行 id「%s」重复" % (n, i))
        seen.add(i)
        text = (r.get("text") or "").strip()
        if not text:
            raise K.KitError("第 %d 行（%s）text 为空" % (n, i))
        sp = (r.get("speed") or "").strip()
        out.append({"id": i, "role": (r.get("role") or "").strip() or "default", "text": text,
                    "tag": (r.get("tag") or "").strip() or None, "speed": float(sp) if sp else None,
                    "lang": (r.get("lang") or "").strip() or None, "note": (r.get("note") or "").strip()})
    if not out:
        raise K.KitError("CSV 里没有可用的数据行")
    return out


def parse_map(items):
    m = {}
    for s in items or []:
        k, _, v = s.partition("=")
        if not v:
            raise K.KitError("--map 写成 剧中角色=账号里的角色名，例如 --map 村长=老者")
        m[k.strip()] = v.strip()
    return m


def folder(role):
    return SAFE_RE.sub("_", role).strip("_") or "default"


def cmd_check(a):
    rows = parse(a.csv)
    mp = parse_map(a.map)
    roles = {}
    for r in rows:
        roles.setdefault(r["role"], []).append(r)
    total = 0.0
    for role, rs in roles.items():
        sec = sum(K.estimate_seconds(r["text"]) for r in rs)
        total += sec
        print("%s → 账号角色：%s｜%d 句｜约 %.0f 秒" % (role, mp.get(role) or a.voice or "（未指定）", len(rs), sec))
    print("共 %d 句、%d 个角色，粗估总时长 %.1f 分钟" % (len(rows), len(roles), total / 60))
    long_ = [r["id"] for r in rows if len(r["text"]) > 120]
    if long_:
        print("提示：以下句子超过 120 字，生成时会在标点处自动切开再拼回：" + "、".join(long_))
    return 0


def cmd_build(a):
    K.check_speed(a.speed)
    rows = parse(a.csv)
    mp = parse_map(a.map)
    if a.only:
        want = set(x.strip() for x in a.only.split(","))
        miss = want - set(r["id"] for r in rows)
        if miss:
            raise K.KitError("--only 里的 id 不在 CSV 中：%s" % "、".join(sorted(miss)))
        rows = [r for r in rows if r["id"] in want]
    K.require_key(a.dry_run)
    vmap = {}
    for r in rows:
        name = mp.get(r["role"]) or a.voice
        vmap[r["role"]] = ["--dry-run"] if a.dry_run else K.voice_args(name, None)
    out = a.output
    cache = os.path.join(out, "cache")
    man = []
    for k, r in enumerate(rows, 1):
        parts = []
        for s in K.sentences(r["text"]):
            parts.append(K.generate(s, vmap[r["role"]], cache, a.dry_run, model=a.model, speed=r["speed"] or a.speed,
                                    tags=[r["tag"]] if r["tag"] else None, language=r["lang"] or a.language,
                                    label="%d/%d %s" % (k, len(rows), r["id"])))
        pcm = parts[0]
        for p in parts[1:]:
            pcm += K.silence(0.15) + p
        pcm = K.normalize(pcm, a.peak)
        rel = ("%s.wav" % r["id"]) if a.layout == "flat" else os.path.join(folder(r["role"]), "%s.wav" % r["id"])
        os.makedirs(os.path.dirname(os.path.join(out, rel)) or out, exist_ok=True)
        K.write_wav(os.path.join(out, rel), pcm)
        man.append({"id": r["id"], "role": r["role"], "file": rel.replace(os.sep, "/"), "seconds": round(K.duration(pcm), 2),
                    "tag": r["tag"] or "", "text": r["text"], "note": r["note"]})
    with open(os.path.join(out, "manifest.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(man[0].keys()))
        w.writeheader()
        w.writerows(man)
    json.dump(man, open(os.path.join(out, "manifest.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    tot = sum(m["seconds"] for m in man)
    longest = max(man, key=lambda m: m["seconds"])
    open(os.path.join(out, "report.txt"), "w", encoding="utf-8").write(
        "共 %d 条，总时长 %.1f 秒；最长：%s（%.1f 秒）\n%s\n" % (len(man), tot, longest["id"], longest["seconds"],
        "\n".join("%s\t%s\t%.1fs" % (m["id"], m["file"], m["seconds"]) for m in man)))
    print("%d 条 → %s/（manifest.csv / manifest.json / report.txt）%s" % (
        len(man), out, "  [dry-run：占位提示音，未调用接口]" if a.dry_run else ""))
    return 0


def cmd_selftest(a):
    d = tempfile.mkdtemp()
    p = os.path.join(d, "l.csv")
    open(p, "w", encoding="utf-8").write("id,role,text,tag,speed,lang,note\nnpc_001,村长,欢迎来到青石村。,,,,开场\nnpc_002,少女,你看见我的猫了吗？,,1.1,,\nui_ok,系统,任务完成！,,,,\n")
    rows = parse(p)
    assert [r["id"] for r in rows] == ["npc_001", "npc_002", "ui_ok"] and rows[1]["speed"] == 1.1
    try:
        open(p, "a", encoding="utf-8").write("ui_ok,系统,重复,,,,\n")
        parse(p)
        raise SystemExit("duplicate id not rejected")
    except K.KitError:
        pass
    open(p, "w", encoding="utf-8").write("id,role,text\nnpc_001,村长,欢迎。\nui_ok,系统,完成！\n")
    class A: pass
    x = A(); x.csv = p; x.output = d + "/o"; x.voice = x.model = x.speed = x.language = x.only = None
    x.map, x.layout, x.peak, x.dry_run = ["村长=老者"], "role", -1.0, True
    cmd_build(x)
    assert os.path.exists(d + "/o/村长/npc_001.wav") and os.path.exists(d + "/o/系统/ui_ok.wav")
    m = json.load(open(d + "/o/manifest.json", encoding="utf-8"))
    assert len(m) == 2 and m[0]["file"] == "村长/npc_001.wav"
    print("selftest ok")
    return 0


def main():
    p = argparse.ArgumentParser(prog="game_voice.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--version", action="version", version=VERSION)
    s = p.add_subparsers(dest="cmd", required=True)
    s.add_parser("selftest").set_defaults(fn=cmd_selftest)
    for name in ("check", "build"):
        c = s.add_parser(name)
        c.add_argument("csv")
        c.add_argument("--voice", help="default account role name for roles without --map")
        c.add_argument("--map", action="append", help="剧中角色=账号角色名 (repeatable)")
        if name == "build":
            c.add_argument("-o", "--output", default="voicepack_out")
            c.add_argument("--layout", choices=("role", "flat"), default="role")
            c.add_argument("--only", help="comma separated ids to (re)generate")
            c.add_argument("--language")
            c.add_argument("--speed", type=float)
            c.add_argument("--model", choices=("expressive", "standard"))
            c.add_argument("--peak", type=float, default=-1.0)
            c.add_argument("--dry-run", action="store_true")
        c.set_defaults(fn=cmd_check if name == "check" else cmd_build)
    a = p.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    K.run(main)
