<?php

if (!defined('ABSPATH')) {
    exit;
}

class HSO_Plugin
{
    private static ?HSO_Plugin $instance = null;

    private HSO_Bridge_Config $bridge_config;
    private HSO_Baseline_Capture $baseline_capture;
    private HSO_Optimization_Gate $optimization_gate;
    private HSO_License_Check $license_check;
    private HSO_Safe_Mode $safe_mode;
    private HSO_Conflict_Detector $conflict_detector;
    private HSO_Rollback_Registry $rollback_registry;
    private HSO_Validation_Status $validation_status;
    private HSO_Recommendation_Action_Center $recommendation_action_center;
    private array $bridge_profile = array();
    private array $connection_state = array();
    private array $baseline_snapshot = array();
    private array $optimization_state = array();
    private array $runtime_context = array();
    private array $license_state = array();
    private array $conflict_state = array();
    private array $operator_input_state = array();
    private array $source_mapping_state = array();
    private array $runtime_blockers = array();

    public static function activate(): void
    {
        $bridge_config = new HSO_Bridge_Config();
        $bridge_config->persist_packaged_profile();

        if (!function_exists('update_option')) {
            return;
        }

        update_option('hso_local_license_snapshot', $bridge_config->build_license_seed(), false);
        update_option('hso_activation_ready', array(
            'plugin_version' => HSO_PLUGIN_VERSION,
            'bound_domain' => (string) ($bridge_config->load()['bound_domain'] ?? ''),
            'default_mode' => (string) ($bridge_config->load()['default_mode'] ?? 'safe_mode'),
            'activated_at' => gmdate('c'),
        ), false);
    }

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
        $this->bridge_config = new HSO_Bridge_Config();
        $this->license_check = new HSO_License_Check();
        $this->safe_mode = new HSO_Safe_Mode();
        $this->conflict_detector = new HSO_Conflict_Detector();
        $this->rollback_registry = new HSO_Rollback_Registry();
        $this->validation_status = new HSO_Validation_Status();
        $this->optimization_gate = new HSO_Optimization_Gate();
        $this->bridge_profile = $this->bridge_config->load();
        $this->baseline_capture = new HSO_Baseline_Capture($this->bridge_profile);
    }

    private function register(): void
    {
        $current_domain = $this->detect_current_domain();
        $this->license_state = $this->license_check->evaluate_domain($current_domain, $this->bridge_config->build_license_seed());
        $this->conflict_state = $this->conflict_detector->scan();
        $this->connection_state = $this->bridge_config->build_connection_state($current_domain);
        $this->baseline_snapshot = $this->baseline_capture->capture($this->license_state, $this->conflict_state);
        $this->baseline_capture->persist_snapshot($this->baseline_snapshot);
        $this->operator_input_state = $this->build_operator_input_state($this->bridge_profile, $this->conflict_state);
        $this->license_state['operator_inputs_complete'] = !empty($this->operator_input_state['complete']);
        $this->source_mapping_state = $this->build_source_mapping_state($this->bridge_profile, $this->conflict_state, $this->baseline_snapshot);
        $this->runtime_blockers = $this->build_runtime_blockers(
            $this->bridge_profile,
            $this->license_state,
            $this->conflict_state,
            $this->baseline_snapshot,
            $this->operator_input_state,
            $this->source_mapping_state
        );

        $mode = $this->determine_mode(
            $this->license_state,
            $this->conflict_state,
            $this->bridge_profile,
            $this->baseline_snapshot,
            $this->source_mapping_state
        );
        $safe_state = $this->safe_mode->build_state(
            $mode,
            $this->license_state,
            $this->conflict_state,
            $this->baseline_snapshot,
            $this->bridge_profile,
            $this->runtime_blockers
        );
        $this->optimization_state = $this->optimization_gate->evaluate(
            $mode,
            $this->license_state,
            $this->conflict_state,
            $this->baseline_snapshot,
            $this->bridge_profile,
            $this->operator_input_state,
            $this->source_mapping_state,
            $this->runtime_blockers
        );
        $next_smallest_safe_step = $this->derive_next_smallest_safe_step(
            $this->operator_input_state,
            $this->source_mapping_state,
            $this->optimization_state
        );

        $this->runtime_context = array(
            'plugin_version' => HSO_PLUGIN_VERSION,
            'current_domain' => $current_domain,
            'current_home_url' => isset($this->baseline_snapshot['current_home_url']) ? (string) $this->baseline_snapshot['current_home_url'] : '',
            'path_base' => isset($this->bridge_profile['path_base']) ? (string) $this->bridge_profile['path_base'] : '/',
            'mode' => $mode,
            'default_mode' => (string) ($this->bridge_profile['default_mode'] ?? 'safe_mode'),
            'fallback_mode' => (string) ($this->bridge_profile['fallback_mode'] ?? 'observe_only'),
            'bound_domain' => isset($this->license_state['bound_domain']) ? (string) $this->license_state['bound_domain'] : '',
            'domain_match' => !empty($this->license_state['domain_match']),
            'release_channel' => isset($this->license_state['release_channel']) ? (string) $this->license_state['release_channel'] : 'pilot',
            'allowed_scopes' => isset($this->license_state['allowed_scopes']) ? (array) $this->license_state['allowed_scopes'] : array(),
            'required_features' => isset($this->bridge_profile['required_features']) ? (array) $this->bridge_profile['required_features'] : array(),
            'source_mapping_confirmed' => !empty($this->source_mapping_state['confirmed']),
            'scope_confirmed' => !empty($this->bridge_profile['scope_confirmed']),
            'operator_inputs_complete' => !empty($this->operator_input_state['complete']),
            'target_meta_description' => '',
            'suite_connection_readiness' => isset($this->connection_state['readiness']) ? (string) $this->connection_state['readiness'] : 'packaged_preview_ready',
            'url_normalization_clean' => !empty($this->baseline_snapshot['url_normalization_clean']),
            'baseline_captured' => !empty($this->baseline_snapshot['captured']),
            'staging_only' => !empty($this->bridge_profile['staging_only']),
            'open_blockers' => isset($this->runtime_blockers['open']) ? (array) $this->runtime_blockers['open'] : array(),
            'heuristic_findings' => isset($this->runtime_blockers['heuristic']) ? (array) $this->runtime_blockers['heuristic'] : array(),
            'resolved_blockers' => isset($this->runtime_blockers['resolved']) ? (array) $this->runtime_blockers['resolved'] : array(),
            'next_smallest_safe_step' => $next_smallest_safe_step,
            'operator_input_state' => $this->operator_input_state,
            'source_mapping_state' => $this->source_mapping_state,
            'safe_state' => $safe_state,
            'optimization_state' => $this->optimization_state,
            'readiness_summary' => $this->build_readiness_summary($mode, $this->optimization_state, $this->runtime_blockers),
            'innovation_control_deck' => $this->build_innovation_control_deck(
                $mode,
                $this->license_state,
                $this->conflict_state,
                $this->operator_input_state,
                $this->source_mapping_state,
                $this->optimization_state,
                $this->runtime_blockers,
                $next_smallest_safe_step
            ),
            'installed_suite_insights' => $this->build_installed_suite_insights(
                $mode,
                $this->license_state,
                $this->baseline_snapshot,
                $this->operator_input_state,
                $this->source_mapping_state,
                $this->optimization_state,
                $this->runtime_blockers
            ),
            'license_domain_scope_panel' => $this->build_license_domain_scope_panel(
                $current_domain,
                $this->license_state,
                $this->baseline_snapshot
            ),
            'installation_health_signals' => $this->build_installation_health_signals(
                $mode,
                $this->conflict_state,
                $this->baseline_snapshot,
                $this->operator_input_state,
                $this->source_mapping_state,
                $this->optimization_state,
                $this->runtime_blockers
            ),
            'doctrine_runtime_state' => $this->build_doctrine_runtime_state(
                $mode,
                $this->license_state,
                $this->optimization_state
            ),
            'production_cutover_checklist' => $this->build_production_cutover_checklist(
                $this->license_state,
                $this->baseline_snapshot,
                $this->conflict_state,
                $this->operator_input_state,
                $this->source_mapping_state,
                $this->optimization_state
            ),
            'customer_subscription_visibility' => $this->build_customer_subscription_visibility(
                $current_domain,
                $this->license_state,
                $this->baseline_snapshot
            ),
            'protected_delivery_status' => $this->build_protected_delivery_status(
                $this->optimization_state,
                $this->runtime_blockers
            ),
            'reference_pilot_runtime_snapshot' => $this->build_reference_pilot_runtime_snapshot(
                $current_domain,
                $mode,
                $next_smallest_safe_step,
                $this->license_state,
                $this->conflict_state,
                $this->baseline_snapshot,
                $this->operator_input_state,
                $this->source_mapping_state,
                $this->optimization_state,
                $this->runtime_blockers
            ),
        );

        $this->recommendation_action_center = new HSO_Recommendation_Action_Center(
            $this->runtime_context,
            $this->bridge_profile,
            $this->conflict_state,
            $this->validation_status,
            $this->rollback_registry
        );
        $this->recommendation_action_center->register_entries();
        $this->runtime_context['recommendation_action_center'] = $this->recommendation_action_center->build_snapshot();

        $validation_snapshot = $this->validation_status->build_snapshot(
            $mode,
            $this->license_state,
            $this->conflict_state,
            $this->baseline_snapshot,
            $this->optimization_state,
            $this->connection_state,
            $this->operator_input_state,
            $this->source_mapping_state,
            $this->runtime_blockers
        );
        $this->validation_status->set_snapshot($validation_snapshot);

        $admin_screen = new HSO_Admin_Screen(
            $this->runtime_context,
            $this->bridge_profile,
            $this->license_state,
            $this->connection_state,
            $this->conflict_state,
            $this->baseline_snapshot,
            $this->optimization_state,
            $validation_snapshot,
            $this->recommendation_action_center
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

    private function determine_mode(
        array $license_state,
        array $conflict_state,
        array $bridge_profile,
        array $baseline_snapshot,
        array $source_mapping_state = array()
    ): string
    {
        $default_mode = isset($bridge_profile['default_mode']) ? (string) $bridge_profile['default_mode'] : 'safe_mode';

        if (!empty($conflict_state['has_blocking_conflict'])) {
            return 'safe_mode';
        }

        if (empty($license_state['bound_domain']) || empty($license_state['domain_match'])) {
            return 'observe_only';
        }

        if (!empty($baseline_snapshot) && empty($baseline_snapshot['url_normalization_clean'])) {
            return 'safe_mode';
        }

        $status = isset($license_state['status']) ? (string) $license_state['status'] : 'approval_required';
        if (in_array($status, array('inactive', 'revoked'), true)) {
            return 'observe_only';
        }

        if ($status !== 'active_scoped') {
            if (in_array($default_mode, array('safe_mode', 'observe_only', 'approval_required'), true)) {
                return $default_mode;
            }
            return 'approval_required';
        }

        if (!empty($conflict_state['source_mapping_unclear'])) {
            return 'approval_required';
        }

        if (!empty($conflict_state['external_seo_owner_active'])) {
            return 'approval_required';
        }

        if (!$this->license_signature_trusted($license_state)) {
            return 'safe_mode';
        }

        if (!$this->channel_allows_active_scoped(isset($license_state['release_channel']) ? (string) $license_state['release_channel'] : '')) {
            return 'observe_only';
        }

        if (
            !$this->channel_allows_active_scoped(isset($license_state['policy_channel']) ? (string) $license_state['policy_channel'] : '')
            || empty($license_state['rollback_profile_id'])
            || empty($license_state['operator_inputs_complete'])
        ) {
            return 'approval_required';
        }

        if (empty($source_mapping_state['confirmed']) || empty($bridge_profile['scope_confirmed'])) {
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

    private function build_operator_input_state(array $bridge_profile, array $conflict_state): array
    {
        $configured = isset($bridge_profile['operator_inputs']) && is_array($bridge_profile['operator_inputs'])
            ? $bridge_profile['operator_inputs']
            : array();

        $plugin_inventory = isset($configured['plugin_inventory']) && is_array($configured['plugin_inventory']) && !empty($configured['plugin_inventory'])
            ? array_values(array_map('strval', $configured['plugin_inventory']))
            : array_values(array_map('strval', (array) ($conflict_state['active_plugins'] ?? array())));

        $fields = array(
            'wordpress_version' => $this->first_complete_string(
                isset($configured['wordpress_version']) ? (string) $configured['wordpress_version'] : '',
                function_exists('get_bloginfo') ? (string) get_bloginfo('version') : ''
            ),
            'active_theme' => $this->first_complete_string(
                isset($configured['active_theme']) ? (string) $configured['active_theme'] : '',
                isset($conflict_state['theme_name']) ? (string) $conflict_state['theme_name'] : ''
            ),
            'active_builder' => $this->first_complete_string(
                isset($configured['active_builder']) ? (string) $configured['active_builder'] : '',
                $this->first_detected_plugin((array) ($conflict_state['active_builders'] ?? array()), 'none')
            ),
            'active_seo_plugin' => $this->first_complete_string(
                isset($configured['active_seo_plugin']) ? (string) $configured['active_seo_plugin'] : '',
                $this->first_detected_plugin((array) ($conflict_state['active_seo_plugins'] ?? array()), 'none')
            ),
            'plugin_inventory' => $plugin_inventory,
            'backup_confirmation' => trim((string) ($configured['backup_confirmation'] ?? '')),
            'restore_confirmation' => trim((string) ($configured['restore_confirmation'] ?? '')),
            'rollback_owner' => trim((string) ($configured['rollback_owner'] ?? '')),
            'validation_owner' => trim((string) ($configured['validation_owner'] ?? '')),
        );
        $server_managed_fields = array();
        foreach (array('rollback_owner', 'validation_owner') as $field) {
            if ($this->is_server_managed_value(isset($fields[$field]) ? (string) $fields[$field] : '')) {
                $server_managed_fields[] = $field;
            }
        }

        $missing_fields = array();
        foreach ($fields as $field => $value) {
            if (!$this->input_value_complete($field, $value)) {
                $missing_fields[] = $field;
            }
        }

        return array(
            'fields' => $fields,
            'required_fields' => array_keys($fields),
            'server_managed_fields' => $server_managed_fields,
            'missing_fields' => $missing_fields,
            'complete' => empty($missing_fields),
        );
    }

    private function build_source_mapping_state(
        array $bridge_profile,
        array $conflict_state,
        array $baseline_snapshot
    ): array {
        $configured = isset($bridge_profile['source_mapping']) && is_array($bridge_profile['source_mapping'])
            ? $bridge_profile['source_mapping']
            : array();

        $homepage_meta_description_single = !empty($configured['homepage_meta_description_single']);
        $head_meta_output_single = !empty($configured['head_meta_output_single']);
        $double_output_detected = !empty($configured['double_output_detected']);
        $double_output_verification = $this->normalize_duplicate_output_verification(
            isset($configured['double_output_verification']) ? (string) $configured['double_output_verification'] : '',
            $double_output_detected
        );
        $operator_confirmation = !empty($configured['operator_confirmation']);
        $external_seo_owner_active = !empty($conflict_state['external_seo_owner_active']);
        $external_seo_owner_plugin = isset($conflict_state['single_seo_plugin_slug'])
            ? (string) $conflict_state['single_seo_plugin_slug']
            : '';
        $coexistence_mode = isset($conflict_state['coexistence_mode'])
            ? (string) $conflict_state['coexistence_mode']
            : 'no_external_seo_owner';

        $missing_requirements = array();
        $blocking_requirements = array();
        $heuristic_requirements = array();
        $coexistence_advisories = array();
        if (!$homepage_meta_description_single) {
            $blocking_requirements[] = 'homepage meta description ownership is not yet confirmed';
        }
        if (!$head_meta_output_single) {
            $blocking_requirements[] = 'head/meta output is not yet confirmed as single-source';
        }
        if ($double_output_detected && $double_output_verification === 'confirmed_runtime_output') {
            $blocking_requirements[] = 'duplicate head or meta output is present';
        } elseif ($double_output_detected) {
            $heuristic_requirements[] = 'duplicate head or meta output remains a heuristic suspicion';
        }
        if (!empty($conflict_state['source_mapping_unclear'])) {
            $blocking_requirements[] = 'another SEO ownership source is still active';
        } elseif ($external_seo_owner_active) {
            $coexistence_advisories[] = $external_seo_owner_plugin !== ''
                ? 'controlled coexistence is active with ' . $external_seo_owner_plugin . '; the bridge stays bounded and does not take over live output'
                : 'controlled coexistence is active with another SEO owner; the bridge stays bounded and does not take over live output';
        }
        if (!$operator_confirmation) {
            $blocking_requirements[] = 'operator source mapping confirmation is still required';
        }
        if (!empty($baseline_snapshot) && empty($baseline_snapshot['captured'])) {
            $blocking_requirements[] = 'baseline snapshot is not yet captured';
        }

        $notes = array_values(array_filter(array_map('strval', (array) ($configured['notes'] ?? array()))));
        $notes = array_values(array_unique(array_merge($notes, $coexistence_advisories)));
        $missing_requirements = array_values(array_unique(array_merge($blocking_requirements, $heuristic_requirements)));
        $confirmed = empty($blocking_requirements);
        $duplicate_output_status = 'not_detected';
        $duplicate_output_basis = 'no duplicate head or meta output is currently recorded';
        if ($double_output_detected && $double_output_verification === 'confirmed_runtime_output') {
            $duplicate_output_status = 'confirmed_runtime_output';
            $duplicate_output_basis = 'duplicate head or meta output is treated as a confirmed runtime finding and remains a real blocker';
        } elseif ($double_output_detected) {
            $duplicate_output_status = 'heuristic_suspected';
            $duplicate_output_basis = 'duplicate head or meta output is only heuristically suspected and still needs verification';
        }

        return array(
            'confirmed' => $confirmed,
            'homepage_meta_description_single' => $homepage_meta_description_single,
            'head_meta_output_single' => $head_meta_output_single,
            'double_output_detected' => $double_output_detected && $double_output_verification === 'confirmed_runtime_output',
            'double_output_signal_present' => $double_output_detected,
            'double_output_verification' => $double_output_verification,
            'duplicate_output_status' => $duplicate_output_status,
            'duplicate_output_basis' => $duplicate_output_basis,
            'hard_blocking_duplicate_output' => $double_output_detected && $double_output_verification === 'confirmed_runtime_output',
            'heuristic_duplicate_output' => $double_output_detected && $double_output_verification === 'heuristic_suspected',
            'external_seo_owner_active' => $external_seo_owner_active,
            'external_seo_owner_plugin' => $external_seo_owner_plugin,
            'coexistence_mode' => $coexistence_mode,
            'coexistence_advisories' => array_values(array_unique($coexistence_advisories)),
            'operator_confirmation' => $operator_confirmation,
            'notes' => $notes,
            'blocking_requirements' => array_values(array_unique($blocking_requirements)),
            'heuristic_requirements' => array_values(array_unique($heuristic_requirements)),
            'missing_requirements' => $missing_requirements,
        );
    }

    private function build_runtime_blockers(
        array $bridge_profile,
        array $license_state,
        array $conflict_state,
        array $baseline_snapshot,
        array $operator_input_state,
        array $source_mapping_state
    ): array {
        $open = array();
        $heuristic = array();
        $resolved = array();
        $packaged = array_values(array_map('strval', (array) ($bridge_profile['current_blockers'] ?? array())));

        foreach ($packaged as $blocker) {
            if ($this->is_localhost_blocker_resolved($blocker, $baseline_snapshot)) {
                $resolved[] = $blocker;
            }
        }

        if (empty($license_state['domain_match'])) {
            $open[] = 'bound domain is missing or mismatched';
        }
        if (empty($baseline_snapshot['url_normalization_clean'])) {
            $open[] = 'url normalization is not yet clean';
        } elseif (!empty($resolved)) {
            $resolved[] = 'example page dashboard hint still points to localhost';
        }
        if (!empty($conflict_state['has_blocking_conflict'])) {
            $open[] = 'blocking plugin conflict is present';
        }

        $missing_inputs = (array) ($operator_input_state['missing_fields'] ?? array());
        if (array_intersect($missing_inputs, array('wordpress_version', 'active_theme', 'active_builder', 'active_seo_plugin', 'plugin_inventory'))) {
            $open[] = 'wordpress environment inventory is not yet complete';
        }
        if (array_intersect($missing_inputs, array('backup_confirmation', 'restore_confirmation', 'rollback_owner', 'validation_owner'))) {
            $open[] = $this->describe_operator_input_blocker($missing_inputs);
        }

        if (!empty($source_mapping_state['blocking_requirements'])) {
            $open[] = 'source mapping confirmation is not yet complete';
        }
        if (!empty($source_mapping_state['hard_blocking_duplicate_output'])) {
            $open[] = 'duplicate head or meta output is confirmed in runtime output';
        }
        if (!empty($source_mapping_state['heuristic_requirements'])) {
            $heuristic[] = 'duplicate head or meta output remains unverified and should be checked before broader changes';
        }
        if (!empty($source_mapping_state['operator_confirmation']) && empty($bridge_profile['source_mapping_confirmed'])) {
            $resolved[] = 'stale packaged source mapping confirmation requirement has been cleared by runtime state';
        }

        return array(
            'open' => array_values(array_unique($open)),
            'heuristic' => array_values(array_unique($heuristic)),
            'resolved' => array_values(array_unique($resolved)),
            'packaged' => $packaged,
        );
    }

    private function build_readiness_summary(string $mode, array $optimization_state, array $runtime_blockers): array
    {
        $blocked = !empty($runtime_blockers['open']) && ($optimization_state['eligibility'] ?? 'blocked') === 'blocked';
        $current_status = 'safe_to_observe';
        if ($blocked) {
            $current_status = 'blocked';
        } elseif (($optimization_state['eligibility'] ?? 'recommend_only') === 'reversible_change_ready') {
            $current_status = 'ready_for_reversible_change_ready';
        } elseif (($optimization_state['eligibility'] ?? 'recommend_only') === 'recommend_only') {
            $current_status = 'ready_for_recommend_only';
        }

        return array(
            'current_status' => $current_status,
            'safe_to_observe' => in_array($mode, array('safe_mode', 'observe_only', 'approval_required'), true),
            'ready_for_recommend_only' => in_array($optimization_state['eligibility'] ?? 'recommend_only', array('recommend_only', 'reversible_change_ready'), true),
            'ready_for_reversible_change_ready' => ($optimization_state['eligibility'] ?? 'recommend_only') === 'reversible_change_ready',
            'blocked' => $blocked,
            'heuristic_review_required' => !empty($runtime_blockers['heuristic']),
        );
    }

    private function build_reference_pilot_runtime_snapshot(
        string $current_domain,
        string $mode,
        string $next_smallest_safe_step,
        array $license_state,
        array $conflict_state,
        array $baseline_snapshot,
        array $operator_input_state,
        array $source_mapping_state,
        array $optimization_state,
        array $runtime_blockers
    ): array {
        $notes = array('Captured from the installed Site Optimizer Bridge runtime context.');
        if ($next_smallest_safe_step !== '') {
            $notes[] = 'Next smallest safe step: ' . $next_smallest_safe_step;
        }

        return array(
            'schema_version' => 1,
            'source' => 'installed_bridge_runtime_snapshot',
            'status' => 'captured_from_installed_bridge',
            'captured_at' => gmdate('c'),
            'bound_domain' => isset($license_state['bound_domain']) ? (string) $license_state['bound_domain'] : '',
            'current_domain' => $current_domain,
            'path_base' => isset($this->bridge_profile['path_base']) ? (string) $this->bridge_profile['path_base'] : '/',
            'domain_match' => !empty($license_state['domain_match']),
            'url_normalization_clean' => !empty($baseline_snapshot['url_normalization_clean']),
            'baseline_captured' => !empty($baseline_snapshot['captured']),
            'blocking_conflicts' => !empty($conflict_state['has_blocking_conflict']) ? 'blocked' : 'green',
            'mode' => $mode,
            'optimization_gate' => isset($optimization_state['eligibility']) ? (string) $optimization_state['eligibility'] : 'blocked',
            'operator_inputs_complete' => !empty($operator_input_state['complete']),
            'source_mapping_confirmed' => !empty($source_mapping_state['confirmed']),
            'open_blockers' => array_values(array_unique(array_map('strval', (array) ($runtime_blockers['open'] ?? array())))),
            'next_smallest_safe_step' => $next_smallest_safe_step,
            'notes' => $notes,
        );
    }

    private function normalize_duplicate_output_verification(string $value, bool $double_output_detected): string
    {
        $normalized = strtolower(trim($value));
        if (!$double_output_detected) {
            return 'not_detected';
        }

        if (in_array($normalized, array('heuristic_suspected', 'confirmed_runtime_output'), true)) {
            return $normalized;
        }

        return 'confirmed_runtime_output';
    }

    private function derive_next_smallest_safe_step(
        array $operator_input_state,
        array $source_mapping_state,
        array $optimization_state
    ): string {
        $missing_inputs = array_values(array_map('strval', (array) ($operator_input_state['missing_fields'] ?? array())));
        if (in_array('backup_confirmation', $missing_inputs, true) || in_array('restore_confirmation', $missing_inputs, true)) {
            return 'record backup and restore confirmation in the staging-only operator inputs';
        }

        if (!empty($source_mapping_state['hard_blocking_duplicate_output'])) {
            return 'verify the duplicate head or meta output in the rendered page output and keep the bridge in safe_mode until it is cleared';
        }

        if (!empty($source_mapping_state['heuristic_duplicate_output'])) {
            return 'verify whether the suspected duplicate head or meta output is real before changing the gate';
        }

        if (in_array('operator source mapping confirmation is still required', (array) ($source_mapping_state['blocking_requirements'] ?? array()), true)) {
            return 'confirm source mapping explicitly in the staging-only admin surface';
        }

        if (!empty($source_mapping_state['external_seo_owner_active'])) {
            return 'continue in recommend_only under controlled SEO coexistence and keep live output ownership with the active SEO plugin';
        }

        if (($optimization_state['eligibility'] ?? 'recommend_only') === 'reversible_change_ready') {
            return 'stay in staging, validate the reversible homepage meta preparation path, and keep rollback ready';
        }

        return 'continue in recommend_only and keep the bridge observable until the next green gate is justified';
    }

    private function describe_operator_input_blocker(array $missing_inputs): string
    {
        $relevant = array_values(array_intersect(
            array_map('strval', $missing_inputs),
            array('backup_confirmation', 'restore_confirmation', 'rollback_owner', 'validation_owner')
        ));
        sort($relevant);

        if ($relevant === array('backup_confirmation', 'restore_confirmation')) {
            return 'backup and restore confirmation are not yet recorded';
        }

        return 'backup, restore, rollback owner, and validation owner are not yet confirmed';
    }

    private function first_complete_string(string $configured, string $fallback): string
    {
        if ($this->string_is_complete($configured)) {
            return trim($configured);
        }

        if ($this->string_is_complete($fallback)) {
            return trim($fallback);
        }

        return '';
    }

    private function first_detected_plugin(array $plugins, string $fallback): string
    {
        foreach ($plugins as $plugin) {
            $value = trim((string) $plugin);
            if ($value !== '') {
                return $value;
            }
        }

        return $fallback;
    }

    private function input_value_complete(string $field, $value): bool
    {
        if ($field === 'plugin_inventory') {
            return is_array($value) && !empty($value);
        }

        return $this->string_is_complete((string) $value);
    }

    private function string_is_complete(string $value): bool
    {
        $normalized = strtolower(trim($value));
        if ($normalized === '') {
            return false;
        }

        return !in_array($normalized, array(
            'tbd',
            'source not yet confirmed',
            'operator input required',
            'approval_required',
            'blocked',
        ), true);
    }

    private function is_server_managed_value(string $value): bool
    {
        return strtolower(trim($value)) === 'server_managed_bridge';
    }

    private function is_localhost_blocker_resolved(string $blocker, array $baseline_snapshot): bool
    {
        $normalized = strtolower($blocker);
        if (strpos($normalized, 'localhost') === false) {
            return false;
        }

        $example_page = isset($baseline_snapshot['example_page']) && is_array($baseline_snapshot['example_page'])
            ? $baseline_snapshot['example_page']
            : array();

        return !empty($baseline_snapshot['url_normalization_clean'])
            && empty($example_page['contains_localhost'])
            && empty($example_page['dashboard_hint_contains_localhost']);
    }

    private function build_installed_suite_insights(
        string $mode,
        array $license_state,
        array $baseline_snapshot,
        array $operator_input_state,
        array $source_mapping_state,
        array $optimization_state,
        array $runtime_blockers
    ): array {
        $fields = isset($operator_input_state['fields']) && is_array($operator_input_state['fields'])
            ? $operator_input_state['fields']
            : array();
        $eligibility = isset($optimization_state['eligibility']) ? (string) $optimization_state['eligibility'] : 'recommend_only';
        $domain_match = !empty($license_state['domain_match']);
        $url_clean = !empty($baseline_snapshot['url_normalization_clean']);
        $baseline_captured = !empty($baseline_snapshot['captured']);

        return array(
            'status_overview' => array(
                'mode' => $mode,
                'optimization_eligibility' => $eligibility,
                'domain_binding' => $domain_match ? 'green' : 'blocked',
                'url_normalization' => $url_clean ? 'green' : 'blocked',
                'baseline_capture' => $baseline_captured ? 'captured' : 'pending',
                'source_mapping' => !empty($source_mapping_state['heuristic_requirements'])
                    ? 'heuristic_review_required'
                    : (!empty($source_mapping_state['confirmed']) ? 'confirmed' : 'needs_confirmation'),
                'operator_inputs' => !empty($operator_input_state['complete']) ? 'complete' : 'needs_completion',
            ),
            'subscription_and_scope' => array(
                'plugin_version' => HSO_PLUGIN_VERSION,
                'license_id' => isset($license_state['license_id']) ? (string) $license_state['license_id'] : '',
                'customer_id' => isset($license_state['customer_id']) ? (string) $license_state['customer_id'] : '',
                'product_id' => isset($license_state['product_id']) ? (string) $license_state['product_id'] : '',
                'bound_domain' => isset($license_state['bound_domain']) ? (string) $license_state['bound_domain'] : '',
                'release_channel' => isset($license_state['release_channel']) ? (string) $license_state['release_channel'] : 'pilot',
                'allowed_scopes' => isset($license_state['allowed_scopes']) ? (array) $license_state['allowed_scopes'] : array(),
                'allowed_features' => isset($license_state['allowed_features']) ? (array) $license_state['allowed_features'] : array(),
                'issued_at' => isset($license_state['issued_at']) ? (string) $license_state['issued_at'] : '',
                'non_expiring' => !empty($license_state['non_expiring']),
                'required_features' => isset($this->bridge_profile['required_features']) ? (array) $this->bridge_profile['required_features'] : array(),
                'operating_model' => 'bounded, explainable and reversible',
                'buyer_visibility_surface' => 'installed_suite_insights_active',
            ),
            'environment' => array(
                'wordpress_version' => isset($fields['wordpress_version']) ? (string) $fields['wordpress_version'] : '',
                'active_theme' => isset($fields['active_theme']) ? (string) $fields['active_theme'] : '',
                'active_builder' => isset($fields['active_builder']) ? (string) $fields['active_builder'] : '',
                'active_seo_plugin' => isset($fields['active_seo_plugin']) ? (string) $fields['active_seo_plugin'] : '',
                'plugin_inventory' => isset($fields['plugin_inventory']) ? (array) $fields['plugin_inventory'] : array(),
                'rollback_owner' => isset($fields['rollback_owner']) ? (string) $fields['rollback_owner'] : '',
                'validation_owner' => isset($fields['validation_owner']) ? (string) $fields['validation_owner'] : '',
                'server_managed_fields' => isset($operator_input_state['server_managed_fields']) ? (array) $operator_input_state['server_managed_fields'] : array(),
                'autonomy_model' => 'safe_mode first, controlled progression only after green gates',
                'trust_model' => 'zero-trust validation and rollback-first discipline',
            ),
            'baseline' => array(
                'current_home_url' => isset($baseline_snapshot['current_home_url']) ? (string) $baseline_snapshot['current_home_url'] : '',
                'expected_home_url' => isset($baseline_snapshot['expected_home_url']) ? (string) $baseline_snapshot['expected_home_url'] : '',
                'expected_scoped_page_url' => isset($baseline_snapshot['expected_scoped_page_url']) ? (string) $baseline_snapshot['expected_scoped_page_url'] : '',
                'captured_at' => isset($baseline_snapshot['captured_at']) ? (string) $baseline_snapshot['captured_at'] : '',
                'current_gate' => $eligibility,
                'explainability_state' => !empty($source_mapping_state['confirmed']) ? 'mapped_and_explainable' : 'waiting_for_source_mapping_confirmation',
                'duplicate_output_status' => isset($source_mapping_state['duplicate_output_status']) ? (string) $source_mapping_state['duplicate_output_status'] : 'not_detected',
                'duplicate_output_basis' => isset($source_mapping_state['duplicate_output_basis']) ? (string) $source_mapping_state['duplicate_output_basis'] : '',
            ),
            'safe_now' => array_values(array_unique(array_map('strval', (array) ($optimization_state['allowed_optimizations'] ?? array())))),
            'stays_protected' => array_values(array_unique(array_map('strval', (array) ($optimization_state['forbidden_optimizations'] ?? array())))),
            'open_blockers' => array_values(array_unique(array_map('strval', (array) ($runtime_blockers['open'] ?? array())))),
            'resolved_blockers' => array_values(array_unique(array_map('strval', (array) ($runtime_blockers['resolved'] ?? array())))),
            'next_steps' => array_values(array_unique(array_merge(
                array_map('strval', (array) ($operator_input_state['missing_fields'] ?? array())),
                array_map('strval', (array) ($source_mapping_state['missing_requirements'] ?? array()))
            ))),
        );
    }

    private function build_license_domain_scope_panel(
        string $current_domain,
        array $license_state,
        array $baseline_snapshot
    ): array {
        $doctrine = isset($this->bridge_profile['doctrine']) && is_array($this->bridge_profile['doctrine'])
            ? $this->bridge_profile['doctrine']
            : array();

        return array(
            'license_id' => isset($license_state['license_id']) ? (string) $license_state['license_id'] : '',
            'customer_id' => isset($license_state['customer_id']) ? (string) $license_state['customer_id'] : '',
            'product_id' => isset($license_state['product_id']) ? (string) $license_state['product_id'] : '',
            'subscription_status' => isset($license_state['status']) ? (string) $license_state['status'] : 'approval_required',
            'plugin_version' => HSO_PLUGIN_VERSION,
            'bound_domain' => isset($license_state['bound_domain']) ? (string) $license_state['bound_domain'] : '',
            'current_domain' => $current_domain,
            'domain_match' => !empty($license_state['domain_match']) ? 'green' : 'blocked',
            'release_channel' => isset($license_state['release_channel']) ? (string) $license_state['release_channel'] : 'pilot',
            'policy_channel' => isset($license_state['policy_channel']) ? (string) $license_state['policy_channel'] : 'pilot',
            'allowed_scopes' => isset($license_state['allowed_scopes']) ? (array) $license_state['allowed_scopes'] : array(),
            'allowed_features' => isset($license_state['allowed_features']) ? (array) $license_state['allowed_features'] : array(),
            'issued_at' => isset($license_state['issued_at']) ? (string) $license_state['issued_at'] : '',
            'non_expiring' => !empty($license_state['non_expiring']),
            'license_signature_state' => isset($license_state['integrity']['signature_state']) ? (string) $license_state['integrity']['signature_state'] : 'source not yet confirmed',
            'license_signing_key_reference' => isset($license_state['integrity']['signing_key_reference']) ? (string) $license_state['integrity']['signing_key_reference'] : 'operator input required',
            'doctrine_policy_version' => isset($doctrine['policy_version']) ? (string) $doctrine['policy_version'] : '8.0',
            'doctrine_risk_class' => isset($doctrine['risk_class']) ? (string) $doctrine['risk_class'] : 'R1',
            'impact_assessment_ref' => isset($doctrine['impact_assessment_ref']) ? (string) $doctrine['impact_assessment_ref'] : '',
            'expected_home_url' => isset($baseline_snapshot['expected_home_url']) ? (string) $baseline_snapshot['expected_home_url'] : '',
            'expected_scoped_page_url' => isset($baseline_snapshot['expected_scoped_page_url']) ? (string) $baseline_snapshot['expected_scoped_page_url'] : '',
        );
    }

    private function build_installation_health_signals(
        string $mode,
        array $conflict_state,
        array $baseline_snapshot,
        array $operator_input_state,
        array $source_mapping_state,
        array $optimization_state,
        array $runtime_blockers
    ): array {
        return array(
            'mode' => $mode,
            'baseline_captured' => !empty($baseline_snapshot['captured']) ? 'green' : 'pending',
            'url_normalization' => !empty($baseline_snapshot['url_normalization_clean']) ? 'green' : 'blocked',
            'blocking_conflicts' => !empty($conflict_state['has_blocking_conflict']) ? 'blocked' : 'green',
            'source_mapping' => !empty($source_mapping_state['heuristic_requirements'])
                ? 'heuristic_review_required'
                : (!empty($source_mapping_state['confirmed']) ? 'green' : 'needs_confirmation'),
            'operator_inputs' => !empty($operator_input_state['complete']) ? 'green' : 'needs_completion',
            'optimization_gate' => isset($optimization_state['eligibility']) ? (string) $optimization_state['eligibility'] : 'recommend_only',
            'rollback_required' => $mode === 'safe_mode' ? 'yes' : 'guarded',
            'rollback_owner' => isset($operator_input_state['fields']['rollback_owner']) ? (string) $operator_input_state['fields']['rollback_owner'] : '',
            'validation_owner' => isset($operator_input_state['fields']['validation_owner']) ? (string) $operator_input_state['fields']['validation_owner'] : '',
            'open_blocker_count' => count((array) ($runtime_blockers['open'] ?? array())),
            'resolved_blocker_count' => count((array) ($runtime_blockers['resolved'] ?? array())),
            'resilience_model' => 'rollback-first and server-managed validation',
            'buyer_visibility_state' => 'installed signals visible in protected admin',
            'explainability_state' => !empty($source_mapping_state['confirmed']) ? 'green' : 'needs_confirmation',
            'duplicate_output_status' => isset($source_mapping_state['duplicate_output_status']) ? (string) $source_mapping_state['duplicate_output_status'] : 'not_detected',
            'duplicate_output_basis' => isset($source_mapping_state['duplicate_output_basis']) ? (string) $source_mapping_state['duplicate_output_basis'] : '',
            'next_smallest_safe_step' => $this->derive_next_smallest_safe_step($operator_input_state, $source_mapping_state, $optimization_state),
        );
    }

    private function build_production_cutover_checklist(
        array $license_state,
        array $baseline_snapshot,
        array $conflict_state,
        array $operator_input_state,
        array $source_mapping_state,
        array $optimization_state
    ): array {
        $checks = array(
            array(
                'label' => 'Domain binding',
                'status' => !empty($license_state['domain_match']) ? 'green' : 'blocked',
                'detail' => !empty($license_state['domain_match']) ? 'Bound domain matches the installed WordPress host.' : 'Domain binding is not yet valid.',
            ),
            array(
                'label' => 'URL normalization',
                'status' => !empty($baseline_snapshot['url_normalization_clean']) ? 'green' : 'blocked',
                'detail' => !empty($baseline_snapshot['url_normalization_clean']) ? 'Home and scoped page URLs are normalized.' : 'Residual URL normalization issues remain present.',
            ),
            array(
                'label' => 'Baseline capture',
                'status' => !empty($baseline_snapshot['captured']) ? 'green' : 'pending',
                'detail' => !empty($baseline_snapshot['captured']) ? 'Baseline snapshot is available.' : 'Baseline evidence has not been captured yet.',
            ),
            array(
                'label' => 'Conflict picture',
                'status' => empty($conflict_state['has_blocking_conflict']) ? 'green' : 'blocked',
                'detail' => empty($conflict_state['has_blocking_conflict']) ? 'No blocking conflict is present.' : 'Blocking plugin coexistence remains unresolved.',
            ),
            array(
                'label' => 'Operator ownership inputs',
                'status' => !empty($operator_input_state['complete']) ? 'green' : 'needs_completion',
                'detail' => !empty($operator_input_state['complete']) ? 'Backup and restore are set; rollback and validation are server-managed through the bridge.' : 'Operator ownership and recovery inputs still need completion.',
            ),
            array(
                'label' => 'Source mapping confirmation',
                'status' => !empty($source_mapping_state['confirmed'])
                    ? 'green'
                    : (!empty($source_mapping_state['heuristic_requirements']) ? 'recommend_only' : 'needs_confirmation'),
                'detail' => !empty($source_mapping_state['confirmed'])
                    ? 'Single-source ownership is confirmed.'
                    : (!empty($source_mapping_state['heuristic_requirements'])
                        ? 'Source mapping is confirmed enough for recommend_only, but duplicate-output heuristics still need verification.'
                        : 'Source mapping still needs explicit confirmation.'),
            ),
            array(
                'label' => 'Reversible stage 1 gate',
                'status' => (($optimization_state['eligibility'] ?? 'recommend_only') === 'reversible_change_ready') ? 'green' : 'approval_required',
                'detail' => (($optimization_state['eligibility'] ?? 'recommend_only') === 'reversible_change_ready') ? 'Only the reversible homepage meta preparation gate is open.' : 'The installation remains below reversible stage 1.',
            ),
            array(
                'label' => 'Production cutover',
                'status' => 'approval_required',
                'detail' => 'Real production delivery, customer fulfillment, and protected release distribution remain approval-gated.',
            ),
        );

        return array(
            'cutover_ready' => false,
            'next_gate' => (($optimization_state['eligibility'] ?? 'recommend_only') === 'reversible_change_ready')
                ? 'stay_in_staging_and_validate_reversible_stage_1'
                : 'stay_in_staging_and_close_open_checks',
            'checks' => $checks,
        );
    }

    private function build_customer_subscription_visibility(
        string $current_domain,
        array $license_state,
        array $baseline_snapshot
    ): array {
        $configured = isset($this->bridge_profile['customer_visibility']) && is_array($this->bridge_profile['customer_visibility'])
            ? $this->bridge_profile['customer_visibility']
            : array();

        return array(
            'surface_mode' => isset($configured['surface_mode']) ? (string) $configured['surface_mode'] : 'protected_admin_only',
            'license_id' => isset($license_state['license_id']) ? (string) $license_state['license_id'] : '',
            'customer_id' => isset($license_state['customer_id']) ? (string) $license_state['customer_id'] : '',
            'product_id' => isset($license_state['product_id']) ? (string) $license_state['product_id'] : '',
            'subscription_status' => isset($configured['subscription_status']) ? (string) $configured['subscription_status'] : 'approval_required',
            'renewal_state' => isset($configured['renewal_state']) ? (string) $configured['renewal_state'] : 'operator_review_required',
            'renewal_window_state' => isset($configured['renewal_window_state']) ? (string) $configured['renewal_window_state'] : 'not_open',
            'failed_payment_recovery_state' => isset($configured['failed_payment_recovery_state']) ? (string) $configured['failed_payment_recovery_state'] : 'not_needed',
            'bound_domain' => isset($license_state['bound_domain']) ? (string) $license_state['bound_domain'] : '',
            'current_domain' => $current_domain,
            'domain_match' => !empty($license_state['domain_match']) ? 'green' : 'blocked',
            'issued_at' => isset($license_state['issued_at']) ? (string) $license_state['issued_at'] : '',
            'non_expiring' => !empty($license_state['non_expiring']),
            'domain_scope_summary' => isset($configured['domain_scope_summary']) ? (string) $configured['domain_scope_summary'] : 'source not yet confirmed',
            'documentation_access' => isset($configured['documentation_access']) ? (string) $configured['documentation_access'] : 'source not yet confirmed',
            'licensed_download_access' => isset($configured['licensed_download_access']) ? (string) $configured['licensed_download_access'] : 'approval_required',
            'license_integrity_state' => isset($configured['license_integrity_state']) ? (string) $configured['license_integrity_state'] : 'operator signing required',
            'support_state' => isset($configured['support_state']) ? (string) $configured['support_state'] : 'operator input required',
            'support_email' => isset($configured['support_email']) ? (string) $configured['support_email'] : '',
            'activation_state' => isset($configured['activation_state']) ? (string) $configured['activation_state'] : 'approval_required',
            'expected_home_url' => isset($baseline_snapshot['expected_home_url']) ? (string) $baseline_snapshot['expected_home_url'] : '',
            'customer_visibility_note' => isset($configured['customer_visibility_note']) ? (string) $configured['customer_visibility_note'] : 'source not yet confirmed',
            'subscription_lifecycle_note' => isset($configured['subscription_lifecycle_note']) ? (string) $configured['subscription_lifecycle_note'] : 'source not yet confirmed',
            'buyer_insight_surface' => 'license, health, delivery and cutover signals visible in protected admin',
            'guarded_automation_model' => 'observe_only or safe_mode until green gates are confirmed',
        );
    }

    private function build_protected_delivery_status(array $optimization_state, array $runtime_blockers): array
    {
        $configured = isset($this->bridge_profile['protected_fulfillment']) && is_array($this->bridge_profile['protected_fulfillment'])
            ? $this->bridge_profile['protected_fulfillment']
            : array();

        return array(
            'delivery_channel' => isset($configured['delivery_channel']) ? (string) $configured['delivery_channel'] : 'protected_local_only',
            'public_delivery' => !empty($configured['public_delivery']) ? 'enabled' : 'disabled',
            'customer_login' => !empty($configured['customer_login']) ? 'enabled' : 'disabled',
            'license_api_exposed' => !empty($configured['license_api_exposed']) ? 'enabled' : 'disabled',
            'install_pack_state' => isset($configured['install_pack_state']) ? (string) $configured['install_pack_state'] : 'approval_required',
            'manifest_state' => isset($configured['manifest_state']) ? (string) $configured['manifest_state'] : 'approval_required',
            'rollback_state' => isset($configured['rollback_state']) ? (string) $configured['rollback_state'] : 'approval_required',
            'signature_prep_state' => isset($configured['signature_prep_state']) ? (string) $configured['signature_prep_state'] : 'operator signing required',
            'signing_key_reference' => isset($configured['signing_key_reference']) ? (string) $configured['signing_key_reference'] : 'operator input required',
            'replay_protection_state' => isset($configured['replay_protection_state']) ? (string) $configured['replay_protection_state'] : 'operator input required',
            'delivery_grant_state' => isset($configured['delivery_grant_state']) ? (string) $configured['delivery_grant_state'] : 'approval_required',
            'customer_release_decision_state' => isset($configured['customer_release_decision_state']) ? (string) $configured['customer_release_decision_state'] : 'approval_required',
            'renewal_delivery_state' => isset($configured['renewal_delivery_state']) ? (string) $configured['renewal_delivery_state'] : 'approval_required',
            'failed_payment_recovery_delivery_state' => isset($configured['failed_payment_recovery_delivery_state']) ? (string) $configured['failed_payment_recovery_delivery_state'] : 'approval_required',
            'optimization_gate' => isset($optimization_state['eligibility']) ? (string) $optimization_state['eligibility'] : 'recommend_only',
            'open_blocker_count' => count((array) ($runtime_blockers['open'] ?? array())),
            'cutover_model' => 'protected delivery only after validated gates and explicit approval',
            'protected_delivery_note' => 'Delivery, activation, login, and license execution remain protected and approval-gated.',
        );
    }

    private function build_innovation_control_deck(
        string $mode,
        array $license_state,
        array $conflict_state,
        array $operator_input_state,
        array $source_mapping_state,
        array $optimization_state,
        array $runtime_blockers,
        string $next_smallest_safe_step
    ): array {
        $eligibility = isset($optimization_state['eligibility']) ? (string) $optimization_state['eligibility'] : 'blocked';
        $external_owner = isset($conflict_state['single_seo_plugin_slug']) ? (string) $conflict_state['single_seo_plugin_slug'] : 'the active SEO plugin';
        $signature_trusted = $this->license_signature_trusted($license_state);

        $execution_mode = 'bounded_observation';
        $priority_focus = 'close_runtime_gates';
        $operator_brief = 'Keep the bridge explainable and bounded until the next green gate is justified.';

        if ($eligibility === 'blocked') {
            $execution_mode = 'stabilize_and_close_gates';
            $priority_focus = 'gate_closure_and_recovery_readiness';
            $operator_brief = 'Close the remaining runtime gaps before widening any optimization surface.';
        } elseif ($eligibility === 'reversible_change_ready') {
            $execution_mode = 'reversible_stage_1_validation';
            $priority_focus = 'reversible_homepage_meta_preparation';
            $operator_brief = 'Only validate the reversible homepage preparation path and keep rollback hot.';
        } elseif (!empty($conflict_state['external_seo_owner_active'])) {
            $execution_mode = 'controlled_growth_under_external_seo_owner';
            $priority_focus = 'recommend_only_coexistence_growth';
            $operator_brief = 'Use the bridge as the decision layer while the active SEO plugin keeps live output ownership.';
        }

        $immediate_actions = array();
        if ($next_smallest_safe_step !== '') {
            $immediate_actions[] = $next_smallest_safe_step;
        }
        if ($eligibility === 'recommend_only' && !empty($conflict_state['external_seo_owner_active'])) {
            $immediate_actions[] = 'Apply approved snippet, heading and structure improvements inside the active SEO owner or theme settings, not through bridge-owned live output.';
            $immediate_actions[] = 'Use the bridge to keep recommendations prioritized, reversible and buyer-readable across the most visible public pages.';
        }
        if ($eligibility === 'reversible_change_ready') {
            $immediate_actions[] = 'Validate the reversible homepage meta preparation path before any broader scope discussion.';
        }

        $next_actions = array();
        if (!$signature_trusted) {
            $next_actions[] = 'Keep live activation approval-gated until the license signature chain is trusted.';
        }
        $next_actions[] = 'Maintain protected delivery, protected release grant and rollback discipline while the plugin remains locally bounded.';
        $next_actions[] = 'Expand only after the next gate is proven with evidence, rollback readiness and no duplicate-output regression.';

        $success_signals = array();
        if (!empty($license_state['domain_match'])) {
            $success_signals[] = 'Domain binding remains green on the licensed host.';
        }
        if (!empty($operator_input_state['complete'])) {
            $success_signals[] = 'Operator recovery inputs remain complete and server-managed fields stay protected.';
        }
        if (!empty($source_mapping_state['confirmed']) && empty($source_mapping_state['hard_blocking_duplicate_output'])) {
            $success_signals[] = 'Source mapping remains confirmed with no hard duplicate-output signal.';
        }
        if (empty($runtime_blockers['open'])) {
            $success_signals[] = 'Open blocker count remains at zero while the bridge stays bounded.';
        }
        $success_signals[] = $eligibility === 'reversible_change_ready'
            ? 'The reversible homepage preparation gate is green and still rollback-first.'
            : 'The plugin keeps recommend_only or safer without drifting into uncontrolled live execution.';

        $protected_holds = array_values(array_unique(array_filter(array_map(
            'strval',
            array_merge(
                (array) ($optimization_state['forbidden_optimizations'] ?? array()),
                array(
                    'active_scoped remains blocked until signature, approval and rollback gates are all green',
                )
            )
        ))));

        return array(
            'execution_mode' => $execution_mode,
            'priority_focus' => $priority_focus,
            'operator_brief' => $operator_brief,
            'immediate_actions' => array_values(array_unique($immediate_actions)),
            'next_actions' => array_values(array_unique($next_actions)),
            'success_signals' => array_values(array_unique($success_signals)),
            'protected_holds' => $protected_holds,
            'buyer_visibility_promise' => 'The bridge exposes explainable next steps without opening public delivery, login or uncontrolled activation.',
        );
    }

    private function build_doctrine_runtime_state(
        string $mode,
        array $license_state,
        array $optimization_state
    ): array {
        $configured = isset($this->bridge_profile['doctrine']) && is_array($this->bridge_profile['doctrine'])
            ? $this->bridge_profile['doctrine']
            : array();

        return array(
            'policy_version' => isset($configured['policy_version']) ? (string) $configured['policy_version'] : '8.0',
            'ai_system_id' => isset($configured['ai_system_id']) ? (string) $configured['ai_system_id'] : 'wordpress_bridge_plugin',
            'risk_class' => isset($configured['risk_class']) ? (string) $configured['risk_class'] : 'R1',
            'impact_assessment_ref' => isset($configured['impact_assessment_ref']) ? (string) $configured['impact_assessment_ref'] : '',
            'provenance_state' => isset($configured['provenance_state']) ? (string) $configured['provenance_state'] : '',
            'supply_chain_state' => isset($configured['supply_chain_state']) ? (string) $configured['supply_chain_state'] : '',
            'human_oversight_state' => isset($configured['human_oversight_state']) ? (string) $configured['human_oversight_state'] : '',
            'fallback_rule' => isset($configured['fallback_rule']) ? (string) $configured['fallback_rule'] : '',
            'license_signature_state' => isset($license_state['integrity']['signature_state']) ? (string) $license_state['integrity']['signature_state'] : 'source not yet confirmed',
            'runtime_mode' => $mode,
            'optimization_gate' => isset($optimization_state['eligibility']) ? (string) $optimization_state['eligibility'] : 'blocked',
        );
    }

    private function license_signature_trusted(array $license_state): bool
    {
        $signature_state = strtolower(trim((string) ($license_state['integrity']['signature_state'] ?? '')));
        return in_array($signature_state, array('trusted', 'verified', 'green', 'active'), true);
    }

    private function channel_allows_active_scoped(string $channel): bool
    {
        return in_array(strtolower(trim($channel)), array('pilot', 'stable'), true);
    }
}
