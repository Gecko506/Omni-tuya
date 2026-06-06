DOMAIN = "omni_tuya_local"
INTEGRATION_VERSION = "0.2.2"
BUILD_NUMBER = "20260606.4"

CONF_REGION = "region"
CONF_API_KEY = "api_key"
CONF_API_SECRET = "api_secret"
CONF_DEVICE_ID = "device_id"
CONF_LOCAL_KEY = "local_key"
CONF_HOST = "host"
CONF_VERSION = "version"
CONF_DPS_MAP = "dps_map"
CONF_PRODUCT_NAME = "product_name"
CONF_DEVICE_TYPE = "device_type"
CONF_NODE_ID = "node_id"
CONF_GATEWAY_ID = "gateway_id"
CONF_GATEWAY_LOCAL_KEY = "gateway_local_key"
CONF_GATEWAY_HOST = "gateway_host"

DEFAULT_REGION = "us"
DEFAULT_VERSION = "3.3"
DEFAULT_POLL_INTERVAL = 15
DEFAULT_DISCOVERY_INTERVAL = 300

EXPORT_DOMAINS = [
    "switch",
    "light",
    "fan",
    "lock",
    "cover",
    "climate",
    "sensor",
    "binary_sensor",
    "button",
    "number",
    "vacuum",
    "alarm_control_panel",
    "humidifier",
]
PLATFORMS = [
    "switch",
    "light",
    "fan",
    "lock",
    "cover",
    "climate",
    "sensor",
    "binary_sensor",
    "button",
    "number",
    "vacuum",
    "alarm_control_panel",
    "humidifier",
    "text",
]

DEVICE_TYPES = {
    "generic": {"label": "Generico", "icon": "mdi:devices"},
    "kitchen": {"label": "Cocina", "icon": "mdi:stove"},
    "coffee_maker": {"label": "Cafetera", "icon": "mdi:coffee-maker"},
    "kettle": {"label": "Hervidor", "icon": "mdi:kettle"},
    "rice_cooker": {"label": "Arrocera", "icon": "mdi:rice"},
    "air_fryer": {"label": "Freidora de aire", "icon": "mdi:pot-steam"},
    "microwave": {"label": "Microondas", "icon": "mdi:microwave"},
    "oven": {"label": "Horno", "icon": "mdi:toaster-oven"},
    "refrigerator": {"label": "Refrigerador", "icon": "mdi:fridge"},
    "washer": {"label": "Lavadora", "icon": "mdi:washing-machine"},
    "dryer": {"label": "Secadora", "icon": "mdi:tumble-dryer"},
    "dishwasher": {"label": "Lavaplatos", "icon": "mdi:dishwasher"},
    "fan": {"label": "Ventilador", "icon": "mdi:fan"},
    "air_conditioner": {"label": "Aire acondicionado", "icon": "mdi:air-conditioner"},
    "heater": {"label": "Calefactor", "icon": "mdi:radiator"},
    "humidifier": {"label": "Humidificador", "icon": "mdi:air-humidifier"},
    "dehumidifier": {"label": "Deshumidificador", "icon": "mdi:air-humidifier-off"},
    "air_purifier": {"label": "Purificador de aire", "icon": "mdi:air-purifier"},
    "robot_vacuum": {"label": "Robot aspirador", "icon": "mdi:robot-vacuum"},
    "vacuum": {"label": "Aspiradora", "icon": "mdi:vacuum"},
    "alarm_kit": {"label": "Kit de alarma", "icon": "mdi:shield-home"},
    "siren": {"label": "Sirena", "icon": "mdi:alarm-light"},
    "motion_sensor": {"label": "Sensor de movimiento", "icon": "mdi:motion-sensor"},
    "door_sensor": {"label": "Sensor puerta/ventana", "icon": "mdi:door-open"},
    "smoke_sensor": {"label": "Sensor de humo", "icon": "mdi:smoke-detector"},
    "water_leak_sensor": {"label": "Sensor de fuga de agua", "icon": "mdi:water-alert"},
    "temperature_sensor": {"label": "Sensor temperatura", "icon": "mdi:thermometer"},
    "humidity_sensor": {"label": "Sensor humedad", "icon": "mdi:water-percent"},
    "presence_sensor": {"label": "Sensor presencia", "icon": "mdi:account-radar"},
    "lock": {"label": "Cerradura", "icon": "mdi:lock-smart"},
    "garage_door": {"label": "Porton/garaje", "icon": "mdi:garage"},
    "curtain": {"label": "Cortina", "icon": "mdi:curtains"},
    "blind": {"label": "Persiana", "icon": "mdi:blinds"},
    "light": {"label": "Luz", "icon": "mdi:lightbulb"},
    "dimmer": {"label": "Dimmer", "icon": "mdi:lightbulb-on"},
    "led_strip": {"label": "Tira LED", "icon": "mdi:led-strip-variant"},
    "outlet": {"label": "Tomacorriente", "icon": "mdi:power-socket-us"},
    "power_strip": {"label": "Regleta", "icon": "mdi:power-strip"},
    "switch": {"label": "Interruptor", "icon": "mdi:light-switch"},
    "ir_remote": {"label": "Control IR/RF", "icon": "mdi:remote"},
    "pet_feeder": {"label": "Comedero mascotas", "icon": "mdi:food-outline"},
    "water_fountain": {"label": "Fuente de agua", "icon": "mdi:fountain"},
    "sprinkler": {"label": "Riego", "icon": "mdi:sprinkler-variant"},
    "valve": {"label": "Valvula", "icon": "mdi:valve"},
    "pump": {"label": "Bomba", "icon": "mdi:pump"},
}

TUYA_BRIGHTNESS_MAX = 1000
TUYA_BRIGHTNESS_MIN = 10

SERVICE_ADD_DEVICE = "add_device"
SERVICE_REMOVE_DEVICE = "remove_device"
SERVICE_SCAN_NETWORK = "scan_network"
SERVICE_SYNC_CLOUD = "sync_cloud"
SERVICE_SET_DEVICE_IP = "set_device_ip"
SERVICE_SET_DEVICE_DOMAIN = "set_device_domain"
SERVICE_SET_DEVICE_TYPE = "set_device_type"
SERVICE_RELOAD_DEVICES = "reload_devices"
SERVICE_DIAGNOSTICS = "diagnostics"

STORAGE_KEY = "omni_tuya_local.devices"
STORAGE_VERSION = 1
