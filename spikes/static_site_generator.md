# Spike: Static Site Generator for Data Visualization

**Objective:** Research alternative static site generators to MkDocs that offer better capabilities for rendering dynamic data visualizations (graphs, charts) and interactive dashboards, while maintaining compatibility with GitHub Pages.

## Current Limitations with MkDocs
*   **Markdown-centric:** MkDocs is excellent for documentation, where content is primarily text and tables.
*   **Limited native visualization:** While it supports embedding HTML, JavaScript, or iframes, integrating complex interactive charts directly from Python data processing (like Matplotlib, Plotly, Altair outputs) is not natively streamlined. It often requires manually generating image files or converting plots to interactive HTML snippets and then embedding them.

## Requirements for a New Static Site Generator
1.  **GitHub Pages Compatibility:** Must be able to generate static HTML, CSS, and JavaScript that can be served by GitHub Pages.
2.  **Data Visualization Integration:** Seamlessly integrate charts and graphs generated from Python data analysis (e.g., using libraries like Matplotlib, Plotly, Seaborn, Altair). Ideally, it should support:
    *   Embedding static image outputs (PNG, SVG).
    *   Embedding interactive HTML/JavaScript plots.
    *   Dynamic generation of visualizations based on data files (e.g., our `data/market_context.json`).
3.  **Markdown Support:** Continue to support Markdown for reports and analysis text.
4.  **Templating/Customization:** Easy to customize the look and feel.
5.  **Python Integration:** Strong ecosystem for Python-based content generation.

## Potential Alternatives

### 1. Pelican
*   **Description:** A static site generator written in Python. It's file-based (Markdown, reStructuredText) and supports Jinja2 templates.
*   **Pros:** Python-native, good for blogging and content sites. Strong community.
*   **Cons:** Visualization is typically done by generating plots as images and embedding them, or integrating JavaScript charting libraries directly. Not inherently a "data dashboard" tool.
*   **GitHub Pages:** Fully compatible.

### 2. Sphinx
*   **Description:** A documentation generator written in Python, widely used for Python projects. Supports reStructuredText and Markdown (via `MyST-parser`).
*   **Pros:** Very powerful for complex documentation, excellent cross-referencing. Can integrate Jupyter notebooks (using `nbsphinx`), which can contain rich visualizations.
*   **Cons:** Can have a steeper learning curve than MkDocs. Primarily documentation-focused, might be overkill for a simple dashboard.
*   **GitHub Pages:** Fully compatible.

### 3. Jupyter Book
*   **Description:** Builds publication-quality books and documents from computational material, including Jupyter notebooks, Markdown, and reStructuredText. Built on Sphinx.
*   **Pros:** **Excellent for embedding rich, interactive data visualizations directly from Jupyter notebooks.** This could be a very strong contender as our analysis is Python-based. Ideal for showcasing computational results.
*   **Cons:** Might be more structured than a simple website needs, focuses on a "book" format.
*   **GitHub Pages:** Fully compatible.

### 4. Quarto
*   **Description:** An open-source scientific and technical publishing system that combines markdown, code (Python, R, Julia), and output. It can render interactive plots from Plotly, Altair, etc., directly.
*   **Pros:** Language-agnostic (supports Python well), highly flexible output formats (HTML, PDF, Word), excellent native support for interactive visualizations and dynamic content from code cells. Very modern.
*   **Cons:** A new tool to learn, different ecosystem.
*   **GitHub Pages:** Fully compatible.

### 5. Custom Flask/Django Micro-app (Not Static)
*   **Description:** Building a small Python web application that dynamically renders charts.
*   **Pros:** Ultimate flexibility.
*   **Cons:** **Not compatible with GitHub Pages** (which only serves static files). Requires a web server (Heroku, Vercel, AWS, etc.), increasing complexity and cost. *Out of scope for this static site requirement.*

## Initial Thoughts
*   **Jupyter Book** and **Quarto** seem like the strongest candidates for integrating advanced Python-generated data visualizations while remaining compatible with GitHub Pages.
*   Both allow for embedding executable code blocks (or results of code execution) directly into the content, which is key for our data-driven analysis.
*   **Jupyter Book** leverages the familiarity of Jupyter notebooks, which is a common environment for data science.
*   **Quarto** offers a very modern, versatile approach to scientific publishing that is highly geared towards interactive results.

Let's explore either Jupyter Book or Quarto further to see which best fits the need for rendering our specific stock analysis graphs.