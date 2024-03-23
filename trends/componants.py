from utils import call_open_ai,google_search_results,selenium_get
import json
import pandas as pd

def find_keyword(today,assumption,language,num_of_terms,context=""):
    print("==== Finding Keywords ===")
    # Create a prompt that contains the paragraphs
    prompt = f"""
    Today is {today}
    Assuming that will '{assumption}'
    What we will be the common searchs across the web that will increase or decrease in the weeks before?, provide your estimation in the following format:
    {context}
    this is the json to respose with:
    [
    {{
        
        "search_term":"<the term search you expect will be impacted>",
        "change_in_search_expectations":"<do you expect the number of searchs to increase or decrease>",
        "change_in_search_explanation":"<additional comments that explain why>"
    }},
    // more here
    ]

    Provide at least {num_of_terms} queries. You must provide them in {language}, think step by step.
    """
    
    result = call_open_ai(prompt)

    result = json.loads(result.replace('\\"',"'"))

    print("Found keywords:")
    for entry in result:
        print(f" - {entry['search_term']}")

    return pd.DataFrame(result)


def lookup_keyword_trend(assumption,in_question_start,in_question_end,country,forecast_terms):

    print("=== Looking up Trends ===")
    import json
    from trends.utils import get_trend_and_forecast_with_retry


    foreca = list()
    figures = list()
    for term in forecast_terms:   
        search_term = term['search_term']

        try:
            fig, forecast_response = get_trend_and_forecast_with_retry(search_term,assumption,in_question_start,in_question_end,country)

            figures.append(fig)
            foreca.append({
                        **term,
                        **forecast_response
                    })
            print(f" v {search_term}")
        except Exception as e:
            print(f" x {search_term}")


    formated_search_results = list()
    final_figures = dict()
    for f,fig in zip(foreca,figures):
        if f['execution_status']:
            result = {}
            for k in f.keys():  
                if not isinstance(f[k],str) and not isinstance(f[k],bool):
                    result[k] = float(f[k])
                elif k not in ['execution_status']:
                    result[k] = f[k]
            
            formated_search_results.append(result)
            final_figures[f['search_term']] = fig

    print("Completed Ternd Forecasting:")
    for fore_term in formated_search_results:
        print(f" - '{fore_term['search_term']}'")
    return final_figures, pd.DataFrame(formated_search_results)


def make_decision(today,assumption,formated_search_results,minimum_trends):
    print("=== Making a decision ===")

    if len(formated_search_results) < minimum_trends:
        return f"can't make a decision base on less then {minimum_trends}"
    import json
    # Create a prompt that contains the paragraphs
    prompt = f"""
    Today is {today}
    We assume this week '{assumption}'
    We ran google search on key terms that should indicate the assumption is correct, and forecast the last data point.
    {json.dumps(formated_search_results, indent=4)} 
    --
    {{
        "forecast_analysis":[
        {{
            "search_term":"<the search term you looked on>",
            "claims":"<the calim if the forecast base on this search term, support and agienst the assumption>"
        }},
        // more here
        ],
        "final_decision":<reason if you think the assumption is correct. Provide Yes or No, a explain yourself in details>

    }}

    """

    result = call_open_ai(prompt)
    # 
    print("Decision is base:")
    result = json.loads(result)
    for res in result['forecast_analysis']:
        print(f" - {res['search_term']}: {res['claims']}")
    return result['final_decision']


def search_keywords_in_google(today,action,num_of_search_term=1,num_results_per_query=1):
    import json
    # Create a prompt that contains the paragraphs
    prompt = f"""
    Today is {today}, you would like to learn what are the common methods people use when following the task '{action}'. 
    What are terms you would like to search to obtain this knowledge, the term should start with 
    produce {num_of_search_term} terms, the format is:
    --
    {{
        "google_search_terms":[
         "first term"
         // more here
        
        ]
    }}

    """

    result = call_open_ai(prompt)
    # 
    result = json.loads(result)
    search_results = list()
    print("Searching Google:")
    for query in result['google_search_terms'][:num_of_search_term]:
        print(f" v '{query}'")
        responses = google_search_results(query,num_results=num_results_per_query)
        for response in responses:
            print(f":scraping: '{response['title']}'")
            search_results.append(selenium_get(response['link']))
    return search_results


def find_keyword_in_google(today,action,assumption,language,num_of_keyword_to_extract,num_of_keyword_to_create,num_results_per_query):
    import warnings
    warnings.simplefilter(action='ignore')

    search_results = search_keywords_in_google(today,action,num_of_search_term=num_of_keyword_to_create,num_results_per_query=num_results_per_query)
    
    all_search_terms = list()
    for search_result in search_results:
        search_terms = find_keyword(today,assumption,language,num_of_keyword_to_extract,context=search_result)
        all_search_terms.append(search_terms)


    context = f"Here search terms that was extracted by an LLM given a context from Google: {pd.concat(all_search_terms).to_dict('records')}"
    return find_keyword(today,assumption,language,num_of_keyword_to_extract,context=context)


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    num_of_keyword_to_extract=2
    num_of_keyword_to_create=2
    num_results_per_query=5
    find_keyword_in_google("27/08/2024",
                           "buy an house in israel",
                           "prices will increase",
                           "english",
                           num_of_keyword_to_extract=num_of_keyword_to_extract,
                           num_of_keyword_to_create=num_of_keyword_to_create,
                           num_results_per_query=num_results_per_query)