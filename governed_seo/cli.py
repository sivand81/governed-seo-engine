"""Command-line entry point. Local files only; no network or production writes."""
import argparse
import json
from pathlib import Path
from .core import audit_html, propose, create_run, approve_run, GovernanceError

def main():
    parser = argparse.ArgumentParser(prog="gseo", description="Offline governed SEO audit and proposals")
    sub = parser.add_subparsers(dest="command", required=True)
    audit = sub.add_parser("audit", help="Audit a local HTML file")
    audit.add_argument("html")
    plan = sub.add_parser("propose", help="Create a governed proposal from a verified local JSON record")
    plan.add_argument("source")
    approve = sub.add_parser("approve", help="Record human approval of an unchanged, validated run")
    approve.add_argument("run")
    approve.add_argument("--sha256", required=True, help="Expected source digest from the run")
    args = parser.parse_args()
    try:
        if args.command == "audit":
            result = audit_html(Path(args.html).read_text(encoding="utf-8"))
        elif args.command == "propose":
            src = json.loads(Path(args.source).read_text(encoding="utf-8"))
            result = create_run(src, propose(src))
        else:
            run = json.loads(Path(args.run).read_text(encoding="utf-8"))
            result = approve_run(run, args.sha256)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except (OSError, ValueError, GovernanceError) as exc:
        parser.exit(2, f"Error: {exc}\n")

if __name__ == "__main__":
    main()