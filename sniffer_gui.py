import time
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import DateEntry
import psycopg2
from datetime import datetime
import re
import os

ip_adr = "xxxxxxxx"
usr_nm = 'xxxxxxxxxx'
passwd = 'xxxxxxxx'
database_nm = 'xxxxxxxxxx'
db_port = 'xxxxx'


root = Tk()
root.tk.call('wm', 'iconphoto', root._w, PhotoImage(file=os.path.dirname(os.path.abspath(__file__)) + '/1.png'))
root.title('Sniffer database')
root.geometry("1500x600")
root.resizable(width=False, height=False)


query_order_state = -1


def query_order_selector():
    s = ";"
    if query_order_state == 0:
        s = "ORDER BY MAC ASC;"
    elif query_order_state == 1:
        s = "ORDER BY MAC DESC;"
    elif query_order_state == 2:
        s = "ORDER BY current_config ASC;"
    elif query_order_state == 3:
        s = "ORDER BY current_config DESC;"
    elif query_order_state == 4:
            s = "ORDER BY desirable_config ASC;"
    elif query_order_state == 5:
        s = "ORDER BY desirable_config DESC;"
    elif query_order_state == 6:
        s = "ORDER BY reconfigured ASC;"
    elif query_order_state == 7:
        s = "ORDER BY reconfigured DESC;"
    elif query_order_state == 8:
        s = "ORDER BY reconfig_ts ASC;"
    elif query_order_state == 9:
        s = "ORDER BY reconfig_ts DESC;"
    elif query_order_state == 10:
        s = "ORDER BY last_ts ASC;"
    elif query_order_state == 11:
        s = "ORDER BY last_ts DESC;"
    elif query_order_state == 12:
        s = "ORDER BY NAS_ID ASC;"
    elif query_order_state == 13:
        s = "ORDER BY NAS_ID DESC;"
    elif query_order_state == 14:
        s = "ORDER BY IP ASC;"
    elif query_order_state == 15:
        s = "ORDER BY IP DESC;"
    else:
        s = ";"
    return s


def query_database():
    selected = my_tree.focus()
    selected_mac = "mac"
    if selected:
        value = my_tree.item(selected, 'values')
        selected_mac = value[0]
    selection_after_update = 0

    with psycopg2.connect(user=usr_nm, password=passwd, host=ip_adr, port=db_port,
                          dbname=database_nm) as db:
        mac_search_entry = entry_search_mac.get()
        selections = []
        cursor = db.cursor()
        flag = False
        if not var.get():
            cursor.execute("SELECT * FROM reconfig " + query_order_selector())
            records = cursor.fetchall()
            my_tree.delete(*my_tree.get_children())
        elif var.get() is True and entry_search_mac.get() != 'Enter required MAC address...' \
                and entry_search_mac.get() != '':

            mac_search_entry = entry_search_mac.get()
            cursor.execute("""SELECT * FROM reconfig WHERE mac::varchar LIKE %s""" + query_order_selector(),
                           ('%' + mac_search_entry + '%',))
            records = cursor.fetchall()
            flag = True
            try:
                my_tree.delete(*my_tree.get_children())
            except Exception:
                pass
        else:
            cursor.execute("SELECT * FROM reconfig " + query_order_selector())
            records = cursor.fetchall()
            my_tree.delete(*my_tree.get_children())

        try:
            count = 0
            false_count = 0
            for record in records:

                if record[0] == mac_search_entry and flag is True:
                    selections.append(record)
                if record[0] == selected_mac:
                    selection_after_update = count

                if not record[3]:
                    false_count += 1
                if count % 2 == 0:
                    my_tree.insert(parent='', index='end', iid=count, text='',
                                   values=record,
                                   tags=('evenrow',))
                else:
                    my_tree.insert(parent='', index='end', iid=count, text='',
                                   values=record,
                                   tags=('oddrow',))
                count += 1

            reconf_all["text"] = "Not configured {:d} of {:d}".format(false_count, count)
        except Exception:
            pass

    try:
        my_tree.focus(selection_after_update)
        my_tree.selection_set(selection_after_update)
    except Exception:
        pass


def new_closing():
    msgbox = messagebox.askquestion(
        "Confirmation window", "Are you sure you want to close this window?"
    )
    if msgbox == "yes":
        search.destroy()
    else:
        pass


def new_update_window():
    global search_entry, search, new_mac_entry, new_des_conf_entry, new_conf_entry, new_n_id_entry

    search = Toplevel(root)
    search.title("Update Row")
    search.geometry("400x700")
    search.resizable(width=False, height=False)

    search.wait_visibility()
    search.grab_set()
    search.focus_set()

    search_frame = LabelFrame(search, text="Required data")
    search_frame.pack(padx=10, pady=10)

    new_mac = Label(search_frame, text='mac')
    new_mac.pack(pady=20, padx=20)
    new_mac_entry = Entry(search_frame, font=("Helvetica", 15), state='readonly')
    new_mac_entry.pack(pady=20, padx=20)

    new_des_conf = Label(search_frame, text='des_conf')
    new_des_conf.pack(pady=20, padx=20)
    new_des_conf_entry = Entry(search_frame, font=("Helvetica", 15))
    new_des_conf_entry.pack(pady=20, padx=20)

    new_conf = Label(search_frame, text='conf')
    new_conf.pack(pady=20, padx=20)
    items_new_reconf = ['True', 'False']
    new_conf_entry = ttk.Combobox(search_frame, font=("Helvetica", 15), values=items_new_reconf)
    new_conf_entry.pack(pady=20, padx=20)

    new_n_id = Label(search_frame, text='nas_id')
    new_n_id.pack(pady=20, padx=20)
    new_n_id_entry = Entry(search_frame, font=("Helvetica", 15))
    new_n_id_entry.pack(pady=20, padx=20)

    search_button = Button(search, text="Paste Changed Values", command=insert_update_line)
    search_button.pack(padx=20, pady=20)


style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview", relief="flat", background="#fff", foreground="black", fieldbackgroubd="#D3D3D3",
                rowheight=25)
style.map("Treeview", background=[("selected", "green")])

tree_frame = Frame(root)
tree_frame.pack(pady=10)

tree_scroll = Scrollbar(tree_frame)
tree_scroll.pack(side=RIGHT, fill=Y)

my_tree = ttk.Treeview(tree_frame, yscrollcommand=tree_scroll.set, selectmode="extended")


def after_update():
    query_database()
    my_tree.after(15000, after_update)


my_tree.pack()
tree_scroll.config(command=my_tree.yview)
columns = ("Mac-address", "current_config", "desirable_config", "reconfigured", "reconfig_ts",
           "last_ts", "NAS_ID", "IP")

my_tree['columns'] = columns
my_tree.column("#0", width=0, stretch=NO)
my_tree.column("Mac-address", anchor=W, width=100)
my_tree.column("current_config", anchor=W, width=400)
my_tree.column("desirable_config", anchor=CENTER, width=400)
my_tree.column("reconfigured", anchor=CENTER, width=90)
my_tree.column("reconfig_ts", anchor=CENTER, width=130)
my_tree.column("last_ts", anchor=CENTER, width=130)
my_tree.column("NAS_ID", anchor=CENTER, width=100)
my_tree.column("IP", anchor=CENTER, width=100)

my_tree.heading("#0", text="", anchor=W)
my_tree.heading("Mac-address", text="Mac-address", anchor=W)
my_tree.heading("current_config", text="current_config", anchor=W)
my_tree.heading("desirable_config", text="desirable_config", anchor=CENTER)
my_tree.heading("reconfigured", text="reconfigured", anchor=CENTER)
my_tree.heading("reconfig_ts", text="reconfig_ts", anchor=CENTER)
my_tree.heading("last_ts", text="last_ts", anchor=CENTER)
my_tree.heading("NAS_ID", text="NAS_ID", anchor=CENTER)
my_tree.heading("IP", text="IP", anchor=CENTER)
my_tree.pack()

columns = ("Mac-address", "current_config", "desirable_config", "reconfigured", "reconfig_ts",
           "last_ts", "NAS_ID", "IP")

for col in columns:
    my_tree.heading(col, text=col, command=lambda _col=col: treeview_sort_column(my_tree, _col))


def treeview_sort_column(tv, col):
    global query_order_state
    if 2 * columns.index(col) == query_order_state:
        query_order_state += 1
    else:
        query_order_state = 2 * columns.index(col)
    query_database()
    for c in columns:
        tv.heading(c, text=c)
    if query_order_state % 2:
        tv.heading(col, text=col + "▼")
    else:
        tv.heading(col, text=col + "▲")


my_tree.tag_configure('oddrow', background='white')
my_tree.tag_configure('evenrow', background='lightblue')

data_frame = LabelFrame(root, text="Record")
data_frame.pack(fill="x", padx=20)

mac_label = Label(data_frame, text="Mac-address")
mac_label.grid(row=0, column=0, padx=10, pady=10)
mac_entry = Entry(data_frame)
mac_entry.grid(row=0, column=1, padx=10, pady=10)

curr_conf_label = Label(data_frame, text="current_config")
curr_conf_label.grid(row=0, column=2, padx=10, pady=10)
curr_conf_entry = Entry(data_frame)
curr_conf_entry.grid(row=0, column=3, padx=10, pady=10, ipadx=40)

des_conf_label = Label(data_frame, text="desirable_config")
des_conf_label.grid(row=0, column=4, padx=10, pady=10)
des_conf_entry = Entry(data_frame)
des_conf_entry.grid(row=0, column=5, padx=10, pady=10, ipadx=40)

item_reconf = ['True', 'False']
reconf_label = Label(data_frame, text="reconfigured")
reconf_label.grid(row=0, column=6, padx=10, pady=10)
reconf_entry = ttk.Combobox(data_frame, values=item_reconf)
reconf_entry.grid(row=0, column=7, padx=10, pady=10)
reconf_entry['state'] = 'readonly'

reconf_ts_label = Label(data_frame, text="reconfig_ts")
reconf_ts_label.grid(row=1, column=0, padx=10, pady=10)
reconf_ts_entry = DateEntry(data_frame, foreground="black", normalforeground="black",
                            selectforeground="red", background="white",
                            date_pattern="YYYY-mm-dd " + str(datetime.now().time()))
reconf_ts_entry.grid(row=1, column=1, padx=10, pady=10, ipadx=16)

last_ts_label = Label(data_frame, text="last_ts")
last_ts_label.grid(row=1, column=2, padx=10, pady=10)
last_ts_entry = DateEntry(data_frame, foreground="black", normalforeground="black",
                          selectforeground="red", background="white",
                          date_pattern="YYYY-mm-dd " + str(datetime.now().time()))
last_ts_entry.grid(row=1, column=3, padx=10, pady=10, ipadx=16)

n_id_label = Label(data_frame, text="NAS_ID")
n_id_label.grid(row=1, column=4, padx=10, pady=10)
n_id_entry = Entry(data_frame)
n_id_entry.grid(row=1, column=5, padx=10, pady=10)

ip_label = Label(data_frame, text="IP")
ip_label.grid(row=1, column=6, padx=10, pady=10)


def validate_ip(P):
    test = re.compile('(^\d{0,3}$|^\d{1,3}\.\d{0,3}$|^\d{1,3}\.\d{1,3}\.\d{0,3}$|^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{0,3}$)')
    if test.match(P):
        return True
    else:
        return False


ip_entry = Entry(data_frame, validate="key", validatecommand=(data_frame.register(validate_ip), '%P'))
ip_entry.grid(row=1, column=7, padx=10, pady=10)


def add_record():
    msgbox = messagebox.askquestion(
        "STOP", "Are you sure you want to add this line?"
    )
    if msgbox == "no":
        return False
    else:
        pass
    with psycopg2.connect(user=usr_nm, password=passwd, host=ip_adr, port=db_port,
                          dbname=database_nm) as db:
        cursor_add = db.cursor()

        q = """INSERT INTO reconfig VALUES ('{:s}', \
        '{:s}', \
        '{:s}', \
        '{:s}', \
        '{:s}', \
        '{:s}', \
        '{:s}', \
        '{:s}');""".format(mac_entry.get(), curr_conf_entry.get(), des_conf_entry.get(),
                           reconf_entry.get(), reconf_ts_entry.get(), last_ts_entry.get(), n_id_entry.get(),
                           ip_entry.get())
        try:
            cursor_add.execute(q)
            db.commit()
            my_tree.delete(*my_tree.get_children())
            query_database()
            mac_entry.delete(0, END)
            curr_conf_entry.delete(0, END)
            des_conf_entry.delete(0, END)
            reconf_entry.delete(0, END)
            reconf_ts_entry.delete(0, END)
            last_ts_entry.delete(0, END)
            n_id_entry.delete(0, END)
            ip_entry.delete(0, END)

        except Exception:
            messagebox.showerror("Error", "Invalid value entered")

    return True


add_new_line_button = Button(data_frame, text="Add new line", command=add_record)
add_new_line_button.grid(row=0, rowspan=2, column=8, columnspan=2, padx=10, pady=10, ipady=4, ipadx=4)

reconf_frame = LabelFrame(root, text="Text")
reconf_frame.pack(fill="x", padx=20)

reconf_all = Label(reconf_frame, height=3, width=25, background="#aaa")
reconf_all.grid(row=0, rowspan=2, column=10, columnspan=2, padx=20, pady=10, ipadx=2, ipady=2)

var = BooleanVar()
var.set(True)
search_mac = Checkbutton(reconf_frame, text="Search for the specified MAC address", variable=var,
                         command=query_database, )
search_mac.grid(row=0, column=14, columnspan=2, padx=20, pady=0, ipadx=2, ipady=2)


def on_entry_click(event):
    if entry_search_mac.get() == 'Enter required MAC address...':
        entry_search_mac.delete(0, "end")
        entry_search_mac.insert(0, '')
        entry_search_mac.config(fg='black')


def on_focusout(event):
    if entry_search_mac.get() == '':
        entry_search_mac.insert(0, 'Enter required MAC address...')
        entry_search_mac.config(fg='grey')


entry_search_mac = Entry(reconf_frame)
entry_search_mac.grid(row=1, column=14, columnspan=2, padx=0, pady=0, ipadx=20, ipady=2)

entry_search_mac.insert(0, 'Enter required MAC address...')
entry_search_mac.bind('<FocusIn>', on_entry_click)
entry_search_mac.bind('<FocusOut>', on_focusout)
entry_search_mac.config(fg='grey')


def key_button(e=None):

    if var.get() is True and entry_search_mac.get() != 'Enter required MAC address...' \
            and entry_search_mac.get() != '':
        query_database()

    elif var.get() is True and entry_search_mac.get() == '':
        query_database()
    else:
        pass


entry_search_mac.bind('<Return>', key_button)


def entry_default_values():
    msgbox = messagebox.askquestion(
        "STOP", "Are you sure you want to paste the default values?"
    )
    if msgbox == "no":
        return False
    else:
        pass
    with psycopg2.connect(user=usr_nm, password=passwd, host=ip_adr, port=db_port,
                          dbname=database_nm) as db:

        cursor_default = db.cursor()

        q = """INSERT INTO reconfig (MAC, current_config, desirable_config, reconfigured, reconfig_ts, last_ts, NAS_ID, IP)
        SELECT 'ad-af-14-51-cc-01', '+NAS_ID=TEST_UID+ZSRV=\"10.156.22.33\"+DSRV=\"10.156.22.33\"+REPI=30', 
        '+NAS_ID=TEST_UID+ZSRV=\"10.156.22.33\"+DSRV=\"10.156.22.33\"+REPI=30', TRUE, '2022-01-19 10:12:00', \
        '{2022-04-19 19:00:01}', 'TEST_UID', '172.16.1.4'
         WHERE NOT EXISTS (SELECT mac FROM reconfig WHERE mac = 'ad-af-14-51-cc-01');"""
        cursor_default.execute(q)

        q = """INSERT INTO reconfig(mac, current_config, desirable_config, reconfigured, reconfig_ts, last_ts, nas_id, ip)
                    SELECT '08-00-2b-01-02-03', '+NAS_ID=TEST_UID+ZSRV=\"10.156.22.33\"+DSRV=\"10.156.22.33\"+REPI=30',
                    '+NAS_ID=IN_TESTS+ZSRV=\"10.156.22.33\"+DSRV=\"10.156.12.48\"+REPI=30', FALSE,
                    '2022-01-19 09:21:00', '2022-04-19 19:11:01', 'IN_TESTS', '172.16.1.5'
                    WHERE NOT EXISTS (SELECT mac FROM reconfig WHERE mac = '08-00-2b-01-02-03');"""
        cursor_default.execute(q)
        db.commit()
        my_tree.delete(*my_tree.get_children())
        query_database()

    return True


def remove_one():
    msgbox = messagebox.askquestion(
        "STOP", "Are you sure you want to delete this line?"
    )
    if msgbox == "no":
        return False
    else:
        pass

    with psycopg2.connect(user=usr_nm, password=passwd, host=ip_adr, port=db_port,
                          dbname=database_nm) as db:

        cursor_remove = db.cursor()
        cursor_remove.execute("""DELETE from reconfig WHERE MAC= '{:s}'""".format(mac_entry.get()))
        db.commit()
        my_tree.delete(*my_tree.get_children())
        query_database()
        clear_entries()
        messagebox.showinfo("Deleted!", "Your Record Has Been Deleted!")

    return True


def insert_update_line():
    msgbox = messagebox.askquestion(
        "STOP", "Are you sure you want to paste these values?"
    )
    if msgbox == "no":
        return False
    else:
        pass

    des_conf = new_des_conf_entry.get()
    mac_addr = new_mac_entry.get()
    reconf = new_conf_entry.get()
    n_id = new_n_id_entry.get()

    with psycopg2.connect(user=usr_nm, password=passwd, host=ip_adr, port=db_port,
                          dbname=database_nm) as db:
        try:
            cursor_insert = db.cursor()
            if des_conf:
                q = "UPDATE reconfig SET desirable_config = '{:s}' WHERE MAC = '{:s}';".format(
                    des_conf, mac_addr
                )
                cursor_insert.execute(q)
            if reconf is not None:
                q = "UPDATE reconfig SET reconfigured = '{:s}' WHERE MAC = '{:s}';".format(
                    reconf, mac_addr
                )
                cursor_insert.execute(q)
            if n_id is not None:
                q = "UPDATE reconfig SET nas_id = '{:s}' WHERE MAC = '{:s}';".format(
                    n_id, mac_addr
                )

                cursor_insert.execute(q)
                db.commit()
                my_tree.delete(*my_tree.get_children())
                query_database()
                mac_entry.delete(0, END)
                curr_conf_entry.delete(0, END)
                des_conf_entry.delete(0, END)
                reconf_entry.delete(0, END)
                reconf_ts_entry.delete(0, END)
                last_ts_entry.delete(0, END)
                n_id_entry.delete(0, END)
                ip_entry.delete(0, END)
                search.destroy()

        except Exception:
            messagebox.showerror("Error", "Invalid value entered")
    return True


def clear_entries():
    reconf_entry['state'] = 'normal'
    mac_entry.delete(0, END)
    curr_conf_entry.delete(0, END)
    des_conf_entry.delete(0, END)
    reconf_entry.delete(0, END)
    reconf_ts_entry.delete(0, END)
    last_ts_entry.delete(0, END)
    n_id_entry.delete(0, END)
    ip_entry.delete(0, END)


def select_double_record(e):
    clear_entries()
    try:
        selected = my_tree.focus()
        values = my_tree.item(selected, 'values')
        new_update_window()
        new_mac_entry["state"] = 'normal'
        new_mac_entry.insert(0, values[0])
        new_mac_entry["state"] = 'readonly'
        new_des_conf_entry.insert(0, values[2])
        new_conf_entry["state"] = 'normal'
        new_conf_entry.insert(0, values[3])
        new_conf_entry["state"] = 'readonly'
        new_n_id_entry.insert(0, values[6])
        reconf_entry['state'] = 'readonly'

    except IndexError:
        search.destroy()
        reconf_entry['state'] = 'readonly'


def select_record(e):
    clear_entries()
    try:
        selected = my_tree.focus()
        values = my_tree.item(selected, 'values')

        mac_entry.insert(0, values[0])
        curr_conf_entry.insert(0, values[1])
        des_conf_entry.insert(0, values[2])
        reconf_entry.insert(0, values[3])
        reconf_entry['state'] = 'readonly'
        reconf_ts_entry.insert(0, values[4])
        last_ts_entry.insert(0, values[5])
        n_id_entry.insert(0, values[6])
        ip_entry.insert(0, values[7])

    except IndexError:
        reconf_entry['state'] = 'readonly'


def change_on_true():
    msgbox = messagebox.askquestion(
        "STOP", "Are you sure  you want to change the reconfigured column to 'TRUE'?"
    )
    if msgbox == "no":
        return False
    else:
        pass
    with psycopg2.connect(user=usr_nm, password=passwd, host=ip_adr, port=db_port,
                          dbname=database_nm) as db:
        cursor_true = db.cursor()
        q = """UPDATE reconfig SET reconfigured='true' WHERE reconfigured='false'"""
        cursor_true.execute(q)
        db.commit()
        success_change_t = True
    return success_change_t


def entry_change_on_true():
    if change_on_true():
        query_database()


def change_on_false():
    msgbox = messagebox.askquestion(
        "STOP", "Do you want to change the reconfigured column to 'FALSE'?"
    )
    if msgbox == "no":
        return False
    else:
        pass
    with psycopg2.connect(user=usr_nm, password=passwd, host=ip_adr, port=db_port,
                          dbname=database_nm) as db:
        cursor_on_false = db.cursor()
        q = """UPDATE reconfig SET reconfigured='false' WHERE reconfigured='true'"""
        cursor_on_false.execute(q)
        db.commit()
        success_change_f = True
    return success_change_f


def entry_change_on_false():
    if change_on_false():
        query_database()


def create_table_again():
    msgbox = messagebox.askquestion(
        "STOP", "Are you sure you want to remove all values from the database?"
    )
    if msgbox == "no":
        return False
    else:
        pass

    with psycopg2.connect(user=usr_nm, password=passwd, host=ip_adr, port=db_port,
                          dbname=database_nm) as database:
        cursor_create = database.cursor()
        q = "DROP TABLE IF EXISTS reconfig"
        cursor_create.execute(q)
        q = "CREATE TABLE IF NOT EXISTS reconfig(MAC macaddr PRIMARY KEY, \
                                             current_config text, \
                                             desirable_config text, \
                                             reconfigured boolean, \
                                             reconfig_ts timestamp, \
                                             last_ts timestamp, \
                                             NAS_ID text, \
                                             IP inet\
                                             );"
        cursor_create.execute(q)
        database.commit()
    query_database()
    return True


button_frame = LabelFrame(root, text="Commands")
button_frame.pack(fill="x", padx=20)

rebuild_button = Button(button_frame, text="Rebuild table", command=create_table_again)
rebuild_button.grid(row=0, column=0, padx=10, pady=10)

remove_one_button = Button(button_frame, text="Delete line", command=remove_one)
remove_one_button.grid(row=0, column=2, padx=10, pady=10)

change_on_true_button = Button(button_frame, text="Change 'reconfigured' to TRUE", command=entry_change_on_true)
change_on_true_button.grid(row=0, column=3, padx=10, pady=10)

change_on_false_button = Button(button_frame, text="Change 'reconfigured' to FALSE", command=entry_change_on_false)
change_on_false_button.grid(row=0, column=4, padx=10, pady=10)

select_default_values = Button(button_frame, text="Paste default values", command=entry_default_values)
select_default_values.grid(row=0, column=5, padx=10, pady=10)

select_update_table = Button(button_frame, text="Update table", command=after_update)
select_update_table.grid(row=0, column=6, padx=10, pady=10)

my_tree.bind("<<TreeviewSelect>>", select_record)
my_tree.bind('<Button-3>', select_double_record)


def closing():
    msgbox = messagebox.askquestion(
        "Confirmation window", "Are you sure you want to exit the programm?"
    )
    if msgbox == "yes":
        root.destroy()
    else:
        pass


query_database()
after_update()
root.protocol("WM_DELETE_WINDOW", closing)
root.mainloop()
