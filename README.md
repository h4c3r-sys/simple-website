# Graph Gadget Editor and Generator

An interactive web application built with Python, Dash, and NetworkX that parses Boolean formulas and generates editable graph gadgets for computational complexity theory and graph theory analysis.

## Features

- **Formula Parser:** Parses Boolean expressions using a custom shunting-yard algorithm `(+, *, &, !, ~, ^)`.
- **Modular Gadget Dictionary:** Easily map logical operators to specific Graph Gadgets (subgraphs). Expandable logic inside `src/gadgets.py`.
- **Global Variable Node Sharing:** Identical variables across a formula link back to a single shared Variable Gadget.
- **Interactive UI:** Built with Dash and Cytoscape. Drag and re-arrange nodes.
- **Multi-language Support:** Includes English, Spanish, French, and Polish out of the box.
- **Data Export:** Export visual configurations as PNG images, or download raw structures in GraphML and JSON formats.

## Local Setup

1. **Install dependencies:**
   Make sure you have Python 3.8+ installed. Run:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the server:**
   ```bash
   PYTHONPATH=. python3 app.py
   ```
   Open `http://localhost:8050` in your web browser.

## Deployment to Vercel (Free Serverless Hosting)

This project is configured out-of-the-box for [Vercel](https://vercel.com). Vercel is an excellent option for free hosting of simple Python Dash/Flask applications.

1. **Install Vercel CLI (optional but recommended):**
   ```bash
   npm i -g vercel
   ```

2. **Deploy:**
   Navigate to the project root directory and run:
   ```bash
   vercel
   ```
   Follow the prompts. Vercel will automatically read the `vercel.json` file, install dependencies from `requirements.txt`, and deploy the `api/index.py` serverless function route.

3. **Deploying via GitHub (Alternative):**
   - Push this code to a GitHub repository.
   - Log into Vercel, click "Add New Project", and import your GitHub repository.
   - Vercel will automatically detect the configuration and deploy it for you.

## Deployment to Netlify

Netlify does not have native, heavy-duty Python support like Vercel's serverless functions out of the box, but you can deploy it using Netlify Functions if you convert the application logic slightly, or more easily, deploy it on platforms like **Render**, **Heroku**, or **Fly.io** using standard Python hosting.

## Customizing Gadgets

To add complex, custom gadgets for a specific graph reduction (like 3-Coloring or Vertex Cover):
1. Open `src/gadgets.py`.
2. Find the class for the operator you want to change (e.g., `XorGadget`).
3. Add custom nodes using `self._add_node(...)` and link them using `self._add_edge(...)`.
4. The Graph Composer will automatically hook the inputs and outputs of your new subgraph into the global AST tree.
