from os import name,system
from random import choice
from colorama import init,Fore,Style
from threading import Thread,Lock,active_count
from sys import stdout
from time import sleep
import requests
import json

class Main:
    def clear(self):
        if name == 'posix':
            system('clear')
        elif name in ('ce', 'nt', 'dos'):
            system('cls')
        else:
            print("\n") * 120

    def SetTitle(self,title:str):
        if name == 'posix':
            stdout.write(f"\x1b]2;{title}\x07")
        elif name in ('ce', 'nt', 'dos'):
            system(f'title {title}')
        else:
            stdout.write(f"\x1b]2;{title}\x07")

    def ReadFile(self,filename,method):
        with open(filename,method,encoding='utf8') as f:
            content = [line.strip('\n') for line in f]
            return content

    def ReadJson(self,filename,method):
        with open(filename,method) as f:
            return json.load(f)

    def __init__(self):
        self.SetTitle('[One Man Builds Twitch Token Checker]')
        self.clear()

        self.title = Style.BRIGHT+Fore.MAGENTA+"""
                         ╔════════════════════════════════════════════════════════════════╗
                                          ╔═╗╔╗╔╔═╗╔╦╗╔═╗╔╗╔╔╗ ╦ ╦╦╦  ╔╦╗╔═╗                      
                                          ║ ║║║║║╣ ║║║╠═╣║║║╠╩╗║ ║║║   ║║╚═╗                      
                                          ╚═╝╝╚╝╚═╝╩ ╩╩ ╩╝╚╝╚═╝╚═╝╩╩═╝═╩╝╚═╝                      
                              ╔╦╗╦ ╦╦╔╦╗╔═╗╦ ╦  ╔╦╗╔═╗╦╔═╔═╗╔╗╔  ╔═╗╦ ╦╔═╗╔═╗╦╔═╔═╗╦═╗
                               ║ ║║║║ ║ ║  ╠═╣   ║ ║ ║╠╩╗║╣ ║║║  ║  ╠═╣║╣ ║  ╠╩╗║╣ ╠╦╝
                               ╩ ╚╩╝╩ ╩ ╚═╝╩ ╩   ╩ ╚═╝╩ ╩╚═╝╝╚╝  ╚═╝╩ ╩╚═╝╚═╝╩ ╩╚═╝╩╚═
                         ╚════════════════════════════════════════════════════════════════╝

        """
        print(self.title)

        config = self.ReadJson('[Data]/configs.json','r')

        self.use_proxy = config['use_proxy']
        self.proxy_type = config['proxy_type']
        self.threads_num = config['threads']

        print('')

        self.hits = 0
        self.bads = 0
        self.retries = 0
        self.lock = Lock()

    def GetRandomUserAgent(self):
        useragents = self.ReadFile('[Data]/useragents.txt','r')
        return choice(useragents)

    def PrintText(self,bracket_color:Fore,text_in_bracket_color:Fore,text_in_bracket,text):
        self.lock.acquire()
        stdout.flush()
        text = text.encode('ascii','replace').decode()
        stdout.write(Style.BRIGHT+bracket_color+'['+text_in_bracket_color+text_in_bracket+bracket_color+'] '+bracket_color+text+'\n')
        self.lock.release()

    def GetRandomProxy(self):
        proxies_file = self.ReadFile('[Data]/proxies.txt','r')
        proxies = {}
        if self.proxy_type == 1:
            proxies = {
                "http":"http://{0}".format(choice(proxies_file)),
                "https":"https://{0}".format(choice(proxies_file))
            }
        elif self.proxy_type == 2:
            proxies = {
                "http":"socks4://{0}".format(choice(proxies_file)),
                "https":"socks4://{0}".format(choice(proxies_file))
            }
        else:
            proxies = {
                "http":"socks5://{0}".format(choice(proxies_file)),
                "https":"socks5://{0}".format(choice(proxies_file))
            }
        return proxies

    def TitleUpdate(self):
        while True:
            self.SetTitle(f'[One Man Builds Twitch Token Checker] ^| HITS: {self.hits} ^| BADS: {self.bads} ^| RETRIES: {self.retries} ^| THREADS: {active_count()-1}')
            sleep(0.1)

    def TokenCheck(self,token):
        try:
            headers = {
                'User-Agent':self.GetRandomUserAgent(),
                'Authorization':f'OAuth {token}'
            }

            response = ''

            link = 'https://id.twitch.tv/oauth2/validate'

            if self.use_proxy == 1:
                response = requests.get(link,headers=headers,proxies=self.GetRandomProxy())
            else:
                response = requests.get(link,headers=headers)

            if 'client_id' in response.text:
                self.PrintText(Fore.MAGENTA,Fore.WHITE,'HIT',token)
                with open('[Data]/[Results]/hits.txt','a',encoding='utf8') as f:
                    f.write(token+'\n')
                response_data = response.text.replace('\n','')
                with open('[Data]/[Results]/detailed_hits.txt','a',encoding='utf8') as f:
                    f.write(f'{token} | {response_data}\n')
                self.hits += 1
            elif 'invalid access token' in response.text:
                self.PrintText(Fore.RED,Fore.WHITE,'BAD',token)
                with open('[Data]/[Results]/bads.txt','a',encoding='utf8') as f:
                    f.write(token+'\n')
                self.bads += 1
            else:
                self.retries += 1
                self.TokenCheck(token)
        except:
            self.retries += 1
            self.TokenCheck(token)

    def Start(self):
        Thread(target=self.TitleUpdate).start()
        tokens = self.ReadFile('[Data]/tokens.txt','r')
        for token in tokens:
            Run = True
            while Run:
                if active_count() <= self.threads_num:
                    Thread(target=self.TokenCheck,args=(token,)).start()
                    Run = False

if __name__ == "__main__":
    main = Main()
    main.Start()