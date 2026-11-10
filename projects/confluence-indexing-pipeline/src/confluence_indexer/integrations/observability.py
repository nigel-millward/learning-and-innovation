"""CloudWatch metrics and SNS alerts."""

from __future__ import annotations

import json
import logging
from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any

log = logging.getLogger(__name__)

_PUT_METRIC_BATCH = 500
_SNS_SUBJECT_MAX = 100


class MetricsPublisher:
    """Publishes run metrics with ``Pipeline`` and ``Environment`` dimensions."""

    def __init__(
        self, cloudwatch_client: Any, namespace: str, pipeline: str, environment: str
    ) -> None:
        self._cw = cloudwatch_client
        self._namespace = namespace
        self._dimensions = [
            {"Name": "Pipeline", "Value": pipeline},
            {"Name": "Environment", "Value": environment},
        ]

    def publish(self, counts: Mapping[str, float], seconds: Mapping[str, float]) -> None:
        now = datetime.now(UTC)
        data = [
            {
                "MetricName": name,
                "Dimensions": self._dimensions,
                "Timestamp": now,
                "Value": float(value),
                "Unit": unit,
            }
            for metrics, unit in ((counts, "Count"), (seconds, "Seconds"))
            for name, value in metrics.items()
        ]
        for start in range(0, len(data), _PUT_METRIC_BATCH):
            self._cw.put_metric_data(
                Namespace=self._namespace, MetricData=data[start : start + _PUT_METRIC_BATCH]
            )
        log.info("Published %d metrics to %s", len(data), self._namespace)


class Alerter:
    def __init__(
        self, sns_client: Any, topic_arn: str | None, pipeline: str, environment: str
    ) -> None:
        self._sns = sns_client
        self._topic_arn = topic_arn
        self._pipeline = pipeline
        self._environment = environment

    def send(self, severity: str, summary: str, details: Mapping[str, Any]) -> None:
        """Publish to SNS. Never raises: alerting must not mask the original failure."""
        if not self._topic_arn:
            log.warning("No ALERT_TOPIC_ARN configured; alert not sent: %s", summary)
            return
        subject = f"[{severity}] {self._pipeline} ({self._environment}): {summary}"
        # SNS subjects: max 100 chars, ASCII, no line breaks.
        subject = subject.encode("ascii", "replace").decode().replace("\n", " ")
        message = {
            "severity": severity,
            "pipeline": self._pipeline,
            "environment": self._environment,
            "summary": summary,
            "timestamp": datetime.now(UTC).isoformat(),
            **details,
        }
        try:
            self._sns.publish(
                TopicArn=self._topic_arn,
                Subject=subject[:_SNS_SUBJECT_MAX],
                Message=json.dumps(message, indent=2, default=str),
                MessageAttributes={
                    "severity": {"DataType": "String", "StringValue": severity},
                    "pipeline": {"DataType": "String", "StringValue": self._pipeline},
                },
            )
        except Exception:
            log.exception("Failed to publish SNS alert: %s", summary)
