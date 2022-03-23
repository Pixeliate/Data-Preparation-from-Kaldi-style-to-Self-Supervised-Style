import os
import re
import sys
from typing import Dict, List
from pathlib import PurePath
from pydub import AudioSegment

if len(sys.argv) != 5:
    print("Usage: python data_prep.py [flac2wav] [raw_list_of_file] [part] [partition]")
    sys.exit(1)
#myst_root =
flac2wav = sys.argv[1]
raw_list = sys.argv[2]
task = sys.argv[3]
partition = sys.argv[4]

print("flac2wav : ",flac2wav," \n","raw_list : ",raw_list,"\n", "task : ",task ,"\n","partition",partition,"\n")

#checking line to be skipped
def checking(line_c):
    #print(line_c)
    flag = 0
    lc = ['','<nosignal>','<sidespeech>','<noise>','<fp> ','<indiscernible>','<silence>','<laugh>','<disturbance>','<no voice>','<breath>','<discard>','<laugh>']     
    if any(word in line_c.split(" ") for word in lc ):
        flag =1
    #new  line to remove  containing numbers
    elif any(char in line_c for char in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '[', '(', ')', ']', '/', '<', '>']):
        flag = 1
    else: flag = 0
    #print("fun flag : ",flag)
    if flag: return 0
    else: return 1

rep_dict = {'[INDISCERNIBLE]': '', '(())': '', '(*)': '', '.': '', '?': '', '-': '', '_': '', 
            ';': '', ':': '', '\n': '', '\\': '', '"': '', '+': '', '*': '', '&': ' and ', '<[^>]+>': ''}

def multiple_replace(string:str, rep_dict:Dict):
    pattern = re.compile("|".join([re.escape(k) for k in sorted(rep_dict,key=len,reverse=True)]), flags=re.DOTALL)
    return pattern.sub(lambda x: rep_dict[x.group(0)], string)

def process_text(text:str):
    text = text.encode('ascii', 'ignore').decode('utf-8')
    text = multiple_replace(text, rep_dict).upper()
    text = re.sub(' +', ' ', text).strip()
    return text

with open(raw_list , 'r') as wav_trans_f , open(
            os.path.join("baseline_trial/data", task, task + "_set.txt"), "w", encoding='utf-8') as text_f :

    text_f.truncate()
    wav_trans = sorted(wav_trans_f.readlines(), key=lambda s: s.split(" ")[0])
    #wav_trans = wav_trans_f.readlines()
    index = 0
    print(wav_trans)
    for line in wav_trans:
        index = index +1
        print(index)
        #print(partition)
        #print(task)
        if(partition and task=="finetune" and index > (len(wav_trans)/2)):
        #if(partition and task=="finetune" and index > 10):
            #print("break")
            break
        elif(partition and task=="test" and index < (len(wav_trans)/2)):
            #print("continue")
            continue
            
            
        linei = line.split('\t',1)
        label_prep = re.split('/|\.' , linei[0])
        #print(linei)
        try: 
            label1 = str(str(label_prep[-3]) + str(label_prep[-2]))
            label = label1.replace("_", "").replace("-","")
            #print("going for try")
            file_path = PurePath(linei[0])
            #print(file_path)
            flac_tmp_audio_data = AudioSegment.from_file(file_path, file_path.suffix[1:])
            addr = str("baseline_trial/data/"+task+"/"+label + ".wav")
            flac_tmp_audio_data.export(addr , format="wav")

            #address = str("baseline_trial/data/"+task+"/"+file_path.name.replace(file_path.suffix, "") + ".wav")
            print("addr : ",addr, "\n")
            text = process_text(linei[1])
            #print(linei[1])
            #print("Tect : ", text)
            result = checking(text)
            #print(result)
            if(result == 1):
                    text_f.write(addr + "\t" + text.upper() + "\n")
     
        except:
            pass
        
wav_trans_f.close()
text_f.close()
