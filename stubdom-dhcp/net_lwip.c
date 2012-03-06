
/* lwip network adapter */

#include <lwip/pbuf.h>
#include "net.h"
#include <lwip/init.h>
#include <lwip/netif.h>
#include <netif/etharp.h>
#include <lwip/tcpip.h>

#define IF_IPADDR   0x0a000001
#define IF_NETMASK  0xffffff00

static int lwip_inited;
static int lwip_restrict;
static char *lwip_ip;
static unsigned char rawmac[6] = { 0x00, 0x11, 0x22, 0x33, 0x44, 0x55 }; // FIXME
static VLANClientState *lwip_vc;

VLANState *lwip_vlan;
static char *lwip_model = NULL;
static char *lwip_name = NULL;

/* from dhcpserver.c */
void lwip_dhcp_init(struct netif *netif);

#if defined(DEBUG_LWIP)
static void hex_dump(FILE *f, const uint8_t *buf, int size)
{
    int len, i, j, c;

    for(i=0;i<size;i+=16) {
        len = size - i;
        if (len > 16)
            len = 16;
        fprintf(f, "%08x ", i);
        for(j=0;j<16;j++) {
            if (j < len)
                fprintf(f, " %02x", buf[i+j]);
            else
                fprintf(f, "   ");
        }
        fprintf(f, " ");
        for(j=0;j<len;j++) {
            c = buf[i+j];
            if (c < ' ' || c > '~')
                c = '.';
            fprintf(f, "%c", c);
        }
        fprintf(f, "\n");
    }
}
#endif

int lwip_can_output(void)
{
    return !lwip_vc || qemu_can_send_packet(lwip_vc);
}

void lwip_output(const uint8_t *pkt, int pkt_len)
{
#ifdef DEBUG_LWIP
    printf("lwip output:\n");
    hex_dump(stdout, pkt, pkt_len);
#endif
    if (!lwip_vc)
        return;
    qemu_send_packet(lwip_vc, pkt, pkt_len);
}

int lwip_is_inited(void)
{
    return lwip_inited;
}

static void lwip_receive(void *opaque, const uint8_t *buf, int size)
{
	struct eth_hdr *ethhdr;
	struct pbuf *p, *q;
	struct netif *netif = (struct netif*)opaque;

#ifdef DEBUG_LWIP
    printf("lwip input:\n");
    hex_dump(stdout, buf, size);
#endif

	/* move received packet into a new pbuf */
	p = pbuf_alloc(PBUF_RAW, size, PBUF_POOL);

#if ETH_PAD_SIZE
  pbuf_header(p, -ETH_PAD_SIZE); /* drop the padding word */
#endif

  /* We iterate over the pbuf chain until we have read the entire
   * packet into the pbuf. */
  for(q = p; q != NULL && size > 0; q = q->next) {
    /* Read enough bytes to fill this pbuf in the chain. The
     * available data in the pbuf is given by the q->len
     * variable. */
    memcpy(q->payload, buf, size < q->len ? size : q->len);
    buf += q->len;
    size -= q->len;
  }

#if ETH_PAD_SIZE
  pbuf_header(p, ETH_PAD_SIZE); /* reclaim the padding word */
#endif
  /* points to packet payload, which starts with an Ethernet header */
  ethhdr = p->payload;

  switch (htons(ethhdr->type)) {
  /* IP packet? */
  case ETHTYPE_IP:
#ifdef DEBUG_LWIP
	  fprintf(stderr, " ->IP\n");
#endif
#if 0
/* CSi disabled ARP table update on ingress IP packets.
   This seems to work but needs thorough testing. */
    /* update ARP table */
    etharp_ip_input(netif, p);
#endif
    /* skip Ethernet header */
    pbuf_header(p, -(int16_t)sizeof(struct eth_hdr));
    /* pass to network layer */
    if (ip_input(p, netif) == ERR_MEM)
      /* Could not store it, drop */
      pbuf_free(p);
    break;

  case ETHTYPE_ARP:
#ifdef DEBUG_LWIP
	printf(" ->ARP\n");
#endif
    /* pass p to ARP module  */
    etharp_arp_input(netif, (struct eth_addr *) netif->hwaddr, p);
    break;

  case 0x86DD:
#ifdef DEBUG_LWIP
	fprintf(stderr, " ->IP6 not supported yet\n");
#endif

  default:
#ifdef DEBUG_LWIP
	fprintf(stderr, " ->unknown (%x htons:%x)\n", ethhdr->type, htons(ethhdr->type));
#endif
    pbuf_free(p);
    p = NULL;
    break;
  }
}

/*
 * netfront_output():
 *
 * This function is called by the TCP/IP stack when an IP packet
 * should be sent. It calls the function called low_level_output() to
 * do the actual transmission of the packet.
 *
 */

static err_t
qemu_output(struct netif *netif, struct pbuf *p,
      struct ip_addr *ipaddr)
{

 /* resolve hardware address, then send (or queue) packet */
  return etharp_output(netif, p, ipaddr);

}

static err_t
low_level_output(struct netif *netif, struct pbuf *p)
{ 
#ifdef DEBUG_LWIP
    printf("lwip output:\n");
#endif
  if (!lwip_vc)
    return ERR_OK;

#ifdef ETH_PAD_SIZE
  pbuf_header(p, -ETH_PAD_SIZE); /* drop the padding word */
#endif

  /* Send the data from the pbuf to the interface, one pbuf at a
     time. The size of the data in each pbuf is kept in the ->len
     variable. */
  if (!p->next) {
#ifdef DEBUG_LWIP
    hex_dump(stdout, p->payload, p->len);
#endif
    /* Only one fragment, can send it directly */
	qemu_send_packet(lwip_vc, p->payload, p->len);
  } else {
    unsigned char data[p->tot_len], *cur;
    struct pbuf *q;

    for(q = p, cur = data; q != NULL; cur += q->len, q = q->next)
      memcpy(cur, q->payload, q->len);
#ifdef DEBUG_LWIP
    hex_dump(stdout, data, p->tot_len);
#endif
	qemu_send_packet(lwip_vc, data, p->tot_len);
  }

#if ETH_PAD_SIZE
  pbuf_header(p, ETH_PAD_SIZE);         /* reclaim the padding word */
#endif

  return ERR_OK;
}


err_t
netif_qemu_init(struct netif *netif)
{

	unsigned char *mac = netif->state;

	netif->flags = NETIF_FLAG_BROADCAST;
	netif->linkoutput = low_level_output;
	netif->output = qemu_output;
	netif->name[0] = 'e';
	netif->name[1] = 'n';

	/* set MAC hardware address */
	netif->hwaddr_len = 6;
	netif->hwaddr[0] = mac[0];
	netif->hwaddr[1] = mac[1];
	netif->hwaddr[2] = mac[2];
	netif->hwaddr[3] = mac[3];
	netif->hwaddr[4] = mac[4];
	netif->hwaddr[5] = mac[5];

	/* maximum transfer unit */
	netif->mtu = 1500;

	/* No interesting per-interface state */
	netif->state = NULL;


	return ERR_OK;
}


static __DECLARE_SEMAPHORE_GENERIC(tcpip_is_up, 0);
static void tcpip_bringup_finished(void *p)
{
  fprintf(stderr, "TCP/IP bringup ends.\n");
  up(&tcpip_is_up);

  if (!lwip_inited) {
	  lwip_inited = 1;
	  lwip_init();
  }

  lwip_vc = qemu_new_vlan_client(lwip_vlan, lwip_model, lwip_name,
		  lwip_receive, NULL, p);
  lwip_vc->info_str[0] = '\0';

  fprintf(stderr, "registering DHCP server\n");
  lwip_dhcp_init((struct netif*)p);
}

/* 
 * Utility function to bring the whole lot up.  Call this from app_main() 
 * or similar -- it starts netfront and have lwIP start its thread,
 * which calls back to tcpip_bringup_finished(), which 
 * lets us know it's OK to continue.
 */
int net_lwip_init(VLANState *vlan, const char *model, const char *name, const char *ip, const char *mask, const char *gateway)
{
  struct netif *netif;
  struct ip_addr ipaddr = { htonl(IF_IPADDR) };
  struct ip_addr netmask = { htonl(IF_NETMASK) };
  struct ip_addr gw = { 0 };

  lwip_model = model;
  lwip_name = name;
  lwip_vlan = vlan;

  fprintf(stderr, "Waiting for network.\n");
  if (ip) {
    ipaddr.addr = inet_addr(ip);
  }
  if (mask) {
	  netmask.addr = inet_addr(mask);
  }
  if (gateway) {
	  gw.addr = inet_addr(gateway);
  }
  fprintf(stderr, "IP %x netmask %x gateway %x.\n",
          ntohl(ipaddr.addr), ntohl(netmask.addr), ntohl(gw.addr));

  fprintf(stderr, "TCP/IP bringup begins.\n");

  netif = xmalloc(struct netif);
  tcpip_init(tcpip_bringup_finished, netif);

  netif_add(netif, &ipaddr, &netmask, &gw, rawmac,
            netif_qemu_init, ip_input);
  netif_set_default(netif);
  netif_set_up(netif);

  down(&tcpip_is_up);


  fprintf(stderr, "Network is ready.\n");
  return 0;
}


