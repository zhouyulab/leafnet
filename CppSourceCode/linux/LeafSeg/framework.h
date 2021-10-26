#pragma once

extern "C"
{
	void merge_areas(int** area_id_map, float** score_map, int r_len, int c_len, float score_threshold);
}