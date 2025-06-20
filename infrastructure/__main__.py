import pulumi
from pulumi import export, get_stack, Output
import pulumi_docker as docker

# Get the stack name to tag resources.
stack = get_stack()

# Build and publish the backend image using the production Dockerfile.
backend_image = docker.Image(
    "sophia-backend-image",
    build=docker.DockerBuild(context="..", dockerfile="../Dockerfile.production"),
    image_name=f"sophia-backend:{stack}",
    skip_push=True,
)

# Define and run the backend container.
backend_container = docker.Container(
    "sophia-backend-container",
    image=backend_image.base_image_name,
    name=f"sophia-backend-{stack}",
    ports=[
        docker.ContainerPortArgs(
            internal_port=8000,
            external_port=8000,
        )
    ],
)

# Export the container name and the backend URL for easy access.
export("container_name", backend_container.name)
export("backend_url", Output.concat("http://localhost:", str(backend_container.ports[0].external_port)))
