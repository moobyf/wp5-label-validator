"""Shutdown callbacks."""
import os
import sys
import time
import threading
from dash import Input, Output, html
import dash

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app


@app.callback(Output('shutdown-modal', 'style'), Input('shutdown-btn', 'n_clicks'), prevent_initial_call=True)
def show_shutdown_modal(n):
    return {'display': 'block'} if n else dash.no_update


@app.callback(Output('shutdown-modal', 'style', allow_duplicate=True), Input('shutdown-cancel-btn', 'n_clicks'), prevent_initial_call=True)
def cancel_shutdown(n):
    return {'display': 'none'} if n else dash.no_update


@app.callback(Output('shutdown-modal', 'children'), Input('shutdown-confirm-btn', 'n_clicks'), prevent_initial_call=True)
def confirm_shutdown(n):
    if n:
        def delayed_exit():
            time.sleep(1)
            print("\n" + "="*50 + "\n🛑 Shutdown requested\n" + "="*50)
            os._exit(0)
        threading.Thread(target=delayed_exit, daemon=True).start()
        return html.Div(style={'position': 'fixed', 'top': '50%', 'left': '50%', 'transform': 'translate(-50%, -50%)',
                               'backgroundColor': 'white', 'borderRadius': '10px', 'padding': '40px', 'textAlign': 'center',
                               'zIndex': 2001, 'boxShadow': '0 10px 40px rgba(0,0,0,0.3)'}, children=[
            html.H2("✅ Shutting down...", style={'color': '#28a745', 'fontSize': '20px'}),
            html.P("Server is stopping. Close this tab.", style={'fontSize': '15px'}),
            html.P("Restart: sbatch run_validator.sh", style={'fontFamily': 'monospace', 'color': '#666', 'fontSize': '14px'})
        ])
    return dash.no_update


@app.callback(Output('heartbeat-response', 'children'), Input('heartbeat-interval', 'n_intervals'))
def heartbeat(n):
    return str(n)
