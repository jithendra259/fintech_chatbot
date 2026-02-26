import numpy as np
import pandas as pd
from sklearn.covariance import LedoitWolf


class ShrinkageAgent:
    @staticmethod
    def james_stein(mu: pd.Series, n_obs: int):
        mu_grand = mu.mean()
        diff = mu - mu_grand
        norm_sq = float((diff**2).sum())

        if norm_sq == 0:
            return mu, 0.0

        sf = max(0.0, 1.0 - (len(mu) - 2) / (n_obs * norm_sq))
        sf = float(np.clip(sf, 0.0, 1.0))

        shrunk_mu = mu_grand + sf * diff
        shrunk_mu = pd.Series(shrunk_mu, index=mu.index)
        return shrunk_mu, float(sf)

    @staticmethod
    def ledoit_wolf(train_returns: pd.DataFrame):
        lw = LedoitWolf()
        lw.fit(train_returns.values)

        sigma_shrunk = pd.DataFrame(
            lw.covariance_,
            index=train_returns.columns,
            columns=train_returns.columns,
        )
        return sigma_shrunk, float(lw.shrinkage_)

    @staticmethod
    def run(aligned_data: dict):
        try:
            train_returns = aligned_data["train_returns"]
            mu_raw = aligned_data["mean_returns"]
            sigma_raw = aligned_data["covariance"]

            mu_shrunk, shrinkage_coef = ShrinkageAgent.james_stein(
                mu_raw, len(train_returns)
            )
            sigma_shrunk, lw_alpha = ShrinkageAgent.ledoit_wolf(train_returns)

            return {
                "mu_shrunk": mu_shrunk,
                "sigma_shrunk": sigma_shrunk,
                "mu_raw": mu_raw,
                "sigma_raw": sigma_raw,
                "shrinkage_coef": round(shrinkage_coef, 6),
                "lw_alpha": round(lw_alpha, 6),
                "n_assets": len(mu_raw),
                "n_obs": len(train_returns),
            }
        except Exception as error:
            raise ValueError(f"ShrinkageAgent failed: {str(error)}") from error
