"""Streamlit Community Cloud entry point for Wasla."""

from pathlib import Path
import runpy

# Streamlit reruns this file after every interaction.  A normal ``import app``
# is cached by Python after the first pass, leaving the page empty on the next
# rerun.  Executing app.py as the active script keeps every interaction live.
runpy.run_path(str(Path(__file__).with_name("app.py")), run_name="__main__")
