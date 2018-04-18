import time
from datetime import datetime
import threading

import libqtile.widget.base as base
import twstock

def real_time_query_worker(realtime_list, bfp_list, idx, stock_id):
    realtime_list[idx] = float(twstock.realtime.get(stock_id)['realtime']['latest_trade_price'])
    bfp = twstock.BestFourPoint(twstock.Stock(stock_id)).best_four_point()
    if bfp:
        bfp_list[idx] = 'B' if bfp[0] else 'S'
    else:
        bfp_list[idx] = ""

class StockWatcher(base.InLoopPollText):
    """A simple text-based Stock Watcher"""
    orientations = base.ORIENTATION_HORIZONTAL
    defaults = [
        ('watch_list', [("3231", '緯創', 22, 26, 25.23)], 'A list stock you watch'),
        ('update_interval', 5., 'Update interval for the watcher'),
        ('stock_update_interval', 60., 'Update interval for stock'),
    ]

    def __init__(self, **config):
        base.InLoopPollText.__init__(self, **config)
        self.add_defaults(StockWatcher.defaults)
        self.realtime = [0] * len(self.watch_list)
        self.bfp = [''] * len(self.watch_list)

    def tick(self):
        self.update(self.poll())
        if int(datetime.now().timestamp()) % self.stock_update_interval == 0:
            for idx in range(len(self.watch_list)):
                threading.Thread(target=real_time_query_worker,
                                 args=(self.realtime, self.bfp, idx, self.watch_list[idx][0])).start()

        return self.update_interval - time.time() % self.update_interval

    def _show_realtime_stock(self):
        idx = int(datetime.now().timestamp()) % len(self.watch_list)
        if self.realtime[idx] and self.watch_list[idx][2] > self.realtime[idx]:
            action = "_"
        elif self.realtime[idx] and self.realtime[idx] > self.watch_list[idx][3]:
            action = "^"
        else:
            action = ""
        output = "{}{}({}) ".format(action, self.watch_list[idx][1], self.watch_list[idx][0])
        if self.realtime[idx]:
            output += "{}({:.2f}%)".format(self.realtime[idx], (self.realtime[idx] - self.watch_list[idx][4]) * 100  / self.watch_list[idx][4])
            output += self.bfp[idx]
        else:
            output += "--"
        return output

    def poll(self):
        return self._show_realtime_stock()
