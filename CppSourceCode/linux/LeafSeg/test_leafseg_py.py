from typing import List
import numpy as np
from numpy.core.fromnumeric import cumsum

def get_borders(area_id_map:np.ndarray, score_map:np.ndarray)->List:
    dot_adj_stack = np.stack([area_id_map[:-1,:-1], area_id_map[:-1,1:], area_id_map[1:,:-1], area_id_map[1:,1:]], axis=-1)
    border_map_high = np.max(dot_adj_stack, axis=-1)
    border_map_low = np.min(dot_adj_stack, axis=-1)
    border_area = np.where(border_map_high != border_map_low)
    mean_score = np.mean(np.stack([score_map[:-1,:-1], score_map[:-1,1:], score_map[1:,:-1], score_map[1:,1:]], axis=-1), axis=-1)
    
    border_dots = np.stack([border_map_high[border_area], border_map_low[border_area]], axis=-1)
    border_dots_score = mean_score[border_area]

    order_low_area = np.argsort(border_dots[:,1], kind='stable')
    border_dots = border_dots[order_low_area]
    border_dots_score = border_dots_score[order_low_area]
    
    order_high_area = np.argsort(border_dots[:,0], kind='stable')
    border_dots = border_dots[order_high_area]
    border_dots_score = border_dots_score[order_high_area]

    border_arr, border_start, border_len = np.unique(border_dots, return_index=True, return_counts=True, axis=0)

    border_list = list()
    for border, start, length in zip(border_arr, border_start, border_len):
        border_list.append((border[0], border[1], np.mean(border_dots_score[start:start+length]) ,length))

    # cumsum_score = np.cumsum(border_dots_score)
    return border_list

def merge_areas(area_id_map:np.ndarray, score_map:np.ndarray, score_threshold:float)->np.ndarray:
    border_list = get_borders(area_id_map, score_map)
    borders = np.array(border_list, dtype=[('area_h', int), ('area_l', int), ('score', int), ('length', int)])
    




    # border_map = np.sort(border_map, axis=1)
    # border_map = np.sort(border_map, axis=0)

    # border_adjs = border_map[:,0:2]
    # border_scores = np.cumsum(border_map[:,2])

test_area_id = np.zeros((50,50), dtype=int)
test_score_id = np.zeros((50,50), dtype=float)

test_area_id[:25,:25] = 1
test_area_id[:25,25:] = 2
test_area_id[25:,:25] = 3
test_area_id[25:,25:] = 4

test_score_id[23:28,:25] = 0.1
test_score_id[23:28,25:] = 0.2
test_score_id[:25,23:28] = 0.3
test_score_id[25:,23:28] = 0.4

get_borders(test_area_id, test_score_id)