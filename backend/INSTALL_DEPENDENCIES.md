# Installing Dependencies

This project requires Python 3.9.25 for compatibility.

## UV Guide

1. Install Python 3.9.25.
2. `cd` into the backend project directory.
3. Create and activate a virtual environment.

    ```bash
    uv venv .venv
    ```

4. Activate the virtual environment:

    - On Windows:

        ```bash
        source .venv\Scripts\activate
        ```

    - On Unix or MacOS:

        ```bash
        source .venv/bin/activate
        ```

5. Install dependencies with UV:

    ```bash
    uv sync
    ```

## Pip Guide

1. Install Python 3.9.25.
2. `cd` into the backend project directory.
3. Create a virtual environment:

    ```bash
    python -m venv .venv
    ```

4. Activate the virtual environment:

    - On Windows:

        ```bash
        source .venv\Scripts\activate
        ```

    - On Unix or MacOS:

        ```bash
        source .venv/bin/activate
        ```

5. Install dependencies with pip:

```bash
pip install -r requirements.txt
```
