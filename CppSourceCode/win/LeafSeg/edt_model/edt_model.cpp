#include "framework.h"
#include <iostream>
#include <map>
#include <set>
#include <algorithm>

using std::map;
using std::set;
using std::max;
using std::min;

struct border
{
	float len;
	float score;
};

struct merging_border
{
	int area;
	float bayes_score;
};

border merge_border(border a, border b)
{
	return { a.len + b.len,((a.score * a.len) + (b.score * b.len)) / (a.len + b.len) };
}


map<int, map<int, border> > get_borders(int** area_id_map, float** score_map, int r_len, int c_len)
{
	// border_map[area_0][area_1] = border(lenth, score)
	// area_1 > area_0
	map<int, map<int, border> > border_map = map<int, map<int, border> >();
	for (int r = 0; r < r_len - 1; r++)
	{
		for (int c = 0; c < c_len - 1; c++)
		{
			// Get areas adjust to point
			int areas[4]{ area_id_map[r][c],area_id_map[r][c + 1],area_id_map[r + 1][c],area_id_map[r + 1][c + 1] };
			std::sort(areas, areas + 4);
			if (areas[0] == 0 || areas[0] == areas[3]) { continue; }
			// if dot is border
			else
			{
				float smean = (score_map[r][c] + score_map[r][c + 1] + score_map[r + 1][c] + score_map[r + 1][c + 1]) / 4;
				for (int i = 0; i < 3; i++)
				{
					for (int j = i+1; j < 4; j++)
					{
						if (areas[i] == areas[j]) { continue; }
						else
						{
							map<int, map<int, border> >::iterator area_0_dict_iter = border_map.find(areas[i]);
							if (area_0_dict_iter == border_map.end())
							{
								border_map.insert(std::pair<int, map<int, border> >(areas[i], map<int, border>()));
								area_0_dict_iter = border_map.find(areas[i]);
							}
							map<int, border>::iterator area_1_dict_iter = area_0_dict_iter->second.find(areas[j]);
							if (area_1_dict_iter == area_0_dict_iter->second.end())
							{
								area_0_dict_iter->second.insert(std::pair<int, border>(areas[j], border { 0,0 }));
								area_1_dict_iter = area_0_dict_iter->second.find(areas[j]);
							}
							area_1_dict_iter->second.score = ((area_1_dict_iter->second.score * area_1_dict_iter->second.len) + smean) / (area_1_dict_iter->second.len + 1);
							area_1_dict_iter->second.len += 1;
						}
					}
				}
			}
		}
	}
	return border_map;
}

map<int, map<int, border> > merge_areas_with_map(int** area_id_map, int r_len, int c_len, map<int, map<int, border> > border_map, map<int, merging_border> merging_map)
{
	map<int, map<int, border> >::iterator iter_0, iter_2;
	map<int, border>::iterator iter_1, iter_3;
	map<int, merging_border>::iterator merging_map_iter;
	// area id map
	for (int r = 0; r < r_len; r++)
	{
		for (int c = 0; c < c_len; c++)
		{
			merging_map_iter = merging_map.find(area_id_map[r][c]);
			if (merging_map_iter != merging_map.end()) { area_id_map[r][c] = merging_map_iter->second.area; }
		}
	}
	// border_map
	map<int, map<int, border> > returning_border_map = map<int, map<int, border> >();
	for (iter_0 = border_map.begin(); iter_0 != border_map.end(); iter_0++)
	{
		// Get id of area_0 after merging
		merging_map_iter = merging_map.find(iter_0->first);
		int area_0;
		if (merging_map_iter != merging_map.end()) { area_0 = merging_map_iter->second.area; }
		else { area_0 = iter_0->first; }
		for (iter_1 = iter_0->second.begin(); iter_1 != iter_0->second.end(); iter_1++)
		{
			// Get id of area_1 after merging
			merging_map_iter = merging_map.find(iter_1->first);
			int area_1;
			if (merging_map_iter != merging_map.end()) { area_1 = merging_map_iter->second.area; }
			else { area_1 = iter_1->first; }
			float current_len = iter_1->second.len;
			float current_score = iter_1->second.score;
			// border removed
			if (area_0 == area_1) { continue; }
			// border no removed
			iter_2 = returning_border_map.find(area_0);
			if (iter_2 == returning_border_map.end())
			{
				returning_border_map.insert(std::pair<int, map<int, border> >(area_0, map<int, border>()));
				iter_2 = returning_border_map.find(area_0);
			}
			iter_3 = iter_2->second.find(area_1);
			if (iter_3 == iter_2->second.end())
			{
				iter_2->second.insert(std::pair<int, border>(area_1, border { current_len, current_score }));
			}
			else
			{
				iter_3->second = merge_border(iter_3->second, { current_len, current_score });
			}
		}
	}
	return returning_border_map;
}


map<int, map<int, border> > remove_isolated_areas(int** area_id_map, int r_len, int c_len, map<int, map<int, border> > border_map, set<int> edge_areas, float score_threshold)
{
	// TEMP VARS
	map<int, map<int, border> >::iterator iter_0;
	map<int, border>::iterator iter_1;
	map<int, merging_border>::iterator iter_2;
	int area_0, area_1;
	// TEMP VARS END
	map<int, int> area_adj_count = map<int, int>();
	map<int, merging_border> one_adj_merge_map;
	map<int, merging_border> two_adj_merge_map;
	set<int> mult_adj_set;

	for (iter_0 = border_map.begin(); iter_0 != border_map.end(); iter_0++)
	{
		// record adj_count for 
		area_0 = iter_0->first;
		for (iter_1 = iter_0->second.begin(); iter_1 != iter_0->second.end(); iter_1++)
		{
			area_1 = iter_1->first;
			float len = iter_1->second.len;
			float score = iter_1->second.score;
			float bayes_score = ((score * len) + (score_threshold * 48)) / (len + 48);
			// Area 0
			if (edge_areas.count(area_0) > 0) { mult_adj_set.insert(area_0); }
			// // If not edge area
			else
			{
				// // If not adjusting mult areas
				if (mult_adj_set.count(area_0) == 0)
				{
					// // If adjusting two areas, now adjusting mult areas
					if (two_adj_merge_map.count(area_0) > 0)
					{
						mult_adj_set.insert(area_0);
						two_adj_merge_map.erase(area_0);
					}
					else
					{
						// // If adjusting one area, now adjusting two areas
						iter_2 = one_adj_merge_map.find(area_0);
						if (iter_2 != one_adj_merge_map.end())
						{
							if (iter_2->second.bayes_score < bayes_score) { two_adj_merge_map.insert(std::pair<int, merging_border>(area_0, merging_border { iter_2->second.area, iter_2->second.bayes_score })); }
							else { two_adj_merge_map.insert(std::pair<int, merging_border>(area_0, merging_border { area_1, bayes_score })); }
							one_adj_merge_map.erase(area_0);
						}
						// // If not recorded, now adjusting one area
						else
						{
							one_adj_merge_map.insert(std::pair<int, merging_border>(area_0, merging_border { area_1, bayes_score }));
						}
					}
				}
			}
			// Area 1
			if (edge_areas.count(area_1) > 0) { mult_adj_set.insert(area_1); }
			// // If not edge area
			else
			{
				// // If not adjusting mult areas
				if (mult_adj_set.count(area_1) == 0)
				{
					// // If adjusting two areas, now adjusting mult areas
					if (two_adj_merge_map.count(area_1) > 0)
					{
						mult_adj_set.insert(area_1);
						two_adj_merge_map.erase(area_1);
					}
					else
					{
						// // If adjusting one area, now adjusting two areas
						iter_2 = one_adj_merge_map.find(area_1);
						if (iter_2 != one_adj_merge_map.end())
						{
							if (iter_2->second.bayes_score < bayes_score) { two_adj_merge_map.insert(std::pair<int, merging_border>(area_1, merging_border { iter_2->second.area, iter_2->second.bayes_score })); }
							else { two_adj_merge_map.insert(std::pair<int, merging_border>(area_1, merging_border { area_0, bayes_score })); }
							one_adj_merge_map.erase(area_1);
						}
						// // If not recorded, now adjusting one area
						else
						{
							one_adj_merge_map.insert(std::pair<int, merging_border>(area_1, merging_border { area_0, bayes_score }));
						}
					}
				}
			}
		}
	}

	one_adj_merge_map.insert(two_adj_merge_map.begin(), two_adj_merge_map.end());
	return merge_areas_with_map(area_id_map, r_len, c_len, border_map, one_adj_merge_map);
}

void merge_areas(int** area_id_map, float** score_map, int r_len, int c_len, float score_threshold)
{
	// TEMP VARS
	map<int, map<int, border> >::iterator iter_0;
	map<int, border>::iterator iter_1;
	map<int, merging_border>::iterator area_merge_iter;
	map<int, int>::iterator rev_iter;
	// TEMP VARS END

	// Edge dots.
	set<int> edge_areas;
	for (int r = 0; r < r_len; r++)
	{
		edge_areas.insert(area_id_map[r][0]);
		edge_areas.insert(area_id_map[r][c_len - 1]);
	}
	for (int c = 0; c < c_len; c++)
	{
		edge_areas.insert(area_id_map[0][c]);
		edge_areas.insert(area_id_map[r_len - 1][c]);
	}

	bool merging = true;
	map<int, map<int, border> > border_map = get_borders(area_id_map, score_map, r_len, c_len);
	while (merging)
	{
		merging = false;
		// An area could ONLY merge one BEST match area in one time!
		// merging_map[area_0] = {area_1, score, len}
		// merging_map_rev[area_1] = area_0
		map<int, merging_border> merging_map = map<int, merging_border>();
		map<int, int> merging_map_rev = map<int, int>();
		// Generate mergable_borders
		for (iter_0 = border_map.begin(); iter_0 != border_map.end(); iter_0++)
		{
			int area_0 = iter_0->first;
			map<int, border> area_0_borders = iter_0->second;
			for (iter_1 = area_0_borders.begin(); iter_1 != area_0_borders.end(); iter_1++)
			{
				int area_1 = iter_1->first;
				float len = iter_1->second.len;
				float score = iter_1->second.score;
				float bayes_score = ((score * len) + (score_threshold * 48)) / (len + 48);
				// border is currently solid
				if (score > score_threshold) { continue; }
				// find existing merge for area_0 (forward)
				area_merge_iter = merging_map.find(area_0);
				if (area_merge_iter != merging_map.end())
				{
					// existing merge is better
					if (area_merge_iter->second.bayes_score < bayes_score) { continue; }
					// or remove existing merge
					else { merging_map_rev.erase(area_merge_iter->second.area); merging_map.erase(area_0); }
				}
				// find existing merge for area_0 (reverse)
				else
				{
					rev_iter = merging_map_rev.find(area_0);
					if (rev_iter != merging_map_rev.end())
					{
						int area_rev = rev_iter->second;
						area_merge_iter = merging_map.find(area_rev);
						// existing merge is better
						if (area_merge_iter->second.bayes_score < bayes_score) { continue; }
						// or remove existing merge
						else { merging_map.erase(area_rev); merging_map_rev.erase(area_0);}
					}
				}
				// find existing merge for area_1 (forward)
				area_merge_iter = merging_map.find(area_1);
				if (area_merge_iter != merging_map.end())
				{
					// existing merge is better
					if (area_merge_iter->second.bayes_score < bayes_score) { continue; }
					// or remove existing merge
					else { merging_map_rev.erase(area_merge_iter->second.area); merging_map.erase(area_1); }
				}
				// find existing merge for area_0 (reverse)
				else
				{
					rev_iter = merging_map_rev.find(area_1);
					if (rev_iter != merging_map_rev.end())
					{
						int area_rev = rev_iter->second;
						area_merge_iter = merging_map.find(area_rev);
						// existing merge is better
						if (area_merge_iter->second.bayes_score < bayes_score) { continue; }
						// or remove existing merge
						else { merging_map.erase(area_rev); merging_map_rev.erase(area_1);}
					}
				}
				merging_map.insert(std::pair<int, merging_border>(area_0, merging_border { area_1, bayes_score }));
				merging_map_rev.insert(std::pair<int, int>(area_1, area_0));
				merging = true;
			}
		}
		border_map = merge_areas_with_map(area_id_map, r_len, c_len, border_map, merging_map);
		// Update edge areas
		for (map<int, merging_border>::iterator merging_map_iter = merging_map.begin(); merging_map_iter != merging_map.end(); merging_map_iter++)
		{
			if (edge_areas.count(merging_map_iter->first) > 0) { edge_areas.insert(merging_map_iter->second.area); }
			if (edge_areas.count(merging_map_iter->second.area) > 0) { edge_areas.insert(merging_map_iter->first); }
		}
		// remove isolated areas
		border_map = remove_isolated_areas(area_id_map, r_len, c_len, border_map, edge_areas, score_threshold);
	}
}