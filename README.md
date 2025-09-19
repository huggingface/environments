# Environments

A simple Python package demonstrating the basic structure for a pip installable package.

## Installation

```bash
pip install git+http://github.com/huggingface/environments.git
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

demo.launch(mcp_server_name=True)
```
