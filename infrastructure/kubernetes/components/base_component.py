from pulumi import ComponentResource


class BaseComponent(ComponentResource):
    def __init__(self, name: str, opts=None):
        super().__init__(f"sophia:components:{name}", name, None, opts)
        self.outputs = {}

    def register_outputs(self, outputs: dict):
        # Register all outputs for the component
        for key, value in outputs.items():
            self.outputs[key] = value

        # Also register them as top-level outputs of the component
        super().register_outputs(self.outputs)
