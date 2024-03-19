from llama_index.core.schema import TransformComponent
from unstructured.cleaners.core import clean


class UnstructuredIOCleaner(TransformComponent):
    def __call__(self, nodes, **kwargs):
        for node in nodes:
            node.text = clean(
                node.text,
                extra_whitespace=True,
                dashes=True,
                trailing_punctuation=True,
                bullets=True,
            )
        return nodes
