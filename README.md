# SDN-Based Intelligent DDoS Mitigator & Traffic Analyzer

Bu çalışma, Yazılım Tanımlı Ağlar (SDN) mimarisini kullanarak geleneksel ağ güvenliği yaklaşımlarına modern ve programlanabilir bir alternatif sunar. Projenin temel amacı, ağ trafiğini derinlemesine analiz ederek (L4 seviyesinde) hem görünürlük sağlamak hem de siber saldırılara karşı (özellikle DDoS) otonom bir savunma mekanizması geliştirmektir.

## 💻 Özellikler
- **Protokol Sınıflandırma:** HTTP, HTTPS, DNS, FTP, SMTP, SSH ve ICMP trafiğini gerçek zamanlı analiz eder.
- **DDoS Koruması:** Eşik değerini (Threshold) aşan IP adreslerini otomatik olarak 60 saniye boyunca bloklar.
- **Kalıcı Loglama:** Tüm saldırı girişimlerini `saldirilar.log` dosyasına zaman damgasıyla kaydeder.
- **OpenFlow 1.3:** Modern SDN standartlarına uygun olarak geliştirilmiştir.

## 🧠 Çalışma Mantığı
1. **Packet-In:** Switch, eşleşme bulamadığı yeni paketleri OpenFlow protokolü üzerinden kontrolcüye gönderir.
2. **Derin Analiz:** Kontrolcü, paketin Ethernet ve IP katmanlarını soyarak L4 (TCP/UDP/ICMP) başlıklarını inceler.
3. **PPS Takibi:** Her kaynak IP için saniyelik paket istatistikleri tutulur.
4. **Mitigation (Engelleme):** Eğer bir IP belirlenen eşiği aşarsa, switch'e o IP'den gelen tüm trafiği 'DROP' etmesi için yüksek öncelikli (priority=100) bir kural yazılır.

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

### Çalışma Anından Bazı Görseller
![HTTP Saldırı Tespiti](images/saldiri_log_1.png)
![DNS Saldırı Tespiti](images/saldiri_log_2.png)


## Saldırı Geçmişi

Yeni bir terminal açıp projenin olduğu klasörün içindeyken aşağıdaki komutu çalıştırdıktan sonra geçmiş saldırılarla ilgili detaylı bilgileri inceleyebilirsiniz.

    cat saldirilar.log

## Ekran Görüntüleri ve Kanıtlar

Sistemin çalışma mantığını ve saldırı anındaki tepkilerini içeren ekran görüntüleri `images` klasörü altında yer almaktadır.

* **Trafik Logları:** Normal ağ trafiğinin (ICMP, TCP vb.) kontrolcü tarafından nasıl sınıflandırıldığını gösteren terminal çıktıları.
* **Saldırı Tespiti:** hping3 saldırısı başladığında eşik değerin aşılması ve "SALDIRI ALARMI" mesajının tetiklenmesi.
* **Otomatik Engelleme:** Saldırgan IP'nin engellenmesi ve ardından gelen paketlerin drop edilmesi.
* **Kalıcı Kayıtlar:** `saldirilar.log` dosyasında tutulan zaman damgalı saldırı raporları.

> **Not:** Tüm görseller projenin doğrulanabilirliği için `/images` klasörüne commit edilmiştir.


## Lisans

MIT
