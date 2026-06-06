# Omni Tuya Local

Home Assistant custom integration for local Tuya control, based on the Tuya Local work built for Omni.

This is a HACS integration, not an add-on. It creates native Home Assistant entities and talks directly to devices through `tinytuya`.

## Included

- Local polling and command execution through TinyTuya.
- Network discovery using UDP listen, TinyTuya scan and TCP sweep.
- Optional Tuya IoT Cloud sync to import device IDs and local keys.
- Native Home Assistant entities:
  - `switch`
  - `light`
  - `lock`
  - `sensor`
  - `climate`
  - `cover`
- Multi-DPS foundation through `dps_map`.
- Sub-device/gateway fields from the Omni implementation.

## Not Included

- Matter bridge.
- HomeKit bridge.
- OmniCore runtime.
- Homebridge.
- Any saved credentials from Omni.

Home Assistant can export entities to Matter/HomeKit through its own integrations if needed.

## Installation

Add this repository as a custom HACS repository, category `Integration`, then install **Omni Tuya Local**.

Restart Home Assistant and add the integration from:

`Settings > Devices & services > Add integration > Omni Tuya Local`

## Services

The integration exposes these services:

- `omni_tuya_local.add_device`
- `omni_tuya_local.remove_device`
- `omni_tuya_local.scan_network`
- `omni_tuya_local.sync_cloud`
- `omni_tuya_local.reload_devices`

## Cloud Sync

Cloud sync only imports device metadata and local keys. Runtime control remains local.

Required Tuya IoT values:

- API key / Access ID
- API secret / Access Secret
- Region: `us`, `eu`, `cn` or `in`

## Migration From Omni

Export each device from Omni with:

- `device_id`
- `name`
- `local_key`
- `host` or `ip`
- `version`
- `domain`
- optional `dps_map`
- optional gateway/sub-device fields

Then add them with the `omni_tuya_local.add_device` service or import via cloud sync.
