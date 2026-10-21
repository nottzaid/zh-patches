/* Mouse input for a Wine game without focus: posts window messages from inside the same wineserver.
   wclick list                 top-level windows (hwnd, pid, class, title, client size)
   wclick click <hwnd> x y     move + left click at client coordinates
   wclick move  <hwnd> x y     move only */
#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static BOOL CALLBACK list_cb(HWND h, LPARAM l)
{
    char cls[256], title[256];
    DWORD pid;
    RECT r;
    GetClassNameA(h, cls, sizeof cls);
    GetWindowTextA(h, title, sizeof title);
    GetWindowThreadProcessId(h, &pid);
    GetClientRect(h, &r);
    if (IsWindowVisible(h))
        printf("%p pid=%lu class='%s' title='%s' client=%ldx%ld\n", (void *)h, pid, cls, title, r.right, r.bottom);
    return TRUE;
}

int main(int argc, char **argv)
{
    if (argc < 2 || !strcmp(argv[1], "list")) {
        EnumWindows(list_cb, 0);
        return 0;
    }
    if (argc < 5) return 2;
    HWND h = (HWND)(UINT_PTR)strtoull(argv[2], NULL, 16);
    LPARAM pos = MAKELPARAM(atoi(argv[3]), atoi(argv[4]));
    if (!IsWindow(h)) { printf("no such window\n"); return 1; }
    PostMessageA(h, WM_MOUSEMOVE, 0, pos);
    Sleep(150);
    if (!strcmp(argv[1], "click")) {
        PostMessageA(h, WM_LBUTTONDOWN, MK_LBUTTON, pos);
        Sleep(120);
        PostMessageA(h, WM_LBUTTONUP, 0, pos);
        Sleep(150);
    }
    printf("ok\n");
    return 0;
}
