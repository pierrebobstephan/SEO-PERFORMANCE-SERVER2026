<?php

if (!defined('ABSPATH')) {
    exit;
}

class HSO_Admin_Screen
{
    private array $runtime_context;
    private array $license_state;
    private array $conflict_state;
    private array $validation_snapshot;

    public function __construct(
        array $runtime_context,
        array $license_state,
        array $conflict_state,
        array $validation_snapshot
    ) {
        $this->runtime_context = $runtime_context;
        $this->license_state = $license_state;
        $this->conflict_state = $conflict_state;
        $this->validation_snapshot = $validation_snapshot;
    }

    public function register(): void
    {
        add_action('admin_menu', array($this, 'add_menu'));
    }

    public function add_menu(): void
    {
        add_management_page(
            'Hetzner SEO Ops',
            'Hetzner SEO Ops',
            'manage_options',
            'hetzner-seo-ops',
            array($this, 'render')
        );
    }

    public function render(): void
    {
        if (!current_user_can('manage_options')) {
            return;
        }

        echo '<div class="wrap">';
        echo '<h1>Hetzner SEO Ops</h1>';
        echo '<p>Doctrine-enforced plugin blueprint. The plugin remains observe-only or safe-mode until license, domain, source mapping, validation, and rollback gates are satisfied.</p>';
        echo '<h2>Runtime</h2>';
        echo '<pre>' . esc_html(wp_json_encode($this->runtime_context, JSON_PRETTY_PRINT)) . '</pre>';
        echo '<h2>License Status</h2>';
        echo '<pre>' . esc_html(wp_json_encode($this->license_state, JSON_PRETTY_PRINT)) . '</pre>';
        echo '<h2>Conflict State</h2>';
        echo '<pre>' . esc_html(wp_json_encode($this->conflict_state, JSON_PRETTY_PRINT)) . '</pre>';
        echo '<h2>Validation Snapshot</h2>';
        echo '<pre>' . esc_html(wp_json_encode($this->validation_snapshot, JSON_PRETTY_PRINT)) . '</pre>';
        echo '</div>';
    }
}
