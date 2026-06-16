"""Tests for dedup hash computation."""


from ztb.utils.hash import compute_dedup_hash


class TestDedupHash:
    def test_same_input_same_hash(self):
        h1 = compute_dedup_hash("智慧校园项目", "教育局", "100万", "2024-01-01")
        h2 = compute_dedup_hash("智慧校园项目", "教育局", "100万", "2024-01-01")
        assert h1 == h2

    def test_different_input_different_hash(self):
        h1 = compute_dedup_hash("智慧校园项目", "教育局", "100万", "2024-01-01")
        h2 = compute_dedup_hash("网络升级项目", "教育局", "100万", "2024-01-01")
        assert h1 != h2

    def test_whitespace_normalized(self):
        h1 = compute_dedup_hash("智慧校园 项目", "教育局", "100万", "2024-01-01")
        h2 = compute_dedup_hash("智慧校园项目", "教育局", "100万", "2024-01-01")
        assert h1 == h2

    def test_punctuation_normalized(self):
        h1 = compute_dedup_hash("智慧校园（一期）项目", "教育局", "100万", "2024-01-01")
        h2 = compute_dedup_hash("智慧校园一期项目", "教育局", "100万", "2024-01-01")
        assert h1 == h2

    def test_none_fields_handled(self):
        h = compute_dedup_hash("项目", None, None, None)
        assert isinstance(h, str) and len(h) == 64

    def test_hash_is_sha256(self):
        h = compute_dedup_hash("test", "test", "test", "test")
        assert len(h) == 64  # SHA256 hex digest length
