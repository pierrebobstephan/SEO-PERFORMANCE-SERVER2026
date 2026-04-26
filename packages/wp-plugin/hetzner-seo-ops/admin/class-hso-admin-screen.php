<?php

if (!defined('ABSPATH')) {
    exit;
}

class HSO_Admin_Screen
{
    private const OPERATOR_INPUTS_NONCE = 'hso_save_operator_inputs';
    private const SOURCE_MAPPING_NONCE = 'hso_save_source_mapping';
    private const APPLY_RESOLUTION_NONCE = 'hso_apply_resolution_candidate';
    private const ROLLBACK_RESOLUTION_NONCE = 'hso_rollback_resolution_candidate';

    private array $runtime_context;
    private array $bridge_profile;
    private array $license_state;
    private array $connection_state;
    private array $conflict_state;
    private array $baseline_snapshot;
    private array $optimization_state;
    private array $validation_snapshot;
    private HSO_Recommendation_Action_Center $recommendation_action_center;

    public function __construct(
        array $runtime_context,
        array $bridge_profile,
        array $license_state,
        array $connection_state,
        array $conflict_state,
        array $baseline_snapshot,
        array $optimization_state,
        array $validation_snapshot,
        HSO_Recommendation_Action_Center $recommendation_action_center
    ) {
        $this->runtime_context = $runtime_context;
        $this->bridge_profile = $bridge_profile;
        $this->license_state = $license_state;
        $this->connection_state = $connection_state;
        $this->conflict_state = $conflict_state;
        $this->baseline_snapshot = $baseline_snapshot;
        $this->optimization_state = $optimization_state;
        $this->validation_snapshot = $validation_snapshot;
        $this->recommendation_action_center = $recommendation_action_center;
    }

    public function register(): void
    {
        add_action('admin_menu', array($this, 'add_menu'));
        add_action('admin_init', array($this, 'handle_post'));
    }

    public function add_menu(): void
    {
        add_menu_page(
            'Site Optimizer',
            'Site Optimizer',
            'manage_options',
            'hetzner-seo-ops',
            array($this, 'render'),
            'dashicons-admin-tools',
            58
        );
    }

    public function render(): void
    {
        if (!current_user_can('manage_options')) {
            return;
        }

        echo '<div class="wrap">';
        echo '<h1>Site Optimizer Bridge</h1>';
        echo '<p>Doctrine-enforced staging bridge. The plugin stays in observe_only or safe_mode until domain binding, baseline, conflict picture, validation, and rollback gates are satisfied. The operating model is intentionally bounded, explainable and reversible.</p>';
        $this->render_notice();
        $this->render_installed_suite_insights();
        $this->render_innovation_control_deck();
        $this->render_recommendation_action_center();
        $this->render_post_purchase_visibility_layer();
        echo '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:16px;margin:16px 0;">';
        $this->render_operator_inputs_form();
        $this->render_source_mapping_form();
        echo '</div>';
        echo '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px;margin:16px 0;">';
        $this->render_card('Readiness Summary', (array) ($this->runtime_context['readiness_summary'] ?? array()));
        $this->render_card('Open Blockers', array('open_blockers' => (array) ($this->runtime_context['open_blockers'] ?? array())));
        $this->render_card('Unresolved Heuristic Findings', array('heuristic_findings' => (array) ($this->runtime_context['heuristic_findings'] ?? array())));
        $this->render_card('Resolved Blockers', array('resolved_blockers' => (array) ($this->runtime_context['resolved_blockers'] ?? array())));
        $this->render_card('Next Smallest Safe Step', array('next_smallest_safe_step' => (string) ($this->runtime_context['next_smallest_safe_step'] ?? '')));
        $this->render_card('Required Operator Inputs', (array) ($this->runtime_context['operator_input_state'] ?? array()));
        $this->render_card('Source Mapping Status', (array) ($this->runtime_context['source_mapping_state'] ?? array()));
        $this->render_card('Optimization Gate', $this->optimization_state);
        $this->render_card('Runtime', $this->runtime_context);
        $this->render_card('Bridge Profile', $this->bridge_profile);
        $this->render_card('License Status', $this->license_state);
        $this->render_card('Suite Connection', $this->connection_state);
        $this->render_card('Conflict Snapshot', $this->conflict_state);
        $this->render_card('Baseline Snapshot', $this->baseline_snapshot);
        $this->render_card('Validation Snapshot', $this->validation_snapshot);
        echo '</div>';
        echo '</div>';
    }

    public function handle_post(): void
    {
        if (!is_admin() || !current_user_can('manage_options')) {
            return;
        }

        $action = isset($_POST['hso_admin_action']) ? sanitize_key(wp_unslash((string) $_POST['hso_admin_action'])) : '';
        if ($action === '') {
            return;
        }

        $bridge_config = new HSO_Bridge_Config();
        if ($action === 'save_operator_inputs') {
            check_admin_referer(self::OPERATOR_INPUTS_NONCE);
            $bridge_config->persist_operator_inputs($this->collect_operator_inputs_from_post());
            $this->redirect_after_save('operator_inputs');
        }

        if ($action === 'save_source_mapping') {
            check_admin_referer(self::SOURCE_MAPPING_NONCE);
            $bridge_config->persist_source_mapping($this->collect_source_mapping_from_post());
            $this->redirect_after_save('source_mapping');
        }

        if ($action === 'apply_resolution_candidate') {
            check_admin_referer(self::APPLY_RESOLUTION_NONCE);
            $candidate_id = sanitize_text_field((string) ($_POST['candidate_id'] ?? ''));
            $result = $this->recommendation_action_center->apply_candidate($candidate_id);
            $this->redirect_after_resolution($result, 'resolution_applied');
        }

        if ($action === 'rollback_resolution_candidate') {
            check_admin_referer(self::ROLLBACK_RESOLUTION_NONCE);
            $candidate_id = sanitize_text_field((string) ($_POST['candidate_id'] ?? ''));
            $result = $this->recommendation_action_center->rollback_candidate($candidate_id);
            $this->redirect_after_resolution($result, 'resolution_rolled_back');
        }
    }

    private function render_card(string $title, array $payload): void
    {
        echo '<section style="background:#fff;border:1px solid #dcdcde;border-radius:8px;padding:16px;">';
        echo '<h2 style="margin-top:0;">' . esc_html($title) . '</h2>';
        echo '<pre style="white-space:pre-wrap;word-break:break-word;margin:0;">' . esc_html(wp_json_encode($payload, JSON_PRETTY_PRINT)) . '</pre>';
        echo '</section>';
    }

    private function render_notice(): void
    {
        if (!isset($_GET['hso_saved'])) {
            if (isset($_GET['hso_error'])) {
                echo '<div class="notice notice-error is-dismissible"><p>' . esc_html(wp_unslash((string) $_GET['hso_error'])) . '</p></div>';
            }
            return;
        }

        $saved = sanitize_key(wp_unslash((string) $_GET['hso_saved']));
        if ($saved === 'source_mapping') {
            $message = 'Source mapping confirmation was saved for this staging-only bridge.';
        } elseif ($saved === 'resolution_applied') {
            $message = 'The assisted-resolution change was applied with a rollback-ready before-state.';
        } elseif ($saved === 'resolution_rolled_back') {
            $message = 'The assisted-resolution change was rolled back to the captured before-state.';
        } else {
            $message = 'Operator inputs were saved for this staging-only bridge.';
        }

        echo '<div class="notice notice-success is-dismissible"><p>' . esc_html($message) . '</p></div>';
    }

    private function render_installed_suite_insights(): void
    {
        $insights = (array) ($this->runtime_context['installed_suite_insights'] ?? array());
        if (empty($insights)) {
            return;
        }

        $status = (array) ($insights['status_overview'] ?? array());
        echo '<section style="background:#fff;border:1px solid #dcdcde;border-radius:8px;padding:20px;margin:16px 0;">';
        echo '<h2 style="margin-top:0;">Installed Suite Insights</h2>';
        echo '<p>This installed bridge shows the current protected Suite state for this WordPress site. It explains what is already green, what is still blocked, what the installed plugin is allowed to prepare next, and why the product stays buyer-readable instead of behaving like a black box.</p>';
        echo '<div style="display:flex;flex-wrap:wrap;gap:10px;margin:16px 0;">';
        $this->render_status_pill('Mode', (string) ($status['mode'] ?? 'unknown'));
        $this->render_status_pill('Gate', (string) ($status['optimization_eligibility'] ?? 'unknown'));
        $this->render_status_pill('Domain Binding', (string) ($status['domain_binding'] ?? 'unknown'));
        $this->render_status_pill('URL Normalization', (string) ($status['url_normalization'] ?? 'unknown'));
        $this->render_status_pill('Baseline', (string) ($status['baseline_capture'] ?? 'unknown'));
        $this->render_status_pill('Source Mapping', (string) ($status['source_mapping'] ?? 'unknown'));
        $this->render_status_pill('Operator Inputs', (string) ($status['operator_inputs'] ?? 'unknown'));
        echo '</div>';
        echo '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px;">';
        $this->render_list_card('Subscription And Scope', (array) ($insights['subscription_and_scope'] ?? array()));
        $this->render_list_card('What The Installed Plugin Sees', (array) ($insights['environment'] ?? array()));
        $this->render_list_card('Baseline Evidence', (array) ($insights['baseline'] ?? array()));
        $this->render_string_list_card('Safe Now', (array) ($insights['safe_now'] ?? array()));
        $this->render_string_list_card('What Stays Protected', (array) ($insights['stays_protected'] ?? array()));
        $this->render_string_list_card('Next Steps Before Production', (array) ($insights['next_steps'] ?? array()));
        echo '</div>';
        echo '</section>';
    }

    private function render_recommendation_action_center(): void
    {
        $center = (array) ($this->runtime_context['recommendation_action_center'] ?? array());
        if (empty($center)) {
            return;
        }

        $summary = array(
            'execution_lane' => (string) ($center['execution_lane'] ?? ''),
            'candidate_count' => (int) ($center['candidate_count'] ?? 0),
            'applied_count' => (int) ($center['applied_count'] ?? 0),
            'rollback_ready_count' => (int) ($center['rollback_ready_count'] ?? 0),
            'status_note' => (string) ($center['status_note'] ?? ''),
        );
        $report_source = (array) ($center['report_source'] ?? array());
        $candidates = isset($center['candidates']) && is_array($center['candidates']) ? $center['candidates'] : array();

        echo '<section style="background:#fff;border:1px solid #dcdcde;border-radius:8px;padding:20px;margin:16px 0;">';
        echo '<h2 style="margin-top:0;">Recommendation Action Center</h2>';
        echo '<p>This protected lane allows a very small class of admin-confirmed assisted resolutions. It does not give the bridge live output ownership; it only writes into the active SEO owner after explicit confirmation, validation and rollback capture.</p>';
        echo '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px;margin-bottom:16px;">';
        $this->render_list_card('Assisted Resolution Summary', $summary);
        $this->render_list_card('Local Report Source', $report_source);
        echo '</div>';
        if (empty($candidates)) {
            echo '<p style="margin:0;">No assisted-resolution candidates are currently available.</p>';
        } else {
            echo '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:16px;">';
            foreach ($candidates as $candidate) {
                $this->render_resolution_candidate_card((array) $candidate);
            }
            echo '</div>';
        }
        echo '</section>';
    }

    private function render_innovation_control_deck(): void
    {
        $deck = (array) ($this->runtime_context['innovation_control_deck'] ?? array());
        if (empty($deck)) {
            return;
        }

        $summary = array(
            'execution_mode' => (string) ($deck['execution_mode'] ?? ''),
            'priority_focus' => (string) ($deck['priority_focus'] ?? ''),
            'operator_brief' => (string) ($deck['operator_brief'] ?? ''),
            'buyer_visibility_promise' => (string) ($deck['buyer_visibility_promise'] ?? ''),
        );

        echo '<section style="background:#fff;border:1px solid #dcdcde;border-radius:8px;padding:20px;margin:16px 0;">';
        echo '<h2 style="margin-top:0;">Innovation Control Deck</h2>';
        echo '<p>This operator-facing deck translates the current doctrine-safe runtime into a practical growth lane. It keeps the plugin bounded, surfaces the next safe actions, and preserves protected holds while the installation stays explainable.</p>';
        echo '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px;">';
        $this->render_list_card('Innovation Posture', $summary);
        $this->render_string_list_card('Immediate Safe Actions', (array) ($deck['immediate_actions'] ?? array()));
        $this->render_string_list_card('Next Innovation Actions', (array) ($deck['next_actions'] ?? array()));
        $this->render_string_list_card('Success Signals', (array) ($deck['success_signals'] ?? array()));
        $this->render_string_list_card('Protected Holds', (array) ($deck['protected_holds'] ?? array()));
        echo '</div>';
        echo '</section>';
    }

    private function render_post_purchase_visibility_layer(): void
    {
        $license_panel = (array) ($this->runtime_context['license_domain_scope_panel'] ?? array());
        $health_signals = (array) ($this->runtime_context['installation_health_signals'] ?? array());
        $doctrine_state = (array) ($this->runtime_context['doctrine_runtime_state'] ?? array());
        $cutover = (array) ($this->runtime_context['production_cutover_checklist'] ?? array());
        $customer_visibility = (array) ($this->runtime_context['customer_subscription_visibility'] ?? array());
        $protected_delivery = (array) ($this->runtime_context['protected_delivery_status'] ?? array());
        if (empty($license_panel) && empty($health_signals) && empty($doctrine_state) && empty($cutover) && empty($customer_visibility) && empty($protected_delivery)) {
            return;
        }

        echo '<section style="background:#fff;border:1px solid #dcdcde;border-radius:8px;padding:20px;margin:16px 0;">';
        echo '<h2 style="margin-top:0;">Post-Purchase Visibility Layer</h2>';
        echo '<p>This protected admin surface is the local post-purchase view for this installation. It shows the subscription binding, installation health, protected delivery state, rollback and validation ownership, and the concrete cutover path without opening any public customer route.</p>';
        echo '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px;">';
        $this->render_list_card('License / Domain / Scope Panel', $license_panel);
        $this->render_list_card('Customer Subscription Visibility', $customer_visibility);
        $this->render_list_card('Installation Health Signals', $health_signals);
        $this->render_list_card('Doctrine 8.0 Governance', $doctrine_state);
        $this->render_list_card('Protected Delivery Status', $protected_delivery);
        $this->render_checklist_card('Production Cutover Checklist', $cutover);
        echo '</div>';
        echo '</section>';
    }

    private function render_operator_inputs_form(): void
    {
        $operator_input_state = (array) ($this->runtime_context['operator_input_state'] ?? array());
        $fields = (array) ($operator_input_state['fields'] ?? array());
        $missing = array_flip((array) ($operator_input_state['missing_fields'] ?? array()));
        $server_managed = array_flip((array) ($operator_input_state['server_managed_fields'] ?? array()));

        echo '<section style="background:#fff;border:1px solid #dcdcde;border-radius:8px;padding:16px;">';
        echo '<h2 style="margin-top:0;">Operator Input Completion</h2>';
        echo '<p>Staging-only confirmations for backup, restore, rollback ownership, and validation ownership. Auto-detected runtime fields stay visible here for review so the bridge can keep recovery and validation explainable before any broader optimization gate is considered.</p>';
        echo '<form method="post">';
        wp_nonce_field(self::OPERATOR_INPUTS_NONCE);
        echo '<input type="hidden" name="hso_admin_action" value="save_operator_inputs" />';
        $this->render_input_row('WordPress Version', 'operator_inputs[wordpress_version]', (string) ($fields['wordpress_version'] ?? ''), true, isset($missing['wordpress_version']));
        $this->render_input_row('Active Theme', 'operator_inputs[active_theme]', (string) ($fields['active_theme'] ?? ''), true, isset($missing['active_theme']));
        $this->render_input_row('Active Builder', 'operator_inputs[active_builder]', (string) ($fields['active_builder'] ?? ''), true, isset($missing['active_builder']));
        $this->render_input_row('Active SEO Plugin', 'operator_inputs[active_seo_plugin]', (string) ($fields['active_seo_plugin'] ?? ''), true, isset($missing['active_seo_plugin']));
        $this->render_inventory_row('Plugin Inventory', (array) ($fields['plugin_inventory'] ?? array()), isset($missing['plugin_inventory']));
        $this->render_input_row('Backup Confirmation', 'operator_inputs[backup_confirmation]', (string) ($fields['backup_confirmation'] ?? ''), false, isset($missing['backup_confirmation']));
        $this->render_input_row('Restore Confirmation', 'operator_inputs[restore_confirmation]', (string) ($fields['restore_confirmation'] ?? ''), false, isset($missing['restore_confirmation']));
        $this->render_input_row('Rollback Owner', 'operator_inputs[rollback_owner]', (string) ($fields['rollback_owner'] ?? ''), isset($server_managed['rollback_owner']), isset($missing['rollback_owner']));
        $this->render_input_row('Validation Owner', 'operator_inputs[validation_owner]', (string) ($fields['validation_owner'] ?? ''), isset($server_managed['validation_owner']), isset($missing['validation_owner']));
        submit_button('Save Operator Inputs', 'primary', 'submit', false);
        echo '</form>';
        echo '</section>';
    }

    private function render_source_mapping_form(): void
    {
        $source_mapping_state = (array) ($this->runtime_context['source_mapping_state'] ?? array());
        $notes = implode("\n", array_map('strval', (array) ($source_mapping_state['notes'] ?? array())));
        $missing = (array) ($source_mapping_state['missing_requirements'] ?? array());
        $duplicate_output_status = (string) ($source_mapping_state['duplicate_output_status'] ?? 'not_detected');
        $duplicate_output_basis = (string) ($source_mapping_state['duplicate_output_basis'] ?? '');
        $double_output_verification = (string) ($source_mapping_state['double_output_verification'] ?? 'not_detected');

        echo '<section style="background:#fff;border:1px solid #dcdcde;border-radius:8px;padding:16px;">';
        echo '<h2 style="margin-top:0;">Source Mapping Confirmation</h2>';
        echo '<p>Staging-only confirmation for homepage meta ownership and single-source head/meta readiness. This does not open any live optimization by itself; it exists so reversible changes only become eligible when ownership is explicit and duplicate output risk is understood.</p>';
        echo '<p><strong>Duplicate output status:</strong> ' . esc_html($duplicate_output_status) . '</p>';
        if ($duplicate_output_basis !== '') {
            echo '<p style="color:#50575e;">' . esc_html($duplicate_output_basis) . '</p>';
        }
        $coexistence_mode = (string) ($source_mapping_state['coexistence_mode'] ?? 'no_external_seo_owner');
        $coexistence_advisories = isset($source_mapping_state['coexistence_advisories']) && is_array($source_mapping_state['coexistence_advisories'])
            ? $source_mapping_state['coexistence_advisories']
            : array();
        echo '<p><strong>Coexistence mode:</strong> ' . esc_html($coexistence_mode) . '</p>';
        if (!empty($coexistence_advisories)) {
            echo '<p><strong>Controlled coexistence notes:</strong></p><ul style="margin-top:0;">';
            foreach ($coexistence_advisories as $item) {
                echo '<li>' . esc_html((string) $item) . '</li>';
            }
            echo '</ul>';
        }
        echo '<form method="post">';
        wp_nonce_field(self::SOURCE_MAPPING_NONCE);
        echo '<input type="hidden" name="hso_admin_action" value="save_source_mapping" />';
        $this->render_checkbox_row(
            'Homepage meta description single source confirmed',
            'source_mapping[homepage_meta_description_single]',
            !empty($source_mapping_state['homepage_meta_description_single'])
        );
        $this->render_checkbox_row(
            'Head/meta output single source confirmed',
            'source_mapping[head_meta_output_single]',
            !empty($source_mapping_state['head_meta_output_single'])
        );
        $this->render_checkbox_row(
            'Duplicate output detected',
            'source_mapping[double_output_detected]',
            !empty($source_mapping_state['double_output_signal_present'])
        );
        $this->render_select_row(
            'Duplicate output verification',
            'source_mapping[double_output_verification]',
            $double_output_verification,
            array(
                'not_detected' => 'No duplicate output recorded',
                'heuristic_suspected' => 'Heuristic suspicion only',
                'confirmed_runtime_output' => 'Confirmed in rendered output',
            )
        );
        $this->render_checkbox_row(
            'Operator confirms the source mapping',
            'source_mapping[operator_confirmation]',
            !empty($source_mapping_state['operator_confirmation'])
        );
        echo '<p><label for="hso-source-mapping-notes" style="font-weight:600;display:block;margin-bottom:6px;">Notes</label>';
        echo '<textarea id="hso-source-mapping-notes" name="source_mapping[notes]" rows="5" style="width:100%;">' . esc_textarea($notes) . '</textarea></p>';
        if (!empty($missing)) {
            echo '<p><strong>Still missing:</strong></p><ul style="margin-top:0;">';
            foreach ($missing as $item) {
                echo '<li>' . esc_html((string) $item) . '</li>';
            }
            echo '</ul>';
        }
        submit_button('Save Source Mapping Confirmation', 'secondary', 'submit', false);
        echo '</form>';
        echo '</section>';
    }

    private function render_input_row(string $label, string $name, string $value, bool $readonly, bool $missing): void
    {
        echo '<p><label style="font-weight:600;display:block;margin-bottom:6px;">' . esc_html($label) . '</label>';
        echo '<input type="text" name="' . esc_attr($name) . '" value="' . esc_attr($value) . '" ' . ($readonly ? 'readonly' : '') . ' style="width:100%;" />';
        if ($readonly) {
            echo '<br /><span style="color:#50575e;">Runtime-detected or server-managed field</span>';
        }
        if ($missing) {
            echo '<br /><span style="color:#b32d2e;">Still required</span>';
        }
        echo '</p>';
    }

    private function render_inventory_row(string $label, array $inventory, bool $missing): void
    {
        echo '<p><label style="font-weight:600;display:block;margin-bottom:6px;">' . esc_html($label) . '</label>';
        echo '<textarea rows="4" readonly style="width:100%;">' . esc_textarea(implode("\n", array_map('strval', $inventory))) . '</textarea>';
        echo '<br /><span style="color:#50575e;">Runtime-detected field</span>';
        if ($missing) {
            echo '<br /><span style="color:#b32d2e;">Still required</span>';
        }
        echo '</p>';
    }

    private function render_checkbox_row(string $label, string $name, bool $checked): void
    {
        echo '<p><label>';
        echo '<input type="checkbox" name="' . esc_attr($name) . '" value="1" ' . checked($checked, true, false) . ' />';
        echo ' ' . esc_html($label);
        echo '</label></p>';
    }

    private function render_select_row(string $label, string $name, string $selected, array $options): void
    {
        echo '<p><label style="font-weight:600;display:block;margin-bottom:6px;">' . esc_html($label) . '</label>';
        echo '<select name="' . esc_attr($name) . '" style="width:100%;">';
        foreach ($options as $value => $option_label) {
            echo '<option value="' . esc_attr((string) $value) . '" ' . selected($selected, (string) $value, false) . '>';
            echo esc_html((string) $option_label);
            echo '</option>';
        }
        echo '</select></p>';
    }

    private function render_status_pill(string $label, string $value): void
    {
        echo '<span style="display:inline-flex;flex-direction:column;gap:2px;border:1px solid #dcdcde;border-radius:999px;padding:8px 14px;background:#f6f7f7;">';
        echo '<strong style="font-size:11px;text-transform:uppercase;letter-spacing:0.04em;">' . esc_html($label) . '</strong>';
        echo '<span>' . esc_html($value) . '</span>';
        echo '</span>';
    }

    private function render_list_card(string $title, array $payload): void
    {
        echo '<section style="background:#f6f7f7;border:1px solid #dcdcde;border-radius:8px;padding:16px;">';
        echo '<h3 style="margin-top:0;">' . esc_html($title) . '</h3>';
        echo '<dl style="margin:0;">';
        foreach ($payload as $key => $value) {
            echo '<dt style="font-weight:600;margin-top:10px;">' . esc_html($this->pretty_label((string) $key)) . '</dt>';
            if (is_array($value)) {
                echo '<dd style="margin:4px 0 0 0;">' . esc_html(implode(', ', array_map('strval', $value))) . '</dd>';
            } else {
                echo '<dd style="margin:4px 0 0 0;">' . esc_html((string) $value) . '</dd>';
            }
        }
        echo '</dl>';
        echo '</section>';
    }

    private function render_string_list_card(string $title, array $items): void
    {
        echo '<section style="background:#f6f7f7;border:1px solid #dcdcde;border-radius:8px;padding:16px;">';
        echo '<h3 style="margin-top:0;">' . esc_html($title) . '</h3>';
        if (empty($items)) {
            echo '<p style="margin:0;">None.</p>';
        } else {
            echo '<ul style="margin:0;padding-left:20px;">';
            foreach ($items as $item) {
                echo '<li>' . esc_html((string) $item) . '</li>';
            }
            echo '</ul>';
        }
        echo '</section>';
    }

    private function render_checklist_card(string $title, array $payload): void
    {
        $checks = isset($payload['checks']) && is_array($payload['checks']) ? $payload['checks'] : array();
        echo '<section style="background:#f6f7f7;border:1px solid #dcdcde;border-radius:8px;padding:16px;">';
        echo '<h3 style="margin-top:0;">' . esc_html($title) . '</h3>';
        if (isset($payload['cutover_ready'])) {
            echo '<p><strong>Cutover Ready:</strong> ' . esc_html(!empty($payload['cutover_ready']) ? 'yes' : 'no') . '</p>';
        }
        if (isset($payload['next_gate'])) {
            echo '<p><strong>Next Gate:</strong> ' . esc_html((string) $payload['next_gate']) . '</p>';
        }
        if (empty($checks)) {
            echo '<p style="margin:0;">No checklist items available.</p>';
        } else {
            echo '<ul style="margin:0;padding-left:20px;">';
            foreach ($checks as $check) {
                $label = isset($check['label']) ? (string) $check['label'] : 'Unnamed check';
                $status = isset($check['status']) ? (string) $check['status'] : 'unknown';
                $detail = isset($check['detail']) ? (string) $check['detail'] : '';
                echo '<li><strong>' . esc_html($label) . ':</strong> ' . esc_html($status);
                if ($detail !== '') {
                    echo '<br /><span style="color:#50575e;">' . esc_html($detail) . '</span>';
                }
                echo '</li>';
            }
            echo '</ul>';
        }
        echo '</section>';
    }

    private function render_resolution_candidate_card(array $candidate): void
    {
        $status = (string) ($candidate['status'] ?? 'admin_confirmation_required');
        $rollback_ready = !empty($candidate['rollback_ready']);

        echo '<section style="background:#f6f7f7;border:1px solid #dcdcde;border-radius:8px;padding:16px;">';
        echo '<h3 style="margin-top:0;">' . esc_html((string) ($candidate['label'] ?? 'Assisted Resolution')) . '</h3>';
        echo '<p><strong>Status:</strong> ' . esc_html($status) . '</p>';
        echo '<p><strong>Automation contract:</strong> ' . esc_html((string) ($candidate['automation_contract_id'] ?? '')) . ' / ' . esc_html((string) ($candidate['automation_contract_version'] ?? '')) . '</p>';
        echo '<p><strong>Contract state:</strong> ' . esc_html((string) ($candidate['automation_contract_state'] ?? '')) . '</p>';
        echo '<p><strong>Execution lane:</strong> ' . esc_html((string) ($candidate['execution_lane'] ?? '')) . '</p>';
        echo '<p><strong>Target URL:</strong> ' . esc_html((string) ($candidate['target_url'] ?? '')) . '</p>';
        echo '<p><strong>Target resolution:</strong> ' . esc_html((string) ($candidate['target_resolution_state'] ?? 'unknown')) . '</p>';
        if (!empty($candidate['target_resolution_note'])) {
            echo '<p><strong>Resolution note:</strong><br />' . esc_html((string) $candidate['target_resolution_note']) . '</p>';
        }
        echo '<p><strong>Proposed value:</strong><br />' . esc_html((string) ($candidate['proposed_value'] ?? '')) . '</p>';
        echo '<p><strong>Why this is safe now:</strong><br />' . esc_html((string) ($candidate['proposal_reason'] ?? '')) . '</p>';
        echo '<p><strong>Validation checks:</strong></p><ul style="margin-top:0;">';
        foreach ((array) ($candidate['validation_checks'] ?? array()) as $check) {
            echo '<li>' . esc_html((string) $check) . '</li>';
        }
        echo '</ul>';
        if (!empty($candidate['applied_at'])) {
            echo '<p><strong>Applied at:</strong> ' . esc_html((string) $candidate['applied_at']) . '</p>';
        }
        if (!empty($candidate['rolled_back_at'])) {
            echo '<p><strong>Rolled back at:</strong> ' . esc_html((string) $candidate['rolled_back_at']) . '</p>';
        }
        if (!empty($candidate['current_runtime_allowed'])) {
            if ($status !== 'applied') {
                echo '<form method="post" style="display:inline-block;margin-right:8px;">';
                wp_nonce_field(self::APPLY_RESOLUTION_NONCE);
                echo '<input type="hidden" name="hso_admin_action" value="apply_resolution_candidate" />';
                echo '<input type="hidden" name="candidate_id" value="' . esc_attr((string) ($candidate['candidate_id'] ?? '')) . '" />';
                submit_button('Apply With Admin Confirmation', 'primary', 'submit', false);
                echo '</form>';
            }
            if ($rollback_ready) {
                echo '<form method="post" style="display:inline-block;">';
                wp_nonce_field(self::ROLLBACK_RESOLUTION_NONCE);
                echo '<input type="hidden" name="hso_admin_action" value="rollback_resolution_candidate" />';
                echo '<input type="hidden" name="candidate_id" value="' . esc_attr((string) ($candidate['candidate_id'] ?? '')) . '" />';
                submit_button('Rollback To Before-State', 'secondary', 'submit', false);
                echo '</form>';
            }
        } else {
            echo '<p style="color:#b32d2e;margin-bottom:0;">Current runtime guardrails do not allow this assisted-resolution candidate.</p>';
        }
        echo '</section>';
    }

    private function pretty_label(string $value): string
    {
        $value = str_replace('_', ' ', $value);
        return ucwords($value);
    }

    private function collect_operator_inputs_from_post(): array
    {
        $posted = isset($_POST['operator_inputs']) && is_array($_POST['operator_inputs'])
            ? wp_unslash($_POST['operator_inputs'])
            : array();

        return array(
            'backup_confirmation' => sanitize_text_field((string) ($posted['backup_confirmation'] ?? '')),
            'restore_confirmation' => sanitize_text_field((string) ($posted['restore_confirmation'] ?? '')),
            'rollback_owner' => 'server_managed_bridge',
            'validation_owner' => 'server_managed_bridge',
        );
    }

    private function collect_source_mapping_from_post(): array
    {
        $posted = isset($_POST['source_mapping']) && is_array($_POST['source_mapping'])
            ? wp_unslash($_POST['source_mapping'])
            : array();
        $notes_raw = isset($posted['notes']) ? (string) $posted['notes'] : '';
        $notes = preg_split('/\r\n|\r|\n/', $notes_raw) ?: array();
        $notes = array_values(array_filter(array_map('sanitize_text_field', $notes)));

        return array(
            'homepage_meta_description_single' => !empty($posted['homepage_meta_description_single']),
            'head_meta_output_single' => !empty($posted['head_meta_output_single']),
            'double_output_detected' => !empty($posted['double_output_detected']),
            'double_output_verification' => sanitize_key((string) ($posted['double_output_verification'] ?? '')),
            'operator_confirmation' => !empty($posted['operator_confirmation']),
            'notes' => $notes,
        );
    }

    private function redirect_after_save(string $saved): void
    {
        $target = add_query_arg(
            array(
                'page' => 'hetzner-seo-ops',
                'hso_saved' => $saved,
            ),
            admin_url('admin.php')
        );
        wp_safe_redirect($target);
        exit;
    }

    private function redirect_after_resolution(array $result, string $saved): void
    {
        $args = array(
            'page' => 'hetzner-seo-ops',
        );
        if (!empty($result['ok'])) {
            $args['hso_saved'] = $saved;
        } else {
            $args['hso_error'] = (string) ($result['message'] ?? 'The assisted-resolution action failed.');
        }

        wp_safe_redirect(add_query_arg($args, admin_url('admin.php')));
        exit;
    }
}
