from joblib import Parallel
from joblib import delayed
import numpy as np
from multiprocessing import cpu_count
import itertools


def score_model(func, train, fold_size, scoring_func, params, folds):
    try:
        
        scores = []
        for i in range(folds):
            
            # 
            split_point=len(train)-(folds-i)*fold_size
            #
            x=train[:split_point]
            f=train[split_point:split_point+fold_size] 
            smooth_series = func(x, len(f),**params)[0]
            
            # compute the score
            forecasted = np.array(smooth_series[-len(f):])
            acutals = np.array(f)
            
            scores.append(scoring_func(forecasted,acutals))
            
        return sum(scores)/len(scores)
    
    except ValueError as e:
        return np.nan
    

    

def grid_search(data, cfg_list, score_lambda, fold_size, folds, parallel=True):
    scores = None
    if parallel:
        # execute configs in parallel
        executor = Parallel(n_jobs=cpu_count(), backend='multiprocessing')
        tasks = (delayed(score_model)(data, fold_size, score_lambda, cfg, folds) for cfg in cfg_list)
        scores = executor(tasks)
    else:
        scores=[]
        for cfg in cfg_list:
            scores.append(score_model(data, fold_size, score_lambda, cfg, folds))
    return scores


def map_to_configuration_list(in_options):
    return [dict(zip(in_options,p)) for p in list(itertools.product(*in_options.values()))]

def handle_scores(scores,cfg_list, print_top = False):
    
    # remove empty results
    max_value = np.nanmax(np.array(scores))
    for i in range(len(scores)):
        if np.isnan(scores[i]):
            scores[i]=max_value
    
    # sort configs by error, asc
    scores=np.array(scores)
    min_index=np.argmin(scores)
    
    if print_top:
        print("Min Top 10 is:")
        for index in np.argpartition(scores,10)[:10]:
            print("----")
            print(f"score is {scores[index]}")
            print(f"score is {cfg_list[index]}")

    return scores[min_index],cfg_list[min_index]