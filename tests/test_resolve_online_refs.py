from __future__ import annotations

from scripts.resolve_and_archive_online_refs import slugify_filename


def test_slugify_filename_removes_invalid_chars() -> None:
    value = slugify_filename('江苏省/生态产品:价值实现?*平台')
    assert '/' not in value
    assert ':' not in value
    assert '?' not in value
    assert '*' not in value
    assert value
