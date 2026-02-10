import cvxpy as cp
import numpy as np

class optimisationagent:
    @staticmethod
    def run(aligned_data:dict, risk_aversion=1.0):
        mean_returns=aligned_data["mean_returns"].values
        covariance=aligned_data["covariance"].values
        assets=aligned_data["mean_returns"].index.tolist()

        n=len(assets)

        #Decision variable: portfolio weights
        w=cp.Variable(n)

        #Objective: maximize risk-adjusted return
        expected_return=mean_returns @ w
        risk=cp.quad_form(w, covariance)

        objective=cp.Maximize(expected_return - risk_aversion*risk)

        #constraints 
        constraints=[
            cp.sum(w)==1,
            w>=0
        ]

        #solve problem 
        problem=cp.Problem(objective , constraints)
        problem.solve(solver=cp.OSQP)

        if problem.status !=cp.OPTIMAL:
            raise ValueError("Optimization did not converge")
        
        weights=w.value

        return {
            "assets":assets,
            "weights":dict(zip(assets, weights)),
            "expected_return":float(mean_returns @ weights),
            "risk":float(weights.T @ covariance @ weights),
            "risk_aversion":risk_aversion
        }