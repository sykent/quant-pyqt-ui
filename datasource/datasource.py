import akshare as ak
import pandas as pd

from utils import timeutils


def data_hist(code, start_time, end_time) -> pd.DataFrame:
    df = ak.stock_zh_a_hist(
        symbol=str(code),
        start_date=timeutils.format_convert(start_time, '%Y-%m-%d', '%Y%m%d'),
        end_date=timeutils.format_convert(end_time, '%Y-%m-%d', '%Y%m%d'),
        adjust="qfq")
    return df
