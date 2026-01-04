import argparse
import json
import time
from pathlib import Path
import requests


def load_jsonl(path: Path):
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def contains_all(haystack: str, needles):
    h = (haystack or "").lower()
    for n in needles:
        if n.lower() not in h:
            return False
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--api", default="http://127.0.0.1:8000/chat")
    ap.add_argument("--session_prefix", default="EVAL")
    ap.add_argument("--infile", default=str(Path(__file__).parent / "testset.jsonl"))
    ap.add_argument("--outdir", default=str(Path(__file__).parent / "out"))
    ap.add_argument("--sleep", type=float, default=0.2)
    args = ap.parse_args()

    infile = Path(args.infile)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    tests = load_jsonl(infile)

    results = []
    route_ok = 0
    cite_ok = 0
    refusal_ok = 0
    contains_ok = 0

    for i, t in enumerate(tests, start=1):
        session_id = f"{args.session_prefix}-{t['id']}"
        payload = {"session_id": session_id, "message": t["message"]}

        try:
            r = requests.post(args.api, json=payload, timeout=120)
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            data = {"error": str(e)}

        # basic checks
        got_route = data.get("route")
        got_citations = data.get("citations", [])
        got_refusal = bool(data.get("refusal"))
        got_answer = data.get("answer", "")

        exp_route = t.get("expected_route")
        exp_cites = bool(t.get("expect_citations"))
        exp_refusal = bool(t.get("expect_refusal"))
        exp_contains = t.get("expect_answer_contains", [])

        r_ok = (got_route == exp_route)
        c_ok = ((len(got_citations) > 0) == exp_cites)
        rf_ok = (got_refusal == exp_refusal)
        ct_ok = contains_all(got_answer, exp_contains)

        route_ok += int(r_ok)
        cite_ok += int(c_ok)
        refusal_ok += int(rf_ok)
        contains_ok += int(ct_ok)

        results.append(
            {
                "id": t["id"],
                "persona": t.get("persona"),
                "message": t["message"],
                "expected_route": exp_route,
                "got_route": got_route,
                "expect_citations": exp_cites,
                "got_citations_n": len(got_citations) if isinstance(got_citations, list) else None,
                "expect_refusal": exp_refusal,
                "got_refusal": got_refusal,
                "contains_ok": ct_ok,
                "route_ok": r_ok,
                "citations_ok": c_ok,
                "refusal_ok": rf_ok,
                "raw": data,
            }
        )

        print(
            f"[{i:02d}/{len(tests)}] {t['id']} route={got_route} "
            f"(exp {exp_route}) cites={len(got_citations) if isinstance(got_citations, list) else 'NA'} "
            f"(exp {exp_cites}) refusal={got_refusal} (exp {exp_refusal})"
        )
        time.sleep(args.sleep)

    # write results
    out_json = outdir / "results.json"
    out_json.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")

    n = len(tests)
    summary = {
        "n": n,
        "route_accuracy": route_ok / n,
        "citation_presence_accuracy": cite_ok / n,
        "refusal_flag_accuracy": refusal_ok / n,
        "answer_contains_accuracy": contains_ok / n,
    }
    (outdir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("\n=== SUMMARY ===")
    for k, v in summary.items():
        if k == "n":
            print(f"{k}: {v}")
        else:
            print(f"{k}: {v:.3f}")
    print(f"\nSaved: {out_json}")
    print(f"Saved: {outdir / 'summary.json'}")


if __name__ == "__main__":
    main()
