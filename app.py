"""
Main Dash app initialization.
"""
import os

os.environ['DASH_DISABLE_JUPYTER'] = '1'

import dash

jupyter_user = os.environ.get('JUPYTERHUB_USER', '')
port = os.environ.get('PORT', '8050')

if jupyter_user:
    requests_pathname_prefix = f'/user/{jupyter_user}/proxy/{port}/'
else:
    requests_pathname_prefix = '/'

app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    title="Label Validator",
    requests_pathname_prefix=requests_pathname_prefix
)

server = app.server
