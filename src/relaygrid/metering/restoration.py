from __future__ import annotations
from dataclasses import dataclass
from collections import defaultdict

@dataclass(frozen=True)
class MeterObservation:
    meter_id: str
    section_id: str
    timestamp_s: float
    voltage_v: float|None
    ping_ok: bool

@dataclass(frozen=True)
class SectionVerification:
    section_id: str
    state: str
    sample_count: int
    energized_ratio: float


def verify_sections(observations:list[MeterObservation],expected_energized:set[str],voltage_threshold:float=90.0):
    latest_by_meter: dict[tuple[str,str],MeterObservation]={}
    for observation in observations:
        key=(observation.section_id,observation.meter_id)
        current=latest_by_meter.get(key)
        if current is None or observation.timestamp_s>current.timestamp_s:
            latest_by_meter[key]=observation

    by=defaultdict(list)
    for observation in latest_by_meter.values():
        by[observation.section_id].append(observation)

    out=[]
    for section in sorted(by.keys() | expected_energized):
        obs=by.get(section,[])
        energized=sum(1 for o in obs if o.ping_ok and o.voltage_v is not None and o.voltage_v>=voltage_threshold)
        ratio=energized/len(obs) if obs else 0.0
        expected=section in expected_energized
        if expected and ratio>=.8: state="confirmed"
        elif expected and ratio>=.2: state="partial"
        elif expected: state="contradictory"
        elif not expected and ratio>.2: state="unexpected_energized"
        else: state="confirmed_deenergized"
        out.append(SectionVerification(section,state,len(obs),ratio))
    return out


def contradictory(verifications:list[SectionVerification]):
    return [v for v in verifications if v.state in {"contradictory","unexpected_energized"}]
