from llama_index.core import set_global_handler


def initialize_tracing_service(service: str = "wandb", project: str = "talking-resume") -> None:
    set_global_handler(service, run_args={"project": project})
