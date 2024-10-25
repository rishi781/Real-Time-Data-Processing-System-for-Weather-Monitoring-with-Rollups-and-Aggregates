
import pytest
from main import kelvin_to_celsius, calculate_daily_summary, check_alert_conditions

def test_kelvin_to_celsius():
    assert round(kelvin_to_celsius(300), 2) == 26.85
    assert kelvin_to_celsius(273.15) == 0
    assert kelvin_to_celsius(0) == -273.15

def test_calculate_daily_summary():
    sample_data = [
        {"temp": 30, "condition": "Clear"},
        {"temp": 32, "condition": "Clear"},
        {"temp": 29, "condition": "Rain"},
    ]
    calculate_daily_summary(sample_data)
    conn = sqlite3.connect("weather_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM daily_summary WHERE date = ?", (datetime.now().strftime("%Y-%m-%d"),))
    result = cursor.fetchone()
    conn.close()
    
    assert result is not None
    avg_temp, max_temp, min_temp, dominant_condition = result[1:]
    assert round(avg_temp, 2) == 30.33
    assert max_temp == 32
    assert min_temp == 29
    assert dominant_condition == "Clear"

def test_check_alert_conditions(capsys):
    city = "Test City"
    check_alert_conditions(city, 36, "Clear")
    check_alert_conditions(city, 37, "Clear")
    check_alert_conditions(city, 38, "Clear")

    captured = capsys.readouterr()
    assert "ALERT!" in captured.out
