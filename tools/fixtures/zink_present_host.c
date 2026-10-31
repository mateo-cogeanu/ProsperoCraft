/* SPDX-License-Identifier: GPL-3.0-or-later */
#include <stdio.h>
int zink_present_run(void);
void zink_probe_report(const char *stage,int result){printf("%d:%s\n",result,stage);}
int main(void){int result=zink_present_run();if(!result)puts("PASS actual GLFW/Zink animation and triple teardown/reinit; host offscreen only");return result?1:0;}
