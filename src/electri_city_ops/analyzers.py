from __future__ import annotations

from electri_city_ops.config import AppConfig
from electri_city_ops.http_probe import HttpProbe, extract_page_signals
from electri_city_ops.models import Finding, Metric, TargetSnapshot


def run_audit_analysis(config: AppConfig, config_notes: list[str]) -> tuple[list[Finding], list[Metric]]:
    findings: list[Finding] = []
    metrics = [
        Metric(name="configured_domains", value=float(len(config.domains)), unit="count", source="audit"),
        Metric(name="remote_fetch_enabled", value=float(int(config.allow_remote_fetch)), source="audit"),
        Metric(name="external_changes_enabled", value=float(int(config.allow_external_changes)), source="audit"),
        Metric(name="email_enabled", value=float(int(config.email.enabled)), source="audit"),
        Metric(
            name="cycle_interval_minutes",
            value=float(config.cycle_interval_minutes),
            unit="minutes",
            source="audit",
        ),
    ]

    if not config.domains:
        findings.append(
            Finding(
                category="config",
                severity="warning",
                title="No target domains configured",
                detail="The system cannot inspect SEO or performance signals without at least one approved target domain.",
                risk="low",
                confidence=1.0,
                source="audit",
                target="system",
                recommendation="Provide the approved target domain list before enabling remote analysis.",
            )
        )
    if config.domains and not config.allow_remote_fetch:
        findings.append(
            Finding(
                category="permissions",
                severity="warning",
                title="Remote fetch is disabled",
                detail="Target domains are present, but remote read access is disabled by configuration.",
                risk="low",
                confidence=1.0,
                source="audit",
                target="system",
                recommendation="Enable allow_remote_fetch only after confirming that read-only target probing is allowed.",
            )
        )
    if config.email.enabled and not config.email.is_complete():
        findings.append(
            Finding(
                category="notifications",
                severity="warning",
                title="Email notifications are incomplete",
                detail="SMTP delivery is enabled, but sender, recipients, or authentication details are missing.",
                risk="low",
                confidence=1.0,
                source="audit",
                target="system",
                recommendation="Complete SMTP settings or disable email until credentials are approved.",
            )
        )
    for note in config_notes:
        findings.append(
            Finding(
                category="config",
                severity="info",
                title="Configuration note",
                detail=note,
                risk="low",
                confidence=1.0,
                source="audit",
                target="system",
                recommendation="Review configuration notes before enabling broader automation.",
            )
        )
    return findings, metrics


def collect_target_snapshots(
    config: AppConfig,
    probe: HttpProbe | None,
) -> tuple[list[TargetSnapshot], list[Finding], list[Metric]]:
    if not config.domains or not config.allow_remote_fetch or probe is None:
        return [], [], []

    snapshots: list[TargetSnapshot] = []
    findings: list[Finding] = []
    metrics: list[Metric] = []

    for domain in config.domains:
        homepage = probe.homepage(domain)
        sitemap = probe.sitemap(domain)
        signals = extract_page_signals(homepage.body) if homepage.ok else None

        snapshot = TargetSnapshot(
            domain=domain,
            final_url=homepage.final_url,
            homepage_status_code=homepage.status_code,
            response_ms=round(homepage.elapsed_ms, 2),
            html_bytes=homepage.body_bytes,
            content_encoding=homepage.headers.get("Content-Encoding", ""),
            cache_control=homepage.headers.get("Cache-Control", ""),
            title=signals.title if signals else "",
            meta_description=signals.meta_description if signals else "",
            canonical=signals.canonical if signals else "",
            h1_count=signals.h1_count if signals else 0,
            html_lang=signals.html_lang if signals else "",
            viewport_present=signals.has_viewport if signals else False,
            robots_meta=signals.robots if signals else "",
            sitemap_status_code=sitemap.status_code,
            fetch_error=homepage.error,
        )
        snapshots.append(snapshot)

        metrics.extend(
            [
                Metric(
                    name="homepage_status_code",
                    value=float(snapshot.homepage_status_code),
                    unit="status",
                    scope=domain,
                    source="target",
                ),
                Metric(
                    name="response_ms",
                    value=float(snapshot.response_ms),
                    unit="ms",
                    scope=domain,
                    source="target",
                ),
                Metric(
                    name="html_bytes",
                    value=float(snapshot.html_bytes),
                    unit="bytes",
                    scope=domain,
                    source="target",
                ),
                Metric(
                    name="sitemap_status_code",
                    value=float(snapshot.sitemap_status_code),
                    unit="status",
                    scope=domain,
                    source="target",
                ),
                Metric(
                    name="title_length",
                    value=float(len(snapshot.title)),
                    unit="chars",
                    scope=domain,
                    source="target",
                ),
                Metric(
                    name="meta_description_length",
                    value=float(len(snapshot.meta_description)),
                    unit="chars",
                    scope=domain,
                    source="target",
                ),
                Metric(
                    name="h1_count",
                    value=float(snapshot.h1_count),
                    unit="count",
                    scope=domain,
                    source="target",
                ),
                Metric(
                    name="has_canonical",
                    value=float(int(bool(snapshot.canonical))),
                    unit="bool",
                    scope=domain,
                    source="target",
                ),
                Metric(
                    name="has_html_lang",
                    value=float(int(bool(snapshot.html_lang))),
                    unit="bool",
                    scope=domain,
                    source="target",
                ),
                Metric(
                    name="viewport_present",
                    value=float(int(snapshot.viewport_present)),
                    unit="bool",
                    scope=domain,
                    source="target",
                ),
                Metric(
                    name="compressed_response",
                    value=float(int(bool(snapshot.content_encoding))),
                    unit="bool",
                    scope=domain,
                    source="target",
                ),
                Metric(
                    name="has_cache_control",
                    value=float(int(bool(snapshot.cache_control))),
                    unit="bool",
                    scope=domain,
                    source="target",
                ),
            ]
        )

        metrics.append(
            Metric(name="sitemap_available", value=float(int(sitemap.ok)), unit="bool", scope=domain, source="target")
        )

        if not homepage.ok:
            findings.append(
                Finding(
                    category="seo_fetch",
                    severity="high",
                    title="Homepage fetch failed",
                    detail=f"{domain} could not be fetched safely: {homepage.error or homepage.status_code}.",
                    risk="medium",
                    confidence=0.95,
                    source="seo",
                    target=domain,
                    recommendation="Verify network reachability, DNS, TLS, robots and access policy for the target domain.",
                )
            )
        if not sitemap.ok:
            findings.append(
                Finding(
                    category="seo_discovery",
                    severity="info",
                    title="Sitemap was not confirmed",
                    detail=f"{domain} sitemap.xml did not respond with a successful status during this safe probe.",
                    risk="low",
                    confidence=0.75,
                    source="seo",
                    target=domain,
                    recommendation="Verify sitemap availability or provide the canonical sitemap location for monitoring.",
                )
            )

    return snapshots, findings, metrics


def run_seo_analysis(target_results: list[TargetSnapshot]) -> tuple[list[Finding], list[Metric]]:
    findings: list[Finding] = []

    for snapshot in target_results:
        if snapshot.fetch_error:
            continue
        if not snapshot.title:
            findings.append(
                Finding(
                    category="seo_structure",
                    severity="high",
                    title="Missing page title",
                    detail=f"{snapshot.domain} returned HTML without a <title> element.",
                    risk="medium",
                    confidence=0.95,
                    source="seo",
                    target=snapshot.domain,
                    recommendation="Add a descriptive title tag for the homepage and validate it in the next crawl.",
                )
            )
        if not snapshot.meta_description:
            findings.append(
                Finding(
                    category="seo_structure",
                    severity="warning",
                    title="Missing meta description",
                    detail=f"{snapshot.domain} returned HTML without a meta description.",
                    risk="low",
                    confidence=0.9,
                    source="seo",
                    target=snapshot.domain,
                    recommendation="Add a homepage meta description to improve snippet quality and reporting completeness.",
                )
            )
        if not snapshot.canonical:
            findings.append(
                Finding(
                    category="seo_structure",
                    severity="warning",
                    title="Missing canonical link",
                    detail=f"{snapshot.domain} did not expose a canonical link on the homepage.",
                    risk="low",
                    confidence=0.9,
                    source="seo",
                    target=snapshot.domain,
                    recommendation="Add a canonical URL to reduce ambiguity for crawlers.",
                )
            )
        if snapshot.h1_count == 0:
            findings.append(
                Finding(
                    category="seo_structure",
                    severity="warning",
                    title="No H1 heading detected",
                    detail=f"{snapshot.domain} homepage HTML contains no H1 heading.",
                    risk="low",
                    confidence=0.8,
                    source="seo",
                    target=snapshot.domain,
                    recommendation="Add a single descriptive H1 heading to the homepage template.",
                )
            )
        if not snapshot.html_lang:
            findings.append(
                Finding(
                    category="seo_structure",
                    severity="info",
                    title="Missing HTML lang attribute",
                    detail=f"{snapshot.domain} homepage HTML does not expose a lang attribute.",
                    risk="low",
                    confidence=0.85,
                    source="seo",
                    target=snapshot.domain,
                    recommendation="Set the HTML lang attribute to improve accessibility and search interpretation.",
                )
            )

    return findings, []


def run_performance_analysis(config: AppConfig, target_results: list[TargetSnapshot]) -> tuple[list[Finding], list[Metric]]:
    if not target_results:
        return [], []

    findings: list[Finding] = []

    for snapshot in target_results:
        if snapshot.fetch_error:
            continue

        if snapshot.response_ms >= config.critical_response_ms:
            findings.append(
                Finding(
                    category="performance",
                    severity="critical",
                    title="Critical response time",
                    detail=(
                        f"{snapshot.domain} homepage responded in "
                        f"{snapshot.response_ms:.0f} ms, above the critical threshold."
                    ),
                    risk="medium",
                    confidence=0.95,
                    source="performance",
                    target=snapshot.domain,
                    recommendation="Investigate backend response time, caching, database pressure and expensive theme/plugin work.",
                )
            )
        elif snapshot.response_ms >= config.warning_response_ms:
            findings.append(
                Finding(
                    category="performance",
                    severity="warning",
                    title="Slow response time",
                    detail=(
                        f"{snapshot.domain} homepage responded in "
                        f"{snapshot.response_ms:.0f} ms, above the warning threshold."
                    ),
                    risk="low",
                    confidence=0.9,
                    source="performance",
                    target=snapshot.domain,
                    recommendation="Review caching, asset loading and server-side work on the homepage request path.",
                )
            )

        if snapshot.html_bytes >= config.large_html_bytes:
            findings.append(
                Finding(
                    category="performance",
                    severity="warning",
                    title="Large homepage HTML payload",
                    detail=f"{snapshot.domain} homepage HTML payload is {snapshot.html_bytes} bytes.",
                    risk="low",
                    confidence=0.85,
                    source="performance",
                    target=snapshot.domain,
                    recommendation="Reduce inline markup and serialized state to shrink the HTML response size.",
                )
            )
        if snapshot.html_bytes >= config.large_html_bytes and not snapshot.content_encoding:
            findings.append(
                Finding(
                    category="performance",
                    severity="warning",
                    title="Large HTML without compression",
                    detail=f"{snapshot.domain} serves a large homepage payload without Content-Encoding.",
                    risk="low",
                    confidence=0.9,
                    source="performance",
                    target=snapshot.domain,
                    recommendation="Enable safe HTTP compression for HTML responses after validating compatibility.",
                )
            )

    return findings, []


def run_error_analysis(
    config: AppConfig,
    target_results: list[TargetSnapshot],
    target_findings: list[Finding],
) -> tuple[list[Finding], list[Metric]]:
    findings: list[Finding] = []
    metrics: list[Metric] = []
    active_findings = target_findings

    if config.domains and not config.allow_remote_fetch:
        findings.append(
            Finding(
                category="coverage",
                severity="info",
                title="Target analysis is blocked by permissions",
                detail="Target domains exist, but read-only remote probing is disabled. The cycle remains intentionally partial.",
                risk="low",
                confidence=1.0,
                source="errors",
                target="system",
                recommendation="Approve remote read access if domain-level observation is required.",
            )
        )

    metrics.append(Metric(name="active_findings", value=float(len(active_findings)), unit="count", source="errors"))
    metrics.append(
        Metric(
            name="observed_target_results",
            value=float(len(target_results)),
            unit="count",
            source="errors",
        )
    )
    if len(active_findings) >= 5:
        findings.append(
            Finding(
                category="stability",
                severity="warning",
                title="Elevated issue volume",
                detail=f"The current cycle produced {len(active_findings)} target-related findings.",
                risk="low",
                confidence=0.8,
                source="errors",
                target="system",
                recommendation="Prioritize the highest-scoring findings and confirm whether alerting should escalate this volume.",
            )
        )
    if target_results and all(snapshot.fetch_error for snapshot in target_results):
        findings.append(
            Finding(
                category="coverage",
                severity="warning",
                title="All target probes failed",
                detail="All configured target probes failed during this read-only cycle, so domain results are incomplete.",
                risk="low",
                confidence=0.9,
                source="errors",
                target="system",
                recommendation="Verify DNS, TLS, network reachability and target-side protections before trusting trend outputs.",
            )
        )
    return findings, metrics
