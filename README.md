# Constant-Fraction Discriminator Simulation

A simulation web app for exploring the operation of a Constant-Fraction Discriminator (CFD).

---

## How to Run

After cloning the repository, run the following from the top-level directory:

```bash
./scripts/run_stim.sh
```

This script will:

-   Check for required Python packages
-   Install missing dependencies using `pip`
-   Launch the Dash web application

Once the web app is running, you should see something like this:

```bash
Dash is running on http://127.0.0.1:8050/
```
Use ctrl+click on the url to open the app in a new browser tab.

* * * * *

Web App
-----------

Users can view and modify two main figures:

-   **Signal Components**
-   **Sweep**

The button above the figure is used to switch between these modes.

### Controls

-   Sliders and entry boxes are used to adjust parameters that modify the figures.
-   Tabs allow the user to switch between different groups of sliders.
-   In the **Noise and Saturation** tab, the noise checkbox enables Gaussian input noise to be added to the signal.

### Figure and Output

-   Individual traces can be hidden by clicking on the corresponding trace name in the legend
-   The following output values are displayed beneath the figure:
    -   Zero Crossing
    -   Rise Time
    -   Most Probable Value (MPV)

* * * * *

Parameters
-------------

-   **Amplitude**\
    The amplitude of the input signal
-   **Delay**\
    The amount to delay the delayed component of the CFD
-   **Attenuation**\
    The amount to attenuate the attenuated component of the CFD
- **Noise**\
    The standard deviation of the injected Gaussian noise
-   **Saturation**\
    The saturation limit of the CFD\
    *Note: This is only visible when reached by a trace, appearing as a flattening of the distribution*
-   **Arming Comparator Reference**\
    The threshold which the input signal must surpass to begin looking for a zero-crossing (enables the output comparator)
-   **Location**\
    A Landau function parameter that determines the horizontal location of the distribution
-   **Scale**\
    A Landau function parameter that determines the width of the distribution



* * * * *

Signal Components Figure
---------------------------

In this mode, users can see the effect the parameters have on each of the constituent signals of the resulting CFD signal.

* * * * *

Sweep Figure
---------------

In this mode, users can add traces using the **Add Trace** button.

-   The adjustable trace is then captured.
-   Its parameters and output values are saved in the table on the right.
-   *trace 0* is always left adjustable. Additional traces remain fixed once captured.

* * * * *
