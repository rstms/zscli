from logging import debug, info
from pathlib import Path


def test_api_ls(test_api):
    cert_list = test_api.list("all", None)
    assert isinstance(cert_list, list)
    assert len(cert_list)
    assert isinstance(cert_list[0], dict)
    for cert in cert_list:
        info(
            {
                "name": cert["common_name"],
                "status": cert["status"],
                "id": cert["id"],
            }
        )


def test_api_download(test_api, shared_datadir):
    cert_list = test_api.list("issued", None)
    assert isinstance(cert_list, list)
    assert isinstance(cert_list[0], dict)
    assert "id" in cert_list[0]
    _id = cert_list[0]["id"]
    cross_signed = True
    files = test_api.download(_id, cross_signed, shared_datadir)
    assert isinstance(files, list)
    assert len(files)
    assert isinstance(files[0], Path)
    for file in files:
        info(str(file))
        debug(file.read_text())
