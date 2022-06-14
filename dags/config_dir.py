import os
from airflow.models import Variable
import logging


def replace_path(key, default_value):
    paths_config_str = Variable.get("paths_config")
    if paths_config_str != "{}":
        paths_conf = eval(paths_config_str)
        try:
            if key in paths_conf.keys():
                return paths_conf[key]
        except Exception as e:
            logging.warning("smth", exc_info=True)
    return default_value


dev_postfix = "BDSD-8115-online-features-sep-k8s-node"
project_root = "hdfs:///share/products/forecast_platform/oos"
main_hdfs_path = replace_path("main_hdfs_path", os.path.join(project_root, "dev", dev_postfix))
prod_hdfs_path = replace_path("prod_hdfs_path", os.path.join(project_root, "prod"))

data_dir_path = replace_path("data_dir_path", os.path.join(prod_hdfs_path, "data"))
prices_path = replace_path("prices_path", os.path.join(data_dir_path, "prices_hist"))
promo_info_path = replace_path("promo_info_path", os.path.join(data_dir_path, "promo_info_hist"))

