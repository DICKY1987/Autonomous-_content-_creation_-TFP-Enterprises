#!/usr/bin/env python3
import argparse, os, sys, time, json, pathlib, yaml
from importlib import import_module
from .scenario_models import Suite
from src.cloud.config_sync import load_credentials

def _import_or_exit(module_name, hint):
    try:
        return import_module(module_name)
    except Exception as e:
        print(f"[ERROR] Could not import {module_name}: {e}\nHint: {hint}")
        sys.exit(2)

def run_smoke(step, cfg):
    mod = _import_or_exit("src.core.automated_content_system", "Ensure src/core/automated_content_system.py is in PYTHONPATH")
    ContentConfig = getattr(mod, "ContentConfig")
    AutomatedContentSystem = getattr(mod, "AutomatedContentSystem")
    config = ContentConfig(topic=cfg.topic or "Test Topic", duration=float(cfg.duration or 20))
    creds = load_credentials(["PEXELS_API_KEY"])
    system = AutomatedContentSystem(config, creds)
    ok, result = system.create_content(cfg.topic or "Test Topic")
    if not ok:
        raise RuntimeError(f"create_content failed: {result}")
    if step.expect_keys:
        for k in step.expect_keys:
            assert k in result, f"Missing key in result: {k}"
    print("[OK] Smoke content created:", result.get("output_path"))
    return result

def run_e2e_daily(cfg):
    main = _import_or_exit("main_execution_system", "Ensure main_execution_system.py is present")
    system_cls = getattr(main, "HistoricalContentBusinessSystem", None)
    if not system_cls:
        raise RuntimeError("HistoricalContentBusinessSystem not found in main_execution_system.py")
    s = system_cls()
    # Monkey-patch uploads if not allowed
    if cfg.allow_uploads is False:
        if hasattr(s, "uploader"):
            s.uploader.upload_to_all_platforms = lambda **kwargs: []
    # Override target count if provided
    if cfg.daily_video_target:
        s.config["production_settings"]["daily_video_target"] = int(cfg.daily_video_target)
    out = s.run_daily_production()
    print("[E2E] Daily production output:", out)
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--suite", required=True, help="Path to YAML suite file")
    args = ap.parse_args()
    data = yaml.safe_load(open(args.suite, "r", encoding="utf-8"))
    suite = Suite(**data)

    if suite.suite == "smoke_short":
        result = run_smoke(suite.steps[0], suite.config)
        print(json.dumps({"status":"ok","result_keys": list(result.keys())}, indent=2))
    elif suite.suite == "e2e_daily_production":
        out = run_e2e_daily(suite.config)
        print(json.dumps({"status":"ok","summary": out}, indent=2))
    else:
        print(f"[WARN] Suite {suite.suite} not implemented in runner yet")

if __name__ == "__main__":
    main()
