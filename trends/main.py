
from utils import get_start_of_week
from dotenv import load_dotenv
import os


def pipeline(today,assumption,in_question_start,in_question_end,language,country,num_of_terms,minimum_trends):
    from componants import find_keyword,lookup_keyword_trend,make_decision

    forecast_terms = find_keyword(today,assumption,language,num_of_terms=num_of_terms)

    forecast_trend_results = lookup_keyword_trend(assumption,in_question_start,in_question_end,country,forecast_terms)

    return make_decision(today,assumption,forecast_trend_results,minimum_trends)




if __name__ == "__main__":
    load_dotenv()
    assert os.getenv("OPENAI_API_KEY") is not None
    
    assumption = "housing pricing in israel will keep decreaseing"
    negative_assumption = "housing pricing in israel will keep increasing"
    today = get_start_of_week()
    country = "IL"#ISR
    language = "hebrew"
    in_question_start, in_question_end = "2021-01-01", get_start_of_week()


    decision = pipeline(today,assumption,in_question_start,in_question_end,language,country,num_of_terms=2,minimum_trends=2)

    print(f"\n---\n {decision} \n---\n ")