import networkx as nx
def find_downstream_dependencies(graph: nx.DiGraph, supplier_id: str) -> dict:

    if supplier_id not in graph:
        raise ValueError(f"Supplier '{supplier_id}' not found.")

    supplier_type = (
        graph.nodes[supplier_id].get("kind")
        or graph.nodes[supplier_id].get("node_type")
    )
    if supplier_type != "supplier":
        raise ValueError(f"'{supplier_id}' is not a supplier.")

    downstream_nodes = nx.descendants(graph, supplier_id)

    result = {"parts": [], "products": [], "orders": []}
    type_mapping = {
        "part": "parts",
        "product": "products",
        "order": "orders",
    }

    for node_id in downstream_nodes:
        node_type = (
            graph.nodes[node_id].get("kind")
            or graph.nodes[node_id].get("node_type")
        )
        category = type_mapping.get(node_type)
        if category is not None:
            result[category].append(node_id)

    for category in result:
        result[category].sort()

    return result
