<?php
/**
 * Plugin Name: Site Optimizer Bridge
 * Description: Doctrine-enforced SEO and performance execution plane. Safe and observe-only defaults stay active until license, scope, policy, validation, and rollback gates are satisfied.
 * Version: 0.1.0-real-staging1
 * Requires at least: 6.0
 * Requires PHP: 7.4
 */

if (!defined('ABSPATH')) {
    exit;
}

define('HSO_PLUGIN_VERSION', '0.1.0-real-staging1');
define('HSO_PLUGIN_DIR', plugin_dir_path(__FILE__));
define('HSO_PLUGIN_URL', plugin_dir_url(__FILE__));

require_once HSO_PLUGIN_DIR . 'includes/class-hso-bridge-config.php';
require_once HSO_PLUGIN_DIR . 'includes/class-hso-baseline-capture.php';
require_once HSO_PLUGIN_DIR . 'includes/class-hso-optimization-gate.php';
require_once HSO_PLUGIN_DIR . 'includes/class-hso-license-check.php';
require_once HSO_PLUGIN_DIR . 'includes/class-hso-safe-mode.php';
require_once HSO_PLUGIN_DIR . 'includes/class-hso-conflict-detector.php';
require_once HSO_PLUGIN_DIR . 'includes/class-hso-rollback-registry.php';
require_once HSO_PLUGIN_DIR . 'includes/class-hso-validation-status.php';
require_once HSO_PLUGIN_DIR . 'includes/class-hso-recommendation-action-center.php';
require_once HSO_PLUGIN_DIR . 'includes/modules/class-hso-meta-description-module.php';
require_once HSO_PLUGIN_DIR . 'admin/class-hso-admin-screen.php';
require_once HSO_PLUGIN_DIR . 'includes/class-hso-plugin.php';

register_activation_hook(__FILE__, array('HSO_Plugin', 'activate'));

add_action('init', array('HSO_Plugin', 'boot'), 20);
