"""Module containing OptiTrade class."""
import pandas as pd


class OptiTrade:
    """OptiTrade class for maximizing gain from a time series given a penalty.

    The goal is to find a low point in the beginning of the time series where
    the instance will opt in to the series and then find the optimal point to
    exit. This is subject to time series values and a penalty taken each time
    the time series is opted in to or out of. This schema is repeated for the
    complete time series and returns the optimal points of entry/exit.
    """

    def __init__(self, tseries: pd.Series, penalty: float or tuple[float]):
        """Construct OptiTrade instance."""
        self.tseries = tseries
        self.penalty = penalty
        self.position = 0
        self.tmp: list = []
        self.registered_pairs: list[list] = []

    def find_smaller(self, tseries: pd.Series = None) -> int:
        """Move position to smallest future value not crossing larger value.

        By multiplying a series with -1 this method may be used to find the
        largest value without crossing smaller values.

        Returns:
            int: Position in time series where smallest value is located.
        """
        if tseries is None:
            tseries = self.tseries
        pos = self.position
        while (pos + 1 < len(tseries) and tseries[pos] >= tseries[pos + 1]):
            pos += 1
        return pos

    def net_positive(self) -> bool:
        """Check if suggested points yield positive net value.

        Evaluate ((1 - self.penalty) * self.tmp[1] -
                  (1 + self.penalty) * self.tmp[0]) > 0

        Returns:
            bool: is the net gain positive.
        """
        return ((1 - self.penalty) * self.tseries[self.tmp[1]] -
                (1 + self.penalty) * self.tseries[self.tmp[0]]) > 0

    def find_next_larger(self) -> int:
        """Find next time when time series is greater than current value.

        Returns:
            int: Position in time series where the time series exceeds
                 current value next. nan if this larger value does not
                 exist.
        """
        min_val = self.tseries[self.position]
        exists = (self.tseries[self.position:].
                  where(self.tseries[self.position:] >
                        min_val)).first_valid_index()
        return exists

    def find_min(self, end_pos: int) -> float:
        """Find smallest value between current position and end_pos.

        If end_pos is None the calculation will use the final entry of the
        time series as end_pos.

        Args:
            end_pos (int): End position for where to find the minimum value.

        Returns:
            float: Minimum value in interval.
        """
        return self.tseries[self.position:end_pos].argmin() + self.position

    def check_profitable(self, intermediate: float) -> bool:
        """Check profitability of opting out of time series in temporary dip.

        Method checks profitability of opting out of time series at current
        position opting back in when the time series value again exceeds
        current value.

        Args:
            intermediate (float): Value for opting in the second time.

        Returns:
            bool: Profitable to temporarily opt out.
        """
        current = self.tseries[self.position]
        return (current - intermediate - self.penalty * (current +
                                                         intermediate)) > 0

    def find_optimal_pairs(self):
        """Traverse the time series to find optimal values."""
        while self.position < len(self.tseries) - 1:
            # Find start point
            opt_in = self.find_smaller()
            self.position = opt_in
            self.tmp.append(opt_in)

            while self.position < len(self.tseries) - 1:
                # Find closest maximum, this is a decision point
                decision_point = self.find_smaller(-self.tseries)
                self.position = decision_point
                self.tmp.append(decision_point)
                # Find next time the time series exceeds current value
                next_larger_id = self.find_next_larger()
                # Handle case when the current peak is global
                if next_larger_id is None and self.net_positive():
                    self.registered_pairs.append(self.tmp)
                    self.tmp = []
                    break
                elif next_larger_id is None:
                    self.tmp = []
                    break

                # Check profitability in opting out and back in when dropped
                intermediate_point = self.find_min(next_larger_id)
                profitable = self.check_profitable(self.tseries
                                                   [intermediate_point])

                if profitable and self.net_positive():
                    # Add positions to registry
                    self.registered_pairs.append(self.tmp)
                    self.tmp = []
                    break
                elif profitable:
                    # Handle case when opting in value can be reduced
                    self.position = self.find_smaller()
                    self.tmp[0] = self.position
                    self.tmp.pop(1)
                else:
                    # Move to next larger value
                    self.position = next_larger_id
                    self.tmp.pop(1)


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    import numpy as np
    # Random test Series
    base = np.cos(np.linspace(0, 2 * np.pi, 100))
    noise = np.random.normal(0, 0.08, size=100)
    test = pd.Series(5 + noise + base)
    # test = pd.Series([5.94, 5.89, 5.97, 6.0, 5.98, 6.07, 5.88, 5.98, 5.9])

    ot = OptiTrade(test, penalty=0.0025)

    ot.find_optimal_pairs()

    signals = ot.registered_pairs
    opting_in = [x[0] for x in signals]
    opting_out = [x[1] for x in signals]

    plt.figure(figsize=(12, 6))
    plt.plot(ot.tseries, label="Values")
    plt.scatter(opting_in, ot.tseries[opting_in], label="Opting in")
    plt.scatter(opting_out, ot.tseries[opting_out], label="Opting out")
    plt.legend()
    plt.grid()
    plt.title("Optimal trading actions")
    plt.show()

# %%
