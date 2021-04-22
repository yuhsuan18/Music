
import xml.etree.cElementTree as ET
import argparse

parser = argparse.ArgumentParser("Transform music into negative harmony")
parser.add_argument("--file",help='dir to the music file')
args = parser.parse_args()



# cycle of fifths
cycle_fifths_key_dict={"-7":"Cb","-6":"Gb","-5":"Db","-4":"Ab","-3":"Eb","-2":"Bb",
    "-1":"F","0":"C","1":"G","2":"D","3":"A","4":"E","5":"B","6":"F#","7":"C#"}

# C4~B4 (60~71)
center_key_midi_dict = {"C":"60","C#":"61","Db":"61,","D":"62","D#":"63","Eb":"63",
    "E":"64","F":"65","F#":"66","Gb":"66","G":"67","G#":"68","Ab":"68","A":"69","A#":"70","Bb":"70","B":"71"}

key_dict={"C":"0","C#":"1","Db":"1","D":"2","D#":"3","Eb":"3","E":"4","F":"5",
    "F#":"6","Gb":"6","G":"7","G#":"8","Ab":"8","A":"9","A#":"10","Bb":"10","B":"11"}

inv_sharp_key_list = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]
inv_flat_key_list = ["C","Db","D","Eb","E","F","Gb","G","G#","A","Bb","B"]



def findKeyAndMode(root):
    
    # find key
    fifths = root.find('.//key/fifths').text
    key = cycle_fifths_key_dict[str(fifths)]


    # find Major or minor (default Major)
    if(root.find('.//key/mode')):
        mode = root.find('.//key/mode').text
        mode = str(mode)
    else:
        # print("default: Major scale")
        mode = 'major'


    # convert key into midi note numbers
    if mode == 'major':
        keyMidiNum = center_key_midi_dict[key]
        keyMidiNum = int(keyMidiNum)  
        # print(keyMidiNum)
    else:
        keyMidiNum = center_key_midi_dict[key]
        keyMidiNum = int(keyMidiNum)+3
        # print(keyMidiNum)
        mode = 'major'
        
    return key,keyMidiNum,mode
    
    
def printOriginalSongNotes(root):

    # // ----> select all subelements
    all_notes = root.findall('.//note') 
    
    notes_sequence = []
    for note in all_notes:
        n = {}
        if note.find('rest') is not None:
            continue
        else:
            n['pitch'] = note.find('./pitch/step').text + note.find('./pitch/octave').text
            if note.find('./pitch/alter') is not None:
                if note.find('./pitch/alter').text == '-1':
                    p = n['pitch'][0] + 'b' + n['pitch'][1]
                    n['pitch'] = p
                else:
                    n['pitch'] = n['pitch'][0] + '#' + n['pitch'][1]
                    
            notes_sequence.append(n)
    
    # print(notes_sequence)



# e.g. 60 => 67
def convertNegative(notein,keyMidiNum):
    
    out = (keyMidiNum+7)-(notein - keyMidiNum)
    return out


def pitchToMidi(pitch):
    level = pitch[-1]
    level = int(level)
    key = pitch[0:-1]
    base = 60 + (level-4)*12 # base : C
    for index,value in key_dict.items():
        if index == key:
            keyNum = value
    keyNum = int(keyNum)
    out = base + keyNum
    #print("input pitch midi num",out)
    return out
    

def midiToPitch(root,midinote,keyMidiNum):
    # midinote = midinote + 12
    
    level = (midinote//12)-1
    halfnote = midinote%12
    
    fifths = root.find('.//key/fifths').text
    fifths = int(fifths)
    if fifths >= 0:
        pitch = inv_sharp_key_list[halfnote]
    else:
        pitch = inv_flat_key_list[halfnote]
    level = str(level)
    negPitch = pitch + level
    return negPitch

    
def pitchToXml(notein):
    step = notein[0]
    octave = notein[-1]
    if(len(notein) == 2):
        alter = 0
    elif(notein[1]=='#'):
        alter = 1
    else:
        alter = -1
    return str(step),str(octave),str(alter)

    
    
def main(): 
    
    tree = ET.parse(args.file)
    root = tree.getroot()
    key,keyMidiNum,mode = findKeyAndMode(root)

    # // ----> select all subelements
    all_notes = root.findall('.//note') 
    
    
    #print("step octave alter")
    for note in all_notes:
        n = {}
        if note.find('rest') is not None:
            continue
        else:
            notein = note.find('./pitch')
            n['pitch'] = note.find('./pitch/step').text + note.find('./pitch/octave').text
            if note.find('./pitch/alter') is not None:
                if note.find('./pitch/alter').text == '-1':
                    p = n['pitch'][0] + 'b' + n['pitch'][1]
                    n['pitch'] = p
                else:
                    n['pitch'] = n['pitch'][0] + '#' + n['pitch'][1]
            
            out = pitchToMidi(n['pitch'])
            out = convertNegative(out,keyMidiNum)
            out = midiToPitch(root,out,keyMidiNum)
            step,octave,alter = pitchToXml(out)
            #print(step,octave,alter)
            
            notein.remove(note.find('./pitch/step')) 
            e = ET.SubElement(notein,'step')
            e.text = step
            e.tail = '\n'
            
            if (alter != 0):
                if note.find('./pitch/alter') is not None:
                    notein.remove(note.find('./pitch/alter'))
                    e = ET.SubElement(notein,'alter')
                    e.text = alter
                    e.tail = '\n'
                else:
                    e = ET.SubElement(notein,'alter')
                    e.text = alter
                    e.tail = '\n'
            else:
                pass
            
            notein.remove(note.find('./pitch/octave'))
            e = ET.SubElement(notein,'octave')
            e.text = octave
            e.tail = '\n'
            
            
    tree.write('NegativeHarmony.musicxml')




if __name__== "__main__":

    main()



