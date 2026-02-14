from pydantic import BaseModel
from typing import Dict


class FlowFeatures(BaseModel):
    src_mac: str

    ack_flag_number: float
    https: float
    rate: float
    header_length: float
    variance: float
    max: float
    tot_sum: float
    time_to_live: float
    std: float
    psh_flag_number: float
    min: float
    dns: float


class SourceMacAnalysis(BaseModel):
    src_mac: str
    flow_count: int
    max_probability: float
    alert_flows: int
    status: str


class AnalysisSummary(BaseModel):
    total_flows: int
    total_sources: int
    anomalous_sources: int
    suspicious_sources: int


class WindowAnalysisResponse(BaseModel):
    sources: Dict[str, SourceMacAnalysis]
    summary: AnalysisSummary