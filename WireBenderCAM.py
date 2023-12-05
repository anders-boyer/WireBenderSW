"""
This class contains the entry point to the software and contains methods for generating all GUI elements

Build:
    pyinstaller --onefile --noconsole --collect-data sv_ttk WireBenderCAM.py

Anderson Boyer
"""

import re
from tkinter import *
from tkinter import ttk, messagebox  # Import ttk for themed widgets
from tkinter import filedialog
from bender_gcode import BenderGCode
from import_coords import ImportCoords
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from point_object import PointObject
import sv_ttk


class GUI:
    def __init__(self, root):

        self.gCodeString = []
        self.root = root
        self.filename = ""

        Grid.rowconfigure(root, 0, weight=1)
        Grid.rowconfigure(root, 1, weight=1)
        Grid.rowconfigure(root, 2, weight=30)
        Grid.rowconfigure(root, 3, weight=1)
        Grid.rowconfigure(root, 4, weight=30)
        Grid.columnconfigure(root, 0, weight=1)
        Grid.columnconfigure(root, 1, weight=100)
        Grid.columnconfigure(root, 2, weight=1)
        Grid.columnconfigure(root, 3, weight=100)

        # Create & Configure frame
        frame = Frame(root)
        frame.grid(row=0, column=0, sticky=N + S + E + W)

        self.button_calculate_bends = ttk.Button(root, text="Calculate Bends", command=self.calculate_bends_popup,
                                                 state="disabled")
        self.button_calculate_bends.grid(row=0, column=0, columnspan=3, padx=(0, 0), pady=0, sticky="nsew")

        self.codeLabel = ttk.Label(root, text="Bend Table")
        self.codeLabel.grid(row=1, column=0, padx=(15, 0), pady=(10, 0), sticky="nsew", columnspan=3)
        self.codeLabel.configure(anchor='center')

        self.collision_label = ttk.Label(root, text="")
        self.collision_label.grid(row=0, column=3, padx=(0, 0), pady=0, sticky="nsew")
        self.collision_label.configure(anchor="center")

        self.bend_table = ttk.Treeview(window, selectmode='browse')
        self.bend_table.grid(row=2, column=0, padx=(15, 0), pady=0, sticky="nsew", columnspan=2)
        self.scrollbar1 = ttk.Scrollbar(root)
        self.scrollbar1.grid(row=2, column=2, padx=0, pady=0, sticky="nsew")
        self.bend_table.config(yscrollcommand=self.scrollbar1.set)

        self.scrollbar1.config(command=self.bend_table.yview)

        self.bend_table["columns"] = (
            "1", "2", "3", "4")

        self.bend_table['show'] = 'headings'

        self.bend_table.column("1", width=2, anchor='c')
        self.bend_table.column("2", width=2, anchor='c')
        self.bend_table.column("3", width=2, anchor='c')
        self.bend_table.column("4", width=2, anchor='c')

        self.bend_table.heading("1", text="Length (mm)")
        self.bend_table.heading("2", text="Rotation (degrees)")
        self.bend_table.heading("3", text="Desired Angle (degrees)")
        self.bend_table.heading("4", text="Motor Angle (degrees)")

        self.codeLabel = ttk.Label(root, text="Point Cloud")
        self.codeLabel.grid(row=3, column=0, padx=(15, 0), pady=(10, 0), sticky="nsew", columnspan=3)
        self.codeLabel.configure(anchor='center')

        def yview(*args):
            self.linebox.yview(*args)
            self.codebox.yview(*args)

        def on_mousewheel(event):
            # Update both listboxes when using the mouse wheel
            self.linebox.yview("scroll", -1 * (event.delta // 120), "units")
            self.codebox.yview("scroll", -1 * (event.delta // 120), "units")
            return "break"  # Prevent the default scrolling behavior

        self.linebox = Listbox(root, justify="right")  # , width=20, height=40)
        self.linebox.grid(row=4, column=0, padx=(15, 0), pady=(0, 5), sticky="nsew")

        self.codebox = Listbox(root)  # , width=20, height=40)
        self.codebox.grid(row=4, column=1, padx=(0, 0), pady=(0, 5), sticky="nsew")

        self.scrollbar2 = ttk.Scrollbar(root, command=yview)
        self.scrollbar2.grid(row=4, column=2, padx=0, pady=(0, 5), sticky="nsew")

        self.codebox.config(yscrollcommand=self.scrollbar2.set)
        self.linebox.config(yscrollcommand=self.scrollbar2.set)

        # Bind the mouse wheel event to the on_mousewheel function
        self.codebox.bind("<MouseWheel>", on_mousewheel)
        self.linebox.bind("<MouseWheel>", on_mousewheel)

        # Create the plot area on the right side
        self.figure = Figure(dpi=80, facecolor='#1e1e1e')  # Set the background color of the figure
        self.canvas = FigureCanvasTkAgg(self.figure, master=root)  # A tk.DrawingArea.
        self.canvas.get_tk_widget().grid(row=1, column=3, sticky="nsew", rowspan=4, padx=0, pady=0)

        self.coords = ImportCoords(self.figure, self.canvas)

        # Create menu bar
        self.menubar = Menu(root)

        # Create "File" menu
        self.file_menu = Menu(self.menubar, tearoff=0)
        self.file_menu.add_command(label="Import", command=self.import_next)
        self.file_menu.add_command(label="Export G-Code", command=self.export_action, state="disabled")
        self.menubar.add_cascade(label="File", menu=self.file_menu)

        # Attach menu bar to the root window
        root.config(menu=self.menubar)

        i, j, k = [0], [0], [0]
        temp_obj = PointObject(i, j, k)
        self.coords.plot3d(temp_obj, "", True)

    def import_next(self):

        self.filename = self.coords.browse_files()
        self.coords.plot3d(self.coords.point_objects[0], self.filename, False)

        self.button_calculate_bends.config(text="Calculate Bends", command=self.calculate_bends_popup, state="normal")

        text_array = self.coords.print_csv()

        self.bend_table.delete(*self.bend_table.get_children())
        self.codebox.delete(0, END)
        self.gCodeString = []

        for i in range(0, len(text_array)):
            self.codebox.insert(END, f'   {text_array[i]}')
            self.linebox.insert(END, f'{i+1}   ')

    def export_action(self):
        # Open a file dialog for saving the G-code file
        file_path = filedialog.asksaveasfilename(
            defaultextension=".gcode",
            filetypes=[("G-code", "*.gcode"), ("All files", "*.*")],
            initialfile=self.filename.split('.')[0]  # Use the default name without extension
        )

        # Check if a file path was chosen
        if file_path:
            # Save the G-code content to the chosen file
            with open(file_path, 'w') as file:
                for line1, line2 in zip(self.gCodeString[0], self.gCodeString[1]):
                    combined_line = f"{line1.ljust(20)}{line2}"  # Adjust the width (20 in this example) based on your needs
                    file.write(combined_line + '\n')

            # Inform the user that the file has been saved
            messagebox.showinfo("Save Complete", f"File saved at:\n{file_path}")

    def calculate_bends_popup(self):

        # Create a Toplevel window (popup)
        calculate_bends_popup = Toplevel()
        calculate_bends_popup.title("Calculate Bends")

        calculate_bends_popup.geometry("550x150")

        Grid.rowconfigure(calculate_bends_popup, 0, weight=1)
        Grid.rowconfigure(calculate_bends_popup, 1, weight=1)
        Grid.rowconfigure(calculate_bends_popup, 2, weight=1)
        Grid.columnconfigure(calculate_bends_popup, 0, weight=1)
        Grid.columnconfigure(calculate_bends_popup, 1, weight=1)

        # Dropdown for material and diameter selection
        material_label = ttk.Label(calculate_bends_popup, text="Material:")
        material_label.grid(row=0, column=0, padx=10, pady=10)
        material_options = ["1085 Steel - 1mm", "1085 Steel - 1.5mm",
                            "Galvanized Steel - 2mm", "Mild Steel - 3mm",
                            "Spring Steel - 3mm", "Mild Steel - 1/8 inch", "Custom - 12mm Pin",
                            "Custom - 16.5mm Pin", "Custom - 27.5mm Pin"]
        material_label.config(anchor='e')
        material_option = StringVar()
        file_combobox = ttk.Combobox(calculate_bends_popup, textvariable=material_option, values=material_options)
        file_combobox.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        file_combobox.set(material_options[0])  # Set default selection

        # Checkbutton for straight section filtering
        orientation_var = IntVar()
        orientation_var.set(1)
        orientation_checkbox = ttk.Checkbutton(
            calculate_bends_popup, text="Show best orientation only (lowest collisions)", variable=orientation_var)
        orientation_checkbox.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        # Next button
        next_button = ttk.Button(calculate_bends_popup, text="Next", command=lambda: self.calc_bends_next(
            calculate_bends_popup, material_option.get(), orientation_var.get()))
        next_button.grid(row=2, column=0, columnspan=2, pady=10)

    @staticmethod
    def custom_material_popup():
        def on_next_button():
            nonlocal filename, diameter  # Use nonlocal to modify outer variables

            filename = filedialog.askopenfilename(initialdir="/", title="Select a File",
                                                  filetypes=(("CSV files", "*.csv"), ("All files", "*.*")))
            diameter = float(entry_diameter.get())

            custom_material_popup.destroy()

        filename = None  # Initialize filename to None
        diameter = None  # Initialize pinPos to None

        custom_material_popup = Toplevel()
        custom_material_popup.title("Custom Material Diameter")
        custom_material_popup.geometry("400x120")

        Grid.rowconfigure(custom_material_popup, 0, weight=1)
        Grid.rowconfigure(custom_material_popup, 1, weight=1)
        Grid.rowconfigure(custom_material_popup, 2, weight=1)

        Grid.columnconfigure(custom_material_popup, 0, weight=1)
        Grid.columnconfigure(custom_material_popup, 1, weight=1)

        # Create labels and entry widget
        label_diameter = ttk.Label(custom_material_popup, text="Diameter:")
        entry_diameter = ttk.Entry(custom_material_popup)
        label_mm = ttk.Label(custom_material_popup, text="mm")

        # Pack labels and entry widget
        label_diameter.grid(row=0, column=0, padx=10, pady=5)
        entry_diameter.grid(row=0, column=1, padx=10, pady=5)
        label_mm.grid(row=0, column=2, padx=(0, 10), pady=5)

        # Create "Next" button
        next_button = ttk.Button(custom_material_popup, text="Import CSV", command=on_next_button)
        next_button.grid(row=1, column=0, columnspan=3, pady=10)

        custom_material_popup.wait_window()  # Wait for the popup to be closed

        return filename, diameter

    @staticmethod
    def warning_popup(message):
        messagebox.showwarning("Warning", message)

    def calc_bends_next(self, calculate_bends_popup, material_string, orientation):

        if ((material_string == "Custom - 12mm Pin") or (material_string == "Custom - 16.5mm Pin") or
                (material_string == "Custom - 27.5mm Pin")):
            calculate_bends_popup.destroy()

            material_file, diameter = self.custom_material_popup()

            if material_string == "Custom - 12mm Pin":
                pin_pos = 12.0
            elif material_string == "Custom - 16.5mm Pin":
                pin_pos = 16.5
            else:
                pin_pos = 27.5

            if (pin_pos < 12.1) & (diameter > 2.6):
                self.warning_popup("You must use the 16.5 mm pin with this diameter!\nSelection has been changed.")
                pin_pos = 16.5
        else:
            calculate_bends_popup.destroy()

            # Create a dictionary for the string to filename mapping
            string_to_file_map = {
                "1085 Steel - 1mm": "1085 Steel - 1mm.csv",
                "1085 Steel - 1.5mm": "1085 Steel - 1_5mm.csv",
                "Galvanized Steel - 2mm": "Galvanized Steel - 2mm.csv",
                "Mild Steel - 3mm": "Mild Steel - 3mm.csv",
                "Spring Steel - 3mm": "Spring Steel - 3mm.csv",
                "Mild Steel - 1/8 inch": "1_8in Mild Steel.csv"
            }

            material_file = string_to_file_map.get(material_string)
            if material_file is not None:
                print(f"The filename for key '{material_string}' is '{material_file}'")
            else:
                print(f"No filename found for key '{material_string}'")

            if material_string == "Mild Steel - 1/8 inch":
                diameter = 3.175
            else:
                diameter = float(re.search(r"(\d+(\.\d+)?)\s*mm", material_string).group(1))

            string_to_pin_map = {
                "1085 Steel - 1mm": 12.0,
                "1085 Steel - 1.5mm": 12.0,
                "Galvanized Steel - 2mm": 12.0,
                "Mild Steel - 3mm": 16.5,
                "Spring Steel - 3mm": 27.5,
                "Mild Steel - 1/8 inch": 16.5
            }

            pin_pos = string_to_pin_map.get(material_string)

        self.coords.convert_coords(diameter, pin_pos)
        self.button_calculate_bends.config(text="Next Plot", command=self.next)
        self.coords.calculate_bends(material_file, diameter)
        self.collision_label.config(
            text=f'This orientation has {self.coords.point_objects[self.coords.plotIdx].collision_count} collisions'
                 f' and {self.coords.point_objects[self.coords.plotIdx].deleted_vertices} deleted vertices')

        if orientation == 1:
            min_collisions = 111111111111111
            min_idx = 4

            for i in range(0, len(self.coords.point_objects)):
                collision_count = self.coords.point_objects[self.coords.plotIdx].collision_count
                if collision_count < min_collisions:
                    min_collisions = collision_count
                    min_idx = i

            self.coords.plotIdx = min_idx

            self.coords.update_gui()
            self.collision_label.config(
                text=f'This orientation has {self.coords.point_objects[self.coords.plotIdx].collision_count} collisions'
                     f' and {self.coords.point_objects[self.coords.plotIdx].deleted_vertices} deleted vertices')

            self.button_calculate_bends.config(state="disabled")

        self.update_bend_table()
        self.update_code_box()
        self.codeLabel.config(text="G-Code")
        self.file_menu.entryconfig(1, state="normal")

        self.warning_popup(f'IMPORTANT:\n\nFor proper operation and to prevent collisions with the machine, '
                           f'you MUST use the\n\n{round(pin_pos, 1)} mm Pin\n\nPlease see the documentation '
                           f'if this is unclear')

    def next(self):
        # increment IDX
        if self.coords.plotIdx >= 3:
            self.coords.plotIdx = 0
        else:
            self.coords.plotIdx += 1
        self.update_code_box()
        self.coords.update_gui()
        self.collision_label.config(
            text=f'This orientation has {self.coords.point_objects[self.coords.plotIdx].collision_count} collisions'
                 f' and {self.coords.point_objects[self.coords.plotIdx].deleted_vertices} deleted vertices')

        self.update_bend_table()

    def update_bend_table(self):
        self.bend_table.delete(*self.bend_table.get_children())
        # Insert LRA data into bend_table
        lra_data = self.coords.point_objects[self.coords.plotIdx].get_lra_data()
        for values in lra_data:
            self.bend_table.insert("", "end", values=values)

    def update_code_box(self):
        self.codebox.delete(0, END)
        self.linebox.delete(0, END)
        point_object = self.coords.point_objects[self.coords.plotIdx]
        gcode = BenderGCode(point_object)
        self.gCodeString = gcode.generate_gcode()

        def tabify(s, tabsize=40):
            return s.ljust(tabsize-len(s))

        for i in range(len(self.gCodeString[0])):
            self.codebox.insert(END, f'  {tabify(self.gCodeString[0][i])}{self.gCodeString[1][i]}')
            self.linebox.insert(END, f'{i + 1}   ')


if __name__ == "__main__":
    window = Tk()
    window.title('Wire Bender SW')
    window.geometry("1500x900")
    window.state('zoomed')

    sv_ttk.set_theme("dark")

    # Initialize the GUIManager class
    gui = GUI(window)

    window.mainloop()
