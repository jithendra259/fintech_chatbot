import numpy as np
import pandas as pd

from config.config import config


class InstabilityAgent:
    @staticmethod
    def compute_baseline(train_returns: pd.DataFrame) -> dict:
        window = config.inst_window
        dates = []
        vol_values = []
        corr_values = []
        drift_values = []
        prev_cov = None

        for end_idx in range(window, len(train_returns) + 1):
            current_window = train_returns.iloc[end_idx - window : end_idx]
            current_date = current_window.index[-1]

            vol = float(current_window.std().mean())
            corr_matrix = current_window.corr().values
            upper_idx = np.triu_indices_from(corr_matrix, k=1)
            corr = float(corr_matrix[upper_idx].mean())
            current_cov = current_window.cov().values

            drift = np.nan
            if prev_cov is not None:
                drift = float(np.linalg.norm(current_cov - prev_cov, ord="fro"))

            dates.append(current_date)
            vol_values.append(vol)
            corr_values.append(corr)
            drift_values.append(drift)
            prev_cov = current_cov

        vol_series = pd.Series(vol_values, index=dates, name="vol")
        corr_series = pd.Series(corr_values, index=dates, name="corr")
        drift_series = pd.Series(drift_values, index=dates, name="drift")

        aligned = pd.concat([vol_series, corr_series, drift_series], axis=1).dropna()

        return {
            "vol_mean": float(aligned["vol"].mean()),
            "vol_std": float(aligned["vol"].std()),
            "corr_mean": float(aligned["corr"].mean()),
            "corr_std": float(aligned["corr"].std()),
            "drift_mean": float(aligned["drift"].mean()),
            "drift_std": float(aligned["drift"].std()),
            "n_windows": int(len(aligned)),
        }

    @staticmethod
    def compute_current(full_returns: pd.DataFrame, baseline: dict) -> dict:
        window = config.inst_window
        current_window = full_returns.iloc[-window:]
        previous_window = full_returns.iloc[-(2 * window) : -window]

        vol_raw = float(current_window.std().mean())

        corr_matrix = current_window.corr().values
        upper_idx = np.triu_indices_from(corr_matrix, k=1)
        corr_raw = float(corr_matrix[upper_idx].mean())

        cov_current = current_window.cov().values
        cov_previous = previous_window.cov().values
        drift_raw = float(np.linalg.norm(cov_current - cov_previous, ord="fro"))

        vol_z = (vol_raw - baseline["vol_mean"]) / baseline["vol_std"]
        corr_z = (corr_raw - baseline["corr_mean"]) / baseline["corr_std"]
        drift_z = (drift_raw - baseline["drift_mean"]) / baseline["drift_std"]

        instability = (vol_z + corr_z + drift_z) / 3.0

        if instability < 0:
            signal = "CALM"
        elif instability < 0.5:
            signal = "NORMAL"
        elif instability < 1.0:
            signal = "ELEVATED"
        elif instability < 2.0:
            signal = "HIGH"
        else:
            signal = "EXTREME"

        return {
            "instability": round(instability, 4),
            "signal": signal,
            "vol_raw": round(vol_raw, 6),
            "corr_raw": round(corr_raw, 6),
            "drift_raw": round(drift_raw, 6),
            "vol_z": round(vol_z, 4),
            "corr_z": round(corr_z, 4),
            "drift_z": round(drift_z, 4),
            "above_threshold": bool(instability > config.theta_H),
            "theta_H": config.theta_H,
            "window_days": config.inst_window,
        }

    @staticmethod
    def run(aligned_data: dict) -> dict:
        try:
            train_returns = aligned_data["train_returns"]
            full_returns = aligned_data["full_returns"]

            min_days = config.inst_window * 2 + 1
            if len(full_returns) < min_days:
                raise ValueError(
                    "Insufficient data for instability computation.\n"
                    f"Need at least {config.inst_window * 2 + 1} days."
                )

            baseline = InstabilityAgent.compute_baseline(train_returns)
            current = InstabilityAgent.compute_current(full_returns, baseline)

            return {
                **current,
                "baseline_vol_mean": baseline["vol_mean"],
                "baseline_vol_std": baseline["vol_std"],
                "baseline_corr_mean": baseline["corr_mean"],
                "baseline_corr_std": baseline["corr_std"],
                "baseline_drift_mean": baseline["drift_mean"],
                "baseline_drift_std": baseline["drift_std"],
                "n_baseline_windows": baseline["n_windows"],
            }
        except Exception as error:
            raise ValueError(f"InstabilityAgent failed: {str(error)}") from error
