import tkinter as tk
import tkinter.messagebox
import customtkinter
import csv
import threading
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

customtkinter.set_appearance_mode("System")  
customtkinter.set_default_color_theme("blue")
scmap = plt.cm.gist_earth
MPLBACKEND = FigureCanvasTkAgg

# GUI
class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        # Create Window
        self.title("Irgendeine Name für das Fenster")
        self.geometry(f"{1200}x{580}")
        # Create Grid 4 Column -> 2,3 for plotting
        self.grid_columnconfigure((0, 1, 2), weight=0)
        self.grid_columnconfigure(3, weight=1)
        self.grid_rowconfigure((0, 1, 2), weight=1)
        self.grid_rowconfigure(3, weight=0)


        # Left Sidebar with GUI Settings and Name of the programm / description 
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="Name der App", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(5, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(5, 5))
        self.scaling_label = customtkinter.CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=7, column=0, padx=20, pady=(5, 0))
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["80%", "90%", "100%", "110%", "120%"],
                                                               command=self.change_scaling_event)
        self.scaling_optionemenu.grid(row=8, column=0, padx=20, pady=(5, 20))


        # Main coordinate Selection Window, values are stored in self.entry_values
        self.selection_frame = customtkinter.CTkFrame(self)
        self.selection_frame.grid(row=0, column=1, rowspan=3, padx=20, pady=(20, 10), sticky="nsew")
        self.selection_frame.grid_rowconfigure(7, weight=1)

        self.labels = ["Longitude", "Latidude", "Radius"]
        self.entrys_placehoder = ["Entry Longitude", "Entry Latitude", "Entry Radius"]
        self.entry_values = []
        self.results = zip(self.labels, self.entrys_placehoder)
        
        self.counter = 0
        for item in self.results:
            self.label_item = customtkinter.CTkLabel(self.selection_frame, text=item[0], font=(customtkinter.CTkFont(size=15)))
            self.label_item.grid(row=self.counter, column=0, padx=20, pady=(5,5), sticky="w")
            self.counter += 1
            self.entry= customtkinter.CTkEntry(self.selection_frame, placeholder_text=item[1])
            self.entry.grid(row=self.counter, column=0, padx=20, pady=(5,5), sticky="w")
            self.entry_values.append(self.entry)
            self.counter += 1
        
        self.apply_butoon = customtkinter.CTkButton(self.selection_frame, text="Apply", command=self.read_initial_cords)
        self.apply_butoon.grid(row=7, column=0, padx=(20,20), pady=(5,10), sticky="sew")


        # Frame for selecting additional coordinates, stored in self.additional_latidude_values / self.additional_longitude_values
        self.additional_cord_frame = customtkinter.CTkFrame(self)
        self.additional_cord_frame.grid(row=0, column=2, rowspan=4, padx=(0, 20), pady=(20, 20), sticky="nsew")
        self.additional_cord_frame.grid_rowconfigure(50, weight=1)
        self.additional_cord_frame.grid_columnconfigure(2, weight=1)

        self.add_cords_label = customtkinter.CTkLabel(self.additional_cord_frame, text="Additional Cords")
        self.add_cords_label.grid(row=0, column=0, columnspan=2, padx=20, pady=(5,5), sticky="we")

        self.add_button = customtkinter.CTkButton(self.additional_cord_frame, text="ADD", width=70, 
                command=lambda: self.change_entrys_additional_cords(True))
        self.add_button.grid(row=1, column=0, padx=(5,5), pady=(5,5), sticky="nw")
        self.del_button = customtkinter.CTkButton(self.additional_cord_frame, text="DEL", width=70, 
                command=lambda: self.change_entrys_additional_cords(False))
        self.del_button.grid(row=1, column=1, padx=(5,5), pady=(5,5), sticky="ne")


        # Status Frame for current work and Progress bar
        self.status_frame = customtkinter.CTkFrame(self, height=100)
        self.status_frame.grid(row=3, column=1, padx=20, pady=(10,20), sticky="nsew")
        self.status_frame.grid_rowconfigure(2, weight=1)
        self.progress_label = customtkinter.CTkLabel(self.status_frame, text="PROGRESS")
        self.progress_label.grid(row=0, column=0, padx=20, pady=10)
        self.progressbar = customtkinter.CTkProgressBar(self.status_frame, mode="intermidiate")
        self.progressbar.grid(row=1, column=0, padx=(20, 20), pady=(10, 20), sticky="sew")


        # Plot Window to create a matplotlib plot
        self.image_frame = customtkinter.CTkFrame(self)
        self.image_frame.grid(row=0, column=3, rowspan=4, columnspan=1, padx=(0, 20), pady=(20, 20), sticky="nsew")
        self.image_frame.grid_rowconfigure(4, weight=1)
        self.image_frame.grid_columnconfigure(0, weight=1)
        self.plot_button = customtkinter.CTkButton(self.image_frame, text="Plot", command=self.plot_entry)
        self.plot_button.grid(row=0, column=0, padx=20, pady=(20, 10))

        
        # Values to initialize by laoding the Window
        self.appearance_mode_optionemenu.set("System")
        self.scaling_optionemenu.set("100%")

        self.row_number_of_item = 1 # Value for additional cord first row
        self.additional_latidude_values = []
        self.additional_longitude_values = []


    # Functions
    # Example plot function with random heatmap 
    def plot_entry(self):
        fig = plot_xyz_cords()
        self.canvas= FigureCanvasTkAgg(fig, master=self.image_frame)
        self.canvas.get_tk_widget().grid(row=1, rowspan=3, column=0, padx=20, pady=10)


    # Change the appearance from the GUI
    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)


    # Change the scale of every item
    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)


    # Returns the main coordinate Values
    def read_initial_cords(self):
        for entry in zip(self.entry_values, self.labels):
            value = float(entry[0].get())
            print(value, entry[1])


    # Add and remove additional entry fields
    def change_entrys_additional_cords(self, add: bool):
        if add:
            self.add_button.grid_forget()
            self.del_button.grid_forget()
            self.entry= customtkinter.CTkEntry(self.additional_cord_frame, placeholder_text="longitude", width=70)
            self.entry.grid(row=self.row_number_of_item, column=0, padx=(5,5), pady=(5,5), sticky="w")
            self.additional_longitude_values.append(self.entry)
            self.entry= customtkinter.CTkEntry(self.additional_cord_frame, placeholder_text="latidude", width=70)
            self.entry.grid(row=self.row_number_of_item, column=1, padx=(5,5), pady=(5,5), sticky="w")
            self.additional_latidude_values.append(self.entry)
            self.row_number_of_item += 1
            self.add_button.grid(row=self.row_number_of_item, column=0, padx=(5,5), pady=(5,5), sticky="nw")
            self.del_button.grid(row=self.row_number_of_item, column=1, padx=(5,5), pady=(5,5), sticky="ne")
        else:
            self.additional_latidude_values[-1].grid_forget()
            self.additional_latidude_values.pop(-1)
            self.additional_longitude_values[-1].grid_forget()
            self.additional_longitude_values.pop(-1)
            self.add_button.grid_forget()
            self.del_button.grid_forget()
            self.row_number_of_item -= 1

            self.add_button.grid(row=self.row_number_of_item, column=0, padx=(5,5), pady=(5,5), sticky="nw")
            self.del_button.grid(row=self.row_number_of_item, column=1, padx=(5,5), pady=(5,5), sticky="ne")

            
if __name__ == "__main__":

# LOGICAL FUNCTIONS
#-----------------------------------------------------------------------
# Extract Cords from a given File - Later file from cord selection
    def extract_xyz_cords():
        csvData = []
        with open("osm/geo_data.txt", "r") as csvFile:
            csvReader = csv.reader(csvFile, delimiter=" ")
            for csvRow in csvReader:
                csvData.append(csvRow[0:3])
        csvData = np.asarray(csvData)
        csvData = csvData.astype(np.float_)
        x, y, z = csvData[:,0], csvData[:,1], csvData[:,2]
        return x, y, z

# Creates the topography map 
    def plot_xyz_cords():
        x,y,z = extract_xyz_cords()
        x=np.unique(x)
        y=np.unique(y)
        X,Y = np.meshgrid(x,y)
        Z=z.reshape(len(x),len(y))
        Z=np.transpose(Z)
        data = Z  
        fig = plt.figure(figsize=(4,4), dpi = 100, facecolor="#2A68A3")
        ax = fig.add_subplot(111)
        ax.contour(X, Y, Z, 7, linewidths = 0.5, colors = 'k')
        im = ax.imshow(data, cmap = scmap, interpolation = 'gaussian', origin='lower',\
                    aspect='equal',  extent = [min(x), max(x), min(y), max(y)] ) 
        ax.set_title("Topography Sample", fontsize=15)
        ax.set_xlabel("X", fontsize=10)
        ax.set_ylabel("Y", fontsize=10)
        fig.colorbar(im)                    # Adding CB
        fig.autofmt_xdate(rotation=45)      # rotate x labels
        return fig

    # Destroy tk-frames and Canvas drawing
    def on_closing():
        app.destroy()
        exit()


    # creating app instance an mainloop it
    app = App()
    app.protocol("WM_DELETE_WINDOW", on_closing)
    app.mainloop()
    

'''
Der Plot kann nicht in einem seperaten Thread erstellt werden da matplotlib nicht
"Threadsicher" ist.
'''