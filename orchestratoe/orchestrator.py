
from agents.data_agent import datafetchagent
from agents.data_alignment_agent import Dataalignmentagent
from agents.optimization_agent import optimisationagent
from agents.ai_reasoning_agent import aireasoningagent

class orchestrator:
    def __init__(self,config):
        self.config=config

    def run_pipeline(self):
        # fetch raw price data 
        raw_data=datafetchagent.run(
            assets=self.config.assets,
            start_date=self.config.start_date,
            end_date=self.config.end_date,
            frequency=self.config.frequency
        )

        #align data and compute statistics 

        aligned_data=Dataalignmentagent.run(raw_data)

        #run classical portifoio optimisation

        portfolio_result=optimisationagent.run(aligned_data,
                            risk_aversion=self.config.risk_aversion
                                               )
        #Generate ai based explanations and insights 
        explanations=aireasoningagent.run(
            portfolio_result,
            )
        
        #return structure output 

        return {
            "portfolio result": portfolio_result,
            "explanations": explanations
        }
