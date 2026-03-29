<?php

if (!defined('ABSPATH')) {
    exit;
}

class HSO_License_Check
{
    public function get_local_license_snapshot(): array
    {
        $snapshot = get_option('hso_local_license_snapshot', array());
        if (!is_array($snapshot)) {
            $snapshot = array();
        }

        $defaults = array(
            'license_id' => 'TBD',
            'status' => 'approval_required',
            'bound_domain' => '',
            'allowed_subdomains' => array(),
            'allowed_scopes' => array('homepage_only', 'feature:meta_description'),
            'release_channel' => 'pilot',
            'policy_channel' => 'pilot',
            'rollback_profile_id' => 'TBD',
            'operator_inputs_complete' => false,
        );

        return array_merge($defaults, $snapshot);
    }

    public function evaluate_domain(string $current_domain): array
    {
        $snapshot = $this->get_local_license_snapshot();
        $bound_domain = $this->normalize_domain((string) $snapshot['bound_domain']);
        $current_domain = $this->normalize_domain($current_domain);
        $allowed_subdomains = array_map(array($this, 'normalize_domain'), (array) $snapshot['allowed_subdomains']);
        $domain_match = $bound_domain !== '' && ($current_domain === $bound_domain || in_array($current_domain, $allowed_subdomains, true));

        return array(
            'license_id' => (string) $snapshot['license_id'],
            'status' => (string) $snapshot['status'],
            'bound_domain' => $bound_domain,
            'release_channel' => (string) $snapshot['release_channel'],
            'policy_channel' => (string) $snapshot['policy_channel'],
            'allowed_scopes' => array_values(array_filter(array_map('strval', (array) $snapshot['allowed_scopes']))),
            'rollback_profile_id' => (string) $snapshot['rollback_profile_id'],
            'operator_inputs_complete' => (bool) $snapshot['operator_inputs_complete'],
            'domain_match' => $domain_match,
        );
    }

    private function normalize_domain(string $domain): string
    {
        $domain = strtolower(trim($domain));
        $domain = preg_replace('#^https?://#', '', $domain);
        return trim((string) $domain, '/');
    }
}
