from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ipv4, tcp, udp, icmp
from ryu.lib import hub
from datetime import datetime 

class SmartDdosGuard(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SmartDdosGuard, self).__init__(*args, **kwargs)
        self.traffic_stats = {}
        self.threshold = 100 
        self.blocked_ips = set()
        self.protocol_map = {21: "FTP", 22: "SSH", 25: "SMTP", 53: "DNS", 80: "HTTP", 443: "HTTPS"}
        
        
        with open("saldirilar.log", "a") as f:
            f.write(f"\n--- Sistem Başlatıldı: {datetime.now()} ---\n")
            
        hub.spawn(self._monitor)

    def log_attack(self, ip, proto):
        zaman = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_mesaji = f"[{zaman}] SALDIRI ENGELLENDİ: Kaynak IP: {ip} | Hedef Protokol: {proto}\n"
        with open("saldirilar.log", "a") as f:
            f.write(log_mesaji)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]
        self._add_flow(datapath, 0, match, actions)

    def _add_flow(self, datapath, priority, match, actions, idle_timeout=0):
        parser = datapath.ofproto_parser
        inst = [parser.OFPInstructionActions(datapath.ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(datapath=datapath, priority=priority, match=match, 
                                instructions=inst, idle_timeout=idle_timeout)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']
        pkt = packet.Packet(msg.data)
        
        ip_pkt = pkt.get_protocol(ipv4.ipv4)
        if not ip_pkt:
            self._send_packet_out(datapath, msg.buffer_id, in_port, ofproto.OFPP_FLOOD, msg.data)
            return

        src_ip = ip_pkt.src
        dst_ip = ip_pkt.dst
        proto_name = "Bilinmeyen"

        
        icmp_pkt = pkt.get_protocol(icmp.icmp)
        tcp_pkt = pkt.get_protocol(tcp.tcp)
        udp_pkt = pkt.get_protocol(udp.udp)

        if icmp_pkt: proto_name = "ICMP (Ping)"
        elif tcp_pkt: proto_name = self.protocol_map.get(tcp_pkt.dst_port, f"TCP:{tcp_pkt.dst_port}")
        elif udp_pkt: proto_name = self.protocol_map.get(udp_pkt.dst_port, f"UDP:{udp_pkt.dst_port}")

        if src_ip in self.blocked_ips:
            return

        print(f"[LOG] {src_ip} -> {dst_ip} | Tür: {proto_name}")

        key = (src_ip, proto_name)
        self.traffic_stats[key] = self.traffic_stats.get(key, 0) + 1

        if self.traffic_stats[key] > self.threshold:
            print(f"!!! SALDIRI TESPİTİ: {src_ip} !!!")
            self.blocked_ips.add(src_ip)
            
            # DOSYAYA KAYDET
            self.log_attack(src_ip, proto_name)
            
            match = parser.OFPMatch(eth_type=0x0800, ipv4_src=src_ip)
            self._add_flow(datapath, 100, match, [], idle_timeout=60)
            return

        self._send_packet_out(datapath, msg.buffer_id, in_port, ofproto.OFPP_FLOOD, msg.data)

    def _send_packet_out(self, datapath, buffer_id, in_port, out_port, data):
        actions = [datapath.ofproto_parser.OFPActionOutput(out_port)]
        out = datapath.ofproto_parser.OFPPacketOut(datapath=datapath, buffer_id=buffer_id,
                                  in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)

    def _monitor(self):
        while True:
            hub.sleep(5)
            self.traffic_stats.clear()
