#include "framework.h"
#include <list>

int o_calc(int r, int c, int c_len) { return(c + (r * c_len)); }

#define POW2(a) ((a)*(a))
#define GEN_METRIC(before, center, after) POW2((center) * 2 - (before) - (after))

void gegl_denoise(float* image_array, int r_len, int c_len, int iteration)
{
	// Construct temp array
	int img_len = r_len * c_len;
	float* temp_array = new float[img_len];
	int offsets[8] = {
		o_calc(-1,-1, c_len), o_calc( 0,-1, c_len), o_calc( 1,-1, c_len),
		o_calc(-1, 0, c_len),                       o_calc( 1, 0, c_len),
		o_calc(-1, 1, c_len), o_calc( 0, 1, c_len), o_calc( 1, 1, c_len)};

	for (int iter = 0; iter < iteration; iter++)
	{
		// Copy input array to temp array
		for (int i = 0; i < img_len; i++){temp_array[i] = image_array[i];}
		// Denoise
		for (int r = 1; r < r_len-1; r++)
		{
			float* center_pix = temp_array + (r * c_len);

			for (int c = 1; c < c_len-1; c++)
			{
				// initialize original metrics for the horizontal, vertical and 2 diagonal metrics
				float metric_reference[4];
				for (int axis = 0; axis < 4; axis++)
				{ 
					float* before_pix = center_pix + offsets[axis];
					float* after_pix = center_pix + offsets[7-axis];
					metric_reference[axis] = GEN_METRIC(*before_pix, *center_pix, *after_pix);
				}
				// try smearing in data from all neighbours
				float sum = *center_pix;
				int count = 1;
				for (int direction = 0; direction < 8; direction++)
				{
					float* pix = center_pix + offsets[direction];
					float value = (*pix * 0.5f) + (*center_pix * 0.5f);
					bool valid = true; /* assume it will be valid */
					// check if the non-smoothing operating check is true if smearing from this direction for any of the axes
					for (int axis = 0; axis < 4; axis++)
					{
						float* before_pix = center_pix + offsets[axis];
						float* after_pix = center_pix + offsets[7 - axis];
						float  metric_new = GEN_METRIC(*before_pix, value, *after_pix);
						if (metric_new > metric_reference[axis])
						{
							// mark as not a valid smoothing, and break out of loop
							valid = 0; 
							break;
						}
					}
					if (valid) 
					{
						// we were still smooth in all axes, add up contribution to final result
						sum += value;
						count++;
					}
				}
				image_array[(r * c_len) + c - 1] = sum / count;
				center_pix++;
			}
		}
	}
	delete[] temp_array;
}