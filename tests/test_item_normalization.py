from wraeclast_quant.normalizers.items import normalize_item_key, normalize_item_name


def test_item_normalization() -> None:
    assert normalize_item_name("  stormglass   catalyst ") == "Stormglass Catalyst"
    assert normalize_item_key("Gemcutter's Prism Shard") == "gemcutters-prism-shard"

