# Before worrying about about segment displays, I want to make a Pygame simulation that can display all of the information
# I gather from the NFC reader and IR sensors
import pygame
import nfc
from nfc.clf import RemoteTarget
from ndef import TextRecord
# import lcd

class TextRect:
  def __init__(self, r = pygame.Rect(0,0,0,0), rectCol = (0, 0, 0), tex = "", texCol = (255,255,255), texSize = 30):
    self.rect = pygame.Rect(r)
    self.text = tex
    self.textColor = texCol
    self.textSize = texSize
    self.rectColor = rectCol

  def output(self):
    pygame.draw.rect(screen, self.rectColor, self.rect)
    screen.blit(pygame.font.Font(None, self.textSize).render(str(self.text), True, self.textColor), (self.rect.left + 5, 
    self.rect.top + self.rect.height // 2.5))

class Scale(TextRect):
    def __init__(self, r = pygame.Rect(0,0,0,0), rectCol = (0, 0, 0), tex = "", texCol = (255,255,255), texSize = 30, scaleP = 0):
        TextRect.__init__(self, r, rectCol, tex, texCol, texSize)
        self.scalePos = 0

    def shift(self, amt = 0):
        self.scalePos += amt
        pygame.draw.rect(screen, white, self.rect)
        self.rect = pygame.Rect.move(self.rect, 0, 30 * amt)
        self.output()

    def output(self):
        pygame.draw.rect(screen, self.rectColor, self.rect)
        screen.blit(pygame.font.Font(None, self.textSize).render(str(abs(self.scalePos)), True, self.textColor), (self.rect.left + 5, 
        self.rect.top + self.rect.height // 2.5))


class Card:
    idCount = 0
    def __init__(self, p = -1, nam = "", batk = 0, bhp = 0, sigs = [], matk = -1, mhp = -1, msigs = "NA"):
        self.baseName = nam
        self.curName = nam
        self.baseAttack = batk
        if matk <= -1:
            self.modAttack = batk
        else:
            self.modAttack = matk
        self.curAttack = self.modAttack

        self.baseHealth = bhp
        if mhp <= -1:
            self.modHealth = bhp
        else:  
            self.modHealth = mhp
        self.curHealth = self.modHealth

        self.baseSigils = sigs
        self.modSigils = sigs if msigs == "NA" else msigs
        self.curSigils = self.modSigils
        self.trackers = {}
        self.activeAttackMod = 0
        Card.idCount += 1
        self.id = Card.idCount
        self.pos = p
        self.sigilSetup()

    def __eq__(self, other):
        return self.id == other.id

    def getXpos(self):
        if self.pos < 4:
            return 150 + abs(self.pos - 3) * 220
        return 150 + (self.pos - 4) * 220

    def getYpos(self):
        return 100 if self.pos < 4 else 450
    
    def changePos(self, newPos, cardOnBoard = True):
        global sideCard
        #Exception handling
        if newPos not in range(0,8):
            print("Failed to change position. New position out of range.\nAttempted to move card " + str(self.pos) + " into position " + str(newPos))
            return
        if cardsList[newPos].curName != "":
            print("Failed to change position. Attempted to move into an occupied space.\nAttempted to move card " + str(self.pos) + " into position " + str(newPos)) 
            return
        
        tempPos = self.pos
        cardsList[newPos] = self
        cardsList[newPos].pos = newPos
        if cardOnBoard:
            cardsList[tempPos] = Card(tempPos)
        else:
            sideCard = Card(tempPos)

    def sigilSetup(self):
        # Movement sigils set up - starts facing right
        if "sprinter" in self.curSigils:
            self.trackers["sprinted"] = False
            if autoMove:
                self.trackers["sprintDir"] = "right"
        if "hefty" in self.curSigils:
            self.trackers["hefted"] = False
            if autoMove:
                self.trackers["heftDir"] = "right"
        if "rampager" in self.curSigils:
            self.trackers["rampaged"] = False
            if autoMove:
                self.trackers["rampageDir"] = "right"

    def output(self):
        pygame.draw.rect(screen, black, pygame.Rect(self.getXpos(), self.getYpos(), 200, 300))
        if self.curName == "":
            return
        
        nameOut = pygame.font.Font(None, 30).render(self.curName, True, white)
        attackOut = pygame.font.Font(None, 70).render(str(self.curAttack) if self.curAttack >= 0 else "0", True, green)
        healthOut = pygame.font.Font(None, 70).render(str(self.curHealth) if self.curHealth >= 0 else "0", True, red)

        if self.pos > 3:
            screen.blit(nameOut, (self.getXpos() + 10, self.getYpos() + 20))
            screen.blit(attackOut, (self.getXpos() + 10, self.getYpos() + 240))
            screen.blit(healthOut, (self.getXpos() + 160, self.getYpos() + 240))
            for i in range(len(self.curSigils)):
                screen.blit(pygame.font.Font(None, 30).render(self.curSigils[i].title(), True, darkOrange), (self.getXpos() + 10, i * 40 + self.getYpos() + 90))
                # If the sigil is a movement one, print out the direction that the card is currently facing
                if self.curSigils[i] == "sprinter":
                    screen.blit(pygame.font.Font(None, 30).render("->" if self.trackers["sprintDir"] == "right" else "<-", True, darkOrange), (self.getXpos() + 100, i * 40 + self.getYpos() + 90))
        else:
            screen.blit(pygame.transform.flip(nameOut, True, True), (self.getXpos() + 10, self.getYpos() + 240))
            screen.blit(pygame.transform.flip(attackOut, True, True), (self.getXpos() + 160, self.getYpos() + 20))
            screen.blit(pygame.transform.flip(healthOut, True, True), (self.getXpos() + 10, self.getYpos() + 20))
            for i in range(len(self.curSigils)):
                screen.blit(pygame.transform.flip(pygame.font.Font(None, 30).render(self.curSigils[i].title(), True, darkOrange), True, True), (self.getXpos() + 10, i * -40 + self.getYpos() + 200))
                # If the sigil is a movement one, print out the direction that the card is currently facing
                if self.curSigils[i] == "sprinter":
                    screen.blit(pygame.font.Font(None, 30).render("->" if self.trackers["sprintDir"] == "right" else "<-", True, darkOrange), (self.getXpos() + 100, i * 40 + self.getYpos() + 90))

    def sideOutput(self):
        sideXpos = 1120
        sideYpos = 280
        pygame.draw.rect(screen, black, pygame.Rect(sideXpos, sideYpos, 200, 300))
        if self.curName == "":
            return

        nameOut = pygame.font.Font(None, 30).render(self.curName, True, white)
        attackOut = pygame.font.Font(None, 70).render(str(self.curAttack), True, green)
        healthOut = pygame.font.Font(None, 70).render(str(self.curHealth), True, red)

        screen.blit(nameOut, (sideXpos + 10, sideYpos + 20))
        screen.blit(attackOut, (sideXpos + 10, sideYpos + 240))
        screen.blit(healthOut, (sideXpos + 160, sideYpos + 240))
        for i in range(len(self.curSigils)):
            screen.blit(pygame.font.Font(None, 30).render(self.curSigils[i].title(), True, darkOrange), (sideXpos + 10, i * 40 + sideYpos + 90))

    def attack(self, other):
        if self.curAttack <= 0 or "repulsive" in other.curSigils:
            return
        
        # Direct attack
        if other.curName == "" or ("airborne" in self.curSigils and "mighty leap" not in other.curSigils) or ("waterborne" in other.curSigils and "aquanaut" not in self.curSigils):
            if self.pos < 4:
                theScale.shift(self.curAttack)
            else: theScale.shift(-1 * self.curAttack)

            pygame.mixer.Sound.play(directHitSound)
            pygame.display.update()
            pygame.time.delay(800)

        # Hit other card
        else:
            # Armored sigil integration
            if "armored" not in other.curSigils:
                # Bastion sigil integration
                if "bastion" in other.curSigils:
                    other.curHealth -= round(self.curAttack/2 + 0.1)
                else:
                    other.curHealth -= self.curAttack
                # defending card afflicted by touch of death
                if "touch of death" in self.curSigils:
                    other.trackers["deathtouched"] = True
            # If Armored, the defender doesn't take damage and loses armored
            else:
                other.curSigils.pop("armored")
            
            other.output()
            pygame.mixer.Sound.play(hitSound)
            pygame.display.update()
            pygame.time.delay(800)

            if "sharp quills" in other.curSigils:
                self.curHealth -= 1
                pygame.mixer.Sound.play(hitSound)
                pygame.display.update()
                pygame.time.delay(800)

def playSound(sound, delayTime = 0):
    pygame.mixer.Sound.play(sound)
    pygame.time.delay(delayTime)

def nfcCardPresent(reader):
    return reader.sense(RemoteTarget('106A'), RemoteTarget('106B'), RemoteTarget('212F')) is not None

def getNfcText(reader):
    target = reader.sense(RemoteTarget('106A'), RemoteTarget('106B'), RemoteTarget('212F'))

    if target is not None:
        try:
            myTag = nfc.tag.activate(reader, target)
            return myTag.ndef.records[0].text
        except AttributeError:
            print("getNfcText()_Error: read failed :( You may have removed the card too soon")
        except IndexError:
            print("getNfcText()_Error: No text on card :(")
    return ""

# Returns when the mouse is clicked
def waitForClick():
    stop = False
    while True:
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP:
                return

# Given a card, create the appropriate amount of bones for it on death
def makeBones(deadCard):
    global resources
    
    if deadCard.pos < 4:
        cardSide = "top"
    else:
        cardSide = "bot"

    if "bone king" in deadCard.curSigils:
        resources[cardSide + "bones"] += 4
    else: resources[cardSide + "bones"] += 1
    outputBones()
    playSound(makeBoneSound, 800)

def fullAttack(attacker, defender):
    if attacker.curName == "":
        return
    pygame.draw.rect(screen, red, (defender.getXpos() + 50, 400 if defender.pos <= 3 else 425, 100, 25))
    pygame.draw.rect(screen, red, (attacker.getXpos() + 50, 400 if attacker.pos <= 3 else 425, 100, 25))
    pygame.display.update()
    pygame.time.delay(500)

    attacker.attack(defender)
    # death check for under 1 health or deathtouched
    checkIfDead(defender.pos)
    checkIfDead(attacker.pos)

    pygame.draw.rect(screen, white, (defender.getXpos() + 50, 400 if defender.pos <= 3 else 425, 100, 25))
    pygame.draw.rect(screen, white, (attacker.getXpos() + 50, 400 if attacker.pos <= 3 else 425, 100, 25))
    pygame.display.update()

def attackProperPosition(attackerPos):
    attacker = cardsList[attackerPos]
    leftDefenderPos = abs(8 - attackerPos)
    rightDefenderPos = abs(6 - attackerPos)
    # Check for left attack
    if "bifurcated strike" in attacker.curSigils:
        if leftDefenderPos < len(cardsList) and leftDefenderPos != attackerPos:
            fullAttack(attacker, cardsList[leftDefenderPos])
    if "trifurcated strike" in attacker.curSigils:
        if leftDefenderPos < len(cardsList) and leftDefenderPos != attackerPos:
            fullAttack(attacker, cardsList[leftDefenderPos])

    # Check for middle attack
    if "double strike" in attacker.curSigils:
        fullAttack(attacker, cardsList[getOpposingPos(attackerPos)])
        fullAttack(attacker, cardsList[getOpposingPos(attackerPos)])
        if "trifurcated strike" in attacker.curSigils:
            fullAttack(attacker, cardsList[getOpposingPos(attackerPos)])
    if "trifurcated strike" in attacker.curSigils or "bifurcated strike" not in attacker.curSigils:
        fullAttack(attacker, cardsList[getOpposingPos(attackerPos)])

    # Check for right attack
    # Dumb stupid patch - pos 7 can't right attack and ends up hitting 1, just returning the function fixes this :)
    if attackerPos == 7:
        return
    if "bifurcated strike" in attacker.curSigils:
        if rightDefenderPos != attackerPos:
            fullAttack(attacker, cardsList[rightDefenderPos])
    if "trifurcated strike" in attacker.curSigils:
        if rightDefenderPos != attackerPos:
            fullAttack(attacker, cardsList[rightDefenderPos])

def getOpposingPos(cardPos):
    return abs(7 - cardPos)

def doAttacks():
    if whoseTurn == "top":
        for i in range(0,4):
            attackProperPosition(i)

    else:
        for i in range(4, 8):
            attackProperPosition(i)

def sprint(cardPos):
    sCard = cardsList[cardPos]
    sCard.trackers["sprinted"] = True
    onEdge = True
    posDirection = 1

    if sCard.pos == 0 or sCard.pos == 4:
        posDirection = 1
        sCard.trackers["sprintDir"] = "right"
    elif sCard.pos == 3 or sCard.pos == 7:
        posDirection = -1
        sCard.trackers["sprintDir"] = "left"

    else:
        onEdge = False
        # if set to automove, the card will move in the direction set to it
        if autoMove:
            if sCard.trackers["sprintDir"] == "right":
                # The direction the card will move relative to the positions of the card spaces
                posDirection = 1
            else:
                posDirection = -1
        else:
            # if not set to automove, checks if both sides are available, if they are, it gives the player the choice of where to move
            if cardsList[cardPos + 1].curName == "" and cardsList[cardPos - 1] == "":
                direction = takeKeyPress((pygame.K_LEFT, pygame.K_RIGHT))
                if (direction == pygame.K_RIGHT):
                    posDirection = 1
                else:
                    posDirection = -1

    # Moves the card towards the direction it is facing, if possible
    if cardsList[cardPos + posDirection].curName == "":
        sCard.changePos(cardPos + posDirection)
        outputScreen()
        activeSigilUpkeep()
        return

    # Prevents the card from moving to a space that it cant (out of range or on other side) or from switching its direction to the wrong side
    if onEdge:
        activeSigilUpkeep()
        return
    
    # swaps the direction the card is facing - if automove is enabled
    if autoMove:
        if sCard.trackers["sprintDir"] == "right": sCard.trackers["sprintDir"] = "left"
        if sCard.trackers["sprintDir"] == "left": sCard.trackers["sprintDir"] = "right"
    
    # Tries to move towards the other direction
    if cardsList[cardPos + (-1 * posDirection)].curName == "":
        sCard.changePos(cardPos + (-1 *posDirection))
        outputScreen()
    activeSigilUpkeep()
        

def startOfTurn(curPlayer):

    # Energy upkeep
    if resources[curPlayer + "maxEnergy"] < 6:
        resources[curPlayer + "maxEnergy"] += 1
    resources[curPlayer + "curEnergy"] = resources[curPlayer + "maxEnergy"]

    for i in cardRanges[curPlayer]:
        card = cardsList[i]
        if "fledgWait" in card.trackers:
            card.trackers.pop("fledgWait")
            if card.curName in evolveDict:
                evolution = evolveDict[card.curName]
                card.curName = evolution["name"]
                card.curAttack += evolution["attackMod"]
                card.curHealth += evolution["healthMod"]
                # Removes all base sigils from the card's current sigils
                for curSigil in card.curSigils:
                    if curSigil in card.modSigils:
                        card.curSigils.remove(curSigil)
                        break
                # Adds the new sigils from the evolution to the current sigils, replacing the base sigils
                for newSigil in evolution["replaceSigils"]:
                    card.curSigils.append(newSigil)
                    
            else:
                card.curName = "Elder " + card.curName
                card.curAttack += 1
                card.curHealth += 2


def endOfTurn(currentPlayer = "top"):
    if currentPlayer == "top":
        cardRange = range(0,4)
    else: cardRange = range(4,8)

    # card checkup. set trackers. end of turn sigil activation
    for i in cardRange:
        curCard = cardsList[i]
        # tracks that the card has been on the board for a turn
        if "fledgling" in curCard.curSigils:
            curCard.trackers["fledgWait"] = True
        # all cards with movement sigils are marked that they haven't moved this turn
        if "sprinter" in curCard.curSigils:
            curCard.trackers["sprinted"] = False
        if "hefty" in curCard.curSigils:
            curCard.trackers["hefted"] = False
        if "rampager" in curCard.curSigils:
            curCard.trackers["rampaged"] = False
        # Generates a bone if the card has bone digger
        if "bone digger" in curCard.curSigils:
            resources[currentPlayer + "bones"] += 1
            playSound(makeBoneSound, 500)
            outputScreen()

    # Moves all cards with movement sigils
    for i in cardRange:
        curCard = cardsList[i]
        if "sprinter" in curCard.curSigils:
            if curCard.trackers["sprinted"] == False:
                sprint(i)
    

def initNewCard(newCardInfo = ""):
    testing = False
    global sideCard

    # if the card has no text and not testing, return nothing to avoid errors
    if newCardInfo == "" and not testing:
        return

    if testing:
        # Takes in the card text info from the console
        while True:
            newCardInfo = input("Paste card info:\n").split(",")
            if len(newCardInfo) == 8:
                break
    else:
        newCardInfo = newCardInfo.split(",")
    
    newCardBaseSigils = []
    newCardModSigils = []
    # Takes in sigils and sets cards with no sigils with an empty list
    if newCardInfo[3] != "":
        newCardBaseSigils = newCardInfo[3].lower().split(":")
        newCardModSigils = newCardBaseSigils

    if newCardInfo[6] != "":
        for additionalSigil in newCardInfo[6].lower().split(":"):
            newCardModSigils.append(additionalSigil)


    # Set the sideCard to be the new card and display it
    sideCard = Card(8, newCardInfo[0], int(newCardInfo[1]), int(newCardInfo[2]),
                    newCardBaseSigils, int(newCardInfo[4]), int(newCardInfo[5]), newCardModSigils)
    outputScreen()


    newCardCosts = newCardInfo[7].split(":")
    gemCosts = []
    consumableCostTypes = ("energy", "bones", "blood", "free")
    gemCostTypes = ("blue", "green", "orange", "prism")

    # Checks if the player has an open spot to play the new card in - if they don't the initialization is cancelled
    if not hasOpenSpot(cardRanges[whoseTurn]):
        ableToPlaceCard = False
        for cost in newCardCosts:
            if cost.split("-")[0] == "blood":
                ableToPlaceCard = True
        if not ableToPlaceCard:
            print("You do not have an open space to play this card")
            sideCard = Card(8)
            while nfcCardPresent(usbReader):
                continue
            return

    # Checks if the player can pay consumable costs - puts all of the gem costs into their own list to be dealt with later
    for cost in newCardCosts:
        costType = cost.split("-")[0]
        costAmount = int(cost.split("-")[1])
        
        if costType in consumableCostTypes:
            if not canPayCost(costType, costAmount, whoseTurn):
                print("you do not have the available resources to play this card")
                sideCard = Card(8)
                while nfcCardPresent(usbReader):
                    continue
                return
        elif costType in gemCostTypes:
            for i in range(costAmount): gemCosts.append(costType)
            
    # Checks if the player can pay the gem costs
    if not canPayGems(whoseTurn, gemCosts):
        print("you do not have the available resources to play this card")
        sideCard = Card(8)
        while nfcCardPresent(usbReader):
            continue
        return
    
    # The player is now capable of paying all costs - pays the player's costs
    for cost in newCardCosts:
        costType = cost.split("-")[0]
        costAmount = int(cost.split("-")[1])
        if costType in consumableCostTypes:
            payCost(costType, costAmount, whoseTurn)


    newCardPos = -1
    while newCardPos not in cardRanges[whoseTurn] or cardsList[newCardPos].curName != "":
        print("position of new card?")
        newCardPos = int(takeKeyPress((pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4), "unicode"))
        if whoseTurn == "top":
            newCardPos += -1
        else: newCardPos += 3

    sideCard.changePos(newCardPos, False)
    onPlaySigils(newCardPos)
    outputScreen()


def activeSigilUpkeep():
    # reset all cards active attack mods to 0 and remove their impact on the card's curAttack
    for card in cardsList:
        card.curAttack -= card.activeAttackMod
        card.activeAttackMod = 0
    
    for card in cardsList:
        if "leader" in card.curSigils:
            for adjPos in adjacentCardsPos[card.pos]:
                cardsList[adjPos].activeAttackMod += 1
        
        if "stinky" in card.curSigils:
            cardsList[getOpposingPos(card.pos)].activeAttackMod -= 1
        
        if "annoying" in card.curSigils:
            cardsList[getOpposingPos(card.pos)].activeAttackMod += 1
        
        if "colony" in card.curSigils:
            for i in getSideRange(card.pos):
                if "colony" in cardsList[i].curSigils:
                    card.activeAttackMod += 1

    # Modifies each card's current attack by the amount it has been changed by active sigils
    for card in cardsList:
        card.curAttack += card.activeAttackMod
    outputScreen()

def onPlaySigils(cardPos):
    activeSigilUpkeep()

    if "colony" in cardsList[cardPos].curSigils:
        cardsList[cardPos].curAttack = 0
    
    if "sentry" in cardsList[getOpposingPos(cardPos)].curSigils:
        cardsList[cardPos].curHealth -= 1
        checkIfDead(cardPos)

    activeSigilUpkeep()

def checkIfDead(cardPos):
    card = cardsList[cardPos]
    if (card.curHealth <= 0 or "deathtouched" in card.trackers) and card.curName != "":
        if "deathtouched" in card.trackers: card.trackers.pop("deathtouched")
        killCard(card.pos)

def getSideRange(cardPos):
    if cardPos < 4:
        return (0, 1, 2, 3)
    else:
        return (4, 5, 6, 7)

def canPayCost(type, amount, curPlayer):
    if type == "free":
        return True
    
    if type == "bones":
        return resources[curPlayer + "bones"] >= amount
        
    if type == "energy":
        return resources[curPlayer + "curEnergy"] >= amount
    
    if type == "blood":
        return totalBlood(curPlayer) >= amount
    
    if type == "gems":
        return canPayGems(curPlayer, amount)

def payCost(type, amount, curPlayer):
    if type == "free":
        return True
    
    if type == "bones":
        if resources[curPlayer + "bones"] >= amount:
            resources[curPlayer + "bones"] -= amount
            return True
        return False
    elif type == "energy":
        if resources[curPlayer + "curEnergy"] >= amount:
            resources[curPlayer + "curEnergy"] -= amount
            return True
        return False
    elif type == "blood":
        if totalBlood(curPlayer) >= amount:
            payBlood(curPlayer, amount)
            return True
        return False

# Calculates the max amount of blood a player could generate
def totalBlood(curPlayer):
    bloodCount = 0
    for i in cardRanges[curPlayer]:
        card = cardsList[i]
        if card.curName != "":
            if "worthy sacrifice" in card.curSigils:
                bloodCount += 3
            else:
                bloodCount += 1
    return bloodCount

def canPayGems(curPlayer, gemsNeeded):
    print("gems needed:", gemsNeeded)
    ownedGems = gemsOwned(curPlayer)
    print("owned gems:", ownedGems)
    colorlessNeeded = []
    i = 0
    while i < len(gemsNeeded):
        gem = gemsNeeded[i]
        if gem == "colorless":
            colorlessNeeded.append(gem)
            gemsNeeded.pop(i)
            i -= 1
        elif gem in ownedGems:
            ownedGems.remove(gem)
        elif "prism" in ownedGems:
            ownedGems.remove("prism")
        else:
            return False
        i += 1
    
    return len(colorlessNeeded) <= len(ownedGems)


def gemsOwned(curPlayer):
    gemList = []
    for i in cardRanges[curPlayer]:
        if "green gem" in cardsList[i].curSigils:
            gemList.append("green")
        if "blue gem" in cardsList[i].curSigils:
            gemList.append("blue")
        if "orange gem" in cardsList[i].curSigils:
            gemList.append("orange")
        if "prism gem" in cardsList[i].curSigils:
            gemList.append("prism")
    return gemList


def payBlood(curPlayer, cost):
    amountPaid = 0
    sacIndexList = []
    needMoreSacs = True

    while needMoreSacs:

        outputScreen()
        print("Blood Paid: " + str(amountPaid) + "\nBlood Cost: " + str(cost))
        print("Which card would you like to sacrifice")
        cardPos = int(takeKeyPress((pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4), "unicode"))
        if curPlayer == "top":
            cardPos += -1
        else:
            cardPos += 3
        if cardPos not in sacIndexList and cardsList[cardPos].curName != "":
            sacIndexList.append(cardPos)
            if "worthy sacrifice" in cardsList[cardPos].curSigils:
                amountPaid += 3
            else:
                amountPaid += 1
                
        # Check if sacrificing is done. 
        # if the cost has been paid, checks if the player has an available space to play their card after sacrifices are made
        if amountPaid >= cost:
            if not hasOpenSpot(cardRanges[curPlayer]):
                for i in sacIndexList:
                    if "many lives" not in cardsList[i].curSigils:
                        needMoreSacs = False
                        break
            else:
                needMoreSacs = False

    print(sacIndexList)
    for sacIndex in sacIndexList:
        if "many lives" not in cardsList[sacIndex].curSigils:
            killCard(sacIndex)

def onDeathSigils(cardPos):
    global resources
    if cardPos < 4:
        mySide = "top"
        enemySide = "bot"
    else:
        mySide = "bot"
        enemySide = "top"
    
    for pos in cardRanges[enemySide]:
        if "scavenger" in cardsList[pos].curSigils:
            resources[enemySide + "bones"] += 1
            outputBones()
            playSound(makeBoneSound, 600)
    


def killCard(cardPos):
    makeBones(cardsList[cardPos])
    onDeathSigils(cardPos)
    cardsList[cardPos] = Card(cardPos)
    activeSigilUpkeep()
    outputScreen()
    playSound(deathSound)
    pygame.time.delay(500)

# Given a list of acceptable inputs, the function waits for one of the keys to be pressed, and then returns the value of the key press
def takeKeyPress(reqKeys = (), returnType = "constant"):
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key in reqKeys:
                    if returnType == "constant":
                        return event.key
                    elif returnType == "unicode":
                        return event.unicode
                    else:
                        print("takeKeyPress_Error: invalid returnType: \"" + returnType + + "\"")
                        return

def hasOpenSpot(cardRange):
    for i in cardRange:
        if cardsList[i].curName == "":
            return True
    return False

def outputBones():
    pygame.draw.rect(screen, white, pygame.Rect(1020, 85, 80, 60))
    pygame.draw.rect(screen, white, pygame.Rect(1020, 435, 80, 60))
    screen.blit(pygame.font.Font(None, 30).render("Bones:", True, black), (1020, 100))
    screen.blit(pygame.font.Font(None, 30).render(str(resources["topbones"]), True, black), (1020, 130))
    screen.blit(pygame.font.Font(None, 30).render("Bones:", True, black), (1020, 450))
    screen.blit(pygame.font.Font(None, 30).render(str(resources["botbones"]), True, black), (1020, 480))

def outputEnergy():
    players = ("top", "bot")
    yVal = 100

    for player in players:
        xVal = 1120
        
        for x in range(resources[player + "maxEnergy"]):
            pygame.draw.rect(screen, darkBlue, pygame.Rect(xVal, yVal, 30, 70))
            xVal += 32
        xVal = 1120
        for x in range(resources[player + "curEnergy"]):
            pygame.draw.rect(screen, lightBlue, pygame.Rect(xVal, yVal, 30, 70))
            xVal += 32
        xVal = 1120
        for x in range(6):
            pygame.draw.rect(screen, black, pygame.Rect(xVal, yVal, 30, 70), 2)
            xVal += 32
        yVal = 680

def outputScreen():

    pygame.display.update()
    # Set white background
    screen.fill(white)

    # ALL Object outputs
    for card in cardsList:
        card.output()

    # Output side card - the card on the initializer or some other funky output
    sideCard.sideOutput()

    # Energy output
    outputEnergy()
    
    #cardInputBox.output()
    theScale.output()
    if whoseTurn == "top":
        screen.blit(pygame.font.Font(None, 40).render("My Turn!", True, green), (20, 200))
    else:
        screen.blit(pygame.font.Font(None, 40).render("My Turn!", True, green), (20, 600))

    #Draws Lines each 100 pixels on x and y axis - ruler for lining up screen elements
    """
    for i in range(9):
        pygame.draw.line(screen, black, (1400, i * 100), (1380, i * 100))
    for i in range(15):
        pygame.draw.line(screen, black, (i * 100, 800), (i * 100, 780))        
    """

    outputBones()
    pygame.display.update()


pygame.init() # REAL STUFF STARTS HERE

# Screen that everything is drawn on, size in pixels
screen = pygame.display.set_mode((1400, 800))

# Every sigil used in the game
allSigils = ["Rabbit Hole", "Bees Within", "Sprinter", "Touch of Death", "Fledgling", "Dam Builder", "Hoarder",
             "Burrower", "Fecundity", "Loose Tail", "Corpse Eater", "Bone King", "Waterborne", "Unkillable", "Sharp Quills",
             "Hefty", "Ant Spawner", "Guardian", "Airborne", "Many Lives", "Repulsive", "Worthy Sacrifice", "Mighty Leap",
             "Bifurcated Strike", "Trifurcated Strike", "Frozen Away", "Trinket Bearer", "Steel Trap", "Amorphous", "Tidal Lock",
             "Omni Strike", "Leader", "Bellist", "Stinky", "Bone Digger", "Brittle", "Skeleton Crew", "Green Mox", "Orange Mox",
             "Blue Mox", "Gem Animator", "Ruby Heart", "Mental Gemnastics", "Gem Dependant", "Great Mox", "Handy", "Squirrel Shedder",
             "Attack Conduit", "Spawn Conduit", "Null Conduit", "Battery Bearer", "Detonator", "Sentry", "Energy Conduit",
             "Bomb Spewer", "Insta-Bomber", "Double Death", "Power Dice", "Enlarge", "Disentomb", "Energy Gun", "Looter",
             "True Scholar", "Stimulate", "Bonehorn", "Kraken Waterborne", "Sniper", "Armored", "Overclocked", "Bomb Latch",
             "Brittle Latch", "Shield Latch", "Gem Guardian", "Vessel Printer", "Clinger"]

# COLORS
white = (255,255,255)
black = (0, 0, 0)
red = (255, 0, 0)
green = (88, 194, 35)
darkOrange = (199, 120, 2)
darkBlue = (2, 74, 163)
lightBlue = (0, 157, 255)

# base font - not really used
font = pygame.font.Font(None, 30)

# Box for text input of card info
#cardInputBox = TextRect((20, 20, 500, 50), black, "", white, 30)
# Variable that stores raw string input from NFC reader and is used to convert it to a usable list
newCardInfo = ""

# Dictionary with each card with natural fledgling and its evolution
evolveDict = {
    "Wolf Cub" : {"name" : "Wolf", "attackMod" : +2, "healthMod" : +1, "replaceSigils" : []},
    "Direwolf Pup" : {"name" : "Direwolf", "attackMod" : +1, "healthMod" : +2, "replaceSigils" : ["double strike"]},
    "Elk Fawn" : {"name" : "Elk", "attackMod" : +1, "healthMod" : +3, "replaceSigils" : ["sprinter"]},
    "Elk" : {"name" : "Moose Buck", "attackMod" : +1, "healthMod" : +2, "replaceSigils" : ["hefty"]},
    "Strange Larva" : {"name" : "Strange Pupa", "attackMod" : +0, "healthMod" : +0, "replaceSigils" : ["fledgling"]},
    "Strange Pupa" : {"name" : "Mothman", "attackMod" : +7, "healthMod" : +0, "replaceSigils" : ["airborne"]},
    "Raven Egg" : {"name" : "Raven", "attackMod" : +2, "healthMod" : +1, "replaceSigils" : ["airborne"]},
    "Tadpole" : {"name" : "Bullfrog", "attackMod" : +1, "healthMod" : +1, "replaceSigils" : ["mighty leap"]},
    "Worker Ant" : {"name" : "Ant Queen", "attackMod" : +0, "healthMod" : +2, "replaceSigils" : ["ant spawner", "colony"]},
    "Flying Ant" : {"name" : "Ant Queen", "attackMod" : +0, "healthMod" : +2, "replaceSigils" : ["ant spawner", "colony"]},
    "Mole" : {"name" : "Mole Man", "attackMod" : +1, "healthMod" : +2, "replaceSigils" : ["burrower", "mighty leap"]},
    "Mantis" : {"name" : "Mantis God", "attackMod" : +0, "healthMod" : +0, "replaceSigils" : ["trifurcated strike"]},
    "Sarcophagus" : {"name" : "Mummy Lord", "attackMod" : +3, "healthMod" : +1, "replaceSigils" : []},
    "Alpha" : {"name" : "Omega", "attackMod" : +1, "healthMod" : +2, "replaceSigils" : ["leader"]},
    "Child 13" : {"name" : "Child 14", "attackMod" : +1, "healthMod" : +2, "replaceSigils" : ["many lives", "airborne"]},
    "Dam" : {"name" : "Hot Dam", "attackMod" : +1, "healthMod" : +2, "replaceSigils" : ["terrain"]},
    "Long Elk" : {"name" : "Longer Elk", "attackMod" : +1, "healthMod" : +2, "replaceSigils" : ["touch of death", "sprinter"]},
    "Opossum" : {"name" : "Awesome Opossum", "attackMod" : +1, "healthMod" : +2, "replaceSigils" : []},
    "Mothman" : {"name" : "Final Form", "attackMod" : +1, "healthMod" : +2, "replaceSigils" : ["airborne"]},
    "Great White" : {"name" : "Greater White", "attackMod" : +1, "healthMod" : +2, "replaceSigils" : ["waterborne"]},
}

# A tuple containing tuples at indicis that correspond to card positions. The tuples contain the card positions that are adjacent to
# a card at the position of the index of that tuple.
adjacentCardsPos = (
    (1,),
    (0,2),
    (1,3),
    (2,),
    (5,),
    (4,6),
    (5,7),
    (6,)
)

# Permanent settings - Only change in code or in game startUp
autoMove = True

# Card instance initialization
cardsList = [Card(0), 
             Card(1), 
             Card(2), 
             Card(3), 
             Card(4), 
             Card(5),
             Card(6), 
             Card(7)]

# The connected usb NFC reader
usbReader = nfc.ContactlessFrontend('usb')

# Card to be shown on the side of the screen - used for all newly played cards
sideCard = Card(8)

# Easy access ranges for for loops
cardRanges = {"top" : range(0, 4), "bot" : range(4, 8)} 

# Sound initialization
deathSound = pygame.mixer.Sound("Inscryption_Sounds\card_death.wav")
hitSound = pygame.mixer.Sound("Inscryption_Sounds\card_attack_creature.wav")
directHitSound = pygame.mixer.Sound("Inscryption_Sounds\card_attack_directly.wav")
makeBoneSound = pygame.mixer.Sound("Inscryption_Sounds\\bone_token_enter_higher.wav")
spendBoneSound = pygame.mixer.Sound("Inscryption_Sounds\\bone_token_exit.wav")

# Bone trackers
resources = {
    "topbones" : 0,
    "botbones" : 0,
    "topmaxEnergy" : 0,
    "botmaxEnergy" : 0,
    "topcurEnergy" : 0,
    "botcurEnergy" : 0
}

# Tracks whose turn it is - can be "top" or "bot"
whoseTurn = "bot"

# Scale that tracks damage
theScale = Scale((30, 400, 50, 50), red, "", black, 20, 0)

# if false, program stops
running = True

startOfTurn(whoseTurn)

while running:
    outputScreen()

    if nfcCardPresent(usbReader):
        initNewCard(getNfcText(usbReader))

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE or event.key == pygame.K_KP_ENTER:
                doAttacks()
                endOfTurn(whoseTurn)
                if whoseTurn == "top":
                    whoseTurn = "bot"
                else: whoseTurn = "top"
                startOfTurn(whoseTurn)
            if event.key == pygame.K_BACKSPACE:
                #cardInputBox.text = cardInputBox.text[:-1]
                continue

            #cardInputBox.text += event.unicode
            if event.key == pygame.K_ESCAPE:
                    running = False
                    break

             