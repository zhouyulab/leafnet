#pragma once

extern "C"
{
	__declspec(dllexport) void merge_areas(int** area_id_map, float** score_map, int r_len, int c_len, float score_threshold);
}

#define WIN32_LEAN_AND_MEAN             // 从 Windows 头文件中排除极少使用的内容
// Windows 头文件
#include <windows.h>