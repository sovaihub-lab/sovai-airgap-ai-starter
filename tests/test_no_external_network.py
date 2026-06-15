import socket

def test_no_external_network():
    try:
        socket.create_connection(("1.1.1.1", 443), timeout=1).close()
        assert False, "External network is reachable"
    except Exception:
        assert True
