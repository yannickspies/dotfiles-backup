#!/usr/bin/env python3
"""Extract key metrics from a Lighthouse JSON report."""
import json
import sys

def extract(data):
    audits = data.get("audits", {})
    cats = data.get("categories", {})

    def audit(key):
        a = audits.get(key, {})
        val = a.get("numericValue")
        score = a.get("score")
        err = a.get("errorMessage")
        if err:
            return {"value": f"ERROR: {err}", "score": "error"}
        if val is not None:
            return {"value": round(val, 2), "score": round(score, 2) if score is not None else None}
        return {"value": "N/A", "score": None}

    perf = cats.get("performance", {}).get("score")
    perf_display = round(perf * 100) if perf is not None else "N/A"

    metrics = {
        "Performance Score": perf_display,
        "FCP": audit("first-contentful-paint"),
        "LCP": audit("largest-contentful-paint"),
        "CLS": audit("cumulative-layout-shift"),
        "TBT": audit("total-blocking-time"),
        "Speed Index": audit("speed-index"),
    }

    # LCP element
    lcp_el = audits.get("largest-contentful-paint-element", {})
    lcp_items = lcp_el.get("details", {}).get("items", [])
    lcp_element = None
    for item in lcp_items:
        node = item.get("node", {})
        if node:
            lcp_element = node.get("selector", node.get("snippet", "unknown"))
            break

    # Layout shift elements
    ls_el = audits.get("layout-shift-elements", {})
    ls_items = ls_el.get("details", {}).get("items", [])
    shifts = []
    for item in ls_items:
        node = item.get("node", {})
        score = item.get("score", 0)
        selector = node.get("selector", "unknown") if node else "unknown"
        shifts.append({"element": selector, "score": round(score, 4)})

    # Document size
    doc_size = None
    net = audits.get("network-requests", {}).get("details", {}).get("items", [])
    for req in net:
        if req.get("resourceType") == "Document" and req.get("url", "").startswith(data.get("requestedUrl", "http")[:30]):
            doc_size = {"transfer": req.get("transferSize", 0), "resource": req.get("resourceSize", 0)}
            break

    return {
        "url": data.get("requestedUrl", "unknown"),
        "lighthouseVersion": data.get("lighthouseVersion", "unknown"),
        "fetchTime": data.get("fetchTime", "unknown"),
        "metrics": metrics,
        "lcpElement": lcp_element,
        "layoutShifts": shifts,
        "documentSize": doc_size,
    }

def fmt_bytes(b):
    if b is None:
        return "N/A"
    if b > 1024:
        return f"{b / 1024:.1f} KB"
    return f"{b} B"

def fmt_ms(v):
    if isinstance(v, str):
        return v
    if v > 1000:
        return f"{v / 1000:.1f}s"
    return f"{round(v)}ms"

def main():
    if len(sys.argv) < 2:
        print("Usage: python read-lighthouse-json.py <file.json> [file2.json ...]")
        sys.exit(1)

    results = []
    for path in sys.argv[1:]:
        with open(path) as f:
            data = json.load(f)
        results.append((path, extract(data)))

    if len(results) == 1:
        path, r = results[0]
        m = r["metrics"]
        print(f"## Lighthouse Report: {r['url']}")
        print(f"Version: {r['lighthouseVersion']} | Fetched: {r['fetchTime']}")
        print()
        print(f"| Metric | Value | Score |")
        print(f"|--------|-------|-------|")
        print(f"| Performance | **{m['Performance Score']}** | |")
        for key in ["FCP", "LCP", "CLS", "TBT", "Speed Index"]:
            v = m[key]
            val = fmt_ms(v["value"]) if key != "CLS" else v["value"]
            sc = v["score"] if v["score"] is not None else "—"
            print(f"| {key} | {val} | {sc} |")
        print()
        if r["lcpElement"]:
            print(f"**LCP element:** `{r['lcpElement']}`")
        else:
            print("**LCP element:** None detected")
        if r["layoutShifts"]:
            print(f"**Layout shifts:**")
            for s in r["layoutShifts"]:
                print(f"  - `{s['element']}` (score: {s['score']})")
        else:
            print("**Layout shifts:** None")
        if r["documentSize"]:
            print(f"**Document size:** {fmt_bytes(r['documentSize']['transfer'])} transferred, {fmt_bytes(r['documentSize']['resource'])} uncompressed")
    else:
        # Comparison table
        print("## Lighthouse Comparison")
        print()
        header = "| Metric |"
        sep = "|--------|"
        for path, r in results:
            label = path.split("/")[-1][:40]
            header += f" {label} |"
            sep += "------|"
        print(header)
        print(sep)

        m_all = [r["metrics"] for _, r in results]
        perf_row = "| **Performance** |"
        for m in m_all:
            perf_row += f" **{m['Performance Score']}** |"
        print(perf_row)

        for key in ["FCP", "LCP", "CLS", "TBT", "Speed Index"]:
            row = f"| {key} |"
            for m in m_all:
                v = m[key]
                val = fmt_ms(v["value"]) if key != "CLS" else v["value"]
                sc = v["score"] if v["score"] is not None else "—"
                row += f" {val} ({sc}) |"
            print(row)

        print()
        for path, r in results:
            label = path.split("/")[-1][:40]
            lcp = r["lcpElement"] or "None"
            shifts = ", ".join(f"`{s['element']}` ({s['score']})" for s in r["layoutShifts"]) or "None"
            doc = fmt_bytes(r["documentSize"]["transfer"]) if r["documentSize"] else "N/A"
            print(f"**{label}:** LCP=`{lcp}` | Shifts: {shifts} | Doc: {doc}")

if __name__ == "__main__":
    main()
