import re, os, itertools, json

pat = re.compile(r"(effect_starting_buildings_.*?) = {")
pat_lvl = re.compile(r"level = (.*?)\n")
pat_bname = re.compile(r"building = \"(.*?)\"")
pat_pm = re.compile(r"\"(pm_.*?)\"")
pat_ag = re.compile(r"(effect_starting_buildings_.*?) = yes")
pat_ftxt = re.compile(r"(pm_.*?) = {(\n|.)*?level_scaled = {((\n|.)*?)}")
pat_ftxt2 = re.compile(r"(pm_.*?) = {(\n|.)*?workforce_scaled = {((\n|.)*?)}")
pat_ftxt3 = re.compile(r"(pm_.*?) = {(\n|.)*?unscaled = {((\n|.)*?)}")
pat_lvlscld = re.compile(r'level_scaled = {((\n|.)*?)}')
pat_wrkfcld = re.compile(r'workforce_scaled = {((\n|.)*?)}')
pat_unscld = re.compile(r'workforce_scaled = {((\n|.)*?)}')
pat_empl = re.compile(r'building_employment_(.*?)_add = (.*?)( |\n)')
pat_input = re.compile(r'building_input_(.*?)_add = (.*?)( |\n)')
pat_output = re.compile(r'building_output_(.*?)_add = (.*?)( |\n)')
pat_emp_mult = re.compile(r'building_employment_(.*?)_mult = (.*?)( |\n)')
pat_bul_pmg = re.compile(r"(building_.*?) = {(\n|.)*?production_method_groups = {((\n|.)*?)}")
pat_ibul_pmg = re.compile(r"(pmg_.*?)(\n| |\t)")
pat_pmg_pm = re.compile(r"(pmg_.*?) = {(\n|.)*?production_methods = {((\n|.)*?)}")
pat_ipmg_pm = re.compile(r"(pm_.*?)(\n| |\t)")



with open("config.txt", "r", encoding='utf-8') as f:
    loc = f.readline().replace("\n", "")

with open("config.txt", "r", encoding='utf-8') as f:
    loc2 = f.readlines()[1].replace("\n", "")

with open("config.txt", "r", encoding='utf-8') as f:
    loc3 = f.readlines()[2].replace("\n", "")

with open("config.txt", "r", encoding='utf-8') as f:
    loc4 = f.readlines()[3].replace("\n", "")

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
        ptnm = pat_bname.findall(line)
        if len(ptr) != 0:
            splits.append(ptr[0])
            pms.append([c_pms[i:i+3] for i in range(0, len(c_pms), 3)])
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
        if len(ptnm) != 0:
            c_pms.append(ptnm[0])
        if "activate_production_methods" in line:
            c_pms.append(pat_pm.findall(line))
        i+=1
    
    pms.append([c_pms[i:i+3] for i in range(0, len(c_pms), 3)])

    pms = pms[1:]

    pms_dict = {}
    g_u_dict = {}
    mult_dict = {}
    

    for n in os.listdir(loc2):
        with open(loc2 + "\\" + n, "r", encoding='utf-8') as f:
            raw_txt = f.read()
            m = re.split(r"(pm.*?) = {", raw_txt.replace("default_building_", "pm_default_building_"))[1:]
        
            m = [m[i:i+2] for i in range(0, len(m), 2)]

        for pm in m:
            employee_data = {}
            for dt in pat_lvlscld.findall(pm[1]):
                for pop in pat_empl.findall(dt[0]):
                    employee_data[pop[0]] = float(pop[1])
            pms_dict[pm[0]] = employee_data

            goods_data = {}
            # assumes the output and input are distinct
            for dt in pat_wrkfcld.findall(pm[1]):
                for good in pat_input.findall(dt[0]):
                    goods_data[good[0]] = -float(good[1])
                for good in pat_output.findall(dt[0]):
                    goods_data[good[0]] = float(good[1])
            g_u_dict[pm[0]] = goods_data

            mult_data = {}
            for dt in pat_unscld.findall(pm[1]):
                for mult in pat_emp_mult.findall(dt[0]):
                    mult_data[mult[0]] = float(mult[1])
            mult_dict[pm[0]] = mult_data

    # list of PMGs for each building
    pmg_getter = {}

    for n in os.listdir(loc3):
        with open(loc3 + "\\" + n, "r", encoding='utf-8') as f:
            raw_txt = f.read()
        for b in pat_bul_pmg.findall(raw_txt):
            pmg_getter[b[0]] = [pmg[0] for pmg in pat_ibul_pmg.findall(b[2])]
        

    # list of PMs for each PMG
    pm_getter = {}

    for n in os.listdir(loc4):
        with open(loc4 + "\\" + n, "r", encoding='utf-8') as f:
            raw_txt = f.read()
        for b in pat_pmg_pm.findall(raw_txt):
            pm_getter[b[0]] = [pm[0] for pm in pat_ipmg_pm.findall(b[2])]

    l = 0
    finfin = []
    for grs in pms:
        gr_dict = {}
        gru_dict = {}
        for ind_pm_g in grs:
            lvl = int(ind_pm_g[1])
            unused_pmgs = list(pmg_getter[ind_pm_g[0]])
            d = []
            l_pre = len(unused_pmgs)
            for ind_pm in ind_pm_g[2]:
                k = []
                for p in unused_pmgs:
                    if ind_pm in pm_getter[p]:
                        k.append(p)


                if len(k) == 0 and not "greeness" in ind_pm:
                    print(ind_pm, "is an incorrect production method for building", ind_pm_g[0])
                if len(k)>1:
                    print(ind_pm_g[0], "has multiple overlapping production method groups")
                if len(k)==1:
                    d.append(ind_pm)

                for u in k:
                    unused_pmgs.remove(u)

            # adds default PMG for unused Production method groups
            d.extend([pm_getter[pmg][0] for pmg in unused_pmgs])
            
            for ind_pm in d:
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
        FIN = ""
        FIN += str(splits[l]) + ":"
        FIN += "\n" + "Overall weekly production: " + str(json.dumps(gru_dict, indent=4))
        FIN += "\n" + "Overall required labour force: " + str(json.dumps(gr_dict, indent=4))
        FIN += "\n" + "Total employment: " + str(sum(gr_dict.values()))
        finfin.append(FIN)
        l+=1
    with open("out.txt", "w", encoding='utf-8') as f:
        f.write('\n'.join(finfin))

