<?php

if (!defined('ABSPATH')) {
    exit;
}

class HSO_Rollback_Registry
{
    private array $entries = array();

    public function register_entry(string $module_slug, array $payload): void
    {
        $this->entries[$module_slug] = array(
            'module' => $module_slug,
            'before_state_key' => isset($payload['before_state_key']) ? (string) $payload['before_state_key'] : 'TBD',
            'rollback_notes' => isset($payload['rollback_notes']) ? (string) $payload['rollback_notes'] : 'TBD',
            'validation_window' => isset($payload['validation_window']) ? (string) $payload['validation_window'] : '1d/7d',
        );
    }

    public function get_entries(): array
    {
        return $this->entries;
    }
}
