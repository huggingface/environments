import inspect
import uuid
from abc import ABC, abstractmethod
from functools import wraps

import gradio as gr
from gradio_client import Client


__version__ = "0.1.0"
__all__ = ["Environment", "load", "register_env"]


class Environment(ABC):
    @abstractmethod
    def reset(self, *args, **kwargs):
        pass

    @abstractmethod
    def step(self, *args, **kwargs):
        pass


class _RemoteEnvironment(Environment):
    def __init__(self, env_id: str):
        username, repo = env_id.split("/")
        self.client = Client(f"https://{username}-{repo}.hf.space/")
        self.session_id = self.client.predict(api_name="/init")

    def reset(self, *args, **kwargs):
        return self.client.predict(self.session_id, api_name="/reset", *args, **kwargs)

    def step(self, *args, **kwargs):
        return self.client.predict(self.session_id, api_name="/step", *args, **kwargs)


def load(env_id: str) -> _RemoteEnvironment:
    return _RemoteEnvironment(env_id)


def bind_method_to_session(method, registry: dict):
    sig = inspect.signature(method)
    params = list(sig.parameters.values())

    @wraps(method)
    def wrapper(session_id: str, *args, **kwargs):
        instance = registry.get(session_id)
        if instance is None:
            raise ValueError(f"Invalid session_id: {session_id}")
        m = getattr(instance, method.__func__.__name__)
        return m(*args, **kwargs)

    # --- update __annotations__ ---
    wrapper.__annotations__ = method.__annotations__.copy()
    wrapper.__annotations__["session_id"] = str

    # --- build signature ---
    new_params = (
        inspect.Parameter(
            "session_id",
            kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation=str,
        ),
        *params,
    )
    wrapper.__signature__ = inspect.Signature(
        parameters=new_params,
        return_annotation=sig.return_annotation,
    )

    return wrapper


def register_env(env_cls: type[Environment]) -> gr.Blocks:
    """
    Register an environment class with Gradio APIs.

    Example:

    ```python
    from environments import register_env, Environment
    import gradio as gr

    class MyEnvironmentClass(Environment):
        def reset(self) -> str:
            return "Reset called!"

        def step(self, action: str) -> str:
            return f"Step called with action: {action}!"

    with gr.Blocks() as demo:
        register_env(MyEnvironmentClass)

    demo.launch(mcp_server_name=True)
    ```
    """
    sessions = {}

    def init_env() -> str:
        """
        Initialize a new environment instance and return a session ID.
        Returns:
            A unique session ID for the new environment instance.
        """
        session_id = str(uuid.uuid4())
        env = env_cls()
        sessions[session_id] = env
        return session_id

    # Bind methods to session dict
    reset_api = bind_method_to_session(env_cls().reset, sessions)
    step_api = bind_method_to_session(env_cls().step, sessions)

    # Create Gradio APIs
    gr.api(
        init_env,
        api_name="init",
        api_description="Initialize a new environment session",
    )
    gr.api(reset_api, api_name="reset")
    gr.api(step_api, api_name="step")
