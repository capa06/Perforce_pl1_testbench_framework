#ifndef DRV_PCAP_H
#define DRV_PCAP_H

#include "icera_global.h"

#include "iobuf.h"
#include "os_abs.h"

#define PCAP_LINKTYPE_ETHERNET  1       /* DIX and 802.3 Ethernet */
#define PCAP_LINKTYPE_PPP       9       /* PPP */
#define PCAP_LINKTYPE_RAW       101     /* Raw IP packet */

typedef struct drv_pcap_t {
    unsigned int size;
    unsigned int snaplen;
    unsigned int linktype;
    os_MutexHandle mutex;
    int fd;
} drv_pcap_t;

drv_pcap_t *drv_pcap_open(char *filename, unsigned int linktype, unsigned int snaplen);
void drv_pcap_capture(drv_pcap_t *pcap, void *buf, int len);
void drv_pcap_capture_iobuf(drv_pcap_t *pcap, iobuf_t *iobuf);

extern DXP_UNCACHED unsigned int drv_pcap_netif_snaplen;
extern DXP_UNCACHED unsigned int drv_pcap_ip_snaplen;

#endif

