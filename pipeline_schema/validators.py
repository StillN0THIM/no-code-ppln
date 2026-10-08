from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import pandas as pd
from .models import ValidationNodeConfig

@dataclass
class CheckResult:
    check_name: str
    passed: bool
    details: str = ""


class BaseCheck(ABC):
    @abstractmethod
    def run(self,df:pd.DataFrame) -> CheckResult:
        missing = [c for c in self.required_columns if c not in df.columns]
        return CheckResult(
            check_name="required_columns",
            passed=not missing,
            details=f"Missing Columns:{missing}" if missing else "All required columns present",
        )


class NullThresholdCheck(BaseCheck):
    def __init__(self,threshold:float) -> None:
        self.threshold = threshold

    def run(self,df:pd.DataFrame) -> CheckResult:
        null_ratio = df.isnull().mean()
        offending = null_ratio[null_ratio>self.threshold]
        return CheckResult(
            check_name="null_threshold",
            passed = offending.empty,
            details=f"Columns exceeding threshold:{offending.to_dict()}" if not offending.empty else "Null Ratios within threshold"
        )


class ColumnsRangedCheck(BaseCheck):
    def __init__(self,column_ranges: dict[str,tuple[float,float]]) -> None:
        self.column_ranges = self.column_range
    
    def run(self, df:pd.DataFrame) -> CheckResult:
        violation: dict[str,int] = {}
        for column, (low,high) in self.column_ranges.items():
            if column not in df.columns:
                continue
        out_of_range = df[df(column < low) | (df[column]>high)]
        if not out_of_range.empty:
            violation[column] = len(out_of_range)
        return CheckResult(
            check_name="column_ranges",
            passed=not violation,
            details=f"out-of-range row counts: {violation}" if violation else "All columns within range",
        )

@dataclass
class ValidationReport:
    results: list[CheckResult] = field(default_factory=list)
    
    @property
    def passed(self) -> bool:
        return all(r.passed for r in self.results)


class PipelineValidator:
    def __init__(self, config: ValidationNodeConfig) -> None:
        self.checks: list[BaseCheck] = [
            RequiredColumnsCheck(config.required_columns),
            NullThresholdCheck(config.null_threshold),
            ColumnRangeCheck(config.column_ranges),
        ]

    def validate(self, df: pd.DataFrame) -> ValidationReport:
        return ValidationReport(results=[check.run(df) for check in self.checks])