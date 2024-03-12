from packages.pipeline.gpt import get_chat_response
from packages.pipeline.notebookreader import extract_cells


cell_output = extract_cells("Pipeline Testing.ipynb")
emotions = "Bored"

get_chat_response(cell_output, emotions)