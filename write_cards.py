import nfc
from ndef import TextRecord
import pygame
from nfc.clf import RemoteTarget

reader = nfc.ContactlessFrontend('usb')
cardInfo = ""
costTypeList = ["free", "blood", "bones", "energy", "blue", "orange", "green", "colorless"]

allSigils = ['rabbit hole', 'bees within', 'sprinter', 'touch of death', 'fledgling', 'dam builder', 'hoarder', 'burrower', 
            'fecundity', 'loose tail', 'corpse eater', 'bone king', 'waterborne', 'unkillable', 'sharp quills', 'hefty',
            'ant spawner', 'guardian', 'airborne', 'many lives', 'repulsive', 'worthy sacrifice', 'mighty leap', 'bifurcated strike',
            'trifurcated strike', 'frozen away', 'trinket bearer', 'steel trap', 'amorphous', 'tidal lock', 'omni strike', 'leader',
            'bellist', 'stinky', 'bone digger', 'brittle', 'skeleton crew', 'green gem', 'orange gem', 'blue gem', 'gem animator',
            'ruby heart', 'mental gemnastics', 'gem dependant', 'great mox', 'handy', 'squirrel shedder', 'attack conduit',
            'spawn conduit', 'null conduit', 'battery bearer', 'detonator', 'sentry', 'energy conduit', 'bomb spewer',
            'insta-bomber', 'double death', 'power dice', 'enlarge', 'disentomb', 'energy gun', 'looter', 'true scholar',
            'stimulate', 'bonehorn', 'kraken waterborne', 'sniper', 'armored', 'overclocked', 'bomb latch',
            'shield latch', 'gem guardian', 'vessel printer', 'clinger', 'aquanaut', 'bastion', 'scavenger', 'colony', 
            'annoying', 'none', 'bloodless', 'prism gem', 'divination', 'double strike', 'mox dropper', 'convalesce']


def findLongerWord(wordList, segment):
    checkWordList = wordList
    
    for size in range(1, len(segment) + 1):
        potentialMatches = []
        for word in checkWordList:
            if segment[:size] == word[:size]:
                potentialMatches.append(word)

        if len(potentialMatches) == 1:
            return potentialMatches[0]
        elif len(potentialMatches) == 0:
            print("Longer_Word_Finder: No matches")
            return ''
        else:
            checkWordList = potentialMatches
    
    print("Multiple Matches Found: ", end="")
    for word in checkWordList:
        print(word, end=" ")
    print()
    return findLongerWord(checkWordList, input("What word did you mean?\n"))

while True:

    cardName = input("Card Name: ").title()
    baseAttack = input("Base Attack: ")
    baseHealth = input("Base Health: ")
    rawSigils = input("Base Sigils (separated by \":\", \"none\" if no sigils): ").lower().split(":")
    baseSigils = []
    costsList = []

    rawSigils[0] = findLongerWord(allSigils, rawSigils[0])
    if rawSigils[0] != "none":
        for sigil in rawSigils:
            baseSigils.append(findLongerWord(allSigils, sigil))

    cardTypeAmount = 1 # int(input("Amount of cost types: "))
    if cardTypeAmount == 0:
        costsList.append("free-0")
        
    for i in range(cardTypeAmount):
        costsList.append(findLongerWord(costTypeList, input("Cost Type (\"free\" if no cost): ")))
        costsList[-1] = costsList[-1] + "-" + input("Amount: ")


    cardInfo = cardName + "," + baseAttack + "," + baseHealth + "," + ":".join(baseSigils) + "," + baseAttack + "," + baseHealth + ",," + ":".join(costsList)
    print(cardInfo)

    input("Ready to Write?")
    target = reader.sense(RemoteTarget('106A'), RemoteTarget('106B'), RemoteTarget('212F'))

    if target is not None:
        try:
            myTag = nfc.tag.activate(reader, target)
            myTag.ndef.records  = [TextRecord(cardInfo)]
            print(myTag.ndef.records[0].text)
        except AttributeError:
            print("write failed :(")

# The sacred formatting, may it never be forgotten
# 'name,baseAtk,baseHealth,sigil:sigil,modAtk,modHealth,addSigil:addSigil,costType:costAmt:costColor

# Blood-3:greengem