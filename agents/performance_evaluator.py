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

    # ---------------------------------------------------
    # Full Evaluation
    # ---------------------------------------------------

    @staticmethod
    def evaluate(returns: pd.DataFrame, weights: dict) -> dict:
        """
        Evaluate a single portfolio.
        """
        portfolio_returns = PerformanceEvaluator.compute_portfolio_returns(
            returns, weights
        )

        cumulative = PerformanceEvaluator.cumulative_return(portfolio_returns)

        return {
            "annualized_return": PerformanceEvaluator.annualized_return(portfolio_returns),
            "annualized_volatility": PerformanceEvaluator.annualized_volatility(portfolio_returns),
            "sharpe_ratio": PerformanceEvaluator.sharpe_ratio(portfolio_returns),
            "max_drawdown": PerformanceEvaluator.max_drawdown(cumulative),
            "cumulative_returns": cumulative
        }

    # ---------------------------------------------------
    # Equal-Weight Benchmark
    # ---------------------------------------------------

    @staticmethod
    def equal_weight_portfolio(returns: pd.DataFrame) -> dict:
        """
        Generate equal-weight portfolio weights.
        """
        n = returns.shape[1]
        return {col: 1 / n for col in returns.columns}

    @staticmethod
    def evaluate_with_benchmark(returns: pd.DataFrame, opt_weights: dict) -> dict:
        """
        Evaluate optimized portfolio and equal-weight benchmark.
        """

        # Optimized portfolio
        optimized_metrics = PerformanceEvaluator.evaluate(returns, opt_weights)

        # Equal-weight benchmark
        eq_weights = PerformanceEvaluator.equal_weight_portfolio(returns)
        equal_weight_metrics = PerformanceEvaluator.evaluate(returns, eq_weights)

        return {
            "optimized": optimized_metrics,
            "equal_weight": equal_weight_metrics
        }
