#!/usr/bin/env python3
"""Connect one installed DCVlog source to the current host; never replace a copy.

This is a filesystem adapter, not an account-registration or cloud-sync API.
"""
import argparse
import importlib.util
import json
import os
from pathlib import Path


def updater_at(source):
    spec = importlib.util.spec_from_file_location("dcvlog_link_updater", source / "tools/update_skill.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def link_host(source, host, *, active_skill_dir=None, target_dir=None,
              home=None, environ=None, check=False):
    result = {"host_registration_verified": False, "cloud_persistence_verified": False}
    try:
        source = Path(source).expanduser().resolve(strict=True)
        updater = updater_at(source)
        # Reuse DCVlog's identity, required-files and locked-corpus validation.
        hashes = {str(p.relative_to(source)): updater.file_hash(p)
                  for p in source.rglob("*") if p.is_file() and not p.is_symlink()
                  and "__pycache__" not in p.parts}
        version = updater.validate_package(source, hashes)
        if target_dir is not None:
            target = Path(target_dir).expanduser()
            if not target.is_absolute() or target.name != "dcvlog":
                raise ValueError("--target-dir must be the host-confirmed absolute dcvlog directory")
        else:
            target = updater.host_install_target(host, home=home, environ=environ,
                                                 active_skill_dir=active_skill_dir)
        result.update(source=str(source), target=str(target), version=version)
        if source in target.resolve().parents:
            raise ValueError("Host target cannot be inside the installed source")
        if target.is_symlink() or target.exists():
            if target.resolve() == source:
                return dict(result, status="linked", verified=True)
            return dict(result, status="conflict", verified=False,
                        reason="Existing directory or link retained; use its updater or host import")
        if check:
            return dict(result, status="missing", verified=False)
        target.parent.mkdir(parents=True, exist_ok=True)
        # Do not fall back to a second independent copy on symlink failure.
        os.symlink(str(source), str(target), target_is_directory=True)
        if target.resolve(strict=True) != source:
            raise ValueError("Host link did not resolve to the installed source")
        return dict(result, status="linked", verified=True)
    except Exception as error:
        return dict(result, status="failed", verified=False, reason=str(error))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", required=True, choices=("workbuddy", "doubao"))
    parser.add_argument("--source", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--active-skill-dir")
    parser.add_argument("--target-dir", help="Only when confirmed by the current host, including cloud hosts")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = link_host(args.source, args.host, active_skill_dir=args.active_skill_dir,
                       target_dir=args.target_dir, check=args.check)
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result.get("verified") else 1


if __name__ == "__main__":
    raise SystemExit(main())
