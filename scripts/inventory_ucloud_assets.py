#!/usr/bin/env python3
"""Project-oriented UCloud asset inventory (customer-facing summary helper).

This script intentionally avoids printing PublicKey/PrivateKey values.
It summarizes what can be derived from currently supported security clients,
and provides placeholders/gaps for console-assisted inventory of other asset groups.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ucloud_security import SecurityCenter
from ucloud_security.exceptions import ConfigError, UCloudAPIError


def safe_call(fn, *args, **kwargs):
    try:
        return {"ok": True, "data": fn(*args, **kwargs)}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def count_from_dataset(payload: Dict[str, Any], *keys: str) -> int | None:
    for key in keys:
        val = payload.get(key)
        if isinstance(val, list):
            return len(val)
    return None


def build_sc(args):
    if args.config:
        return SecurityCenter(args.config)
    return SecurityCenter.from_credentials(
        public_key=args.public_key,
        private_key=args.private_key,
        project_id=args.project_id,
    )


def add_gap(gaps: List[Dict[str, str]], category: str, reason: str):
    gaps.append({"category": category, "reason": reason})


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--config")
    p.add_argument("--public-key")
    p.add_argument("--private-key")
    p.add_argument("--project-id")
    args = p.parse_args()

    if not args.config and not (args.public_key and args.private_key and args.project_id):
        raise SystemExit("provide --config or all of --public-key --private-key --project-id")

    sc = build_sc(args)
    project_id = args.project_id or "from-config"

    result: Dict[str, Any] = {
        "project": {
            "project_id": project_id,
            "scope": "current_project",
            "cross_project_note": "If the user asks for all-account assets, review other ProjectIds as well.",
        },
        "identity": {
            "api_key_entry": "https://console.ucloud.cn/uapi/apikey",
            "api_key_exposure": "not_outputting_keys",
        },
        "overview": {
            "compute": {"status": "needs_console_or_future_api_support"},
            "network": {"status": "partial"},
            "data_and_storage": {"status": "needs_console_or_future_api_support"},
            "security": {"status": "partial"},
            "enterprise_apps": {"status": "needs_console_or_console_checks"},
        },
        "security_assets": {},
        "network_assets": {},
        "gaps": [],
        "findings": [],
        "next_steps": [],
    }

    # Firewall
    fw = safe_call(sc.firewall.list_firewalls)
    result["network_assets"]["firewall"] = fw
    if fw["ok"] and isinstance(fw["data"], dict):
        result["overview"]["network"]["firewalls"] = count_from_dataset(fw["data"], "DataSet", "FirewallSet")
    else:
        add_gap(result["gaps"], "firewall", "Unable to confirm via current API path")

    # WAF
    waf_domains = safe_call(sc.waf.list_domains)
    result["security_assets"]["waf_domains"] = waf_domains
    if waf_domains["ok"] and isinstance(waf_domains["data"], dict):
        domain_count = count_from_dataset(waf_domains["data"], "DomainHostList", "DataSet", "Domains")
        result["overview"]["security"]["waf_domains"] = domain_count
        if domain_count == 0:
            result["findings"].append("UWAF exists but currently has 0 protected domains.")
    else:
        add_gap(result["gaps"], "waf_domains", "Unable to confirm WAF domain inventory")

    waf_quota = safe_call(sc.waf.check_quota)
    result["security_assets"]["waf_quota"] = waf_quota
    if not waf_quota["ok"]:
        add_gap(result["gaps"], "waf_quota", "Unable to confirm WAF quota details")

    # DDoS
    ddos = safe_call(sc.ddos.list_services)
    result["security_assets"]["ddos_services"] = ddos
    if ddos["ok"] and isinstance(ddos["data"], dict):
        result["overview"]["security"]["ddos_services"] = count_from_dataset(
            ddos["data"], "ServiceSet", "DataSet", "ResourceSet"
        )
    else:
        add_gap(result["gaps"], "ddos_services", "Unable to confirm DDoS service inventory")

    # Known console-assisted gaps for first-version inventory system
    add_gap(result["gaps"], "compute", "Use console home page/resource pages to review UHost, ULightHost, UPHost, UK8S, Cube, UHub")
    add_gap(result["gaps"], "network", "Use console to review EIP, ULB, UVPC, subnet, NAT, UDNS in full")
    add_gap(result["gaps"], "data_and_storage", "Use console to review US3, UFS/UPFS, UDB, MongoDB, PostgreSQL, SQL Server, UMem")
    add_gap(result["gaps"], "enterprise_apps", "Use console to review UDNR, USSL, ICP resources")

    result["next_steps"] = [
        "Use console home page resource overview as the first-pass summary for compute/network/database counts.",
        "If the user needs all-account inventory, continue with https://console.ucloud.cn/uproject/list across other ProjectIds.",
        "Direct users to https://console.ucloud.cn/uapi/apikey for key retrieval steps without printing keys.",
        "For UWAF onboarding gaps, use https://console.ucloud.cn/udnr/registerInquire , https://console.ucloud.cn/ussl , https://console.ucloud.cn/icp , https://console.ucloud.cn/uewaf .",
    ]

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (ConfigError, UCloudAPIError) as e:
        raise SystemExit(str(e))
