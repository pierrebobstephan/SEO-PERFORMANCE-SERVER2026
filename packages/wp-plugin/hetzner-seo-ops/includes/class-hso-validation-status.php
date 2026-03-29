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

    public function build_snapshot(string $mode, array $license_state, array $conflict_state): array
    {
        return array(
            'mode' => $mode,
            'license_status' => isset($license_state['status']) ? (string) $license_state['status'] : 'approval_required',
            'domain_match' => !empty($license_state['domain_match']),
            'primary_signals' => array(
                'homepage_meta_description_single' => false,
                'source_mapping_confirmed' => false,
            ),
            'neighbor_signals' => array(
                'title_stable' => true,
                'canonical_stable' => true,
                'robots_stable' => true,
                'rank_math_active' => !empty($conflict_state['rank_math_active']),
            ),
            'rollback_required' => $mode === 'safe_mode',
        );
    }

    public function get_snapshot(): array
    {
        return $this->snapshot;
    }
}
