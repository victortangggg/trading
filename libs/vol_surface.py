# import streamlit as st
# import numpy as np
# import plotly.graph_objects as go
# import yfinance as yf
# import polars as pl
# from scipy.interpolate import griddata
# from datetime import datetime
# import re
# import pytz

# tqqq = yf.Ticker("TQQQ")
# df_options = pl.DataFrame(schema={
#     'contractSymbol': pl.String,
#     'lastTradeDate': pl.Datetime("ns", "UTC"),
#     'strike': pl.Float64,
#     'lastPrice': pl.Float64,
#     'bid': pl.Float64,
#     'ask': pl.Float64,
#     'change': pl.Float64,
#     'percentChange': pl.Float64,
#     'volume': pl.Int64,
#     'openInterest': pl.Int64,
#     'impliedVolatility': pl.Float64,
#     'inTheMoney': pl.Boolean,
#     'contractSize': pl.String,
#     'currency': pl.String,
# })

# for exp in tqqq.options:
#     for option_type in ["calls", "puts"]:
#         df = getattr(tqqq.option_chain( exp ), option_type)
#         df_options = df_options.vstack( pl.from_pandas(df).cast(df_options.schema) )

# def get_days_to_expiry( contract_symbol ):
#     pattern = r"([A-Z]+)(\d+)([C|P])(\d+)"
#     matched = re.match( pattern, contract_symbol)
#     if matched:
#         expiry_date = datetime.strptime( matched.group(2), "%y%m%d").date()
#         now_nyctz = datetime.now( pytz.timezone("America/New_York") )
#         days_to_expiry = (expiry_date - now_nyctz.date()).days
#         return days_to_expiry

# df_options = df_options.with_columns(
#     pl.col("lastTradeDate").dt.convert_time_zone("America/New_York")
# ).with_columns(
#     pl.col("contractSymbol").map_elements( get_days_to_expiry, return_dtype=pl.Int64 ).alias("days_to_expiry")
# )

# x = df_options["strike"].to_numpy()
# y = df_options["days_to_expiry"].to_numpy()
# z = df_options["impliedVolatility"].to_numpy()

# # Create grid
# xi = np.linspace(x.min(), x.max(), 100)
# yi = np.linspace(y.min(), y.max(), 100)
# xi, yi = np.meshgrid(xi, yi)

# # Interpolate
# zi = griddata((x, y), z, (xi, yi), method='linear')

# # Plot
# fig = go.Figure(data=[go.Surface(z=zi, x=xi, y=yi)])
# fig.update_layout(
#     title='TQQQ Implied Volatility Surface',
#     scene=dict(
#         xaxis_title='Strike',
#         yaxis_title='Days to Expiry',
#         zaxis_title='Implied Volatility'
#     ),
#     width=1000,  # Wider
#     height=700,  # Taller
#     autosize=False,
#     margin=dict(l=40, r=40, b=40, t=40),
# )

# # Plot!
# st.plotly_chart(fig)