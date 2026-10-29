#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "incident.h"
#include "priority.h"
#include "heap.h"
#include "vehicle.h"
#include "graph.h"
#include "dijkstra.h"

#define MAX_INCIDENTS 200
static Incident incidents[MAX_INCIDENTS];
static int incident_count = 0;

static void load_incidents(void) {
    FILE *f = fopen("data/incidents.csv", "r");
    if (!f) return;
    char line[512];
    if (fgets(line, sizeof(line), f) == NULL) { fclose(f); return; }
    while (fgets(line, sizeof(line), f) && incident_count < MAX_INCIDENTS) {
        Incident in;
        char *tok = strtok(line, ",\r\n"); if (!tok) continue; in.id = atoi(tok);
        tok = strtok(NULL, ",\r\n"); if (!tok) continue; snprintf(in.type, sizeof(in.type), "%s", tok);
        tok = strtok(NULL, ",\r\n"); if (!tok) continue; snprintf(in.severity, sizeof(in.severity), "%s", tok);
        tok = strtok(NULL, ",\r\n"); if (!tok) continue; in.people = atoi(tok);
        tok = strtok(NULL, ",\r\n"); if (!tok) continue; in.location = atoi(tok);
        tok = strtok(NULL, ",\r\n"); if (!tok) continue; in.priority = atoi(tok);
        tok = strtok(NULL, ",\r\n"); if (!tok) continue; snprintf(in.priority_label, sizeof(in.priority_label), "%s", tok);
        tok = strtok(NULL, ",\r\n"); if (!tok) continue; snprintf(in.vehicle_id, sizeof(in.vehicle_id), "%s", tok);
        tok = strtok(NULL, ",\r\n"); if (!tok) continue; snprintf(in.status, sizeof(in.status), "%s", tok);
        incidents[incident_count++] = in;
    }
    fclose(f);
}
static void print_incident(const Incident *i) {
    printf("%d | %s | %s | people=%d | location=%d | priority=%d (%s) | vehicle=%s | status=%s\n", i->id, i->type, i->severity, i->people, i->location, i->priority, i->priority_label, i->vehicle_id, i->status);
}
int main(int argc, char **argv) {
    if (argc < 2) { printf("Commands: list, queue, vehicles, route START END, search ID, sort, add TYPE SEVERITY PEOPLE LOCATION\n"); return 0; }
    load_incidents();
    if (!strcmp(argv[1], "list")) {
        for (int i=0;i<incident_count;i++) print_incident(&incidents[i]);
    } else if (!strcmp(argv[1], "queue")) {
        MaxHeap h; heap_init(&h);
        for (int i=0;i<incident_count;i++) heap_push(&h, incidents[i]);
        Incident x; while (heap_pop(&h, &x)) print_incident(&x);
    } else if (!strcmp(argv[1], "vehicles")) {
        print_vehicles("data/vehicles.csv");
    } else if (!strcmp(argv[1], "route") && argc >= 4) {
        int start=atoi(argv[2]), end=atoi(argv[3]);
        Graph g; graph_init(&g, 7); graph_load_csv(&g, "data/roads.csv");
        int dist=0; int path[32], n=0;
        if (dijkstra(&g,start,end,&dist,path,&n)) { printf("Shortest distance: %d\nRoute: ",dist); for(int i=0;i<n;i++) printf("%d%s",path[i],i==n-1?"\n":" -> "); }
        else printf("No route found. Nodes must be between 1 and 7.\n");
        graph_free(&g);
    } else if (!strcmp(argv[1], "search") && argc >= 3) {
        int id=atoi(argv[2]), found=0;
        for(int i=0;i<incident_count;i++) if(incidents[i].id==id){print_incident(&incidents[i]);found=1;break;}
        if(!found) printf("Incident %d not found.\n",id);
    } else if (!strcmp(argv[1], "sort")) {
        for(int i=0;i<incident_count;i++) for(int j=0;j<incident_count-i-1;j++) if(incidents[j].priority<incidents[j+1].priority){Incident t=incidents[j];incidents[j]=incidents[j+1];incidents[j+1]=t;}
        for(int i=0;i<incident_count;i++) print_incident(&incidents[i]);
    } else if (!strcmp(argv[1], "add") && argc >= 6) {
        Incident x; memset(&x,0,sizeof(x)); x.id=1000+incident_count;
        snprintf(x.type,sizeof(x.type),"%s",argv[2]); snprintf(x.severity,sizeof(x.severity),"%s",argv[3]); x.people=atoi(argv[4]); x.location=atoi(argv[5]);
        x.priority=calculate_priority(x.severity,x.people); snprintf(x.priority_label,sizeof(x.priority_label),"%s",x.severity); snprintf(x.vehicle_id,sizeof(x.vehicle_id),"-"); snprintf(x.status,sizeof(x.status),"Registered");
        FILE *f=fopen("data/incidents.csv","a"); if(!f){perror("Could not open incidents.csv");return 1;}
        fprintf(f,"%d,%s,%s,%d,%d,%d,%s,%s,%s\n",x.id,x.type,x.severity,x.people,x.location,x.priority,x.priority_label,x.vehicle_id,x.status); fclose(f);
        printf("Added incident %d with priority %d.\n",x.id,x.priority);
    } else { printf("Unknown command or missing arguments.\n"); return 1; }
    return 0;
}
