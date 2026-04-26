<?php

if (!defined('ABSPATH')) {
    exit;
}

class HSO_Recommendation_Action_Center
{
    private const ACTION_JOURNAL_OPTION = 'hso_recommendation_action_journal';
    private const RANK_MATH_DESCRIPTION_META_KEY = 'rank_math_description';
    private const RANK_MATH_META_DESCRIPTION_CONTRACT_ID = 'ac-rank-math-meta-description-update-v1';
    private const RANK_MATH_META_DESCRIPTION_CONTRACT_VERSION = '1.0';

    private array $runtime_context;
    private array $bridge_profile;
    private array $conflict_state;
    private array $resolved_report_source = array();
    private HSO_Validation_Status $validation_status;
    private HSO_Rollback_Registry $rollback_registry;

    public function __construct(
        array $runtime_context,
        array $bridge_profile,
        array $conflict_state,
        HSO_Validation_Status $validation_status,
        HSO_Rollback_Registry $rollback_registry
    ) {
        $this->runtime_context = $runtime_context;
        $this->bridge_profile = $bridge_profile;
        $this->conflict_state = $conflict_state;
        $this->validation_status = $validation_status;
        $this->rollback_registry = $rollback_registry;
    }

    public function register_entries(): void
    {
        $this->rollback_registry->register_entry(
            'rank_math_meta_description_assisted_resolution',
            array(
                'before_state_key' => 'rank_math_description',
                'rollback_notes' => 'Restore the previous Rank Math meta description value or remove the temporary value if it did not exist before.',
                'validation_window' => 'immediate/1d',
            )
        );
    }

    public function build_snapshot(): array
    {
        $report = $this->load_report_payload();
        $journal = $this->load_action_journal();
        $candidates = $this->normalize_candidates($report, $journal);
        $report_source = !empty($this->resolved_report_source)
            ? $this->resolved_report_source
            : array(
                'path' => $this->report_path(),
                'report_id' => '',
                'built_at' => '',
                'bound_domain' => '',
            );

        return array(
            'available' => !empty($report),
            'report_source' => array(
                'path' => isset($report_source['path']) ? (string) $report_source['path'] : '',
                'report_id' => isset($report_source['report_id']) ? (string) $report_source['report_id'] : '',
                'built_at' => isset($report_source['built_at']) ? (string) $report_source['built_at'] : '',
                'bound_domain' => isset($report_source['bound_domain']) ? (string) $report_source['bound_domain'] : '',
            ),
            'execution_lane' => 'admin_confirmed_assisted_resolution_only',
            'candidate_count' => count($candidates),
            'applied_count' => count(array_filter($candidates, static function (array $item): bool {
                return ($item['status'] ?? '') === 'applied';
            })),
            'rollback_ready_count' => count(array_filter($candidates, static function (array $item): bool {
                return !empty($item['rollback_ready']);
            })),
            'status_note' => $this->build_status_note($report, $candidates),
            'candidates' => $candidates,
        );
    }

    public function apply_candidate(string $candidate_id): array
    {
        $candidate = $this->find_candidate($candidate_id);
        if ($candidate === null) {
            return array('ok' => false, 'message' => 'The requested assisted-resolution candidate was not found.');
        }
        if (!$this->candidate_is_allowed($candidate)) {
            return array('ok' => false, 'message' => 'The current runtime does not allow this assisted-resolution candidate.');
        }
        if (($candidate['action_type'] ?? '') !== 'rank_math_meta_description_update') {
            return array('ok' => false, 'message' => 'Only Rank Math meta-description updates are allowed in this action lane.');
        }

        $target_post_id = $this->resolve_target_post_id((string) ($candidate['target_url'] ?? ''));
        if ($target_post_id <= 0) {
            return array('ok' => false, 'message' => 'The target page could not be resolved to a WordPress page for assisted resolution.');
        }

        $proposed_value = trim((string) ($candidate['proposed_value'] ?? ''));
        if ($proposed_value === '') {
            return array('ok' => false, 'message' => 'The proposed value is empty, so nothing safe can be applied.');
        }

        $previous_value = (string) get_post_meta($target_post_id, self::RANK_MATH_DESCRIPTION_META_KEY, true);
        update_post_meta($target_post_id, self::RANK_MATH_DESCRIPTION_META_KEY, $proposed_value);
        $stored_value = (string) get_post_meta($target_post_id, self::RANK_MATH_DESCRIPTION_META_KEY, true);
        if ($stored_value !== $proposed_value) {
            $this->restore_meta_description($target_post_id, $previous_value);
            return array('ok' => false, 'message' => 'The proposed Rank Math meta description could not be validated after apply, so it was rolled back immediately.');
        }

        $journal = $this->load_action_journal();
        $journal[$candidate_id] = array(
            'candidate_id' => $candidate_id,
            'action_type' => 'rank_math_meta_description_update',
            'status' => 'applied',
            'applied_at' => gmdate('c'),
            'target_post_id' => $target_post_id,
            'target_url' => (string) ($candidate['target_url'] ?? ''),
            'previous_value' => $previous_value,
            'proposed_value' => $proposed_value,
            'validation_state' => 'stored_value_matches_proposal',
            'rollback_ready' => true,
        );
        update_option(self::ACTION_JOURNAL_OPTION, $journal, false);

        return array('ok' => true, 'message' => 'The assisted Rank Math meta-description update was applied and a rollback snapshot was captured.');
    }

    public function rollback_candidate(string $candidate_id): array
    {
        $journal = $this->load_action_journal();
        $entry = isset($journal[$candidate_id]) && is_array($journal[$candidate_id]) ? $journal[$candidate_id] : null;
        if ($entry === null || ($entry['status'] ?? '') !== 'applied') {
            return array('ok' => false, 'message' => 'No applied assisted-resolution entry is available to roll back.');
        }

        $target_post_id = isset($entry['target_post_id']) ? (int) $entry['target_post_id'] : 0;
        if ($target_post_id <= 0) {
            return array('ok' => false, 'message' => 'The rollback target is missing or invalid.');
        }

        $previous_value = (string) ($entry['previous_value'] ?? '');
        $this->restore_meta_description($target_post_id, $previous_value);
        $stored_value = (string) get_post_meta($target_post_id, self::RANK_MATH_DESCRIPTION_META_KEY, true);
        if ($previous_value !== '' && $stored_value !== $previous_value) {
            return array('ok' => false, 'message' => 'Rollback validation failed because the previous Rank Math value was not restored.');
        }
        if ($previous_value === '' && $stored_value !== '') {
            return array('ok' => false, 'message' => 'Rollback validation failed because the temporary Rank Math value still exists.');
        }

        $journal[$candidate_id]['status'] = 'rolled_back';
        $journal[$candidate_id]['rolled_back_at'] = gmdate('c');
        $journal[$candidate_id]['rollback_ready'] = false;
        $journal[$candidate_id]['validation_state'] = 'rolled_back_to_before_state';
        update_option(self::ACTION_JOURNAL_OPTION, $journal, false);

        return array('ok' => true, 'message' => 'The assisted Rank Math meta-description update was rolled back to the captured before-state.');
    }

    private function build_status_note(array $report, array $candidates): string
    {
        if (empty($report)) {
            return 'No readable local suite report is currently available for assisted-resolution ingest.';
        }
        if (empty($candidates)) {
            return 'The current report exposes no automation candidates that are safe in the current recommend_only lane.';
        }
        return 'Admin confirmation is required before any assisted change is written into Rank Math, and every supported change captures a rollback-ready before-state.';
    }

    private function find_candidate(string $candidate_id): ?array
    {
        foreach ($this->normalize_candidates($this->load_report_payload(), $this->load_action_journal()) as $candidate) {
            if (($candidate['candidate_id'] ?? '') === $candidate_id) {
                return $candidate;
            }
        }
        return null;
    }

    private function normalize_candidates(array $report, array $journal): array
    {
        $raw_candidates = isset($report['automation_candidates']) && is_array($report['automation_candidates'])
            ? $report['automation_candidates']
            : array();
        $normalized = array();
        foreach ($raw_candidates as $candidate) {
            if (!is_array($candidate)) {
                continue;
            }
            $candidate_id = isset($candidate['candidate_id']) ? (string) $candidate['candidate_id'] : '';
            if ($candidate_id === '') {
                continue;
            }
            $entry = isset($journal[$candidate_id]) && is_array($journal[$candidate_id]) ? $journal[$candidate_id] : array();
            $status = isset($entry['status']) ? (string) $entry['status'] : 'admin_confirmation_required';
            $candidate['status'] = $status;
            $candidate['applied_at'] = isset($entry['applied_at']) ? (string) $entry['applied_at'] : '';
            $candidate['rolled_back_at'] = isset($entry['rolled_back_at']) ? (string) $entry['rolled_back_at'] : '';
            $candidate['rollback_ready'] = !empty($entry['rollback_ready']) && $status === 'applied';
            $target_post_id = $this->resolve_target_post_id((string) ($candidate['target_url'] ?? ''));
            $candidate['target_post_id'] = $target_post_id;
            $candidate['target_resolution_state'] = $target_post_id > 0 ? 'wordpress_page_resolved' : 'not_resolved';
            $candidate['target_resolution_note'] = $target_post_id > 0
                ? 'Target URL resolves to a concrete WordPress page/post for Rank Math post-meta update.'
                : 'Target URL does not currently resolve to a concrete WordPress page/post. If this is the homepage, configure a static front page or apply the snippet manually in Rank Math homepage settings.';
            $candidate['current_runtime_allowed'] = $this->candidate_is_allowed($candidate);
            $normalized[] = $candidate;
        }
        return $normalized;
    }

    private function candidate_is_allowed(array $candidate): bool
    {
        if (($candidate['automation_contract_id'] ?? '') !== self::RANK_MATH_META_DESCRIPTION_CONTRACT_ID) {
            return false;
        }
        if (($candidate['automation_contract_version'] ?? '') !== self::RANK_MATH_META_DESCRIPTION_CONTRACT_VERSION) {
            return false;
        }
        if (($candidate['automation_contract_state'] ?? '') !== 'contract_verified') {
            return false;
        }
        if (empty($candidate['requires_admin_confirmation']) || empty($candidate['requires_before_state_capture']) || empty($candidate['requires_rollback'])) {
            return false;
        }
        if (($candidate['approval_state'] ?? '') !== 'admin_confirmation_required') {
            return false;
        }
        if (($candidate['rollback_state'] ?? '') !== 'ready_if_before_state_captured') {
            return false;
        }
        if (($candidate['target_field'] ?? '') !== self::RANK_MATH_DESCRIPTION_META_KEY) {
            return false;
        }
        if (($candidate['action_type'] ?? '') !== 'rank_math_meta_description_update') {
            return false;
        }
        if (($candidate['execution_lane'] ?? '') !== 'admin_confirmed_assisted_resolution_only') {
            return false;
        }
        if (($candidate['target_resolution_state'] ?? '') !== 'wordpress_page_resolved' || (int) ($candidate['target_post_id'] ?? 0) <= 0) {
            return false;
        }
        if (($this->runtime_context['optimization_state']['eligibility'] ?? 'blocked') !== 'recommend_only') {
            return false;
        }
        if (empty($this->runtime_context['domain_match'])) {
            return false;
        }
        if (empty($this->runtime_context['operator_inputs_complete']) || empty($this->runtime_context['source_mapping_confirmed'])) {
            return false;
        }
        if (empty($this->conflict_state['external_seo_owner_active'])) {
            return false;
        }
        return strpos((string) ($this->conflict_state['single_seo_plugin_slug'] ?? ''), 'seo-by-rank-math/') !== false;
    }

    private function load_report_payload(): array
    {
        $this->resolved_report_source = array();
        foreach ($this->report_path_candidates() as $path) {
            if ($path === '' || !file_exists($path) || !is_readable($path)) {
                continue;
            }
            $raw = file_get_contents($path);
            if ($raw === false) {
                continue;
            }
            $decoded = json_decode($raw, true);
            if (!is_array($decoded)) {
                continue;
            }
            if (($decoded['bound_domain'] ?? '') !== ($this->runtime_context['bound_domain'] ?? '')) {
                continue;
            }
            $this->resolved_report_source = array(
                'path' => $path,
                'report_id' => isset($decoded['report_id']) ? (string) $decoded['report_id'] : '',
                'built_at' => isset($decoded['built_at']) ? (string) $decoded['built_at'] : '',
                'bound_domain' => isset($decoded['bound_domain']) ? (string) $decoded['bound_domain'] : '',
            );
            return $decoded;
        }
        return array();
    }

    private function report_path(): string
    {
        $ingest = isset($this->bridge_profile['local_report_ingest']) && is_array($this->bridge_profile['local_report_ingest'])
            ? $this->bridge_profile['local_report_ingest']
            : array();
        if (empty($ingest['enabled'])) {
            return '';
        }
        return trim((string) ($ingest['path'] ?? ''));
    }

    private function report_path_candidates(): array
    {
        $ingest = isset($this->bridge_profile['local_report_ingest']) && is_array($this->bridge_profile['local_report_ingest'])
            ? $this->bridge_profile['local_report_ingest']
            : array();
        if (empty($ingest['enabled'])) {
            return array();
        }

        $candidates = array();
        $primary_path = trim((string) ($ingest['path'] ?? ''));
        if ($primary_path !== '') {
            $candidates[] = $primary_path;
        }

        $bundled_path = trim((string) ($ingest['bundled_snapshot_path'] ?? ''));
        if ($bundled_path !== '') {
            if ($bundled_path[0] === '/') {
                $candidates[] = $bundled_path;
            } elseif (defined('HSO_PLUGIN_DIR')) {
                $candidates[] = HSO_PLUGIN_DIR . ltrim($bundled_path, '/');
            }
        }

        return array_values(array_unique($candidates));
    }

    private function load_action_journal(): array
    {
        if (!function_exists('get_option')) {
            return array();
        }
        $value = get_option(self::ACTION_JOURNAL_OPTION, array());
        return is_array($value) ? $value : array();
    }

    private function resolve_target_post_id(string $url): int
    {
        $normalized_url = $this->normalize_url_for_compare($url);
        if ($normalized_url === '') {
            return 0;
        }

        $home_url = function_exists('home_url') ? $this->normalize_url_for_compare((string) home_url('/')) : '';
        $front_page_id = function_exists('get_option') ? (int) get_option('page_on_front', 0) : 0;
        if ($front_page_id > 0 && $home_url !== '' && $normalized_url === $home_url) {
            return $front_page_id;
        }

        if (function_exists('get_privacy_policy_url') && function_exists('get_option')) {
            $privacy_url = $this->normalize_url_for_compare((string) get_privacy_policy_url());
            $privacy_page_id = (int) get_option('wp_page_for_privacy_policy', 0);
            if ($privacy_page_id > 0 && $privacy_url !== '' && $normalized_url === $privacy_url) {
                return $privacy_page_id;
            }
        }

        if (function_exists('url_to_postid')) {
            $post_id = (int) url_to_postid($url);
            if ($post_id > 0) {
                return $post_id;
            }
        }

        $path = wp_parse_url($url, PHP_URL_PATH);
        if (!is_string($path)) {
            return 0;
        }
        $path = trim($path, '/');
        if ($path === '') {
            return $front_page_id;
        }

        if (function_exists('get_page_by_path')) {
            $page = get_page_by_path($path, OBJECT, 'page');
            if ($page && isset($page->ID)) {
                return (int) $page->ID;
            }
            $post = get_page_by_path($path, OBJECT, 'post');
            if ($post && isset($post->ID)) {
                return (int) $post->ID;
            }
        }
        return 0;
    }

    private function normalize_url_for_compare(string $url): string
    {
        $url = trim($url);
        if ($url === '') {
            return '';
        }
        return rtrim($url, '/');
    }

    private function restore_meta_description(int $post_id, string $previous_value): void
    {
        if ($previous_value === '') {
            delete_post_meta($post_id, self::RANK_MATH_DESCRIPTION_META_KEY);
            return;
        }

        update_post_meta($post_id, self::RANK_MATH_DESCRIPTION_META_KEY, $previous_value);
    }
}
