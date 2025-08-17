# -*-coding: utf8-*-
"""MotionBuilder: plot selected models animation."""

def main(event={}, context={}):
    try:
        from pyfbsdk import FBSystem, FBPlotOptions, FBTime
    except Exception:
        return {"return_code": 4}

    data = event.get("data", {})
    # Configure plot options
    plot_option = FBPlotOptions()
    plot_option.PlotOnFlame = True
    plot_option.ConstantKeyReducerKeepOneKey = True
    plot_option.UseConstantKeyReducer = False
    plot_option.RotationFilterToApply = FBPlotOptions.kFBRotationFilterUnroll if hasattr(FBPlotOptions, 'kFBRotationFilterUnroll') else 0
    plot_option.PlotPeriod = FBTime(0, 0, 0, 1)

    # Plot current take on selected
    FBSystem().CurrentTake.PlotTakeOnSelected(plot_option)
    return {"return_code": 0}
