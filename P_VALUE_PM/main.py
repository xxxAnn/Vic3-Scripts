import re, os, json

def price(price_dic, goods):
    return sum([int(price_dic[good[0]])*int(good[1]) for good in goods])

pat = re.compile(r'(.*?) = \{(\n|.)*?cost = (.*?)\n(\n|.)*?\}')
pat_ftxt = re.compile(r"(pm_.*?) = {(\n|.)*?workforce_scaled = {((\n|.)*?)}(\n|.)*?level_scaled = {((\n|.)*?)}")
pat_empl = re.compile(r'building_employment_(.*?)_add = (.*?)( |\n)')
pat_input = re.compile(r'building_input_(.*?)_add = (.*?)( |\n)')
pat_output = re.compile(r'building_output_(.*?)_add = (.*?)( |\n)')

with open("config.txt", "r", encoding='utf-8') as f:
    loc = f.readline().replace("\n", "")

with open("config.txt", "r", encoding='utf-8') as f:
    loc2 = f.readlines()[1].replace("\n", "")
    
if __name__ == "__main__":
    with open(loc, "r", encoding='utf-8') as f:
        goods_prices = dict([(x[0], x[2]) for x in pat.findall(f.read())])
        
    g_u_dict = {}
    for n in os.listdir(loc2):
        with open(loc2 + "\\" + n, "r", encoding='utf-8') as f:
            raw_txt = f.read()
            for pm in pat_ftxt.findall(raw_txt):
                o = price(goods_prices, pat_output.findall(pm[2])) 
                i = price(goods_prices, pat_input.findall(pm[2]))
                o_i = o - i
                e = sum([int(pop[1]) for pop in pat_empl.findall(pm[5])])
                if e != 0 and (o != 0 or i != 0):
                    g_u_dict[pm[0]] = round((52*o_i)/e, 1)
    print(json.dumps(g_u_dict, indent=4))
