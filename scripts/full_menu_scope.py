"""New full-application experiment scope; never inherits R025 authorization."""
from copy import deepcopy
from menu_window_scope import SCOPE as WINDOW_SCOPE
SCOPE=deepcopy(WINDOW_SCOPE)
SCOPE.update(experiment='unixnu-full-application-window-v1',full_unixnu_run=True,
             application_host='application',application_source='fixed-UniXNU-PE32-from-FV',
             config_source='private-readonly-memory-volume',configured_actions=['exit'],
             connect_all=False,scale=1,bds_reached=False)
