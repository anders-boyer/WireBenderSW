
from tkinter import *
from tkinter import ttk, messagebox  # Import ttk for themed widgets
from tkinter import filedialog

from bender_gcode import benderGCode
from import_coords import importCoords
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from point_object import pointObject


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

        self.button_calculate_bends = Button(root, text="Calculate Bends", command=self.calculate_bends_popup, state="disabled")
        self.button_calculate_bends.grid(row=0, column=0, columnspan=3, padx=(15, 0), pady=2, sticky="nsew")

        self.codeLabel = Label(root, text="Bend Table")
        self.codeLabel.grid(row=1, column=0, padx=0, pady=0, sticky="sew", columnspan=3)

        self.collision_label = Label(root, text="")
        self.collision_label.grid(row=0, column=3, padx=0, pady=0, sticky="nsew")

        self.bend_table = ttk.Treeview(window, selectmode='browse')
        self.bend_table.grid(row=2, column=0, padx=(15, 0), pady=0, sticky="nsew", columnspan=2)
        self.scrollbar1 = Scrollbar(root)
        self.scrollbar1.grid(row=2, column=2, padx=0, pady=0, sticky="nsew")
        self.bend_table.config(yscrollcommand=self.scrollbar1.set)
        # setting scrollbar command parameter
        # to listbox.yview method its yview because
        # we need to have a vertical view
        self.scrollbar1.config(command=self.bend_table.yview)

        self.bend_table["columns"] = (
            "1", "2", "3", "4", "5")

        self.bend_table['show'] = 'headings'

        self.bend_table.column("1", width=2, anchor='c')
        self.bend_table.column("2", width=2, anchor='c')
        self.bend_table.column("3", width=2, anchor='c')
        self.bend_table.column("4", width=40, anchor='c')
        self.bend_table.column("5", width=2, anchor='c')


        self.bend_table.heading("1", text="Length (mm)")
        self.bend_table.heading("2", text="Rotation (degrees)")
        self.bend_table.heading("3", text="Desired Angle (degrees)")
        self.bend_table.heading("4", text="Angle + springback (degrees)")
        self.bend_table.heading("5", text="Motor Angle (degrees)")


        # self.bendbox = Listbox(root)#, width=20, height=30)
        # self.bendbox.grid(row=2, column=0, padx=15, pady=0, sticky="nsew", columnspan=2)
        # self.scrollbar1 = Scrollbar(root)
        # self.scrollbar1.grid(row=2, column=2, padx=0, pady=0, sticky="nsew")
        # # Insert elements into the listbox
        # # for values in range(100):
        # #     self.bendbox.insert(END, values)
        #     # Attaching Listbox to Scrollbar
        # # Since we need to have a vertical
        # # scroll we use yscrollcommand
        # self.bendbox.config(yscrollcommand=self.scrollbar1.set)
        # # setting scrollbar command parameter
        # # to listbox.yview method its yview because
        # # we need to have a vertical view
        # self.scrollbar1.config(command=self.bendbox.yview)

        self.codeLabel = Label(root, text="Point Cloud")
        self.codeLabel.grid(row=3, column=0, padx=0, pady=0, sticky="sew", columnspan=3)

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

        self.scrollbar2 = Scrollbar(root, command=yview)
        self.scrollbar2.grid(row=4, column=2, padx=0, pady=(0, 5), sticky="nsew")

        self.codebox.config(yscrollcommand=self.scrollbar2.set)
        self.linebox.config(yscrollcommand=self.scrollbar2.set)

        # Bind the mouse wheel event to the on_mousewheel function
        self.codebox.bind("<MouseWheel>", on_mousewheel)
        self.linebox.bind("<MouseWheel>", on_mousewheel)
        # setting scrollbar command parameter
        # to listbox.yview method its yview because
        # we need to have a vertical view
        # self.scrollbar2.config(command=self.codebox.yview)
        # self.scrollbar2.config(command=self.linebox.yview)

        # Create the plot area on the right side
        self.figure = Figure(dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, master=root)  # A tk.DrawingArea.
        self.canvas.get_tk_widget().grid(row=1, column=3, sticky="nsew", rowspan=4, padx=0, pady=0)

        self.gui = importCoords(self.figure, self.canvas)

        # Create menu bar
        self.menubar = Menu(root)

        # Create "File" menu
        self.file_menu = Menu(self.menubar, tearoff=0)
        self.file_menu.add_command(label="Import", command=self.show_import_popup)
        self.file_menu.add_command(label="Export G-Code", command=self.export_action, state="disabled")
        self.menubar.add_cascade(label="File", menu=self.file_menu)

        # Attach menu bar to the root window
        root.config(menu=self.menubar)

        i, j, k = [0], [0], [0]
        tempObj = pointObject(i, j, k)
        self.gui.plot3d(tempObj, "", True)

    def show_import_popup(self):
        # Create a Toplevel window (popup)
        import_popup = Toplevel()
        import_popup.title("Import Options")

        # Dropdown for file selection
        file_label = Label(import_popup, text="File Type:")
        file_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        file_options = ["TXT", "CSV"]  # Add more options if needed
        selected_file = StringVar()
        file_combobox = ttk.Combobox(import_popup, textvariable=selected_file, values=file_options)
        file_combobox.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        file_combobox.set(file_options[0])  # Set default selection

        # Checkbutton for straight section filtering
        straight_filter_var = IntVar()
        straight_filter_var.set(0)
        straight_filter_checkbox = Checkbutton(import_popup, text="Straight Section Filtering?", variable=straight_filter_var)
        straight_filter_checkbox.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        # Checkbutton for segment reordering
        reorder_var = IntVar()
        reorder_var.set(0)
        reorder_checkbox = Checkbutton(import_popup, text="Segment Reordering (did you use the provided SolidWorks macro?)", variable=reorder_var)
        reorder_checkbox.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        # Next button
        next_button = Button(import_popup, text="Next", command=lambda: self.import_next(import_popup, selected_file.get(), straight_filter_var.get(), reorder_var.get()))
        next_button.grid(row=3, column=0, columnspan=2, pady=10)

    def import_next(self, import_popup, file_type, straight_filter, reorder_option):
        # Handle the import options and close the popup
        # print("File Type:", file_type)
        # print("Straight Filter:", straight_filter)
        # print("Segment Reordering:", reorder_option)
        try:
            self.filename = self.gui.browse_files(reorder_option, straight_filter)
            self.gui.plot3d(self.gui.point_objects[0], self.filename, False)

            self.button_calculate_bends.config(text="Calculate Bends", command=self.calculate_bends_popup, state="normal")

            text_array = self.gui.print_csv()

            self.bend_table.delete(*self.bend_table.get_children())
            self.codebox.delete(0, END)
            self.gCodeString = []

            for i in range(0, len(text_array)-1):
                self.codebox.insert(END, f'   {text_array[i]}')
                self.linebox.insert(END, f'{i+1}   ')
        except:
            print("Import window closed")

        # Close the import popup
        import_popup.destroy()

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
                for line in self.gCodeString:
                    file.write(line + '\n')

            # Inform the user that the file has been saved
            messagebox.showinfo("Save Complete", f"File saved at:\n{file_path}")

    def calculate_bends_popup(self):

        # Create a Toplevel window (popup)
        calculate_bends_popup = Toplevel()
        calculate_bends_popup.title("Calculate Bends")

        # Dropdown for bend pin selection
        bend_pin_label = Label(calculate_bends_popup, text="Bend Pin Location:")
        bend_pin_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        pin_options = ["12 mm", "16.5 mm", "27.5 mm"]
        selected_pin = StringVar()
        file_combobox = ttk.Combobox(calculate_bends_popup, textvariable=selected_pin, values=pin_options)
        file_combobox.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        file_combobox.set(pin_options[1])  # Set default selection

        # Dropdown for material selection
        material_label = Label(calculate_bends_popup, text="Material:")
        material_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        material_options = ["spring steel", "stainless steel", "mild steel", "aluminum"]
        material_option = StringVar()
        file_combobox = ttk.Combobox(calculate_bends_popup, textvariable=material_option, values=material_options)
        file_combobox.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        file_combobox.set(material_options[0])  # Set default selection

        # Dropdown for diameter selection
        diameter_label = Label(calculate_bends_popup, text="Wire Diameter")
        diameter_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        diameter_options = ["0.5 mm", "0.75 mm", "1 mm", "1.5 mm", "2 mm", "3 mm"]
        diameter_option = StringVar()
        file_combobox = ttk.Combobox(calculate_bends_popup, textvariable=diameter_option, values=diameter_options)
        file_combobox.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        file_combobox.set(diameter_options[2])  # Set default selection

        # Checkbutton for straight section filtering
        orientation_var = IntVar()
        orientation_var.set(1)
        orientation_checkbox = Checkbutton(calculate_bends_popup, text="Show best orientation only (lowest collisions)",variable=orientation_var)
        orientation_checkbox.grid(row=3, column=0, padx=10, pady=5, sticky="w")

        # Next button
        next_button = Button(calculate_bends_popup, text="Next", command=lambda: self.calc_bends_next(calculate_bends_popup, selected_pin.get(), material_option.get(), diameter_option.get(), orientation_var.get()))
        next_button.grid(row=4, column=0, columnspan=2, pady=10)

    def calc_bends_next(self, calculate_bends_popup, pinPos, material, diameter, orientation):

        material = 1  # needs to be implemented

        diameter = float(diameter.split("mm")[0].strip())
        pinPos = float(pinPos.split("mm")[0].strip())

        self.gui.convert_coords(diameter, pinPos)
        self.button_calculate_bends.config(text="Next Plot", command=self.next)
        self.gui.calculate_bends(material, diameter, pinPos)
        self.collision_label.config(
            text=f'This orientation has {self.gui.point_objects[self.gui.plotIdx].collision_count} collisions'
                 f'and {self.gui.point_objects[self.gui.plotIdx].deleted_vertices} deleted vertices')


        if orientation == 1:
            min_collisions = 111111111111111
            min_idx = 4

            for i in range(0, len(self.gui.point_objects)):
                collision_count = self.gui.point_objects[self.gui.plotIdx].collision_count
                if collision_count < min_collisions:
                    min_collisions = collision_count
                    min_idx = i

            self.gui.plotIdx = min_idx

            self.gui.update_gui()
            self.collision_label.config(
                text=f'This orientation has {self.gui.point_objects[self.gui.plotIdx].collision_count} collisions'
                     f'and {self.gui.point_objects[self.gui.plotIdx].deleted_vertices} deleted vertices')

            self.button_calculate_bends.config(state="disabled")

        self.updateBendTable()
        self.updateCodeBox()
        self.codeLabel.config(text="G-Code")

        self.file_menu.entryconfig(1, state="normal")

        calculate_bends_popup.destroy()

    def next(self):
        self.gui.incrementIdx()
        self.updateCodeBox()
        self.gui.next()
        self.collision_label.config(
            text=f'This orientation has {self.gui.point_objects[self.gui.plotIdx].collision_count} collisions'
                 f'and {self.gui.point_objects[self.gui.plotIdx].deleted_vertices} deleted vertices')

        self.updateBendTable()

    def updateBendTable(self):
        self.bend_table.delete(*self.bend_table.get_children())
        # Insert LRA data into bend_table
        lra_data = self.gui.point_objects[self.gui.plotIdx].get_lra_data()
        for values in lra_data:
            self.bend_table.insert("", "end", values=values)

    def updateCodeBox(self):
        self.codebox.delete(0, END)
        self.linebox.delete(0, END)
        pointObject = self.gui.point_objects[self.gui.plotIdx]
        gCode = benderGCode(pointObject)
        self.gCodeString = gCode.generate_gcode()

        for elem in self.gCodeString:
            self.codebox.insert(END, elem)


if __name__ == "__main__":
    window = Tk()
    window.title('Wire Bender SW')
    window.geometry("1500x900")
    window.config(background="white")
    window.state('zoomed')

    # Initialize the GUIManager class
    gui_manager = GUI(window)

    window.mainloop()
