import dash
from dash import dcc, html, Input, Output, State
import dash_cytoscape as cyto
cyto.load_extra_layouts()
import networkx as nx
import json
import uuid
import os

from src.parser import parse_boolean_formula
from src.composer import build_graph_from_ast

# --- Translations Dictionary ---
TRANSLATIONS = {
    'en': {
        'title': 'Graph Gadget Editor and Generator',
        'input_label': 'Boolean Formula (e.g., (A + B) ^ C):',
        'generate_btn': 'Generate Graph',
        'export_png_btn': 'Export PNG',
        'export_graphml_btn': 'Export GraphML',
        'export_json_btn': 'Export JSON',
        'error_msg': 'Error generating graph: ',
        'success_msg': 'Graph generated successfully!'
    },
    'es': {
        'title': 'Editor y Generador de Gadgets de Grafos',
        'input_label': 'Fórmula Booleana (ej., (A + B) ^ C):',
        'generate_btn': 'Generar Grafo',
        'export_png_btn': 'Exportar PNG',
        'export_graphml_btn': 'Exportar GraphML',
        'export_json_btn': 'Exportar JSON',
        'error_msg': 'Error al generar el grafo: ',
        'success_msg': '¡Grafo generado con éxito!'
    },
    'fr': {
        'title': 'Éditeur et Générateur de Gadgets de Graphe',
        'input_label': 'Formule Booléenne (ex., (A + B) ^ C):',
        'generate_btn': 'Générer le Graphe',
        'export_png_btn': 'Exporter PNG',
        'export_graphml_btn': 'Exporter GraphML',
        'export_json_btn': 'Exporter JSON',
        'error_msg': 'Erreur lors de la génération du graphe : ',
        'success_msg': 'Graphe généré avec succès !'
    }
}

app = dash.Dash(__name__)
# This is needed for Vercel deployments to work properly
server = app.server

app.layout = html.Div([
    html.Div([
        html.H1(id='app-title', children=TRANSLATIONS['en']['title']),

        html.Div([
            html.Label("Language: "),
            dcc.Dropdown(
                id='lang-dropdown',
                options=[
                    {'label': 'English', 'value': 'en'},
                    {'label': 'Español', 'value': 'es'},
                    {'label': 'Français', 'value': 'fr'}
                ],
                value='en',
                clearable=False,
                style={'width': '150px', 'display': 'inline-block', 'marginLeft': '10px'}
            )
        ], style={'marginBottom': '20px'}),

        html.Label(id='input-label', children=TRANSLATIONS['en']['input_label']),
        dcc.Input(id='formula-input', type='text', value='(A + B) ^ C',
                  style={'width': '400px', 'marginLeft': '10px'}),
        html.Button(id='generate-btn', children=TRANSLATIONS['en']['generate_btn'],
                    n_clicks=0, style={'marginLeft': '10px'}),

        html.Div(id='message-div', style={'marginTop': '10px', 'color': 'red'}),

        html.Div([
            html.Button(id='export-png-btn', children=TRANSLATIONS['en']['export_png_btn'],
                        style={'marginRight': '10px'}),
            html.Button(id='export-graphml-btn', children=TRANSLATIONS['en']['export_graphml_btn'],
                        style={'marginRight': '10px'}),
            html.Button(id='export-json-btn', children=TRANSLATIONS['en']['export_json_btn']),
            dcc.Download(id="download-graphml"),
            dcc.Download(id="download-json")
        ], style={'marginTop': '20px', 'marginBottom': '20px'}),
    ]),

    # Store the actual raw networkx graph JSON in the browser for export callbacks
    dcc.Store(id='networkx-data-store'),

    cyto.Cytoscape(
        id='cytoscape-graph',
        layout={'name': 'dagre'}, # Hierarchical layout
        style={'width': '100%', 'height': '600px', 'border': '1px solid black'},
        elements=[],
        stylesheet=[
            {
                'selector': 'node',
                'style': {
                    'content': 'data(label)',
                    'text-valign': 'center',
                    'color': 'white',
                    'text-outline-width': 2,
                    'text-outline-color': '#222'
                }
            },
            {
                'selector': '[type = "variable"]',
                'style': {
                    'background-color': '#FF4136'
                }
            },
            {
                'selector': '[type = "input"]',
                'style': {
                    'background-color': '#2ECC40',
                    'shape': 'diamond'
                }
            },
            {
                'selector': '[type = "output"]',
                'style': {
                    'background-color': '#0074D9',
                    'shape': 'diamond'
                }
            },
            {
                'selector': '[type = "internal"]',
                'style': {
                    'background-color': '#AAAAAA'
                }
            },
            {
                'selector': 'edge',
                'style': {
                    'curve-style': 'bezier',
                    'target-arrow-shape': 'triangle'
                }
            }
        ]
    )
], style={'fontFamily': 'sans-serif', 'padding': '20px'})


# Callback for translation
@app.callback(
    [Output('app-title', 'children'),
     Output('input-label', 'children'),
     Output('generate-btn', 'children'),
     Output('export-png-btn', 'children'),
     Output('export-graphml-btn', 'children'),
     Output('export-json-btn', 'children')],
    [Input('lang-dropdown', 'value')]
)
def update_language(lang):
    t = TRANSLATIONS.get(lang, TRANSLATIONS['en'])
    return (
        t['title'],
        t['input_label'],
        t['generate_btn'],
        t['export_png_btn'],
        t['export_graphml_btn'],
        t['export_json_btn']
    )


# Callback to parse formula and generate graph elements
@app.callback(
    [Output('cytoscape-graph', 'elements'),
     Output('networkx-data-store', 'data'),
     Output('message-div', 'children'),
     Output('message-div', 'style')],
    [Input('generate-btn', 'n_clicks')],
    [State('formula-input', 'value'),
     State('lang-dropdown', 'value')]
)
def generate_graph(n_clicks, formula, lang):
    if not formula:
        return [], None, "", {}

    t = TRANSLATIONS.get(lang, TRANSLATIONS['en'])

    try:
        ast = parse_boolean_formula(formula)
        graph = build_graph_from_ast(ast)

        elements = []
        # Add nodes
        for node, data in graph.nodes(data=True):
            elements.append({
                'data': {
                    'id': str(node),
                    'label': data.get('label', str(node)),
                    'type': data.get('type', 'default')
                }
            })

        # Add edges
        for source, target in graph.edges():
            elements.append({
                'data': {
                    'source': str(source),
                    'target': str(target)
                }
            })

        # Store node link data for export
        nx_data = nx.node_link_data(graph)

        return elements, nx_data, t['success_msg'], {'marginTop': '10px', 'color': 'green'}

    except Exception as e:
        return [], None, f"{t['error_msg']}{str(e)}", {'marginTop': '10px', 'color': 'red'}


# Callback to trigger PNG export natively through Dash Cytoscape
@app.callback(
    Output("cytoscape-graph", "generateImage"),
    Input("export-png-btn", "n_clicks"),
    prevent_initial_call=True
)
def get_image(n_clicks):
    if n_clicks is None or n_clicks == 0:
        return dash.no_update
    return {
        'type': 'png',
        'action': 'download',
        'filename': 'graph_gadget'
    }


# Callbacks for GraphML and JSON export
@app.callback(
    Output("download-graphml", "data"),
    Input("export-graphml-btn", "n_clicks"),
    State("networkx-data-store", "data"),
    prevent_initial_call=True
)
def export_graphml(n_clicks, graph_data):
    if not graph_data or n_clicks is None or n_clicks == 0:
        return dash.no_update

    graph = nx.node_link_graph(graph_data)
    # Write to a temporary string
    xml_str = "\n".join(nx.generate_graphml(graph))
    return dict(content=xml_str, filename="graph.graphml")


@app.callback(
    Output("download-json", "data"),
    Input("export-json-btn", "n_clicks"),
    State("networkx-data-store", "data"),
    prevent_initial_call=True
)
def export_json(n_clicks, graph_data):
    if not graph_data or n_clicks is None or n_clicks == 0:
        return dash.no_update

    return dict(content=json.dumps(graph_data, indent=2), filename="graph.json")


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)
