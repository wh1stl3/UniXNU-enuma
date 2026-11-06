"""New full-application experiment scope; never inherits R025 authorization."""
from copy import deepcopy
from full_menu_scope import SCOPE as WINDOW_SCOPE
SCOPE=deepcopy(WINDOW_SCOPE)
SCOPE.update(experiment='unixnu-post-driver-return-menu-v1',
             launch_phase='DXE dispatcher after actual SimpleFb StartImage return',
             driver_return='EFI_SUCCESS required; journal point13 unchanged',
             menu_result_point=28,owned_deferred_context=True,
             configured_entry_title='Driver returned - Return to firmware',bds_reached=False)
