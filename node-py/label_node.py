from kubernetes import client, config, watch
import sys

# Load Kubernetes configuration from default location
config.load_kube_config()

# Create a Kubernetes client object
v1 = client.CoreV1Api()

# Get list of all nodes in the cluster
nodes = v1.list_node().items

def label_large_nodes(node):
    # Get number of CPUs on the node
    num_cpus = int(node.status.capacity['cpu'])

    # If the node has 8 or more CPUs, label it as "du=yes"
    node_name = node.metadata.name
    labels = node.metadata.labels or {}
    du = "no"
    if num_cpus >= 16:
        du = "yes"
    if labels.get("du") == du:
        print(f"{node_name} already properly labeled")
        return

    labels = {"du": du}

    patch = {"metadata": {"labels": labels}}
    v1.patch_node(node_name, patch)
    print(f"Labeled node {node_name} as du={du}")


# Watch for changes to the list of nodes
w = watch.Watch()
try:
    for event in w.stream(v1.list_node, timeout_seconds=0):
        if event['type'] == 'ADDED' or event['type'] == 'MODIFIED':
            node = event['object']
            label_large_nodes(node)
except KeyboardInterrupt:
    print("Watch stopped by user")
    sys.exit(0)

