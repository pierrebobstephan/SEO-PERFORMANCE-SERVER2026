from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import html
import json
from pathlib import Path
import textwrap
from typing import Any
from urllib.parse import urlsplit

from electri_city_ops.config import AppConfig, load_config


ALLOWED_BIND_HOSTS = {"127.0.0.1", "localhost"}
PUBLIC_NAV = (
    ("/", "Home"),
    ("/features", "Features"),
    ("/security", "Security"),
    ("/plugin", "Plugin"),
    ("/licensing", "Licensing"),
    ("/docs", "Docs"),
    ("/downloads", "Downloads"),
    ("/support", "Support"),
)


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
    notes: tuple[str, ...] = ()


@dataclass(slots=True)
class PortalResponse:
    status: int
    content_type: str
    body: bytes


def public_portal_config_path(workspace_root: Path) -> Path:
    return workspace_root.resolve() / "config" / "public-portal.json"


def load_public_portal_config(workspace_root: Path) -> PublicPortalConfig:
    payload = json.loads(public_portal_config_path(workspace_root).read_text(encoding="utf-8"))
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
        support_contact=str(payload.get("support_contact", "operator input required")).strip()
        or "operator input required",
        download_gate_state=str(payload.get("download_gate_state", "approval_required")).strip()
        or "approval_required",
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
        notes=tuple(notes),
    )


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_latest_summary(workspace_root: Path) -> dict[str, Any]:
    report_path = workspace_root / "var" / "reports" / "latest.json"
    if not report_path.exists():
        return {
            "latest_report_present": False,
            "status": "source not yet confirmed",
            "mode": "source not yet confirmed",
        }
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    summary = payload.get("summary", {})
    target_results = payload.get("target_results", [])
    first_result = target_results[0] if isinstance(target_results, list) and target_results else {}
    return {
        "latest_report_present": True,
        "run_id": payload.get("run_id", ""),
        "status": payload.get("status", ""),
        "mode": payload.get("mode", ""),
        "configured_domains": summary.get("configured_domains"),
        "domain_results": summary.get("domain_results"),
        "successful_target_probes": summary.get("successful_target_probes"),
        "homepage_title": first_result.get("title", ""),
        "homepage_final_url": first_result.get("final_url", ""),
    }


def build_public_portal_snapshot(workspace_root: Path, config: AppConfig, portal: PublicPortalConfig) -> dict[str, Any]:
    return {
        "product_name": portal.product_name,
        "selected_subdomain": portal.selected_subdomain,
        "alternative_subdomains": list(portal.alternative_subdomains),
        "canonical_base_url": portal.canonical_base_url,
        "support_contact": portal.support_contact,
        "download_gate_state": portal.download_gate_state,
        "public_routes": list(portal.public_routes),
        "protected_route_prefixes": list(portal.protected_route_prefixes),
        "portal_status": {
            "mode": config.mode,
            "allow_external_changes": config.allow_external_changes,
            "portal_upstream_host": portal.bind_host,
            "portal_upstream_port": portal.port,
            "operator_console_public": False,
            "control_plane_public": False,
        },
        "safe_reference_status": _safe_latest_summary(workspace_root),
    }


def _canonical_url(portal: PublicPortalConfig, path: str) -> str:
    if path == "/":
        return f"{portal.canonical_base_url}/"
    return f"{portal.canonical_base_url}{path}"


def _page_copy(portal: PublicPortalConfig, snapshot: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        "/": {
            "title": f"{portal.product_name} | WordPress SEO and Performance Control Plane",
            "description": (
                "Doctrine-enforced WordPress SEO and performance product portal with safe plugin execution, "
                "control-plane validation, rollback discipline and scoped licensing."
            ),
            "hero": f"{portal.product_name} for WordPress",
            "lede": (
                "A doctrine-enforced product portal for scoped SEO and performance optimization, built around "
                "safe plugin execution, guarded control-plane logic and reversible rollout paths."
            ),
            "sections": [
                {
                    "heading": "Product Positioning",
                    "content": (
                        "The public portal introduces the product, its plugin-first optimization model, "
                        "its rollback-first operating doctrine and the separation between public product content "
                        "and protected operator control-plane functions."
                    ),
                },
                {
                    "heading": "Reference System",
                    "content": (
                        "electri-c-ity-studios-24-7.com remains the reference and test instance. "
                        "Other WordPress sites are future customer targets with separate license, scope and validation boundaries."
                    ),
                },
                {
                    "heading": "Current Safe Status",
                    "content": (
                        f"Latest local reference report status: {snapshot['safe_reference_status'].get('status', 'unknown')}; "
                        f"mode: {snapshot['safe_reference_status'].get('mode', 'unknown')}; "
                        f"download gate: {portal.download_gate_state}."
                    ),
                },
            ],
        },
        "/features": {
            "title": f"Features | {portal.product_name}",
            "description": "Feature overview for doctrine-enforced WordPress SEO and performance operations.",
            "hero": "Feature Overview",
            "lede": "Safe optimization, scoped delivery and reversible execution remain the core product pattern.",
            "sections": [
                {
                    "heading": "Control Plane",
                    "content": (
                        "Licensing, policy narrowing, rollback profiles, manifest previews, validation windows and "
                        "dry-run onboarding are prepared in the Hetzner control plane."
                    ),
                },
                {
                    "heading": "WordPress Plugin",
                    "content": (
                        "The plugin is the primary execution plane for scoped homepage and template-level SEO work, "
                        "with safe-mode, conflict detection, validation hooks and rollback discipline."
                    ),
                },
                {
                    "heading": "Release Model",
                    "content": (
                        "Stable, pilot and rollback channels are domain-bound. "
                        "No domain inherits scope, entitlements or release rights from another."
                    ),
                },
            ],
        },
        "/security": {
            "title": f"Security and Rollback | {portal.product_name}",
            "description": "Public summary of defensive guardrails, validation and rollback philosophy.",
            "hero": "Security and Rollback Philosophy",
            "lede": "Public pages can be open. Operator and customer control paths cannot.",
            "sections": [
                {
                    "heading": "Guardrails",
                    "content": (
                        "The platform prioritizes workspace isolation, scope clarity, domain isolation, "
                        "blast-radius minimization, validation and documented rollback."
                    ),
                },
                {
                    "heading": "Public vs Protected",
                    "content": (
                        "Product content, docs entry pages and support pages can be public. "
                        "Operator routes, control-plane actions, license APIs and customer execution paths remain protected."
                    ),
                },
                {
                    "heading": "Rollback",
                    "content": (
                        "Every future live effect requires a before-state, a validation window and a domain-bound rollback profile."
                    ),
                },
            ],
        },
        "/plugin": {
            "title": f"Plugin Execution Model | {portal.product_name}",
            "description": "Public overview of the WordPress plugin execution plane and coexistence model.",
            "hero": "WordPress Plugin Execution Model",
            "lede": "The plugin is the primary future execution path, but it remains scoped, guarded and conflict-aware.",
            "sections": [
                {
                    "heading": "Execution Plane",
                    "content": (
                        "The WordPress plugin executes only on licensed, bound domains and within allowed scopes. "
                        "Safe mode and observe-only remain default fallbacks."
                    ),
                },
                {
                    "heading": "Conflict Awareness",
                    "content": (
                        "Theme, builder and SEO-plugin conflicts are checked before active output. "
                        "Rank Math remains in controlled coexistence until validated replacement logic exists."
                    ),
                },
                {
                    "heading": "No Abrupt Replacement",
                    "content": (
                        "Meta description, title, canonical and robots ownership must be mapped before any replacement path is activated."
                    ),
                },
            ],
        },
        "/licensing": {
            "title": f"Licensing Model | {portal.product_name}",
            "description": "Public overview of domain-bound licensing and scoped product access.",
            "hero": "License and Scope Model",
            "lede": "Licenses unlock bounded capability. They never override security guardrails.",
            "sections": [
                {
                    "heading": "Domain Binding",
                    "content": (
                        "Each license is bound to a defined domain and scope set. "
                        "No global or ambiguous multi-domain effect is allowed."
                    ),
                },
                {
                    "heading": "Entitlements",
                    "content": (
                        "Future downloads, updates and policy flows are gated by license, channel and domain entitlement."
                    ),
                },
                {
                    "heading": "Approval State",
                    "content": (
                        "A confirmed entitlement can prepare access. "
                        "It still does not remove validation, rollback or operator approval requirements."
                    ),
                },
            ],
        },
        "/docs": {
            "title": f"Docs and Architecture | {portal.product_name}",
            "description": "Public documentation entry for product architecture, plugin model and security philosophy.",
            "hero": "Documentation Entry",
            "lede": "The public documentation layer explains what the system is, what it does and what remains protected.",
            "sections": [
                {
                    "heading": "Architecture",
                    "content": (
                        "Hetzner control plane, WordPress plugin execution plane and public product portal are separate layers."
                    ),
                },
                {
                    "heading": "Validation",
                    "content": (
                        "Observe, analyze, decide, simulate, apply, validate, learn and rollback remain the governing execution pattern."
                    ),
                },
                {
                    "heading": "Portal Scope",
                    "content": (
                        "This portal is for product information, documentation entry, support routing and future gated access only."
                    ),
                },
            ],
        },
        "/downloads": {
            "title": f"Downloads | {portal.product_name}",
            "description": "Public download page with gated access model and no open package release.",
            "hero": "Downloads and Access",
            "lede": "No anonymous production download is exposed at this stage.",
            "sections": [
                {
                    "heading": "Current State",
                    "content": (
                        f"Download state: {portal.download_gate_state}. "
                        "Packages, manifests and release artifacts remain local preview or protected release objects."
                    ),
                },
                {
                    "heading": "Gated Access",
                    "content": (
                        "Future access requires license, domain entitlement, approval state, release channel fit and protected delivery."
                    ),
                },
                {
                    "heading": "No Open License API",
                    "content": (
                        "No public endpoint may grant scope, license or customer action without protection and domain checks."
                    ),
                },
            ],
        },
        "/support": {
            "title": f"Support and Contact | {portal.product_name}",
            "description": "Support and contact entry page for the product portal.",
            "hero": "Support and Contact",
            "lede": "Support can be public. Operator and customer control functions cannot.",
            "sections": [
                {
                    "heading": "Support Contact",
                    "content": f"Primary support contact: {portal.support_contact}.",
                },
                {
                    "heading": "Portal Scope",
                    "content": (
                        "The support surface is informational and routing-oriented. "
                        "It does not expose operator control-plane capabilities."
                    ),
                },
                {
                    "heading": "Documentation Entry",
                    "content": "For architecture and guardrail overview, start at the Docs section of this portal.",
                },
            ],
        },
    }


def _render_layout(
    portal: PublicPortalConfig,
    path: str,
    page: dict[str, Any],
    snapshot: dict[str, Any],
) -> str:
    canonical_url = _canonical_url(portal, path)
    nav_links = "".join(
        f'<a href="{html.escape(route)}"{" class=\"active\"" if route == path else ""}>{html.escape(label)}</a>'
        for route, label in PUBLIC_NAV
    )
    section_html = "".join(
        f"""
        <section class="card">
          <h2>{html.escape(section['heading'])}</h2>
          <p>{html.escape(section['content'])}</p>
        </section>
        """
        for section in page["sections"]
    )
    status_card = f"""
    <section class="status-card">
      <span class="pill">public portal</span>
      <span class="pill">protected control plane</span>
      <span class="pill">download gate: {html.escape(portal.download_gate_state)}</span>
      <p>Reference status: {html.escape(str(snapshot['safe_reference_status'].get('status', 'unknown')))} in mode {html.escape(str(snapshot['safe_reference_status'].get('mode', 'unknown')))}.</p>
      <p>Selected subdomain: {html.escape(portal.selected_subdomain)}</p>
    </section>
    """
    json_ld = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "SoftwareApplication",
            "name": portal.product_name,
            "applicationCategory": "BusinessApplication",
            "description": page["description"],
            "url": canonical_url,
            "operatingSystem": "Web",
        }
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{html.escape(page['title'])}</title>
  <meta name="description" content="{html.escape(page['description'])}" />
  <link rel="canonical" href="{html.escape(canonical_url)}" />
  <meta property="og:type" content="website" />
  <meta property="og:title" content="{html.escape(page['title'])}" />
  <meta property="og:description" content="{html.escape(page['description'])}" />
  <meta property="og:url" content="{html.escape(canonical_url)}" />
  <meta property="og:site_name" content="{html.escape(portal.product_name)}" />
  <meta name="twitter:card" content="summary_large_image" />
  <script type="application/ld+json">{json_ld}</script>
  <style>
    :root {{
      --bg: #f3efe7;
      --ink: #171311;
      --muted: #655d58;
      --panel: rgba(255, 250, 242, 0.92);
      --line: rgba(100, 74, 50, 0.18);
      --accent: #9c4b18;
      --accent-dark: #6e3310;
      --gold: #d8b36b;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      color: var(--ink);
      font-family: Georgia, "Times New Roman", serif;
      background:
        radial-gradient(circle at top right, rgba(216,179,107,0.22), transparent 35%),
        radial-gradient(circle at top left, rgba(156,75,24,0.14), transparent 30%),
        linear-gradient(180deg, #f9f5ed 0%, var(--bg) 100%);
    }}
    header {{
      padding: 28px 24px 22px;
      border-bottom: 1px solid var(--line);
      background: rgba(255, 248, 238, 0.88);
      backdrop-filter: blur(10px);
      position: sticky;
      top: 0;
    }}
    .brand {{
      font-size: 13px;
      letter-spacing: 0.18em;
      text-transform: uppercase;
      color: var(--accent);
      font-weight: 700;
      margin-bottom: 10px;
    }}
    nav {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 16px;
    }}
    nav a {{
      color: var(--ink);
      text-decoration: none;
      padding: 8px 10px;
      border-bottom: 2px solid transparent;
      font-weight: 700;
    }}
    nav a.active {{
      border-color: var(--accent);
      color: var(--accent-dark);
    }}
    .hero {{
      padding: 42px 24px 18px;
      display: grid;
      grid-template-columns: 1.3fr 0.9fr;
      gap: 24px;
      align-items: start;
    }}
    .hero h1 {{
      margin: 0 0 14px;
      font-size: clamp(38px, 6vw, 68px);
      line-height: 0.98;
      letter-spacing: -0.03em;
      max-width: 12ch;
    }}
    .hero p {{
      font-size: 20px;
      line-height: 1.5;
      color: var(--muted);
      max-width: 38rem;
    }}
    .status-card {{
      background: linear-gradient(160deg, rgba(255,255,255,0.95), rgba(255,243,225,0.92));
      border: 1px solid var(--line);
      padding: 20px;
      box-shadow: 0 20px 34px rgba(40, 23, 9, 0.09);
    }}
    .pill {{
      display: inline-block;
      margin: 0 8px 8px 0;
      padding: 6px 10px;
      border: 1px solid rgba(156,75,24,0.24);
      color: var(--accent-dark);
      background: rgba(156,75,24,0.08);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      font-weight: 700;
    }}
    main {{
      padding: 12px 24px 42px;
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 18px;
    }}
    .card {{
      background: var(--panel);
      border: 1px solid var(--line);
      padding: 20px;
      box-shadow: 0 18px 30px rgba(45, 30, 20, 0.08);
      min-height: 180px;
    }}
    .card h2 {{
      margin-top: 0;
      margin-bottom: 12px;
      font-size: 21px;
    }}
    .card p {{
      margin: 0;
      line-height: 1.6;
      color: var(--muted);
    }}
    footer {{
      padding: 0 24px 34px;
      color: var(--muted);
      font-size: 14px;
    }}
    @media (max-width: 860px) {{
      .hero {{
        grid-template-columns: 1fr;
      }}
      .hero h1 {{
        max-width: none;
      }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="brand">{html.escape(portal.product_name)}</div>
    <nav>{nav_links}</nav>
  </header>
  <section class="hero">
    <div>
      <h1>{html.escape(page['hero'])}</h1>
      <p>{html.escape(page['lede'])}</p>
    </div>
    {status_card}
  </section>
  <main>{section_html}</main>
  <footer>
    Public product portal for {html.escape(portal.selected_subdomain)}. Protected operator, control-plane and customer execution functions remain non-public.
  </footer>
</body>
</html>"""


def _render_plain_html(title: str, text: str) -> str:
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8" /><title>{html.escape(title)}</title></head><body><h1>{html.escape(title)}</h1><p>{html.escape(text)}</p></body></html>"""


def render_robots_txt(portal: PublicPortalConfig) -> str:
    return textwrap.dedent(
        f"""\
        User-agent: *
        Allow: /
        Disallow: /operator
        Disallow: /admin
        Disallow: /control-plane
        Disallow: /console
        Disallow: /api/
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
    }


def resolve_portal_request(
    path: str,
    workspace_root: Path,
    config: AppConfig,
    portal: PublicPortalConfig,
) -> PortalResponse:
    route = urlsplit(path).path or "/"
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

    page_map = _page_copy(portal, build_public_portal_snapshot(workspace_root, config, portal))
    if route not in page_map:
        body = _render_plain_html(
            "Not Found",
            "The requested portal page does not exist.",
        ).encode("utf-8")
        return PortalResponse(HTTPStatus.NOT_FOUND, "text/html; charset=utf-8", body)

    snapshot = build_public_portal_snapshot(workspace_root, config, portal)
    page = page_map[route]
    return PortalResponse(200, "text/html; charset=utf-8", _render_layout(portal, route, page, snapshot).encode("utf-8"))


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

    def _send_response(self, response: PortalResponse) -> None:
        self.send_response(response.status)
        self.send_header("Content-Type", response.content_type)
        self.send_header("Content-Length", str(len(response.body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'unsafe-inline'; img-src 'self' data:;")
        self.end_headers()
        self.wfile.write(response.body)

    def do_HEAD(self) -> None:
        response = resolve_portal_request(
            self.path,
            self.server.workspace_root,
            self.server.app_config,
            self.server.portal_config,
        )
        self.send_response(response.status)
        self.send_header("Content-Type", response.content_type)
        self.send_header("Content-Length", str(len(response.body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'unsafe-inline'; img-src 'self' data:;")
        self.end_headers()

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
