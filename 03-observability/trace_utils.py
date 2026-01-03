import os
from langfuse.decorators import observe

def setup_tracing():
    """Configure Langfuse for tracing."""
    # Ensure keys are set in environment
    if not os.environ.get("LANGFUSE_PUBLIC_KEY"):
        print("Warning: LANGFUSE_PUBLIC_KEY not set")
    
    print("Langfuse tracing enabled.")
    # In DSPy, we might use a callback or the decorator pattern
    # dspy.settings.configure(callbacks=[...])
