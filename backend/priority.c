#include <string.h>
#include "priority.h"
int calculate_priority(const char *severity, int people) {
 int base=200; if(!strcmp(severity,"Critical")) base=1000; else if(!strcmp(severity,"High")) base=700; else if(!strcmp(severity,"Medium")) base=400; return base + people*25;
}
