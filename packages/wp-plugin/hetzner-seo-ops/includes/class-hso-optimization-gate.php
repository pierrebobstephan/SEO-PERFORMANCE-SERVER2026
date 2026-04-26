<?php

if (!defined('ABSPATH')) {
    exit;
}

class HSO_Optimization_Gate
{
    public function evaluate(
        string $mode,
        array $license_state,
        array $conflict_state,
        array $baseline_snapshot,
        array $bridge_profile,
        array $operator_input_state = array(),
        array $source_mapping_state = array(),
        array $runtime_blockers = array()
    ): array {
        $allowed = array(
            'baseline_capture',
            'head_diagnostics',
            'structure_diagnostics',
            'visibility_diagnostics',
        );
        $forbidden = array(
            'rank_math_deactivation',
            'sitewide_meta_overwrite',
            'global_head_rewrite',
            'canonical_override',
            'multi_domain_operation',
            'theme_or_builder_replacement',
        );
        $reasons = array();
        $blocking_reasons = array();
        $advisory_reasons = array();
        $eligibility = 'recommend_only';

        if (empty($license_state['domain_match'])) {
            $eligibility = 'blocked';
            $blocking_reasons[] = 'bound domain mismatch';
        }

        if (empty($baseline_snapshot['url_normalization_clean'])) {
            $eligibility = 'blocked';
            $blocking_reasons[] = 'url normalization is not yet clean';
        }

        if (!empty($conflict_state['has_blocking_conflict'])) {
            $eligibility = 'blocked';
            $blocking_reasons[] = 'blocking plugin conflict is present';
        }

        if (!empty($source_mapping_state['hard_blocking_duplicate_output'])) {
            $eligibility = 'blocked';
            $blocking_reasons[] = 'duplicate head or meta output is present';
        } elseif (!empty($source_mapping_state['heuristic_duplicate_output'])) {
            $advisory_reasons[] = 'duplicate head or meta output remains a heuristic suspicion';
        }

        if (!empty($conflict_state['source_mapping_unclear'])) {
            $eligibility = 'blocked';
            $blocking_reasons[] = 'source mapping remains unclear';
        } elseif (!empty($conflict_state['external_seo_owner_active'])) {
            $advisory_reasons[] = 'existing SEO owner remains active under controlled coexistence';
        }

        if (!empty($source_mapping_state['blocking_requirements'])) {
            $eligibility = 'blocked';
            $blocking_reasons[] = 'source mapping is not confirmed';
        } elseif (empty($source_mapping_state['confirmed'])) {
            $advisory_reasons[] = 'source mapping still needs review';
        }

        if (empty($operator_input_state['complete'])) {
            $eligibility = 'blocked';
            $blocking_reasons[] = 'required operator inputs are incomplete';
        }

        if (empty($bridge_profile['scope_confirmed'])) {
            $advisory_reasons[] = 'scope is not confirmed';
        }

        if ($eligibility !== 'blocked'
            && empty($conflict_state['source_mapping_unclear'])
            && !empty($source_mapping_state['confirmed'])
            && !empty($operator_input_state['complete'])
            && !empty($bridge_profile['scope_confirmed'])
            && !empty($license_state['domain_match'])
            && !empty($baseline_snapshot['url_normalization_clean'])
            && empty($conflict_state['has_blocking_conflict'])
            && empty($conflict_state['external_seo_owner_active'])
            && empty($source_mapping_state['hard_blocking_duplicate_output'])
            && empty($source_mapping_state['heuristic_duplicate_output'])
        ) {
            $eligibility = 'reversible_change_ready';
            $allowed[] = 'prepare_reversible_homepage_meta_description';
        }

        $reasons = array_values(array_unique(array_merge($blocking_reasons, $advisory_reasons)));

        return array(
            'mode' => $mode,
            'eligibility' => $eligibility,
            'recommendation_only' => $eligibility !== 'reversible_change_ready',
            'allowed_optimizations' => array_values(array_unique($allowed)),
            'forbidden_optimizations' => $forbidden,
            'reasons' => $reasons,
            'blocking_reasons' => array_values(array_unique($blocking_reasons)),
            'advisory_reasons' => array_values(array_unique($advisory_reasons)),
            'open_blockers' => array_values(array_unique(array_map('strval', (array) ($runtime_blockers['open'] ?? array())))),
            'heuristic_findings' => array_values(array_unique(array_map('strval', (array) ($runtime_blockers['heuristic'] ?? array())))),
            'resolved_blockers' => array_values(array_unique(array_map('strval', (array) ($runtime_blockers['resolved'] ?? array())))),
        );
    }
}
