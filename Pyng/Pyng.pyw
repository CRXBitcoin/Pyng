import os
import platform
import subprocess
import threading
import time
from tkinter import Tk, Label, Entry, Button, Text, END, Scrollbar, filedialog, Toplevel, messagebox
from tkinter.ttk import Progressbar, Style

# Detect OS and create the ping command
def get_ping_command(target):
    if platform.system() == "Windows":
        return ["ping", "-n", "1", target]  # Send one ping at a time
    else:
        return ["ping", "-c", "1", target]  # Send one ping at a time on Unix

# Function to execute ping command
def execute_ping(target, packet_size, interval, log_area, stop_event, stats):
    log_area.insert(END, f"Starting ping to {target} with packet size {packet_size} bytes and interval {interval} seconds.\n")
    log_area.see(END)
    try:
        while not stop_event.is_set():
            command = get_ping_command(target)
            try:
                start_time = time.time()
                process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                stdout, stderr = process.communicate()
                end_time = time.time()

                # Logging output
                if stdout:
                    log_area.insert(END, stdout)
                if stderr:
                    log_area.insert(END, stderr)

                response_time = round((end_time - start_time) * 1000, 2)  # Convert to ms
                log_area.insert(END, f"Response Time: {response_time} ms\n")
                log_area.see(END)

                # Update stats
                stats["pings_sent"] += 1
                stats["total_response_time"] += response_time

            except Exception as e:
                log_area.insert(END, f"Error: {e}\n")
                break

            time.sleep(interval)
    finally:
        log_area.insert(END, f"Ping to {target} stopped.\n")
        log_area.see(END)

# Display splash screen
def show_splash_screen():
    splash = Toplevel()
    splash.title("Welcome")
    splash.geometry("300x200")
    splash.overrideredirect(True)

    Label(splash, text="Pyng", font=("Helvetica", 16, "bold")).pack(pady=20)
    Label(splash, text="Created by @CRXBitcoin", font=("Helvetica", 12)).pack(pady=10)

    splash.after(2000, splash.destroy)

# GUI Setup
def start_gui():
    def start_ping():
        target = target_entry.get()
        packet_size = packet_size_entry.get()
        interval = interval_entry.get()

        if not target:
            log_area.insert(END, "Error: No target specified.\n")
            return

        try:
            packet_size = int(packet_size)
            if not (0 < packet_size <= 65500):
                raise ValueError("Packet size must be between 1 and 65500.")
            interval = float(interval)
            if interval <= 0:
                raise ValueError("Interval must be greater than 0.")
        except ValueError as ve:
            log_area.insert(END, f"Error: {ve}\n")
            return

        log_area.insert(END, f"Starting Pyng on {target}...\n")
        log_area.see(END)

        # Stop any ongoing ping
        stop_event.set()
        stop_event.clear()

        # Start ping in a separate thread
        threading.Thread(
            target=execute_ping,
            args=(target, packet_size, interval, log_area, stop_event, stats),
            daemon=True
        ).start()

    def stop_ping():
        stop_event.set()
        log_area.insert(END, "Stopping Pyng...\n")
        log_area.see(END)

    def save_log():
        log_file = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("CSV Files", "*.csv")])
        if log_file:
            with open(log_file, "w") as file:
                file.write(log_area.get(1.0, END))
            log_area.insert(END, f"Logs saved to {log_file}\n")

    def show_stats():
        if stats["pings_sent"] > 0:
            avg_response_time = stats["total_response_time"] / stats["pings_sent"]
            messagebox.showinfo(
                "Ping Statistics",
                f"Total Pings Sent: {stats['pings_sent']}\nAverage Response Time: {avg_response_time:.2f} ms"
            )
        else:
            messagebox.showinfo("Ping Statistics", "No pings have been sent yet.")

    # Main Window
    root = Tk()
    root.title("Pyng - Ping of Death DDoS Tool")
    show_splash_screen()

    Label(root, text="Target IP/Domain:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
    target_entry = Entry(root, width=40)
    target_entry.grid(row=0, column=1, padx=10, pady=5)

    Label(root, text="Packet Size (max 65500):").grid(row=1, column=0, padx=10, pady=5, sticky="w")
    packet_size_entry = Entry(root, width=40)
    packet_size_entry.grid(row=1, column=1, padx=10, pady=5)

    Label(root, text="Ping Interval (seconds):").grid(row=2, column=0, padx=10, pady=5, sticky="w")
    interval_entry = Entry(root, width=40)
    interval_entry.grid(row=2, column=1, padx=10, pady=5)

    start_button = Button(root, text="Start Ping", command=start_ping, bg="green", fg="white")
    start_button.grid(row=3, column=0, padx=10, pady=10)

    stop_button = Button(root, text="Stop Ping", command=stop_ping, bg="red", fg="white")
    stop_button.grid(row=3, column=1, padx=10, pady=10)

    save_button = Button(root, text="Save Logs", command=save_log, bg="blue", fg="white")
    save_button.grid(row=4, column=0, padx=10, pady=10)

    stats_button = Button(root, text="Show Stats", command=show_stats, bg="purple", fg="white")
    stats_button.grid(row=4, column=1, padx=10, pady=10)

    log_area = Text(root, height=20, width=80)
    log_area.grid(row=5, column=0, columnspan=2, padx=10, pady=5)

    scrollbar = Scrollbar(root, command=log_area.yview)
    log_area.config(yscrollcommand=scrollbar.set)
    scrollbar.grid(row=5, column=2, sticky="ns")

    # Statistics and Stop Event
    stats = {"pings_sent": 0, "total_response_time": 0.0}
    stop_event = threading.Event()

    root.mainloop()

# Entry Point
if __name__ == "__main__":
    start_gui()
