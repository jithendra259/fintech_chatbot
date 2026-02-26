import cvxpy as cp
import numpy as np
import pandas as pd

from config.config import config


class OptimizationAgent:
    @staticmethod
    def equal_weight(assets: list) -> dict:
        return {asset: 1 / len(assets) for asset in assets}

    @staticmethod
    def mv_optimize(mu: pd.Series, sigma: pd.DataFrame, lam: float):
        n = len(mu)
        w = cp.Variable(n)

        objective = cp.Maximize(mu.values @ w - (lam / 2) * cp.quad_form(w, sigma.values))
        constraints = [cp.sum(w) == 1, w >= 0]
        problem = cp.Problem(objective, constraints)

        try:
            problem.solve(solver=cp.SCS)
        except Exception:
            pass

        if problem.status != cp.OPTIMAL:
            try:
                problem.solve(solver=cp.OSQP)
            except Exception:
                pass

        if problem.status != cp.OPTIMAL:
            return None

        weights = np.clip(np.array(w.value).flatten(), 0, None)
        total_weight = weights.sum()
        if total_weight <= 0:
            return None

        weights = weights / total_weight
        return pd.Series(weights, index=mu.index)

    @staticmethod
    def run(shrinkage_data: dict, regime_data: dict):
        assets = []
        mu = pd.Series(dtype=float)
        sigma = pd.DataFrame()
        lam = config.risk_aversion

        try:
            mu = shrinkage_data["mu_shrunk"]
            sigma = shrinkage_data["sigma_shrunk"]
            assets = mu.index.tolist()
            regime = regime_data["regime"]
            lam = config.risk_aversion

            if regime == "equal_weight":
                weights_dict = OptimizationAgent.equal_weight(assets)
                status = "equal_weight_governance"
            else:
                result = OptimizationAgent.mv_optimize(mu, sigma, lam)
                if result is not None:
                    weights_dict = result.to_dict()
                    status = "optimal"
                else:
                    weights_dict = OptimizationAgent.equal_weight(assets)
                    status = "fallback_equal_weight"

            w_array = np.array([weights_dict[a] for a in assets])
            mu_array = mu.values
            sig_array = sigma.values
            expected_return = float(mu_array @ w_array)
            portfolio_risk = float(w_array.T @ sig_array @ w_array)
            hhi = float((w_array**2).sum())
            effective_n = round(1 / hhi, 2) if hhi > 0 else len(assets)

            return {
                "weights": weights_dict,
                "regime_applied": regime,
                "optimizer_status": status,
                "expected_return": round(expected_return, 6),
                "portfolio_risk": round(portfolio_risk, 6),
                "hhi": round(hhi, 6),
                "effective_n": effective_n,
                "lambda_used": lam,
                "n_assets": len(assets),
            }
        except Exception:
            weights_dict = OptimizationAgent.equal_weight(assets)
            w_array = np.array([weights_dict[a] for a in assets]) if assets else np.array([])
            mu_array = mu.values if len(mu) else np.array([])
            sig_array = sigma.values if not sigma.empty else np.array([[]])
            expected_return = float(mu_array @ w_array) if len(assets) else 0.0
            portfolio_risk = float(w_array.T @ sig_array @ w_array) if len(assets) else 0.0
            hhi = float((w_array**2).sum()) if len(assets) else 0.0
            effective_n = round(1 / hhi, 2) if hhi > 0 else len(assets)

            return {
                "weights": weights_dict,
                "regime_applied": regime_data.get("regime", "shrunk_mv"),
                "optimizer_status": "error_fallback_equal_weight",
                "expected_return": round(expected_return, 6),
                "portfolio_risk": round(portfolio_risk, 6),
                "hhi": round(hhi, 6),
                "effective_n": effective_n,
                "lambda_used": lam,
                "n_assets": len(assets),
            }
