from __future__ import annotations

from dataclasses import asdict
import json
import logging
import os
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from electri_city_ops.automation_contracts import (
    attach_contract,
    build_automation_contract_state,
    candidate_contract_issues,
    get_automation_contract,
    load_automation_contracts,
    validate_automation_contracts,
)
from electri_city_ops.config import AppConfig, EmailNotificationConfig, load_config
from electri_city_ops.http_probe import FetchResult, HttpProbe, extract_page_signals
from electri_city_ops.models import Finding, stable_fingerprint, utc_now
from electri_city_ops.notifier import send_email_summary
from electri_city_ops.workspace import WorkspaceGuard


PRIVATE_SITE_REPORT_SCHEMA_VERSION = 1


def load_private_site_report_profile(
    profile_path: str | Path,
    workspace_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(workspace_root).resolve() if workspace_root else Path(profile_path).resolve().parents[1]
    guard = WorkspaceGuard(root)
    resolved = guard.resolve_inside(profile_path)
    payload = json.loads(resolved.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("private site report profile must be a JSON object")
    return payload


def resolve_private_site_report_email_config(
    profile: dict[str, Any],
    workspace_root: str | Path | None = None,
) -> tuple[EmailNotificationConfig, list[str]]:
    delivery = profile.get("email_delivery", {})
    if not isinstance(delivery, dict):
        delivery = {}

    file_env = _load_env_refs_from_file(delivery, workspace_root)

    recipient = str(delivery.get("recipient", "")).strip()
    sender_env = str(delivery.get("sender_env", "SMTP_FROM")).strip()
    username_env = str(delivery.get("smtp_username_env", "SMTP_USER")).strip()
    password_env = str(delivery.get("smtp_password_env", "SMTP_PASSWORD")).strip()

    sender = os.environ.get(sender_env, "").strip() or file_env.get(sender_env, "").strip() or str(delivery.get("sender", "")).strip()
    if not sender and not sender_env:
        sender = recipient
    username = os.environ.get(username_env, "").strip() or file_env.get(username_env, "").strip()
    password = os.environ.get(password_env, "").strip() or file_env.get(password_env, "").strip()

    config = EmailNotificationConfig(
        enabled=bool(delivery.get("enabled", False)),
        sender=sender,
        recipients=(recipient,) if recipient else tuple(),
        smtp_host=str(delivery.get("smtp_host", "")).strip(),
        smtp_port=int(delivery.get("smtp_port", 587)),
        smtp_username=username,
        smtp_password=password,
        starttls=bool(delivery.get("starttls", True)),
    )

    missing_envs: list[str] = []
    if sender_env and not sender:
        missing_envs.append(sender_env)
    if username_env and not username:
        missing_envs.append(username_env)
    if password_env and not password:
        missing_envs.append(password_env)
    if not recipient:
        missing_envs.append("recipient")

    return config, missing_envs


def build_private_site_recommend_only_report(
    profile: dict[str, Any],
    app_config: AppConfig,
    probe: HttpProbe,
) -> dict[str, Any]:
    pages = profile.get("pages", [])
    if not isinstance(pages, list) or not pages:
        raise ValueError("private site report profile requires a non-empty pages list")

    runtime = profile.get("runtime_guardrail_snapshot", {})
    if not isinstance(runtime, dict):
        runtime = {}

    built_at = utc_now().isoformat()
    page_reports: list[dict[str, Any]] = []
    total_findings = 0
    warning_count = 0
    info_count = 0
    error_count = 0

    for item in pages:
        if not isinstance(item, dict):
            continue
        url = str(item.get("url", "")).strip()
        if not url:
            continue
        label = str(item.get("label", url)).strip() or url
        page_type = str(item.get("page_type", "generic")).strip() or "generic"
        result = probe.fetch(url)
        page_report = _build_page_report(
            label=label,
            page_type=page_type,
            url=url,
            result=result,
            app_config=app_config,
        )
        page_reports.append(page_report)
        page_findings = page_report["findings"]
        total_findings += len(page_findings)
        warning_count += sum(1 for finding in page_findings if finding["severity"] == "warning")
        info_count += sum(1 for finding in page_findings if finding["severity"] == "info")
        error_count += sum(1 for finding in page_findings if finding["severity"] == "high")

    try:
        automation_contracts = load_automation_contracts(app_config.workspace_root)
        automation_contract_issues = validate_automation_contracts(automation_contracts)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        automation_contracts = {"schema_version": 1, "default_policy": "deny_by_default", "contracts": []}
        automation_contract_issues = [f"automation contracts could not be loaded: {exc}"]
    automation_contract_state = build_automation_contract_state(automation_contracts, automation_contract_issues)
    priority_execution_queue = _build_priority_execution_queue(page_reports)
    global_recommendations = _build_global_recommendations(page_reports, runtime)
    automation_candidates = _build_automation_candidates(
        page_reports,
        runtime,
        str(profile.get("bound_domain", "")).strip(),
        automation_contracts,
        automation_contract_issues,
    )
    innovation_control_deck = _build_innovation_control_deck(
        page_reports,
        runtime,
        global_recommendations,
        priority_execution_queue,
    )
    email_config, missing_email_envs = resolve_private_site_report_email_config(profile, app_config.workspace_root)

    return {
        "schema_version": PRIVATE_SITE_REPORT_SCHEMA_VERSION,
        "report_id": str(profile.get("report_id", "private_site_recommend_only")),
        "built_at": built_at,
        "mode": "recommend_only",
        "bound_domain": str(profile.get("bound_domain", "")).strip(),
        "runtime_guardrail_snapshot": runtime,
        "summary": {
            "page_count": len(page_reports),
            "finding_count": total_findings,
            "warning_count": warning_count,
            "info_count": info_count,
            "high_count": error_count,
            "ready_for_recommend_only": True,
            "live_change_state": "no_live_change_proposed",
            "controlled_coexistence": runtime.get("coexistence_mode", ""),
            "priority_focus": innovation_control_deck.get("priority_focus", ""),
        },
        "pages": page_reports,
        "priority_execution_queue": priority_execution_queue,
        "automation_contract_state": automation_contract_state,
        "automation_candidates": automation_candidates,
        "innovation_control_deck": innovation_control_deck,
        "global_recommendations": global_recommendations,
        "guardrails": [
            "No live overwrite is proposed while Rank Math remains the active SEO owner.",
            "No public billing, login, delivery or license route is introduced by this report path.",
            "Recommendations remain bounded to content, head and structure review for the listed pages only.",
        ],
        "email_delivery_state": {
            "enabled": email_config.enabled,
            "recipient": list(email_config.recipients),
            "smtp_profile": str(profile.get("email_delivery", {}).get("smtp_profile", "")),
            "activation_state": "ready" if email_config.is_complete() and email_config.enabled else "operator_input_required",
            "missing_env_refs": missing_email_envs,
        },
    }


def write_private_site_report(
    report: dict[str, Any],
    profile: dict[str, Any],
    workspace_root: str | Path,
) -> tuple[Path, Path]:
    guard = WorkspaceGuard(Path(workspace_root).resolve())
    output = profile.get("output", {})
    if not isinstance(output, dict):
        output = {}
    json_path = guard.resolve_inside(output.get("json_path", "var/reports/private-site/latest.json"))
    markdown_path = guard.resolve_inside(output.get("markdown_path", "var/reports/private-site/latest.md"))
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(render_private_site_report_markdown(report), encoding="utf-8")
    return json_path, markdown_path


def render_private_site_report_markdown(report: dict[str, Any]) -> str:
    summary = report.get("summary", {})
    runtime = report.get("runtime_guardrail_snapshot", {})
    deck = report.get("innovation_control_deck", {})
    lines = [
        "# Private Site Recommend-Only Report",
        "",
        f"- Built at: `{report.get('built_at', '')}`",
        f"- Bound domain: `{report.get('bound_domain', '')}`",
        f"- Plugin mode: `{runtime.get('plugin_mode', '')}`",
        f"- Optimization gate: `{runtime.get('optimization_gate', '')}`",
        f"- Coexistence mode: `{runtime.get('coexistence_mode', '')}`",
        "",
        "## Summary",
        "",
        f"- Pages reviewed: `{summary.get('page_count', 0)}`",
        f"- Findings: `{summary.get('finding_count', 0)}`",
        f"- Warning findings: `{summary.get('warning_count', 0)}`",
        f"- Info findings: `{summary.get('info_count', 0)}`",
        f"- Live change state: `{summary.get('live_change_state', '')}`",
        f"- Priority focus: `{summary.get('priority_focus', '')}`",
        "",
        "## Innovation Control Deck",
        "",
        f"- Execution mode: `{deck.get('execution_mode', '')}`",
        f"- Priority focus: `{deck.get('priority_focus', '')}`",
        f"- Operator brief: `{deck.get('operator_brief', '')}`",
        "",
        "### Immediate Safe Actions",
        "",
    ]

    for item in deck.get("immediate_actions", []):
        lines.append(f"- {item}")

    lines.extend(["", "### Next Innovation Actions", ""])
    for item in deck.get("next_actions", []):
        lines.append(f"- {item}")

    lines.extend(["", "### Success Signals", ""])
    for item in deck.get("success_signals", []):
        lines.append(f"- {item}")

    lines.extend(["", "### Protected Holds", ""])
    for item in deck.get("protected_holds", []):
        lines.append(f"- {item}")

    lines.extend(["", "## Admin-Confirmed Automation Candidates", ""])
    contract_state = report.get("automation_contract_state", {})
    if contract_state:
        lines.extend(
            [
                f"- Contract status: `{contract_state.get('status', '')}`",
                f"- Default policy: `{contract_state.get('default_policy', '')}`",
                f"- Allowed action types: `{', '.join(contract_state.get('allowed_action_types', []))}`",
                "",
            ]
        )
    candidates = report.get("automation_candidates", [])
    if not candidates:
        lines.append("- No automation candidates are currently approved for this report lane.")
    else:
        for item in candidates:
            lines.extend(
                [
                    f"### {item.get('label', 'Candidate')}",
                    "",
                    f"- Action type: `{item.get('action_type', '')}`",
                    f"- Execution lane: `{item.get('execution_lane', '')}`",
                    f"- Automation contract: `{item.get('automation_contract_id', '')}` / `{item.get('automation_contract_version', '')}`",
                    f"- Contract state: `{item.get('automation_contract_state', '')}`",
                    f"- Runtime gate: `{item.get('runtime_gate', '')}`",
                    f"- Active SEO owner: `{item.get('active_seo_owner', '')}`",
                    f"- Target URL: `{item.get('target_url', '')}`",
                    f"- Approval state: `{item.get('approval_state', '')}`",
                    f"- Rollback state: `{item.get('rollback_state', '')}`",
                    f"- Proposed value: `{item.get('proposed_value', '')}`",
                    f"- Why this is safe now: `{item.get('proposal_reason', '')}`",
                ]
            )
            lines.append("Validation checks:")
            for check in item.get("validation_checks", []):
                lines.append(f"- {check}")
            lines.append("")

    lines.extend(["", "## Priority Execution Queue", ""])
    queue = report.get("priority_execution_queue", [])
    if not queue:
        lines.append("- No execution queue items are currently open.")
    else:
        for item in queue:
            lines.extend(
                [
                    f"### {item.get('label', 'Page')}",
                    "",
                    f"- URL: `{item.get('url', '')}`",
                    f"- Priority: `{item.get('priority', '')}`",
                    f"- Focus: `{item.get('focus', '')}`",
                    f"- Why now: `{item.get('why_now', '')}`",
                    f"- Finding count: `{item.get('finding_count', 0)}`",
                    "Top actions:",
                ]
            )
            for action in item.get("top_actions", []):
                lines.append(f"- {action}")
            lines.append("")

    lines.extend([
        "## Per-Page Signals And Recommendations",
        "",
    ])

    for page in report.get("pages", []):
        lines.extend(
            [
                f"### {page.get('label', page.get('url', 'Page'))}",
                "",
                f"- URL: `{page.get('url', '')}`",
                f"- HTTP status: `{page.get('status_code', '')}`",
                f"- Response time: `{page.get('response_ms', '')} ms`",
                f"- Title: `{page.get('title', '')}`",
                f"- Meta description length: `{page.get('meta_description_length', 0)}`",
                f"- Canonical: `{page.get('canonical', '')}`",
                f"- H1 count: `{page.get('h1_count', 0)}`",
                f"- HTML lang: `{page.get('html_lang', '')}`",
                f"- Viewport present: `{page.get('viewport_present', False)}`",
                "",
                "Findings:",
            ]
        )
        findings = page.get("findings", [])
        if not findings:
            lines.append("- No page-level findings.")
        else:
            for finding in findings:
                lines.append(f"- [{finding.get('severity', '')}] {finding.get('title', '')}: {finding.get('recommendation', '')}")
        lines.append("")

    lines.extend(["## Global Recommendations", ""])
    for item in report.get("global_recommendations", []):
        lines.append(f"- {item}")

    lines.extend(["", "## Guardrails", ""])
    for item in report.get("guardrails", []):
        lines.append(f"- {item}")

    email_delivery = report.get("email_delivery_state", {})
    lines.extend(["", "## Email Delivery State", ""])
    lines.append(f"- Activation state: `{email_delivery.get('activation_state', '')}`")
    recipient = ", ".join(email_delivery.get("recipient", []))
    lines.append(f"- Recipient: `{recipient or '(not configured)'}`")
    missing = email_delivery.get("missing_env_refs", [])
    if missing:
        lines.append(f"- Missing env refs: `{', '.join(missing)}`")

    return "\n".join(lines) + "\n"


def send_private_site_report_email(
    report: dict[str, Any],
    profile: dict[str, Any],
    workspace_root: str | Path,
    logger: logging.Logger,
) -> bool:
    email_config, missing_envs = resolve_private_site_report_email_config(profile, workspace_root)
    if missing_envs:
        logger.warning("private site report email is missing env refs: %s", ", ".join(missing_envs))
    subject_prefix = str(profile.get("email_delivery", {}).get("subject_prefix", "[Site Optimizer Private Report]")).strip()
    subject = f"{subject_prefix} {report.get('bound_domain', '')} {report.get('built_at', '')[:10]}"
    body = render_private_site_report_markdown(report)
    return send_email_summary(email_config, subject=subject, body=body, logger=logger)


def build_and_write_private_site_report(
    profile_path: str | Path,
    config_path: str | Path,
    workspace_root: str | Path,
    *,
    send_email: bool = False,
    logger: logging.Logger | None = None,
) -> tuple[dict[str, Any], Path, Path, bool]:
    profile = load_private_site_report_profile(profile_path, workspace_root)
    app_config, _ = load_config(config_path, workspace_root)
    probe = HttpProbe(
        user_agent=app_config.user_agent,
        timeout_seconds=app_config.request_timeout_seconds,
        max_response_bytes=app_config.max_response_bytes,
    )
    report = build_private_site_recommend_only_report(profile, app_config, probe)
    json_path, markdown_path = write_private_site_report(report, profile, workspace_root)
    sent = False
    if send_email:
        active_logger = logger or logging.getLogger("electri_city_ops.private_site_report")
        sent = send_private_site_report_email(report, profile, workspace_root, active_logger)
    return report, json_path, markdown_path, sent


def _build_page_report(
    *,
    label: str,
    page_type: str,
    url: str,
    result: FetchResult,
    app_config: AppConfig,
) -> dict[str, Any]:
    signals = extract_page_signals(result.body) if result.ok else None
    findings: list[Finding] = []
    if not result.ok:
        findings.append(
            Finding(
                category="fetch",
                severity="high",
                title="Page fetch failed",
                detail=f"{url} could not be fetched safely.",
                risk="medium",
                confidence=0.95,
                source="private_site_report",
                target=url,
                recommendation="Keep the bridge in recommend_only and verify the page route before any deeper optimization planning.",
            )
        )
    else:
        title = signals.title if signals else ""
        meta_description = signals.meta_description if signals else ""
        canonical = signals.canonical if signals else ""
        if title == "":
            findings.append(_page_finding(url, "warning", "Missing title", "Add a clear, human-readable title tag."))
        elif len(title) < 35:
            findings.append(_page_finding(url, "info", "Short title", "Expand the title to better describe the page intent and brand context."))
        elif len(title) > 65:
            findings.append(_page_finding(url, "info", "Long title", "Tighten the title so the strongest page terms appear earlier in search snippets."))

        if page_type == "about" and "about-us -" in title.lower():
            findings.append(
                _page_finding(
                    url,
                    "warning",
                    "Slug-style about title",
                    "Replace the slug-like title with a readable About page title that leads with brand and purpose.",
                )
            )

        if meta_description == "":
            findings.append(_page_finding(url, "warning", "Missing meta description", "Add a meta description inside Rank Math before any bridge-owned live output is considered."))
        elif len(meta_description) < 80:
            findings.append(_page_finding(url, "warning", "Short meta description", "Expand the meta description to roughly 120-155 characters with a clearer value proposition."))
        elif len(meta_description) > 160:
            findings.append(_page_finding(url, "info", "Long meta description", "Shorten the meta description to reduce search snippet truncation risk."))

        if not canonical:
            findings.append(_page_finding(url, "warning", "Missing canonical", "Add or validate a canonical URL in Rank Math or theme output."))
        elif canonical.rstrip("/") != url.rstrip("/"):
            findings.append(_page_finding(url, "info", "Canonical differs from requested URL", "Verify that the canonical target is intentionally different and still exact-domain-bound."))

        h1_count = signals.h1_count if signals else 0
        if h1_count == 0:
            findings.append(_page_finding(url, "warning", "Missing H1", "Add one primary H1 heading for the page."))
        elif h1_count > 1:
            findings.append(_page_finding(url, "warning", "Multiple H1 headings", "Reduce the page to one primary H1 and demote decorative or repeated headings."))

        if not (signals.html_lang if signals else ""):
            findings.append(_page_finding(url, "info", "Missing html lang", "Expose the page language consistently in the root HTML tag."))
        if not (signals.has_viewport if signals else False):
            findings.append(_page_finding(url, "warning", "Missing viewport", "Add a viewport meta tag for mobile rendering stability."))

        robots = (signals.robots if signals else "").lower()
        if "noindex" in robots:
            findings.append(_page_finding(url, "warning", "Noindex robots directive", "Confirm whether this page should remain excluded from search."))

        if result.elapsed_ms >= app_config.warning_response_ms:
            findings.append(
                _page_finding(
                    url,
                    "warning" if result.elapsed_ms < app_config.critical_response_ms else "high",
                    "Slow response time",
                    "Review caching, theme payload and plugin overhead before expanding optimization scope.",
                )
            )

    recommendations = [finding.recommendation for finding in findings]
    return {
        "label": label,
        "page_type": page_type,
        "url": url,
        "status_code": result.status_code,
        "response_ms": round(result.elapsed_ms, 2),
        "title": signals.title if signals else "",
        "title_length": len(signals.title) if signals else 0,
        "meta_description": signals.meta_description if signals else "",
        "meta_description_length": len(signals.meta_description) if signals else 0,
        "canonical": signals.canonical if signals else "",
        "robots": signals.robots if signals else "",
        "h1_count": signals.h1_count if signals else 0,
        "html_lang": signals.html_lang if signals else "",
        "viewport_present": signals.has_viewport if signals else False,
        "fetch_error": result.error,
        "findings": [asdict(finding) for finding in findings],
        "recommendations": recommendations,
    }


def _build_global_recommendations(page_reports: list[dict[str, Any]], runtime: dict[str, Any]) -> list[str]:
    recommendations = [
        "Keep Rank Math as the live SEO owner while using the bridge for bounded diagnostics and recommendations.",
        "Apply title, meta-description and heading improvements inside Rank Math or theme settings before considering any bridge-owned live output.",
        "Prioritize homepage snippet quality and H1 cleanup first, then normalize About, Impressum and Privacy titles/headings.",
    ]
    if runtime.get("optimization_gate") == "recommend_only":
        recommendations.append("Stay in recommend_only until signature, delivery grant and protected release gates are explicitly approved.")
    return recommendations


def _build_automation_candidates(
    page_reports: list[dict[str, Any]],
    runtime: dict[str, Any],
    bound_domain: str,
    automation_contracts: dict[str, Any],
    automation_contract_issues: list[str],
) -> list[dict[str, Any]]:
    if automation_contract_issues:
        return []
    if str(runtime.get("optimization_gate", "")) != "recommend_only":
        return []
    if str(runtime.get("coexistence_mode", "")) != "rank_math_controlled_coexistence":
        return []

    candidates: list[dict[str, Any]] = []
    for page in page_reports:
        finding_titles = {str(item.get("title", "")) for item in page.get("findings", [])}
        if not {"Short meta description", "Missing meta description"} & finding_titles:
            continue

        proposed_value = _proposed_meta_description(page)
        if proposed_value == "":
            continue

        url = str(page.get("url", ""))
        target_domain = urlparse(url).hostname or ""
        label = str(page.get("label", url or "Page"))
        page_type = str(page.get("page_type", "generic"))
        is_homepage = page_type == "homepage"
        action_type = (
            "rank_math_homepage_meta_description_update"
            if is_homepage
            else "rank_math_meta_description_update"
        )
        contract = get_automation_contract(automation_contracts, action_type)
        target_field = (
            "rank_math_titles.homepage_description"
            if is_homepage
            else "rank_math_description"
        )
        candidate = {
            "candidate_id": stable_fingerprint(url, action_type, proposed_value),
            "label": (
                f"{label}: Rank Math homepage meta description update"
                if is_homepage
                else f"{label}: Rank Math meta description update"
            ),
            "page_label": label,
            "page_type": page_type,
            "action_type": action_type,
            "execution_lane": "admin_confirmed_assisted_resolution_only",
            "runtime_gate": str(runtime.get("optimization_gate", "")),
            "active_seo_owner": str(runtime.get("active_seo_plugin", "")),
            "bound_domain": bound_domain,
            "target_domain": target_domain,
            "target_url": url,
            "target_field": target_field,
            "approval_state": "admin_confirmation_required",
            "rollback_state": "ready_if_before_state_captured",
            "proposal_reason": (
                "The active SEO owner remains Rank Math, so the suite can safely assist by writing into the Rank Math homepage option only after explicit admin approval."
                if is_homepage
                else "The active SEO owner remains Rank Math, so the suite can safely assist by writing into the existing owner only after explicit admin approval."
            ),
            "proposed_value": proposed_value,
            "proposed_length": len(proposed_value),
        }
        if candidate_contract_issues(candidate, contract):
            continue
        candidates.append(attach_contract(candidate, contract))
    return candidates


def _build_priority_execution_queue(page_reports: list[dict[str, Any]]) -> list[dict[str, Any]]:
    queue: list[dict[str, Any]] = []
    for page in page_reports:
        findings = page.get("findings", [])
        if not findings:
            continue

        warning_count = sum(1 for finding in findings if finding.get("severity") == "warning")
        high_count = sum(1 for finding in findings if finding.get("severity") == "high")
        info_count = sum(1 for finding in findings if finding.get("severity") == "info")
        page_type = str(page.get("page_type", "generic"))
        base_score = (high_count * 100) + (warning_count * 20) + (info_count * 5)
        if page_type == "homepage":
            base_score += 15
        elif page_type == "about":
            base_score += 10

        queue.append(
            {
                "label": str(page.get("label", page.get("url", "Page"))),
                "url": str(page.get("url", "")),
                "page_type": page_type,
                "priority": _priority_label(base_score),
                "priority_score": base_score,
                "focus": _derive_page_focus(page),
                "why_now": _derive_page_why_now(page_type),
                "finding_count": len(findings),
                "top_actions": _dedupe_preserve_order(page.get("recommendations", []))[:3],
            }
        )

    return sorted(
        queue,
        key=lambda item: (-int(item.get("priority_score", 0)), -_page_type_weight(str(item.get("page_type", ""))), str(item.get("label", ""))),
    )


def _build_innovation_control_deck(
    page_reports: list[dict[str, Any]],
    runtime: dict[str, Any],
    global_recommendations: list[str],
    priority_execution_queue: list[dict[str, Any]],
) -> dict[str, Any]:
    gate = str(runtime.get("optimization_gate", "recommend_only"))
    coexistence_mode = str(runtime.get("coexistence_mode", ""))
    active_owner = str(runtime.get("active_seo_plugin", "the active SEO plugin"))
    priority_focus = str(priority_execution_queue[0]["focus"]) if priority_execution_queue else "bounded_visibility_review"

    execution_mode = "bounded_observation"
    operator_brief = "Keep the bridge explainable and bounded while the next green gate is established."
    if gate == "blocked":
        execution_mode = "stabilize_and_close_gates"
        operator_brief = "Close runtime blockers before widening the optimization surface."
    elif gate == "reversible_change_ready":
        execution_mode = "reversible_stage_1_validation"
        operator_brief = "Validate only the reversible homepage meta-preparation path and keep rollback hot."
    elif coexistence_mode != "" and coexistence_mode != "no_external_seo_owner":
        execution_mode = "controlled_growth_under_external_seo_owner"
        operator_brief = f"Use the bridge as the decision layer while {active_owner} keeps live SEO output ownership."

    immediate_actions: list[str] = []
    for item in priority_execution_queue[:2]:
        top_actions = item.get("top_actions", [])
        if top_actions:
            immediate_actions.append(f"{item.get('label', 'Page')}: {top_actions[0]}")
    if gate == "recommend_only":
        immediate_actions.append("Implement approved title, meta-description and heading changes inside Rank Math or theme settings, not via bridge-owned live output.")

    next_actions = _dedupe_preserve_order(
        [action for item in priority_execution_queue[2:] for action in item.get("top_actions", [])] + global_recommendations
    )[:4]

    success_signals = _derive_success_signals(page_reports, gate)
    protected_holds = _dedupe_preserve_order(
        [
            "Do not deactivate the active SEO plugin as part of this pass." if coexistence_mode != "no_external_seo_owner" else "",
            "Do not introduce global head rewrites, canonical overrides or sitewide meta overwrites from the bridge.",
            "Do not leave recommend_only or enter active live delivery without signature, approval and rollback gates.",
            "Keep all changes reversible and buyer-readable while protected delivery remains approval-gated.",
        ]
    )

    return {
        "execution_mode": execution_mode,
        "priority_focus": priority_focus,
        "operator_brief": operator_brief,
        "immediate_actions": immediate_actions,
        "next_actions": next_actions,
        "success_signals": success_signals,
        "protected_holds": protected_holds,
    }


def _derive_success_signals(page_reports: list[dict[str, Any]], gate: str) -> list[str]:
    titles = {finding.get("title", "") for page in page_reports for finding in page.get("findings", [])}
    signals: list[str] = []
    if "Short meta description" in titles:
        signals.append("Priority pages expose fuller meta descriptions in the 120-155 character range.")
    if "Multiple H1 headings" in titles:
        signals.append("Each reviewed page renders exactly one primary H1 heading.")
    if "Slug-style about title" in titles:
        signals.append("The About page title becomes brand-led and readable instead of slug-shaped.")
    signals.append(f"The optimization gate stays `{gate}` or better with zero new blockers.")
    return _dedupe_preserve_order(signals)


def _derive_page_focus(page: dict[str, Any]) -> str:
    titles = {str(item.get("title", "")) for item in page.get("findings", [])}
    page_type = str(page.get("page_type", "generic"))
    if page_type == "homepage" and {"Short meta description", "Multiple H1 headings"} & titles:
        return "homepage_snippet_and_heading_clarity"
    if "Slug-style about title" in titles:
        return "brand_narrative_and_heading_clarity"
    if "Short meta description" in titles:
        return "snippet_quality"
    if "Multiple H1 headings" in titles:
        return "heading_clarity"
    if "Missing canonical" in titles or "Canonical differs from requested URL" in titles:
        return "canonical_consistency"
    return "page_quality_hardening"


def _derive_page_why_now(page_type: str) -> str:
    if page_type == "homepage":
        return "Homepage is the highest-leverage public entry point for search snippets and first impressions."
    if page_type == "about":
        return "About content shapes brand trust, narrative clarity and entity understanding."
    if page_type == "legal":
        return "Legal pages should stay structurally clean and search-readable without weakening compliance messaging."
    return "This page has bounded, reversible improvements ready inside the current recommend_only lane."


def _priority_label(score: int) -> str:
    if score >= 40:
        return "high"
    if score >= 20:
        return "medium"
    return "low"


def _page_type_weight(page_type: str) -> int:
    if page_type == "homepage":
        return 3
    if page_type == "about":
        return 2
    if page_type == "legal":
        return 1
    return 0


def _dedupe_preserve_order(items: list[Any]) -> list[str]:
    normalized: list[str] = []
    for item in items:
        value = str(item).strip()
        if value != "" and value not in normalized:
            normalized.append(value)
    return normalized


def _proposed_meta_description(page: dict[str, Any]) -> str:
    page_type = str(page.get("page_type", "generic"))
    label = str(page.get("label", "Page"))
    if page_type == "homepage":
        return "Electri_C_ity Studios streams electro music 24/7 and presents crypto art, radio culture and digital releases on one bold creative platform."
    if page_type == "legal" and label.lower() == "privacy policy":
        return "Read the Privacy Policy from Electri_C_ity Studios to understand data handling, cookies, contact requests and your rights on this website."
    if page_type == "legal":
        return f"Read the {label} from Electri_C_ity Studios for clear, exact-domain-bound legal and contact information on this website."
    return f"Explore {label} from Electri_C_ity Studios with clearer search visibility, stronger page intent and buyer-readable structure."


def _page_finding(target: str, severity: str, title: str, recommendation: str) -> Finding:
    return Finding(
        category="private_site_report",
        severity=severity,
        title=title,
        detail=title,
        risk="low",
        confidence=0.85,
        source="private_site_report",
        target=target,
        recommendation=recommendation,
        fingerprint=stable_fingerprint(target, title, recommendation),
    )


def _load_env_refs_from_file(delivery: dict[str, Any], workspace_root: str | Path | None) -> dict[str, str]:
    env_load_point = str(delivery.get("env_load_point", "")).strip()
    if not env_load_point or workspace_root is None:
        return {}

    guard = WorkspaceGuard(Path(workspace_root).resolve())
    env_path = guard.resolve_inside(env_load_point)
    if not env_path.exists():
        return {}

    values: dict[str, str] = {}
    for line in env_path.read_text(encoding="utf-8").splitlines():
        raw = line.strip()
        if raw == "" or raw.startswith("#") or "=" not in raw:
            continue
        key, value = raw.split("=", 1)
        values[key.strip()] = value.strip()
    return values
