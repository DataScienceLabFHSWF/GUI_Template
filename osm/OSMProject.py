import tkinter as tk
import tkinter.messagebox
import customtkinter
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
import matplotlib.pyplot as plt

customtkinter.set_appearance_mode("System")  
customtkinter.set_default_color_theme("blue")  


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # Create Window
        self.title("Irgendeine Name für das Fenster")
        self.geometry(f"{1200}x{580}")

        # Create Grid 4 Column -> 2,3 for plotting
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure((2, 3), weight=1)
        self.grid_rowconfigure((0, 1, 2), weight=1)
        self.grid_rowconfigure(3, weight=0)


        # Left Sidebar with GUI Settings and Name of the programm 
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


        # Selection Frame for cords
        self.selection_frame = customtkinter.CTkFrame(self)
        self.selection_frame.grid(row=0, column=1, rowspan=3, padx=20, pady=(20, 10), sticky="nsew")
        self.selection_frame.grid_rowconfigure(6, weight=1)
        self.longitude_entry = customtkinter.CTkEntry(self.selection_frame, placeholder_text="Entry Longitude")
        self.longitude_entry.grid(row=1, column=0, padx=20, pady=(10,10))

        self.longitude_label = customtkinter.CTkLabel(self.selection_frame, text="Longitude")
        self.longitude_label.grid(row=0, column=0, padx=20, pady=(10,10))
        self.longitude_entry = customtkinter.CTkEntry(self.selection_frame, placeholder_text="Entry Longitude")
        self.longitude_entry.grid(row=1, column=0, padx=20, pady=(10,10))

        self.latidude_label = customtkinter.CTkLabel(self.selection_frame, text="Latidude")
        self.latidude_label.grid(row=2, column=0, padx=20, pady=(10,10))
        self.latidude_entry = customtkinter.CTkEntry(self.selection_frame, placeholder_text="Entry Latidude")
        self.latidude_entry.grid(row=3, column=0, padx=20, pady=(10,10))
        self.latidude_entry

        self.radius_label = customtkinter.CTkLabel(self.selection_frame, text="Radius")
        self.radius_label.grid(row=4, column=0, padx=20, pady=(10,10))
        self.radius_entry = customtkinter.CTkEntry(self.selection_frame, placeholder_text="Entry Radius")
        self.radius_entry.grid(row=5, column=0, padx=20, pady=(10,10))

        
        # Status Frame
        self.status_frame = customtkinter.CTkFrame(self)
        self.status_frame.grid(row=3, column=1, padx=20, rowspan=1, pady=(10,20), sticky="nsew")
        self.status_frame.rowconfigure(1, weight=1)
        self.progress_label = customtkinter.CTkLabel(self.status_frame, text="progress")
        self.progress_label.grid(row=0, column=0, padx=20, pady=10)
        self.progressbar = customtkinter.CTkProgressBar(self.status_frame)
        self.progressbar.grid(row=1, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")


        # Plot Frame for matplotlib
        self.image_frame = customtkinter.CTkFrame(self)
        self.image_frame.grid(row=0, column=2, rowspan=4, columnspan=2, padx=(0, 20), pady=(20, 20), sticky="nsew")
        self.image_frame.grid_rowconfigure(4, weight=1)
        self.placeholder = customtkinter.CTkLabel(self.image_frame, text="Plot")
        self.placeholder.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.figure = Figure(figsize=(4,4), dpi=100)
        self.figure_canvas = FigureCanvasTkAgg(self.figure, self.image_frame)
        self.bal = self.figure.add_subplot()
        self.bal.plot()
        self.figure_canvas.get_tk_widget().grid(row=1, column=0, padx=20, pady=(10,10))
    
        # Set values
        self.progressbar.configure(mode="indeterminnate")
        self.progressbar.start() # Change when task starting
        self.appearance_mode_optionemenu.set("System")
        self.scaling_optionemenu.set("100%")

    
    # Functions
    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)



# start tkinter as own application and avoid contex-name error
if __name__ == "__main__":
    app = App()
    app.mainloop()
   


