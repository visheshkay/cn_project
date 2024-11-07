from flask import Flask, request, jsonify
import numpy as np
import json

app = Flask(__name__)

graph = None
next_hop = None
n = 0

def init_graph(num_routers):
    global graph, next_hop, n
    n = num_routers
    graph = np.full((n, n), float('inf'))
    next_hop = np.full((n, n), -1)
    for i in range(n):
        graph[i][i] = 0
        next_hop[i][i] = i
    return graph, next_hop

def get_init():
    global graph,next_hop
    pass_results = []
    def convert_value(value):
        if value == float('inf') or value == np.inf:
            return None  # or a large number like 99999 if you prefer
        return int(value)
    pass_results.append({
            "pass_num": int(0),
            "routing_table": [[convert_value(value) for value in row] for row in graph],
            "next_hop": [[convert_value(value) for value in row] for row in next_hop]
        })
    json_result = json.dumps(pass_results, indent=4)
    
    return json_result
    


def add_link(u, v, dist):
    global graph, next_hop
    graph[u][v] = dist
    graph[v][u] = dist
    next_hop[u][v] = v
    next_hop[v][u] = u


def distance_vector_routing():
    global graph, next_hop
    routing_table = graph.copy()
    pass_num = 1
    pass_results = []

    while True:
        updated = False
        new_table = routing_table.copy()

        for i in range(n):
            for j in range(n):
                if i != j:
                    for k in range(n):
                        if routing_table[i][j] > routing_table[i][k] + routing_table[k][j]:
                            new_table[i][j] = routing_table[i][k] + routing_table[k][j]
                            next_hop[i][j] = next_hop[i][k] if next_hop[i][k] != -1 else j
                            updated = True

        # Convert to JSON-compatible format with infinity handling
        def convert_value(value):
            if value == float('inf') or value == np.inf:
                return None  # or a large number like 99999 if you prefer
            return int(value)

        # Store each pass result
        pass_results.append({
            "pass_num": int(pass_num),
            "routing_table": [[convert_value(value) for value in row] for row in new_table],
            "next_hop": [[convert_value(value) for value in row] for row in next_hop]
        })
        
        if not updated:
            break

        routing_table = new_table
        pass_num += 1

    # Convert pass_results to JSON format
    json_result = json.dumps(pass_results, indent=4)
    
    return json_result

@app.route('/init', methods=['POST'])
def init():
    data = request.json
    num_routers = data['num_routers']
    init_graph(num_routers)
    return jsonify({"message": f"Graph initialized with {num_routers} routers"})

@app.route('/add_link', methods=['POST'])
def add_link_route():
    data = request.json  # Expecting data to be a list of link dictionaries
    links = data.get('links', [])  # Extract links array from the request body
    
    for link in links:
        u, v, distance = link['u'], link['v'], link['distance']
        add_link(u, v, distance)
        
    return jsonify({"message": f"{len(links)} links added successfully"})

@app.route('/get_routing_table', methods=['GET'])
def get_routing_table():
    pass_results = distance_vector_routing()
    return jsonify({"pass_results": pass_results})

@app.route('/initial_routing_table',methods=['GET'])
def initial_routing_table():
    res = get_init()
    return jsonify({"initial_table:": res})


if __name__ == '__main__':
    app.run(debug=True)