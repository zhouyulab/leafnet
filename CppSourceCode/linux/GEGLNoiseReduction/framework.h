#pragma once

extern "C"
{
	void gegl_denoise(float* image_array, int r_len, int c_len, int iteration);
}