from dspy.teleprompt import BootstrapFewShot
from .dataset import train_data

def optimize_agent(agent, metric):
    """
    optimize the agent using BootstrapFewShot.
    This finds good few-shot examples from the training data.
    """
    optimizer = BootstrapFewShot(metric=metric, max_bootstrapped_demos=4, max_labeled_demos=4)
    
    # Run the optimization
    optimized_agent = optimizer.compile(agent, trainset=train_data)
    
    return optimized_agent
