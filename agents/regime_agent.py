from config.config import config


class RegimeAgent:
    @staticmethod
    def run(instability_data: dict) -> dict:
        try:
            I_t = instability_data["instability"]
            theta_H = instability_data["theta_H"]
            signal = instability_data["signal"]

            activated_ew = bool(I_t > theta_H)
            if activated_ew:
                regime = "equal_weight"
            else:
                regime = "shrunk_mv"

            margin = round(I_t - theta_H, 4)

            if activated_ew:
                reason = (
                    f"Instability I_t={I_t:.4f} exceeds threshold "
                    f"theta_H={theta_H}. Market stress is {signal}. "
                    f"Equal Weight activated — shrinkage estimates "
                    f"unreliable under current conditions. "
                    f"Capital protection prioritised over optimisation."
                )
            else:
                reason = (
                    f"Instability I_t={I_t:.4f} is below threshold "
                    f"theta_H={theta_H}. Market stress is {signal}. "
                    f"ShrunkMV active — shrinkage estimation reliable "
                    f"under current conditions. "
                    f"Risk-adjusted optimisation applied."
                )

            governance_note = (
                f"Regime Operator R(I_t): "
                f"Equal Weight if I_t > {theta_H} "
                f"else ShrunkMV. "
                f"Current margin from threshold: {margin}. "
                f"This implements Definition 2 of the "
                f"Supervisory Portfolio Governance Framework."
            )

            return {
                "regime": regime,
                "activated_ew": activated_ew,
                "instability": I_t,
                "theta_H": theta_H,
                "margin": margin,
                "signal": signal,
                "reason": reason,
                "governance_note": governance_note,
            }
        except Exception as error:
            raise ValueError(f"RegimeAgent failed: {str(error)}") from error
