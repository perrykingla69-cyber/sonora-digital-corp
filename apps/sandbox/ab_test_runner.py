"""
A/B Test Runner — scipy stats for content testing at ABE Music
"""
import json
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from scipy import stats
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class ABTestResult:
    test_name: str
    variant_a: str
    variant_b: str
    n_a: int
    n_b: int
    mean_a: float
    mean_b: float
    lift_pct: float
    p_value: float
    confidence_interval: Tuple[float, float]
    significant: bool
    winner: Optional[str]
    recommendation: str


class ABTestRunner:

    def __init__(self, confidence_level: float = 0.95):
        self.alpha = 1 - confidence_level

    def run_test(
        self,
        test_name: str,
        variant_a_name: str,
        variant_b_name: str,
        data_a: List[float],
        data_b: List[float],
    ) -> ABTestResult:
        n_a, n_b = len(data_a), len(data_b)
        mean_a, mean_b = np.mean(data_a), np.mean(data_b)
        lift_pct = ((mean_b - mean_a) / max(abs(mean_a), 1e-9)) * 100

        t_stat, p_value = stats.ttest_ind(data_a, data_b, equal_var=False)
        significant = p_value < self.alpha

        diff = mean_b - mean_a
        se = np.sqrt(np.var(data_a) / n_a + np.var(data_b) / n_b)
        t_crit = stats.t.ppf(1 - self.alpha / 2, df=n_a + n_b - 2)
        ci = (diff - t_crit * se, diff + t_crit * se)

        if significant:
            winner = variant_b_name if mean_b > mean_a else variant_a_name
            rec = f"Implementar {winner} — lift {abs(lift_pct):.1f}% con {int((1-p_value)*100)}% confianza"
        else:
            winner = None
            rec = f"Sin diferencia significativa (p={p_value:.3f}) — continuar recolectando datos"

        return ABTestResult(
            test_name=test_name,
            variant_a=variant_a_name,
            variant_b=variant_b_name,
            n_a=n_a,
            n_b=n_b,
            mean_a=round(float(mean_a), 4),
            mean_b=round(float(mean_b), 4),
            lift_pct=round(float(lift_pct), 2),
            p_value=round(float(p_value), 4),
            confidence_interval=(round(float(ci[0]), 4), round(float(ci[1]), 4)),
            significant=significant,
            winner=winner,
            recommendation=rec,
        )

    def run_batch(self, tests: List[Dict]) -> List[Dict]:
        results = []
        for t in tests:
            r = self.run_test(
                test_name=t["name"],
                variant_a_name=t["variant_a"],
                variant_b_name=t["variant_b"],
                data_a=t["data_a"],
                data_b=t["data_b"],
            )
            results.append(asdict(r))
        return results


if __name__ == "__main__":
    runner = ABTestRunner()
    result = runner.run_test(
        "thumbnail_test",
        "foto_artista",
        "letra_cancion",
        data_a=[0.032, 0.028, 0.035, 0.031, 0.029] * 20,
        data_b=[0.041, 0.044, 0.038, 0.042, 0.040] * 20,
    )
    print(json.dumps(asdict(result), indent=2))
