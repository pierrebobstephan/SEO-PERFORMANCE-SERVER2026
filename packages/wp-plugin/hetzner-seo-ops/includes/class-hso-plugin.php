<?php

if (!defined('ABSPATH')) {
    exit;
}

class HSO_Plugin
{
    private static ?HSO_Plugin $instance = null;

    private HSO_License_Check $license_check;
    private HSO_Safe_Mode $safe_mode;
    private HSO_Conflict_Detector $conflict_detector;
    private HSO_Rollback_Registry $rollback_registry;
    private HSO_Validation_Status $validation_status;
    private array $runtime_context = array();
    private array $license_state = array();
    private array $conflict_state = array();

    public static function boot(): HSO_Plugin
    {
        if (self::$instance === null) {
            self::$instance = new self();
            self::$instance->register();
        }

        return self::$instance;
    }

    private function __construct()
    {
        $this->license_check = new HSO_License_Check();
        $this->safe_mode = new HSO_Safe_Mode();
        $this->conflict_detector = new HSO_Conflict_Detector();
        $this->rollback_registry = new HSO_Rollback_Registry();
        $this->validation_status = new HSO_Validation_Status();
    }

    private function register(): void
    {
        $current_domain = $this->detect_current_domain();
        $this->license_state = $this->license_check->evaluate_domain($current_domain);
        $this->conflict_state = $this->conflict_detector->scan();

        $mode = $this->determine_mode($this->license_state, $this->conflict_state);
        $safe_state = $this->safe_mode->build_state($mode, $this->license_state, $this->conflict_state);

        $this->runtime_context = array(
            'plugin_version' => HSO_PLUGIN_VERSION,
            'current_domain' => $current_domain,
            'mode' => $mode,
            'bound_domain' => isset($this->license_state['bound_domain']) ? (string) $this->license_state['bound_domain'] : '',
            'release_channel' => isset($this->license_state['release_channel']) ? (string) $this->license_state['release_channel'] : 'pilot',
            'allowed_scopes' => isset($this->license_state['allowed_scopes']) ? (array) $this->license_state['allowed_scopes'] : array(),
            'source_mapping_confirmed' => false,
            'scope_confirmed' => false,
            'target_meta_description' => '',
            'safe_state' => $safe_state,
        );

        $validation_snapshot = $this->validation_status->build_snapshot($mode, $this->license_state, $this->conflict_state);
        $this->validation_status->set_snapshot($validation_snapshot);

        $admin_screen = new HSO_Admin_Screen(
            $this->runtime_context,
            $this->license_state,
            $this->conflict_state,
            $validation_snapshot
        );
        $admin_screen->register();

        $meta_description_module = new HSO_Meta_Description_Module(
            $this->runtime_context,
            $this->conflict_state,
            $this->rollback_registry,
            $this->validation_status
        );
        $meta_description_module->register();
    }

    private function determine_mode(array $license_state, array $conflict_state): string
    {
        if (!empty($conflict_state['has_blocking_conflict'])) {
            return 'safe_mode';
        }

        if (empty($license_state['bound_domain']) || empty($license_state['domain_match'])) {
            return 'observe_only';
        }

        $status = isset($license_state['status']) ? (string) $license_state['status'] : 'approval_required';
        if (in_array($status, array('inactive', 'revoked'), true)) {
            return 'observe_only';
        }

        if ($status !== 'active_scoped') {
            return 'approval_required';
        }

        if (!empty($conflict_state['source_mapping_unclear'])) {
            return 'approval_required';
        }

        return 'active_scoped';
    }

    private function detect_current_domain(): string
    {
        if (function_exists('home_url')) {
            $host = wp_parse_url(home_url('/'), PHP_URL_HOST);
            if (is_string($host)) {
                return strtolower($host);
            }
        }

        return '';
    }
}
