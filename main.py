import customtkinter as ctk
import os
import pandas as pd
import plotly.express as px
import plotly.io as pio
import sys
from datetime import datetime, timedelta
from tkinter import filedialog, messagebox
import webbrowser

class AppWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.altimeter_data = None
        self.imu_data = None

        self.initUI()

    def initUI(self):
        for i in range(3):
            self.grid_rowconfigure(i, weight=1)
        for j in range(2):
            self.grid_columnconfigure(j, weight=1)

        padx = 5
        pady = 5

        self.altimeter_file_button = ctk.CTkButton(self, text="Select Altimeter File", command=self.select_altimeter_file)
        self.altimeter_file_button.grid(row=0, column=0, pady=pady, padx=padx, sticky="we")

        self.show_height_button = ctk.CTkButton(self, text="Show Height above Ground", command=self.show_height)
        self.show_height_button.grid(row=1, column=0, pady=pady, padx=padx, sticky="we")

        self.imu_file_button = ctk.CTkButton(self, text="Select IMU File", command=self.select_imu_file)
        self.imu_file_button.grid(row=0, column=1, pady=pady, padx=padx, sticky="we")

        self.show_z_accel_button = ctk.CTkButton(self, text="Show U-Acceleration", command=self.show_u_acceleration)
        self.show_z_accel_button.grid(row=1, column=1, pady=pady, padx=padx, sticky="we")

        self.timestamp_input = ctk.CTkEntry(self, placeholder_text="Timestamp of liftoff (eg. 2023-11-08 9:47:12.000)")
        self.timestamp_input.grid(row=2, column=1, pady=pady, padx=padx, sticky="we")

        self.altimeter_row_input = ctk.CTkEntry(self, placeholder_text="Altimeter row index of liftoff")
        self.altimeter_row_input.grid(row=2, column=0, pady=pady, padx=padx, sticky="we")

        # Set the fill_timestamps_button at the bottom and center it
        self.fill_timestamps_button = ctk.CTkButton(self, text="Fill in timestamps", command=self.fill_timestamps)
        self.fill_timestamps_button.grid(row=3, column=0, pady=pady, padx=padx, sticky="we", columnspan=2)

        # Set the minimum size of the window
        self.minsize(800, 200)

        # Set window title and size
        self.title('AIR-ETH Altimeter Time Matching Tool')
        self.geometry('800x200')

    def generate_and_open_html_plot(self, fig, file_name):
        """
        Generates an HTML file from a Plotly figure and opens it in the default web browser.

        Args:
        - fig (plotly.graph_objs._figure.Figure): The Plotly figure to convert to HTML.
        - file_name (str): The base name of the HTML file to be created.
        """
        try:
            # Determine the base path for the file (next to the executable or script)
            base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            file_path = os.path.join(base_path, file_name)

            # Convert the figure to HTML and save it
            plot_html = pio.to_html(fig, full_html=False)
            with open(file_path, "w", encoding='utf-8') as file:
                file.write(plot_html)

            # Open the file in the default web browser
            webbrowser.open(f'file://{file_path}')
        except Exception as e:
            print(f"Error in generate_and_open_html_plot: {e}")

    def load_imu_data(self, file_name):
        # Load your data here
        columns_to_import = ["UTC_Nano","UTC_Year","UTC_Month","UTC_Day","UTC_Hour","UTC_Minute","UTC_Second","FreeAcc_U"]
        imu_data = pd.read_csv(file_name, sep=',', usecols=columns_to_import, header=12)

        # Convert the time columns to datetime objects
        imu_data['UTC_DateTime'] = pd.to_datetime(imu_data[['UTC_Year', 'UTC_Month', 'UTC_Day', 'UTC_Hour', 'UTC_Minute', 'UTC_Second', 'UTC_Nano']].rename(columns={
            'UTC_Year': 'year', 
            'UTC_Month': 'month', 
            'UTC_Day': 'day', 
            'UTC_Hour': 'hour', 
            'UTC_Minute': 'minute', 
            'UTC_Second': 'second',
            'UTC_Nano': 'nanosecond'}))

        # Remove all columns except the date and the acceleration
        return imu_data[['UTC_DateTime', 'FreeAcc_U']]

    def select_altimeter_file(self):
        # Select and load the altimeter file
        file_name = filedialog.askopenfilename(title='Open file', filetypes=[('CSV', '*.csv')])
        if file_name:
            self.altimeter_data = pd.read_csv(file_name, sep=';', header=0)
            # Check if header contains "Value" and "Time"
            if not all(x in self.altimeter_data.columns for x in ["Value", "Time"]):
                messagebox.showwarning("Invalid file", "The selected file does not contain the columns 'Value' and 'Time'")
                self.altimeter_data = None
                return
            self.altimeter_data_file_name = file_name
        
    def show_height(self):
        # Logic to show height above ground
        if self.altimeter_data is not None:
            filtered_data = self.altimeter_data[self.altimeter_data['Value'] < 300]
            fig = px.line(filtered_data, x=filtered_data.index, y='Value', title='Altimeter Height vs Row Index (below 300 m)')
            self.generate_and_open_html_plot(fig, "temp_plot_alti.html")
        else: 
            print("Altimeter data is not loaded")

    def select_imu_file(self):
        # Select and load the altimeter file (txt file)
        file_name = filedialog.askopenfilename(title='Open file', filetypes=[('TXT', '*.txt')])
        if file_name: self.imu_data = self.load_imu_data(file_name)

    def get_timestamp_input(self):
        try:
            return datetime.strptime(self.timestamp_input.get(), "%Y-%m-%d %H:%M:%S.%f")
        except ValueError:
            messagebox.showwarning("Invalid input", "The timestamp must be in the format YYYY-MM-DD HH:MM:SS.SSSS")
            return None

    def get_altimeter_row_input(self):
        # Only pass the value if it is not empty and an int
        try:
            return int(self.altimeter_row_input.get())
        except ValueError:
            # Warn the user that the input is not valid with a warning message popup
            messagebox.showwarning("Invalid input", "The altimeter row index must be an integer")
            return None
        
    def show_u_acceleration(self):
        # Logic to show Z-Acceleration
        if self.imu_data is not None:
            imu_data_to_plot = self.imu_data.iloc[::40, :]
            fig = px.line(imu_data_to_plot, x='UTC_DateTime', y='FreeAcc_U', title='Free Acceleration in UP vs Time')
            self.generate_and_open_html_plot(fig, "temp_plot_imu.html")
        else: 
            print("IMU data is not loaded")

    def fill_timestamps(self):
        # Check if all required data is loaded
        if self.altimeter_data is None:
            messagebox.showwarning("Missing data", "Please load the altimeter data")
            return False
        
        lift_off_time = self.get_timestamp_input()
        row_corresponding_to_start_time = self.get_altimeter_row_input()

        if lift_off_time is None or row_corresponding_to_start_time is None:
            # Handle the case where one or both inputs are invalid
            print("Invalid input. Please enter valid data.")
            return False

        # Calculate the actual start time of the data by subtracting the passed time in seconds from the lift off time
        actual_start_time = lift_off_time - timedelta(seconds=self.altimeter_data.loc[row_corresponding_to_start_time, 'Time'])

        # Add new columns for date and time
        self.altimeter_data['Date'] = [actual_start_time + timedelta(seconds=t) for t in self.altimeter_data['Time']]
        self.altimeter_data['YYYY-MM-DD'] = self.altimeter_data['Date'].dt.strftime('%Y-%m-%d')
        self.altimeter_data['HH:MM:SS.SSSS'] = self.altimeter_data['Date'].dt.strftime('%H:%M:%S.%f').str.slice(stop=13)

        # Convert the height from meters to millimeters as integers to finite values
        self.altimeter_data['Height_mm'] = self.altimeter_data['Value'].apply(lambda x: x*1000 if pd.notnull(x) else x)

        # Select the required columns
        formatted_data = self.altimeter_data[['YYYY-MM-DD', 'HH:MM:SS.SSSS', 'Height_mm']]

        # Typecast the height to nullable integer (Int64) if it is finite
        formatted_data.loc[:, 'Height_mm'] = formatted_data['Height_mm'].apply(lambda x: x if pd.isnull(x) else int(x)).astype('Int64')

        # Save the data to the class
        self.formatted_data = formatted_data

        # Remove the .csv in self.altimeter_data_file_name if it exists
        self.altimeter_data_file_name = self.altimeter_data_file_name.replace(".csv", "")

        # Save the data to a CSV file according to the original file name without headers and ";" as separator
        self.formatted_data.to_csv(f"{self.altimeter_data_file_name}_formatted.csv", index=False, header=False, sep=';')

        # Show a success message
        messagebox.showinfo("Success", f"Timestamps filled in and data saved to CSV at {self.altimeter_data_file_name}_formatted.csv")

        return True

# Running the app
if __name__ == '__main__':
    if getattr(sys, 'frozen', False):
        import pyi_splash

    app = AppWindow()
    
    if getattr(sys, 'frozen', False):
        pyi_splash.close()
    
    app.mainloop()
