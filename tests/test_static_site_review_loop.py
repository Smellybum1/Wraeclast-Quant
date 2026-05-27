from wraeclast_quant.reports.static_site import (
    render_static_site,
)

from static_site_helpers import payload as _payload


def test_static_site_renders_mvp_readiness() -> None:
    html = render_static_site(_payload())

    assert "MVP Readiness" in html
    assert "<th>Local loop</th><td>No-OAuth local decision-support ready</td>" in html
    assert "<th>Latest run</th><td>7</td>" in html
    assert "<th>Review state</th><td>1/2 reviewed</td>" in html
    assert "wq review-queue --run-id 7" in html
    assert "data/processed/review_queue.md" in html
    assert "wq record-outcome --run-id 7" in html


def test_static_site_renders_outcome_summary() -> None:
    html = render_static_site(_payload())

    assert "Recommendation Outcome Summary" in html
    assert "<th>positive</th><td>2</td>" in html
    assert "<th>neutral</th><td>1</td>" in html
    assert "<th>negative</th><td>0</td>" in html


def test_static_site_renders_review_coverage() -> None:
    html = render_static_site(_payload())

    assert "Recommendation Review Coverage" in html
    assert "<th>Run</th><td>7</td>" in html
    assert "<th>Total recommendations</th><td>2</td>" in html
    assert "<th>Reviewed</th><td>1</td>" in html
    assert "<th>Unreviewed</th><td>1</td>" in html
    assert "<th>Reviewed %</th><td>50.0%</td>" in html
    assert "<th>Next review action</th>" in html
    assert "wq review-queue --run-id 7" in html
    assert "wq record-outcome --run-id 7" in html
