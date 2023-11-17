import os
import sys
import webview


def delete_temp_file(html_file_path):
    """
    Delete the specified temporary HTML file.

    Parameters:
    html_file_path (str): The file path of the HTML file to be deleted.

    Returns:
    None
    """
    if os.path.exists(html_file_path):
        os.remove(html_file_path)


def main():
    """
    Main function to create and display a webview window.

    Reads an HTML file specified in the command line arguments, creates
    a webview window with this HTML content, and deletes the file after
    the window is closed.

    Command Line Arguments:
    1st argument (optional): File path to the HTML file.

    Returns:
    None
    """
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

    # After the window is closed, delete the temporary file
    delete_temp_file(html_file_path)


if __name__ == "__main__":
    main()
