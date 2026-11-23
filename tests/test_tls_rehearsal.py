from pathlib import Path

def test_tls_rehearsal_config_contains_security_controls():
    root=Path(__file__).resolve().parents[1]
    s=(root/"deploy/nginx.conf").read_text()
    assert "listen 8443 ssl" in s
    assert "ssl_protocols TLSv1.2 TLSv1.3" in s
    assert "limit_req_status 429" in s
    assert "client_max_body_size 64k" in s
    c=(root/"deploy/tls-rehearsal.compose.yml").read_text()
    assert "127.0.0.1:8443:8443" in c
    assert "./tls/server.key" in c
    assert "no-new-privileges:true" in c
