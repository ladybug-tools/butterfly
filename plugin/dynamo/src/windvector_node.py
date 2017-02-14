# assign inputs
_windSpeed, _windDirection_ = IN
windVector = None

if _windSpeed and _windDirection_:
    try:
        _windDirection_.Unitize()
        windVector = _windSpeed * _windDirection_
    except AttributeError:
        # dynamo
        nv = _windDirection_.Normalized();
        windVector = nv.Scale(_windSpeed);

# assign outputs to OUT
OUT = (windVector,)