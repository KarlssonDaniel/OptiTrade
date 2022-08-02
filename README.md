# OptiTrade
A trading god with knowledge of all upcoming events in a time series. Meant as a target for less majestic traders.

The idea is that for a given time series and action penalty (commission fee) find the optimal actions to maximize the sum of the time series when accounting for the penalty. An example would be how to trade a stock optimally in a given (known) window of time.

# Basic goal

The goal is to find pairs of points $x_1$ and $x_2$ in the time series such that given a penalty $c \in [0; 1]$ each pair fulfils,

$$(1 - c)x_2 - (1 + c)x_1 > 0\,.$$

These pairs should then be maximized according to,

$$\max_{x_1,\, x_2}\, (1 - c)x_2 - (1 + c)x_1\,,$$

such that there are no overlaps between the any two pairs in the time series.

# Workflow

The goal is achieved in the following way.

1. Find a low point to start with.
2. Find the closest maximum.
3. Check if the time series will reach above the current value later.
    
    * If not, ensure that the current value gives a positive net value when taking penalty into account.

        * If net value is greater than zero, register these two actions.
        * If net value is not greater than zero, discard these actions and find the next low point.

    * If there are larger future values, check if it is profitable to hold on the the current entry or if the penalty and differences in value makes it more profitable to drop out of the time series, taking the penalty and then returning at an upcoming low point. This can be achieved by considering the cases,
    
      $$\begin{align}
          N_1 &= (1-c)x_4 - (1+c)x_1\,, \\
          N_2 &= (1-c)x_2 - (1+c)x_1 + (1-c)x_4 - (1+c)x_3\,,
      \end{align}$$
    
      where $x_i$ ($i \in \{1,2,3,4\}$) are four potential points of opting in/out. The first equation calculates the net gain by not opting out at the dip in the time series. The second equation opts out at the first dip corresponding to $x_2$ and then opting back in when $x_3$ is reached. Taking the difference and requiring yields the following formula,
      
      $$\begin{equation}
          N_2 - N_1 = (1-c)x_2 - (1+c)x_3 = x_2 - x_3 - c(x_2 + x_3)\,.
      \end{equation}$$
      
      If this difference is positive the strategy to opt out and then back in an extra time is the better option.
    
        * Be aware of possibilities to reduce the opting in value in case the current value pair is not yielding a positive net result.

4. Repeat from last value until end of time series.