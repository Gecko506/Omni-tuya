DOMAIN = "omni_tuya_local"

CONF_REGION = "region"
CONF_API_KEY = "api_key"
CONF_API_SECRET = "api_secret"
CONF_DEVICE_ID = "device_id"
CONF_LOCAL_KEY = "local_key"
CONF_HOST = "host"
CONF_VERSION = "version"
CONF_DPS_MAP = "dps_map"
CONF_PRODUCT_NAME = "product_name"
CONF_NODE_ID = "node_id"
CONF_GATEWAY_ID = "gateway_id"
CONF_GATEWAY_LOCAL_KEY = "gateway_local_key"
CONF_GATEWAY_HOST = "gateway_host"

DEFAULT_REGION = "us"
DEFAULT_VERSION = "3.3"
DEFAULT_POLL_INTERVAL = 15
DEFAULT_DISCOVERY_INTERVAL = 300

PLATFORMS = ["switch", "light", "lock", "sensor", "climate", "cover"]

TUYA_BRIGHTNESS_MAX = 1000
TUYA_BRIGHTNESS_MIN = 10

SERVICE_ADD_DEVICE = "add_device"
SERVICE_REMOVE_DEVICE = "remove_device"
SERVICE_SCAN_NETWORK = "scan_network"
SERVICE_SYNC_CLOUD = "sync_cloud"
SERVICE_RELOAD_DEVICES = "reload_devices"

STORAGE_KEY = "omni_tuya_local.devices"
STORAGE_VERSION = 1
