"""Custom ipywidgets components for reltools notebooks."""

import ipywidgets as widgets
from IPython.display import display


def create_file_upload_widget():
    """
    Create a file upload widget for SQL files.

    Returns:
        FileUpload widget configured for SQL files
    """
    return widgets.FileUpload(
        accept='.sql',
        multiple=False,
        description='Upload SQL'
    )


def create_output_display():
    """
    Create an output display widget.

    Returns:
        Output widget for displaying results
    """
    return widgets.Output()
