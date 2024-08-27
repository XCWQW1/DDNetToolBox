from app.config import cfg


class GlobalsVal:
    ddnet_setting_config = {}
    ddnet_info = None
    server_list_file = False
    DDNetToolBoxVersion = "v1.0.3"
    ddnet_folder = cfg.get(cfg.DDNetFolder)