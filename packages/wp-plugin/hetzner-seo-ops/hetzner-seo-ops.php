<?php
/**
 * Plugin Name: Hetzner SEO Ops
 * Description: Doctrine-enforced SEO and performance execution plane. Safe and observe-only defaults stay active until license, scope, policy, validation, and rollback gates are satisfied.
 * Version: 0.0.1-dev
 * Requires at least: 6.0
 * Requires PHP: 7.4
 */

if (!defined('ABSPATH')) {
    exit;
}

define('HSO_PLUGIN_VERSION', '0.0.1-dev');
define('HSO_PLUGIN_DIR', plugin_dir_path(__FILE__));
define('HSO_PLUGIN_URL', plugin_dir_url(__FILE__));

require_once HSO_PLUGIN_DIR . 'includes/class-hso-license-check.php';
require_once HSO_PLUGIN_DIR . 'includes/class-hso-safe-mode.php';
require_once HSO_PLUGIN_DIR . 'includes/class-hso-conflict-detector.php';
require_once HSO_PLUGIN_DIR . 'includes/class-hso-rollback-registry.php';
require_once HSO_PLUGIN_DIR . 'includes/class-hso-validation-status.php';
require_once HSO_PLUGIN_DIR . 'includes/modules/class-hso-meta-description-module.php';
require_once HSO_PLUGIN_DIR . 'admin/class-hso-admin-screen.php';
require_once HSO_PLUGIN_DIR . 'includes/class-hso-plugin.php';

HSO_Plugin::boot();
