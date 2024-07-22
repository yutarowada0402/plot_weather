import openmeteo_requests

import requests_cache
import pandas as pd
from retry_requests import retry
import plotly.graph_objects as go
from plotly.subplots import make_subplots


cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# 天気を取得する場所の緯度経度を設定
# 東京ディズニーランドに設定
url = "https://api.open-meteo.com/v1/forecast"
params = {
	"latitude": 35.6331,
	"longitude": 139.8806,
	"hourly": ["temperature_2m", "relative_humidity_2m"],
 	"timezone": "Asia/Tokyo"
}
responses = openmeteo.weather_api(url, params=params)

response = responses[0]

hourly = response.Hourly()
hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
hourly_relative_humidity_2m = hourly.Variables(1).ValuesAsNumpy()

hourly_data = {"date": pd.date_range(
	start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
	end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = hourly.Interval()),
	inclusive = "left"
)}
hourly_data["temperature_2m"] = hourly_temperature_2m
hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m

hourly_dataframe = pd.DataFrame(data = hourly_data)


fig = make_subplots(specs=[[{"secondary_y": True}]])

# ③ グラフを記述する際に第1軸と第2軸を設定
# 第1軸のグラフ
fig.add_trace(
    go.Scatter(x=hourly_data['date'], y=hourly_data['temperature_2m'], name="気温"),
    secondary_y=False,
)

# 第2軸のグラフ
fig.add_trace(
    go.Scatter(x=hourly_data['date'], y=hourly_data['relative_humidity_2m'], name="湿度"),
    secondary_y=True,
)

fig.update_layout(
    title = '東京ディズニーランドの直近1週間の気温・湿度予報'
)
fig.update_xaxes(
    tickformat='%m/%d(%a) %H:00',
    dtick=21600000,  # 6時間ごとに目盛りを表示（ミリ秒単位、1時間 = 3600秒 = 3600 * 1000ミリ秒）
    tickangle=60 
)
fig.update_yaxes(title_text="<b>気温</b> ℃", secondary_y=False)
fig.update_yaxes(title_text="<b>湿度</b> ％", secondary_y=True)

fig.show()