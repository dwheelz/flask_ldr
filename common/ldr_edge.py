import RPi.GPIO as GPIO
from time import sleep, time


class TimeTillEdge:
    """
    MUST UTILISE 'WITH' TO FUNCTION

    """
    board_dict = {0: GPIO.BOARD, 1: GPIO.BCM}
    edge_dict = {0: GPIO.RISING, 1: GPIO.FALLING, 2: GPIO.BOTH}

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
        self.gpio_mode = self.board_dict[gpio_mode]
        self.gpio_pin = gpio_pin
        self.edge = self.edge_dict[edge]
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

        if io_order == 0:
            __setup(GPIO.IN)
            sleep(0.1)
            __setup(GPIO.OUT)
            GPIO.output(self.gpio_pin, False)
        elif io_order == 1:
            __setup(GPIO.OUT)
            GPIO.output(self.gpio_pin, False)
            sleep(0.1)
            __setup(GPIO.IN)
        else:
            raise ValueError(
                f"{io_order} is not a supported arg. Supported args are: 'in_out', 'out_in'"
            )

    def edge_time(self, io_order: int = 1) -> tuple:
        """
        returns the time it took to reach the specified edge
        if timeout is reached - timeout value is returned

        Keyword Arguments:
            in_out_order {int}: for example: 0 sets the pin to an input, then an output
        Returns:
            tuple -- "total_time": digit (float or int), "timeout_reached": bool
        """
        # default to timeout hit
        total_time = self.timeout / 1000  # ms to s conversion
        timeout_reached = True

        start_t = time() # begin timer
        self._io_order(io_order)  # set IO for pin
        if GPIO.wait_for_edge(self.gpio_pin, self.edge, timeout=self.timeout) is not None:
            total_time = round(time() - start_t, 2)
            timeout_reached = False

        return total_time, timeout_reached

    def poll_edge_time(self, iterations: int = 3, io_order: int = 1, average_results: bool = True, stop_on_timeout: bool = True) -> dict:
        """Polls the edge time for X iterations.

        Args:
            iterations (int, optional): Defaults to 3.
            io_order (int, optional): Defaults to 1.
            average_results (bool, optional): Defaults to True.
            stop_on_timeout (bool, optional): Defaults to True.

        Returns:
            dict: Example with average_results set to True:
                {
                    0: {'time': 6.7122557163238525, 'timeout': False},
                    1: {'time': 6.4456610679626465, 'timeout': False},
                    2: {'time': 6.279986381530762, 'timeout': False},
                    'average': 6.47930105527242
                }
        """
        return_dict = {}
        iters = 0
        for i in range(0, iterations):
            et, to = self.edge_time(io_order)
            return_dict[str(i)] = {"time": et, "timeout": to}

            if to and stop_on_timeout:
                break

            iters += 1

        if average_results:
            if iters == 0:  # Timeout was reached on the first attempt
                avg_val = self.timeout / 1000  # ms to s conversion
            else:
                avg_val = round(sum([x["time"] for x in return_dict.values()]) / iters, 2)

            return_dict["average"] = avg_val

        return return_dict


if __name__ == "__main__":
    with TimeTillEdge() as TTE:
        print(TTE.poll_edge_time())