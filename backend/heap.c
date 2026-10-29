#include "heap.h"
static void swap(Incident *a, Incident *b){Incident t=*a;*a=*b;*b=t;}
void heap_init(MaxHeap *h){h->size=0;}
void heap_push(MaxHeap *h, Incident x){if(h->size>=300)return;int i=h->size++;h->items[i]=x;while(i>0){int p=(i-1)/2;if(h->items[p].priority>=h->items[i].priority)break;swap(&h->items[p],&h->items[i]);i=p;}}
int heap_pop(MaxHeap *h, Incident *out){if(h->size==0)return 0;*out=h->items[0];h->items[0]=h->items[--h->size];int i=0;for(;;){int l=2*i+1,r=2*i+2,b=i;if(l<h->size&&h->items[l].priority>h->items[b].priority)b=l;if(r<h->size&&h->items[r].priority>h->items[b].priority)b=r;if(b==i)break;swap(&h->items[i],&h->items[b]);i=b;}return 1;}
