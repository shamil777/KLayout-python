from importlib import reload

import Tmon_chain_10x5_resonators
reload(Tmon_chain_10x5_resonators)

import Tmon_chain_10x5_aoe_drives
reload(Tmon_chain_10x5_aoe_drives)
import Tmon_chain_10x5_FBs
reload(Tmon_chain_10x5_FBs)
import Tmon_single_10x5_FBs
reload(Tmon_single_10x5_FBs)
import Tmon_5Q_chain_10x5
reload(Tmon_5Q_chain_10x5)

app = pya.Application.instance()
mw = app.main_window()
lv = mw.current_view()
cv = lv.active_cellview()
cv.cell_name = "total"
lv.zoom_fit()
