import re

from config.config import config
from agents.data_agent import DataFetchAgent
from agents.data_alignment_agent import DataAlignmentAgent
from agents.shrinkage_agent import ShrinkageAgent
from agents.instability_agent import InstabilityAgent
from agents.regime_agent import RegimeAgent
from agents.optimization_agent import OptimizationAgent
from agents.performance_evaluator import PerformanceEvaluator
from agents.ai_reasoning_agent import AIReasoningAgent
from orchestrator.intent_classifier import classify_intent
from orchestrator.intent_classifier import get_context_sections
from orchestrator.intent_classifier import extract_parameters


class Orchestrator:
    def __init__(self, config=config):
        self.config = config
        self.price_data = None
        self.selected_stocks = []
        self.messages = []
        self.session_active = False
        self.session_data = {}

    def start_session(self, selected_stocks: list) -> dict:
        try:
            if not selected_stocks:
                return {"success": False, "message": "No stocks selected."}

            for stock in selected_stocks:
                if stock not in config.assets:
                    return {"success": False, "message": f"Invalid stock: {stock}"}

            price_data = DataFetchAgent.run(
                assets=selected_stocks,
                start_date=config.start_date,
                end_date=config.end_date,
                frequency=config.data_frequency,
            )

            aligned_data = DataAlignmentAgent.run(price_data)
            shrinkage_data = ShrinkageAgent.run(aligned_data)
            instability_data = InstabilityAgent.run(aligned_data)
            regime_data = RegimeAgent.run(instability_data)
            optimization_data = OptimizationAgent.run(shrinkage_data, regime_data)
            performance_data = PerformanceEvaluator.evaluate_with_benchmark(
                aligned_data["test_returns"],
                optimization_data["weights"],
                previous_weights=None,
            )

            self.session_data = {
                "aligned": aligned_data,
                "shrinkage": shrinkage_data,
                "instability": instability_data,
                "regime": regime_data,
                "optimization": optimization_data,
                "performance": performance_data,
                "selected_stocks": selected_stocks,
                "params": {
                    "lambda": config.risk_aversion,
                    "theta_H": config.theta_H,
                },
            }

            self.price_data = price_data
            self.selected_stocks = selected_stocks
            self.session_active = True

            system_msg = self._build_system_message()
            self.messages = [system_msg]

            return {
                "success": True,
                "message": (
                    f"Analysis complete for {selected_stocks}. "
                    f"Instability: {instability_data['instability']} "
                    f"({instability_data['signal']}). "
                    f"Regime: {regime_data['regime']}. "
                    f"Sharpe: {performance_data['optimized']['sharpe_ratio']}. "
                    f"Ask me anything."
                ),
            }
        except Exception as error:
            return {"success": False, "message": f"Error: {str(error)}"}

    def _build_system_message(self) -> dict:
        aligned = self.session_data["aligned"]
        instability = self.session_data["instability"]
        regime = self.session_data["regime"]
        shrinkage = self.session_data["shrinkage"]
        optimization = self.session_data["optimization"]
        performance = self.session_data["performance"]
        params = self.session_data["params"]
        selected_stocks = self.session_data["selected_stocks"]

        data_info_string = (
            f"SELECTED STOCKS: {selected_stocks}\n"
            f"TRAINING PERIOD: {aligned['train_start']} to {aligned['train_end']}\n"
            f"({aligned['n_train_days']} days)\n"
            f"TEST PERIOD: {aligned['test_start']} to {aligned['test_end']}\n"
            f"({aligned['n_test_days']} days)\n"
            f"NUMBER OF ASSETS: {aligned['n_assets']}"
        )

        instability_string = (
            "INSTABILITY INDEX:\n"
            f"I_t = {instability['instability']}\n"
            f"Signal = {instability['signal']}\n"
            f"Above Threshold = {instability['above_threshold']}\n"
            f"Threshold theta_H = {instability['theta_H']}\n"
            f"Volatility Z-score = {instability['vol_z']}\n"
            f"Correlation Z-score = {instability['corr_z']}\n"
            f"Drift Z-score = {instability['drift_z']}"
        )

        regime_string = (
            "REGIME DECISION:\n"
            f"Current Regime = {regime['regime']}\n"
            f"Equal Weight Activated = {regime['activated_ew']}\n"
            f"Margin from Threshold = {regime['margin']}\n"
            f"Reason = {regime['reason']}\n"
            f"Governance Note = {regime['governance_note']}"
        )

        shrinkage_string = (
            "SHRINKAGE APPLIED:\n"
            f"James-Stein Factor = {shrinkage['shrinkage_coef']}\n"
            f"Ledoit-Wolf Alpha = {shrinkage['lw_alpha']}\n"
            f"Number of Observations = {shrinkage['n_obs']}"
        )

        sorted_weights = sorted(
            optimization["weights"].items(),
            key=lambda item: item[1],
            reverse=True,
        )
        weights_lines = [f"{ticker}: {weight * 100:.2f}%" for ticker, weight in sorted_weights]
        weights_string = "PORTFOLIO WEIGHTS:\n" + "\n".join(weights_lines)

        optimization_string = (
            "OPTIMIZATION DETAILS:\n"
            f"Regime Applied = {optimization['regime_applied']}\n"
            f"Optimizer Status = {optimization['optimizer_status']}\n"
            f"Expected Return = {optimization['expected_return']}\n"
            f"Portfolio Risk = {optimization['portfolio_risk']}\n"
            f"HHI = {optimization['hhi']}\n"
            f"Effective N = {optimization['effective_n']}\n"
            f"Lambda Used = {optimization['lambda_used']}"
        )

        optimized_perf = performance["optimized"]
        performance_string = (
            "OPTIMIZED PORTFOLIO PERFORMANCE (test period):\n"
            f"Annualized Return = {optimized_perf['annualized_return']}\n"
            f"Annualized Volatility = {optimized_perf['annualized_volatility']}\n"
            f"Sharpe Ratio = {optimized_perf['sharpe_ratio']}\n"
            f"Max Drawdown = {optimized_perf['max_drawdown']}\n"
            f"Calmar Ratio = {optimized_perf['calmar_ratio']}\n"
            f"HHI = {optimized_perf['hhi']}\n"
            f"Effective N = {optimized_perf['effective_n']}"
        )

        benchmark_perf = performance["equal_weight"]
        benchmark_string = (
            "EQUAL WEIGHT BENCHMARK (test period):\n"
            f"Annualized Return = {benchmark_perf['annualized_return']}\n"
            f"Annualized Volatility = {benchmark_perf['annualized_volatility']}\n"
            f"Sharpe Ratio = {benchmark_perf['sharpe_ratio']}\n"
            f"Max Drawdown = {benchmark_perf['max_drawdown']}\n"
            f"Calmar Ratio = {benchmark_perf['calmar_ratio']}\n"
            f"HHI = {benchmark_perf['hhi']}\n"
            f"Effective N = {benchmark_perf['effective_n']}"
        )

        prices = aligned["prices"][selected_stocks]
        price_history_slice = prices.loc[config.start_date:]
        if price_history_slice.empty:
            price_history_slice = prices

        ph_start = str(price_history_slice.index[0].date())
        ph_end = str(price_history_slice.index[-1].date())
        ph_first = price_history_slice.iloc[0]
        ph_last = price_history_slice.iloc[-1]
        ph_growth = ph_last / ph_first
        ph_returns = (ph_growth - 1.0) * 100.0
        equal_growth = float(ph_growth.mean())
        equal_return = (equal_growth - 1.0) * 100.0

        price_history_lines = [
            f"{ticker}: start={float(ph_first[ticker]):.2f}, "
            f"end={float(ph_last[ticker]):.2f}, "
            f"total_return={float(ph_returns[ticker]):.2f}%"
            for ticker in selected_stocks
        ]
        price_history_string = (
            "PRICE HISTORY (equal-money historical scenario):\n"
            f"Period: {ph_start} to {ph_end}\n"
            "If equal money was invested in each selected stock at period start and held:\n"
            + "\n".join(price_history_lines)
            + f"\nEqual-money basket growth multiple = {equal_growth:.4f}\n"
            + f"Equal-money basket total return = {equal_return:.2f}%"
        )

        governance_note_string = (
            "GOVERNANCE FRAMEWORK:\n"
            "Definition 1 - Instability Index:\n"
            "I_t = (vol_z + corr_z + drift_z) / 3\n"
            "Definition 2 - Regime Operator:\n"
            "R(I_t) = Equal Weight if I_t > theta_H\n"
            "         else ShrunkMV\n"
            "Definition 3 - Governance Stability:\n"
            "GS = L1 norm of weight changes\n"
            f"Current params: lambda={params['lambda']},\n"
            f"                theta_H={params['theta_H']}"
        )

        params_string = (
            "CURRENT PARAMETERS:\n"
            f"Lambda (risk aversion) = {params['lambda']}\n"
            f"Theta_H (regime threshold) = {params['theta_H']}"
        )

        self.session_data["sections"] = {
            "data_info": data_info_string,
            "instability": instability_string,
            "regime": regime_string,
            "shrinkage": shrinkage_string,
            "weights": weights_string,
            "optimization": optimization_string,
            "performance": performance_string,
            "benchmark": benchmark_string,
            "price_history": price_history_string,
            "governance_note": governance_note_string,
            "params": params_string,
        }

        full_context = (
            f"{config.system_prompt}\n\n"
            + "\n\n".join(
                [
                    data_info_string,
                    instability_string,
                    regime_string,
                    shrinkage_string,
                    weights_string,
                    optimization_string,
                    performance_string,
                    benchmark_string,
                    price_history_string,
                    governance_note_string,
                    params_string,
                ]
            )
        )

        return {"role": "system", "content": full_context}

    def _build_focused_context(self, section_names: list) -> dict:
        sections = self.session_data["sections"]
        selected_sections = [sections[name] for name in section_names if name in sections]
        focused_context = f"{config.system_prompt}\n\n" + "\n".join(selected_sections)
        return {"role": "system", "content": focused_context}

    def _build_investment_scenario_context(self, user_message: str):
        query_lower = user_message.lower()
        year_match = re.search(r"\b(19|20)\d{2}\b", query_lower)
        if year_match is None:
            return None

        year = int(year_match.group(0))

        amount = None
        amount_patterns = [
            r"(?:invest|invested|investment)\s*(?:of|in)?\s*([\d,]+(?:\.\d+)?)",
            r"([\d,]+(?:\.\d+)?)\s*(?:rupees|inr|rs)\b",
        ]
        for pattern in amount_patterns:
            amount_match = re.search(pattern, query_lower)
            if amount_match:
                try:
                    amount = float(amount_match.group(1).replace(",", ""))
                except ValueError:
                    amount = None
                break

        if amount is None:
            amount = 1.0

        prices = self.session_data["aligned"]["prices"][self.selected_stocks]
        scenario_prices = prices.loc[f"{year}-01-01":]
        if scenario_prices.empty:
            return (
                "INVESTMENT SCENARIO (query-specific):\n"
                f"Requested start year: {year}\n"
                "No price data found for that start year in the current session."
            )

        start_date = str(scenario_prices.index[0].date())
        end_date = str(scenario_prices.index[-1].date())
        start_row = scenario_prices.iloc[0]
        end_row = scenario_prices.iloc[-1]

        lines = []
        total_start = 0.0
        total_end = 0.0
        gain_count = 0

        for ticker in self.selected_stocks:
            start_price = float(start_row[ticker])
            end_price = float(end_row[ticker])
            growth = (end_price / start_price) if start_price != 0 else 0.0
            final_value = amount * growth
            pnl = final_value - amount
            return_pct = (growth - 1.0) * 100.0
            side = "GAIN" if pnl >= 0 else "LOSS"

            if pnl >= 0:
                gain_count += 1

            lines.append(
                f"{ticker} | {start_price:.2f} | {end_price:.2f} | "
                f"{final_value:.2f} | {return_pct:.2f}% | {side}"
            )
            total_start += amount
            total_end += final_value

        n_assets = len(self.selected_stocks)
        total_return_pct = ((total_end / total_start) - 1.0) * 100.0 if total_start else 0.0
        total_pnl = total_end - total_start
        gain_stocks_pct = (gain_count / n_assets) * 100.0 if n_assets else 0.0
        loss_stocks_pct = 100.0 - gain_stocks_pct if n_assets else 0.0

        return (
            "INVESTMENT SCENARIO (query-specific):\n"
            f"Start year requested: {year}\n"
            f"Actual period used: {start_date} to {end_date}\n"
            f"Investment per stock assumed: {amount:.2f}\n"
            "Rows: Ticker | Start Price | End Price | Final Value | Return % | Gain/Loss\n"
            + "\n".join(lines)
            + "\nSummary:\n"
            + f"Total invested = {total_start:.2f}\n"
            + f"Total final value = {total_end:.2f}\n"
            + f"Total P&L = {total_pnl:.2f}\n"
            + f"Total return = {total_return_pct:.2f}%\n"
            + f"Gain stocks % = {gain_stocks_pct:.2f}%\n"
            + f"Loss stocks % = {loss_stocks_pct:.2f}%"
        )

    def chat(self, user_message: str) -> dict:
        try:
            if not self.session_active:
                return {
                    "success": False,
                    "response": "No active session. Please select stocks first.",
                }

            if user_message == "":
                return {"success": False, "response": "Please type a message."}

            query_lower = user_message.lower()
            has_year = re.search(r"\b(19|20)\d{2}\b", query_lower) is not None
            has_investment_phrase = any(
                phrase in query_lower
                for phrase in ["invest", "return", "how much", "cumulative", "grown", "profit", "loss"]
            )

            intent_result = classify_intent(user_message)
            intent = intent_result["intent"]
            if has_year and has_investment_phrase:
                intent = "historical_query"
            sections = get_context_sections(intent)
            params = extract_parameters(user_message)

            if intent == "parameter_change" and (
                params.get("lambda") is not None or params.get("theta_H") is not None
            ):
                param_change_result = self._handle_parameter_change(params)
                if param_change_result is not None:
                    session_data = self.session_data
                    delta_context = (
                        f"\n\n[PARAMETER CHANGE SUMMARY - "
                        f"Show before vs after comparison table]\n"
                        f"Parameter changed: {list(param_change_result['param_changed'].keys())}\n"
                        f"BEFORE:\n"
                        f"  Lambda = {param_change_result['prev_lambda']}\n"
                        f"  Theta_H = {param_change_result['prev_theta_H']}\n"
                        f"  Sharpe = {param_change_result['prev_sharpe']}\n"
                        f"  Max Drawdown = {param_change_result['prev_max_dd']}\n"
                        f"AFTER:\n"
                        f"  Lambda = {session_data['params']['lambda']}\n"
                        f"  Theta_H = {session_data['params']['theta_H']}\n"
                        f"  Sharpe = {param_change_result['new_sharpe']}\n"
                        f"  Max Drawdown = {param_change_result['new_max_dd']}\n"
                        f"  Regime = {param_change_result['new_regime']}\n"
                        f"Explain what this parameter change means "
                        f"for portfolio governance and risk."
                    )
                    user_message = user_message + delta_context

            scenario_context = None
            if has_year and has_investment_phrase:
                scenario_context = self._build_investment_scenario_context(user_message)

            focused_msg = self._build_focused_context(sections)
            if scenario_context:
                focused_msg = {
                    "role": "system",
                    "content": f"{focused_msg['content']}\n\n{scenario_context}",
                }
            messages_to_send = [focused_msg] + self.messages[1:][-6:]

            self.messages.append({"role": "user", "content": user_message})

            result = AIReasoningAgent.chat(messages_to_send, user_message)

            self.messages.append({"role": "assistant", "content": result["response"]})

            return {
                "success": True,
                "response": result["response"],
                "intent": intent,
                "sections_used": sections,
            }
        except Exception as error:
            return {"success": False, "response": f"Error: {str(error)}"}

    def _handle_parameter_change(self, params: dict) -> dict:
        prev_lambda = self.session_data["params"]["lambda"]
        prev_theta_H = self.session_data["params"]["theta_H"]
        prev_metrics = self.session_data["performance"].copy()
        prev_weights = self.session_data["optimization"]["weights"].copy()
        prev_regime = self.session_data["regime"]["regime"]

        lambda_changed = params.get("lambda") is not None
        theta_changed = params.get("theta_H") is not None

        if lambda_changed:
            self.session_data["params"]["lambda"] = params["lambda"]
            config.risk_aversion = params["lambda"]

        if theta_changed:
            self.session_data["params"]["theta_H"] = params["theta_H"]
            config.theta_H = params["theta_H"]

        if lambda_changed:
            new_opt = OptimizationAgent.run(
                self.session_data["shrinkage"],
                self.session_data["regime"],
            )
            new_perf = PerformanceEvaluator.evaluate_with_benchmark(
                self.session_data["aligned"]["test_returns"],
                new_opt["weights"],
                previous_weights=prev_weights,
            )
            self.session_data["optimization"] = new_opt
            self.session_data["performance"] = new_perf

        if params.get("theta_H") is not None:
            new_theta_H = params["theta_H"]

            # Create updated instability data with new theta_H
            updated_instability = dict(
                self.session_data["instability"]
            )
            updated_instability["theta_H"] = new_theta_H
            updated_instability["above_threshold"] = bool(
                updated_instability["instability"] > new_theta_H
            )

            # Rerun regime with new threshold
            new_regime = RegimeAgent.run(updated_instability)

            # Rerun optimizer with new regime
            new_opt = OptimizationAgent.run(
                self.session_data["shrinkage"],
                new_regime
            )

            # Rerun performance with new weights
            new_perf = PerformanceEvaluator.evaluate_with_benchmark(
                self.session_data["aligned"]["test_returns"],
                new_opt["weights"],
                previous_weights=prev_weights
            )

            # Update session data
            self.session_data["instability"] = updated_instability
            self.session_data["regime"] = new_regime
            self.session_data["optimization"] = new_opt
            self.session_data["performance"] = new_perf

            # Update config
            config.theta_H = new_theta_H
            self.session_data["params"]["theta_H"] = new_theta_H

            # Rebuild system message
            self._build_system_message()

        updated_system_msg = self._build_system_message()
        if self.messages:
            self.messages[0] = updated_system_msg
        else:
            self.messages = [updated_system_msg]

        try:
            regime_changed = prev_metrics != self.session_data["performance"]
        except Exception:
            regime_changed = prev_regime != self.session_data["regime"]["regime"]

        return {
            "param_changed": params,
            "prev_lambda": prev_lambda,
            "prev_theta_H": prev_theta_H,
            "prev_sharpe": prev_metrics["optimized"]["sharpe_ratio"],
            "new_sharpe": self.session_data["performance"]["optimized"]["sharpe_ratio"],
            "prev_max_dd": prev_metrics["optimized"]["max_drawdown"],
            "new_max_dd": self.session_data["performance"]["optimized"]["max_drawdown"],
            "prev_regime": prev_regime,
            "new_regime": self.session_data["regime"]["regime"],
            "regime_changed": regime_changed,
        }

    def reset_session(self) -> dict:
        self.price_data = None
        self.selected_stocks = []
        self.messages = []
        self.session_active = False
        self.session_data = {}
        return {"success": True, "message": "Session reset successfully."}
