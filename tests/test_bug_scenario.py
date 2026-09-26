import pytest

from relaygrid.metering.ami import last_gasp_clusters
from relaygrid.metering.restoration import MeterObservation, verify_sections


def test_ami_windows_deduplicate_meters_and_include_silent_sections():
    clusters = last_gasp_clusters(
        [("M1", 0.0, "F1"), ("M2", 20.0, "F1"), ("M3", 40.0, "F1")],
        window_s=30.0,
    )
    assert [len(cluster) for cluster in clusters] == [2, 1]

    observations = [
        MeterObservation("M1", "S1", 10.0, 120.0, True),
        MeterObservation("M1", "S1", 11.0, 121.0, True),
        MeterObservation("M2", "S1", 12.0, None, False),
    ]
    result = {item.section_id: item for item in verify_sections(observations, {"S1", "S2"})}
    assert result["S1"].sample_count == 2
    assert result["S1"].energized_ratio == pytest.approx(0.5)
    assert result["S1"].state == "partial"
    assert result["S2"].state == "contradictory"
    assert result["S2"].sample_count == 0
