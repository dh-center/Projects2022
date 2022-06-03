from aiohttp import ClientTimeout

proxy_connector_params = {
    "limit": 1000,
    "limit_per_host": 0,
    "force_close": False,
    "enable_cleanup_closed": False,
    "loop": None,
    "verify_ssl": True,
    "fingerprint": None,
    "use_dns_cache": True,
    "ttl_dns_cache": 10,
    "ssl_context": None,
    "local_addr": None
}

tcp_connector_params = {
    "limit": 1000,
    "limit_per_host": 0,
    "force_close": False,
    "enable_cleanup_closed": False,
    "loop": None,
    "verify_ssl": True,
    "fingerprint": None,
    "use_dns_cache": True,
    "ttl_dns_cache": 10,
    "ssl_context": None,
    "local_addr": None
}

CLIENT_TIMEOUT = ClientTimeout(
    total=30.0,
    sock_connect=30.0,
    sock_read=30.0
)
