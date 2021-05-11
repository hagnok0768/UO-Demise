# ======================================================================================================================
AUTHOR : WHATEVER
STHEALTH CLIENT
# ======================================================================================================================
from py_stealth import *
from datetime import datetime, timedelta
from time import sleep

# ======================================================================================================================
# CONSTANTS
# ======================================================================================================================

TAILOR_VENDOR = 0xb0278  # ID NPC 
BLACKSMITH_VENDOR = 0xb0299  # ID NPC 
VENDOR_CONTEXT_MENU = 1  # NAO ALTERAR
BOD_TYPE = 0x2258  # NAO ALTERAR
TAILOR_BOD_COLOR = 1155  # NAO ALTERAR
BLACKSMITH_BOD_COLOR = 1102  # NAO ALTERAR
TAKE_TAILOR = True  # CASO NAO QUEIRA BODS DE TAILOR POR False.
TAKE_BLACKSMITH = True  # CASO NAO QUEIRA BODS DE BS POR False.
TAILOR_BOOK = 0  # ID, NAO ALTERAR
BLACKSMITH_BOOK = 0  # ID, NAO ALTERAR
TAILOR_MSG = 'Pegando Tailor BOD'
BLACKSMITH_MSG = 'Pegando BS BOD'
WAIT_TIME = 1000  # NAO ALTERAR
WAIT_LAG_TIME = 10000  # NAO ALTERAR
MY_PROFILES = [
    'login1', 'login2', 'login3', 'login4', 'login5', 'login6', 'login7'    
]

# ======================================================================================================================
# Variables
# ======================================================================================================================

tailor_bods, blacksmith_bods = 0, 0
conta = 0

# ======================================================================================================================
# Utils
# ======================================================================================================================

def wait_lag(wait_time=WAIT_TIME, lag_time=WAIT_LAG_TIME):
    Wait(wait_time)
    CheckLag(lag_time)
    return None


def close_gumps():
    while IsGump():
        if not Connected():
            return False
        if not IsGumpCanBeClosed(GetGumpsCount() - 1):
            return False
        CloseSimpleGump(GetGumpsCount() - 1)
    return True   
    
# Function to find a book by name in your pack
def findNamedBook(searchStr):
    res = FindTypeEx(8793, 0, Backpack(), False)
    FoundBooks = GetFindedList()
    for book in FoundBooks:
        tooltip = GetTooltip(book)
        if searchStr in tooltip:
           return book
    # some error since no matching book found
    return 0


# ======================================================================================================================
# Boder
# ======================================================================================================================

class Boder(object):
    def __init__(self, name):
        self.name = name
        self.time_order = datetime.now()
        self.backpack_item_count = 0

    @staticmethod
    def get_bods_count(bod_color):
        if bod_color == TAILOR_BOD_COLOR:
            global tailor_bods
            tailor_bods += CountEx(BOD_TYPE, bod_color, Backpack())
            AddToSystemJournal('Total de Tailor Bods Coletados = {0}'.format(tailor_bods))
        else:
            global blacksmith_bods
            blacksmith_bods += CountEx(BOD_TYPE, bod_color, Backpack())
            AddToSystemJournal('Total de BS Bods Coletados = {0}'.format(blacksmith_bods))
                          
        
    def check_backpack(self):
        backpack_item_count = GetTooltipRec(Backpack())
        for item in backpack_item_count:
            if len(item['Params']) == 4:
                self.backpack_item_count = int(item['Params'][0])
                break
        if self.backpack_item_count == 125:
            AddToSystemJournal('{0} BAG CHEIA.'.format(self.name))
            return True
        return False

    def collect_bods(self, msg, vendor, menu, bod_color, bod_book):
        while True:
            start_time = datetime.now()
            AddToSystemJournal(msg)
            wait_lag(WAIT_TIME // 2)
            SetContextMenuHook(vendor, menu)
            wait_lag(WAIT_TIME // 2)
            RequestContextMenu(vendor)
            wait_lag()
            WaitGump('1')
            wait_lag()
            if bod_book:
                while FindTypeEx(BOD_TYPE, bod_color, Backpack(), False) > 1:
                    MoveItem(FindItem(), 1, bod_book, 0, 0, 0)
                    wait_lag()
                    close_gumps()
            if InJournalBetweenTimes('in your backpack|may be available in about', start_time,
                                     datetime.now()) > 0:
                break
        self.get_bods_count(bod_color)
        return None


if __name__ == '__main__':
    # ==================================================================================================================
    # Start Script
    # ==================================================================================================================  
    ClearJournal()
    ClearSystemJournal()
    if not TAKE_TAILOR and not TAKE_BLACKSMITH:
        quit(AddToSystemJournal('???????? ??????! ' +
                                '???? ?? ???? ?? ?????????? TAKE_TAILOR ??? TAKE_BLACKSMITH ?????? ???? True.' +
                                '?????? ??????????.'))
    for i in range(len(MY_PROFILES)):
        MY_PROFILES[i] = Boder(MY_PROFILES[i])
    while True:
        for profile in MY_PROFILES:
            if datetime.now() > profile.time_order:
                if True:
                    ChangeProfile(profile.name)
                    SetARStatus(True)
                    Connect()
                    AddToSystemJournal('Conectando...')
                    Wait(2000)
                    conta = 0
                    while not Connected():
                        Wait(1000)
                        if not Connected() and conta > 13:
                            Connect()
                            Wait(2000)
                            conta = 0 
                            AddToSystemJournal('Reconectando...')
                        conta = conta + 1
                       
                if not profile.check_backpack(): 
                
                    Wait(1000) 
                    
                    close_gumps()
                    
                    if TAKE_TAILOR:
                        Wait(1000)
                        TAILOR_BOOK = findNamedBook('TS') # find our tailor book
                        Wait(1000) 
                        profile.collect_bods(TAILOR_MSG,
                                             TAILOR_VENDOR,
                                             VENDOR_CONTEXT_MENU,
                                             TAILOR_BOD_COLOR,
                                             TAILOR_BOOK)  
                                                
                                                   
                    
                    if TAKE_BLACKSMITH:                  
                        Wait(1000)              
                        BLACKSMITH_BOOK = findNamedBook('BS') # find our smith book                       
                        Wait(1000)      
                        profile.collect_bods(BLACKSMITH_MSG,
                                             BLACKSMITH_VENDOR,
                                             VENDOR_CONTEXT_MENU,
                                             BLACKSMITH_BOD_COLOR,
                                             BLACKSMITH_BOOK) 
                                               
                else:
                    profile.get_bods_count(TAILOR_BOD_COLOR)
                    profile.get_bods_count(BLACKSMITH_BOD_COLOR)
                    MY_PROFILES.remove(profile)
                SetARStatus(False)
                while Connected():
                    Disconnect()
                    Wait(2500)
                profile.time_order = datetime.now() + timedelta(hours=1)
                if len(MY_PROFILES) == 0:
                    AddToSystemJournal('Parando o Macro, Bag cheia!!!')
                    quit('Stop')
                if profile == MY_PROFILES[-1]:
                    tailor_bods, blacksmith_bods = 0, 0

        sleep(60)
    # ==================================================================================================================
    # End Script
    # ==================================================================================================================