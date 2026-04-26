<?php

if (!defined('ABSPATH')) {
    exit;
}

class HSO_License_Check
{
    public function get_local_license_snapshot(array $seed = array()): array
    {
        $snapshot = get_option('hso_local_license_snapshot', array());
        if (!is_array($snapshot)) {
            $snapshot = array();
        }

        $defaults = array(
            'license_id' => 'TBD',
            'customer_id' => 'operator input required',
            'product_id' => 'hso-plugin',
            'status' => 'approval_required',
            'bound_domain' => '',
            'allowed_subdomains' => array(),
            'allowed_scopes' => array('homepage_only', 'feature:meta_description'),
            'allowed_features' => array('meta_description'),
            'release_channel' => 'pilot',
            'policy_channel' => 'pilot',
            'rollback_profile_id' => 'TBD',
            'issued_at' => '',
            'non_expiring' => true,
            'expires_at' => '',
            'integrity' => array(
                'signature' => 'source not yet confirmed',
                'signature_state' => 'operator_signing_required',
                'signing_key_reference' => 'local_server_signing_key',
            ),
            'operator_inputs_complete' => false,
        );

        return array_merge($defaults, $seed, $snapshot);
    }

    public function evaluate_domain(string $current_domain, array $seed = array()): array
    {
        $snapshot = $this->get_local_license_snapshot($seed);
        $bound_domain = $this->normalize_domain((string) $snapshot['bound_domain']);
        $current_domain = $this->normalize_domain($current_domain);
        $allowed_subdomains = $this->normalize_allowed_subdomains(
            $bound_domain,
            (array) $snapshot['allowed_subdomains']
        );
        $domain_match = $bound_domain !== '' && ($current_domain === $bound_domain || in_array($current_domain, $allowed_subdomains, true));

        return array(
            'license_id' => (string) $snapshot['license_id'],
            'customer_id' => (string) $snapshot['customer_id'],
            'product_id' => (string) $snapshot['product_id'],
            'status' => (string) $snapshot['status'],
            'bound_domain' => $bound_domain,
            'allowed_subdomains' => array_values($allowed_subdomains),
            'release_channel' => (string) $snapshot['release_channel'],
            'policy_channel' => (string) $snapshot['policy_channel'],
            'allowed_scopes' => array_values(array_filter(array_map('strval', (array) $snapshot['allowed_scopes']))),
            'allowed_features' => array_values(array_filter(array_map('strval', (array) $snapshot['allowed_features']))),
            'rollback_profile_id' => (string) $snapshot['rollback_profile_id'],
            'issued_at' => isset($snapshot['issued_at']) ? trim((string) $snapshot['issued_at']) : '',
            'non_expiring' => !empty($snapshot['non_expiring']),
            'expires_at' => isset($snapshot['expires_at']) ? trim((string) $snapshot['expires_at']) : '',
            'integrity' => is_array($snapshot['integrity']) ? $snapshot['integrity'] : array(),
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

    private function normalize_allowed_subdomains(string $bound_domain, array $allowed_subdomains): array
    {
        $normalized = array();
        foreach ($allowed_subdomains as $item) {
            $candidate = $this->normalize_domain((string) $item);
            if ($candidate === '' || !$this->is_explicit_descendant($candidate, $bound_domain)) {
                continue;
            }
            $normalized[$candidate] = $candidate;
        }

        return array_values($normalized);
    }

    private function is_explicit_descendant(string $candidate, string $bound_domain): bool
    {
        if ($candidate === '' || $bound_domain === '' || $candidate === $bound_domain) {
            return false;
        }

        return str_ends_with($candidate, '.' . $bound_domain);
    }
}
