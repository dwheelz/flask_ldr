import RPi.GPIO as GPIO
from time import sleep, time


class TimeTillEdge:
    """
    MUST UTILISE 'WITH' TO FUNCTION

    """

    def __init__(self, gpio_mode: int = 0, gpio_pin: int = 7, edge: int = 0, timeout: int = 30000):
        """
        Waits for edge(s) on a specified gpio pin
        Default gpio mode is BOARD
        Keyword Arguments:
            gpio_mode {str} -- GPIO mode - 0: BOARD, 1: BCM (default: 0)
            gpio_pin {int} -- GPIO pin number (default: 7)
            edge {int} -- 0: rising, 1: falling, 2: both (default: 0)
            timeout {int} -- in MS - max wait time before giving up (default: 30000)
        """
        board_dict = {0: GPIO.BOARD, 1: GPIO.BCM}
        self.gpio_mode = board_dict[gpio_mode]
        self.gpio_pin = gpio_pin
        edge_dict = {0: GPIO.RISING, 1: GPIO.FALLING, 2: GPIO.BOTH}
        self.edge = edge_dict[edge]
        self.timeout = timeout

    def __enter__(self):
        GPIO.setmode(self.gpio_mode)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        GPIO.cleanup()

    def _io_order(self, io_order: int):
        """
        Sets the input output order of the pins
        if you are wanting to check for GPIO.RISING in _edge_time, you will want OUT, IN
        GPIO.FALLING, will likely want IN, OUT
        Arguments:
            io_order {int} -- 0: in-out, 1: out-in
        """

        def __setup(gp_in_out): GPIO.setup(self.gpio_pin, gp_in_out)

        if io_order.lower() == 0:
            __setup(GPIO.IN)
            sleep(0.1)
            __setup(GPIO.OUT)
            GPIO.output(self.gpio_pin, False)
        elif io_order.lower() == 1:
            __setup(GPIO.OUT)
            GPIO.output(self.gpio_pin, False)
            sleep(0.1)
            __setup(GPIO.IN)
        else:
            raise ValueError(
                f"{io_order} is not a supported arg. Supported args are: 'in_out', 'out_in'")

    def edge_time(self, io_order: int = 1) -> float:
        """
        returns the time it took to reach the specified edge
        if timeout is reached - timeout value is returned
        Keyword Arguments:
            in_out_order {int}: for example: 0 sets the pin to an input, then an output
        Returns:
            float -- time it took to hit edge
        """
        # begin timer
        start_t = time()

        # set IO for pin
        self._io_order(io_order)

        # wait for edge
        if GPIO.wait_for_edge(self.gpio_pin, self.edge, timeout=self.timeout) is None:
            return self.timeout
        else:
            # return total time
            return time() - start_t

    def return_avg_edge_time(self, r_num: int = 3, io_order: int = 1) -> float:
        """
        returns an average of X readings
        if a timeout is reached it will stop and either:
            - return average of collected readings
            - if no readings have been collected, just return a warning
        Keyword Arguments:
            r_num {int} -- (default: {3})
            in_out_order {int}: for example: 0 sets the pin to an input, then an output
        Returns:
            list -- [list of total edge times]
        """
        return_list = []

        for _ in range(0, r_num):
            edge_t = self.edge_time(io_order)
            if edge_t == self.timeout:
                break
            else:
                return_list.append(edge_t)

        if len(return_list) != r_num:
            return self.timeout  # return timeout value
        else:
            return sum(return_list) / r_num


if __name__ == "__main__":
    with TimeTillEdge(timeout=14500) as TTE:
        print(TTE.return_avg_edge_time())