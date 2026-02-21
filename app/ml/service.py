import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple
from fastapi import HTTPException, status
from app.ml.model_loader import get_model_objects
from app.ml.schemas import WindowAnalysisResponse, SourceMacAnalysis, AnalysisSummary, FlowFeatures

ALERT_THRESHOLD = 0.61
SUSPICION_THRESHOLD = 0.40
SINGLE_PACKET_THRESHOLD = 0.90
MIN_ALERT_FLOWS = 2
MIN_SUSPICIOUS_COUNT = 3

_model_objects = None
_user_results: Dict[int, WindowAnalysisResponse] = {}


def _get_model_objects() -> Tuple[Any, Any, List[str], Dict[str, float]]:
    global _model_objects
    if _model_objects is None:
        _model_objects = get_model_objects()
    return _model_objects

def _preprocess_flows(df: pd.DataFrame, features: List[str], medians: Dict[str, float]) -> pd.DataFrame:
    df = df.copy()
    df.replace([np.inf, -np.inf], np.nan, inplace=True)

    missing_features = set(features) - set(df.columns)
    if missing_features:
        for feat in missing_features:
            df[feat] = np.nan

    for col in features:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        df[col] = df[col].fillna(medians[col])

    return df[features].astype(float)


def analyze_window(flows: List[FlowFeatures], user_id: int) -> tuple[WindowAnalysisResponse, List[dict]]:
    total_flows = len(flows)
    suspicious_packets: List[dict] = []

    if not flows:
        result = WindowAnalysisResponse(
            sources={},
            summary=AnalysisSummary(
                total_flows=0,
                total_sources=0,
                anomalous_sources=0,
                suspicious_sources=0
            )
        )
        _user_results[user_id] = result
        return result, suspicious_packets

    try:
        model, scaler, features, medians = _get_model_objects()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Model loading failed: {str(e)}"
        )

    flows_dict = [flow.model_dump() for flow in flows]
    df_flows = pd.DataFrame(flows_dict)

    try:
        X = _preprocess_flows(df_flows, features, medians)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Preprocessing failed: {str(e)}"
        )
    
    if X.empty:
        result = WindowAnalysisResponse(
            sources={},
            summary=AnalysisSummary(
                total_flows=total_flows,
                total_sources=0,
                anomalous_sources=0,
                suspicious_sources=0
            )
        )
        _user_results[user_id] = result
        return result, suspicious_packets

    try:
        X_scaled = scaler.transform(X)
        probabilities = model.predict_proba(X_scaled)[:, 1]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Model prediction failed: {str(e)}"
        )

    df_flows["probability"] = probabilities

    sources, anomalous_count, suspicious_count, packets = _analyze_sources_by_ip(df_flows)

    suspicious_packets.extend(packets)

    result = WindowAnalysisResponse(
        sources=sources,
        summary=AnalysisSummary(
            total_flows=total_flows,
            total_sources=len(sources),
            anomalous_sources=anomalous_count,
            suspicious_sources=suspicious_count
        )
    )

    _user_results[user_id] = result
    return result, suspicious_packets


def _analyze_sources_by_ip(df_flows: pd.DataFrame) -> Tuple[Dict[str, SourceMacAnalysis], int, int, List[dict]]:
    sources = {}
    anomalous_count = 0
    suspicious_count = 0
    suspicious_packets: List[dict] = []

    for src_ip, group in df_flows.groupby("src_ip"):
        group_probs = group["probability"].values

        src_mac = group["src_mac"].iloc[0]
        dst_mac = group["dst_mac"].iloc[0]

        print(f"IP: {src_ip} (MAC: {src_mac} -> {dst_mac}), probabilities: {group_probs}")

        flow_count = len(group_probs)
        max_probability = float(group_probs.max())
        alert_flows = int((group_probs >= ALERT_THRESHOLD).sum())
        suspicious_flows = int(((group_probs >= SUSPICION_THRESHOLD) & (group_probs < ALERT_THRESHOLD)).sum())

        if max_probability >= SINGLE_PACKET_THRESHOLD or alert_flows >= MIN_ALERT_FLOWS:
            status_value = "anomaly"
            anomalous_count += 1
        elif suspicious_flows >= MIN_SUSPICIOUS_COUNT:
            status_value = "suspicious"
            suspicious_count += 1

            suspicious_packets.extend(group.to_dict("records"))
        else:
            status_value = "normal"

        sources[str(src_ip)] = SourceMacAnalysis(
            src_ip=str(src_ip),
            src_mac=str(src_mac),
            dst_mac=str(dst_mac),
            flow_count=flow_count,
            max_probability=max_probability,
            alert_flows=alert_flows,
            status=status_value
        )

    return sources, anomalous_count, suspicious_count, suspicious_packets

def get_user_analysis_result(user_id: int) -> WindowAnalysisResponse:
    if user_id not in _user_results:
        return WindowAnalysisResponse(
            sources={},
            summary=AnalysisSummary(
                total_flows=0,
                total_sources=0,
                anomalous_sources=0,
                suspicious_sources=0
            )
        )
    return _user_results[user_id]