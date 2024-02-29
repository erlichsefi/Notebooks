from utils import call_open_ai
import json

def find_keyword(today,assumption,language,num_of_terms):
    print("==== Finding Keywords ===")
    # Create a prompt that contains the paragraphs
    prompt = f"""
    Today is {today}
    Assuming that will '{assumption}'
    What we will be the common searchs across the web that will increase or decrease in the weeks before?, provide your estimation in the following format:

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

    return result


def lookup_keyword_trend(assumption,in_question_start,in_question_end,country,forecast_terms):

    print("=== Looking up Trends ===")
    import json
    from utils import get_trend_and_forecast_with_retry


    foreca = list()
    for term in forecast_terms:   
        search_term = term['search_term']

        try:
            forecast_response = get_trend_and_forecast_with_retry(search_term,assumption,in_question_start,in_question_end,country)

            foreca.append({
                        **term,
                        **forecast_response
                    })
            print(f" v {search_term}")
        except Exception as e:
            print(f" x {search_term}")


    formated_search_results = list()
    for f in foreca:
        if f['execution_status']:
            result = {}
            for k in f.keys():  
                if not isinstance(f[k],str) and not isinstance(f[k],bool):
                    result[k] = float(f[k])
                elif k not in ['execution_status']:
                    result[k] = f[k]
            
            formated_search_results.append(result)

    print("Completed Ternd Forecasting:")
    for fore_term in formated_search_results:
        print(f" - '{fore_term['search_term']}'")
    return formated_search_results


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