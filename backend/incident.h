#ifndef INCIDENT_H
#define INCIDENT_H
typedef struct { int id; char type[40]; char severity[20]; int people; int location; int priority; char priority_label[20]; char vehicle_id[20]; char status[30]; } Incident;
#endif
