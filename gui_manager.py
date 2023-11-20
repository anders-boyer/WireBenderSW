# gui_manager.py

from tkinter import *
from tkinter import ttk  # Import ttk for themed widgets
from gui import GUI
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from point_object import PointObject

class GUIManager:
    def __init__(self, root):

        self.root = root
        Grid.rowconfigure(root, 0, weight=1)
        Grid.rowconfigure(root, 1, weight=1)
        Grid.rowconfigure(root, 2, weight=30)
        Grid.rowconfigure(root, 3, weight=1)
        Grid.rowconfigure(root, 4, weight=30)
        Grid.columnconfigure(root, 0, weight=80)
        Grid.columnconfigure(root, 1, weight=80)
        Grid.columnconfigure(root, 2, weight=1)
        Grid.columnconfigure(root, 3, weight=100)

        # Create & Configure frame
        frame = Frame(root)
        frame.grid(row=0, column=0, sticky=N + S + E + W)

        self.button_calculate_bends = Button(root, text="Calculate Bends", command=self.calculate_bends_popup, state="disabled")
        self.button_calculate_bends.grid(row=0, column=0, columnspan=2, padx=15, pady=2, sticky="nsew")

        self.top_label = Label(root, text="Bend Table")
        self.top_label.grid(row=1, column=0, padx=0, pady=0, sticky="sew", columnspan=3)

        self.collision_label = Label(root, text="")
        self.collision_label.grid(row=0, column=3, padx=0, pady=0, sticky="nsew")

        self.bend_table = ttk.Treeview(window, selectmode='browse')
        self.bend_table.grid(row=2, column=0, padx=15, pady=0, sticky="nsew", columnspan=2)
        self.scrollbar1 = Scrollbar(root)
        self.scrollbar1.grid(row=2, column=2, padx=0, pady=5, sticky="nsew")
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

        self.top_label = Label(root, text="Point Cloud")
        self.top_label.grid(row=3, column=0, padx=0, pady=0, sticky="sew", columnspan=3)

        self.codebox = Listbox(root)#, width=20, height=40)
        self.codebox.grid(row=4, column=0, padx=15, pady=5, sticky="nsew", columnspan=2)
        self.scrollbar2 = Scrollbar(root)
        self.scrollbar2.grid(row=4, column=2, padx=0, pady=5, sticky="nsew")
        # Insert elements into the listbox
        # for values in range(100):
        #     self.codebox.insert(END, values)
            # Attaching Listbox to Scrollbar
        # Since we need to have a vertical
        # scroll we use yscrollcommand
        self.codebox.config(yscrollcommand=self.scrollbar2.set)
        # setting scrollbar command parameter
        # to listbox.yview method its yview because
        # we need to have a vertical view
        self.scrollbar2.config(command=self.codebox.yview)

        # Create the plot area on the right side
        self.figure = Figure(dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, master=root)  # A tk.DrawingArea.
        self.canvas.get_tk_widget().grid(row=1, column=3, sticky="nsew", rowspan=4, padx=0, pady=0)

        # Initialize the GUI class from the gui.py file
        self.gui = GUI(self.figure, self.canvas)

        # Create menu bar
        menubar = Menu(root)

        # Create "File" menu
        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="Import", command=self.show_import_popup)
        file_menu.add_command(label="Export G-Code", command=self.export_action, state="disabled")
        menubar.add_cascade(label="File", menu=file_menu)

        # Attach menu bar to the root window
        root.config(menu=menubar)

        i, j, k = [0], [0], [0]
        tempObj = PointObject(i, j, k)
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
        straight_filter_var.set(1)
        straight_filter_checkbox = Checkbutton(import_popup, text="Straight Section Filtering?", variable=straight_filter_var)
        straight_filter_checkbox.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        # Checkbutton for segment reordering
        reorder_var = IntVar()
        reorder_var.set(1)
        reorder_checkbox = Checkbutton(import_popup, text="Segment Reordering (did you use the provided SolidWorks macro?)", variable=reorder_var)
        reorder_checkbox.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        # Next button
        next_button = Button(import_popup, text="Next", command=lambda: self.import_next(import_popup, selected_file.get(), straight_filter_var.get(), reorder_var.get()))
        next_button.grid(row=3, column=0, columnspan=2, pady=10)

    def import_next(self, import_popup, file_type, straight_filter, reorder_option):
        # Handle the import options and close the popup
        print("File Type:", file_type)
        print("Straight Filter:", straight_filter)
        print("Segment Reordering:", reorder_option)

        filename = self.gui.browse_files(reorder_option, straight_filter)
        self.gui.plot3d(self.gui.point_objects[0], filename, False)

        text_array = self.gui.print_csv()

        self.bend_table.delete(*self.bend_table.get_children())
        self.codebox.delete(0, END)
        for elem in text_array:
            self.codebox.insert(END, elem)

        self.button_calculate_bends['state'] = NORMAL

        # Close the import popup
        import_popup.destroy()

    def export_action(self):
        # Implement your export action here
        print("Export action")

    def calculate_bends_popup(self):

        # Create a Toplevel window (popup)
        calculate_bends_popup = Toplevel()
        calculate_bends_popup.title("Calculate Bends")

        # Dropdown for bend pin selection
        bend_pin_label = Label(calculate_bends_popup, text="Bend Pin Location:")
        bend_pin_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        pin_options = ["6 mm", "10 mm", "14 mm"]
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
        diameter_options = ["0.5 mm", "0.75 mm", "1 mm", "1.5 mm", "2 mm"]
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

    def calc_bends_next(self, calculate_bends_popup, pin, material, diameter, orientation):

        self.gui.convert_coords()
        self.button_calculate_bends.config(text="Next Plot", command=self.next)
        self.gui.calculate_bends()
        self.collision_label.config(
            text=f'This orientation has {self.gui.point_objects[self.gui.plotIdx].collision_count} collisions')

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
                text=f'This orientation has {self.gui.point_objects[self.gui.plotIdx].collision_count} collisions')

            self.button_calculate_bends.config(state="disabled")

        # Insert LRA data into bend_table
        lra_data = self.gui.point_objects[self.gui.plotIdx].get_lra_data()
        for values in lra_data:
            self.bend_table.insert("", "end", values=values)

        self.gui.incrementIdx()
        calculate_bends_popup.destroy()

    def next(self):
        self.gui.next()
        self.collision_label.config(
            text=f'This orientation has {self.gui.point_objects[self.gui.plotIdx].collision_count} collisions')

        # Insert LRA data into bend_table
        # Insert LRA data into bend_table
        lra_data = self.gui.point_objects[self.gui.plotIdx].get_lra_data()
        for values in lra_data:
            self.bend_table.insert("", "end", values=values)
        self.gui.incrementIdx()


if __name__ == "__main__":
    window = Tk()
    window.title('Wire Bender SW')
    window.geometry("1500x900")
    window.config(background="white")
    window.state('zoomed')

    # Initialize the GUIManager class
    gui_manager = GUIManager(window)

    window.mainloop()
