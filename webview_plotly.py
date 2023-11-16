import sys
import webview
import os

def delete_temp_file(html_file_path):
    # Delete the temporary HTML file
    if os.path.exists(html_file_path):
        os.remove(html_file_path)

if __name__ == "__main__":
    # Get the path to the HTML file from the command line arguments
    html_file_path = sys.argv[1] if len(sys.argv) > 1 else ""

    # Read the HTML content
    html_content = ""
    if os.path.exists(html_file_path):
        with open(html_file_path, "r") as file:
            html_content = file.read()

    # Create and start the webview window
    window = webview.create_window('Data Visualizer', html=html_content)

    # Start the webview and wait until the window is closed
    webview.start(debug=True)

    # After the window is closed, delete the temporary file and signal completion
    delete_temp_file(html_file_path)
