<?php

if (!defined('ABSPATH')) {
    exit;
}

class HSO_Baseline_Capture
{
    private array $bridge_profile;

    public function __construct(array $bridge_profile)
    {
        $this->bridge_profile = $bridge_profile;
    }

    public function capture(array $license_state, array $conflict_state): array
    {
        $expected_home_url = (string) ($this->bridge_profile['expected_home_url'] ?? '');
        $expected_scoped_page_url = (string) ($this->bridge_profile['expected_scoped_page_url'] ?? '');
        $home_option = $this->string_option('home');
        $siteurl_option = $this->string_option('siteurl');
        $current_home_url = function_exists('home_url') ? (string) home_url('/') : '';
        $example_page = $this->capture_example_page($expected_scoped_page_url);

        $residuals = array();
        if ($expected_home_url !== '' && !$this->urls_match($home_option, $expected_home_url)) {
            $residuals[] = 'home option does not match expected home url';
        }
        if ($expected_home_url !== '' && !$this->urls_match($siteurl_option, $expected_home_url)) {
            $residuals[] = 'siteurl option does not match expected home url';
        }
        if ($expected_home_url !== '' && !$this->urls_match($current_home_url, $expected_home_url)) {
            $residuals[] = 'current home url does not match expected home url';
        }
        if (!$example_page['found']) {
            $residuals[] = 'scoped example page is missing';
        }
        if ($expected_scoped_page_url !== '' && $example_page['found'] && !$this->urls_match($example_page['permalink'], $expected_scoped_page_url)) {
            $residuals[] = 'scoped example page permalink does not match expected example page url';
        }
        if ($example_page['contains_localhost']) {
            $residuals[] = 'example page content still contains localhost reference';
        }
        if ($example_page['dashboard_hint_contains_localhost']) {
            $residuals[] = 'example page dashboard hint still points to localhost';
        }

        return array(
            'captured' => true,
            'captured_at' => gmdate('c'),
            'home_option' => $home_option,
            'siteurl_option' => $siteurl_option,
            'current_home_url' => $current_home_url,
            'expected_home_url' => $expected_home_url,
            'expected_scoped_page_url' => $expected_scoped_page_url,
            'domain_match' => !empty($license_state['domain_match']),
            'active_seo_plugins' => (array) ($conflict_state['active_seo_plugins'] ?? array()),
            'active_builders' => (array) ($conflict_state['active_builders'] ?? array()),
            'theme_name' => (string) ($conflict_state['theme_name'] ?? 'source not yet confirmed'),
            'example_page' => $example_page,
            'url_normalization_clean' => empty($residuals),
            'url_normalization_residuals' => $residuals,
        );
    }

    public function persist_snapshot(array $snapshot): void
    {
        if (!function_exists('update_option')) {
            return;
        }

        update_option('hso_baseline_snapshot', $snapshot, false);
    }

    private function capture_example_page(string $expected_scoped_page_url): array
    {
        $slug = $this->extract_slug($expected_scoped_page_url);
        $snapshot = array(
            'slug' => $slug,
            'found' => false,
            'permalink' => '',
            'contains_localhost' => false,
            'dashboard_hint_contains_localhost' => false,
        );

        if ($slug === '' || !function_exists('get_page_by_path')) {
            return $snapshot;
        }

        $page = get_page_by_path($slug, OBJECT, 'page');
        if (!is_object($page) || !isset($page->post_content)) {
            return $snapshot;
        }

        $content = (string) $page->post_content;
        $permalink = $this->safe_permalink($page, $expected_scoped_page_url);
        $dashboard_localhost = strpos($content, 'Dashboard') !== false && strpos($content, 'localhost') !== false;
        if (!$dashboard_localhost && strpos($content, 'dein Dashboard') !== false && strpos($content, 'localhost') !== false) {
            $dashboard_localhost = true;
        }

        return array(
            'slug' => $slug,
            'found' => true,
            'permalink' => $permalink,
            'contains_localhost' => strpos($content, 'localhost') !== false,
            'dashboard_hint_contains_localhost' => $dashboard_localhost,
        );
    }

    private function extract_slug(string $url): string
    {
        $path = (string) wp_parse_url($url, PHP_URL_PATH);
        $path = trim($path, '/');
        if ($path === '') {
            return '';
        }

        $segments = explode('/', $path);
        return (string) end($segments);
    }

    private function string_option(string $key): string
    {
        if (!function_exists('get_option')) {
            return '';
        }

        $value = get_option($key, '');
        return is_string($value) ? $value : '';
    }

    private function urls_match(string $left, string $right): bool
    {
        return $this->normalize_url($left) === $this->normalize_url($right);
    }

    private function safe_permalink($page, string $fallback): string
    {
        if (!function_exists('get_permalink')) {
            return $fallback;
        }

        if (!function_exists('did_action') || did_action('init') <= 0) {
            return $fallback;
        }

        global $wp_rewrite;
        if (!is_object($wp_rewrite)) {
            return $fallback;
        }

        try {
            $permalink = get_permalink($page);
        } catch (Throwable $throwable) {
            return $fallback;
        }

        return is_string($permalink) && $permalink !== '' ? $permalink : $fallback;
    }

    private function normalize_url(string $url): string
    {
        return rtrim(trim($url), '/');
    }
}
