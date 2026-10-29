#include <stdio.h>
#include "vehicle.h"
void print_vehicles(const char *path){FILE*f=fopen(path,"r");if(!f){perror(path);return;}char line[256];while(fgets(line,sizeof(line),f))printf("%s",line);fclose(f);}
