import numpy as np
import pandas as pd


class PerformanceEvaluator:
    """
    Evaluates portfolio performance metrics.
    Includes benchmark comparison with equal-weight portfolio.
    """

    # ---------------------------------------------------
    # Core Portfolio Calculations
    # ---------------------------------------------------

    @staticmethod
    def compute_portfolio_returns(returns: pd.DataFrame, weights: dict) -> pd.Series:
        """
        Compute daily portfolio returns given asset returns and weights.
        """
        weight_vector = np.array([weights[col] for col in returns.columns])
        portfolio_returns = returns.values @ weight_vector
        return pd.Series(portfolio_returns, index=returns.index)

    @staticmethod
    def cumulative_return(portfolio_returns: pd.Series) -> pd.Series:
        """
        Compute cumulative returns.
        """
        return (1 + portfolio_returns).cumprod()

    # ---------------------------------------------------
    # Annualized Metrics
    # ---------------------------------------------------

    @staticmethod
    def annualized_return(portfolio_returns: pd.Series, trading_days: int = 252) -> float:
        mean_daily = portfolio_returns.mean()
        return mean_daily * trading_days

    @staticmethod
    def annualized_volatility(portfolio_returns: pd.Series, trading_days: int = 252) -> float:
        daily_vol = portfolio_returns.std()
        return daily_vol * np.sqrt(trading_days)

    @staticmethod
    def sharpe_ratio(portfolio_returns: pd.Series, risk_free_rate: float = 0.0) -> float:
        ann_return = PerformanceEvaluator.annualized_return(portfolio_returns)
        ann_vol = PerformanceEvaluator.annualized_volatility(portfolio_returns)

        if ann_vol == 0:
            return 0.0

        return (ann_return - risk_free_rate) / ann_vol

    @staticmethod
    def max_drawdown(cumulative_returns: pd.Series) -> float:
        rolling_max = cumulative_returns.cummax()
        drawdown = cumulative_returns / rolling_max - 1
        return drawdown.min()

    @staticmethod
    def equal_weight_portfolio(returns: pd.DataFrame) -> dict:
        """
        Generate equal-weight portfolio weights.
        """
        n = returns.shape[1]
        return {col: 1 / n for col in returns.columns}

    # ---------------------------------------------------
    # Additional Metrics
    # ---------------------------------------------------

    @staticmethod
    def calmar_ratio(portfolio_returns: pd.Series) -> float:
        ann_return = PerformanceEvaluator.annualized_return(portfolio_returns)
        cumulative = PerformanceEvaluator.cumulative_return(portfolio_returns)
        max_dd = PerformanceEvaluator.max_drawdown(cumulative)
        if max_dd == 0:
            return 0.0
        return float(ann_return / abs(max_dd))

    @staticmethod
    def compute_hhi(weights: dict) -> float:
        w = np.array(list(weights.values()), dtype=float)
        return float((w**2).sum())

    @staticmethod
    def compute_effective_n(hhi: float) -> float:
        if hhi == 0:
            return 0.0
        return round(1 / hhi, 2)

    @staticmethod
    def governance_stability(current_weights: dict, previous_weights: dict | None):
        if previous_weights is None:
            return None

        keys = sorted(set(current_weights.keys()) | set(previous_weights.keys()))
        diffs = [
            abs(float(current_weights.get(k, 0.0)) - float(previous_weights.get(k, 0.0)))
            for k in keys
        ]
        return round(float(np.sum(diffs)), 6)

    # ---------------------------------------------------
    # Full Evaluation
    # ---------------------------------------------------

    @staticmethod
    def evaluate(
        returns: pd.DataFrame,
        weights: dict,
        previous_weights: dict | None = None,
    ) -> dict:
        portfolio_returns = PerformanceEvaluator.compute_portfolio_returns(returns, weights)
        cumulative = PerformanceEvaluator.cumulative_return(portfolio_returns)

        ann_ret = PerformanceEvaluator.annualized_return(portfolio_returns)
        ann_vol = PerformanceEvaluator.annualized_volatility(portfolio_returns)
        sharpe = PerformanceEvaluator.sharpe_ratio(portfolio_returns)
        max_dd = PerformanceEvaluator.max_drawdown(cumulative)
        calmar = PerformanceEvaluator.calmar_ratio(portfolio_returns)
        hhi = PerformanceEvaluator.compute_hhi(weights)
        eff_n = PerformanceEvaluator.compute_effective_n(hhi)
        gs = PerformanceEvaluator.governance_stability(weights, previous_weights)

        return {
            "annualized_return": round(ann_ret, 4),
            "annualized_volatility": round(ann_vol, 4),
            "sharpe_ratio": round(sharpe, 4),
            "max_drawdown": round(max_dd, 4),
            "calmar_ratio": round(calmar, 4),
            "hhi": round(hhi, 6),
            "effective_n": eff_n,
            "governance_stability": gs,
            "cumulative_returns": cumulative,
        }

    # ---------------------------------------------------
    # Equal-Weight Benchmark
    # ---------------------------------------------------

    @staticmethod
    def evaluate_with_benchmark(
        returns: pd.DataFrame,
        opt_weights: dict,
        previous_weights: dict | None = None,
    ) -> dict:
        optimized = PerformanceEvaluator.evaluate(returns, opt_weights, previous_weights)
        eq_weights = PerformanceEvaluator.equal_weight_portfolio(returns)
        equal_weight = PerformanceEvaluator.evaluate(returns, eq_weights, None)

        return {
            "optimized": optimized,
            "equal_weight": equal_weight,
        }
