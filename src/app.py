from src.api.open_meteo import get_forecasts
from src.util.geo import LatLon, get_german_states, merge_forecasts

if __name__ == "__main__":
    states = get_german_states()
    forecasts = get_forecasts([LatLon(s.lat, s.lon) for s in states])
    forecast = merge_forecasts(forecasts, [s.weight for s in states])
    print("DAYS", [d.isoformat()[:10] for d in forecast.days])
    print("DAYLIGHT", forecast.daylight_dur)
    print("SUNSHINE", forecast.sunshine_dur)
