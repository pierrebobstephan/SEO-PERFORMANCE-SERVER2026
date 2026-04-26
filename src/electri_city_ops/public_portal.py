from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import html
import json
import os
from pathlib import Path
import textwrap
from typing import Any
from urllib.parse import parse_qs, urlencode, urlsplit
from urllib.request import Request, urlopen

from electri_city_ops.config import AppConfig, load_config
from electri_city_ops.workspace import WorkspaceGuard


ALLOWED_BIND_HOSTS = {"127.0.0.1", "localhost"}
OPERATOR_INPUT_REQUIRED = "operator input required"
SOURCE_NOT_YET_CONFIRMED = "source not yet confirmed"
APPROVAL_REQUIRED = "approval_required"
GOOGLE_CLOUD_TRANSLATION_BASIC_V2 = "google_cloud_translation_basic_v2"
GOOGLE_TRANSLATE_BASIC_V2_ENDPOINT = "https://translation.googleapis.com/language/translate/v2"
DEFAULT_TRANSLATION_LANGUAGES = ("en", "de", "fr", "es", "it", "pt", "nl")
GOOGLE_TRANSLATE_MAX_TEXTS_PER_REQUEST = 24
GOOGLE_TRANSLATE_MAX_CHARS_PER_REQUEST = 2400
LANGUAGE_LABELS = {
    "en": "English",
    "de": "Deutsch",
    "fr": "Francais",
    "es": "Espanol",
    "it": "Italiano",
    "pt": "Portugues",
    "nl": "Nederlands",
}
PUBLIC_NAV = (
    ("/", "Home"),
    ("/explore", "Explore"),
    ("/features", "Features"),
    ("/plugin", "Plugin"),
    ("/security", "Security"),
    ("/licensing", "Licensing"),
    ("/buy", "Buy"),
    ("/downloads", "Downloads"),
    ("/support", "Support"),
    ("/docs", "Docs"),
)
NAV_LABELS = {
    **{route: label for route, label in PUBLIC_NAV},
    "/agencies": "Agencies",
    "/publishers": "Publishers",
}
LEGAL_ROUTE_ALIASES = {"/impressum": "/legal"}

PUBLIC_MONTHLY_PLANS: tuple[dict[str, str], ...] = (
    {
        "badge": "Focused single-domain tier",
        "title": "Guardian Core Monthly",
        "price_line": "EUR 2,500.00 / month",
        "scope_line": "Monthly optimization scope for one exact licensed domain.",
        "included_line": "Controlled SEO and performance optimization with validation and rollback.",
        "copy": (
            "Guardian Core Monthly is the clear entry point for one exact licensed domain. It is built for controlled SEO "
            "and performance optimization with validation, rollback discipline and no black-box activation."
        ),
        "scope_summary": "Guardian Core Monthly: one exact licensed domain",
    },
    {
        "badge": "Scaled multi-domain tier",
        "title": "Sovereign Enterprise Monthly",
        "price_line": "EUR 9,500.00 / month",
        "scope_line": "Monthly multi-domain optimization for an exact licensed domain set confirmed during commercial review.",
        "included_line": "Audit, validation and controlled activation for larger environments.",
        "copy": (
            "Sovereign Enterprise Monthly is designed for larger WordPress environments that need multi-domain optimization, "
            "auditability, validation evidence and controlled activation without dropping exact domain scoping."
        ),
        "scope_summary": "Sovereign Enterprise Monthly: commercially reviewed exact licensed multi-domain scope",
    },
    {
        "badge": "High-compliance tier",
        "title": "Sovereign Critical Monthly",
        "price_line": "EUR 25,000.00 / month",
        "scope_line": "Monthly high-compliance scope for an individually approved exact licensed domain set.",
        "included_line": "Individual approval, strict validation and controlled activation.",
        "copy": (
            "Sovereign Critical Monthly is the high-compliance model for business-critical or especially sensitive environments "
            "that require individual approval, strict validation and tightly controlled activation."
        ),
        "scope_summary": "Sovereign Critical Monthly: individually approved exact licensed high-compliance scope",
    },
)


@dataclass(slots=True)
class PublicPortalTranslationConfig:
    enabled: bool
    provider: str
    default_language: str
    supported_languages: tuple[str, ...]
    api_key_env: str
    env_load_point: str
    activation_state: str


@dataclass(slots=True)
class PublicPortalConfig:
    bind_host: str
    port: int
    selected_subdomain: str
    alternative_subdomains: tuple[str, ...]
    canonical_base_url: str
    product_name: str
    support_contact: str
    download_gate_state: str
    public_routes: tuple[str, ...]
    protected_route_prefixes: tuple[str, ...]
    translation: PublicPortalTranslationConfig
    operator_fields: "PublicPortalOperatorConfig"
    legal_fields: dict[str, Any]
    notes: tuple[str, ...] = ()


@dataclass(slots=True)
class PortalResponse:
    status: int
    content_type: str
    body: bytes


@dataclass(slots=True)
class PublicPortalOperatorConfig:
    support_contact: str
    support_email: str
    commercial_inquiry_label: str
    commercial_inquiry_state: str
    pricing_model_state: str
    package_tiers_state: str
    access_request_state: str
    support_readiness_state: str
    commercial_readiness_state: str
    legal_readiness_state: str
    download_readiness_state: str


def public_portal_config_path(workspace_root: Path) -> Path:
    return workspace_root.resolve() / "config" / "public-portal.json"


def public_portal_operator_config_path(workspace_root: Path) -> Path:
    return workspace_root.resolve() / "config" / "public-portal-operator.json"


def public_portal_legal_config_path(workspace_root: Path) -> Path:
    return workspace_root.resolve() / "config" / "public-portal-legal.json"


def _normalized_operator_value(payload: dict[str, Any], key: str, default: str) -> str:
    raw = payload.get(key, default)
    value = str(raw).strip() if raw is not None else ""
    return value or default


def _normalize_language_code(raw: Any, default: str = "en") -> str:
    value = str(raw or "").strip().lower()
    normalized = "".join(character for character in value if character.isalnum() or character == "-")
    return normalized or default


def _load_env_refs_from_file(workspace_root: Path, env_load_point: str) -> dict[str, str]:
    if env_load_point.strip() == "":
        return {}
    guard = WorkspaceGuard(workspace_root.resolve())
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


def _public_plan_titles_inline() -> str:
    return ", ".join(plan["title"] for plan in PUBLIC_MONTHLY_PLANS[:-1]) + f" and {PUBLIC_MONTHLY_PLANS[-1]['title']}"


def _public_plan_scope_bullets() -> list[str]:
    return [plan["scope_summary"] for plan in PUBLIC_MONTHLY_PLANS]


def _public_plan_pricing_cards() -> list[dict[str, Any]]:
    links = (
        (
            {"href": "/licensing", "label": "Review single-domain fit"},
            {"href": "/terms", "label": "Open terms and license scope"},
        ),
        (
            {"href": "/licensing", "label": "Review multi-domain fit"},
            {"href": "/support", "label": "Clarify enterprise scope"},
        ),
        (
            {"href": "/support", "label": "Request high-compliance review"},
            {"href": "/terms", "label": "Open terms and license scope"},
        ),
    )
    return [{**plan, "links": list(link_pair)} for plan, link_pair in zip(PUBLIC_MONTHLY_PLANS, links, strict=False)]


def _public_plan_terms_sections() -> list[dict[str, Any]]:
    return [{"heading": plan["title"], "paragraphs": [plan["price_line"], plan["scope_line"], plan["included_line"], plan["copy"]]} for plan in PUBLIC_MONTHLY_PLANS]


def _load_public_portal_translation_config(payload: dict[str, Any]) -> PublicPortalTranslationConfig:
    raw = payload.get("translation", {})
    if not isinstance(raw, dict):
        raw = {}
    default_language = _normalize_language_code(raw.get("default_language", "en"))
    supported_languages = tuple(
        dict.fromkeys(
            _normalize_language_code(item, default_language)
            for item in raw.get("supported_languages", DEFAULT_TRANSLATION_LANGUAGES)
            if str(item).strip()
        )
    )
    if default_language not in supported_languages:
        supported_languages = (default_language, *supported_languages)
    return PublicPortalTranslationConfig(
        enabled=bool(raw.get("enabled", True)),
        provider=str(raw.get("provider", GOOGLE_CLOUD_TRANSLATION_BASIC_V2)).strip()
        or GOOGLE_CLOUD_TRANSLATION_BASIC_V2,
        default_language=default_language,
        supported_languages=supported_languages or (default_language,),
        api_key_env=str(raw.get("api_key_env", "GOOGLE_TRANSLATE_API_KEY")).strip() or "GOOGLE_TRANSLATE_API_KEY",
        env_load_point=str(raw.get("env_load_point", "deploy/systemd/public-portal.env")).strip()
        or "deploy/systemd/public-portal.env",
        activation_state=str(raw.get("activation_state", OPERATOR_INPUT_REQUIRED)).strip() or OPERATOR_INPUT_REQUIRED,
    )


def load_public_portal_operator_config(workspace_root: Path) -> PublicPortalOperatorConfig:
    path = public_portal_operator_config_path(workspace_root)
    if path.exists():
        payload = json.loads(path.read_text(encoding="utf-8"))
    else:
        payload = {}
    return PublicPortalOperatorConfig(
        support_contact=_normalized_operator_value(payload, "support_contact", OPERATOR_INPUT_REQUIRED),
        support_email=_normalized_operator_value(payload, "support_email", OPERATOR_INPUT_REQUIRED),
        commercial_inquiry_label=_normalized_operator_value(
            payload, "commercial_inquiry_label", "Commercial inquiry path"
        ),
        commercial_inquiry_state=_normalized_operator_value(
            payload, "commercial_inquiry_state", OPERATOR_INPUT_REQUIRED
        ),
        pricing_model_state=_normalized_operator_value(payload, "pricing_model_state", OPERATOR_INPUT_REQUIRED),
        package_tiers_state=_normalized_operator_value(
            payload, "package_tiers_state", SOURCE_NOT_YET_CONFIRMED
        ),
        access_request_state=_normalized_operator_value(
            payload, "access_request_state", APPROVAL_REQUIRED
        ),
        support_readiness_state=_normalized_operator_value(
            payload, "support_readiness_state", OPERATOR_INPUT_REQUIRED
        ),
        commercial_readiness_state=_normalized_operator_value(
            payload, "commercial_readiness_state", OPERATOR_INPUT_REQUIRED
        ),
        legal_readiness_state=_normalized_operator_value(payload, "legal_readiness_state", "configured"),
        download_readiness_state=_normalized_operator_value(
            payload, "download_readiness_state", APPROVAL_REQUIRED
        ),
    )


def _default_public_portal_legal_payload() -> dict[str, Any]:
    pages = {
        "identity": {
            "operator_name": "Pierre (Bob) Stephan",
            "trading_as": "trading as Electri_C_ity - Studios",
            "street": "Altensteiner Strasse 131",
            "postal_city": "36448 Bad Liebenstein",
            "country": "Germany",
            "support_email": "pierre.stephan1@electri-c-ity-studios.com",
            "vat_id": "DE363614431",
            "invoices_note": "Invoices are issued for completed orders.",
            "response_time": "1-3 business days (Europe/Berlin)",
        },
        "footer_nav": [
            {"href": "/legal", "label": "Impressum / Legal Notice"},
            {"href": "/privacy", "label": "Privacy Policy"},
            {"href": "/terms", "label": "Terms / License Terms"},
            {"href": "/refund", "label": "Refund Policy"},
            {"href": "/contact", "label": "Contact / Support"},
        ],
        "pages": {
            "legal": {
                "route": "/legal",
                "title": "Impressum / Legal Notice",
                "description": "Legal operator and contact details for Site Optimizer Core.",
                "hero": "Impressum / Legal Notice",
                "lede": "Legal operator and contact details for Site Optimizer Core.",
                "sections": [
                    {
                        "heading": "Operator",
                        "paragraphs": [
                            "Pierre (Bob) Stephan",
                            "trading as Electri_C_ity - Studios",
                            "Altensteiner Strasse 131",
                            "36448 Bad Liebenstein",
                            "Germany",
                        ],
                    },
                    {
                        "heading": "Contact",
                        "paragraphs": [
                            "Email: pierre.stephan1@electri-c-ity-studios.com",
                            "VAT ID: DE363614431",
                            "Responsible for content: Pierre (Bob) Stephan",
                        ],
                    },
                    {
                        "heading": "Support",
                        "paragraphs": [
                            "Support for licensing, activation, download, billing, and technical issues is available via email.",
                            "Typical response time: 1-3 business days (Europe/Berlin).",
                        ],
                    },
                    {
                        "heading": "Invoicing",
                        "paragraphs": [
                            "Invoices are issued for completed orders. VAT details are available on request and in commercial correspondence where applicable."
                        ],
                    },
                ],
            },
            "privacy": {
                "route": "/privacy",
                "title": "Privacy Policy",
                "description": "This policy explains the main categories of personal data processed on the Site Optimizer Core public website, checkout flow, delivery path, and support path.",
                "hero": "Privacy Policy",
                "lede": "This policy explains the main categories of personal data processed on the Site Optimizer Core public website, checkout flow, delivery path, and support path.",
                "sections": [
                    {
                        "heading": "Controller",
                        "paragraphs": [
                            "Pierre (Bob) Stephan",
                            "trading as Electri_C_ity - Studios",
                            "Altensteiner Strasse 131",
                            "36448 Bad Liebenstein",
                            "Germany",
                            "Email: pierre.stephan1@electri-c-ity-studios.com",
                        ],
                    },
                    {
                        "heading": "Contact",
                        "paragraphs": [
                            "For privacy requests, support, licensing, billing, or technical questions, contact pierre.stephan1@electri-c-ity-studios.com."
                        ],
                    },
                    {
                        "heading": "Data we process",
                        "paragraphs": [
                            "Website access data: server and security logs created when the public website is visited.",
                            "Checkout data: email address, licensed domain, order references, and related checkout records.",
                            "Portal and delivery data: license key, licensed domain, access checks, and support information provided by the customer.",
                        ],
                    },
                    {
                        "heading": "Service partners and tools",
                        "paragraphs": [
                            "Payment processing: payment approval and order capture are handled through PayPal.",
                            "Analytics and measurement: public pages load Google tag / measurement scripts.",
                            "Email communication: delivery and support communication may include order and license identifiers.",
                        ],
                    },
                    {
                        "heading": "Why we process data",
                        "paragraphs": [
                            "Data is processed to operate the website, create and complete checkouts, validate licensed access, deliver the current release, respond to support requests, and maintain service security and reporting."
                        ],
                    },
                    {
                        "heading": "Your rights",
                        "paragraphs": [
                            "Depending on applicable law, you may have rights of access, rectification, erasure, restriction, objection, and complaint. To exercise these rights, contact pierre.stephan1@electri-c-ity-studios.com."
                        ],
                    },
                ],
            },
            "terms": {
                "route": "/terms",
                "title": "Terms of Service / License Terms",
                "description": (
                    "These public terms describe the visible Site Optimizer Core monthly plans: "
                    f"{_public_plan_titles_inline()}, plus their domain-bound commercial boundaries."
                ),
                "hero": "Terms of Service / License Terms",
                "lede": (
                    "These public terms describe the visible Site Optimizer Core monthly plans: "
                    f"{_public_plan_titles_inline()}, plus their domain-bound commercial boundaries."
                ),
                "sections": _public_plan_terms_sections()
                + [
                    {
                        "heading": "Shared public offer boundaries",
                        "paragraphs": [
                            "Not included under the public offer: open multi-domain rights beyond the licensed domain scope, custom implementation, migration, development services, or any rights beyond the public license scope unless separately agreed in writing.",
                            "Licensed download access remains protected and scope-bound. Public pages describe the offer, but they do not open private delivery, login, activation, or customer execution flows.",
                            "Access: current active release access while the license remains active",
                            "Support: email support for licensing, activation, download, billing, and technical issues",
                        ],
                    },
                    {
                        "heading": "License and access",
                        "paragraphs": [
                            "The public license is bound to the exact licensed domain or exact licensed domain set covered by the selected public plan. Licensed access, download access, and portal validation depend on an active license and correct domain validation."
                        ],
                    },
                    {
                        "heading": "Support, billing, and refunds",
                        "paragraphs": [
                            "Support is available by email at pierre.stephan1@electri-c-ity-studios.com. Invoices are issued for completed orders. Refunds and withdrawal rights are handled in accordance with applicable consumer law and the refund policy published on this website."
                        ],
                    },
                ],
            },
            "refund": {
                "route": "/refund",
                "title": "Refund Policy",
                "description": "This page summarizes the refund and withdrawal position for the public Site Optimizer Core offer.",
                "hero": "Refund Policy",
                "lede": "This page summarizes the refund and withdrawal position for the public Site Optimizer Core offer.",
                "sections": [
                    {
                        "heading": "EU consumer withdrawal right",
                        "paragraphs": [
                            "Consumers in the EU have a 14-day right of withdrawal for eligible distance purchases."
                        ],
                    },
                    {
                        "heading": "Digital products and license delivery",
                        "paragraphs": [
                            "For digital products and license deliveries, this right may expire once immediate performance begins, provided the customer expressly agrees to immediate delivery and acknowledges the loss of the withdrawal right."
                        ],
                    },
                    {
                        "heading": "When refunds remain available",
                        "paragraphs": [
                            "Refunds remain available where required by applicable consumer law."
                        ],
                    },
                    {
                        "heading": "Contact for refund requests",
                        "paragraphs": [
                            "To request a refund or exercise an applicable withdrawal right, contact pierre.stephan1@electri-c-ity-studios.com."
                        ],
                    },
                ],
            },
            "contact": {
                "route": "/contact",
                "title": "Contact / Support",
                "description": "Support for licensing, activation, download, billing, and technical issues is available by email.",
                "hero": "Contact / Support",
                "lede": "Support for licensing, activation, download, billing, and technical issues is available by email.",
                "sections": [
                    {
                        "heading": "Support contact",
                        "paragraphs": [
                            "Email: pierre.stephan1@electri-c-ity-studios.com",
                            "Typical response time: 1-3 business days (Europe/Berlin)",
                        ],
                    },
                    {
                        "heading": "What support covers",
                        "paragraphs": [
                            "Licensing, activation, download, billing, and technical issues connected to the public Site Optimizer Core offer."
                        ],
                    },
                    {
                        "heading": "What to include in your message",
                        "paragraphs": [
                            "Order details: order ID or checkout reference where available",
                            "License details: license key and licensed domain for access issues",
                            "Issue summary: a short description of the problem and what you already checked",
                        ],
                    },
                    {
                        "heading": "Billing and operator details",
                        "paragraphs": [
                            "Pierre (Bob) Stephan, trading as Electri_C_ity - Studios",
                            "Altensteiner Strasse 131",
                            "36448 Bad Liebenstein",
                            "Germany",
                            "VAT ID: DE363614431",
                        ],
                    },
                ],
            },
        },
    }
    return pages


def load_public_portal_legal_config(workspace_root: Path) -> dict[str, Any]:
    path = public_portal_legal_config_path(workspace_root)
    if path.exists():
        payload = json.loads(path.read_text(encoding="utf-8"))
    else:
        payload = _default_public_portal_legal_payload()
    defaults = _default_public_portal_legal_payload()
    identity = {**defaults["identity"], **payload.get("identity", {})}
    footer_nav = payload.get("footer_nav", defaults["footer_nav"])
    pages = {**defaults["pages"], **payload.get("pages", {})}
    pages = {
        "identity": identity,
        "footer_nav": footer_nav,
        "pages": pages,
    }
    return pages


def load_public_portal_config(workspace_root: Path) -> PublicPortalConfig:
    payload = json.loads(public_portal_config_path(workspace_root).read_text(encoding="utf-8"))
    operator_fields = load_public_portal_operator_config(workspace_root)
    legal_fields = load_public_portal_legal_config(workspace_root)
    translation = _load_public_portal_translation_config(payload)
    bind_host = str(payload.get("bind_host", "127.0.0.1")).strip() or "127.0.0.1"
    notes: list[str] = []
    if bind_host not in ALLOWED_BIND_HOSTS:
        notes.append(f"Configured bind_host '{bind_host}' is not allowed. Falling back to 127.0.0.1.")
        bind_host = "127.0.0.1"
    if bind_host == "localhost":
        bind_host = "127.0.0.1"

    return PublicPortalConfig(
        bind_host=bind_host,
        port=max(1024, int(payload.get("port", 8781))),
        selected_subdomain=str(payload.get("selected_subdomain", "")).strip(),
        alternative_subdomains=tuple(
            item.strip()
            for item in payload.get("alternative_subdomains", [])
            if isinstance(item, str) and item.strip()
        ),
        canonical_base_url=str(payload.get("canonical_base_url", "")).strip().rstrip("/"),
        product_name=str(payload.get("product_name", "Electri City Site Optimizer")).strip()
        or "Electri City Site Optimizer",
        support_contact=operator_fields.support_contact,
        download_gate_state=str(payload.get("download_gate_state", APPROVAL_REQUIRED)).strip()
        or APPROVAL_REQUIRED,
        public_routes=tuple(
            item.strip()
            for item in payload.get("public_routes", [])
            if isinstance(item, str) and item.strip()
        ),
        protected_route_prefixes=tuple(
            item.strip()
            for item in payload.get("protected_route_prefixes", [])
            if isinstance(item, str) and item.strip()
        ),
        translation=translation,
        operator_fields=operator_fields,
        legal_fields=legal_fields,
        notes=tuple(notes),
    )


def _safe_latest_summary(workspace_root: Path) -> dict[str, Any]:
    report_path = workspace_root / "var" / "reports" / "latest.json"
    if not report_path.exists():
        return {
            "latest_report_present": False,
            "status": "source not yet confirmed",
            "mode": "source not yet confirmed",
            "domain": "source not yet confirmed",
        }
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    summary = payload.get("summary", {})
    target_results = payload.get("target_results", [])
    first_result = target_results[0] if isinstance(target_results, list) and target_results else {}
    pages = {
        "latest_report_present": True,
        "run_id": payload.get("run_id", ""),
        "status": payload.get("status", ""),
        "mode": payload.get("mode", ""),
        "configured_domains": summary.get("configured_domains"),
        "domain_results": summary.get("domain_results"),
        "successful_target_probes": summary.get("successful_target_probes"),
        "domain": first_result.get("domain", ""),
        "homepage_title": first_result.get("title", ""),
        "homepage_final_url": first_result.get("final_url", ""),
        "meta_description": first_result.get("meta_description", ""),
        "response_ms": first_result.get("response_ms"),
        "html_bytes": first_result.get("html_bytes"),
        "homepage_status_code": first_result.get("homepage_status_code"),
        "sitemap_status_code": first_result.get("sitemap_status_code"),
        "cache_control": first_result.get("cache_control", ""),
        "content_encoding": first_result.get("content_encoding", ""),
        "canonical": first_result.get("canonical", ""),
        "h1_count": first_result.get("h1_count"),
        "robots_meta": first_result.get("robots_meta", ""),
    }
    return pages


def build_public_portal_snapshot(workspace_root: Path, config: AppConfig, portal: PublicPortalConfig) -> dict[str, Any]:
    reference = _safe_latest_summary(workspace_root)
    response_ms = reference.get("response_ms")
    html_bytes = reference.get("html_bytes")
    operator = portal.operator_fields
    legal = portal.legal_fields
    translation_env = _load_env_refs_from_file(workspace_root, portal.translation.env_load_point)
    translation_api_key = (
        os.environ.get(portal.translation.api_key_env, "").strip()
        or translation_env.get(portal.translation.api_key_env, "").strip()
    )
    reference_metrics = [
        {"label": "Reference Mode", "value": str(reference.get("mode", "unknown"))},
        {"label": "Portal Gate", "value": portal.download_gate_state},
        {"label": "Homepage Status", "value": str(reference.get("homepage_status_code", "n/a"))},
        {
            "label": "Response Time",
            "value": f"{response_ms:.1f} ms" if isinstance(response_ms, (int, float)) else "n/a",
        },
        {"label": "HTML Size", "value": f"{int(html_bytes):,} bytes" if isinstance(html_bytes, int) else "n/a"},
        {"label": "Sitemap Status", "value": str(reference.get("sitemap_status_code", "n/a"))},
    ]
    readiness_summary = [
        {
            "label": "Support readiness",
            "state": operator.support_readiness_state,
            "detail": f"Contact: {operator.support_contact}; Email: {operator.support_email}.",
        },
        {
            "label": "Commercial readiness",
            "state": operator.commercial_readiness_state,
            "detail": (
                f"{operator.commercial_inquiry_label}: {operator.commercial_inquiry_state}; "
                f"Pricing: {operator.pricing_model_state}; Packages: {operator.package_tiers_state}."
            ),
        },
        {
            "label": "Access readiness",
            "state": operator.access_request_state,
            "detail": "Portal copy is request-ready, but live request handling remains protected.",
        },
        {
            "label": "Legal readiness",
            "state": operator.legal_readiness_state,
            "detail": "Public legal pages are source-synced and remain presentation-level only; no protected function is opened here.",
        },
        {
            "label": "Download readiness",
            "state": operator.download_readiness_state,
            "detail": f"Portal gate: {portal.download_gate_state}; no open download or private route exposure.",
        },
    ]
    return {
        "product_name": portal.product_name,
        "selected_subdomain": portal.selected_subdomain,
        "alternative_subdomains": list(portal.alternative_subdomains),
        "canonical_base_url": portal.canonical_base_url,
        "support_contact": portal.support_contact,
        "download_gate_state": portal.download_gate_state,
        "public_routes": list(portal.public_routes),
        "protected_route_prefixes": list(portal.protected_route_prefixes),
        "operator_fields": {
            "support_contact": operator.support_contact,
            "support_email": operator.support_email,
            "commercial_inquiry_label": operator.commercial_inquiry_label,
            "commercial_inquiry_state": operator.commercial_inquiry_state,
            "pricing_model_state": operator.pricing_model_state,
            "package_tiers_state": operator.package_tiers_state,
            "access_request_state": operator.access_request_state,
            "support_readiness_state": operator.support_readiness_state,
            "commercial_readiness_state": operator.commercial_readiness_state,
            "legal_readiness_state": operator.legal_readiness_state,
            "download_readiness_state": operator.download_readiness_state,
        },
        "legal_identity": legal["identity"],
        "footer_nav": legal["footer_nav"],
        "readiness_summary": readiness_summary,
        "portal_status": {
            "mode": config.mode,
            "allow_external_changes": config.allow_external_changes,
            "portal_upstream_host": portal.bind_host,
            "portal_upstream_port": portal.port,
            "operator_console_public": False,
            "control_plane_public": False,
            "translation_provider": portal.translation.provider,
            "translation_default_language": portal.translation.default_language,
            "translation_supported_languages": list(portal.translation.supported_languages),
            "translation_activation_state": "ready"
            if portal.translation.enabled and translation_api_key
            else portal.translation.activation_state,
        },
        "safe_reference_status": reference,
        "reference_metrics": reference_metrics,
    }


def _canonical_url(portal: PublicPortalConfig, path: str) -> str:
    path = LEGAL_ROUTE_ALIASES.get(path, path)
    if path == "/":
        return f"{portal.canonical_base_url}/"
    return f"{portal.canonical_base_url}{path}"


def _google_translate_texts(texts: list[str], target_language: str, api_key: str) -> list[str]:
    if not texts:
        return []
    translated: list[str] = []
    for batch in _partition_translation_batches(texts):
        payload = urlencode(
            {
                "q": batch,
                "source": "en",
                "target": target_language,
                "format": "text",
                "key": api_key,
            },
            doseq=True,
        ).encode("utf-8")
        request = Request(
            GOOGLE_TRANSLATE_BASIC_V2_ENDPOINT,
            data=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded; charset=utf-8"},
        )
        with urlopen(request, timeout=10) as response:
            result = json.loads(response.read().decode("utf-8"))
        translations = result.get("data", {}).get("translations", [])
        if len(translations) != len(batch):
            raise ValueError("google translation response count mismatch")
        translated.extend(
            html.unescape(str(item.get("translatedText", ""))) or original
            for item, original in zip(translations, batch)
        )
    return translated


def _partition_translation_batches(texts: list[str]) -> list[list[str]]:
    batches: list[list[str]] = []
    current_batch: list[str] = []
    current_chars = 0
    for text in texts:
        text_chars = len(text)
        if current_batch and (
            len(current_batch) >= GOOGLE_TRANSLATE_MAX_TEXTS_PER_REQUEST
            or current_chars + text_chars > GOOGLE_TRANSLATE_MAX_CHARS_PER_REQUEST
        ):
            batches.append(current_batch)
            current_batch = []
            current_chars = 0
        current_batch.append(text)
        current_chars += text_chars
    if current_batch:
        batches.append(current_batch)
    return batches


def _collect_translatable_strings(payload: Any, *, key: str | None = None) -> list[str]:
    if isinstance(payload, dict):
        strings: list[str] = []
        for item_key, value in payload.items():
            if item_key in {"href", "route"}:
                continue
            strings.extend(_collect_translatable_strings(value, key=item_key))
        return strings
    if isinstance(payload, list):
        strings: list[str] = []
        for item in payload:
            strings.extend(_collect_translatable_strings(item))
        return strings
    if isinstance(payload, str):
        return [payload] if payload.strip() else []
    return []


def _apply_translated_strings(payload: Any, translations: list[str], *, key: str | None = None) -> Any:
    iterator = iter(translations)

    def _walk(value: Any, *, item_key: str | None = None) -> Any:
        if isinstance(value, dict):
            result: dict[str, Any] = {}
            for child_key, child_value in value.items():
                if child_key in {"href", "route"}:
                    result[child_key] = child_value
                else:
                    result[child_key] = _walk(child_value, item_key=child_key)
            return result
        if isinstance(value, list):
            return [_walk(item) for item in value]
        if isinstance(value, str):
            if value.strip():
                return next(iterator)
            return value
        return value

    return _walk(payload, item_key=key)


def _resolve_public_portal_translation_state(
    workspace_root: Path,
    portal: PublicPortalConfig,
    requested_language: str,
) -> dict[str, Any]:
    default_language = portal.translation.default_language
    normalized_requested = _normalize_language_code(requested_language, default_language)
    supported_languages = portal.translation.supported_languages
    if normalized_requested not in supported_languages:
        normalized_requested = default_language
    env_values = _load_env_refs_from_file(workspace_root, portal.translation.env_load_point)
    api_key = (
        os.environ.get(portal.translation.api_key_env, "").strip()
        or env_values.get(portal.translation.api_key_env, "").strip()
    )
    ready = portal.translation.enabled and bool(api_key)
    return {
        "requested_language": normalized_requested,
        "default_language": default_language,
        "effective_language": default_language,
        "supported_languages": list(supported_languages),
        "provider": portal.translation.provider,
        "activation_state": "ready" if ready else portal.translation.activation_state,
        "api_key": api_key,
        "machine_translation_requested": normalized_requested != default_language,
        "machine_translation_applied": False,
        "note": "",
    }


def _translate_public_page_copy(
    page: dict[str, Any],
    target_language: str,
    api_key: str,
) -> dict[str, Any]:
    strings = _collect_translatable_strings(page)
    translated = _google_translate_texts(strings, target_language, api_key)
    return _apply_translated_strings(page, translated)


def _build_legal_pages(portal: PublicPortalConfig) -> dict[str, dict[str, Any]]:
    pages: dict[str, dict[str, Any]] = {}
    legal_pages = portal.legal_fields.get("pages", {})
    for payload in legal_pages.values():
        route = payload["route"]
        pages[route] = {
            "title": f"{payload['title']} | {portal.product_name}",
            "description": payload["description"],
            "eyebrow": "Public legal information",
            "hero": payload["hero"],
            "lede": payload["lede"],
            "sections": [
                {
                    "eyebrow": "Source-synced public page",
                    "heading": section["heading"],
                    "paragraphs": section.get("paragraphs", []),
                }
                for section in payload.get("sections", [])
            ],
            "trust_points": [
                "Source-synced public legal page",
                "Presentation harmonized only at the portal layer",
                "No login, checkout, license API or private download opened here",
            ],
            "primary_cta": {"href": "/contact", "label": "Open contact and support"},
            "secondary_cta": {"href": "/support", "label": "Return to support guidance"},
            "disable_software_application_markup": True,
            "final_cta": {
                "heading": "Need product context beyond this legal page?",
                "body": "Use the public docs, support guidance and licensing overview for portal context. Protected execution remains separate.",
                "primary": {"href": "/docs", "label": "Open the documentation entry"},
                "secondary": {"href": "/support", "label": "Return to support guidance"},
            },
        }
    return pages


def _related_page(href: str, label: str, summary: str) -> dict[str, str]:
    return {"href": href, "label": label, "summary": summary}


def _build_audience_pages(portal: PublicPortalConfig, snapshot: dict[str, Any]) -> dict[str, dict[str, Any]]:
    operator = portal.operator_fields
    readiness_summary = snapshot["readiness_summary"]
    public_plan_titles_copy = _public_plan_titles_inline()
    public_plan_scope_bullets = _public_plan_scope_bullets()
    public_pricing_cards = _public_plan_pricing_cards()
    return {
        "/explore": {
            "title": f"Explore WordPress SEO and Performance Optimization Paths | {portal.product_name}",
            "description": (
                "Explore the public product paths for a guarded WordPress SEO and performance suite, including "
                "visible monthly plans, documentation, licensing, support and protected delivery preparation."
            ),
            "eyebrow": "Explore the platform",
            "hero": "Explore the guarded routes into the WordPress optimization product.",
            "lede": (
                "This page helps visitors choose the right public path first: product orientation, visible monthly plans, "
                "licensing boundaries, support clarification, documentation entry or gated access preparation. "
                "The same doctrine also keeps later plugin execution bounded, explainable and reversible."
            ),
            "trust_points": [
                "Public orientation page only",
                "Plugin-first execution model",
                "Visible Guardian Core, Sovereign Enterprise and Sovereign Critical monthly plans",
                "Buyer-readable installed insight surface after activation",
                "No checkout, login or protected delivery exposed here",
            ],
            "primary_cta": {"href": "/buy", "label": "Compare the public monthly plans"},
            "secondary_cta": {"href": "/features", "label": "Review the product capabilities"},
            "sections": [
                {
                    "eyebrow": "Orientation",
                    "heading": "Start with the path that matches your current certainty",
                    "paragraphs": [
                        (
                            "If you are still evaluating fit, start with the product capabilities and the plugin model. "
                            "If you already know the domain, scope and stack, move next into licensing, buy and guarded access preparation. "
                            "The best path is the one with the least ambiguity and the strongest explainability."
                        )
                    ],
                    "bullets": [
                        "Explore features and product structure first",
                        "Use docs when you want architecture and doctrine depth before a request path",
                        "Use support for scope clarification before protected workflows are requested",
                        "Use buy and downloads to understand the public offer and what stays gated",
                        "Compare the public monthly plans before you ask for protected access",
                    ],
                    "links": [
                        {"href": "/features", "label": "Open features"},
                        {"href": "/docs", "label": "Open docs"},
                        {"href": "/support", "label": "Open support guidance"},
                    ],
                },
                {
                    "eyebrow": "Visible monthly plans",
                    "heading": "The public offer is visible before delivery is ever opened",
                    "paragraphs": [
                        (
                            f"The portal now makes the public monthly plans visible up front: {public_plan_titles_copy}. "
                            "Each plan keeps exact licensed scope explicit and each keeps documentation, validation posture and protected access expectations visible."
                        ),
                        (
                            "That does not open delivery, activation or customer execution. It simply makes the public offer easier to evaluate before any protected step is considered."
                        ),
                        (
                            "It also makes the installed product easier to trust later, because the same Suite is designed to show buyer-readable scope, health and cutover signals after activation."
                        ),
                    ],
                    "bullets": public_plan_scope_bullets
                    + [
                        "Documentation, validation posture and protected access expectations remain visible across the public plans",
                    ],
                    "links": [
                        {"href": "/buy", "label": "Open the buy page"},
                        {"href": "/terms", "label": "Open the terms and license terms"},
                        {"href": "/licensing", "label": "Review licensing fit"},
                        {"href": "/downloads", "label": "Review gated access preparation"},
                    ],
                },
                {
                    "eyebrow": "Installed visibility",
                    "heading": "The bridge is built to explain itself after installation",
                    "paragraphs": [
                        (
                            "The public portal is only the first layer. Once the protected plugin is installed, the buyer can inspect domain binding, baseline evidence, open blockers, protected delivery state and the next gate before any broader optimization is allowed."
                        )
                    ],
                    "bullets": [
                        "License, domain and scope stay visible in the installed admin surface",
                        "Baseline, conflict picture and guardrails stay readable",
                        "Protected delivery remains separate even when buyer visibility improves",
                    ],
                    "links": [
                        {"href": "/plugin", "label": "See the plugin execution model"},
                        {"href": "/buy", "label": "Review the public monthly plans"},
                    ],
                },
                {
                    "eyebrow": "Audience fit",
                    "heading": "Choose the audience path that most closely matches your role",
                    "paragraphs": [
                        "Agencies, publishers and owner-operators have different evaluation needs. The portal now separates those perspectives without changing the protected delivery model or the zero-trust validation posture."
                    ],
                    "bullets": [
                        "Agencies: client-by-client scoping and safer rollout discipline",
                        "Publishers: homepage ownership, performance hygiene and rollback-aware changes",
                        "Buy: Guardian Core, Sovereign Enterprise and Sovereign Critical monthly plans plus guarded access and support preparation",
                    ],
                    "links": [
                        {"href": "/agencies", "label": "See the agencies path"},
                        {"href": "/publishers", "label": "See the publishers path"},
                        {"href": "/buy", "label": "See the buy path"},
                    ],
                },
            ],
            "faq": [
                {
                    "question": "Does explore open any protected function?",
                    "answer": "No. Explore is a public orientation layer only and keeps delivery, activation and customer execution protected.",
                },
                {
                    "question": "Where should a new visitor go after this page?",
                    "answer": "Usually to buy, features, docs, licensing or support, depending on whether the next need is public offer review, product understanding, doctrine depth, commercial fit or scope clarification.",
                },
            ],
            "final_cta": {
                "heading": "Choose the next public path with the least ambiguity",
                "body": "Use buy for the visible monthly plans, features for product understanding, docs for doctrine depth, licensing for domain and scope fit, or support when the scope still needs clarification.",
                "primary": {"href": "/buy", "label": "Open the buy path"},
                "secondary": {"href": "/docs", "label": "Open the docs path"},
            },
        },
        "/agencies": {
            "title": f"WordPress SEO and Performance Optimization for Agencies | {portal.product_name}",
            "description": (
                "See how agencies can evaluate the plugin-first WordPress optimization product with clear domain scoping, "
                "rollback discipline and no implied multi-domain entitlement."
            ),
            "eyebrow": "Agency fit",
            "hero": "Agency-friendly product logic without pretending multi-domain rights.",
            "lede": (
                "This public page explains why agencies may value the platform for safer client-by-client optimization planning, "
                "while keeping the visible offer strictly bound to explicit exact licensed scope per public plan."
            ),
            "trust_points": [
                "Client-by-client scoping",
                "Tier-bound domain counts with no open-ended multi-domain promise",
                "Protected rollout remains separate",
                "Installed plugin state is designed to stay buyer-readable per domain",
            ],
            "primary_cta": {"href": "/licensing", "label": "Check domain and scope boundaries"},
            "secondary_cta": {"href": "/support", "label": "Clarify agency fit with support"},
            "sections": [
                {
                    "eyebrow": "Why agencies care",
                    "heading": "Safer operational discipline matters when you advise multiple WordPress sites",
                    "paragraphs": [
                        (
                            "Agencies usually need stronger rollback logic, clearer plugin coexistence and narrower scope definitions than improvised per-client SEO stacks can provide. "
                            "That is the strongest public value proposition here."
                        )
                    ],
                    "bullets": [
                        "Better preflight clarity before any pilot is considered",
                        "Cleaner domain-by-domain licensing boundaries",
                        "Better fit for documented rollout and rollback expectations",
                    ],
                    "links": [
                        {"href": "/plugin", "label": "Review plugin execution constraints"},
                        {"href": "/security", "label": "Review rollback and validation"},
                    ],
                },
                {
                    "eyebrow": "Important boundary",
                    "heading": "Agency interest does not change the public license boundary",
                    "paragraphs": [
                        (
                            "The visible public offer remains tied to explicit exact licensed scope: Guardian Core Monthly for one exact licensed domain, "
                            "Sovereign Enterprise Monthly for a commercially reviewed exact licensed multi-domain scope, and Sovereign Critical Monthly for an individually approved exact licensed high-compliance scope. "
                            "This page does not imply reseller rights, open-ended multi-domain entitlements or custom agency rollout terms."
                        )
                    ],
                    "bullets": [
                        "No coverage beyond the exact licensed scope of the selected public plan",
                        "No custom implementation or migration services implied here",
                        "Any broader arrangement would still require separate written agreement and later approval",
                    ],
                    "links": [
                        {"href": "/terms", "label": "Read the public terms"},
                        {"href": "/buy", "label": "See the public buy path"},
                    ],
                },
            ],
            "faq": [
                {
                    "question": "Does this page promise an agency package?",
                    "answer": "No. It explains agency fit and tier boundaries only. The public tiers are visible, but custom agency structures, reseller rights and protected fulfillment remain outside this page.",
                }
            ],
            "final_cta": {
                "heading": "Use licensing and support to qualify a real domain-specific fit",
                "body": "Agencies should narrow down one exact target domain, the current WordPress stack and the desired pilot scope before any protected path is considered.",
                "primary": {"href": "/buy", "label": "Review the public offer"},
                "secondary": {"href": "/support", "label": "Open scope clarification"},
            },
        },
        "/publishers": {
            "title": f"WordPress SEO and Performance Optimization for Publishers | {portal.product_name}",
            "description": (
                "See how publishers and owner-operators can use the plugin-first WordPress optimization model for homepage SEO, "
                "markup hygiene and rollback-aware performance work."
            ),
            "eyebrow": "Publisher fit",
            "hero": "Built for operators who want clearer ownership over homepage SEO and performance.",
            "lede": (
                "Publishers and owner-operators benefit most when the homepage, metadata, markup and validation logic can be handled more deliberately than in a loose plugin stack."
            ),
            "trust_points": [
                "Homepage-first optimization discipline",
                "Conflict-aware plugin path",
                "Rollback-aware output changes",
                "Installed bridge keeps health and cutover signals visible after activation",
            ],
            "primary_cta": {"href": "/plugin", "label": "Review the plugin path"},
            "secondary_cta": {"href": "/buy", "label": "See the public offer"},
            "sections": [
                {
                    "eyebrow": "Why publishers care",
                    "heading": "The platform is strongest where one site needs better SEO ownership and cleaner change control",
                    "paragraphs": [
                        (
                            "The reference path starts with homepage metadata, heading structure, markup hygiene, validation and rollback. "
                            "That aligns well with publisher sites and performance-oriented WordPress operators."
                        )
                    ],
                    "bullets": [
                        "Homepage meta description and structure are narrow, measurable pilot candidates",
                        "Conflict detection reduces accidental overlap with existing SEO plugins",
                        "Observe_only and safe_mode reduce the pressure to change too much too early",
                    ],
                    "links": [
                        {"href": "/features", "label": "See the full feature set"},
                        {"href": "/downloads", "label": "Review gated access preparation"},
                    ],
                },
                {
                    "eyebrow": "Guarded rollout",
                    "heading": "Publisher fit still depends on clean scope, source ownership and rollback clarity",
                    "paragraphs": [
                        (
                            "This remains a guarded product path. The public portal prepares the discussion, but does not imply that any live WordPress site can be changed without later approval and precise scope confirmation."
                        )
                    ],
                    "links": [
                        {"href": "/security", "label": "See the guardrails"},
                        {"href": "/support", "label": "See what support needs from you"},
                    ],
                },
            ],
            "faq": [
                {
                    "question": "Is this already a public self-serve optimization tool?",
                    "answer": "No. It is a public product portal for a guarded optimization product. Protected execution, downloads and activation remain separate.",
                }
            ],
            "final_cta": {
                "heading": "Move next into plugin fit, buy readiness or support clarification",
                "body": "Publishers usually need to confirm source ownership, stack details and rollback responsibility before any later pilot can move forward.",
                "primary": {"href": "/downloads", "label": "Prepare gated access context"},
                "secondary": {"href": "/support", "label": "Open support guidance"},
            },
        },
        "/buy": {
            "title": f"WordPress SEO and Performance Suite Pricing and Offer | {portal.product_name}",
            "description": (
                f"Compare the public monthly plans {public_plan_titles_copy} for a guarded WordPress SEO and performance suite "
                "with exact licensed scope, validation discipline and protected access expectations."
            ),
            "eyebrow": "Pricing, scope and protected delivery",
            "hero": "Choose the public monthly plan before any protected delivery step begins.",
            "lede": (
                f"This page explains the visible monthly plans {public_plan_titles_copy}, who each plan fits, what stays included, "
                "what remains outside the public offer and why protected delivery still stays deliberately gated. "
                "It also explains why the installed bridge later stays buyer-readable, bounded and reversible instead of behaving like a black box."
            ),
            "trust_points": [
                "Clear public plans with explicit exact licensed scope",
                "Installed buyer-readable admin insights after activation",
                "No open checkout, login, activation or package fulfillment here",
                "Protected delivery, validation and rollback remain separate by design",
            ],
            "primary_cta": {"href": "/licensing", "label": "Check plan and licensing fit"},
            "secondary_cta": {"href": "/terms", "label": "Read the public terms"},
            "spotlight": {
                "title": "Protected delivery stays deliberate",
                "body": (
                    "The public pricing model is visible on purpose. Delivery, activation, private download and customer execution "
                    "remain protected because the Suite is designed around scope control, validation evidence and rollback readiness. "
                    "The buyer still gets readable installed state after activation; what stays closed is unsafe or unbounded execution."
                ),
            },
            "readiness_summary": readiness_summary,
            "pricing_tiers": public_pricing_cards,
            "sections": [
                {
                    "eyebrow": "Who this is for",
                    "heading": "Choose the plan that matches your real exact licensed domain scope",
                    "paragraphs": [
                        (
                            "Guardian Core Monthly is the clearest fit for one operator and one exact licensed domain. Sovereign Enterprise Monthly fits larger, tightly managed environments with a commercially reviewed exact licensed multi-domain scope. "
                            "Sovereign Critical Monthly fits business-critical environments that need individually approved high-compliance control."
                        ),
                        (
                            "The public offer is therefore not just a price table. It is a scope filter that helps decide whether the next conversation "
                            "belongs in licensing, downloads preparation or support clarification."
                        ),
                    ],
                    "bullets": public_plan_scope_bullets,
                    "links": [
                        {"href": "/licensing", "label": "Check scope and domain fit"},
                        {"href": "/support", "label": "Clarify plan fit with support"},
                    ],
                },
                {
                    "eyebrow": "Included across all public plans",
                    "heading": "What the public offer includes clearly and consistently",
                    "paragraphs": [
                        (
                            "Every visible plan keeps the same basic public structure: monthly commercial use within the exact licensed scope of the selected plan, "
                            "plus documentation, validation posture and protected access expectations."
                        ),
                        (
                            "That consistency keeps the public offer easier to compare without implying that lower-friction delivery, broader rights or deeper services are already included."
                        ),
                        (
                            "The product is also built to keep the installed bridge explainable after activation, so the buyer can see scope, health and cutover status without opening customer login or public delivery routes."
                        ),
                    ],
                    "bullets": [
                        "Monthly commercial use within the selected exact licensed scope",
                        "Documentation",
                        "Protected access expectations",
                        "Buyer-readable installed insight surface after protected activation",
                    ],
                    "links": [
                        {"href": "/terms", "label": "See the full public offer wording"},
                        {"href": "/downloads", "label": "Review guarded access preparation"},
                    ],
                },
                {
                    "eyebrow": "Not included under the public offer",
                    "heading": "What the public offer does not expand or silently promise",
                    "paragraphs": [
                        "Not included under the public offer: open multi-domain rights beyond the exact licensed scope, custom implementation, migration, development services, or any rights beyond the public license scope unless separately agreed in writing.",
                        (
                            "This keeps the page commercially honest. It shows a stronger public model, but it does not pretend that pricing automatically includes wider delivery, custom work or unbounded multi-domain rights."
                        ),
                    ],
                    "links": [
                        {"href": "/terms", "label": "Read the terms and license boundaries"},
                        {"href": "/refund", "label": "Review refund and withdrawal context"},
                    ],
                },
                {
                    "eyebrow": "Protected delivery",
                    "heading": "Why licensed download access remains protected and scope-bound",
                    "paragraphs": [
                        "Licensed download access remains protected and scope-bound. Public pages describe the offer, but they do not open private delivery, login, activation, or customer execution flows.",
                        (
                            "That protection matters because the Suite is built around scope clarity, plugin coexistence, validation evidence and rollback readiness. "
                            "Public visibility is allowed. Unbounded execution is not."
                        ),
                        (
                            "The result is a calmer buying path: the offer is visible, the installed state is explainable, and any real delivery or execution step remains controlled instead of implicit."
                        ),
                    ],
                    "bullets": [
                        "No anonymous production package delivery",
                        "No instant activation or customer execution path from this page",
                        "Protected delivery remains tied to domain, scope and later approval",
                    ],
                    "links": [
                        {"href": "/downloads", "label": "See the gated access path"},
                        {"href": "/security", "label": "See why protected delivery stays gated"},
                    ],
                },
                {
                    "eyebrow": "Trust, safety and rollback",
                    "heading": "Why exact licensed scope and guarded delivery improve trust",
                    "paragraphs": [
                        (
                            "Exact licensed scope stays visible because the Suite is not meant to leak across unclear site boundaries. "
                            "The public pricing model is stronger when domain boundaries stay explicit instead of implied."
                        ),
                        (
                            "The same principle supports safer rollback: if scope stays bounded, validation and rollback decisions stay easier to explain and safer to reverse."
                        ),
                        (
                            "That same doctrine also improves buyer trust after installation, because the bridge can show what it sees, what is blocked and what is still approval-gated instead of hiding all logic behind activation."
                        ),
                    ],
                    "bullets": [
                        "Domain scope stays explicit instead of implied",
                        "Rollback reasoning stays clearer when scope is narrower",
                        "Protected delivery reduces accidental cross-domain drift",
                        "Installed plugin state is designed to stay explainable to the buyer",
                    ],
                    "links": [
                        {"href": "/security", "label": "Review validation and rollback"},
                        {"href": "/licensing", "label": "Review domain-bound licensing"},
                    ],
                },
                {
                    "eyebrow": "What to prepare",
                    "heading": "What to prepare before requesting access or activation context",
                    "paragraphs": [
                        (
                            "A serious next step starts with the exact target domain, current WordPress stack, source ownership for the homepage output and later rollback responsibility."
                        ),
                        (
                            f"Commercial inquiry path: {operator.commercial_inquiry_state}. Pricing model state: {operator.pricing_model_state}. Package tiers state: {operator.package_tiers_state}."
                        ),
                    ],
                    "bullets": [
                        "Exact licensed domain",
                        "Theme, builder and active SEO plugin inventory",
                        "Rollback owner and validation owner",
                    ],
                    "links": [
                        {"href": "/support", "label": "See what support needs from you"},
                        {"href": "/contact", "label": "Open contact and support details"},
                    ],
                },
                {
                    "eyebrow": "What remains approval_required",
                    "heading": "What remains protected after this public offer page",
                    "paragraphs": [
                        "Any real license activation, package delivery, private download, protected customer access or live execution step remains approval_required."
                    ],
                    "bullets": [
                        f"Access readiness: {operator.access_request_state}",
                        f"Download readiness: {operator.download_readiness_state}",
                        "Customer authentication: approval_required",
                        "Protected execution routes: non-public",
                    ],
                    "links": [
                        {"href": "/downloads", "label": "Review the gated access page"},
                        {"href": "/support", "label": "Open support guidance"},
                        {"href": "/refund", "label": "Review refund policy"},
                    ],
                },
            ],
            "faq": [
                {
                    "question": "Can I buy and download directly from this page?",
                    "answer": "No. This page explains the public offer and the guarded next steps only. Open checkout, customer login, activation and package fulfillment are not exposed here.",
                },
                {
                    "question": "Why are exact licensed domain and exact licensed domains stated so explicitly?",
                    "answer": "Because the product stays safer when domain scope is explicit. The public offer is intentionally bounded to one exact licensed domain or an explicitly reviewed exact licensed domain set instead of vague multi-domain rights.",
                },
                {
                    "question": "What does licensed download access mean on a protected offer page?",
                    "answer": "It means the licensed plan includes download eligibility, but delivery remains protected and scope-bound. Public pages describe the offer without opening private download, login or execution routes.",
                },
                {
                    "question": "Which plan usually fits which operator?",
                    "answer": "Guardian Core Monthly fits one exact licensed domain, Sovereign Enterprise Monthly fits larger environments with a commercially reviewed exact licensed multi-domain scope, and Sovereign Critical Monthly fits high-compliance environments with individually approved exact licensed scope.",
                },
            ],
            "final_cta": {
                "heading": "Use terms, licensing, downloads and support as the public preflight path",
                "body": "Review the public terms, confirm domain fit, inspect guarded access preparation and clarify support context before any protected delivery step is considered.",
                "primary": {"href": "/downloads", "label": "Review guarded access preparation"},
                "secondary": {"href": "/support", "label": "Clarify scope with support"},
            },
        },
    }


def _apply_related_pages(pages: dict[str, dict[str, Any]]) -> None:
    related_map = {
        "/": [
            _related_page("/explore", "Explore the portal", "Start with the orientation path for product, docs and support."),
            _related_page("/buy", "See the public offer path", "Understand the visible offer without opening checkout or delivery."),
            _related_page("/agencies", "Agency fit", "See how agencies can evaluate the product without implying multi-domain rights."),
            _related_page("/publishers", "Publisher fit", "See the fit for operators focused on homepage SEO and performance."),
        ],
        "/explore": [
            _related_page("/features", "Features", "Review the product stack and protected control-plane model."),
            _related_page("/docs", "Docs", "Enter the documentation path from a public overview."),
            _related_page("/support", "Support", "Clarify scope before any protected workflow."),
            _related_page("/buy", "Buy", "Move from exploration into the public offer and guarded next steps."),
        ],
        "/features": [
            _related_page("/explore", "Explore", "Use the public orientation layer first."),
            _related_page("/plugin", "Plugin", "See the primary WordPress execution path."),
            _related_page("/buy", "Buy", "Connect capabilities to the public offer path."),
            _related_page("/docs", "Docs", "Continue into architectural documentation."),
        ],
        "/security": [
            _related_page("/docs", "Docs", "Review doctrine, validation and rollback details."),
            _related_page("/support", "Support", "Use support for scope clarification, not protected execution."),
            _related_page("/legal", "Legal notice", "Check operator and legal identity details."),
            _related_page("/privacy", "Privacy", "Review the source-synced privacy statement."),
        ],
        "/plugin": [
            _related_page("/buy", "Buy", "See how the public offer relates to the plugin path."),
            _related_page("/licensing", "Licensing", "Review domain and scope boundaries."),
            _related_page("/support", "Support", "Clarify source ownership and coexistence questions."),
            _related_page("/security", "Security", "Review safe mode, validation and rollback logic."),
        ],
        "/licensing": [
            _related_page("/buy", "Buy", "See the public offer and what stays gated."),
            _related_page("/terms", "Terms", "Read the public terms and license scope."),
            _related_page("/downloads", "Downloads", "Review guarded access preparation."),
            _related_page("/support", "Support", "Clarify commercial and scope questions."),
        ],
        "/buy": [
            _related_page("/terms", "Terms / License Terms", "Read the visible public offer and license scope."),
            _related_page("/licensing", "Licensing", "Check exact licensed domain fit and scope boundaries."),
            _related_page("/downloads", "Downloads", "See what guarded access preparation looks like."),
            _related_page("/support", "Support", "Clarify scope, stack and readiness before protected delivery."),
            _related_page("/refund", "Refund Policy", "Review consumer-law and refund boundaries."),
        ],
        "/docs": [
            _related_page("/explore", "Explore", "Return to the public orientation path."),
            _related_page("/plugin", "Plugin", "Review the execution model."),
            _related_page("/security", "Security", "See doctrine and rollback boundaries."),
            _related_page("/support", "Support", "Move from docs into scope clarification."),
        ],
        "/downloads": [
            _related_page("/buy", "Buy", "See the visible offer before the guarded delivery path."),
            _related_page("/licensing", "Licensing", "Confirm domain and scope fit."),
            _related_page("/support", "Support", "Prepare the support-side context for a later request."),
            _related_page("/terms", "Terms", "Review public delivery and support boundaries."),
        ],
        "/support": [
            _related_page("/buy", "Buy", "Connect support questions with the public offer path."),
            _related_page("/downloads", "Downloads", "See what access-readiness requires."),
            _related_page("/licensing", "Licensing", "Review scope and domain fit."),
            _related_page("/contact", "Contact / Support", "Open the public contact details."),
        ],
        "/agencies": [
            _related_page("/buy", "Buy", "See the public offer without implying agency entitlements."),
            _related_page("/licensing", "Licensing", "Review one-domain scope boundaries."),
            _related_page("/support", "Support", "Clarify agency-side rollout questions."),
            _related_page("/terms", "Terms", "Read the public offer and exclusions."),
        ],
        "/publishers": [
            _related_page("/plugin", "Plugin", "Review the guarded WordPress execution path."),
            _related_page("/features", "Features", "See broader platform capabilities."),
            _related_page("/downloads", "Downloads", "Review the gated access preparation path."),
            _related_page("/support", "Support", "Clarify stack and source ownership questions."),
        ],
        "/legal": [
            _related_page("/privacy", "Privacy", "Review the source-synced privacy policy."),
            _related_page("/terms", "Terms", "Review public offer and license terms."),
            _related_page("/contact", "Contact", "Open public support details."),
            _related_page("/support", "Support", "Return to support guidance."),
        ],
        "/privacy": [
            _related_page("/legal", "Legal notice", "Review operator identity and public legal notice."),
            _related_page("/contact", "Contact", "Use the public support address for privacy questions."),
            _related_page("/terms", "Terms", "Review public offer and access boundaries."),
            _related_page("/support", "Support", "Return to the public support path."),
        ],
        "/terms": [
            _related_page("/buy", "Buy", "Move from terms into the buy and readiness path."),
            _related_page("/refund", "Refund", "Review consumer-law and refund boundaries."),
            _related_page("/licensing", "Licensing", "Review domain and scope fit."),
            _related_page("/contact", "Contact", "Use the public support address."),
        ],
        "/refund": [
            _related_page("/terms", "Terms", "Return to the public offer and license terms."),
            _related_page("/contact", "Contact", "Use the public support address for refund questions."),
            _related_page("/legal", "Legal notice", "Review operator identity details."),
            _related_page("/support", "Support", "Return to the public support path."),
        ],
        "/contact": [
            _related_page("/support", "Support", "Return to support guidance and scope preparation."),
            _related_page("/buy", "Buy", "Review the public offer path."),
            _related_page("/downloads", "Downloads", "See the guarded access path."),
            _related_page("/legal", "Legal notice", "Review operator and legal identity details."),
        ],
    }
    for route, items in related_map.items():
        if route in pages:
            pages[route]["related_pages"] = items


def _page_copy(portal: PublicPortalConfig, snapshot: dict[str, Any]) -> dict[str, dict[str, Any]]:
    reference = snapshot["safe_reference_status"]
    operator = portal.operator_fields
    legal_identity = portal.legal_fields["identity"]
    reference_domain = reference.get("domain") or "electri-c-ity-studios-24-7.com"
    reference_mode = str(reference.get("mode", "observe_only"))
    reference_status = str(reference.get("status", "validated"))
    response_ms = reference.get("response_ms")
    response_copy = f"{response_ms:.1f} ms" if isinstance(response_ms, (int, float)) else "n/a"
    html_bytes = reference.get("html_bytes")
    html_copy = f"{int(html_bytes):,} bytes" if isinstance(html_bytes, int) else "n/a"
    status_code = reference.get("homepage_status_code", "n/a")
    sitemap_status = reference.get("sitemap_status_code", "n/a")
    support_copy = operator.support_contact
    support_email_copy = operator.support_email
    commercial_label_copy = operator.commercial_inquiry_label
    commercial_state_copy = operator.commercial_inquiry_state
    pricing_state_copy = operator.pricing_model_state
    package_state_copy = operator.package_tiers_state
    access_state_copy = operator.access_request_state
    readiness_summary = snapshot["readiness_summary"]
    support_contact_paragraph = (
        "Primary support contact is currently documented as operator input required. The portal keeps that honest instead of inventing contact details that are not yet confirmed."
        if support_copy == OPERATOR_INPUT_REQUIRED
        else f"Primary support contact is currently shown as {support_copy}. This remains a public information field only and does not expose protected operator action."
    )
    licensing_pricing_faq = (
        "No. Pricing and commercial delivery details remain operator input required and are not invented on the public portal."
        if pricing_state_copy == OPERATOR_INPUT_REQUIRED
        else "Yes, public pricing tiers are visible. No, this page still does not become a checkout or fulfillment surface."
    )
    public_plan_titles_copy = _public_plan_titles_inline()
    public_plan_scope_bullets = _public_plan_scope_bullets()
    public_pricing_cards = _public_plan_pricing_cards()
    pages = {
        "/": {
            "title": f"WordPress SEO and Performance Suite, Pricing and Access Readiness | {portal.product_name}",
            "description": (
                "Plugin-first WordPress SEO and performance suite with visible monthly plans, exact licensed domain boundaries, "
                "request-ready access guidance, protected delivery and doctrine-enforced rollback discipline."
            ),
            "eyebrow": "WordPress SEO and Performance Optimization Platform",
            "hero": "A guarded WordPress SEO and Performance Suite with visible public tiers.",
            "lede": (
                "Electri City Site Optimizer combines a protected Hetzner control plane with a future "
                "domain-bound WordPress plugin, so SEO and performance changes stay scoped, measurable, request-ready, explainable and reversible."
            ),
            "trust_points": [
                "Plugin-first execution path for WordPress SEO and performance work",
                "Visible Guardian Core, Sovereign Enterprise and Sovereign Critical monthly plans",
                "Rollback, validation and observe_only discipline before any real change",
                "Buyer-readable installed insights after protected plugin activation",
                "Public product portal separated from protected operator and customer routes",
                "Request-ready without opening downloads, login or license execution",
            ],
            "primary_cta": {"href": "/buy", "label": "Review the public monthly plans"},
            "secondary_cta": {"href": "/explore", "label": "Explore the product paths"},
            "spotlight": {
                "title": "Reference site evidence and visible public offer",
                "body": (
                    f"The current reference run for {reference_domain} is {reference_status} in {reference_mode}. "
                    f"Homepage status {status_code}, response time {response_copy}, HTML size {html_copy}, "
                    f"sitemap status {sitemap_status}. The public portal now also makes {public_plan_titles_copy} visible without exposing control-plane internals or protected delivery."
                ),
            },
            "sections": [
                {
                    "eyebrow": "Positioning",
                    "heading": "Built for serious WordPress SEO and performance operations",
                    "paragraphs": [
                        (
                            "The public portal introduces a doctrine-enforced product for teams that want tighter SEO control, "
                            "cleaner change discipline, clearer buyer visibility and safer WordPress optimization than ad hoc plugin stacking usually provides."
                        ),
                        (
                            "The architecture keeps public marketing, protected control-plane logic and future customer execution "
                            "strictly separated, so the visible product surface stays clear while operational authority stays protected. "
                            "That is the core of governed autonomy here: the Suite can become smarter without becoming reckless."
                        ),
                    ],
                    "bullets": [
                        "Hetzner remains the learning, validation, licensing and rollback authority",
                        "WordPress plugin remains the primary future execution plane on each licensed domain",
                        "Cloudflare stays secondary and only for later, scoped edge-level work",
                    ],
                    "links": [
                        {"href": "/features", "label": "See the product capabilities"},
                        {"href": "/licensing", "label": "Understand domain-bound licensing"},
                    ],
                },
                {
                    "eyebrow": "Visible monthly plans",
                    "heading": "The public offer is now clear before any protected delivery step",
                    "paragraphs": [
                        (
                            f"The Suite now shows its public monthly plans directly: {public_plan_titles_copy}. "
                            "Each plan keeps exact licensed scope explicit and each keeps documentation, validation posture and protected access expectations visible."
                        ),
                        (
                            "This improves commercial clarity without weakening the doctrine. Delivery, activation, private download and customer execution still remain protected."
                        ),
                    ],
                    "bullets": [
                        "Guardian Core Monthly: EUR 2,500.00 / month for one exact licensed domain",
                        "Sovereign Enterprise Monthly: EUR 9,500.00 / month for a commercially reviewed exact licensed multi-domain scope",
                        "Sovereign Critical Monthly: EUR 25,000.00 / month for an individually approved exact licensed high-compliance scope",
                        "Controlled validation and protected access expectations stay visible across the public monthly plans",
                    ],
                    "links": [
                        {"href": "/buy", "label": "See the full public offer"},
                        {"href": "/terms", "label": "Read the public terms"},
                        {"href": "/licensing", "label": "Review scope and domain fit"},
                    ],
                },
                {
                    "eyebrow": "Who this is for",
                    "heading": "Built for teams that want safer WordPress optimization than ad hoc plugin stacking",
                    "paragraphs": [
                        (
                            "The strongest fit is a WordPress team, operator, builder or agency that can clearly name the target domain, "
                            "the active theme or builder stack and the scope they want reviewed before any later pilot is requested."
                        ),
                        (
                            "That makes the platform especially relevant for homepage SEO ownership, metadata refinement, markup hygiene, "
                            "rollback-aware release handling, controlled plugin coexistence and buyer-readable installed visibility."
                        ),
                    ],
                    "bullets": [
                        "Teams with one clearly defined WordPress domain in scope",
                        "Operators who can document theme, builder and SEO-plugin ownership",
                        "Projects that accept narrow pilots before broader execution",
                    ],
                    "links": [
                        {"href": "/plugin", "label": "Read the plugin execution model"},
                        {"href": "/support", "label": "See what support needs from you"},
                    ],
                },
                {
                    "eyebrow": "Installed buyer visibility",
                    "heading": "After protected activation, the bridge is designed to explain what it sees",
                    "paragraphs": [
                        (
                            "The Suite is not meant to disappear into a black box after installation. The protected bridge is designed to show domain binding, baseline evidence, readiness state, protected delivery state and the next safe gate inside WordPress admin."
                        ),
                        (
                            "That makes the product easier to trust commercially: the buyer can inspect what is active, what stays blocked and what still needs confirmation before broader optimization is even considered."
                        ),
                    ],
                    "bullets": [
                        "License, domain and scope stay readable after activation",
                        "Health signals, blockers and cutover gates stay visible",
                        "Rollback and validation stay first-class, not hidden internals",
                    ],
                    "links": [
                        {"href": "/plugin", "label": "See the plugin execution path"},
                        {"href": "/buy", "label": "See the public offer path"},
                    ],
                },
                {
                    "eyebrow": "Request readiness",
                    "heading": "What to prepare before requesting access or pilot review",
                    "paragraphs": [
                        (
                            "The portal is now ready to prepare a later access or pilot conversation, but not to approve or execute it on its own. "
                            "A good request starts with domain clarity, output ownership and rollback responsibility."
                        ),
                        (
                            "This improves conversion quality because vague requests are filtered into documentation and support clarification before any protected workflow is even considered."
                        ),
                    ],
                    "bullets": [
                        "Prepare the target domain and minimal desired scope",
                        "Prepare the current WordPress stack: theme, builder and SEO plugin",
                        "Prepare validation owner and rollback owner for later pilot review",
                    ],
                    "links": [
                        {"href": "/downloads", "label": "Review gated access preparation"},
                        {"href": "/support", "label": "Clarify scope with support"},
                    ],
                },
                {
                    "eyebrow": "Approval boundaries",
                    "heading": "What remains approval_required",
                    "paragraphs": [
                        (
                            "The portal can now qualify interest more clearly, but it still does not open the protected delivery path. "
                            "Every real plugin release, license activation, private download or customer execution step remains gated."
                        )
                    ],
                    "bullets": [
                        "Protected routes stay non-public",
                        "No open license API or anonymous production download path",
                        "observe_only remains the safe fallback when certainty is missing",
                    ],
                    "links": [{"href": "/security", "label": "See the full guardrail model"}],
                },
                {
                    "eyebrow": "Operator-configured portal fields",
                    "heading": "Portal-visible readiness can improve without opening protected workflows",
                    "paragraphs": [
                        (
                            "Support, commercial and access-readiness signals now come from a dedicated operator field layer. "
                            "That means the portal can become more complete over time without pretending that protected delivery is already public."
                        )
                    ],
                    "bullets": [
                        f"Support contact: {support_copy}",
                        f"Commercial inquiry state: {commercial_state_copy}",
                        f"Access request state: {access_state_copy}",
                        "Public monthly plans: Guardian Core Monthly for one exact licensed domain, Sovereign Enterprise Monthly for a commercially reviewed exact licensed multi-domain scope, Sovereign Critical Monthly for an individually approved exact licensed high-compliance scope",
                    ],
                    "links": [
                        {"href": "/buy", "label": "See the public monthly plans"},
                        {"href": "/support", "label": "See support readiness"},
                        {"href": "/downloads", "label": "See access-readiness guidance"},
                    ],
                },
            ],
            "comparison": {
                "heading": "Why this is not a generic SEO plugin stack",
                "rows": [
                    {
                        "topic": "Scope discipline",
                        "product": "Domain-bound licensing and explicitly allowed scopes",
                        "typical": "Sitewide effects often expand faster than documentation",
                    },
                    {
                        "topic": "Rollback readiness",
                        "product": "Rollback profiles, validation windows and abort criteria are first-class",
                        "typical": "Rollback planning is often implicit or manual-only",
                    },
                    {
                        "topic": "Protected operations",
                        "product": "Public portal and protected control plane are separated by design",
                        "typical": "Product pages and operator functions are too often mixed",
                    },
                    {
                        "topic": "Conflict awareness",
                        "product": "Theme, builder and SEO-plugin collisions are part of the execution model",
                        "typical": "Coexistence logic is often reactive and late",
                    },
                    {
                        "topic": "Buyer visibility",
                        "product": "Installed bridge keeps scope, health and next-gate signals readable",
                        "typical": "Buyers are often asked to trust invisible runtime state",
                    },
                ],
            },
            "faq": [
                {
                    "question": "Is the public portal the same as the operator console?",
                    "answer": (
                        "No. The public portal is a product and documentation surface. Operator, control-plane and customer execution routes remain protected."
                    ),
                },
                {
                    "question": "Is the WordPress plugin already offered as an open download?",
                    "answer": (
                        "No. Downloads remain gated. Open anonymous production delivery is intentionally not available."
                    ),
                },
                {
                    "question": "Does the product abruptly replace Rank Math?",
                    "answer": (
                        "No. Rank Math is treated as an active coexistence case until source ownership, validation and rollback are fully mapped."
                    ),
                },
                {
                    "question": "Can I already submit a live access request from the public portal?",
                    "answer": (
                        "Not through an active protected workflow. The portal prepares the request path and clarifies what must be ready before any later approval step."
                    ),
                },
            ],
            "final_cta": {
                "heading": "Move from product interest into a bounded public preflight",
                "body": (
                    "Use buy for the visible monthly plans, then move into licensing, downloads and support to clarify scope, fit and what still stays approval_required."
                ),
                "primary": {"href": "/buy", "label": "Open the buy page"},
                "secondary": {"href": "/support", "label": "Review support and inquiry paths"},
            },
        },
        "/features": {
            "title": f"WordPress SEO and Performance Features | {portal.product_name}",
            "description": (
                "Explore the feature set behind the WordPress SEO and performance optimization platform: "
                "plugin execution, control-plane validation, scoped licensing and rollback-aware delivery."
            ),
            "eyebrow": "Feature overview",
            "hero": "Feature layers for WordPress SEO, performance, release safety and scoped delivery.",
            "lede": (
                "The product combines observe-only intelligence, policy-aware planning and a future plugin execution plane that "
                "stays domain-bound, conflict-aware, explainable and rollback-ready."
            ),
            "trust_points": [
                "Control plane learns from reports, trends and rollback evidence",
                "Plugin MVP stays in safe_mode or observe_only by default",
                "Release, policy and rollback objects remain domain-scoped",
                "Installed bridge keeps buyer-visible state instead of hidden runtime assumptions",
            ],
            "primary_cta": {"href": "/docs", "label": "Read the architecture docs"},
            "secondary_cta": {"href": "/security", "label": "See the safety model"},
            "sections": [
                {
                    "eyebrow": "Observe and learn",
                    "heading": "Reference intelligence before execution",
                    "paragraphs": [
                        (
                            "The Hetzner control plane remains responsible for observing, learning, validating and planning. "
                            "It turns raw report data, historical trends and pilot evidence into safer execution decisions."
                        )
                    ],
                    "bullets": [
                        "Historical rollups for 1d, 7d, 30d and 365d",
                        "Read-only report harvesting and domain result summaries",
                        "Trend and doctrine checks before any future live action",
                    ],
                    "links": [{"href": "/docs", "label": "Use the docs entry point"}],
                },
                {
                    "eyebrow": "Plugin-first execution",
                    "heading": "Local WordPress execution with narrow scope and conflict checks",
                    "paragraphs": [
                        (
                            "The plugin path is the primary future way to improve metadata, heading structure, markup quality and "
                            "other on-page issues that belong close to the WordPress rendering layer."
                        )
                    ],
                    "bullets": [
                        "Homepage Meta Description pilot path",
                        "H1 consolidation and markup hygiene as later scoped modules",
                        "Conflict detection against themes, builders and SEO plugins",
                        "Installed buyer-readable insight surface after protected activation",
                    ],
                    "links": [{"href": "/plugin", "label": "Inspect the plugin path"}],
                },
                {
                    "eyebrow": "Release and rollback",
                    "heading": "Domain-bound delivery objects instead of vague global rollout",
                    "paragraphs": [
                        (
                            "Licenses, channels, manifests, policies and rollback profiles are modeled per domain. "
                            "That keeps product delivery traceable and avoids unclear multi-domain side effects."
                        )
                    ],
                    "bullets": [
                        "Stable, pilot and rollback channels",
                        "Policy narrowing instead of policy expansion",
                        "Rollback profiles linked to domain and scope",
                    ],
                    "links": [{"href": "/licensing", "label": "Review licensing and scope"}],
                },
            ],
            "comparison": {
                "heading": "Feature emphasis",
                "rows": [
                    {
                        "topic": "SEO structure",
                        "product": "Metadata, H1, markup and content ownership stay close to WordPress output",
                        "typical": "Edge-only fixes miss template and plugin root causes",
                    },
                    {
                        "topic": "Performance discipline",
                        "product": "Performance work is evaluated alongside scope, conflict risk and rollback cost",
                        "typical": "Performance tweaks are often treated as isolated wins",
                    },
                    {
                        "topic": "Domain governance",
                        "product": "Licensing, releases and policies stay domain-scoped",
                        "typical": "Shared logic can drift into accidental cross-domain effects",
                    },
                    {
                        "topic": "Explainability",
                        "product": "Installed state, blockers and next gates stay visible to the buyer",
                        "typical": "Optimization tools often hide operational state behind vague status labels",
                    },
                ],
            },
            "faq": [
                {
                    "question": "Why is the WordPress plugin the primary execution path?",
                    "answer": (
                        "Because the current highest-value opportunities are metadata, headings, HTML weight and markup quality, "
                        "which belong closest to WordPress rendering."
                    ),
                },
                {
                    "question": "Does the product already run live changes on customer sites?",
                    "answer": (
                        "No. The current product state remains controlled, local and approval-gated for any real external effect."
                    ),
                },
            ],
            "final_cta": {
                "heading": "Want the full model behind the features?",
                "body": "The docs, security and licensing sections explain how these features remain controlled and reversible.",
                "primary": {"href": "/security", "label": "Review validation and rollback"},
                "secondary": {"href": "/licensing", "label": "See scope and license boundaries"},
            },
        },
        "/security": {
            "title": f"Validation, Guardrails and Rollback | {portal.product_name}",
            "description": (
                "Learn how the platform protects WordPress SEO and performance changes through doctrine enforcement, "
                "route separation, validation windows and rollback-first discipline."
            ),
            "eyebrow": "Security and rollback",
            "hero": "Security, validation and rollback are product features, not afterthoughts.",
            "lede": (
                "The product portal can be public. Operator, customer and control-plane authority cannot. Every later live effect must pass "
                "doctrine, scope, validation and rollback checks before it is considered safe. The same doctrine favors explainability and server-owned recovery over blind automation."
            ),
            "trust_points": [
                "Public routes stay separated from protected routes",
                "observe_only is the default fallback when certainty is missing",
                "Rollback criteria are required before later live action",
                "Zero-trust validation beats hidden automation",
            ],
            "primary_cta": {"href": "/docs", "label": "Read the operating doctrine"},
            "secondary_cta": {"href": "/support", "label": "Check support and escalation entry"},
            "sections": [
                {
                    "eyebrow": "Guardrails",
                    "heading": "The doctrine limits autonomy to safe, validated and reversible behavior",
                    "paragraphs": [
                        (
                            "Autonomy is allowed only inside a defensive operating model. Protected routes stay closed, "
                            "external writes require approval, and undefined scope is treated as a reason to fall back, not to guess."
                        )
                    ],
                    "bullets": [
                        "No public operator or license endpoints",
                        "No unclear multi-domain action paths",
                        "No removal of rollback or validation requirements through licensing",
                        "No buyer-visible promise that outruns the actual guardrails",
                    ],
                },
                {
                    "eyebrow": "Validation",
                    "heading": "Before-state, after-state and neighboring signals must agree",
                    "paragraphs": [
                        (
                            "The system uses before-state evidence, primary metrics, neighboring signals, abort criteria and "
                            "observation windows to decide whether a later pilot is healthy or requires rollback."
                        ),
                        (
                            f"The current reference run already demonstrates the read-only baseline: status {status_code}, "
                            f"response {response_copy}, HTML {html_copy}, sitemap {sitemap_status}."
                        ),
                    ],
                    "bullets": [
                        "Immediate check plus 1d and 7d follow-up windows",
                        "Rollback required if primary metrics degrade or side effects grow",
                        "Learning engine records both wins and failed assumptions",
                        "Installed bridge keeps the evidence visible instead of burying it",
                    ],
                },
                {
                    "eyebrow": "Protected surface",
                    "heading": "What stays public and what must stay protected",
                    "paragraphs": [
                        (
                            "Public content may include product pages, gated download explanations, support entry and documentation entry pages. "
                            "Operator, customer, license and protected download paths remain blocked or non-public."
                        )
                    ],
                    "bullets": [
                        "Public: product pages, docs entry, support, robots, sitemap, health",
                        "Protected: operator, admin, control-plane, customer and private download routes",
                        "Local operator console stays separate and localhost-only",
                    ],
                },
            ],
            "faq": [
                {
                    "question": "Can a license override security limits or rollback rules?",
                    "answer": "No. Licensing can enable eligibility, but it cannot remove doctrine, validation or rollback guardrails.",
                },
                {
                    "question": "What happens when source ownership or scope is unclear?",
                    "answer": "The system falls back to observe_only, blueprint_ready or approval_required instead of applying uncertain changes.",
                },
                {
                    "question": "Are protected routes being opened by this public portal?",
                    "answer": "No. Route separation remains strict and protected prefixes stay blocked.",
                },
            ],
            "final_cta": {
                "heading": "Security should accelerate trust, not slow product clarity",
                "body": "Continue into the plugin model to see how safe_mode, conflict checks and coexistence logic work together.",
                "primary": {"href": "/plugin", "label": "Open the plugin page"},
                "secondary": {"href": "/downloads", "label": "Review gated access"},
            },
        },
        "/plugin": {
            "title": f"WordPress Plugin Execution Model | {portal.product_name}",
            "description": (
                "See how the doctrine-enforced WordPress plugin path handles homepage metadata, safe_mode, conflict detection, "
                "coexistence with SEO plugins and later domain-bound execution."
            ),
            "eyebrow": "Plugin-first execution",
            "hero": "A WordPress plugin path that is narrow, conflict-aware and built for controlled rollout.",
            "lede": (
                "The plugin is the primary future execution plane. It is designed to stay local to the licensed domain, "
                "to detect ownership conflicts early, to avoid duplicate or unclear output and to keep its own state explainable after activation."
            ),
            "trust_points": [
                "Default posture remains safe_mode or observe_only",
                "Homepage Meta Description is the first planned scoped pilot",
                "Rank Math remains active until a validated replacement path exists",
                "Installed admin surface shows scope, health, delivery and cutover state",
            ],
            "primary_cta": {"href": "/licensing", "label": "See domain and scope binding"},
            "secondary_cta": {"href": "/features", "label": "Review the broader product feature set"},
            "sections": [
                {
                    "eyebrow": "Execution model",
                    "heading": "Local execution on the licensed WordPress domain",
                    "paragraphs": [
                        (
                            "The plugin is intended to run on the WordPress site itself, not as a remote blanket editor. "
                            "That keeps output logic close to the source, which matters for metadata ownership, heading structure and markup cleanup."
                        )
                    ],
                    "bullets": [
                        "Bound-domain checks before any active module can run",
                        "Allowed scopes keep execution narrow and auditable",
                        "Rollback hooks and validation status stay part of the module lifecycle",
                        "Buyer-readable installed insights stay available after activation",
                    ],
                },
                {
                    "eyebrow": "Pilot 1",
                    "heading": "Homepage Meta Description is the first planned plugin pilot",
                    "paragraphs": [
                        (
                            "The first planned plugin pilot focuses on the homepage Meta Description. It stays intentionally small: "
                            "homepage scope only, single signal family, measurable outcome, documented fallback."
                        ),
                        (
                            f"The current reference description is '{reference.get('meta_description', 'source not yet confirmed')}', "
                            "which confirms a clear optimization opportunity without justifying abrupt source replacement."
                        ),
                    ],
                    "bullets": [
                        "No automatic title, canonical or robots takeover",
                        "No sitewide expansion from a homepage-only approval",
                        "No activation until source ownership is mapped and approved",
                    ],
                    "links": [{"href": "/security", "label": "Review validation and rollback constraints"}],
                },
                {
                    "eyebrow": "Coexistence",
                    "heading": "Rank Math and other SEO plugins are handled as coexistence cases",
                    "paragraphs": [
                        (
                            "The product does not assume exclusive ownership over metadata. Existing theme, builder and SEO-plugin behavior must be mapped first. "
                            "Only then can a safer replacement or coexistence path be chosen."
                        )
                    ],
                    "bullets": [
                        "No double meta output",
                        "No abrupt Rank Math removal",
                        "Conflict detection must keep modules disabled when ownership is unclear",
                        "Source mapping must be explicit before reversible changes are prepared",
                    ],
                },
            ],
            "comparison": {
                "heading": "Plugin path versus edge-only work",
                "rows": [
                    {
                        "topic": "Metadata ownership",
                        "product": "Handled near WordPress source and plugin filters",
                        "typical": "Edge rules cannot reliably fix ownership confusion",
                    },
                    {
                        "topic": "Structure fixes",
                        "product": "H1, markup and output modules can be scoped per template or page type",
                        "typical": "Edge layers cannot see enough template intent",
                    },
                    {
                        "topic": "Conflict detection",
                        "product": "Theme, builder and SEO-plugin overlap can be inspected locally",
                        "typical": "External layers usually infer conflicts too late",
                    },
                ],
            },
            "faq": [
                {
                    "question": "Does the plugin apply changes sitewide by default?",
                    "answer": "No. The target model is narrow scope first, with explicit allowed scopes and rollback readiness.",
                },
                {
                    "question": "Why keep Rank Math in place for now?",
                    "answer": "Because source ownership must be mapped and replacement logic validated before a safe migration path exists.",
                },
            ],
            "final_cta": {
                "heading": "Plugin-first does not mean plugin-uncontrolled",
                "body": "Licensing, scope binding and control-plane validation keep the future plugin path disciplined.",
                "primary": {"href": "/licensing", "label": "Review licensing rules"},
                "secondary": {"href": "/docs", "label": "Open the documentation entry"},
            },
        },
        "/licensing": {
            "title": f"Plugin Licensing, Scope Control and Access Readiness | {portal.product_name}",
            "description": (
                "Understand how plugin licensing, domain-bound scopes, commercial placeholders and protected delivery "
                "keep the WordPress optimization product controlled, request-ready and auditable."
            ),
            "eyebrow": "Licensing and scope",
            "hero": "Licenses unlock bounded capability. They never override doctrine or safety limits.",
            "lede": (
                "The licensing layer exists to keep domains, scopes, releases and rollback profiles separated. "
                "It is not a shortcut around validation, protected delivery, commercial honesty or conflict logic. It is also the basis for later buyer-readable scope and delivery visibility inside the installed bridge."
            ),
            "trust_points": [
                "Each public plan maps to an explicit exact licensed scope",
                "Allowed scopes stay explicit and narrow",
                "Channels and rollback profiles remain domain-bound",
                "Commercial placeholders stay honest until confirmed",
            ],
            "primary_cta": {"href": "/support", "label": "Prepare a commercial inquiry"},
            "secondary_cta": {"href": "/downloads", "label": "Review access request readiness"},
            "readiness_summary": readiness_summary,
            "sections": [
                {
                    "eyebrow": "Domain binding",
                    "heading": "No vague or open-ended domain entitlement",
                    "paragraphs": [
                        (
                            "Each license object is intended to bind to explicit exact licensed domains and an explicit scope set. "
                            "That prevents accidental cross-domain effects and keeps future rollout decisions explainable even when the selected plan covers more than one domain."
                        )
                    ],
                    "bullets": [
                        "Guardian Core Monthly: one exact licensed domain",
                        "Sovereign Enterprise Monthly: commercially reviewed exact licensed multi-domain scope",
                        "Sovereign Critical Monthly: individually approved exact licensed high-compliance scope",
                        "Wildcard or ambiguous domain sharing is out of scope",
                        "Reference site and customer sites stay separated",
                    ],
                },
                {
                    "eyebrow": "Who this licensing model is for",
                    "heading": "Best suited for operators who can define domain, scope and ownership clearly",
                    "paragraphs": [
                        (
                            "A later license conversation makes sense when the target domain is known, the WordPress stack can be named and "
                            "the requested scope can stay narrow enough for validation and rollback."
                        )
                    ],
                    "bullets": [
                        "Homepage-only pilots remain possible",
                        "Template or module ownership should be explainable",
                        "Approval remains required for real execution",
                    ],
                    "links": [
                        {"href": "/plugin", "label": "See the plugin execution constraints"},
                        {"href": "/support", "label": "Check what support needs from you"},
                    ],
                },
                {
                    "eyebrow": "Commercial preparation",
                    "heading": "Pricing tiers are visible, but commercial execution still stays protected",
                    "paragraphs": [
                        (
                            "The portal now shows the public monthly plans directly: Guardian Core Monthly EUR 2,500.00, Sovereign Enterprise Monthly EUR 9,500.00 and Sovereign Critical Monthly EUR 25,000.00. "
                            "That does not open checkout, auto-issuance, protected downloads or customer execution."
                        )
                    ],
                    "bullets": [
                        f"Pricing model: {pricing_state_copy}",
                        f"{commercial_label_copy}: {commercial_state_copy}",
                        f"Quoted package tiers: {package_state_copy}",
                        "Installed buyer visibility still stays separate from public checkout or delivery",
                    ],
                },
                {
                    "eyebrow": "What remains approval_required",
                    "heading": "No public licensing step can bypass the protected execution layer",
                    "paragraphs": [
                        (
                            "Even a future commercial or licensing conversation does not create automatic delivery rights. "
                            "Actual entitlements, domain activation, policy delivery and private downloads stay protected."
                        )
                    ],
                    "bullets": [
                        "Final customer entitlements: approval_required",
                        "Protected release and policy delivery: approval_required",
                        "Any real domain activation: approval_required",
                    ],
                    "links": [
                        {"href": "/downloads", "label": "Review protected delivery limits"},
                        {"href": "/security", "label": "See why approval stays mandatory"},
                    ],
                },
                {
                    "eyebrow": "What is not publicly available",
                    "heading": "Visible pricing does not imply checkout or auto-fulfillment",
                    "paragraphs": [
                        (
                            "This page can now show public pricing tiers and clearer commercial boundaries, but it still does not include self-service purchase flows, activation buttons or domain entitlement issuance."
                        )
                    ],
                    "bullets": [
                        "No public checkout or checkout link",
                        "No automatic license issuance",
                        "No hidden fulfillment path behind the CTA layer",
                    ],
                },
            ],
            "faq": [
                {
                    "question": "Can one license safely control multiple unrelated customer domains?",
                    "answer": "No. The platform is modeled around domain-bound isolation and explicit scope separation.",
                },
                {
                    "question": "Does licensing automatically publish plugin downloads?",
                    "answer": "No. Download delivery remains gated by license, entitlement, channel and protected access rules.",
                },
                {
                    "question": "Does this page already include public pricing or a commercial checkout flow?",
                    "answer": licensing_pricing_faq,
                },
            ],
            "final_cta": {
                "heading": "Use licensing to qualify fit before any later protected step",
                "body": "If the domain, scope and ownership picture is clear, continue to downloads and support to prepare the request path without overpromising delivery.",
                "primary": {"href": "/downloads", "label": "Go to access-request readiness"},
                "secondary": {"href": "/support", "label": "Open support and inquiry guidance"},
            },
        },
        "/docs": {
            "title": f"Architecture, Docs and Implementation Paths | {portal.product_name}",
            "description": (
                "Use the documentation entry point for the WordPress SEO and performance platform: architecture, plugin execution, "
                "control plane, licensing, validation and rollback."
            ),
            "eyebrow": "Documentation entry",
            "hero": "Start with architecture, doctrine and rollout logic before you request a pilot.",
            "lede": (
                "The docs layer explains how the public portal, protected control plane and future plugin execution fit together, "
                "so product evaluation starts with clarity instead of guesswork. It also explains why the installed bridge stays observable and buyer-readable before broader execution is allowed."
            ),
            "trust_points": [
                "Architecture, plugin and licensing docs are already mapped",
                "Validation and rollback doctrine stay visible at every layer",
                "Public docs do not expose protected operator authority",
                "Installed buyer visibility is documented as part of the product model",
            ],
            "primary_cta": {"href": "/security", "label": "Read the guardrail summary"},
            "secondary_cta": {"href": "/plugin", "label": "Inspect the plugin path"},
            "sections": [
                {
                    "eyebrow": "Core reading path",
                    "heading": "What to read first",
                    "paragraphs": [
                        (
                            "A good reading order starts with the public portal overview, continues through security and licensing, "
                            "then moves into plugin execution and rollback-aware delivery."
                        )
                    ],
                    "bullets": [
                        "Home for product positioning and differentiation",
                        "Security for doctrine, validation and rollback",
                        "Plugin and licensing for execution constraints",
                    ],
                },
                {
                    "eyebrow": "Reference evidence",
                    "heading": "Documentation stays grounded in the reference system",
                    "paragraphs": [
                        (
                            f"The current reference site remains {reference_domain}. Latest safe signals include homepage title "
                            f"'{reference.get('homepage_title', 'source not yet confirmed')}', canonical '{reference.get('canonical', 'source not yet confirmed')}', "
                            f"and robots '{reference.get('robots_meta', 'source not yet confirmed')}'."
                        )
                    ],
                    "bullets": [
                        "Reference evidence is informational, not a public operator feed",
                        "Current mode remains observe_only for real effects",
                        "Public docs remain separated from protected console functionality",
                    ],
                },
                {
                    "eyebrow": "Current limits",
                    "heading": "What the docs do not promise yet",
                    "paragraphs": [
                        (
                            "The docs intentionally avoid claiming open downloads, public license APIs, live customer onboarding or "
                            "instant plugin replacement paths when those capabilities remain approval-gated."
                        )
                    ],
                    "bullets": [
                        "No open customer dashboard",
                        "No public operator console",
                        "No commercial or legal promise beyond documented current state",
                    ],
                },
            ],
            "faq": [
                {
                    "question": "Are these docs the same as the protected internal operator documentation?",
                    "answer": "No. This is the public documentation entry layer. Protected operator materials stay separate.",
                },
                {
                    "question": "Can the docs be used to access plugin downloads?",
                    "answer": "They can explain the gating model, but they do not expose open production downloads.",
                },
            ],
            "final_cta": {
                "heading": "Use the docs to understand the product before any rollout conversation",
                "body": "The portal is strongest when architecture, licensing and rollback expectations are clear from the start.",
                "primary": {"href": "/licensing", "label": "Review domain binding"},
                "secondary": {"href": "/support", "label": "See support placeholders"},
            },
        },
        "/downloads": {
            "title": f"Gated Plugin Access Requests and Protected Downloads | {portal.product_name}",
            "description": (
                "Learn how gated plugin access requests, protected downloads, release channels and domain entitlement "
                "fit the WordPress optimization product without opening public delivery."
            ),
            "eyebrow": "Gated access only",
            "hero": "No open anonymous production download. Access is intentionally gated.",
            "lede": (
                "The portal now prepares a clearer access-request path, but it still does not expose a public plugin package, license API, account login or customer execution channel. "
                "What it does offer is a clearer explanation of how protected delivery and installed buyer visibility fit together."
            ),
            "trust_points": [
                f"Current download gate state: {portal.download_gate_state}",
                "Protected delivery stays separate from public portal pages",
                "Entitlement requires domain, license and channel fit",
                "Request-ready without opening a public download path",
            ],
            "primary_cta": {"href": "/support", "label": "Prepare support-side access context"},
            "secondary_cta": {"href": "/licensing", "label": "Check license and scope fit"},
            "readiness_summary": readiness_summary,
            "sections": [
                {
                    "eyebrow": "Current state",
                    "heading": "Why downloads remain gated",
                    "paragraphs": [
                        (
                            "Open anonymous delivery would bypass the domain, scope, channel and rollback checks the product is built around. "
                            "That would weaken the doctrine instead of reinforcing it."
                        )
                    ],
                    "bullets": [
                        "No open plugin ZIP link",
                        "No public private-download route",
                        "No public release or manifest API",
                    ],
                },
                {
                    "eyebrow": "Access-request readiness",
                    "heading": "What to prepare before requesting access",
                    "paragraphs": [
                        (
                            "A useful later access request starts before any protected workflow exists. "
                            "The portal now explains what support and licensing logic will need from the requester before any real entitlement can be reviewed."
                        )
                    ],
                    "bullets": [
                        "Target domain and expected environment role",
                        "Current WordPress stack: theme, builder and SEO plugin inventory",
                        "Requested scope, validation owner and rollback owner",
                    ],
                    "links": [
                        {"href": "/support", "label": "See what support needs from you"},
                        {"href": "/plugin", "label": "Review plugin execution constraints"},
                    ],
                },
                {
                    "eyebrow": "Protected delivery model",
                    "heading": "Stable, pilot and rollback channels remain domain-bound and protected",
                    "paragraphs": [
                        (
                            "Later access will depend on license state, entitlement, release channel fit and protected delivery. "
                            "Stable, pilot and rollback artifacts are designed to remain tied to the licensed domain context."
                        )
                    ],
                    "bullets": [
                        "Pilot channel for narrow testing",
                        "Stable channel for validated releases",
                        "Rollback channel for recovery, not feature expansion",
                        "Installed bridge can stay visible without exposing public delivery",
                    ],
                },
                {
                    "eyebrow": "What is not publicly available",
                    "heading": "Request-ready does not mean open delivery",
                    "paragraphs": [
                        (
                            "The portal can now qualify interest better, but it still does not expose a live request form, a customer login, "
                            "a public package URL or a release activation workflow."
                        )
                    ],
                    "bullets": [
                        f"Access request workflow: {access_state_copy}",
                        f"Customer authentication model: {SOURCE_NOT_YET_CONFIRMED}",
                        f"Protected fulfillment path: {APPROVAL_REQUIRED}",
                        "Public private-download route: not available",
                    ],
                },
                {
                    "eyebrow": "Operator-configured request state",
                    "heading": "The portal can show request readiness without pretending to process requests",
                    "paragraphs": [
                        (
                            "The readiness layer is now configuration-driven. Operators can later populate visible request context, "
                            "but the portal still cannot submit, approve or fulfill anything by itself."
                        )
                    ],
                    "bullets": [
                        f"Commercial inquiry label: {commercial_label_copy}",
                        f"Commercial inquiry state: {commercial_state_copy}",
                        f"Download readiness: {operator.download_readiness_state}",
                    ],
                },
            ],
            "faq": [
                {
                    "question": "Can I download the plugin directly from this page?",
                    "answer": "No. This page is informational. Production downloads remain gated and protected.",
                },
                {
                    "question": "Will public download access ever bypass domain or scope checks?",
                    "answer": "No. Domain binding, entitlement, scope control and protected delivery remain core constraints.",
                },
                {
                    "question": "Can I submit a real access request form from this page today?",
                    "answer": "No. The page is request-ready in content only. Live request submission and fulfillment remain approval_required.",
                },
            ],
            "final_cta": {
                "heading": "Use this page to prepare access context, not to bypass protected delivery",
                "body": "The next useful step is support-side clarification plus license-fit review. The actual download path stays non-public.",
                "primary": {"href": "/support", "label": "Open support and inquiry guidance"},
                "secondary": {"href": "/licensing", "label": "Read licensing details"},
            },
        },
        "/support": {
            "title": f"Support, Scope Clarification and Commercial Inquiry | {portal.product_name}",
            "description": (
                "Support, technical scope clarification and commercial inquiry entry point for the WordPress SEO and performance optimization platform, "
                "with clear limits around protected operations, gated downloads and operator-input placeholders."
            ),
            "eyebrow": "Support and contact",
            "hero": "Support can be public. Protected operator authority cannot.",
            "lede": (
                "This page is the public entry for support, commercial inquiry preparation and technical scope clarification around the portal, "
                "the plugin path, licensing boundaries and documentation. It does not expose protected operator or customer actions, but it does explain the buyer-visible model the installed bridge is designed to expose."
            ),
            "trust_points": [
                "Support entry is public and informational",
                "Operator and customer execution surfaces remain protected",
                "Commercial and contact details stay explicit when not yet confirmed",
                "Request preparation is allowed; protected fulfillment is not",
            ],
            "primary_cta": {"href": "/downloads", "label": "Prepare access context"},
            "secondary_cta": {"href": "/docs", "label": "Start with the docs"},
            "readiness_summary": readiness_summary,
            "sections": [
                {
                    "eyebrow": "Support lanes",
                    "heading": "Support, commercial inquiry and technical scope clarification stay separate",
                    "paragraphs": [
                        (
                            "The support surface is now clearer about the kinds of requests it is preparing for: documentation guidance, "
                            "technical scope clarification and later commercial inquiry preparation."
                        ),
                        (
                            "What it still does not do is expose a live support desk, login flow, private download service or operator-side control action."
                        ),
                    ],
                    "bullets": [
                        "Technical scope clarification: public and informational",
                        "Commercial inquiry preparation: public but placeholder-only",
                        "Protected execution or fulfillment: approval_required",
                        f"Public contact page: {legal_identity['support_email']}",
                    ],
                },
                {
                    "eyebrow": "Current contact state",
                    "heading": "Operator-contact placeholders remain explicit",
                    "paragraphs": [
                        (support_contact_paragraph),
                        (f"Current support contact field: {support_copy}."),
                    ],
                    "bullets": [
                        f"Support email: {support_email_copy}",
                        f"{commercial_label_copy}: {commercial_state_copy}",
                        f"Public issue intake flow: {SOURCE_NOT_YET_CONFIRMED}",
                    ],
                },
                {
                    "eyebrow": "Request readiness",
                    "heading": "What support needs from you",
                    "paragraphs": [
                        (
                            "Support is most useful when it helps clarify domain scope, source ownership, plugin coexistence, "
                            "commercial fit and validation expectations before any later change request."
                        )
                    ],
                    "bullets": [
                        "Which WordPress domain is in scope",
                        "Which theme, builder and SEO plugin are active",
                        "Which business or operational goal is driving the request",
                        "Which rollback owner and validation owner are assigned",
                        "Which buyer-visible installed signals should remain readable after activation",
                    ],
                    "links": [
                        {"href": "/licensing", "label": "Check license and scope boundaries"},
                        {"href": "/downloads", "label": "Review access-request readiness"},
                        {"href": "/contact", "label": "Open public contact details"},
                    ],
                },
                {
                    "eyebrow": "What is not publicly available",
                    "heading": "This page remains informational and does not open protected functions",
                    "paragraphs": [
                        (
                            "This support entry does not act as a login page, a license issuance page, a private download endpoint or "
                            "a customer execution dashboard. Those paths remain protected and approval-gated."
                        )
                    ],
                    "bullets": [
                        "No login flow",
                        "No customer dashboard",
                        "No live operator action path",
                    ],
                },
                {
                    "eyebrow": "Support readiness",
                    "heading": "Support visibility can improve through config without changing the protection model",
                    "paragraphs": [
                        (
                            "The support surface now reads operator-configured visibility fields. That allows cleaner public support guidance "
                            "later, while protected delivery, activation and customer actions remain out of scope."
                        )
                    ],
                    "bullets": [
                        f"Support readiness: {operator.support_readiness_state}",
                        f"Commercial readiness: {operator.commercial_readiness_state}",
                        f"Access readiness: {access_state_copy}",
                    ],
                },
            ],
            "faq": [
                {
                    "question": "Can I request immediate live changes through this support page?",
                    "answer": "No. Support can guide scope and documentation, but real changes remain approval-gated and protected.",
                },
                {
                    "question": "Why does the page still show operator input required?",
                    "answer": "Because unconfirmed contact or commercial details are intentionally not invented or implied.",
                },
                {
                    "question": "Can support activate a license or send a private package from this page?",
                    "answer": "No. This page prepares inquiry and scope clarification only. Any real activation or fulfillment remains protected and approval_required.",
                },
            ],
            "final_cta": {
                "heading": "Use support to qualify fit before any protected workflow exists",
                "body": "Clarify domain scope, plugin ownership, commercial readiness and rollback responsibility first. Protected execution stays separate.",
                "primary": {"href": "/licensing", "label": "Check licensing boundaries"},
                "secondary": {"href": "/plugin", "label": "Review the plugin pilot path"},
            },
        },
    }
    pages.update(_build_audience_pages(portal, snapshot))
    pages.update(_build_legal_pages(portal))
    _apply_related_pages(pages)
    return pages


def _escape(text: Any) -> str:
    return html.escape(str(text))


def _page_label(portal: PublicPortalConfig, path: str) -> str:
    path = LEGAL_ROUTE_ALIASES.get(path, path)
    if path in NAV_LABELS:
        return NAV_LABELS[path]
    for item in portal.legal_fields.get("footer_nav", []):
        if item.get("href") == path:
            return str(item.get("label", "Page"))
    return "Page"


def _render_nav(path: str) -> str:
    items = []
    for route, label in PUBLIC_NAV:
        classes = "nav-link active" if route == path else "nav-link"
        items.append(f'<a href="{_escape(route)}" class="{classes}">{_escape(label)}</a>')
    return "".join(items)


def _translation_href(path: str, language: str) -> str:
    if language == "en":
        return path
    query = urlencode({"lang": language})
    return f"{path}?{query}" if path != "/" else f"/?{query}"


def _render_translation_switcher(path: str, translation_state: dict[str, Any]) -> str:
    links = []
    current_language = translation_state.get("requested_language", "en")
    for language in translation_state.get("supported_languages", []):
        classes = "translation-link active" if language == current_language else "translation-link"
        label = LANGUAGE_LABELS.get(language, language.upper())
        links.append(
            f'<a class="{classes}" href="{_escape(_translation_href(path, language))}" hreflang="{_escape(language)}">{_escape(label)}</a>'
        )
    if not links:
        return ""
    return (
        '<div class="translation-switcher" aria-label="Language switcher">'
        '<span class="translation-label">Language</span>'
        f'{"".join(links)}'
        "</div>"
    )


def _render_translation_banner(translation_state: dict[str, Any]) -> str:
    note = str(translation_state.get("note", "")).strip()
    if note == "":
        return ""
    tone = " translation-banner warning" if not translation_state.get("machine_translation_applied") else " translation-banner"
    return (
        f'<section class="{tone.strip()}">'
        '<div class="section-eyebrow">Language</div>'
        f"<p>{_escape(note)}</p>"
        "</section>"
    )


def _og_locale_for_language(language: str) -> str:
    return {
        "de": "de_DE",
        "fr": "fr_FR",
        "es": "es_ES",
        "it": "it_IT",
        "pt": "pt_PT",
        "nl": "nl_NL",
    }.get(language, "en_US")


def _render_breadcrumbs(portal: PublicPortalConfig, path: str) -> str:
    path = LEGAL_ROUTE_ALIASES.get(path, path)
    if path == "/":
        return ""
    label = _page_label(portal, path)
    return (
        '<nav class="breadcrumbs" aria-label="Breadcrumbs">'
        f'<a href="{_escape(_canonical_url(portal, "/"))}">Home</a>'
        '<span>/</span>'
        f"<span>{_escape(label)}</span>"
        "</nav>"
    )


def _render_link_list(links: list[dict[str, str]]) -> str:
    if not links:
        return ""
    items = "".join(
        f'<a class="text-link" href="{_escape(link["href"])}">{_escape(link["label"])}</a>'
        for link in links
    )
    return f'<div class="link-row">{items}</div>'


def _render_section(section: dict[str, Any]) -> str:
    paragraphs = "".join(f"<p>{_escape(paragraph)}</p>" for paragraph in section.get("paragraphs", []))
    bullets = section.get("bullets", [])
    bullet_html = ""
    if bullets:
        bullet_html = '<ul class="bullet-list">' + "".join(f"<li>{_escape(item)}</li>" for item in bullets) + "</ul>"
    links = _render_link_list(section.get("links", []))
    eyebrow = section.get("eyebrow")
    eyebrow_html = f'<div class="section-eyebrow">{_escape(eyebrow)}</div>' if eyebrow else ""
    return (
        '<section class="content-card">'
        f"{eyebrow_html}"
        f"<h2>{_escape(section['heading'])}</h2>"
        f"{paragraphs}"
        f"{bullet_html}"
        f"{links}"
        "</section>"
    )


def _render_metric_grid(snapshot: dict[str, Any]) -> str:
    cards = "".join(
        (
            '<article class="metric-card">'
            f"<span>{_escape(item['label'])}</span>"
            f"<strong>{_escape(item['value'])}</strong>"
            "</article>"
        )
        for item in snapshot.get("reference_metrics", [])
    )
    return f'<section class="metric-grid" aria-label="Reference metrics">{cards}</section>'


def _render_sales_ribbon(portal: PublicPortalConfig, snapshot: dict[str, Any]) -> str:
    operator = portal.operator_fields
    pills = [
        "Exact licensed scope",
        "Visible monthly plans",
        "Protected activation only",
        "Buyer-readable installed runtime",
        "Validation and rollback first",
    ]
    pill_html = "".join(f'<span class="sales-pill">{_escape(item)}</span>' for item in pills)
    return (
        '<section class="sales-ribbon">'
        '<div class="sales-ribbon-copy">'
        '<div class="sales-ribbon-kicker">Modern sales platform</div>'
        "<h2>Premium WordPress SEO and performance growth platform with exact licensed scope, visible pricing and protected activation.</h2>"
        "<p>Guardian Core starts at EUR 2,500.00 / month, Sovereign Enterprise scales into reviewed multi-domain environments and Sovereign Critical covers individually approved high-compliance growth operations.</p>"
        f"<p>Commercial path: {_escape(operator.commercial_inquiry_state)}. Support path: {_escape(operator.support_contact)}.</p>"
        "</div>"
        f'<div class="sales-ribbon-pills">{pill_html}</div>'
        "</section>"
    )


def _render_conversion_panel(
    portal: PublicPortalConfig,
    page: dict[str, Any],
    snapshot: dict[str, Any],
) -> str:
    support_email = portal.operator_fields.support_email
    plan_cards = _public_plan_pricing_cards()
    highlights = (
        {"label": "From", "value": plan_cards[0]["price_line"]},
        {"label": "Visible plans", "value": str(len(plan_cards))},
        {"label": "Delivery", "value": "Protected only"},
        {"label": "Runtime", "value": "Buyer-readable"},
    )
    metrics_html = "".join(
        (
            '<article class="conversion-metric">'
            f"<span>{_escape(item['label'])}</span>"
            f"<strong>{_escape(item['value'])}</strong>"
            "</article>"
        )
        for item in highlights
    )
    plan_list = "".join(
        (
            "<li>"
            f"<strong>{_escape(plan['title'])}</strong>"
            f"<span>{_escape(plan['scope_summary'])}</span>"
            "</li>"
        )
        for plan in PUBLIC_MONTHLY_PLANS
    )
    secondary_href = page["secondary_cta"]["href"] if page["secondary_cta"]["href"] != page["primary_cta"]["href"] else "/support"
    secondary_label = page["secondary_cta"]["label"] if page["secondary_cta"]["href"] != page["primary_cta"]["href"] else "Talk to support"
    return (
        '<aside class="conversion-panel">'
        '<div class="conversion-kicker">Commercial preflight</div>'
        "<h2>Move from public visibility to protected activation without fake self-serve promises.</h2>"
        "<p>Every page now sells the same disciplined commercial model: visible offer, explicit scope, safer rollout, premium positioning and operator-governed activation.</p>"
        f'<div class="conversion-metrics">{metrics_html}</div>'
        '<ul class="conversion-list">'
        f"{plan_list}"
        f"<li><strong>Support email</strong><span>{_escape(support_email)}</span></li>"
        f"<li><strong>Current portal gate</strong><span>{_escape(snapshot['download_gate_state'])}</span></li>"
        "</ul>"
        '<div class="cta-row">'
        f'<a class="button primary" href="{_escape(page["primary_cta"]["href"])}">{_escape(page["primary_cta"]["label"])}</a>'
        f'<a class="button secondary" href="{_escape(secondary_href)}">{_escape(secondary_label)}</a>'
        "</div>"
        "</aside>"
    )


def _render_sales_offer_deck(path: str) -> str:
    cards = "".join(
        (
            '<article class="offer-card">'
            f'<div class="offer-kicker">{_escape(plan["badge"])}</div>'
            f"<h3>{_escape(plan['title'])}</h3>"
            f'<p class="offer-price">{_escape(plan["price_line"])}</p>'
            f'<p class="offer-scope">{_escape(plan["scope_line"])}</p>'
            f"<p>{_escape(plan['included_line'])}</p>"
            '<div class="link-row">'
            f'<a class="text-link" href="/buy">See plan details</a>'
            f'<a class="text-link" href="{"/support" if plan["title"] != "Guardian Core Monthly" else "/licensing"}">'
            f'{"Clarify commercial fit" if plan["title"] != "Guardian Core Monthly" else "Review scope fit"}'
            "</a>"
            "</div>"
            "</article>"
        )
        for plan in PUBLIC_MONTHLY_PLANS
    )
    path_copy = {
        "/": "All pages now sell the same premium model: visible offer, exact licensed scope and protected activation instead of anonymous self-serve delivery.",
        "/buy": "This page closes the commercial gap: pricing is visible, scope is explicit and activation remains premium, reviewed and protected.",
    }.get(
        path,
        "The offer deck stays visible across the portal so buyers can move from education into commercial fit without losing clarity."
    )
    return (
        '<section class="offer-deck">'
        '<div class="section-eyebrow">Public offer deck</div>'
        "<h2>A high-modern sales surface for premium WordPress optimization.</h2>"
        f"<p>{_escape(path_copy)}</p>"
        f'<div class="offer-grid">{cards}</div>'
        "</section>"
    )


def _render_sales_journey() -> str:
    steps = (
        ("01", "Frame the domain scope", "Name the exact licensed domain or explicitly reviewed domain set before any live handoff starts."),
        ("02", "Choose the commercial tier", "Map the buyer to Guardian Core, Sovereign Enterprise or Sovereign Critical with visible pricing and honest scope."),
        ("03", "Validate stack and ownership", "Confirm WordPress stack, SEO ownership, rollback ownership and activation readiness."),
        ("04", "Protected activation only", "Delivery, activation and runtime execution stay governed, traceable and reversible."),
    )
    cards = "".join(
        (
            '<article class="journey-step">'
            f'<div class="journey-index">{_escape(item[0])}</div>'
            f"<h3>{_escape(item[1])}</h3>"
            f"<p>{_escape(item[2])}</p>"
            "</article>"
        )
        for item in steps
    )
    return (
        '<section class="journey-band">'
        '<div class="section-eyebrow">Conversion path</div>'
        "<h2>Turn interest into a governed buying decision.</h2>"
        "<p>The portal now behaves like a premium commercial system: persuasive, modern and conversion-oriented, while still keeping every protected execution step behind validation and approval.</p>"
        f'<div class="journey-grid">{cards}</div>'
        "</section>"
    )


def _render_readiness_summary(items: list[dict[str, str]]) -> str:
    if not items:
        return ""
    cards = "".join(
        (
            '<article class="readiness-card">'
            f"<span>{_escape(item['label'])}</span>"
            f"<strong>{_escape(item['state'])}</strong>"
            f"<p>{_escape(item['detail'])}</p>"
            "</article>"
        )
        for item in items
    )
    return (
        '<section class="readiness-block" aria-label="Portal readiness summary">'
        '<div class="section-eyebrow">Readiness summary</div>'
        "<h2>Portal-visible readiness without protected execution</h2>"
        f'<div class="readiness-grid">{cards}</div>'
        "</section>"
    )


def _render_pricing_tiers(items: list[dict[str, Any]]) -> str:
    if not items:
        return ""
    cards = "".join(
        (
            '<article class="pricing-card">'
            f'<div class="pricing-badge">{_escape(item.get("badge", "Public monthly plan"))}</div>'
            f"<h3>{_escape(item['title'])}</h3>"
            f'<p class="pricing-line">{_escape(item["price_line"])}</p>'
            f'<p class="pricing-scope">{_escape(item["scope_line"])}</p>'
            f'<p class="pricing-included">{_escape(item["included_line"])}</p>'
            f"<p>{_escape(item['copy'])}</p>"
            f"{_render_link_list(item.get('links', []))}"
            "</article>"
        )
        for item in items
    )
    return (
        '<section class="pricing-block">'
        '<div class="section-eyebrow">Compare the public monthly plans</div>'
        "<h2>Guardian Core, Sovereign Enterprise and Sovereign Critical stay visible, bounded and protected.</h2>"
        "<p>Each public plan keeps pricing, exact licensed domain scope, documentation and protected access expectations visible while activation, delivery and execution remain gated.</p>"
        f'<div class="pricing-grid">{cards}</div>'
        "</section>"
    )


def _render_comparison(comparison: dict[str, Any] | None) -> str:
    if not comparison:
        return ""
    rows = "".join(
        (
            "<tr>"
            f"<th>{_escape(row['topic'])}</th>"
            f"<td>{_escape(row['product'])}</td>"
            f"<td>{_escape(row['typical'])}</td>"
            "</tr>"
        )
        for row in comparison.get("rows", [])
    )
    return (
        '<section class="comparison-block">'
        '<div class="section-eyebrow">Differentiation</div>'
        f"<h2>{_escape(comparison['heading'])}</h2>"
        '<div class="comparison-table-wrap"><table class="comparison-table">'
        "<thead><tr><th>Topic</th><th>This product</th><th>Typical alternative</th></tr></thead>"
        f"<tbody>{rows}</tbody>"
        "</table></div>"
        "</section>"
    )


def _render_faq(faq: list[dict[str, str]]) -> str:
    if not faq:
        return ""
    items = "".join(
        (
            '<details class="faq-item">'
            f"<summary>{_escape(item['question'])}</summary>"
            f"<p>{_escape(item['answer'])}</p>"
            "</details>"
        )
        for item in faq
    )
    return (
        '<section class="faq-block">'
        '<div class="section-eyebrow">FAQ</div>'
        "<h2>Frequently asked questions</h2>"
        f"{items}"
        "</section>"
    )


def _render_related_pages(items: list[dict[str, str]]) -> str:
    if not items:
        return ""
    cards = "".join(
        (
            '<article class="related-card">'
            f'<h3><a href="{_escape(item["href"])}">{_escape(item["label"])}</a></h3>'
            f"<p>{_escape(item['summary'])}</p>"
            f'<a class="text-link" href="{_escape(item["href"])}">Open page</a>'
            "</article>"
        )
        for item in items
    )
    return (
        '<section class="related-block">'
        '<div class="section-eyebrow">Related pages</div>'
        "<h2>Continue through the public portal</h2>"
        f'<div class="related-grid">{cards}</div>'
        "</section>"
    )


def _render_final_cta(final_cta: dict[str, Any]) -> str:
    return (
        '<section class="cta-band">'
        '<div class="section-eyebrow">Next step</div>'
        f"<h2>{_escape(final_cta['heading'])}</h2>"
        f"<p>{_escape(final_cta['body'])}</p>"
        '<div class="cta-row">'
        f'<a class="button primary" href="{_escape(final_cta["primary"]["href"])}">{_escape(final_cta["primary"]["label"])}</a>'
        f'<a class="button secondary" href="{_escape(final_cta["secondary"]["href"])}">{_escape(final_cta["secondary"]["label"])}</a>'
        "</div>"
        "</section>"
    )


def _render_footer(portal: PublicPortalConfig) -> str:
    nav = "".join(
        f'<a class="footer-link" href="{_escape(item["href"])}">{_escape(item["label"])}</a>'
        for item in portal.legal_fields.get("footer_nav", [])
    )
    identity = portal.legal_fields.get("identity", {})
    identity_line = (
        f'Operator: {_escape(identity.get("operator_name", SOURCE_NOT_YET_CONFIRMED))}, '
        f'{_escape(identity.get("trading_as", SOURCE_NOT_YET_CONFIRMED))} · '
        f'VAT ID: {_escape(identity.get("vat_id", SOURCE_NOT_YET_CONFIRMED))} · '
        f'Support: {_escape(identity.get("support_email", SOURCE_NOT_YET_CONFIRMED))} · '
        f'{_escape(identity.get("invoices_note", SOURCE_NOT_YET_CONFIRMED))}'
    )
    return (
        '<footer>'
        '<nav class="footer-nav" aria-label="Legal navigation">'
        f"{nav}"
        "</nav>"
        f'<p class="footer-identity">{identity_line}</p>'
        "<p>Protected operator, control-plane, customer and private download routes remain non-public by design.</p>"
        "</footer>"
    )


def _breadcrumb_json_ld(portal: PublicPortalConfig, path: str) -> dict[str, Any] | None:
    path = LEGAL_ROUTE_ALIASES.get(path, path)
    if path == "/":
        return None
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": 1,
                "name": "Home",
                "item": _canonical_url(portal, "/"),
            },
            {
                "@type": "ListItem",
                "position": 2,
                "name": _page_label(portal, path),
                "item": _canonical_url(portal, path),
            },
        ],
    }


def _faq_json_ld(faq: list[dict[str, str]]) -> dict[str, Any] | None:
    if not faq:
        return None
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": item["question"],
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": item["answer"],
                },
            }
            for item in faq
        ],
    }


def _structured_data(portal: PublicPortalConfig, path: str, page: dict[str, Any]) -> str:
    graph: list[dict[str, Any]] = [
        {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": portal.product_name,
            "url": portal.canonical_base_url,
            "description": page["description"],
        }
    ]
    if not page.get("disable_software_application_markup", False):
        graph.append(
            {
                "@context": "https://schema.org",
                "@type": "SoftwareApplication",
                "name": portal.product_name,
                "applicationCategory": "BusinessApplication",
                "operatingSystem": "Web",
                "description": page["description"],
                "url": _canonical_url(portal, path),
                "featureList": page.get("trust_points", []),
            }
        )
    breadcrumb = _breadcrumb_json_ld(portal, path)
    if breadcrumb is not None:
        graph.append(breadcrumb)
    faq = _faq_json_ld(page.get("faq", []))
    if faq is not None:
        graph.append(faq)
    return "\n".join(
        f'<script type="application/ld+json">{json.dumps(item, ensure_ascii=True)}</script>' for item in graph
    )


def _render_layout(
    portal: PublicPortalConfig,
    path: str,
    page: dict[str, Any],
    snapshot: dict[str, Any],
    translation_state: dict[str, Any],
) -> str:
    canonical_url = _canonical_url(portal, path)
    effective_language = str(translation_state.get("effective_language", portal.translation.default_language))
    robots_content = (
        "noindex,follow,max-image-preview:large"
        if translation_state.get("machine_translation_applied")
        else "index,follow,max-image-preview:large"
    )
    nav_links = _render_nav(path)
    translation_switcher = _render_translation_switcher(path, translation_state)
    translation_banner = _render_translation_banner(translation_state)
    breadcrumb_html = _render_breadcrumbs(portal, path)
    sales_ribbon_html = _render_sales_ribbon(portal, snapshot)
    trust_chips = "".join(f'<span class="chip">{_escape(point)}</span>' for point in page.get("trust_points", []))
    spotlight = page.get("spotlight")
    spotlight_html = ""
    if spotlight:
        spotlight_html = (
            '<div class="hero-note">'
            f"<h2>{_escape(spotlight['title'])}</h2>"
            f"<p>{_escape(spotlight['body'])}</p>"
            "</div>"
        )
    conversion_panel_html = _render_conversion_panel(portal, page, snapshot)
    status_card = (
        '<aside class="status-card">'
        '<div class="status-kicker">Local only / no external effect</div>'
        f"<h2>{_escape(snapshot['safe_reference_status'].get('status', 'unknown'))} reference status</h2>"
        f"<p>Selected subdomain: {_escape(portal.selected_subdomain)}</p>"
        f"<p>Protected routes stay blocked. Operator console remains non-public. Portal mode remains {_escape(snapshot['portal_status']['mode'])}.</p>"
        '<div class="status-list">'
        + "".join(
            (
                '<div class="status-item">'
                f"<span>{_escape(item['label'])}</span>"
                f"<strong>{_escape(item['value'])}</strong>"
                "</div>"
            )
            for item in snapshot.get("reference_metrics", [])[:4]
        )
        + "</div>"
        "</aside>"
    )
    section_html = "".join(_render_section(section) for section in page.get("sections", []))
    sales_offer_deck_html = _render_sales_offer_deck(path)
    sales_journey_html = _render_sales_journey()
    readiness_html = _render_readiness_summary(page.get("readiness_summary", []))
    pricing_html = _render_pricing_tiers(page.get("pricing_tiers", []))
    comparison_html = _render_comparison(page.get("comparison"))
    related_html = _render_related_pages(page.get("related_pages", []))
    faq_html = _render_faq(page.get("faq", []))
    final_cta_html = _render_final_cta(page["final_cta"])
    structured_data = _structured_data(portal, path, page)
    return f"""<!doctype html>
<html lang="{_escape(effective_language)}">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{_escape(page['title'])}</title>
  <meta name="description" content="{_escape(page['description'])}" />
  <link rel="canonical" href="{_escape(canonical_url)}" />
  <meta name="robots" content="{_escape(robots_content)}" />
  <meta property="og:type" content="website" />
  <meta property="og:title" content="{_escape(page['title'])}" />
  <meta property="og:description" content="{_escape(page['description'])}" />
  <meta property="og:url" content="{_escape(canonical_url)}" />
  <meta property="og:site_name" content="{_escape(portal.product_name)}" />
  <meta property="og:locale" content="{_escape(_og_locale_for_language(effective_language))}" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{_escape(page['title'])}" />
  <meta name="twitter:description" content="{_escape(page['description'])}" />
  {structured_data}
  <style>
    :root {{
      --page: #f3efe8;
      --panel: rgba(255, 252, 247, 0.92);
      --panel-strong: rgba(250, 245, 238, 0.97);
      --line: rgba(57, 43, 31, 0.12);
      --text: #15110d;
      --muted: #5f554d;
      --brand: #0e6c7b;
      --brand-dark: #083f48;
      --accent: #dd6b20;
      --accent-soft: rgba(221, 107, 32, 0.14);
      --glow: rgba(14, 108, 123, 0.18);
      --shadow: 0 24px 60px rgba(28, 19, 12, 0.10);
      --radius-lg: 32px;
      --radius-md: 22px;
      --radius-sm: 16px;
      --max: 1180px;
    }}
    * {{
      box-sizing: border-box;
    }}
    body {{
      margin: 0;
      color: var(--text);
      font-family: "Neue Haas Grotesk Text", "Avenir Next", "Segoe UI Variable", sans-serif;
      background:
        radial-gradient(circle at 0% 0%, rgba(14,108,123,0.16), transparent 28%),
        radial-gradient(circle at 92% 4%, rgba(221,107,32,0.17), transparent 22%),
        radial-gradient(circle at 50% 100%, rgba(8,63,72,0.10), transparent 24%),
        linear-gradient(180deg, #fcfaf5 0%, var(--page) 50%, #ece3d5 100%);
    }}
    a {{
      color: inherit;
    }}
    .shell {{
      max-width: var(--max);
      margin: 0 auto;
      padding: 0 22px 48px;
    }}
    header {{
      position: sticky;
      top: 0;
      z-index: 10;
      backdrop-filter: blur(14px);
      background: rgba(247, 243, 236, 0.78);
      border-bottom: 1px solid var(--line);
    }}
    .header-inner {{
      max-width: var(--max);
      margin: 0 auto;
      padding: 18px 22px 16px;
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
    }}
    .brand-lockup {{
      display: grid;
      gap: 4px;
    }}
    .brand-kicker {{
      color: var(--brand);
      font-size: 12px;
      letter-spacing: 0.16em;
      text-transform: uppercase;
      font-weight: 800;
    }}
    .brand-title {{
      font-family: "Fraunces", "Iowan Old Style", "Palatino Linotype", Georgia, serif;
      font-size: 22px;
      font-weight: 700;
      letter-spacing: -0.02em;
    }}
    .sales-ribbon {{
      display: grid;
      grid-template-columns: 1.15fr 0.95fr;
      gap: 18px;
      margin-top: 18px;
      padding: 22px 24px;
      border-radius: var(--radius-lg);
      background:
        linear-gradient(135deg, rgba(8,63,72,0.96), rgba(14,108,123,0.90)),
        linear-gradient(180deg, rgba(255,255,255,0.08), rgba(255,255,255,0));
      color: #f9f5ed;
      box-shadow: 0 24px 60px rgba(8, 63, 72, 0.24);
      position: relative;
      overflow: hidden;
    }}
    .sales-ribbon::after {{
      content: "";
      position: absolute;
      width: 240px;
      height: 240px;
      right: -40px;
      top: -80px;
      background: radial-gradient(circle, rgba(255,255,255,0.18), transparent 70%);
      border-radius: 50%;
      pointer-events: none;
    }}
    .sales-ribbon-kicker {{
      font-size: 12px;
      letter-spacing: 0.16em;
      text-transform: uppercase;
      font-weight: 800;
      color: rgba(255, 243, 227, 0.82);
      margin-bottom: 10px;
    }}
    .sales-ribbon h2 {{
      margin: 0 0 10px;
      font-size: clamp(28px, 4vw, 42px);
      line-height: 1.02;
      letter-spacing: -0.04em;
    }}
    .sales-ribbon p {{
      margin: 0;
      color: rgba(250, 245, 236, 0.84);
      line-height: 1.7;
      font-size: 15px;
    }}
    .sales-ribbon-copy {{
      display: grid;
      gap: 10px;
      position: relative;
      z-index: 1;
    }}
    .sales-ribbon-pills {{
      display: flex;
      flex-wrap: wrap;
      align-content: center;
      gap: 10px;
      justify-content: flex-end;
      position: relative;
      z-index: 1;
    }}
    .sales-pill {{
      display: inline-flex;
      align-items: center;
      padding: 10px 14px;
      border-radius: 999px;
      background: rgba(255, 246, 235, 0.12);
      border: 1px solid rgba(255, 246, 235, 0.18);
      font-size: 13px;
      font-weight: 800;
      color: #fff3e1;
      backdrop-filter: blur(8px);
    }}
    nav {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }}
    .header-utilities {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      align-items: center;
      justify-content: flex-end;
    }}
    .nav-link {{
      text-decoration: none;
      padding: 9px 12px;
      border-radius: 999px;
      font-weight: 700;
      color: var(--muted);
      transition: background 160ms ease, color 160ms ease, transform 160ms ease;
    }}
    .nav-link:hover,
    .nav-link:focus {{
      background: rgba(14, 108, 123, 0.08);
      color: var(--brand-dark);
      transform: translateY(-1px);
    }}
    .nav-link.active {{
      background: rgba(14, 108, 123, 0.14);
      color: var(--brand-dark);
    }}
    .breadcrumbs {{
      display: flex;
      gap: 8px;
      align-items: center;
      color: var(--muted);
      font-size: 14px;
      padding-top: 28px;
    }}
    .translation-switcher {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
      justify-content: flex-end;
    }}
    .translation-label {{
      font-size: 12px;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: var(--muted);
      font-weight: 800;
    }}
    .translation-link {{
      text-decoration: none;
      padding: 7px 10px;
      border-radius: 999px;
      background: rgba(14, 108, 123, 0.06);
      color: var(--brand-dark);
      font-size: 13px;
      font-weight: 700;
    }}
    .translation-link.active {{
      background: rgba(14, 108, 123, 0.16);
    }}
    .translation-banner {{
      margin-top: 14px;
      padding: 16px 18px;
      border-radius: var(--radius-md);
      background: rgba(14, 108, 123, 0.08);
      border: 1px solid rgba(14, 108, 123, 0.14);
    }}
    .translation-banner.warning {{
      background: rgba(217, 108, 36, 0.08);
      border-color: rgba(217, 108, 36, 0.16);
    }}
    .translation-banner p {{
      margin: 0;
      color: var(--muted);
      line-height: 1.6;
    }}
    .breadcrumbs a {{
      color: var(--brand-dark);
      text-decoration: none;
    }}
    .hero-grid {{
      display: grid;
      grid-template-columns: 1.25fr 0.9fr;
      gap: 26px;
      padding: 24px 0 20px;
      align-items: stretch;
    }}
    .hero-aside-stack {{
      display: grid;
      gap: 18px;
      align-content: start;
    }}
    .hero-panel,
    .status-card,
    .conversion-panel {{
      background: linear-gradient(180deg, rgba(255,255,255,0.92), rgba(251,245,234,0.92));
      border: 1px solid var(--line);
      border-radius: var(--radius-lg);
      box-shadow: var(--shadow);
      padding: 28px;
    }}
    .hero-panel {{
      position: relative;
      overflow: hidden;
    }}
    .hero-panel::after {{
      content: "";
      position: absolute;
      right: -60px;
      top: -80px;
      width: 220px;
      height: 220px;
      border-radius: 50%;
      background: radial-gradient(circle, rgba(14,108,123,0.16), transparent 70%);
      pointer-events: none;
    }}
    .eyebrow {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      font-size: 12px;
      letter-spacing: 0.15em;
      text-transform: uppercase;
      color: var(--brand);
      font-weight: 800;
      margin-bottom: 12px;
    }}
    .hero-panel h1 {{
      font-family: "Fraunces", "Iowan Old Style", "Palatino Linotype", Georgia, serif;
      font-size: clamp(42px, 6vw, 76px);
      line-height: 0.96;
      letter-spacing: -0.045em;
      margin: 0 0 16px;
      max-width: 12ch;
    }}
    .hero-panel p {{
      margin: 0;
      font-size: 20px;
      line-height: 1.6;
      color: var(--muted);
      max-width: 42rem;
    }}
    .chip-row,
    .cta-row,
    .link-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      margin-top: 18px;
    }}
    .chip {{
      display: inline-flex;
      align-items: center;
      padding: 8px 12px;
      border-radius: 999px;
      background: rgba(14, 108, 123, 0.09);
      border: 1px solid rgba(14, 108, 123, 0.12);
      color: var(--brand-dark);
      font-size: 13px;
      font-weight: 700;
    }}
    .conversion-panel {{
      position: relative;
      overflow: hidden;
      background:
        linear-gradient(180deg, rgba(255,255,255,0.96), rgba(250,245,237,0.94)),
        radial-gradient(circle at top right, rgba(221,107,32,0.10), transparent 32%);
    }}
    .conversion-panel::after {{
      content: "";
      position: absolute;
      inset: auto -40px -70px auto;
      width: 180px;
      height: 180px;
      border-radius: 50%;
      background: radial-gradient(circle, rgba(14,108,123,0.10), transparent 70%);
      pointer-events: none;
    }}
    .conversion-kicker {{
      font-size: 12px;
      letter-spacing: 0.16em;
      text-transform: uppercase;
      color: var(--accent);
      font-weight: 800;
      margin-bottom: 10px;
    }}
    .conversion-panel h2 {{
      margin: 0 0 10px;
      font-size: 30px;
      line-height: 1.02;
      letter-spacing: -0.04em;
    }}
    .conversion-panel p {{
      margin: 0 0 14px;
      color: var(--muted);
      line-height: 1.65;
    }}
    .conversion-metrics {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
      margin: 18px 0;
    }}
    .conversion-metric {{
      padding: 14px;
      border-radius: var(--radius-sm);
      background: rgba(255, 252, 247, 0.92);
      border: 1px solid var(--line);
    }}
    .conversion-metric span {{
      display: block;
      margin-bottom: 6px;
      font-size: 11px;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: var(--muted);
      font-weight: 800;
    }}
    .conversion-metric strong {{
      font-size: 18px;
      line-height: 1.2;
    }}
    .conversion-list {{
      list-style: none;
      padding: 0;
      margin: 0;
      display: grid;
      gap: 10px;
    }}
    .conversion-list li {{
      display: grid;
      gap: 3px;
      padding: 12px 14px;
      border-radius: var(--radius-sm);
      background: rgba(255, 251, 244, 0.94);
      border: 1px solid var(--line);
    }}
    .conversion-list strong {{
      font-size: 14px;
    }}
    .conversion-list span {{
      color: var(--muted);
      font-size: 14px;
      line-height: 1.5;
    }}
    .button {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-height: 46px;
      padding: 0 18px;
      border-radius: 999px;
      text-decoration: none;
      font-weight: 800;
      letter-spacing: 0.01em;
    }}
    .button.primary {{
      color: #fff8f0;
      background: linear-gradient(135deg, var(--brand), var(--brand-dark));
      box-shadow: 0 12px 24px rgba(10, 78, 89, 0.18);
    }}
    .button.secondary {{
      color: var(--brand-dark);
      background: rgba(14, 108, 123, 0.08);
      border: 1px solid rgba(14, 108, 123, 0.18);
    }}
    .hero-note {{
      margin-top: 22px;
      padding: 18px;
      border-radius: var(--radius-md);
      background: linear-gradient(135deg, rgba(14,108,123,0.09), rgba(217,108,36,0.08));
      border: 1px solid rgba(14, 108, 123, 0.12);
    }}
    .hero-note h2 {{
      margin: 0 0 8px;
      font-size: 21px;
    }}
    .hero-note p {{
      font-size: 16px;
    }}
    .status-card {{
      display: grid;
      align-content: start;
      gap: 14px;
    }}
    .status-kicker {{
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.16em;
      color: var(--accent);
      font-weight: 800;
    }}
    .status-card h2 {{
      margin: 0;
      font-size: 30px;
      line-height: 1.05;
    }}
    .status-card p {{
      margin: 0;
      color: var(--muted);
      line-height: 1.6;
    }}
    .status-list {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
    }}
    .status-item {{
      padding: 14px;
      border-radius: var(--radius-sm);
      background: rgba(255, 250, 244, 0.88);
      border: 1px solid var(--line);
    }}
    .status-item span,
    .metric-card span {{
      display: block;
      font-size: 12px;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      color: var(--muted);
      margin-bottom: 6px;
      font-weight: 700;
    }}
    .status-item strong,
    .metric-card strong {{
      font-size: 20px;
      line-height: 1.1;
    }}
    .metric-grid {{
      display: grid;
      grid-template-columns: repeat(6, minmax(0, 1fr));
      gap: 14px;
      margin: 8px 0 28px;
    }}
    .metric-card {{
      background: rgba(255, 251, 246, 0.9);
      border: 1px solid var(--line);
      border-radius: var(--radius-sm);
      padding: 16px;
      box-shadow: 0 12px 22px rgba(28, 18, 10, 0.05);
    }}
    .readiness-block {{
      margin-top: 10px;
      background: linear-gradient(180deg, rgba(255, 250, 243, 0.95), rgba(246, 239, 229, 0.96));
      border: 1px solid var(--line);
      border-radius: var(--radius-lg);
      padding: 24px;
      box-shadow: var(--shadow);
    }}
    .readiness-grid {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 14px;
      margin-top: 14px;
    }}
    .readiness-card {{
      background: rgba(255, 252, 248, 0.94);
      border: 1px solid var(--line);
      border-radius: var(--radius-sm);
      padding: 16px;
    }}
    .readiness-card span {{
      display: block;
      font-size: 12px;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      color: var(--muted);
      margin-bottom: 8px;
      font-weight: 700;
    }}
    .readiness-card strong {{
      display: block;
      font-size: 20px;
      line-height: 1.2;
      margin-bottom: 10px;
    }}
    .readiness-card p {{
      margin: 0;
      color: var(--muted);
      line-height: 1.6;
      font-size: 14px;
    }}
    .offer-deck,
    .journey-band {{
      margin-top: 20px;
      background: var(--panel-strong);
      border: 1px solid var(--line);
      border-radius: var(--radius-lg);
      padding: 26px;
      box-shadow: var(--shadow);
    }}
    .offer-grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 16px;
      margin-top: 18px;
    }}
    .offer-card {{
      background: rgba(255, 252, 247, 0.96);
      border: 1px solid var(--line);
      border-radius: var(--radius-md);
      padding: 22px;
      box-shadow: 0 18px 32px rgba(34, 23, 14, 0.07);
    }}
    .offer-kicker {{
      display: inline-flex;
      align-items: center;
      min-height: 28px;
      padding: 0 10px;
      border-radius: 999px;
      background: rgba(14, 108, 123, 0.10);
      color: var(--brand-dark);
      font-size: 12px;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      font-weight: 800;
    }}
    .offer-card h3 {{
      margin: 14px 0 8px;
      font-size: 28px;
      line-height: 1.02;
      letter-spacing: -0.03em;
    }}
    .offer-card p {{
      margin: 0 0 12px;
      color: var(--muted);
      line-height: 1.6;
    }}
    .offer-price,
    .offer-scope {{
      color: var(--text);
      font-weight: 800;
    }}
    .journey-grid {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 14px;
      margin-top: 18px;
    }}
    .journey-step {{
      background: rgba(255, 251, 245, 0.96);
      border: 1px solid var(--line);
      border-radius: var(--radius-md);
      padding: 20px;
      box-shadow: 0 16px 28px rgba(34, 23, 14, 0.06);
    }}
    .journey-index {{
      width: 42px;
      height: 42px;
      border-radius: 14px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      background: linear-gradient(135deg, rgba(14,108,123,0.14), rgba(221,107,32,0.14));
      color: var(--brand-dark);
      font-size: 13px;
      font-weight: 900;
      letter-spacing: 0.08em;
      margin-bottom: 14px;
    }}
    .journey-step h3 {{
      margin: 0 0 8px;
      font-size: 21px;
      line-height: 1.15;
    }}
    .journey-step p {{
      margin: 0;
      color: var(--muted);
      line-height: 1.65;
    }}
    .content-grid {{
      display: grid;
      grid-template-columns: repeat(12, minmax(0, 1fr));
      gap: 18px;
      margin-top: 10px;
    }}
    .content-card {{
      grid-column: span 4;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: var(--radius-md);
      padding: 24px;
      box-shadow: 0 18px 32px rgba(34, 23, 14, 0.07);
      animation: rise 320ms ease;
    }}
    .section-eyebrow {{
      font-size: 12px;
      letter-spacing: 0.15em;
      text-transform: uppercase;
      color: var(--accent);
      font-weight: 800;
      margin-bottom: 10px;
    }}
    .content-card h2,
    .comparison-block h2,
    .faq-block h2,
    .cta-band h2 {{
      margin: 0 0 12px;
      font-size: 28px;
      line-height: 1.1;
      letter-spacing: -0.03em;
    }}
    .content-card p,
    .comparison-block p,
    .faq-item p,
    .cta-band p {{
      color: var(--muted);
      line-height: 1.7;
      margin: 0 0 14px;
    }}
    .bullet-list {{
      margin: 0;
      padding-left: 18px;
      color: var(--muted);
      display: grid;
      gap: 10px;
    }}
    .text-link {{
      color: var(--brand-dark);
      font-weight: 800;
      text-decoration: none;
    }}
    .comparison-block,
    .pricing-block,
    .related-block,
    .faq-block,
    .cta-band {{
      margin-top: 20px;
      background: var(--panel-strong);
      border: 1px solid var(--line);
      border-radius: var(--radius-lg);
      padding: 26px;
      box-shadow: var(--shadow);
    }}
    .pricing-grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 16px;
      margin-top: 18px;
    }}
    .pricing-card {{
      background: rgba(255, 252, 247, 0.96);
      border: 1px solid var(--line);
      border-radius: var(--radius-md);
      padding: 22px;
      box-shadow: 0 18px 32px rgba(34, 23, 14, 0.07);
    }}
    .pricing-badge {{
      display: inline-flex;
      align-items: center;
      min-height: 28px;
      padding: 0 10px;
      border-radius: 999px;
      background: rgba(217, 108, 36, 0.12);
      color: var(--accent);
      font-size: 12px;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      font-weight: 800;
    }}
    .pricing-card h3 {{
      margin: 14px 0 10px;
      font-size: 30px;
      line-height: 1.02;
      letter-spacing: -0.03em;
    }}
    .pricing-card p {{
      color: var(--muted);
      line-height: 1.65;
      margin: 0 0 12px;
    }}
    .pricing-line,
    .pricing-scope,
    .pricing-included {{
      color: var(--text);
      font-weight: 800;
    }}
    .pricing-line {{
      font-size: 24px;
      letter-spacing: -0.02em;
    }}
    .pricing-scope,
    .pricing-included {{
      font-size: 15px;
    }}
    .comparison-table-wrap {{
      overflow-x: auto;
    }}
    .comparison-table {{
      width: 100%;
      border-collapse: collapse;
      min-width: 680px;
    }}
    .comparison-table th,
    .comparison-table td {{
      padding: 14px 12px;
      border-top: 1px solid var(--line);
      text-align: left;
      vertical-align: top;
    }}
    .comparison-table thead th {{
      border-top: none;
      color: var(--brand-dark);
      font-size: 14px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }}
    .faq-item {{
      border-top: 1px solid var(--line);
      padding: 16px 0;
    }}
    .related-grid {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 14px;
    }}
    .related-card {{
      background: rgba(255, 252, 247, 0.94);
      border: 1px solid var(--line);
      border-radius: var(--radius-sm);
      padding: 18px;
    }}
    .related-card h3 {{
      margin: 0 0 10px;
      font-size: 20px;
      line-height: 1.15;
    }}
    .related-card h3 a {{
      text-decoration: none;
      color: var(--text);
    }}
    .related-card p {{
      margin: 0 0 12px;
      color: var(--muted);
      line-height: 1.6;
    }}
    .faq-item:first-of-type {{
      border-top: none;
      padding-top: 0;
    }}
    .faq-item summary {{
      cursor: pointer;
      font-weight: 800;
      list-style: none;
    }}
    .faq-item summary::-webkit-details-marker {{
      display: none;
    }}
    footer {{
      padding: 30px 0 8px;
      color: var(--muted);
      font-size: 14px;
      line-height: 1.7;
    }}
    .footer-nav {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      margin-bottom: 12px;
    }}
    .footer-link {{
      color: var(--brand-dark);
      text-decoration: none;
      font-weight: 700;
    }}
    .footer-identity {{
      margin: 0 0 8px;
    }}
    @keyframes rise {{
      from {{
        opacity: 0;
        transform: translateY(8px);
      }}
      to {{
        opacity: 1;
        transform: translateY(0);
      }}
    }}
    @media (max-width: 1080px) {{
      .metric-grid {{
        grid-template-columns: repeat(3, minmax(0, 1fr));
      }}
      .readiness-grid {{
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }}
      .related-grid {{
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }}
      .sales-ribbon,
      .offer-grid,
      .journey-grid {{
        grid-template-columns: 1fr;
      }}
      .pricing-grid {{
        grid-template-columns: 1fr;
      }}
      .content-card {{
        grid-column: span 6;
      }}
    }}
    @media (max-width: 860px) {{
      .hero-grid {{
        grid-template-columns: 1fr;
      }}
      .sales-ribbon {{
        grid-template-columns: 1fr;
      }}
      .hero-panel h1 {{
        max-width: none;
      }}
      .status-list {{
        grid-template-columns: 1fr 1fr;
      }}
      .content-card {{
        grid-column: span 12;
      }}
    }}
    @media (max-width: 640px) {{
      .shell {{
        padding: 0 16px 34px;
      }}
      .header-inner {{
        padding: 16px;
      }}
      .hero-panel,
      .status-card,
      .comparison-block,
      .faq-block,
      .cta-band {{
        padding: 22px;
      }}
      .hero-panel p {{
        font-size: 18px;
      }}
      .metric-grid,
      .status-list,
      .conversion-metrics,
      .readiness-grid,
      .related-grid,
      .offer-grid,
      .journey-grid {{
        grid-template-columns: 1fr;
      }}
      .button {{
        width: 100%;
      }}
      .comparison-table {{
        min-width: 0;
      }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="header-inner">
      <div class="brand-lockup">
        <div class="brand-kicker">Public product portal</div>
        <div class="brand-title">{_escape(portal.product_name)}</div>
      </div>
      <div class="header-utilities">
        <nav aria-label="Primary navigation">{nav_links}</nav>
        {translation_switcher}
      </div>
    </div>
  </header>
  <div class="shell">
    {breadcrumb_html}
    {translation_banner}
    {sales_ribbon_html}
    <section class="hero-grid">
      <div class="hero-panel">
        <div class="eyebrow">{_escape(page['eyebrow'])}</div>
        <h1>{_escape(page['hero'])}</h1>
        <p>{_escape(page['lede'])}</p>
        <div class="chip-row">{trust_chips}</div>
        <div class="cta-row">
          <a class="button primary" href="{_escape(page['primary_cta']['href'])}">{_escape(page['primary_cta']['label'])}</a>
          <a class="button secondary" href="{_escape(page['secondary_cta']['href'])}">{_escape(page['secondary_cta']['label'])}</a>
        </div>
        {spotlight_html}
      </div>
      <div class="hero-aside-stack">
        {conversion_panel_html}
        {status_card}
      </div>
    </section>
    {_render_metric_grid(snapshot)}
    {sales_offer_deck_html}
    {sales_journey_html}
    {readiness_html}
    {pricing_html}
    <section class="content-grid">{section_html}</section>
    {comparison_html}
    {related_html}
    {faq_html}
    {final_cta_html}
    {_render_footer(portal)}
  </div>
</body>
</html>"""


def _render_plain_html(title: str, text: str) -> str:
    return (
        "<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\" />"
        f"<title>{_escape(title)}</title></head><body><h1>{_escape(title)}</h1><p>{_escape(text)}</p></body></html>"
    )


def render_robots_txt(portal: PublicPortalConfig) -> str:
    return textwrap.dedent(
        f"""\
        User-agent: *
        Allow: /
        Disallow: /operator
        Disallow: /admin
        Disallow: /control-plane
        Disallow: /console
        Disallow: /customer
        Disallow: /api/
        Disallow: /downloads/private
        Sitemap: {portal.canonical_base_url}/sitemap.xml
        """
    )


def render_sitemap_xml(portal: PublicPortalConfig) -> str:
    urls = []
    now = datetime.now(timezone.utc).date().isoformat()
    for route in portal.public_routes:
        urls.append(
            f"<url><loc>{html.escape(_canonical_url(portal, route))}</loc><lastmod>{now}</lastmod></url>"
        )
    urls.append(f"<url><loc>{html.escape(portal.canonical_base_url)}/healthz</loc><lastmod>{now}</lastmod></url>")
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        + "".join(urls)
        + "</urlset>"
    )


def build_public_health_payload(workspace_root: Path, config: AppConfig, portal: PublicPortalConfig) -> dict[str, Any]:
    return {
        "status": "ok",
        "service": "public_portal",
        "workspace_root": str(workspace_root),
        "mode": config.mode,
        "selected_subdomain": portal.selected_subdomain,
        "canonical_base_url": portal.canonical_base_url,
        "local_upstream_url": f"http://{portal.bind_host}:{portal.port}/",
        "public_routes_only": True,
        "protected_routes_public": False,
        "allow_external_changes": config.allow_external_changes,
        "landing_variant": "seo_conversion_sales_platform_v3",
    }


def resolve_portal_request(
    path: str,
    workspace_root: Path,
    config: AppConfig,
    portal: PublicPortalConfig,
) -> PortalResponse:
    parsed = urlsplit(path)
    route = parsed.path or "/"
    route = LEGAL_ROUTE_ALIASES.get(route, route)
    if route in {"/healthz", "/health"}:
        body = json.dumps(build_public_health_payload(workspace_root, config, portal), indent=2).encode("utf-8")
        return PortalResponse(200, "application/json; charset=utf-8", body)

    if route == "/robots.txt":
        return PortalResponse(200, "text/plain; charset=utf-8", render_robots_txt(portal).encode("utf-8"))

    if route == "/sitemap.xml":
        return PortalResponse(200, "application/xml; charset=utf-8", render_sitemap_xml(portal).encode("utf-8"))

    if any(route == prefix or route.startswith(prefix + "/") for prefix in portal.protected_route_prefixes):
        body = _render_plain_html(
            "Protected Route",
            "This route is not public. Operator, control-plane and customer execution paths remain protected.",
        ).encode("utf-8")
        return PortalResponse(HTTPStatus.FORBIDDEN, "text/html; charset=utf-8", body)

    snapshot = build_public_portal_snapshot(workspace_root, config, portal)
    page_map = _page_copy(portal, snapshot)
    if route not in page_map:
        body = _render_plain_html(
            "Not Found",
            "The requested portal page does not exist.",
        ).encode("utf-8")
        return PortalResponse(HTTPStatus.NOT_FOUND, "text/html; charset=utf-8", body)

    page = page_map[route]
    requested_language = parse_qs(parsed.query).get("lang", [portal.translation.default_language])[0]
    translation_state = _resolve_public_portal_translation_state(workspace_root, portal, requested_language)
    if translation_state["machine_translation_requested"]:
        if translation_state["activation_state"] == "ready":
            try:
                page = _translate_public_page_copy(
                    page,
                    translation_state["requested_language"],
                    translation_state["api_key"],
                )
                translation_state["effective_language"] = translation_state["requested_language"]
                translation_state["machine_translation_applied"] = True
                translation_state["note"] = (
                    "Machine-translated from the English source via Google Cloud Translation. "
                    "The English source remains canonical and translated pages stay non-canonical."
                )
            except Exception:
                translation_state["note"] = (
                    "Google translation could not be completed for this request. The English source remains in use."
                )
        else:
            translation_state["note"] = (
                "Google translation is configured as an optional portal layer, but the API key is not active here yet. "
                "The English source remains in use."
            )
    return PortalResponse(
        200,
        "text/html; charset=utf-8",
        _render_layout(portal, route, page, snapshot, translation_state).encode("utf-8"),
    )


class PublicPortalServer(ThreadingHTTPServer):
    def __init__(
        self,
        server_address: tuple[str, int],
        handler_class: type[BaseHTTPRequestHandler],
        *,
        workspace_root: Path,
        app_config: AppConfig,
        portal_config: PublicPortalConfig,
    ) -> None:
        super().__init__(server_address, handler_class)
        self.workspace_root = workspace_root
        self.app_config = app_config
        self.portal_config = portal_config


class PublicPortalHandler(BaseHTTPRequestHandler):
    server: PublicPortalServer

    def log_message(self, format: str, *args: object) -> None:
        return

    def _send_headers(self, response: PortalResponse) -> None:
        self.send_response(response.status)
        self.send_header("Content-Type", response.content_type)
        self.send_header("Content-Length", str(len(response.body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'unsafe-inline'; img-src 'self' data:;")
        self.end_headers()

    def _send_response(self, response: PortalResponse) -> None:
        self._send_headers(response)
        self.wfile.write(response.body)

    def do_HEAD(self) -> None:
        response = resolve_portal_request(
            self.path,
            self.server.workspace_root,
            self.server.app_config,
            self.server.portal_config,
        )
        self._send_headers(response)

    def do_GET(self) -> None:
        response = resolve_portal_request(
            self.path,
            self.server.workspace_root,
            self.server.app_config,
            self.server.portal_config,
        )
        self._send_response(response)


def run_public_portal(
    config_path: str | Path = "config/settings.toml",
    *,
    workspace_root: str | Path | None = None,
    host: str | None = None,
    port: int | None = None,
) -> int:
    app_config, _ = load_config(config_path, workspace_root)
    portal_config = load_public_portal_config(app_config.workspace_root)
    bind_host = portal_config.bind_host if host is None else str(host).strip()
    if bind_host not in ALLOWED_BIND_HOSTS:
        raise ValueError("Public portal app may only bind to 127.0.0.1 or localhost.")
    bind_host = "127.0.0.1"
    bind_port = portal_config.port if port is None else int(port)
    server = PublicPortalServer(
        (bind_host, bind_port),
        PublicPortalHandler,
        workspace_root=app_config.workspace_root,
        app_config=app_config,
        portal_config=PublicPortalConfig(
            bind_host=bind_host,
            port=bind_port,
            selected_subdomain=portal_config.selected_subdomain,
            alternative_subdomains=portal_config.alternative_subdomains,
            canonical_base_url=portal_config.canonical_base_url,
            product_name=portal_config.product_name,
            support_contact=portal_config.support_contact,
            download_gate_state=portal_config.download_gate_state,
            public_routes=portal_config.public_routes,
            protected_route_prefixes=portal_config.protected_route_prefixes,
            translation=portal_config.translation,
            operator_fields=portal_config.operator_fields,
            legal_fields=portal_config.legal_fields,
            notes=portal_config.notes,
        ),
    )
    print(f"Public portal local upstream running at http://{bind_host}:{bind_port}/")
    print("Reverse proxy required for public reachability; protected routes remain non-public.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0
