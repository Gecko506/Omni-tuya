from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class TuyaEntityDescription:
    entity_id_suffix: str
    platform: str
    dps_id: str = "1"
    semantic: str = "state"
    name: str | None = None
    device_class: str | None = None
    unit: str | None = None


@dataclass(slots=True)
class TuyaDeviceConfig:
    device_id: str
    name: str
    local_key: str
    host: str = ""
    version: str = "3.3"
    domain: str = "switch"
    product_name: str = ""
    area_id: str | None = None
    enabled: bool = True
    poll_interval: int = 15
    dps_map: dict[str, Any] = field(default_factory=dict)
    gateway_id: str = ""
    node_id: str = ""
    gateway_host: str = ""
    gateway_local_key: str = ""
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TuyaDeviceConfig":
        return cls(
            device_id=str(data.get("device_id") or data.get("id") or ""),
            name=str(data.get("name") or data.get("device_id") or "Tuya Device"),
            local_key=str(data.get("local_key") or data.get("key") or ""),
            host=str(data.get("host") or data.get("ip") or ""),
            version=str(data.get("version") or data.get("ver") or "3.3"),
            domain=str(data.get("domain") or guess_domain(data)),
            product_name=str(data.get("product_name") or ""),
            area_id=data.get("area_id"),
            enabled=bool(data.get("enabled", True)),
            poll_interval=int(data.get("poll_interval") or 15),
            dps_map=dict(data.get("dps_map") or {}),
            gateway_id=str(data.get("gateway_id") or ""),
            node_id=str(data.get("node_id") or data.get("cid") or ""),
            gateway_host=str(data.get("gateway_host") or data.get("gateway_ip") or ""),
            gateway_local_key=str(data.get("gateway_local_key") or ""),
            raw=dict(data.get("raw") or {}),
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "device_id": self.device_id,
            "name": self.name,
            "local_key": self.local_key,
            "host": self.host,
            "ip": self.host,
            "version": self.version,
            "domain": self.domain,
            "product_name": self.product_name,
            "area_id": self.area_id,
            "enabled": self.enabled,
            "poll_interval": self.poll_interval,
            "dps_map": self.dps_map,
            "gateway_id": self.gateway_id,
            "node_id": self.node_id,
            "gateway_host": self.gateway_host,
            "gateway_local_key": self.gateway_local_key,
            "raw": self.raw,
        }


def guess_domain(data: dict[str, Any]) -> str:
    name = str(data.get("name") or "").lower()
    product = str(data.get("product_name") or "").lower()
    category = str(data.get("category") or "").lower()
    if any(word in name or word in product for word in ("light", "lamp", "bombillo", "luz", "dimmer")):
        return "light"
    if any(word in name or word in product for word in ("lock", "cerradura")) or category in {"ms", "cs"}:
        return "lock"
    if any(word in name or word in product for word in ("climate", "thermostat", "termostato", "ac ", "aire")):
        return "climate"
    if any(word in name or word in product for word in ("cover", "curtain", "shade", "cortina")):
        return "cover"
    if any(word in name or word in product for word in ("sensor", "temperature", "humidity", "temp", "humedad")):
        return "sensor"
    return "switch"


def normalize_device(data: dict[str, Any]) -> dict[str, Any]:
    return TuyaDeviceConfig.from_dict(data).as_dict()
