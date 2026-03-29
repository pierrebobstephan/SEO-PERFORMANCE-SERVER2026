<?php

if (!defined('ABSPATH')) {
    exit;
}

class HSO_Meta_Description_Module
{
    private array $runtime_context;
    private array $conflict_state;
    private HSO_Rollback_Registry $rollback_registry;
    private HSO_Validation_Status $validation_status;

    public function __construct(
        array $runtime_context,
        array $conflict_state,
        HSO_Rollback_Registry $rollback_registry,
        HSO_Validation_Status $validation_status
    ) {
        $this->runtime_context = $runtime_context;
        $this->conflict_state = $conflict_state;
        $this->rollback_registry = $rollback_registry;
        $this->validation_status = $validation_status;
    }

    public function register(): void
    {
        $this->rollback_registry->register_entry(
            'homepage_meta_description',
            array(
                'before_state_key' => 'homepage_meta_description_source',
                'rollback_notes' => 'Return to previous homepage meta description source or leave ownership with current SEO plugin.',
                'validation_window' => 'immediate/1d/7d',
            )
        );

        if (!$this->is_eligible()) {
            return;
        }

        add_action('wp_head', array($this, 'render_meta_description'), 1);
    }

    public function is_eligible(): bool
    {
        if (($this->runtime_context['mode'] ?? 'observe_only') !== 'active_scoped') {
            return false;
        }

        if (!in_array('homepage_only', (array) ($this->runtime_context['allowed_scopes'] ?? array()), true)) {
            return false;
        }

        if (!in_array('feature:meta_description', (array) ($this->runtime_context['allowed_scopes'] ?? array()), true)) {
            return false;
        }

        if (empty($this->runtime_context['scope_confirmed']) || empty($this->runtime_context['source_mapping_confirmed'])) {
            return false;
        }

        if (!empty($this->conflict_state['source_mapping_unclear']) || !empty($this->conflict_state['rank_math_active'])) {
            return false;
        }

        $description = trim((string) ($this->runtime_context['target_meta_description'] ?? ''));
        return $description !== '';
    }

    public function render_meta_description(): void
    {
        if (!function_exists('is_front_page') || !is_front_page()) {
            return;
        }

        $description = trim((string) ($this->runtime_context['target_meta_description'] ?? ''));
        if ($description === '') {
            return;
        }

        echo '<meta name="description" content="' . esc_attr($description) . "\" />\n";
    }
}
