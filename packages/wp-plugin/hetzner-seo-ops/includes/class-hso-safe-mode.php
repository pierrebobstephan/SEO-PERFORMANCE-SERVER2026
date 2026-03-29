<?php

if (!defined('ABSPATH')) {
    exit;
}

class HSO_Safe_Mode
{
    public function build_state(string $mode, array $license_state, array $conflict_state): array
    {
        $reasons = array();

        if ($mode === 'safe_mode') {
            $reasons[] = 'blocking conflict or malformed local state';
        }
        if (empty($license_state['domain_match'])) {
            $reasons[] = 'bound domain is missing or mismatched';
        }
        if (!empty($conflict_state['source_mapping_unclear'])) {
            $reasons[] = 'source mapping is not confirmed';
        }

        return array(
            'mode' => $mode,
            'safe_mode_required' => $mode === 'safe_mode',
            'observe_only_required' => $mode === 'observe_only',
            'approval_required' => $mode === 'approval_required',
            'reasons' => array_values(array_unique($reasons)),
        );
    }
}
