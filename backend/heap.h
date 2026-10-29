#ifndef HEAP_H
#define HEAP_H
#include "incident.h"
typedef struct { Incident items[300]; int size; } MaxHeap;
void heap_init(MaxHeap *h); void heap_push(MaxHeap *h, Incident x); int heap_pop(MaxHeap *h, Incident *out);
#endif
