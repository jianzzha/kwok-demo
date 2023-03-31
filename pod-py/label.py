import asyncio
import kopf
import jsonschema
from kubernetes.client import (CoreV1Api, CustomObjectsApi)
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
    logger.info(
        f"Handling creation of MyCustomResource {meta['name']} in namespace {namespace}")
    # Validate the MyCustomResource object against the schema
    try:
        jsonschema.validate(
            spec, MY_CUSTOM_RESOURCE_SCHEMA["properties"]["spec"]["properties"])
    except jsonschema.exceptions.ValidationError as e:
        logger.error(f"Invalid MyCustomResource object: {e}")
        return

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
            logger.info(
                f"Labeled Pod {pod.metadata.name} with mycustomresource/data={spec['data']}")
        except ApiException as e:
            logger.error(f"Failed to label Pod {pod.metadata.name}: {e}")


def label_pod(pod):
    namespace = pod['metadata']['namespace']
    api = CoreV1Api()
    custom_api_client = CustomObjectsApi()
    # List all custom resources that belong to the CRD
    cr_list = custom_api_client.list_namespaced_custom_object(
        group='example.com',
        version='v1',
        namespace=namespace,
        plural='mycustomresources'
    )
    # Tag any newly created pod based on the `data` field in the custom resource object
    for cr in cr_list['items']:
        data = cr.get('spec', {}).get('data')
        if data:
            labels = pod['metadata'].get('labels', {})
            labels['mycustomresource/data'] = data
            api.patch_namespaced_pod(
                name=pod['metadata']['name'],
                namespace=namespace,
                body={
                    "metadata": {
                        "labels": {
                            "mycustomresource/data": data
                        }
                    }
                }
            )


@kopf.on.update('pod')
def handle_pod_update(body, old, new, **kwargs):
    old_data = old['metadata'].get('labels', {}).get('mycustomresource/data')
    new_data = new['metadata'].get('labels', {}).get('mycustomresource/data')
    if old_data == new_data:
        return
    label_pod(body)


@kopf.on.create('pods')
def handle_pod_creation(body, **kwargs):
    label_pod(body)


def initialize(logger):
    api = CoreV1Api()
    custom_api_client = CustomObjectsApi()
    try:
        cr_list = custom_api_client.list_cluster_custom_object(
                group='example.com',
                version='v1',
                plural='mycustomresources'
        )
    except ApiException as e:
        logger.info("API error, CRD not defined")
        return

    logger.info(f"{cr_list}")
    if cr_list and len(cr_list['items']) == 0:
        logger.info("CR not defined")
        return

    for cr in cr_list['items']:
        namespace = cr['metadata']['namespace']
        data = cr.get('spec', {}).get('data')
        if not data:
            continue
        pods = api.list_namespaced_pod(namespace=namespace).items
        for pod in pods:
            if 'mycustomresource/data' not in pod.metadata.labels or \
                pod.metadata.labels['mycustomresource/data'] != data:
                pod.metadata.labels['mycustomresource/data'] = data
                api.patch_namespaced_pod(
                    pod.metadata.name,
                    pod.metadata.namespace,
                    {'metadata': {'labels': pod.metadata.labels}}
                )


async def delayed_task(logger):
    await asyncio.sleep(1)
    initialize(logger)


@kopf.on.startup()
async def startup_handler(logger, **kwargs):
    task = asyncio.create_task(delayed_task(logger))


if __name__ == '__main__':
    kopf.run()