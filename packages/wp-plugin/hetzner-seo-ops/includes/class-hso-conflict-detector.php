<?php

if (!defined('ABSPATH')) {
    exit;
}

class HSO_Conflict_Detector
{
    public function scan(): array
    {
        $active_plugins = (array) get_option('active_plugins', array());
        $normalized_plugins = array_map('strval', $active_plugins);

        $seo_plugins = array_values(array_filter($normalized_plugins, array($this, 'is_seo_plugin')));
        $builders = array_values(array_filter($normalized_plugins, array($this, 'is_builder_plugin')));
        $rank_math_active = $this->plugin_list_contains($normalized_plugins, 'seo-by-rank-math');
        $seo_plugin_count = count($seo_plugins);
        $external_seo_owner_active = $seo_plugin_count === 1;
        $single_seo_plugin_slug = $external_seo_owner_active ? (string) $seo_plugins[0] : '';
        $coexistence_mode = 'no_external_seo_owner';
        if ($seo_plugin_count > 1) {
            $coexistence_mode = 'multiple_external_seo_owners_blocking';
        } elseif ($rank_math_active) {
            $coexistence_mode = 'rank_math_controlled_coexistence';
        } elseif ($external_seo_owner_active) {
            $coexistence_mode = 'single_external_seo_owner_active';
        }

        $theme_name = 'source not yet confirmed';
        if (function_exists('wp_get_theme')) {
            $theme = wp_get_theme();
            if ($theme && method_exists($theme, 'get')) {
                $theme_name = (string) $theme->get('Name');
            }
        }

        return array(
            'active_plugins' => $normalized_plugins,
            'active_seo_plugins' => $seo_plugins,
            'active_builders' => $builders,
            'theme_name' => $theme_name,
            'rank_math_active' => $rank_math_active,
            'external_seo_owner_active' => $external_seo_owner_active,
            'single_seo_plugin_slug' => $single_seo_plugin_slug,
            'coexistence_mode' => $coexistence_mode,
            'source_mapping_unclear' => $seo_plugin_count > 1,
            'has_blocking_conflict' => $seo_plugin_count > 1,
        );
    }

    private function is_seo_plugin(string $plugin_slug): bool
    {
        $needles = array(
            'seo-by-rank-math',
            'wordpress-seo',
            'all-in-one-seo-pack',
            'autodescription',
            'seopress',
        );

        foreach ($needles as $needle) {
            if (strpos($plugin_slug, $needle) !== false) {
                return true;
            }
        }

        return false;
    }

    private function is_builder_plugin(string $plugin_slug): bool
    {
        $needles = array(
            'elementor',
            'beaver-builder',
            'oxygen',
            'siteorigin-panels',
            'js_composer',
            'divi-builder',
        );

        foreach ($needles as $needle) {
            if (strpos($plugin_slug, $needle) !== false) {
                return true;
            }
        }

        return false;
    }

    private function plugin_list_contains(array $plugins, string $needle): bool
    {
        foreach ($plugins as $plugin_slug) {
            if (strpos($plugin_slug, $needle) !== false) {
                return true;
            }
        }

        return false;
    }
}
