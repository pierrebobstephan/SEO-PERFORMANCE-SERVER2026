<?php

if (!defined('ABSPATH')) {
    exit;
}

class HSO_Bridge_Config
{
    private const OPERATOR_INPUTS_OPTION = 'hso_bridge_operator_inputs';
    private const SOURCE_MAPPING_OPTION = 'hso_bridge_source_mapping';

    private array $config = array();

    public function load(): array
    {
        if (!empty($this->config)) {
            return $this->config;
        }

        $config = $this->default_config();
        $path = HSO_PLUGIN_DIR . 'config/bridge-config.json';
        if (file_exists($path)) {
            $raw = file_get_contents($path);
            if ($raw !== false) {
                $decoded = json_decode($raw, true);
                if (is_array($decoded)) {
                    $config = array_merge($config, $decoded);
                }
            }
        }

        $config['operator_inputs'] = array_merge(
            (array) ($config['operator_inputs'] ?? array()),
            $this->load_local_override(self::OPERATOR_INPUTS_OPTION)
        );
        $config['source_mapping'] = array_merge(
            (array) ($config['source_mapping'] ?? array()),
            $this->load_local_override(self::SOURCE_MAPPING_OPTION)
        );

        $config['allowed_scopes'] = array_values(array_filter(array_map('strval', (array) ($config['allowed_scopes'] ?? array()))));
        $config['allowed_features'] = array_values(array_filter(array_map('strval', (array) ($config['allowed_features'] ?? array()))));
        $config['required_features'] = array_values(array_filter(array_map('strval', (array) ($config['required_features'] ?? array()))));
        $config['current_blockers'] = array_values(array_filter(array_map('strval', (array) ($config['current_blockers'] ?? array()))));
        $config['stop_conditions'] = array_values(array_filter(array_map('strval', (array) ($config['stop_conditions'] ?? array()))));
        $config['bound_domain'] = $this->normalize_domain((string) ($config['bound_domain'] ?? ''));
        $config['allowed_subdomains'] = $this->normalize_allowed_subdomains(
            $config['bound_domain'],
            (array) ($config['allowed_subdomains'] ?? array())
        );
        $config['customer_id'] = $this->normalize_string_field($config, 'customer_id');
        $config['product_id'] = $this->normalize_string_field($config, 'product_id');
        $config['issued_at'] = $this->normalize_string_field($config, 'issued_at');
        $config['expires_at'] = $this->normalize_string_field($config, 'expires_at');
        $config['non_expiring'] = !array_key_exists('non_expiring', $config) || !empty($config['non_expiring']);
        $config['integrity'] = $this->normalize_integrity((array) ($config['integrity'] ?? array()));
        $config['doctrine'] = $this->normalize_doctrine_profile((array) ($config['doctrine'] ?? array()));
        $config['operator_inputs'] = $this->normalize_operator_inputs((array) ($config['operator_inputs'] ?? array()));
        $config['source_mapping'] = $this->normalize_source_mapping((array) ($config['source_mapping'] ?? array()));
        $config['customer_visibility'] = $this->normalize_customer_visibility((array) ($config['customer_visibility'] ?? array()));
        $config['protected_fulfillment'] = $this->normalize_protected_fulfillment((array) ($config['protected_fulfillment'] ?? array()));
        $config['local_report_ingest'] = $this->normalize_local_report_ingest((array) ($config['local_report_ingest'] ?? array()));

        $this->config = $config;
        return $this->config;
    }

    public function build_license_seed(): array
    {
        $config = $this->load();

        return array(
            'license_id' => (string) ($config['license_id'] ?? 'TBD'),
            'customer_id' => (string) ($config['customer_id'] ?? 'operator input required'),
            'product_id' => (string) ($config['product_id'] ?? 'hso-plugin'),
            'status' => (string) ($config['status'] ?? 'approval_required'),
            'bound_domain' => (string) ($config['bound_domain'] ?? ''),
            'allowed_subdomains' => (array) ($config['allowed_subdomains'] ?? array()),
            'allowed_scopes' => (array) ($config['allowed_scopes'] ?? array()),
            'allowed_features' => (array) ($config['allowed_features'] ?? array()),
            'release_channel' => (string) ($config['release_channel'] ?? 'pilot'),
            'policy_channel' => (string) ($config['policy_channel'] ?? 'pilot'),
            'rollback_profile_id' => (string) ($config['rollback_profile_id'] ?? 'TBD'),
            'issued_at' => (string) ($config['issued_at'] ?? ''),
            'non_expiring' => !empty($config['non_expiring']),
            'expires_at' => (string) ($config['expires_at'] ?? ''),
            'integrity' => (array) ($config['integrity'] ?? array()),
            'operator_inputs_complete' => !empty($config['operator_inputs_complete']),
            'operator_inputs' => (array) ($config['operator_inputs'] ?? array()),
        );
    }

    public function build_connection_state(string $current_domain): array
    {
        $config = $this->load();
        $bound_domain = $this->normalize_domain((string) ($config['bound_domain'] ?? ''));
        $current_domain = $this->normalize_domain($current_domain);

        return array(
            'connection_mode' => (string) ($config['suite_connection_mode'] ?? 'packaged_preview_only'),
            'readiness' => (string) ($config['suite_connection_readiness'] ?? 'packaged_preview_ready'),
            'bound_domain' => $bound_domain,
            'current_domain' => $current_domain,
            'domain_match' => $bound_domain !== '' && $current_domain === $bound_domain,
            'expected_home_url' => (string) ($config['expected_home_url'] ?? ''),
            'expected_scoped_page_url' => (string) ($config['expected_scoped_page_url'] ?? ''),
            'default_mode' => (string) ($config['default_mode'] ?? 'safe_mode'),
            'fallback_mode' => (string) ($config['fallback_mode'] ?? 'observe_only'),
            'current_blockers' => (array) ($config['current_blockers'] ?? array()),
            'staging_only' => !empty($config['staging_only']),
        );
    }

    public function persist_packaged_profile(): void
    {
        if (!function_exists('update_option')) {
            return;
        }

        update_option('hso_bridge_profile_snapshot', $this->load(), false);
    }

    public function persist_operator_inputs(array $inputs): void
    {
        if (!function_exists('update_option')) {
            return;
        }

        update_option(self::OPERATOR_INPUTS_OPTION, $this->normalize_operator_inputs($inputs), false);
        $this->config = array();
    }

    public function persist_source_mapping(array $source_mapping): void
    {
        if (!function_exists('update_option')) {
            return;
        }

        update_option(self::SOURCE_MAPPING_OPTION, $this->normalize_source_mapping($source_mapping), false);
        $this->config = array();
    }

    private function default_config(): array
    {
        return array(
            'schema_version' => 1,
            'bridge_profile' => 'source not yet confirmed',
            'bridge_label' => 'Site Optimizer Bridge',
            'staging_only' => true,
            'suite_connection_mode' => 'packaged_preview_only',
            'suite_connection_readiness' => 'packaged_preview_ready',
            'license_id' => 'TBD',
            'customer_id' => 'operator input required',
            'product_id' => 'hso-plugin',
            'status' => 'approval_required',
            'bound_domain' => '',
            'allowed_subdomains' => array(),
            'path_base' => '/',
            'expected_home_url' => '',
            'expected_scoped_page_url' => '',
            'release_channel' => 'pilot',
            'policy_channel' => 'pilot',
            'rollback_profile_id' => 'TBD',
            'allowed_features' => array('meta_description'),
            'issued_at' => '',
            'non_expiring' => true,
            'expires_at' => '',
            'integrity' => array(
                'signature' => 'source not yet confirmed',
                'signature_state' => 'operator_signing_required',
                'signing_key_reference' => 'local_server_signing_key',
            ),
            'doctrine' => array(
                'policy_version' => '8.0',
                'ai_system_id' => 'wordpress_bridge_plugin',
                'risk_class' => 'R1',
                'impact_assessment_ref' => 'ia-wordpress-bridge-plugin-v1',
                'provenance_state' => 'packaged_preview_attested',
                'supply_chain_state' => 'local_signed_delivery_prep',
                'human_oversight_state' => 'server_and_operator_governed',
                'fallback_rule' => 'observe_only_safe_mode_or_approval_required_until_green',
            ),
            'default_mode' => 'safe_mode',
            'fallback_mode' => 'observe_only',
            'allowed_scopes' => array('homepage_only'),
            'required_features' => array('meta_description'),
            'scope_confirmed' => false,
            'source_mapping_confirmed' => false,
            'operator_inputs_complete' => false,
            'operator_inputs' => array(
                'wordpress_version' => '',
                'active_theme' => '',
                'active_builder' => '',
                'active_seo_plugin' => '',
                'plugin_inventory' => array(),
                'backup_confirmation' => '',
                'restore_confirmation' => '',
                'rollback_owner' => 'server_managed_bridge',
                'validation_owner' => 'server_managed_bridge',
            ),
            'source_mapping' => array(
                'homepage_meta_description_single' => false,
                'head_meta_output_single' => false,
                'double_output_detected' => false,
                'double_output_verification' => 'not_detected',
                'operator_confirmation' => false,
                'notes' => array('source mapping is not yet confirmed'),
            ),
            'customer_visibility' => array(
                'surface_mode' => 'protected_admin_only',
                'subscription_status' => 'approval_required',
                'renewal_state' => 'operator review required',
                'renewal_window_state' => 'not_open',
                'failed_payment_recovery_state' => 'not_needed',
                'domain_scope_summary' => 'source not yet confirmed',
                'documentation_access' => 'source not yet confirmed',
                'licensed_download_access' => 'approval_required',
                'license_integrity_state' => 'operator signing required',
                'support_state' => 'email support active',
                'support_email' => 'pierre.stephan1@electri-c-ity-studios.com',
                'activation_state' => 'approval_required',
                'customer_visibility_note' => 'source not yet confirmed',
                'subscription_lifecycle_note' => 'source not yet confirmed',
            ),
            'protected_fulfillment' => array(
                'delivery_channel' => 'protected_local_only',
                'public_delivery' => false,
                'customer_login' => false,
                'license_api_exposed' => false,
                'install_pack_state' => 'approval_required',
                'manifest_state' => 'approval_required',
                'rollback_state' => 'approval_required',
                'signature_prep_state' => 'operator signing required',
                'signing_key_reference' => 'operator input required',
                'replay_protection_state' => 'operator input required',
                'delivery_grant_state' => 'approval_required',
                'customer_release_decision_state' => 'approval_required',
                'renewal_delivery_state' => 'approval_required',
                'failed_payment_recovery_delivery_state' => 'approval_required',
            ),
            'local_report_ingest' => array(
                'enabled' => false,
                'path' => '',
                'bundled_snapshot_path' => '',
                'report_id' => '',
            ),
            'optimization_stage' => 'stage1_readiness_only',
            'optimization_readiness' => 'approval_required',
            'current_blockers' => array('operator input required'),
            'stop_conditions' => array('fatal error', 'visible page damage'),
        );
    }

    private function normalize_domain(string $domain): string
    {
        $domain = strtolower(trim($domain));
        $domain = preg_replace('#^https?://#', '', $domain);
        return trim((string) $domain, '/');
    }

    private function normalize_operator_inputs(array $inputs): array
    {
        return array(
            'wordpress_version' => $this->normalize_string_field($inputs, 'wordpress_version'),
            'active_theme' => $this->normalize_string_field($inputs, 'active_theme'),
            'active_builder' => $this->normalize_string_field($inputs, 'active_builder'),
            'active_seo_plugin' => $this->normalize_string_field($inputs, 'active_seo_plugin'),
            'plugin_inventory' => array_values(array_filter(array_map('strval', (array) ($inputs['plugin_inventory'] ?? array())))),
            'backup_confirmation' => $this->normalize_string_field($inputs, 'backup_confirmation'),
            'restore_confirmation' => $this->normalize_string_field($inputs, 'restore_confirmation'),
            'rollback_owner' => 'server_managed_bridge',
            'validation_owner' => 'server_managed_bridge',
        );
    }

    private function normalize_source_mapping(array $source_mapping): array
    {
        $double_output_detected = !empty($source_mapping['double_output_detected']);

        return array(
            'homepage_meta_description_single' => !empty($source_mapping['homepage_meta_description_single']),
            'head_meta_output_single' => !empty($source_mapping['head_meta_output_single']),
            'double_output_detected' => $double_output_detected,
            'double_output_verification' => $this->normalize_duplicate_output_verification(
                isset($source_mapping['double_output_verification']) ? (string) $source_mapping['double_output_verification'] : '',
                $double_output_detected
            ),
            'operator_confirmation' => !empty($source_mapping['operator_confirmation']),
            'notes' => array_values(array_filter(array_map('strval', (array) ($source_mapping['notes'] ?? array())))),
        );
    }

    private function normalize_integrity(array $integrity): array
    {
        return array(
            'signature' => $this->normalize_string_field($integrity, 'signature'),
            'signature_state' => $this->normalize_string_field($integrity, 'signature_state'),
            'signing_key_reference' => $this->normalize_string_field($integrity, 'signing_key_reference'),
        );
    }

    private function normalize_doctrine_profile(array $doctrine): array
    {
        return array(
            'policy_version' => $this->normalize_string_field($doctrine, 'policy_version'),
            'ai_system_id' => $this->normalize_string_field($doctrine, 'ai_system_id'),
            'risk_class' => $this->normalize_string_field($doctrine, 'risk_class'),
            'impact_assessment_ref' => $this->normalize_string_field($doctrine, 'impact_assessment_ref'),
            'provenance_state' => $this->normalize_string_field($doctrine, 'provenance_state'),
            'supply_chain_state' => $this->normalize_string_field($doctrine, 'supply_chain_state'),
            'human_oversight_state' => $this->normalize_string_field($doctrine, 'human_oversight_state'),
            'fallback_rule' => $this->normalize_string_field($doctrine, 'fallback_rule'),
        );
    }

    private function normalize_local_report_ingest(array $ingest): array
    {
        return array(
            'enabled' => !empty($ingest['enabled']),
            'path' => $this->normalize_string_field($ingest, 'path'),
            'bundled_snapshot_path' => $this->normalize_string_field($ingest, 'bundled_snapshot_path'),
            'report_id' => $this->normalize_string_field($ingest, 'report_id'),
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

    private function normalize_customer_visibility(array $customer_visibility): array
    {
        return array(
            'surface_mode' => $this->normalize_string_field($customer_visibility, 'surface_mode'),
            'subscription_status' => $this->normalize_string_field($customer_visibility, 'subscription_status'),
            'renewal_state' => $this->normalize_string_field($customer_visibility, 'renewal_state'),
            'renewal_window_state' => $this->normalize_string_field($customer_visibility, 'renewal_window_state'),
            'failed_payment_recovery_state' => $this->normalize_string_field($customer_visibility, 'failed_payment_recovery_state'),
            'domain_scope_summary' => $this->normalize_string_field($customer_visibility, 'domain_scope_summary'),
            'documentation_access' => $this->normalize_string_field($customer_visibility, 'documentation_access'),
            'licensed_download_access' => $this->normalize_string_field($customer_visibility, 'licensed_download_access'),
            'license_integrity_state' => $this->normalize_string_field($customer_visibility, 'license_integrity_state'),
            'support_state' => $this->normalize_string_field($customer_visibility, 'support_state'),
            'support_email' => $this->normalize_string_field($customer_visibility, 'support_email'),
            'activation_state' => $this->normalize_string_field($customer_visibility, 'activation_state'),
            'customer_visibility_note' => $this->normalize_string_field($customer_visibility, 'customer_visibility_note'),
            'subscription_lifecycle_note' => $this->normalize_string_field($customer_visibility, 'subscription_lifecycle_note'),
        );
    }

    private function normalize_protected_fulfillment(array $protected_fulfillment): array
    {
        return array(
            'delivery_channel' => $this->normalize_string_field($protected_fulfillment, 'delivery_channel'),
            'public_delivery' => !empty($protected_fulfillment['public_delivery']),
            'customer_login' => !empty($protected_fulfillment['customer_login']),
            'license_api_exposed' => !empty($protected_fulfillment['license_api_exposed']),
            'install_pack_state' => $this->normalize_string_field($protected_fulfillment, 'install_pack_state'),
            'manifest_state' => $this->normalize_string_field($protected_fulfillment, 'manifest_state'),
            'rollback_state' => $this->normalize_string_field($protected_fulfillment, 'rollback_state'),
            'signature_prep_state' => $this->normalize_string_field($protected_fulfillment, 'signature_prep_state'),
            'signing_key_reference' => $this->normalize_string_field($protected_fulfillment, 'signing_key_reference'),
            'replay_protection_state' => $this->normalize_string_field($protected_fulfillment, 'replay_protection_state'),
            'delivery_grant_state' => $this->normalize_string_field($protected_fulfillment, 'delivery_grant_state'),
            'customer_release_decision_state' => $this->normalize_string_field($protected_fulfillment, 'customer_release_decision_state'),
            'renewal_delivery_state' => $this->normalize_string_field($protected_fulfillment, 'renewal_delivery_state'),
            'failed_payment_recovery_delivery_state' => $this->normalize_string_field($protected_fulfillment, 'failed_payment_recovery_delivery_state'),
        );
    }

    private function normalize_string_field(array $payload, string $key): string
    {
        return isset($payload[$key]) ? trim((string) $payload[$key]) : '';
    }

    private function normalize_allowed_subdomains(string $bound_domain, array $allowed_subdomains): array
    {
        $normalized = array();
        foreach ($allowed_subdomains as $item) {
            $candidate = $this->normalize_domain((string) $item);
            if ($candidate === '' || !$this->is_explicit_descendant($candidate, $bound_domain)) {
                continue;
            }
            $normalized[$candidate] = $candidate;
        }

        return array_values($normalized);
    }

    private function is_explicit_descendant(string $candidate, string $bound_domain): bool
    {
        if ($candidate === '' || $bound_domain === '' || $candidate === $bound_domain) {
            return false;
        }

        return str_ends_with($candidate, '.' . $bound_domain);
    }

    private function load_local_override(string $option_name): array
    {
        if (!function_exists('get_option')) {
            return array();
        }

        $value = get_option($option_name, array());
        return is_array($value) ? $value : array();
    }
}
