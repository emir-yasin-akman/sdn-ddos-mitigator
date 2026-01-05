# SDN-Based Intelligent DDoS Mitigator & Traffic Analyzer

Bu çalışma, Yazılım Tanımlı Ağlar (SDN) mimarisini kullanarak geleneksel ağ güvenliği yaklaşımlarına modern ve programlanabilir bir alternatif sunar. Projenin temel amacı, ağ trafiğini derinlemesine analiz ederek (L4 seviyesinde) hem görünürlük sağlamak hem de siber saldırılara karşı (özellikle DDoS) otonom bir savunma mekanizması geliştirmektir.

## 💻 Özellikler
- **Protokol Sınıflandırma:** HTTP, HTTPS, DNS, FTP, SMTP, SSH ve ICMP trafiğini gerçek zamanlı analiz eder.
- **DDoS Koruması:** Eşik değerini (Threshold) aşan IP adreslerini otomatik olarak 60 saniye boyunca bloklar.
- **Kalıcı Loglama:** Tüm saldırı girişimlerini `saldirilar.log` dosyasına zaman damgasıyla kaydeder.
- **OpenFlow 1.3:** Modern SDN standartlarına uygun olarak geliştirilmiştir.

## 🛠️ Kurulum
1. Mininet ve Ryu'yu yükleyin.

2. Projeyi klonlayın:
   ```bash
   git clone https://github.com/emir-yasin-akman/sdn-ddos-mitigator.git
   cd sdn-ddos-mitigator

3. Ryu Kontrolcüsünü başlatın:
    ```bash
    ryu-manager smart_controller.py
NOT: Eğer kontrolcüyü başlatma esnasında herhangi bir hata alırsanız kontrolcüyü bir sanal ortamda (venv) başlatırsanız sorun ortadan kalkacaktır.

4. Mininet topolojisini kurun:
    ```bash
    sudo mn --controller=remote,ip=127.0.0.1 --switch=ovs,protocols=OpenFlow13 --topo=single,3 

## Test Senaryosu

    Normal Trafik: h1 ping -c 4 h2 (Loglarda ICMP olarak görünür)
    Normal Trafik: h1 wget http://10.0.0.2 (Loglarda HTTP olarak görünür)
    Normal Trafik: h1 nslookup google.com h2 (Loglarda DNS olarak görünür)
    Normal Trafik: h1 nc -zv 10.0.0.2 21 (Loglarda FTP olarak görünür)
    Normal Trafik: h1 nc -zv 10.0.0.2 22 (Loglarda SSH olarak görünür)
    Normal Trafik: h1 nc -zv 10.0.0.2 25 (Loglarda SMTP olarak görünür)
    Normal Trafik: h1 nc -zv 10.0.0.2 443 (Loglarda HTTPS olarak görünür)

    Saldırı Simülasyonu: h1 hping3 --flood -S -p 80 10.0.0.2 (Loglarda SALDIRI uyarısı verir ve h1 bloklanır)
    Saldırı Simülasyonu: h3 hping3 --flood --udp -p 53 10.0.0.2 (Loglarda SALDIRI uyarısı verir ve h3 bloklanır)

## Saldırı Geçmişi

Yeni bir terminal açıp projenin olduğu klasörün içindeyken aşağıdaki komutu çalıştırdıktan sonra geçmiş saldırılarla ilgili detaylı      bilgileri inceleyebilirsiniz.

    cat saldirilar.log

## Lisans

MIT
