import numpy as np
from scipy.stats import landau


# Function to calculate component signals
def signalCalcs(x, loc, scale, sat, ampl, delay, att, sigma, nzOn):
    f = lambda x: -ampl * landau.pdf(x, loc=loc, scale=scale)
    y = -f(x)

    if nzOn:
        noise = np.random.normal(loc=0, scale=sigma, size=len(x))
        y = y + noise

    for i in range(len(x)):
            if (y[i] > sat):
                y[i] = sat

    delsig = np.interp(x-delay, x, y, left=0, right=0)
    attsig = -att * y
    cfd = delsig + attsig

    return f, y, delsig, attsig, cfd


# Function to calculate interpolation
# Used in zero crossing and rise time calculations
def lin_interp_x(x,y,i,crossing):
    x1, x2 = x[i], x[i+1]
    y1, y2 = y[i], y[i+1]
    
    x_interp = x1 + (crossing - y1)*(x2-x1)/(y2-y1)
    
    return x_interp

# Function to calculate zero crossing
def zero_crossing(x, y, cfd, arm):
    # indices where incoming signal is creater than arming threshold
    armed = np.where(y>arm)[0]
    
    # indices where sign of cfd changes
    sign_change = np.where(np.diff(np.sign(cfd)))[0]

    if len(sign_change) == 0 or len(armed) == 0:
        return None  # no zero crossing
    else:
        # first index of sign_change after output is armed
        j = np.argmax(sign_change > armed[0]) # returns an index of indices
        i = sign_change[j] # returns an index

    x_zero = lin_interp_x(x,cfd,i,0)

    return x_zero

# Function to calculate rise time
def rise_time(x,y):
    maximum = max(y)

    # indices of *near 10% and 90% of amplitude
    h_index = np.where(np.diff(np.sign(y - 0.9*maximum)))[0][0]
    l_index = np.where(np.diff(np.sign(y- 0.1*maximum )))[0][0]
    
    hi = lin_interp_x(x, y, h_index, 0.9*maximum)
    lo = lin_interp_x(x, y, l_index, 0.1*maximum)
    tr = hi - lo

    return tr