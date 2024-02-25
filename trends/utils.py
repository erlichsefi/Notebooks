



def forecast(interest_over_time_df,kw,number_of_dates_to_comapre):
    import pandas as pd
    from prophet import Prophet

    import logging
    logger = logging.getLogger('cmdstanpy')
    logger.addHandler(logging.NullHandler())
    logger.propagate = False
    logger.setLevel(logging.CRITICAL)

    # Example DataFrame with date and value columns
    data = pd.DataFrame({
        'ds': pd.date_range(start=interest_over_time_df.index.min(), end=interest_over_time_df.index.max(), freq='W'),
        'y': interest_over_time_df[kw].values  # Assuming 'Python Programming' is the column of interest
    })
        # Instantiate Prophet model
    model = Prophet()

    # Fit the model to your data
    model.fit(data)

    # Create a dataframe for future dates you want to forecast
    future_dates = model.make_future_dataframe(periods=number_of_dates_to_comapre,freq="W")  # Forecasting for 365 days

    # Perform the forecast
    forecast = model.predict(future_dates)

    # Visualize the forecast
    fig = model.plot(forecast)

    return forecast.iloc[-number_of_dates_to_comapre][['trend','trend_lower','yhat_upper','yhat','yhat_lower','yhat_upper']].to_dict()


def get_trend_data(kw,date_start,date_end,country,number_of_dates_to_comapre):
    from pytrends.request import TrendReq

    # Login to Google. Only need to run this once, the rest of requests will use the same session.
    pytrend = TrendReq(geo=country)#, retries=3, backoff_factor=2)

    # Build the payload
    kw_list = [kw]
    timeframe = f'{date_start} {date_end}'  
    pytrend.build_payload(kw_list, timeframe=timeframe)

    # Interest Over Time
    interest_over_time_df = pytrend.interest_over_time()

    if interest_over_time_df.shape[0] == 0:
        raise ValueError("trend api, return no data.")
    return interest_over_time_df.iloc[:-number_of_dates_to_comapre],interest_over_time_df.iloc[-number_of_dates_to_comapre:]




def get_trend_data_with_retry(kw,date_start,date_end,country,number_of_dates_to_comapre):
    import pytrends.exceptions
    import time

    retry_delay = 5  # Initial delay before retrying (in seconds)
    max_retries = 3  # Maximum number of retries

    for attempt in range(max_retries):
        try:
            return get_trend_data(kw,date_start,date_end,country,number_of_dates_to_comapre) 
        except pytrends.exceptions.TooManyRequestsError:
            if attempt < max_retries - 1:
                #print("Rate limit exceeded. Retrying in {} seconds...".format(retry_delay))
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                #print("Max retries exceeded. Exiting.")
                raise Exception("Get Trend max retries exceeded. Exiting.")
            
def get_trend_and_forecast(kw,date_start,date_end,country,number_of_dates_to_comapre=1):

    interest_over_time_df,interest_over_time_df_lastest = get_trend_data_with_retry(kw,date_start,date_end,country,number_of_dates_to_comapre)
    forecast_result = forecast(interest_over_time_df,kw,number_of_dates_to_comapre)

    return {
        "execution_status":True,
        **forecast_result,
        "actual":interest_over_time_df_lastest[kw].values[0]
    }

    

def call_open_ai(prompt):
    from openai import OpenAI

    client = OpenAI()

    stream = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        stream=False,
    )
    return stream.choices[0].message.content

def ask_to_rephrase(kw,objective):
    prompt = f"""
    You are trying to find keyword that was searched in google that indicate if '{objective}' will take place, however the google search on this term '{kw}' results without any value.
    Rephrase, keep the semantic meaning the same, mostly shorten the term.

    response in the following format
    {{
    "new_search_term":"<new term>"
    }}
"""
    result = call_open_ai(prompt)

    import json
    return json.loads(result)['new_search_term']
    


def get_trend_and_forecast_with_retry(kw,objective,date_start,date_end,country,number_of_dates_to_comapre=1):
    max_retries = 1  # Maximum number of retries
  
    for attempt in range(max_retries):
        try:
            return {
                **get_trend_and_forecast(kw,date_start, date_end,country,number_of_dates_to_comapre=number_of_dates_to_comapre),
                "search_term":kw
            }
        except ValueError:
            if attempt < max_retries - 1:
                #print("No keyword. Rephrasing '{}' ...".format(kw))
                kw = ask_to_rephrase(kw,objective)
                #print(f"Rephrased to '{kw}'")
            else:
                #print("Max retries rephrased exceeded. Exiting.")
                raise Exception("Rephrasing, Max retries exceeded. Exiting.") 
   


import datetime
def get_start_of_week(date=None):
    """
    Get the start of the week for a given date.
    
    Parameters:
        date (datetime.datetime): The date for which to find the start of the week. 
                                  If None, the current date is used.
    
    Returns:
        datetime.datetime: The start of the week.
    """
    if date is None:
        date = datetime.datetime.now()
    
    start_of_week = date - datetime.timedelta(days=date.weekday())
    return start_of_week.strftime("%Y-%m-%d")