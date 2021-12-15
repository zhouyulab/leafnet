#pragma once

#define WIN32_LEAN_AND_MEAN             // 从 Windows 头文件中排除极少使用的内容
// Windows 头文件
#include <windows.h>

extern "C"
{
	__declspec(dllexport) void gegl_denoise(float* image_array, int r_len, int c_len, int iteration);
}