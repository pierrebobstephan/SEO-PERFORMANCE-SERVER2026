<?php

if (!defined('ABSPATH')) {
    exit;
}

class HSO_Validation_Status
{
    private array $snapshot = array();

    public function set_snapshot(array $snapshot): void
    {
        $this->snapshot = $snapshot;
    }

    public function build_snapshot(
        string $mode,
        array $license_state,
        array $conflict_state,
        array $baseline_snapshot = array(),
        array $optimization_state = array(),
        array $connection_state = array(),
        array $operator_input_state = array(),
        array $source_mapping_state = array(),
        array $runtime_blockers = array()
    ): array
    {
        return array(
            'mode' => $mode,
            'license_status' => isset($license_state['status']) ? (string) $license_state['status'] : 'approval_required',
            'domain_match' => !empty($license_state['domain_match']),
            'primary_signals' => array(
                'homepage_meta_description_single' => !empty($source_mapping_state['homepage_meta_description_single']),
                'source_mapping_confirmed' => !empty($source_mapping_state['confirmed']),
                'url_normalization_clean' => !empty($baseline_snapshot['url_normalization_clean']),
            ),
            'neighbor_signals' => array(
                'title_stable' => true,
                'canonical_stable' => !empty($baseline_snapshot['url_normalization_clean']),
                'robots_stable' => true,
                'rank_math_active' => !empty($conflict_state['rank_math_active']),
                'double_output_detected' => !empty($source_mapping_state['double_output_detected']),
                'duplicate_output_status' => isset($source_mapping_state['duplicate_output_status']) ? (string) $source_mapping_state['duplicate_output_status'] : 'not_detected',
            ),
            'suite_connection' => array(
                'connection_mode' => isset($connection_state['connection_mode']) ? (string) $connection_state['connection_mode'] : 'packaged_preview_only',
                'readiness' => isset($connection_state['readiness']) ? (string) $connection_state['readiness'] : 'source not yet confirmed',
            ),
            'baseline_status' => array(
                'captured' => !empty($baseline_snapshot['captured']),
                'url_normalization_clean' => !empty($baseline_snapshot['url_normalization_clean']),
                'residuals' => isset($baseline_snapshot['url_normalization_residuals']) ? (array) $baseline_snapshot['url_normalization_residuals'] : array(),
            ),
            'operator_inputs' => array(
                'complete' => !empty($operator_input_state['complete']),
                'missing_fields' => isset($operator_input_state['missing_fields']) ? (array) $operator_input_state['missing_fields'] : array(),
            ),
            'source_mapping' => array(
                'confirmed' => !empty($source_mapping_state['confirmed']),
                'blocking_requirements' => isset($source_mapping_state['blocking_requirements']) ? (array) $source_mapping_state['blocking_requirements'] : array(),
                'heuristic_requirements' => isset($source_mapping_state['heuristic_requirements']) ? (array) $source_mapping_state['heuristic_requirements'] : array(),
                'missing_requirements' => isset($source_mapping_state['missing_requirements']) ? (array) $source_mapping_state['missing_requirements'] : array(),
            ),
            'optimization_eligibility' => isset($optimization_state['eligibility']) ? (string) $optimization_state['eligibility'] : 'recommend_only',
            'open_blockers' => array_values(array_unique(array_map('strval', (array) ($runtime_blockers['open'] ?? array())))),
            'heuristic_findings' => array_values(array_unique(array_map('strval', (array) ($runtime_blockers['heuristic'] ?? array())))),
            'rollback_required' => $mode === 'safe_mode',
        );
    }

    public function get_snapshot(): array
    {
        return $this->snapshot;
    }
}
