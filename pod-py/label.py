import kopf
import jsonschema
from kubernetes.client import CoreV1Api
from kubernetes.client.rest import ApiException

# Define the CRD schema for MyCustomResource
MY_CUSTOM_RESOURCE_SCHEMA = {
    "type": "object",
    "required": ["apiVersion", "kind", "metadata", "spec"],
    "properties": {
        "kind": {"type": "string"},
        "apiVersion": {"type": "string"},
        "metadata": {
            "type": "object",
            "required": ["name"],
            "properties": {
                "name": {"type": "string"}
            }
        },
        "spec": {
            "type": "object",
            "required": ["data"],
            "properties": {
                "data": {"type": "string"}
            }
        }
    }
}

# Define a handler function for the MyCustomResource object
@kopf.on.create('example.com', 'v1', 'mycustomresources')
@kopf.on.update('example.com', 'v1', 'mycustomresources')
def handle_mycustomresource_creation(spec, meta, namespace, logger, **kwargs):
    logger.info(f"Handling creation of MyCustomResource {meta['name']} in namespace {namespace}")
    # Validate the MyCustomResource object against the schema
    try:
        jsonschema.validate(spec, MY_CUSTOM_RESOURCE_SCHEMA["properties"]["spec"]["properties"])
    except jsonschema.exceptions.ValidationError as e:
        logger.error(f"Invalid MyCustomResource object: {e}")
        return

    # Get the CoreV1Api instance
    api = CoreV1Api()

    # List all Pods in the same namespace
    pods = api.list_namespaced_pod(namespace=namespace)

    # Loop through all Pods in the namespace and label them
    for pod in pods.items:
        try:
            api.patch_namespaced_pod(
                name=pod.metadata.name,
                namespace=namespace,
                body={
                    "metadata": {
                        "labels": {
                            "mycustomresource/data": spec['data']
                        }
                    }
                }
            )
            logger.info(f"Labeled Pod {pod.metadata.name} with mycustomresource/data={spec['data']}")
        except ApiException as e:
            logger.error(f"Failed to label Pod {pod.metadata.name}: {e}")

