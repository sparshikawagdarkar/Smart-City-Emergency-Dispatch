#ifndef GRAPH_H
#define GRAPH_H
#define MAX_NODES 32
typedef struct { int weight[MAX_NODES][MAX_NODES]; int n; } Graph;
void graph_init(Graph *g,int n); int graph_load_csv(Graph *g,const char *path); void graph_free(Graph *g);
#endif
