import re, os, itertools, json

pat = re.compile(r"(effect_starting_buildings_.*?) = {")
pat_lvl = re.compile(r"level = (.*?)\n")
pat_pm = re.compile(r"\"(pm_.*?)\"")
pat_ag = re.compile(r"(effect_starting_buildings_.*?) = yes")
pat_ftxt = re.compile(r"(pm_.*?) = {(\n|.)*?level_scaled = {((\n|.)*?)}")
pat_ftxt2 = re.compile(r"(pm_.*?) = {(\n|.)*?workforce_scaled = {((\n|.)*?)}")
pat_ftxt3 = re.compile(r"(pm_.*?) = {(\n|.)*?unscaled = {((\n|.)*?)}")
pat_empl = re.compile(r'building_employment_(.*?)_add = (.*?)( |\n)')
pat_input = re.compile(r'building_input_(.*?)_add = (.*?)( |\n)')
pat_output = re.compile(r'building_output_(.*?)_add = (.*?)( |\n)')
pat_emp_mult = re.compile(r'building_employment_(.*?)_mult = (.*?)( |\n)')



with open("config.txt", "r", encoding='utf-8') as f:
    loc = f.readline().replace("\n", "")

with open("config.txt", "r", encoding='utf-8') as f:
    loc2 = f.readlines()[1].replace("\n", "")

if __name__ == "__main__":
    with open(loc, "r", encoding='utf-8') as f:
        lines = f.readlines()
        
    splits = []
    pms = []
    c_pms = []
    i = 0
    j = 0
    building_id = 0
    for line in lines:
        ptr = pat.findall(line)
        ptlvr = pat_lvl.findall(line)
        ptgn = pat_ag.findall(line)
        if len(ptr) != 0:
            splits.append(ptr[0])
            pms.append([c_pms[i:i+2] for i in range(0, len(c_pms), 2)])
            c_pms = []
        if len(ptlvr) != 0:
            c_pms.append(ptlvr[0])
        if len(ptgn) != 0:
            name = ptgn[0]
            c = 1
            for s in splits: 
                if s == name:
                    break
                c+=1
            c_pms.extend(list(itertools.chain.from_iterable(pms[c])))
        if "activate_production_methods" in line:
            c_pms.append(pat_pm.findall(line))
        i+=1
    
    pms.append([c_pms[i:i+2] for i in range(0, len(c_pms), 2)])

    pms = pms[1:]

    pms_dict = {}
    g_u_dict = {}
    mult_dict = {}
    

    for n in os.listdir(loc2):
        with open(loc2 + "\\" + n, "r", encoding='utf-8') as f:
            raw_txt = f.read()
            for pm in pat_ftxt.findall(raw_txt):
                employee_data = {}
                for pop in pat_empl.findall(pm[2]):
                    employee_data[pop[0]] = int(pop[1])
                pms_dict[pm[0]] = employee_data
            for pm in pat_ftxt2.findall(raw_txt):
                goods_data = {}
                # assumes the output and input are distinct
                for good in pat_input.findall(pm[2]):
                    goods_data[good[0]] = -int(good[1])
                for good in pat_output.findall(pm[2]):
                    goods_data[good[0]] = int(good[1])
                g_u_dict[pm[0]] = goods_data
            for pm in pat_ftxt3.findall(raw_txt):
                mult_data = {}
                for mult in pat_emp_mult.findall(pm[2]):
                    mult_data[mult[0]] = float(mult[1])
                mult_dict[pm[0]] = mult_data
                


    l = 0

    print(mult_dict)

    for grs in pms:
        gr_dict = {}
        gru_dict = {}
        for ind_pm_g in grs:
            lvl = int(ind_pm_g[0])
            for ind_pm in ind_pm_g[1]:
                cmults = {}
                try: # some pms have no employees, so they are simply ignored
                    for k, _ in pms_dict[ind_pm].items():
                        if ind_pm in mult_dict:
                            if k in mult_dict[ind_pm]:
                                if k in cmults:
                                    cmults[k] += mult_dict[ind_pm][k]
                                else: 
                                    cmults[k] += mult_dict[ind_pm][k]
                    for k, v in pms_dict[ind_pm].items():
                        
                        if k in gr_dict:
                            gr_dict[k] += lvl*v
                        else: 
                            gr_dict[k] = lvl*v

                        if k in cmults:
                            gr_dict[k] += gr_dict[k]*cmults[k]

                except: pass
                try: # empty pms
                    for k, v in g_u_dict[ind_pm].items():
                        if k in gru_dict:
                            gru_dict[k] += lvl*v
                        else:
                            gru_dict[k] = lvl*v
                except: pass
                
        print(splits[l], ": ")
        print("Overall weekly production: ", json.dumps(gru_dict, indent=4))
        print("Overall required labour force: ", json.dumps(gr_dict, indent=4))
        print("\n")
        l+=1

