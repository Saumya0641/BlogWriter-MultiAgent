from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Iterator, Tuple

import pandas as pd
import streamlit as st

from backend import app


# ── helpers ───────────────────────────────────────────────────────────────────

def safe_slug(title: str) -> str:
    s = title.strip().lower()
    s = re.sub(r"[^a-z0-9 _-]+", "", s)
    s = re.sub(r"\s+", "_", s).strip("_")
    return s or "blog"


def try_stream(graph_app, inputs: Dict[str, Any]) -> Iterator[Tuple[str, Any]]:
    try:
        for step in graph_app.stream(inputs, stream_mode="updates"):
            yield ("updates", step)
        out = graph_app.invoke(inputs)
        yield ("final", out)
        return
    except Exception:
        pass
    try:
        for step in graph_app.stream(inputs, stream_mode="values"):
            yield ("values", step)
        out = graph_app.invoke(inputs)
        yield ("final", out)
        return
    except Exception:
        pass
    out = graph_app.invoke(inputs)
    yield ("final", out)


def extract_latest_state(current: Dict[str, Any], payload: Any) -> Dict[str, Any]:
    if isinstance(payload, dict):
        if len(payload) == 1 and isinstance(next(iter(payload.values())), dict):
            current.update(next(iter(payload.values())))
        else:
            current.update(payload)
    return current


def list_past_blogs() -> List[Path]:
    files = [p for p in Path(".").glob("*.md") if p.is_file()]
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return files


def read_md(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


def extract_title(md: str, fallback: str) -> str:
    for line in md.splitlines():
        if line.startswith("# "):
            return line[2:].strip() or fallback
    return fallback


def load_blog_file(p: Path) -> Dict[str, Any]:
    """Load a .md file and its companion .json if it exists."""
    md_text  = read_md(p)
    plan     = None
    evidence = []
    mode     = None
    queries  = []

    json_path = p.with_suffix(".json")
    if json_path.exists():
        try:
            meta     = json.loads(json_path.read_text(encoding="utf-8"))
            plan     = meta.get("plan")
            evidence = meta.get("evidence", [])
            mode     = meta.get("mode")
            queries  = meta.get("queries", [])
        except Exception:
            pass

    return {"plan": plan, "evidence": evidence, "mode": mode, "queries": queries, "final": md_text}


def plan_to_dict(plan_obj: Any) -> Dict | None:
    if plan_obj is None:
        return None
    if hasattr(plan_obj, "model_dump"):
        return plan_obj.model_dump()
    if isinstance(plan_obj, dict):
        return plan_obj
    try:
        return json.loads(json.dumps(plan_obj, default=str))
    except Exception:
        return None


# ── page config ───────────────────────────────────────────────────────────────

st.set_page_config(page_title="LangGraph Blog Writer", layout="wide")
st.title("Blog Writing Agent")

if "last_out" not in st.session_state:
    st.session_state["last_out"] = None
if "logs" not in st.session_state:
    st.session_state["logs"] = []

# ── sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.header("Generate New Blog")
    topic = st.text_area("Topic", height=120)
    as_of = st.date_input("As-of date", value=date.today())
    run_btn = st.button("🚀 Generate Blog", type="primary")

    st.divider()
    st.subheader("Past blogs")

    past_files = list_past_blogs()
    if not past_files:
        st.caption("No saved blogs found (*.md in current folder).")
        selected_label = None
        file_by_label  = {}
    else:
        options: List[str] = []
        file_by_label: Dict[str, Path] = {}
        for p in past_files[:50]:
            try:
                md_text = read_md(p)
                title   = extract_title(md_text, p.stem)
            except Exception:
                title = p.stem
            label = f"{title}  ·  {p.name}"
            options.append(label)
            file_by_label[label] = p

        selected_label = st.radio(
            "Select a blog to load", options, index=0, label_visibility="collapsed"
        )

        if st.button("📂 Load selected blog"):
            p = file_by_label.get(selected_label)
            if p:
                st.session_state["last_out"] = load_blog_file(p)
                st.rerun()

# ── tabs ──────────────────────────────────────────────────────────────────────

tab_plan, tab_evidence, tab_preview, tab_logs = st.tabs(
    ["🧩 Plan", "🔎 Evidence", "📝 Markdown Preview", "🧾 Logs"]
)

# ── run ───────────────────────────────────────────────────────────────────────

if run_btn:
    if not topic.strip():
        st.warning("Please enter a topic.")
        st.stop()

    st.session_state["logs"] = []

    inputs: Dict[str, Any] = {
        "topic": topic.strip(),
        "mode": "",
        "needs_research": False,
        "queries": [],
        "evidence": [],
        "plan": None,
        "as_of": as_of.isoformat(),
        "recency_days": 7,
        "sections": [],
        "final": "",
    }

    status        = st.status("Running graph…", expanded=True)
    progress_area = st.empty()
    current_state: Dict[str, Any] = {}
    last_node = None

    for kind, payload in try_stream(app, inputs):
        if kind in ("updates", "values"):
            node_name = None
            if (isinstance(payload, dict) and len(payload) == 1
                    and isinstance(next(iter(payload.values())), dict)):
                node_name = next(iter(payload.keys()))
            if node_name and node_name != last_node:
                status.write(f"➡️ Node: `{node_name}`")
                last_node = node_name

            current_state = extract_latest_state(current_state, payload)

            plan_raw = current_state.get("plan")
            n_tasks  = len(plan_to_dict(plan_raw).get("tasks", [])) if plan_to_dict(plan_raw) else None
            summary  = {
                "mode":           current_state.get("mode"),
                "needs_research": current_state.get("needs_research"),
                "queries":        (current_state.get("queries") or [])[:5],
                "evidence_count": len(current_state.get("evidence") or []),
                "tasks":          n_tasks,
                "sections_done":  len(current_state.get("sections") or []),
            }
            progress_area.json(summary)
            st.session_state["logs"].append(
                f"[{kind}] {json.dumps(payload, default=str)[:1200]}"
            )

        elif kind == "final":
            out = payload
            # enrich with mode/queries from current_state if not in final payload
            if isinstance(out, dict):
                out.setdefault("mode",    current_state.get("mode"))
                out.setdefault("queries", current_state.get("queries", []))
            st.session_state["last_out"] = out
            status.update(label="✅ Done", state="complete", expanded=False)
            st.session_state["logs"].append("[final] received final state")

# ── render output ─────────────────────────────────────────────────────────────

out = st.session_state.get("last_out")

if out:

    # ── Plan tab ──────────────────────────────────────────────────────────────
    with tab_plan:
        st.subheader("Plan")
        plan_dict = plan_to_dict(out.get("plan"))
        if not plan_dict:
            st.info("No plan found. (Older blogs saved before metadata support won't have a plan.)")
        else:
            st.write("**Title:**", plan_dict.get("blog_title", ""))
            c1, c2, c3 = st.columns(3)
            c1.write("**Audience:** " + str(plan_dict.get("audience", "")))
            c2.write("**Tone:** "     + str(plan_dict.get("tone", "")))
            c3.write("**Kind:** "     + str(plan_dict.get("blog_kind", "")))

            tasks = plan_dict.get("tasks", [])
            if tasks:
                df = pd.DataFrame([
                    {
                        "id":                 t.get("id"),
                        "title":              t.get("title"),
                        "target_words":       t.get("target_words"),
                        "requires_research":  t.get("requires_research"),
                        "requires_citations": t.get("requires_citations"),
                        "requires_code":      t.get("requires_code"),
                        "tags":               ", ".join(t.get("tags") or []),
                    }
                    for t in tasks
                ]).sort_values("id")
                st.dataframe(df, use_container_width=True, hide_index=True)
                with st.expander("Task details (JSON)"):
                    st.json(tasks)

    # ── Evidence tab ──────────────────────────────────────────────────────────
    with tab_evidence:
        st.subheader("Evidence")

        mode    = out.get("mode")
        queries = out.get("queries") or []

        if mode:
            st.caption(f"Mode: `{mode}`")
        if queries:
            with st.expander(f"🔍 Search queries ({len(queries)})"):
                for q in queries:
                    st.markdown(f"- {q}")

        evidence = out.get("evidence") or []
        if not evidence:
            st.info("No evidence returned (closed_book mode or no Tavily results).")
        else:
            rows = []
            for e in evidence:
                if hasattr(e, "model_dump"):
                    e = e.model_dump()
                rows.append({
                    "title":        e.get("title"),
                    "published_at": e.get("published_at"),
                    "source":       e.get("source"),
                    "url":          e.get("url"),
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # ── Preview tab ───────────────────────────────────────────────────────────
    with tab_preview:
        st.subheader("Markdown Preview")
        final_md = out.get("final") or ""
        if not final_md:
            st.warning("No final markdown found.")
        else:
            st.markdown(final_md)

            plan_obj   = out.get("plan")
            blog_title = (
                plan_obj.blog_title if hasattr(plan_obj, "blog_title")
                else plan_obj.get("blog_title", "blog") if isinstance(plan_obj, dict)
                else extract_title(final_md, "blog")
            )
            st.download_button(
                "⬇️ Download Markdown",
                data=final_md.encode("utf-8"),
                file_name=f"{safe_slug(blog_title)}.md",
                mime="text/markdown",
            )

    # ── Logs tab ──────────────────────────────────────────────────────────────
    with tab_logs:
        st.subheader("Logs")
        st.text_area(
            "Event log",
            value="\n\n".join(st.session_state["logs"][-80:]),
            height=520,
        )

else:
    with tab_plan:
        st.info("Enter a topic and click **Generate Blog**.")
    with tab_evidence:
        st.info("Evidence will appear here after a run.")
    with tab_preview:
        st.info("Preview will appear here after a run.")
    with tab_logs:
        st.info("Logs will appear here after a run.")