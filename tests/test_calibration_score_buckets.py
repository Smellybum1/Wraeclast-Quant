from wraeclast_quant.reports.calibration import score_bucket


def test_calibration_score_bucket_boundaries() -> None:
    assert score_bucket(75.0) == "75+"
    assert score_bucket(55.0) == "55-74.99"
    assert score_bucket(35.0) == "35-54.99"
    assert score_bucket(34.99) == "<35"
