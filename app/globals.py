from app.config import cfg


class GlobalsVal:
    ddnet_setting_config = {}
    ddnet_info = None
    server_list_file = False
    DDNetToolBoxVersion = "v1.1.5"
    ddnet_folder = cfg.get(cfg.DDNetFolder)
    ddnet_folder_status = False
