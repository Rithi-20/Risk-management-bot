# GenAI Legal Assistant - Hackathon Demo

## Overview
This application is a **Legal Co-Pilot for SMEs**, designed to analyze contracts, identify risks (Indian Law Context), and provide plain-English explanations.

## Features
*   **Instant Risk Scoring**: Visual gauge of contract fairness.
*   **Red Flag Detection**: Automatically finds "Indemnity", "Unilateral Termination", and "Jurisdiction" issues.
*   **Clause Explorer**: Side-by-side view (Legal Text vs. Simple English).
*   **PDF Report**: Downloadable audit trail.
*   **Indian Context**: tuned for MSME payment terms and local jurisdiction.

## Setup & Run
1.  **Prerequisites**: Python 3.10+
2.  **Install**:
    ```bash
    python -m venv venv
    ./venv/Scripts/activate
    pip install -r requirements.txt
    python -m spacy download en_core_web_sm
    ```
3.  **Run**:
    ```bash
    streamlit run main.py
    ```

## Project Structure
*   `main.py`: The dashboard application (Streamlit).
*   `src/logic/risk_engine.py`: The "Brain" (Mock LLM + Heuristics).
*   `src/logic/nlp_processor.py`: Text extraction & Entity recognition.
*   `src/utils/`: PDF generation and file handling.

## Future Roadmap
*   Connect real LLM API (GPT-4/Claude) in `risk_engine.py`.
*   add `google-trans-new` for full Hindi translation.
