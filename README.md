# Environments

A simple framework to create and deploy custom environments on the Hugging Face Hub with MCP.

## Installation

```bash
pip install git+https://github.com/huggingface/environments.git
```

## Create your Environment

```python
from environments import Environment

class CountToTen(Environment):
    def __init__(self):
        self.counter = None

    def reset(self) -> tuple[dict, float, bool]:
        self.counter = 0
        return f"Counter reset to {self.counter}", 0.0, False

    def step(self) -> tuple[dict, float, bool]:
        if self.counter is None or self.counter >= 10:
            return "Try resetting first", 0.0, False
        self.counter += 1
        return f"Counter is now {self.counter}", 1.0, self.counter >= 10
```

## Deploy your Environment on the Hugging Face Hub with MCP

```python
from environments import register_env
import gradio as gr

with gr.Blocks() as demo:
    register_env(CountToTen)

demo.launch(mcp_server=True)
```

Check this space: https://huggingface.co/spaces/qgallouedec/counter

## Load and use your environment

```python
>>> from environments import load
>>> env = load("qgallouedec/counter")
Loaded as API: https://qgallouedec-counter.hf.space/ ✔
>>> env.reset()
('Counter reset to 0', 0.0, False)
>>> env.step()
('Counter is now 1', 1.0, False)
```
