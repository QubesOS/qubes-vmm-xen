#define DHCP_OPTIONS_LEN 96U

#include "string.h"
#include <stdio.h>

/* lwIP includes. */
#include "lwip/memp.h" 
#include "lwip/stats.h"
#include "lwip/dhcp.h"
#include "lwip/sockets.h"

#define DHCP_MAGIC_COOKIE 0x63538263UL

static struct ip_addr server_ip;
/* parameters to propose */
static struct {
  struct ip_addr ip;
  struct ip_addr netmask;
  struct ip_addr gw;
  struct ip_addr dns1;
  struct ip_addr dns2;
  uint32_t lease_time;
} dhcp_params;

// DHCP options
struct S_DhcpOptions
{
   unsigned nDHCPOpt;
   char     nLen;
};

/* forward declaration */
int process_dhcp_msg (struct dhcp_msg *msg, int *pSize);
int fill_dhcp_options (struct dhcp_msg *msg, int nDhcpType);
static u8_t *dhcp_get_option_ptr(struct dhcp_msg *msg, u8_t option_type);
void recv_from_lwip(void *arg, struct udp_pcb *upcb, struct pbuf *p,
		                               struct ip_addr *addr, u16_t port);
int bind_dhcp(void);

/* "public" functions begin */

/* use:
 * 1. configure with lwip_dhcp_config
 * 2. start with lwip_dhcp_init (lwip must be already initialized)
 */

void lwip_dhcp_init(struct netif *netif) {
	server_ip.addr = netif->ip_addr.addr;
	dhcp_params.lease_time = 86400;

	bind_dhcp();
}

void lwip_dhcp_config(const char *param, const char *value) {
  if (!strcmp(param, "ip")) {
	dhcp_params.ip.addr = inet_addr(value);
  } else if (!strcmp(param, "gw")) {
	dhcp_params.gw.addr = inet_addr(value);
  } else if (!strcmp(param, "netmask")) {
	dhcp_params.netmask.addr = inet_addr(value);
  } else if (!strcmp(param, "dns1")) {
	dhcp_params.dns1.addr = inet_addr(value);
  } else if (!strcmp(param, "dns2")) {
	fprintf(stderr, "dhcp: WARNING: DNS2 not supported\n");
	dhcp_params.dns2.addr = inet_addr(value);
  }
}

void recv_from_lwip(void *arg, struct udp_pcb *upcb, struct pbuf *p,
		                       struct ip_addr *addr, u16_t port)
{
	struct dhcp_msg msg;
	struct pbuf *cur, *p_out;
	int offset;
	int nSize = 0;
	int bUniCast;
	struct ip_addr dst_addr;

	LWIP_DEBUGF(DHCP_DEBUG | 1, ("dhcp: received packet addr: %x, port %d\n", addr->addr, port));
		
	if (p->tot_len > sizeof (struct dhcp_msg)) {
		fprintf(stderr, "DHCP: Packet to big (%u > %lu)\n", p->tot_len, sizeof (struct dhcp_msg));
		return;
	}
	pbuf_copy_partial(p, &msg, sizeof(struct dhcp_msg), 0);

	/*if msg is too short,
	If all bootP fields have been read*/
	if (p->tot_len < sizeof(struct dhcp_msg) - DHCP_OPTIONS_LEN)
	{
		fprintf(stderr, "DHCP: Message truncated (length was %d)\r\n", p->tot_len);
		return;
	}

	msg.sname[sizeof (msg.sname) - 1] = 0;
	msg.file [sizeof (msg.file)  - 1] = 0;

	/* ensure that options are terminated */
	if (p->tot_len < sizeof(struct dhcp_msg)) {
		msg.options[p->tot_len - (sizeof(struct dhcp_msg) - DHCP_OPTIONS_LEN)] = DHCP_OPTION_END;
	}

	/*we have only to answer to BOOTREQUEST msg*/
	if (msg.op != DHCP_BOOTREQUEST)
	{
		fprintf(stderr, "DHCP: DhcpSrv Request %d not processed\r\n", msg.op);
		return;
	}

	/* if packet was sent to our unicast address -> will reply directly; otherwise will reply to broadcast */
	bUniCast = ((addr->addr != htonl (INADDR_NONE)) 
                     && (addr->addr != htonl (INADDR_ANY))) ;

	if (process_dhcp_msg ( &msg, &nSize))
	{
		LWIP_DEBUGF(DHCP_DEBUG | 1, ("dhcp: message processed\n"));
		/*if no source address was specified reply with a broadcast*/
		if (!bUniCast)
		{
			dst_addr.addr = htonl (INADDR_NONE);
		} else {
			dst_addr.addr = addr->addr;
		}

		p_out = pbuf_alloc(PBUF_TRANSPORT, nSize, PBUF_RAM);
		if (p_out == NULL) {
			fprintf(stderr, "dhcp: pbuf_alloc failed\n");
			return;
		}
		memcpy(p_out->payload, &msg, nSize);
		LWIP_DEBUGF(DHCP_DEBUG | 1, ("DhcpSrv: send %d bytes\n", nSize));
		if (udp_sendto(upcb, p_out, &dst_addr, port) != ERR_OK)
		{
			fprintf(stderr, "sendto error\r\n");
		}
		pbuf_free(p_out);
	}
}

/* "public" functions end */


int bind_dhcp()
{
	struct udp_pcb *upcb;

	upcb = udp_new();
	if (upcb == NULL) {
		fprintf(stderr, "dhcp: udp_new failed\n");
		return 1;
	}

	udp_recv(upcb, recv_from_lwip, NULL);
	if (udp_bind(upcb, IP_ADDR_ANY, DHCP_SERVER_PORT) != ERR_OK) {
		fprintf(stderr, "dhcp: udp_bind failed\n");
		return 1;
	}

	return 0;
}

#define  SizeOfTab(x)   (sizeof (x) / sizeof (x[0]))

/*******************************************************************************
 Name         : process_dhcp_msg
 Description  : Process DHCP msg : return TRUE if an answer has been prepared
                if so, pSize contains size of packet to send
*******************************************************************************/
int process_dhcp_msg (struct dhcp_msg *msg, int *pSize)
{
	unsigned char 	*p;
	int            	i, nDhcpType = 0;
	int				isOK = 1;


	if (msg->cookie == DHCP_MAGIC_COOKIE)
	{
		/*search DHCP message type*/
		p = dhcp_get_option_ptr (msg, DHCP_OPTION_MESSAGE_TYPE);

		if (p!=NULL) 
		{
			/*找到*/
			nDhcpType = *(p+2);
		} else
		  fprintf(stderr, "DHCP: Message type not found\n");
	} else 
		fprintf(stderr, "DHCP: Cookie mismatch %x != %lx\n", msg->cookie, DHCP_MAGIC_COOKIE);

	/*client must send request with "Your IP" set to INADDR_ANY*/
    if (msg->yiaddr.addr != INADDR_ANY)   
	{
		LWIP_DEBUGF(DHCP_DEBUG | 1, ("Address already assigned,return fail\n"));
		return 0;
	}

	/* process each message type */
	switch (nDhcpType)
	{
        case 0           	:    /*BootP*/
		case DHCP_DISCOVER	:
			/* perhaps client prefer some IP? */
            p  = dhcp_get_option_ptr(msg, DHCP_OPTION_REQUESTED_IP);
            if (p!=NULL)
            {
            	msg->ciaddr = * (struct ip_addr *) (p+2); 
               	fprintf(stderr, "DHCP: Client requested address %x\n", msg->ciaddr.addr);
            }

			/* XXX insert some dynamic allocation here if needed */

            /*populate the packet to be returned*/
            msg->op = DHCP_BOOTREPLY;                           /* reply to DHCP_DISCOVER*/
            msg->yiaddr = dhcp_params.ip; /* proposed IP */
			
			/* fill rest of options (DNS, routers etc) */
           	*pSize = fill_dhcp_options (msg, DHCP_OFFER);

			/* send the reply */
			return 1;

            break ;

		case DHCP_REQUEST :
			LWIP_DEBUGF(DHCP_DEBUG | 1, ("DHCPREQUEST:\n"));

			/*search field server ID if specified should be us*/
			p = dhcp_get_option_ptr (msg, DHCP_OPTION_SERVER_ID);
			if (p != NULL)
			{
			  isOK = (*(uint32_t*)(p+2) == server_ip.addr);
			}

			/*search field REQUEST ADDR in options
			  if specified should fit database*/
			p  = dhcp_get_option_ptr (msg, DHCP_OPTION_REQUESTED_IP);
			if (p!=NULL)
			{
			  isOK = ( *(uint32_t*)(p+2) == dhcp_params.ip.addr ) ;
			}
			if (isOK)
			{
			  LWIP_DEBUGF(DHCP_DEBUG | 1, ("Previously allocated address acked\n"));

			  /*populate the packet to be returned*/
			  msg->op = DHCP_BOOTREPLY;
			  msg->yiaddr = dhcp_params.ip;

			  *pSize = fill_dhcp_options (msg, DHCP_ACK);
			}
			else
			{
			  LWIP_DEBUGF(DHCP_DEBUG | 1, ("Client %x requested address which was not allocated\n",
				  msg->ciaddr.addr ));

			  return 0; // do not answer
			}

			return 1;
			
			break;

		case DHCP_DECLINE :
			LWIP_DEBUGF(DHCP_DEBUG | 1, ("DHCPDECLINE:\n"));
			break;

		case DHCP_RELEASE :
			LWIP_DEBUGF(DHCP_DEBUG | 1, ("DHCPRELEASE:\n"));
			break;
		case DHCP_INFORM:
			/*populate the packet to be returned*/
			msg->op = DHCP_BOOTREPLY;
			msg->yiaddr = dhcp_params.ip;

			*pSize = fill_dhcp_options (msg, DHCP_ACK);
			return 1;
			break;
			
		default:
			//LWIP_DEBUGF(DHCP_DEBUG | 1, ("Default: not processed command\r\n"));
			break;

	} // switch type

	// do not answer if not requested explicite
	return  0;

} // process_dhcp_msg

/* from lwip/core/dhcp.c */
static u8_t *dhcp_get_option_ptr(struct dhcp_msg *msg, u8_t option_type)
{
  u8_t overload = DHCP_OVERLOAD_NONE;

  /* start with options field */
  u8_t *options = (u8_t *)msg->options;
  u16_t offset = 0;
  /* at least 1 byte to read and no end marker, then at least 3 bytes to read? */
  while ((offset < DHCP_OPTIONS_LEN) && (options[offset] != DHCP_OPTION_END)) {
	/* LWIP_DEBUGF(DHCP_DEBUG, ("msg_offset=%"U16_F", q->len=%"U16_F, msg_offset, q->len)); */
	/* are the sname and/or file field overloaded with options? */
	if (options[offset] == DHCP_OPTION_OVERLOAD) {
	  LWIP_DEBUGF(DHCP_DEBUG | LWIP_DBG_TRACE | 2, ("overloaded message detected\n"));
	  /* skip option type and length */
	  offset += 2;
	  overload = options[offset++];
	}
	/* requested option found */
	else if (options[offset] == option_type) {
	  LWIP_DEBUGF(DHCP_DEBUG | LWIP_DBG_TRACE, ("option found at offset %"U16_F" in options\n", offset));
	  return &options[offset];
	  /* skip option */
	} else {
	  LWIP_DEBUGF(DHCP_DEBUG, ("skipping option %"U16_F" in options\n", options[offset]));
	  /* skip option type */
	  offset++;
	  /* skip option length, and then length bytes */
	  offset += 1 + options[offset];
	}
  }
  /* is this an overloaded message? */
  if (overload != DHCP_OVERLOAD_NONE) {
	u16_t field_len;
	if (overload == DHCP_OVERLOAD_FILE) {
	  LWIP_DEBUGF(DHCP_DEBUG | LWIP_DBG_TRACE | 1, ("overloaded file field\n"));
	  options = (u8_t *)&msg->file;
	  field_len = DHCP_FILE_LEN;
	} else if (overload == DHCP_OVERLOAD_SNAME) {
	  LWIP_DEBUGF(DHCP_DEBUG | LWIP_DBG_TRACE | 1, ("overloaded sname field\n"));
	  options = (u8_t *)&msg->sname;
	  field_len = DHCP_SNAME_LEN;
	  /* TODO: check if else if () is necessary */
	} else {
	  LWIP_DEBUGF(DHCP_DEBUG | LWIP_DBG_TRACE | 1, ("overloaded sname and file field\n"));
	  options = (u8_t *)&msg->sname;
	  field_len = DHCP_FILE_LEN + DHCP_SNAME_LEN;
	}
	offset = 0;

	/* at least 1 byte to read and no end marker */
	while ((offset < field_len) && (options[offset] != DHCP_OPTION_END)) {
	  if (options[offset] == option_type) {
		LWIP_DEBUGF(DHCP_DEBUG | LWIP_DBG_TRACE, ("option found at offset=%"U16_F"\n", offset));
		return &options[offset];
		/* skip option */
	  } else {
		LWIP_DEBUGF(DHCP_DEBUG | LWIP_DBG_TRACE, ("skipping option %"U16_F"\n", options[offset]));
		/* skip option type */
		offset++;
		offset += 1 + options[offset];
	  }
	}
  }
  return NULL;
}

/*******************************************************************************
 Name         : fill_dhcp_options
 Description  : fill DHCP fields
*******************************************************************************/
int fill_dhcp_options (struct dhcp_msg  *msg, int nDhcpType)
{
	unsigned char  *pOpt = (unsigned char *) (msg->options);
	int             i;
	static struct S_DhcpOptions sDhcpOpt [] =
	{
	  {   DHCP_OPTION_MESSAGE_TYPE,   1, },
	  {   DHCP_OPTION_SERVER_ID,      4, },
	  {   DHCP_OPTION_SUBNET_MASK,    4, },
	  {   DHCP_OPTION_ROUTER,         4, },
	  {   DHCP_OPTION_DNS_SERVER,     4, },
	  {   DHCP_OPTION_LEASE_TIME,     4, },
	  {   DHCP_OPTION_T1,             4, },
	  {   DHCP_OPTION_T2,             4, },
	  {   DHCP_OPTION_END,            0, },
	};

	
	for (i=0 ; i < SizeOfTab(sDhcpOpt) ; i++)
	{
		if (sDhcpOpt[i].nLen!=0) 
		{
			*pOpt++ = (unsigned char) sDhcpOpt[i].nDHCPOpt ; 
			*pOpt++ = (unsigned char) sDhcpOpt[i].nLen;
		}
	 
		switch (sDhcpOpt[i].nDHCPOpt)
		{
		case DHCP_OPTION_MESSAGE_TYPE    :  * pOpt = (unsigned char) nDhcpType ; break ; 
		case DHCP_OPTION_SERVER_ID	     :  * (uint32_t *) pOpt = server_ip.addr; break ;
		case DHCP_OPTION_SUBNET_MASK     :  * (uint32_t *) pOpt = dhcp_params.netmask.addr; break ;
		case DHCP_OPTION_ROUTER          :  * (uint32_t *) pOpt = dhcp_params.gw.addr; break ;
		case DHCP_OPTION_DNS_SERVER      :  * (uint32_t *) pOpt = dhcp_params.dns1.addr;  break; 
		case DHCP_OPTION_LEASE_TIME      :  * (uint32_t *) pOpt = htonl (dhcp_params.lease_time);  break ;
		case DHCP_OPTION_T1              :
		case DHCP_OPTION_T2              :  * (uint32_t *) pOpt = htonl (dhcp_params.lease_time);  break ;
		case DHCP_OPTION_END             : 
			*pOpt++ = DHCP_OPTION_END;
			*pOpt++ = DHCP_OPTION_END;
			*pOpt++ = DHCP_OPTION_END;
			break;
		} //switch option

		pOpt += sDhcpOpt[i].nLen ;    //points on next field
	} //for all option

	/* Back to the length of the outgoing packets */
	return (int) (pOpt - (unsigned char*) msg);
} 

