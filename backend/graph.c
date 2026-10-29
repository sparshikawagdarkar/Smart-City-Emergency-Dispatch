#include <stdio.h>
#include "graph.h"
void graph_init(Graph*g,int n){g->n=n;for(int i=0;i<MAX_NODES;i++)for(int j=0;j<MAX_NODES;j++)g->weight[i][j]=(i==j?0:1000000);}
int graph_load_csv(Graph*g,const char*path){FILE*f=fopen(path,"r");if(!f)return 0;char line[128];fgets(line,sizeof(line),f);int a,b,w;while(fgets(line,sizeof(line),f)){if(sscanf(line,"%d,%d,%d",&a,&b,&w)==3&&a>=1&&b>=1&&a<=g->n&&b<=g->n){g->weight[a-1][b-1]=w;g->weight[b-1][a-1]=w;}}fclose(f);return 1;}
void graph_free(Graph*g){(void)g;}
