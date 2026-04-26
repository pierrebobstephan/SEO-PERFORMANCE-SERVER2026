<?php

if (!defined('ABSPATH')) {
    exit;
}

class HSO_Safe_Mode
{
    public function build_state(
        string $mode,
        array $license_state,
        array $conflict_state,
        array $baseline_snapshot = array(),
        array $bridge_profile = array(),
        array $runtime_blockers = array()
    ): array
    {
        $reasons = array();

        if ($mode === 'safe_mode') {
            $reasons[] = !empty($conflict_state['has_blocking_conflict'])
                ? 'blocking conflict is present'
                : 'safe mode remains active until validation and approval gates are satisfied';
        }
        if (empty($license_state['domain_match'])) {
            $reasons[] = 'bound domain is missing or mismatched';
        }
        if (!empty($conflict_state['source_mapping_unclear'])) {
            $reasons[] = 'source mapping is not confirmed';
        }
        if (!empty($baseline_snapshot) && empty($baseline_snapshot['url_normalization_clean'])) {
            $reasons[] = 'url normalization is not yet clean';
        }
        if (!empty($runtime_blockers['open'])) {
            $reasons = array_merge($reasons, array_map('strval', (array) $runtime_blockers['open']));
        }

        return array(
            'mode' => $mode,
            'safe_mode_required' => $mode === 'safe_mode',
            'observe_only_required' => $mode === 'observe_only',
            'approval_required' => $mode === 'approval_required',
            'reasons' => array_values(array_unique($reasons)),
            'resolved_blockers' => array_values(array_unique(array_map('strval', (array) ($runtime_blockers['resolved'] ?? array())))),
        );
    }
}
