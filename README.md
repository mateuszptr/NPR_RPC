# NPR_RPC

Zdalne wykonywanie poleceń za pomocą RPC.

## Przygotowanie środowiska

Wymagania: python 3.5+, biblioteka asyncio i biblioteka rpcudp

```bash
pip3 install asyncio
pip3 install rpcudp
```

## Uruchomienie

Serwer może współbieżnie obsługiwać wielu klientów, klient uruchamia jedno polecenie na serwerze, po czym kończy działanie

Uruchomienie serwera:
```bash
python3 server.py <ip> <port dla rpc> <port wychodzący>
```

Uruchomienie klienta:
```bash
python3 client.py <polecenie> <ip serwera> <port rpc serwera> <ip klienta> <port rpc klienta> <port wychodzący klienta>
```

Po uruchomieniu, klient łączy się z serwerem. Gdy otrzyma potwierdzenie uruchomienia zadania, przesyła standardowe wejście na serwer
Polecenie podane przez klienta uruchamiane jest na serwerze w shellu. Możemy dzięki temu wysyłać złożone polecenia i korzystać z potoków.

## Przykładowe uruchomienie
```bash
python3 server.py "192.168.0.22" 1234 1235
```

```bash
python3 client.py "tr [:lower:] [:upper:] | sort" "192.168.0.14" 1234 "192.168.0.22" 4567 4568
```

