"""This module contains asynchronous code which runs once on server start that monitors sessions for hourly bet resolution."""
import threading

def stats_thread_func():
    pass

session_monitor_thread = threading.Thread(target=stats_thread_func)
session_monitor_thread.start()